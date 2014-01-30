#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import thread

import time
import inspect
import logging
import traceback
import atexit
import json
import collections
import cgi
import gettext

try:
    import xmpp
except ImportError:
    print >> sys.stderr, """
    You need to install xmpppy from http://xmpppy.sf.net/.
    On Debian-based systems, install the python-xmpp package.
    """
    sys.exit(-1)

class BotBase(object):
    # Show types for presence
    AVAILABLE, AWAY, CHAT = None, 'away', 'chat'
    DND, XA, OFFLINE = 'dnd', 'xa', 'unavailable'

    PING_FREQUENCY = 30 # Set to the number of seconds, e.g. 60.
    PING_TIMEOUT = 2 # Seconds to wait for a response.

    ########## Constructor ##########   
    def __init__(self, username, password, nickname=None, timezone='UTC', text_color=None, localization=None, res=None, debug=False, privatedomain=False, acceptownmsgs=False, handlers=None):
        # TODO sort this initialisation thematically
        self.__debug = debug
        self.log = logging.getLogger(__name__)
        self.__username = username
        self.__password = password
        self.nickname = nickname
        self.timezone = timezone
        self.jid = xmpp.JID(self.__username)
        self.res = (res or self.__class__.__name__)
        self.conn = None
        self.readyTs = 0
        self.__finished = False
        self.__show = None
        self.__status = None
        self.__seen = {}
        self.__threads = {}
        self.__lastping = time.time()
        self.__privatedomain = privatedomain
        self.__acceptownmsgs = acceptownmsgs
        self.text_color = text_color
        self.currentTopic = ""
        self.localization = "en"
        self.muted = False
        self.muc_users = {}
        self.roster = None
        self.myroster = {}
        self.muc_channels = []

        self.handlers = (handlers or [('message', self.callback_message), ('presence', self.callback_presence)])

        # Collect commands from source
        self.commands = {}
        for name, value in inspect.getmembers(self, inspect.ismethod):
            if getattr(value, '_jabberbot_command', False):
                name = getattr(value, '_jabberbot_command_name')
                self.log.info('Registered command: %s' % name)
                self.commands[name] = value

        if not localization:
            localization = self.localization
        else:
            self.localization = localization
        trans = gettext.translation("rmk.gabi", "locale", [localization]) 
        trans.install()

        self.MSG_AUTHORIZE_ME = _('Hey there. You are not yet on my roster. Authorize my request and I will do the same.')
        self.MSG_NOT_AUTHORIZED = _('You did not authorize my subscription request. Access denied.')
        self.MSG_HELP_TAIL = _('Type help *command name* to get more info about that specific command.')
        self.MSG_HELP_UNDEFINED_COMMAND = _('That command is not defined.')

        self.stats = self.loadJSON('save_stats.dat', { 'messageCount': 0 })
        atexit.register(self.saveJSON, 'save_stats.dat', self.stats)

    ########## Save / Load Functions ##########
    def saveJSON(self, filename, content):
        """Saves the given content to the given filename as JSON"""
        dstfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db', self.nickname.lower() + '_' + filename)
        try:
            file = open(dstfile, 'w')
            file.write(json.dumps(content))
            file.close()
            self.log.debug("Saving to %s" % (dstfile))
        except IOError:
            self.log.warning("Could not safe data to file %s!" % (dstfile))

    def loadJSON(self, filename, default):
        """Loads content from the given filename as JSON. If no file could be read, it returns the default."""
        dstfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db', self.nickname.lower() + '_' + filename)
        try:
            file = open(dstfile, 'r')
            # self.cron_list = self.utils.convert_from_unicode(json.loads(file.read()))
            values = json.loads(file.read())
            file.close()
            self.log.debug("Loading data from %s" % (dstfile))
            return values
        except IOError:
            return default
        except ValueError:
            return default

    ########## Class Methods ##########
    def _send_status(self):
        """Send status to everyone"""
        self.conn.send(xmpp.dispatcher.Presence(show=self.__show,
            status=self.__status))

    def __set_status(self, value):
        """Set status message.
        If value remains constant, no presence stanza will be send"""
        if self.__status != value:
            self.__status = value
            self._send_status()

    def __get_status(self):
        """Get current status message"""
        return self.__status


    def __set_show(self, value):
        """Set show (status type like AWAY, DND etc.).
        If value remains constant, no presence stanza will be send"""
        if self.__show != value:
            self.__show = value
            self._send_status()

    def __get_show(self):
        """Get current show (status type like AWAY, DND etc.)."""
        return self.__show

    status_message = property(fget=__get_status, fset=__set_status)
    status_type = property(fget=__get_show, fset=__set_show)

    ########## Instance Methods ##########
    def get_sender_username(self, mess):
        """Extract the sender's user name from a message"""
        type = mess.getType()
        jid = mess.getFrom()

        if type == "groupchat":
            username = jid.getResource()
        elif type == "chat":
            username = jid.getNode()
        else:
            username = ""
        return username

    def get_full_jids(self, jid):
        """Returns all full jids, which belong to a bare jid

        Example: A bare jid is bob@jabber.org, with two clients connected, which
        have the full jids bob@jabber.org/home and bob@jabber.org/work."""
        for res in self.roster.getResources(jid):
            full_jid = "%s/%s" % (jid,res)
            yield full_jid


    ########## Client Methods ##########
    def connect(self):
        if not self.conn:
        #TODO improve debug
            if self.__debug:
                conn = xmpp.Client(self.jid.getDomain())
            else:
                conn = xmpp.Client(self.jid.getDomain(), debug=[])

            #connection attempt
            conres = conn.connect()
            if not conres:
                self.log.error('Unable to connect to server %s.' % self.jid.getDomain())
                return None
            if conres != 'tls':
                self.log.warning('Unable to establish secure connection '\
                '- TLS failed!')

            authres = conn.auth(self.jid.getNode(), self.__password, self.res)
            if not authres:
                self.log.error('Unable to authorize with server.')
                return None
            if authres != 'sasl':
                self.log.warning("unable to perform SASL auth on %s. "\
                "Old authentication method used!" % self.jid.getDomain())

            # Connection established - save connection
            self.conn = conn

            # Send initial presence stanza (say hello to everyone)
            self.conn.sendInitPresence(requestRoster=1)
            # Save roster and log Items
            self.roster = self.conn.getRoster()
            # self.roster = self.conn.Roster.getRoster()
            self.log.info('*** roster ***')
            for contact in self.roster.getItems():
                self.log.info('  %s' % contact)
            self.log.info('*** roster ***')

            my_roster = self.conn.getRoster()
            for i in my_roster.getItems():
                self.myroster[i] = my_roster.getStatus(i)
            if len(self.myroster) > 0:
                self.myroster = self.convert_from_unicode(self.myroster)

            # Register given handlers (TODO move to own function)
            for (handler, callback) in self.handlers:
                self.conn.RegisterHandler(handler, callback)
                self.log.debug('Registered handler: %s' % handler)

        return self.conn

    def quitBot(self):
        self.__finished = True

    def join_room(self, room, username=None, password=None):
        """Join the specified multi-user chat room

        If username is NOT provided fallback to node part of JID"""
        # TODO fix namespacestrings and history settings
        NS_MUC = 'http://jabber.org/protocol/muc'
        username = self.nickname
        if username is None:
        # TODO use xmpppy function getNode
            username = self.__username.split('@')[0]
        my_room_JID = '/'.join((room, username))
        pres = xmpp.Presence(to=my_room_JID)
        pres.setShow(None)
        pres.setStatus("At your service.")
        if password is not None:
            pres.setTag('x',namespace=NS_MUC).setTagData('password',password)
        try:
            self.connect().send(pres)
            self.readyTs = time.time()
            self.muc_channels.append(room)
        except (AttributeError, ValueError) as e:
            self.log.warning('No connection could be established. ERROR:\n%s' % e)
            self.quitBot()

    def send_message(self, mess):
        """Send an XMPP message"""
        self.stats['messageCount'] += 1
        self.connect().send(mess)

    def send(self, user, text, in_reply_to=None, message_type='chat'):
        """Sends a simple message to the specified user."""
        mess = self.build_message(text)
        mess.setTo(user)

        if in_reply_to:
            mess.setThread(in_reply_to.getThread())
            mess.setType(in_reply_to.getType())
        else:
            mess.setThread(self.__threads.get(user, None))
            mess.setType(message_type)

        self.send_message(mess)

    def send_simple_reply(self, mess, text, private=False):
        """Send a simple response to a message"""
        if not self.muted:
            self.send_message(self.build_reply(mess, text, private))
        else:
            if private:
                self.send_message(self.build_reply(mess, text, private))

    def build_reply(self, mess, text=None, private=False):
        """Build a message for responding to another message.
        Message is NOT sent"""
        response = self.build_message(text)
        if private:
            response.setTo(mess.getFrom())
            response.setType('chat')
        else:
            response.setTo(mess.getFrom().getStripped())
            response.setType(mess.getType())
        response.setThread(mess.getThread())
        return response

    def encode_message(self, content):
        """Encodes the text as needed"""
        # cgi.escape(unicode(str(line), "utf-8")).encode('ascii', 'xmlcharrefreplace')  #nohtml
        if isinstance(content, str):
            self.log.debug('Content is string: %s' % (content))
            unicode_content = content.decode('utf-8')

        elif isinstance(content, unicode):
            self.log.debug('Content is unicode: %s' % (content))
            unicode_content = content
        else:
            self.log.warning('Content is no string: %s' % (content))
            unicode_content = content

        return unicode_content #.encode('ascii', 'replace')


    def build_message(self, text):
        """Builds an xhtml message without attributes.
        If input is not valid xhtml-im fallback to normal."""
        plain_message = text
        if isinstance(text, list):
            plain_message = '\n'.join(text)
        plain_message = re.sub(r'<[^>]+>', '', plain_message)
        message = xmpp.protocol.Message(body=plain_message)

        html = xmpp.Node('html', {'xmlns': 'http://jabber.org/protocol/xhtml-im'})
        html_message = ""

        if isinstance(text, list):
            html_message = '<br />'.join(text)
        else:
            html_message = text

        try:
            html_message = "<span style='color: #%s'>" % self.text_color + html_message + "</span>"
            html_message = self.encode_message("<body xmlns='http://www.w3.org/1999/xhtml'>" + html_message + "</body>")
            html_message = html_message.encode('utf-8')
            html.addChild(node=xmpp.simplexml.XML2Node(html_message))
            message.addChild(node=html)
        except Exception, e:
            self.log.warning('Error while building XHTML message with %s: %s' % (html_message, e))

        return message

    def broadcast(self, message, only_available=False):
        """Broadcast a message to all users 'seen' by this bot.

        If the parameter 'only_available' is True, the broadcast
        will not go to users whose status is not 'Available'."""
        for jid, (show, status) in self.__seen.items():
            if not only_available or show is self.AVAILABLE:
                self.send(jid, message)

    ########## Calbacks ##########
    def callback_presence(self, conn, presence):
        jid, type_, show, status = presence.getFrom(), \
                presence.getType(), presence.getShow(), \
                presence.getStatus()
        who = str(presence.getFrom())

        if self.jid.bareMatch(jid):
            # update internal status
            if type_ != self.OFFLINE:
               self.__status = status
               self.__show = show
            else:
               self.__status = ""
               self.__show = self.OFFLINE
            if not self.__acceptownmsgs:
               # Ignore our own presence messages
               return

        if type_ is None:
            # Keep track of status message and type changes
            old_show, old_status = self.__seen.get(jid, (self.OFFLINE, None))
            if old_show != show:
                self.status_type_changed(jid, show)

            if old_status != status:
                self.status_message_changed(jid, status)

            self.__seen[jid] = (show, status)
        elif type_ == self.OFFLINE and jid in self.__seen:
            # Notify of user offline status change
            del self.__seen[jid]
            self.status_type_changed(jid, self.OFFLINE)

        try:
            subscription = self.roster.getSubscription(unicode(jid.__str__()))
        except KeyError, e:
            # User not on our roster
            subscription = None
        except AttributeError, e:
            # Recieved presence update before roster built
            return

        if type_ == 'error':
            self.log.error(presence.getError())

        self.log.debug('Got presence: %s (type: %s, show: %s, status: %s, '\
            'subscription: %s)' % (jid, type_, show, status, subscription))
        # If subscription is private,
        # disregard anything not from the private domain
        if self.__privatedomain and type_ in ('subscribe', 'subscribed', \
            'unsubscribe'):
            if self.__privatedomain == True:
                # Use the bot's domain
                domain = self.jid.getDomain()
            else:
                # Use the specified domain
                domain = self.__privatedomain

            # Check if the sender is in the private domain
            user_domain = jid.getDomain()
            if domain != user_domain:
                self.log.info('Ignoring subscribe request: %s does not '\
                'match private domain (%s)' % (user_domain, domain))
                return

        if type_ == 'subscribe':
            # Incoming presence subscription request
            if subscription in ('to', 'both', 'from'):
                self.roster.Authorize(jid)
                self._send_status()

            if subscription not in ('to', 'both'):
                self.roster.Subscribe(jid)

            if subscription in (None, 'none'):
                self.send(jid, self.MSG_AUTHORIZE_ME)
        elif type_ == 'subscribed':
            # Authorize any pending requests for that JID
            self.roster.Authorize(jid)
        elif type_ == 'unsubscribed':
            # Authorization was not granted
            self.send(jid, self.MSG_NOT_AUTHORIZED)
            self.roster.Unauthorize(jid)
        elif type_ == 'unavailable':
            self.log.warning("Remove online user: %s" % (who))
            try:
                del self.muc_users[who]
            except Exception as e:
                self.log.warning("Remove online user error: %s" % (e))
        else:
            if presence.getJid():
                # print "presence.getJid(): %s" % presence.getJid()
                # print "self.jid: %s" % self.jid
                myself = False
                for room in self.muc_channels:
                    if who == "%s/%s" % (room, self.nickname):
                        myself = True
                if not myself:
                # try:
                #     srcJid = presence.getJid().split('/')[0]
                # except KeyError:
                #     srcJid = False
                # if srcJid:
                    # if srcJid != self.jid:
                    try:
                        # status = self.roster.getShow(presence.getJid())
                        status = presence.getShow()
                        # print "%s -> %s" % (who, status)
                    except KeyError:
                        status = False
                    if status in [None, 'chat']:
                        self.log.info("User now available (online, chat): %s" % (who))
                        self.muc_users[who] = presence.getJid()
                    elif status in ['xa', 'away', 'dnd']:
                        self.log.info("User now unavailable (offline, afk, dnd): %s" % (who))
                        try:
                            del self.muc_users[who]
                        except Exception as e:
                            self.log.info("Remove online user error: %s" % (e))
                else:
                    self.log.info("Ignoring myself")
        self.log.info("Users online: %s" % (' '.join(self.muc_users)))

    def callback_message(self, conn, mess):
        """Messages sent to the bot will arrive here.
        Command handling + routing is done in this function."""

        # Prepare to handle either private chats or group chats
        type = mess.getType()
        jid = mess.getFrom()
        props = mess.getProperties()
        text = mess.getBody()
        username = self.get_sender_username(mess)


        if type not in ("groupchat", "chat"):
            self.log.debug("unhandled message type: %s" % type)
            return

        # Ignore messages from before we joined
        if xmpp.NS_DELAY in props: return

        # Ignore messages from myself
        if self.jid.bareMatch(jid): return

        self.log.debug("*** props = %s" % props)
        self.log.debug("*** jid = %s" % jid)
        self.log.debug("*** username = %s" % username)
        self.log.debug("*** type = %s" % type)
        self.log.debug("*** text = %s" % text)

        # If a message format is not supported (eg. encrypted),
        # txt will be None
        if not text: return

        # Ignore messages from users not seen by this bot
        if jid not in self.__seen:
            self.log.info('Ignoring message from unseen guest: %s' % jid)
            self.log.debug("I've seen: %s" %
                ["%s" % x for x in self.__seen.keys()])
            return

        # Remember the last-talked-in message thread for replies
        # FIXME i am not threadsafe
        self.__threads[jid] = mess.getThread()

        jid_string = '{0}'.format(jid).lower()
        channel = jid_string.split('/')[0]
        botname1 = '{0}/{1}'.format(channel, self.__username).lower()
        botname2 = '{0}/{1}'.format(channel, self.__username.split('@')[0]).lower()

        if (jid_string != botname1) and (jid_string != botname2):
            if text[0] == '!':
                text = self.nickname + ' ' + text[1:]
            if text[0] in ['@', '!']:
                text = text[1:]
            if text[0:len(self.nickname)].lower() == self.nickname.lower():
                text_without_nickname = text[(len(self.nickname) + 1):]
                if ' ' in text_without_nickname:
                    command, args = text_without_nickname.split(' ', 1)
                else:
                    command, args = text_without_nickname, ''

                args = args.encode('utf-8')

                cmd = command.lower()

                if self.commands.has_key(cmd):
                    def execute_and_send():
                        try:
                            reply = self.commands[cmd](mess, args)
                            if reply:
                                self.send_simple_reply(mess, reply)
                        except Exception, e:
                            self.log.exception('An error happened while processing '\
                                'a message ("%s") from %s: %s"' %
                                (text, jid, traceback.format_exc(e)))
                    execute_and_send()
            else:
                self.on_not_a_command(mess)

    ########## Bot Thread Methods ##########
    def idle_proc(self):
        """This function will be called in the main loop."""
        self._idle_ping()

    def _idle_ping(self):
        """Pings the server, calls on_ping_timeout() on no response.

        To enable set self.PING_FREQUENCY to a value higher than zero.
        """
        if self.PING_FREQUENCY \
            and time.time() - self.__lastping > self.PING_FREQUENCY:
            self.__lastping = time.time()
            #logging.debug('Pinging the server.')
            ping = xmpp.Protocol('iq', typ='get', \
                payload=[xmpp.Node('ping', attrs={'xmlns':'urn:xmpp:ping'})])
            try:
                res = self.conn.SendAndWaitForResponse(ping, self.PING_TIMEOUT)
                #logging.debug('Got response: ' + str(res))
                if res is None:
                    self.on_ping_timeout()
            except IOError, e:
                logging.error('Error pinging the server: %s, '\
                    'treating as ping timeout.' % e)
                self.on_ping_timeout()

    def on_ping_timeout(self):
        logging.info('Terminating due to PING timeout.')
        self.quitBot()

    def shutdown(self):
        """This function will be called when we're done serving

        Override this method in derived class if you
        want to do anything special at shutdown.
        """
        pass

    def serve_forever(self, connect_callback=None, disconnect_callback=None):
        """Connects to the server and handles messages."""
        conn = self.connect()
        if conn:
            self.log.info('bot connected. serving forever.')
        else:
            self.log.warn('could not connect to server - aborting.')
            return

        if connect_callback:
            connect_callback()
        self.__lastping = time.time()

        while not self.__finished:
            try:
                conn.Process(1)
                self.idle_proc()
            except KeyboardInterrupt:
                self.log.info('bot stopped by user request. '\
                    'shutting down.')
                break

        self.shutdown()

        if disconnect_callback:
            disconnect_callback()


    ########## Events ##########
    def do_kick(self, room, nick, reason=None):
        """Kicks user from muc
        Works only with sufficient rights."""
        NS_MUCADMIN = 'http://jabber.org/protocol/muc#admin'
        item = xmpp.simplexml.Node('item')
        item.setAttr('nick', nick)
        item.setAttr('role', 'none')
        iq = xmpp.Iq(typ='set',queryNS=NS_MUCADMIN,xmlns=None,to=room,payload=set([item]))
        if reason is not None:
            item.setTagData('reason',reason)
        self.connect().send(iq)

    def do_topic(self, room):
        newTopic = [self.userTopic]
        count = 0
        for (ts, topic) in sorted(self.countTopic):
            count += 1
            if count > 4:
                break
            newTopic.append(topic)

        newTmpTopic = ' | '.join(newTopic)
        if newTmpTopic != self.currentTopic:
            self.currentTopic = newTmpTopic

            subject = xmpp.simplexml.Node('subject', payload=set([newTmpTopic]))
            mess = xmpp.Message(to=room, xmlns=None, typ='groupchat', payload=set([subject]))
            self.connect().send(mess)

    def do_invite(self, room, jid, reason=None):
        """Invites user to muc.
        Works only if user has permission to invite to muc"""
        NS_MUCUSER = 'http://jabber.org/protocol/muc#user'
        invite = xmpp.simplexml.Node('invite')
        invite.setAttr('to',jid)
        if reason is not None:
           invite.setTagData('reason',reason)
        mess = xmpp.Message(to=room)
        mess.setTag('x',namespace=NS_MUCUSER).addChild(node=invite)
        self.log.error(mess)
        self.connect().send(mess)

    #FIXME rename!
    def status_type_changed(self, jid, new_status_type):
        """Callback for tracking status types (dnd, away, offline, ...)"""
        self.log.debug('user %s changed status to %s' % (jid, new_status_type))
        status = "{0}".format(new_status_type)
        if status == 'None':
            self.on_came_online(jid)
        elif status == 'unavailable':
            self.on_gone_offline(jid)

    #FIXME rename!
    def status_message_changed(self, jid, new_status_message):
        """Callback for tracking status messages (the free-form status text)"""
        self.log.debug('user %s updated text to %s' %
            (jid, new_status_message))

    def on_not_a_command(self, mess):
        """plix overwrite me"""
        self.log.debug("on not a command called")

    def on_came_online(self, jid):
        """plix overwrite me"""
        self.log.debug("{0} came online".format(jid))

    def on_gone_offline(self, jid):
        """plix overwrite me"""
        self.log.debug("{0} gone offline".format(jid))

    def get_my_username(self):
        return self.nickname

    ###### Helper methods (mostly taken from JamesII https://github.com/oxivanisher/JamesII/blob/master/src/james/jamesutils.py) ########
    def getAge(self, timestamp):
        age = int(time.time() - timestamp)

        if age < 0:
            age = age * -1

        if age == 0:
            return ''

        elif age == 1:
            return _('1 second')
        elif age < 60:
            return _('{0} seconds').format(age)

        elif age == 60:
            return _('1 minute')
        elif age > 60 and age < 3600:
            return _('{0} minutes').format(int(age / 60))

        elif age >= 3600 and age < 7200:
            return _('1 hour')
        elif age >= 7200 and age < 86400:
            return _('{0} hours').format(int(age / 3600))

        elif age >= 86400 and age < 172300:
            return _('1 day')
        elif age >= 172300 and age < 604800:
            return _('{0} days').format(int(age / 86400))

        elif age >= 604800 and age < 1209600:
            return _('1 week')
        elif age >= 1209600 and age < 31449600:
            return _('{0} weeks').format(int(age / 604800))

        elif age >= 31449600 and age < 62899200:
            return _('1 year')
        else:
            return _('{0} years').format(int(age / 31449600))

    def convert_from_unicode(self, data):
        if isinstance(data, unicode):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(self.convert_from_unicode, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self.convert_from_unicode, data))
        else:
            return data

    def list_unicode_cleanup(self, data):
        args = [s.encode('utf-8', errors='ignore').strip() for s in data]
        args = filter(lambda s: s != '', args)
        return args

    def time_string2seconds(self, arg):
        # converts 12:22 and 12:22:33 into seconds
        seconds = 0
        minutes = 0
        hours = 0
        try:
            if arg.count(':') == 2:
                data = arg.split(':')
                seconds = int(data[2])
                minutes = int(data[1])
                hours = int(data[0])
            elif arg.count(':') == 1:
                data = arg.split(':')
                minutes = int(data[1])
                hours = int(data[0])
        except Exception as e:
            pass
        return (hours * 3600 + minutes * 60 + int(seconds))

    def date_string2values(self, arg):
        # converts dd.mm.yyyy into [yyyy, mm, dd]
        try:
            data = arg.split('.')
            if int(data[0]) > 0 and int(data[0]) < 32:
                if int(data[1]) > 0 and int(data[1]) < 13:
                    if int(data[2]) > 1969:
                        return [int(data[2]), int(data[1]), int(data[0])]
        except Exception as e:
            return False

########## Decorator for Bot Command Functions ##########
def botcmd(*args, **kwargs):
    """Decorator for bot command functions"""

    def decorate(func, hidden=False, name=None, thread=False):
        setattr(func, '_jabberbot_command', True)
        setattr(func, '_jabberbot_command_hidden', hidden)
        setattr(func, '_jabberbot_command_name', name or func.__name__)
        setattr(func, '_jabberbot_command_thread', thread) # Experimental!
        return func

    if len(args):
        return decorate(args[0], **kwargs)
    else:
        return lambda func: decorate(func, **kwargs)