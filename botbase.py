#!/usr/bin/python

import os
import re
import sys
import thread

import time
import inspect
import logging
import traceback
import atexit

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

    # UI-messages (overwrite to change content)
    MSG_AUTHORIZE_ME = 'Hey there. You are not yet on my roster. Authorize my request and I will do the same.'
    MSG_NOT_AUTHORIZED = 'You did not authorize my subscription request. Access denied.'
    MSG_UNKNOWN_COMMAND = 'Unknown command: "%(command)s". Type "help" for available commands.'
    MSG_HELP_TAIL = 'Type help <command name> to get more info about that specific command.'
    MSG_HELP_UNDEFINED_COMMAND = 'That command is not defined.'
    MSG_ERROR_OCCURRED = 'Sorry for your inconvenience. An unexpected error occurred.'

    PING_FREQUENCY = 0 # Set to the number of seconds, e.g. 60.
    PING_TIMEOUT = 2 # Seconds to wait for a response.

    ########## Constructor ##########   
    def __init__(self, username, password, candy_colors=False, res=None, debug=False, privatedomain=False, acceptownmsgs=False, handlers=None):
        # TODO sort this initialisation thematically
        self.__debug = debug
        self.log = logging.getLogger(__name__)
        self.__username = username
        self.__password = password
        self.jid = xmpp.JID(self.__username)
        self.res = (res or self.__class__.__name__)
        self.conn = None
        self.__finished = False
        self.__show = None
        self.__status = None
        self.__seen = {}
        self.__threads = {}
        self.__lastping = time.time()
        self.__privatedomain = privatedomain
        self.__acceptownmsgs = acceptownmsgs
        self.candy_colors = candy_colors
        self.memList = {}
        self.afkList = {}
        self.reminderDict = {}

        atexit.register(self.saveLists)

        #FIXME load saved lists

        self.handlers = (handlers or [('message', self.callback_message), ('presence', self.callback_presence)])

        # Collect commands from source
        self.commands = {}
        for name, value in inspect.getmembers(self, inspect.ismethod):
            if getattr(value, '_jabberbot_command', False):
                name = getattr(value, '_jabberbot_command_name')
                self.log.info('Registered command: %s' % name)
                self.commands[name] = value

        self.roster = None


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

    # This must become private!
    def get_csv_admin_users_handler(self):
        return open('db/admins.csv', 'rb')

    # This must become private!
    def get_handler_csv_urls_write(self):
        return open('db/urls.csv', 'ab')

    # This must become private!
    def get_handler_csv_urls_read(self):
        return open('db/urls.csv', 'rb')

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
                self.log.error('unable to connect to server %s.' % self.jid.getDomain())
                return None
            if conres != 'tls':
                self.log.warning('unable to establish secure connection '\
                '- TLS failed!')

            authres = conn.auth(self.jid.getNode(), self.__password, self.res)
            if not authres:
                self.log.error('unable to authorize with server.')
                return None
            if authres != 'sasl':
                self.log.warning("unable to perform SASL auth on %s. "\
                "Old authentication method used!" % self.jid.getDomain())

            # Connection established - save connection
            self.conn = conn

            # Send initial presence stanza (say hello to everyone)
            self.conn.sendInitPresence()
            # Save roster and log Items
            self.roster = self.conn.Roster.getRoster()
            self.log.info('*** roster ***')
            for contact in self.roster.getItems():
                self.log.info('  %s' % contact)
            self.log.info('*** roster ***')

            # Register given handlers (TODO move to own function)
            for (handler, callback) in self.handlers:
                self.conn.RegisterHandler(handler, callback)
                self.log.debug('Registered handler: %s' % handler)

        return self.conn


    def join_room(self, room, nickname, username=None, password=None):
        self.__nickname = nickname
        """Join the specified multi-user chat room

        If username is NOT provided fallback to node part of JID"""
        # TODO fix namespacestrings and history settings
        NS_MUC = 'http://jabber.org/protocol/muc'
        username = nickname
        if username is None:
        # TODO use xmpppy function getNode
            username = self.__username.split('@')[0]
        my_room_JID = '/'.join((room, username))
        pres = xmpp.Presence(to=my_room_JID)
        if password is not None:
            pres.setTag('x',namespace=NS_MUC).setTagData('password',password)
        self.connect().send(pres)

    def quit(self):
       self.__finished = True

    def send_message(self, mess):
        """Send an XMPP message"""
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

    def build_message(self, text):
        """Builds an xhtml message without attributes.
        If input is not valid xhtml-im fallback to normal."""
        message = None # init message variable
        # Try to determine if text has xhtml-tags - TODO needs improvement
        text_plain = re.sub(r'<[^>]+>', '', text)
        if text_plain != text:
            # Create body w stripped tags for reciptiens w/o xhtml-abilities
            # FIXME unescape &quot; etc.
            if self.candy_colors:
                message_text = '|c:7|' + text_plain
            else:
                message_text = text_plain
            message = xmpp.protocol.Message(body=message_text)
            # Start creating a xhtml body
            html = xmpp.Node('html', \
                {'xmlns': 'http://jabber.org/protocol/xhtml-im'})
            try:
                html.addChild(node=xmpp.simplexml.XML2Node( \
                    "<body xmlns='http://www.w3.org/1999/xhtml'>" + \
                    text.encode('utf-8') + "</body>"))
                message.addChild(node=html)
            except Exception, e:
                # Didn't work, incorrect markup or something.
                self.log.debug('An error while building a xhtml message. '\
                'Fallback to normal messagebody')
                # Fallback - don't sanitize invalid input. User is responsible!
                message = None
        if message is None:
        # Normal body
            if self.candy_colors:
                message_text = '|c:7|' + text
            else:
                message_text = text
            message = xmpp.protocol.Message(body=message_text)
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

        jid_string = '{0}'.format(jid)
        channel = jid_string.split('/')[0]
        botname1 = '{0}/{1}'.format(channel, self.__username)
        botname2 = '{0}/{1}'.format(channel, self.__username.split('@')[0])

        """ remove colors """
        if text[0:3] == '|c:':
            text = text[5:]

        if (jid_string != botname1) and (jid_string != botname2):
            if text[0:4] == 'gabi':
                text_without_gabi = text[5:]
                if ' ' in text_without_gabi:
                    command, args = text_without_gabi.split(' ', 1)
                else:
                    command, args = text_without_gabi, ''

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
        self.quit()

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

    def do_topic(self, room, topic):
        subject = xmpp.simplexml.Node('subject', payload=set([topic]))
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
        return self.__nickname


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

########## Save Functions ##########
def saveLists(self):
    self.memList = {}
    self.afkList = {}
    self.reminderDict = {}

    # try:
    #     file = open(self.command_cron_file, 'w')
    #     file.write(json.dumps(self.cron_list))
    #     file.close()
    #     self.logger.debug("Saving crontab to %s" % (self.command_cron_file))
    # except IOError:
    #     self.logger.warning("Could not safe cron tab to file!")

    pass