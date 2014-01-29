#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import datetime
import time
import calendar
import atexit
import json
import collections
import pytz
import urllib2
import socket
import cgi

timeout = 5
socket.setdefaulttimeout(timeout)

from botbase import BotBase, botcmd


def formatTimeText(var, singular, plural):
    if var == 1:
        return ("%s %s" % (var, singular))
    elif var > 1:
        return ("%s %s" % (var, plural))
    else:
        return False

class GabiCustom(BotBase):

    def __init__(self, username, password, timezone='UTC', candy_colors=False, res=None, debug=False, privatedomain=False, acceptownmsgs=False, handlers=None):
        super(GabiCustom, self).__init__(username, password, timezone, candy_colors, res, debug, privatedomain, acceptownmsgs, handlers)

        self.lastSeenDict = self.loadJSON('save_lastSeen.dat', {})
        atexit.register(self.saveJSON, 'save_lastSeen.dat', self.lastSeenDict)
        self.usersNowOffline = {}

        self.memDict = self.loadJSON('save_memo.dat', {})
        atexit.register(self.saveJSON, 'save_memo.dat', self.memDict)

        self.afkDict = self.loadJSON('save_afk.dat', {})
        atexit.register(self.saveJSON, 'save_afk.dat', self.afkDict)

        self.reminderDict = self.loadJSON('save_reminder.dat', {})
        atexit.register(self.saveJSON, 'save_reminder.dat', self.reminderDict)

        self.cowntdownList = self.loadJSON('save_count.dat', [])
        atexit.register(self.saveJSON, 'save_count.dat', self.cowntdownList)

        self.urlList = self.loadJSON('save_urls.dat', [])
        atexit.register(self.saveJSON, 'save_urls.dat', self.urlList)

        self.afkRejoinTime = 900

        self.periodicCountLastCheck = 0
        self.periodicCountWaitTime = 3600
        self.periodicCountCheckTs = {}

        self.countTopic = []

        self.imgEndings = {'.gif' : 'Image: Graphics Interchange Format (GIF)', 
                           '.jpg' : 'Image: Joint Photographic Experts Group (JPG)',
                           '.jpeg': 'Image: Joint Photographic Experts Group (JPEG)',
                           '.tiff': 'Image: Portable Network Graphics (TIFF)',
                           '.png' : 'Image: Tagged Image File Format (PNG)',
                           '.mkv' : 'Video: Matroska (MKV)',
                           '.mk3d': 'Video: Matroska (MK3D)',
                           '.mka' : 'Audio: Matroska (MKA)',
                           '.mks' : 'Video: Matroska (MKS)',
                           '.ogg' : 'Audio: Ogg Vorbis (OGG)',
                           '.oga' : 'Audio: Ogg Vorbis (OGA)',
                           '.ogv' : 'Audio: Ogg Vorbis (OGV)',
                           '.ogx' : 'Audio: Ogg Vorbis (OGX)',
                           '.wmv' : 'Video: Windows Media Video (WMV)',
                           '.flac': 'Audio: Free Lossless Audio Codec (FLAC)',
                           '.mpg' : 'Video: Moving Picture Experts Group (MPG)',
                           '.mpeg': 'Video: Moving Picture Experts Group (MPEG)',
                           '.m4v' : 'Video: Moving Picture Experts Group (M4V)',
                           '.m4a' : 'Audio: Moving Picture Experts Group (M4A)',
                           '.m4b' : 'Audio: Moving Picture Experts Group (M4B)',
                           '.m4p' : 'Audio: Moving Picture Experts Group (M4P)',
                           '.m4r' : 'Audio: Moving Picture Experts Group (M4R)',
                           '.mp4' : 'Video: Moving Picture Experts Group (MP4)',
                           '.mp3' : 'Audio: Moving Picture Experts Group (MP3)',
                           '.pdf' : 'Document: Portable Document Format (PDF)',
                           '.doc' : 'Document: Microsoft Word Format (DOC)',
                           '.docx': 'Document: Microsoft Word Format (DOCX)',
                           '.ppt' : 'Document: Microsoft Power Point Format (PPT)',
                           '.xls' : 'Document: Microsoft Excel (XLS)',
                           '.xlsx': 'Document: Microsoft Excel (XLSX)',
                           '.odt' : 'Document: Open Document Format Text (ODT)',
                           '.ods' : 'Document: Open Document Format Sheet (ODS)',
                           '.odp' : 'Document: Open Document Format Presentation (ODP)',
                           '.odg' : 'Document: Open Document Format Graphic (ODG)',
                           '.avi' : 'Video: Audio Video Interleave (AVI)' }

    def on_not_a_command(self, mess):
        type = mess.getType()
        jid = mess.getFrom()
        props = mess.getProperties()
        text = mess.getBody()
        username = self.get_sender_username(mess)

        if username == self.get_my_username():
            return

        #fangen wir mal an mit gucken ob der bb oder was sagen will
        reg_ex_bb = (r".*?bb$", r".*?bin mal weg.*?", r".*?baba")
        for reg in reg_ex_bb:
            c = re.compile(reg)
            if c.match(text) != None:
                self.send_simple_reply(mess, _("Have fun, {0}!").format(username))
                return

        #fangen wir mal an mit gucken ob wer re sagt        
        reg_ex_re = (r"^\|c\:[0-9]\|re$", r"^rehor$", r"^\|c\:[0-9]\|rehor$", r"^re$")
        for reg in reg_ex_re:
            c = re.compile(reg)
            if c.match(text) != None:
                if username in self.afkDict:
                    self.send_simple_reply(mess, _("wb {0}! How was {1}?").format(username, self.afkDict[username]))
                    del self.afkDict[username];
                else:
                    self.send_simple_reply(mess, "wb {0}!".format(username))
                return

        #tippfehlerkontrolle
        reg_ex_ac = (r".*?amche", r".*?shcon", r".*?acuh", r".*?dsa", r".*?cih", r".*?ihc", r".*?psi", r".*?issue")
        autoCorr = { '.*?amche' : 'mache', '.*?shcon': 'schon', '.*?acuh': 'auch', '.*?dsa': 'das', '.*?cih': 'ich', '.*?ihc': 'ich', '.*?psi' : 'gajim', '.*?issue' : 'skischuh' }
        for reg in reg_ex_ac:
            c = re.compile(reg)
            if c.match(text) != None:
                self.send_simple_reply(mess, _('{0} wanted to say "{1}".').format(username, autoCorr[reg]))                    
                    
                return

        #fangen wir mal an mit gucken ob wer penis sagt
        reg_ex_pn = (r".*?penis", r".*?Penis")
        for reg in reg_ex_pn:
            c = re.compile(reg)
            if c.match(text) != None:
                self.send_simple_reply(mess, _("Hihihi, {0} said penis!").format(username))
                return
                    
        #fangen wir mal an mit gucken ob wer Guten Morgen sagt
        reg_ex_pn = (r".*?Guten Morgen", r".*?guten morgen", r".*?Moinz", r".*?moinz", r".*?morning", r".*?good morning")
        for reg in reg_ex_pn:
            c = re.compile(reg)
            if c.match(text) != None:
                now = datetime.datetime.now(pytz.timezone(self.timezone))
                if now.hour > 10:
                    self.send_simple_reply(mess, _("Morning? Check your clock, {0}!").format(username), True)
                else:
                    self.send_simple_reply(mess, _("Good morning, {0}. Nice to see you here.").format(username), True)
                    return

        #so jetzt alle URLS
        reg_ex_url = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        c = re.compile(reg_ex_url)
        writer = None
        handler = None

        
        for url in c.findall(text):
            url = url.strip()

            htmlTitle = None
            for ending in self.imgEndings.keys():
                if url.lower().endswith(ending):
                    htmlTitle = self.imgEndings[ending]


            if not htmlTitle:
                req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 

                try:
                    response = urllib2.urlopen(req)
                    html = response.read()
                    titleRE = re.compile("<title>(.+?)</title>")
                    htmlTitle = titleRE.search(html).group(1)
                except urllib2.HTTPError as e:
                    self.log.warning("URL Error %s on URL: %s" % (e.code, url))
                    if e.code == 404:
                        continue
                except:
                    pass

            if htmlTitle:
                # self.send_simple_reply(mess, _("URL title from {0}: <a href='{2}' target='_blank'>{1}</a>").format(username, htmlTitle, url))
                pass
            else:
                htmlTitle = ""

            newUrl = True
            for (oldUsername, timestamp, oldUrl, title) in self.urlList:
                if url in oldUrl:
                    newUrl = False

            if newUrl:
                self.urlList.append((username, str(datetime.datetime.now(pytz.timezone(self.timezone))), url, htmlTitle))

        if writer != None:
            handler.close()

        # haben wir einen count zum anzeigen?
        periodicCount = self.periodicCheckCount(mess)
        if periodicCount:
            self.send_simple_reply(mess, '\n'.join(periodicCount))

    def on_came_online(self, jid):

        #ignore if we just started up
        if (self.readyTs + 3) > time.time():
            return

        strJID = '%s' % jid
        room = self.list_unicode_cleanup(strJID.split('/'))[0]
        user = self.list_unicode_cleanup(strJID.split('/'))[1]

        if user != self.get_my_username():

            # LastSeen
            age = 0
            if not self.usersNowOffline.has_key(user):
                self.usersNowOffline[user] = True
            userWasOffline = self.usersNowOffline[user]
            self.usersNowOffline[user] = False

            try:
                if self.lastSeenDict[user] > 0:
                    age = self.lastSeenDict[user]
            except Exception:
                pass
            self.lastSeenDict[user] = int(time.time())

            if userWasOffline:
                hallo = []
                if age > 0:
                    if (int(time.time()) - age) > self.afkRejoinTime:
                        hallo.append(_('Welcome back {0}, i saw you last {1} ago.').format(user, self.getAge(age)))
                else:
                    hallo.append(_('Hello {0}, i see you for the first time. I am {1} the Robot-Human-Contacter.').format(user, self.nickname))
                    hallo.append(_('Enter "{0} help" or "!help" for help.').format(self.nickname))

                if user in self.afkDict:
                    hallo.append(_("How was {0}?").format(self.afkDict[user]))
                    del self.afkDict[user];

                if len(hallo) > 0:
                    self.send(room, '\n'.join(hallo), None, 'groupchat')

            # Reminder
            if self.reminderDict.has_key(user.lower()):
                if len(self.reminderDict[user.lower()]) > 0:
                    reminderMessage = _('{0}, I have to tell you:').format(user) + '\n'
                    for (sender, message, timestamp) in self.reminderDict[user.lower()]:
                        reminderMessage += _('From {0} {1} ago: {2}').format(sender, self.getAge(timestamp), message) + '\n'

                    self.reminderDict[user.lower()] = []
                    self.send(room, reminderMessage, None, 'groupchat')
                    

    def on_gone_offline(self, jid):
        strJID = '%s' % jid
        # room = self.list_unicode_cleanup(strJID.split('/'))[0]
        user = self.list_unicode_cleanup(strJID.split('/'))[1]

        if user != self.get_my_username():
            self.lastSeenDict[user] = int(time.time())
            self.usersNowOffline[user] = True

            # hallo = 'Und da ist {0} weg'.format(user)
            #self.send(room, hallo, None, 'groupchat')

    # LastSeen Methods
    @botcmd
    def last (self, mess, args):
        """When was a user last seen"""
        if not args:
            ret = ''
            for name in self.lastSeenDict.keys():
                ret = ret + _('{0} {1} ago').format(name, self.getAge(self.lastSeenDict[name])) + '\n'
            return ret
        else:
            lastSeen = 0
            for name in self.lastSeenDict.keys():
                if name.lower() == args.lower():
                    lastSeen = self.lastSeenDict[name]
                    userName = name

            if lastSeen > 0:
                self.send_simple_reply(mess, _('{0} was last seen {1} ago.').format(userName, self.getAge(lastSeen)), True)
            else:
                self.send_simple_reply(mess, _('{0}, I did never see {1}.').format(self.get_sender_username(mess), args), True)

    # Memo Methods
    @botcmd
    def memo (self, mess, args):
        """Memorize something"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            self.memDict[username] = args;
            self.send_simple_reply(mess, _('I memorized now: "{0}".').format(args), True)
        elif username in self.memDict:
            self.send_simple_reply(mess, _('Your memo: "{0}".').format(self.memDict[username]), True)
        else:
            self.send_simple_reply(mess, _('What should i memorize?'), True)

    #AFK Methods
    @botcmd
    def afk (self, mess, args):
        """Save AFK message"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            message = args
        else:
            message = "AFK"
        self.afkDict[username] = message

        if username != self.get_my_username():
            self.lastSeenDict[username] = int(time.time())
            self.usersNowOffline[username] = True

        self.send_simple_reply(mess, _('See you later, {0}. Have fun at {1}.').format(username, message), False)

    @botcmd
    def whoafk (self, mess, args):
        """Show AFK message"""
        if len(self.afkDict) > 0:
            ret = ''
            for username in self.afkDict.keys():
                ret = ret + "\n%-10s: %s" % (username, self.afkDict[username])
            self.send_simple_reply(mess, ret, True)
        else:
            self.send_simple_reply(mess, _('Nobody left any message.'), True)

    #Reminder Methods
    @botcmd
    def remind (self, mess, args):
        """Remind a user with something when he comes back"""
        from_username = self.get_sender_username(mess)
        new_args = args.split(" ")

        if len(args) > 1:
            target_user = new_args[0]
            target_message = ' '.join(new_args[1:])

            ret_message = _('I will tell {0}: {1}').format(target_user, target_message)

            if not self.reminderDict.has_key(target_user.lower()):
                self.reminderDict[target_user.lower()] = []
            self.reminderDict[target_user.lower()].append((from_username, target_message, int(time.time())))

        else:
            ret_message = _("You have to enter a name followed by the message.")
        self.send_simple_reply(mess, ret_message, True)

    #Cowntdown Methods
    @botcmd
    def count (self, mess, args):
        # self.cowntdownList = (targetTime, longterm (y/n), fromuser, what)
        """Saves a cowntdown to a specified date/time"""
        from_username = self.get_sender_username(mess)
        args = args.split(" ")
        ret_message = [_("Commands for count are: add, list, del")]

        if args[0].lower() == "add":
            args = args[1:]
            target_time = datetime.datetime.now()
            day = 0
            month = 0
            year = 0
            target_timestamp = None
            try:
                target_timestamp = int(args[0])
                args = args[1:]
            except Exception as e:
                pass

            if not target_timestamp:
                longterm = False
                try:
                    time_date = self.date_string2values(args[0])
                    target_time = target_time.replace(year  = time_date[0])
                    target_time = target_time.replace(month = time_date[1])
                    target_time = target_time.replace(day   = time_date[2])
                    longterm = True
                    args = args[1:]
                except Exception as e:
                    pass

                try:
                    time_sec = self.time_string2seconds(args[0])
                    hour = int(time_sec / 3600)
                    minute = int((time_sec - hour * 3600) / 60)
                    second = int(time_sec % 60)
                    target_time = target_time.replace(hour   = hour)
                    target_time = target_time.replace(minute = minute)
                    target_time = target_time.replace(second = second)
                    # print "%sh %sm %ss" % (hour, minute, second)
                    if (hour + minute + second) != 0:
                        args = args[1:]
                        if not longterm:
                            targetTs = calendar.timegm(target_time.utctimetuple())
                            # print targetTs
                            # print now
                            if targetTs < now:
                                target_time.fromtimestamp(targetTs + 86400)

                except Exception as e:
                    pass

                target_timestamp = int(target_time.strftime('%s'))

                if target_timestamp > 0 and len(args) > 0:
                    # return [self.timer_at(target_timestamp, args)]
                    self.cowntdownList.append((target_timestamp, longterm, from_username, ' '.join(args)))
                    ret_message.append(_("Count saved for '{0}' ({1})").format(' '.join(args), target_time.strftime("%a, %d %b %Y %H:%M:%S")))
                    # print target_time.strftime("%s")
                else:
                    args = []
                    ret_message.append(_("You have to enter time/date and an event. Examples:"))
                    ret_message.append(_("{0} count add 18:15 It is a quarter past 6").format(self.nickname))
                    ret_message.append(_("{0} count add 31.12.2014 23:59 The old year is history").format(self.nickname))
        elif args[0].lower() == "list":
            ret_message = [_('The following counts are set:')]
            count = 0
            for (timestamp, longterm, user, message) in self.cowntdownList:
                count += 1
                target_time = datetime.datetime.fromtimestamp(timestamp)
                ret_message.append(_('{0}\t{1}\t"{2}" set by "{3}"').format(count, target_time.strftime("%a, %d %b %Y %H:%M:%S"), message, user))
                # print target_time.strftime("%s")
            if count == 0:
                ret_message = [_('There are no counts saved.')]
        elif args[0].lower() == "del":
            ret_message = [_("Unknown index. Please specify a valid index: ({0} count list).").format(self.nickname)]
            try:
                delIndex = int(args[1]) - 1
                if delIndex >= 0:
                    (timestamp, longterm, user, message) = self.cowntdownList[delIndex]
                    target_time = datetime.datetime.fromtimestamp(timestamp)
                    ret_message = [_('{0}\t"{1}" set by "{2}" has been removed.').format(target_time.strftime("%a, %d %b %Y %H:%M:%S"), message, user)]
                    self.cowntdownList.pop(delIndex)
            except (IndexError, ValueError):
                pass
        else:
            #do the counting and add to ret_message
            now = int(time.time())
            for (timestamp, longterm, user, message) in self.cowntdownList:
                ret_message.append(self.createTimeReturn(now, timestamp, longterm, user, message))

        self.send_simple_reply(mess, ret_message, True)

    @botcmd
    def urls (self, mess, args):
        """Whispers you the last 20 URLs that where posted if no search term is supplied."""
        retUrls = []
        retMsg = []

        count = 0
        for (username, timestamp, url, title) in reversed(self.urlList):
            if args in url or args in title:
                retUrls.append((username, timestamp, url, title))
                count += 1
                if count >= 20:
                    break

        for (username, timestamp, url, title) in reversed(retUrls):
            if not title:
                title = cgi.escape(self.encode_message(url)).encode("ascii", "xmlcharrefreplace")
            else:
                title = self.encode_message(title).encode("ascii", "xmlcharrefreplace")
            
            username = self.encode_message(username).encode("ascii", "xmlcharrefreplace")
            url = cgi.escape(self.encode_message(url)).encode("ascii", "xmlcharrefreplace")

            try:
                retMsg.append(_("{0} {1}: <a href='{2}'>{3}</a>").format(username, timestamp, url, title))
            except Exception, e:
                self.log.warning('Error while building URLS message with %s: %s' % (title, e))

        self.send_simple_reply(mess, retMsg, True)

    @botcmd
    def mute(self, mess, args):
        """Mute or unmute me"""
        if self.muted:
            self.muted = False
            self.log.warning("WARNING now unmuted")
            self.send_simple_reply(mess, _("I am now unmuted."))
        else:
            self.log.warning("WARNING now muted")
            self.send_simple_reply(mess, _("I am now muted."))
            self.muted = True

    @botcmd
    def about(self, mess, args):
        """I tell you who I am"""
        retMsg = _("I am {0}, a chatbot. If you like to know more, visit: <a href='https://github.com/IMBApplications/rmk.gabi' target='_blank'> https://github.com/IMBApplications/rmk.gabi</a>. My creator is oxi if you like to talk to him about me. I delivered {1} messages since i last restarted {2}.").format(self.nickname, self.stats['messageCount'], str(time.ctime(int(self.readyTs))))
        self.send_simple_reply(mess, retMsg, True)

    """ Support Methods """
    def periodicCheckCount(self, mess):
        showMe = True
        dayInSecs = 86400
        now = int(time.time())
        #newPeriodicCountLastCheck = []
        if (now - self.periodicCountLastCheck) < self.periodicCountWaitTime:
            showMe = False
        self.periodicCountLastCheck = now

        now_time = datetime.datetime.fromtimestamp(now)
        ret_message = []
        self.countTopic = []
        for (timestamp, longterm, user, message) in self.cowntdownList:
            removeMe = False
            target_time = datetime.datetime.fromtimestamp(timestamp)
            if timestamp == now:
                #NOW!
                if showMe:
                    ret_message.append(_("Now: {0}").format(message))
                    if not longterm:
                        removeMe = True
            elif timestamp < now:
                #the event happend
                if not longterm:
                    if target_time.day < now_time.day:
                        removeMe = True
                    else:
                        if showMe:
                            ret_message.append(_("{0} ago: {1}").format(self.getAge(timestamp), message))
                            removeMe = True
                else:
                    if now_time.day == target_time.day and now_time.month == target_time.month:
                        yearsPast = now_time.year - target_time.year
                        if yearsPast == 0:
                            countMessage = _("Today: {0} from {1}").format(message, user)
                            self.countTopic.append((timestamp, countMessage))
                            if showMe:
                                ret_message.append(countMessage)
                        else:
                            countMessage = _("{0} years ago: {1}").format(yearsPast, message)
                            self.countTopic.append((timestamp, countMessage))
                            if showMe:
                                ret_message.append(countMessage)
                    # check for same date to check yearly stuff
            else:
                # it is in the future
                if now_time.day == target_time.day and now_time.month == target_time.month:
                    yearsFuture = target_time.year - now_time.year
                    if longterm:
                        tmpMessage = _("In {0} years: {1}").format(yearsFuture, message)
                        self.countTopic.append((timestamp, tmpMessage))
                        if showMe:
                            ret_message.append(tmpMessage)
                    else:
                        try:
                            self.periodicCountCheckTs[timestamp]
                        except KeyError:
                            self.periodicCountCheckTs[timestamp] = 0

                        if (timestamp - now) < 3600 and (now - self.periodicCountCheckTs[timestamp]) > 600:
                            showMe = True
                        elif (timestamp - now) < 1800 and (now - self.periodicCountCheckTs[timestamp]) > 300:
                            showMe = True
                        elif (timestamp - now) < 900 and (now - self.periodicCountCheckTs[timestamp]) > 180:
                            showMe = True
                        elif (timestamp - now) < 60 and (now - self.periodicCountCheckTs[timestamp]) > 10:
                            showMe = True

                        if showMe:
                            ret_message.append(self.createTimeReturn(now, timestamp, longterm, user, message))
                            self.periodicCountCheckTs[timestamp] = now
                else:
                    targetDate = target_time.replace(hour = 0, minute = 0, second = 0)
                    nowDate = now_time.replace(hour = 0, minute = 0, second = 0)
                    futureTimeDiff = int(targetDate.strftime("%s")) - int(nowDate.strftime("%s"))

                    if futureTimeDiff < (dayInSecs * 2):
                        self.countTopic.append((timestamp, _("Tomorrow: {0}").format(message)))
                    elif futureTimeDiff < (dayInSecs * 7):
                        self.countTopic.append((timestamp, _("In {0} days: {1}").format(int(futureTimeDiff / dayInSecs) + 1, message)))
                    elif futureTimeDiff < (dayInSecs * 8):
                        self.countTopic.append((timestamp, _("In 1 week: {0}").format(message)))
                    elif (futureTimeDiff % (dayInSecs * 7)) == 0 and (futureTimeDiff % (dayInSecs * 7)) < 9:
                        self.countTopic.append((timestamp, _("In {0} weeks: {1}").format(int(futureTimeDiff / (dayInSecs * 7)), message)))
                    elif futureTimeDiff < (dayInSecs * 50):
                        self.countTopic.append((timestamp, _("In {0} days: {1}").format(int(futureTimeDiff / dayInSecs) + 1, message)))


            if removeMe:
                myIndex = [y[0] for y in self.cowntdownList].index(timestamp)
                # print myIndex
                # print self.cowntdownList.pop(myIndex)
                #newPeriodicCountLastCheck.append((timestamp, longterm, user, message))

        #self.cowntdownList = newPeriodicCountLastCheck
        self.periodicCountLastCheck = time.time()

        self.do_topic(mess.getFrom().getStripped())

        return ret_message

    def createTimeReturn(self, now, timestamp, longterm, user, message):
        age = now - timestamp
        if age < 0:
            age = age * -1

        ret_line = [_("{0} seconds").format(age)]

        mins = formatTimeText(int(age / 60), _("minute"), _("minutes"))
        if mins:
            ret_line.append(mins)

        hours = formatTimeText(int(age / 3600), _("hour"), _("hours"))
        if hours:
            ret_line.append(hours)

        days = formatTimeText(int(age / 86400), _("day"), _("days"))
        if days:
            ret_line.append(days)

        weeks = formatTimeText(int(age / 604800), _("week"), _("weeks"))
        if weeks:
            ret_line.append(weeks)

        months = formatTimeText(int(age / 2419200), _("month"), _("months"))
        if months:
            ret_line.append(months)

        years = formatTimeText(int(age / 31449600), _("year"), _("years"))
        if years:
            ret_line.append(years)

        if timestamp == now:
            return _('Now! {0}').format(message)
        elif timestamp > now:
            return _('In {0}: {1}').format(_(' or ').join(ret_line), message)
        else:
            return _('{0} ago: {1}').format(_(' or ').join(ret_line), message)
