#!/usr/bin/env python

import re
import csv
import datetime
import time
import calendar
import atexit
import json
import collections
import pytz

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

        self.lastSeenDict = self.loadJSON('db/save_lastSeen.dat', {})
        atexit.register(self.saveJSON, 'db/save_lastSeen.dat', self.lastSeenDict)
        self.usersNowOffline = {}

        self.memDict = self.loadJSON('db/save_memo.dat', {})
        atexit.register(self.saveJSON, 'db/save_memo.dat', self.memDict)

        self.afkDict = self.loadJSON('db/save_afk.dat', {})
        atexit.register(self.saveJSON, 'db/save_afk.dat', self.afkDict)

        self.reminderDict = self.loadJSON('db/save_reminder.dat', {})
        atexit.register(self.saveJSON, 'db/save_reminder.dat', self.reminderDict)

        self.cowntdownList = self.loadJSON('db/save_count.dat', [])
        atexit.register(self.saveJSON, 'db/save_count.dat', self.cowntdownList)

        self.afkRejoinTime = 900

        self.periodicCountLastCheck = 0
        self.periodicCountWaitTime = 3600
        self.periodicCountCheckTs = {}

        self.countTopic = []

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
                self.send_simple_reply(mess, "Hau raus, {0}!".format(username))
                return

        #fangen wir mal an mit gucken ob wer re sagt        
        reg_ex_re = (r"^\|c\:[0-9]\|re$", r"^rehor$", r"^\|c\:[0-9]\|rehor$", r"^re$")
        for reg in reg_ex_re:
            c = re.compile(reg)
            if c.match(text) != None:
                if username in self.afkDict:
                    self.send_simple_reply(mess, "wb " + username + "! Wie wars beim " + self.afkDict[username] + "?")
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
                self.send_simple_reply(mess, username + ' meinte "' + autoCorr[reg] + '".')                    
                    
                return

        #fangen wir mal an mit gucken ob wer penis sagt
        reg_ex_pn = (r".*?penis", r".*?Penis")
        for reg in reg_ex_pn:
            c = re.compile(reg)
            if c.match(text) != None:
                self.send_simple_reply(mess, "Gnihihi, {0} hat Penis gesagt!".format(username))
                return
                    
        #fangen wir mal an mit gucken ob wer Guten Morgen sagt
        reg_ex_pn = (r".*?Guten Morgen", r".*?guten morgen", r".*?Moinz", r".*?moinz")
        for reg in reg_ex_pn:
            c = re.compile(reg)
            if c.match(text) != None:
                now = datetime.datetime.now(pytz.timezone(self.timezone))
                if now.hour > 10:
                    self.send_simple_reply(mess, "FUCK YOU, {0}! Guck ma auf die Uhr!".format(username))
                else:
                    self.send_simple_reply(mess, "Guten Morgen, {0}. Schoen, dass du da bist.".format(username))
                    return

        #so jetzt alle URLS
        reg_ex_url = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        c = re.compile(reg_ex_url)
        writer = None
        handler = None

        for url in c.findall(text):
            if writer == None:
                handler = self.get_handler_csv_urls_write()
                writer = csv.writer(handler, delimiter=';', quotechar='#')
                writer.writerow([username, str(datetime.datetime.now(pytz.timezone(self.timezone))) , url])

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
                        hallo.append('Welcome back {0}, dich habe ich schon seit {1} nicht mehr gesehen.'.format(user, self.getAge(age)))
                else:
                    hallo.append('Hallo {0}, dich sehe ich zum ersten mal hier. Ich bin Gabi der Roboter-Mensch-Kontakter.')
                    hallo.append('Gib "gabi help" ein fuer hilfe.'.format(user))

                if user in self.afkDict:
                    hallo.append("Wie wars beim " + self.afkDict[user] + "?")
                    del self.afkDict[user];

                if len(hallo) > 0:
                    self.send(room, '\n'.join(hallo), None, 'groupchat')

            # Reminder
            if self.reminderDict.has_key(user.lower()):
                if len(self.reminderDict[user.lower()]) > 0:
                    reminderMessage = '%s, ich soll dir folgendes ausrichten:\n' % user
                    for (sender, message, timestamp) in self.reminderDict[user.lower()]:
                        reminderMessage += 'Von %s vor %s: %s\n' % (sender, self.getAge(timestamp), message)

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
    def zuletzt (self, mess, args):
        """Gibt dir an, wann ein Benutzer zuletzt gesehen wurde"""
        if not args:
            ret = ''
            for name in self.lastSeenDict.keys():
                ret = ret + name + ' vor ' + self.getAge(self.lastSeenDict[name]) + '\n'
            return ret
        else:
            lastSeen = 0
            for name in self.lastSeenDict.keys():
                if name.lower() == args.lower():
                    lastSeen = self.lastSeenDict[name]
                    userName = name

            if lastSeen > 0:
                return userName + ' habe ich zuletzt vor ' + self.getAge(lastSeen) + ' gesehen.'
            else:
                return self.get_sender_username(mess) + ', ' + args + ' habe ich noch nie gesehen.'

    # Memo Methods
    @botcmd
    def memo (self, mess, args):
        """sie merkt sich was"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            self.memDict[username] = args;
            return 'Merke mir: "' + args + '".'
        elif username in self.memDict:
            return 'Habe mir: "' + self.memDict[username] + '" gemerkt.'
        else:
            return 'Ja, was denn?'

    #AFK Methods
    @botcmd
    def afk (self, mess, args):
        """user away"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            message = args
        else:
            message = "AFK"
        self.afkDict[username] = message

        if username != self.get_my_username():
            self.lastSeenDict[username] = int(time.time())
            self.usersNowOffline[username] = True

        return 'Bis spaeter, ' + username  + '. Viel Spass beim ' + message + '.'

    @botcmd
    def werafk (self, mess, args):
        """sagt, was sie sich gemerkt hat"""
        if len(self.afkDict) > 0:
            ret = ''
            for username in self.afkDict.keys():
                ret = ret + "\n%-10s: %s" % (username, self.afkDict[username])
            return ret;
        else:
            return 'Es hat sich niemand abgemeldet.'

    #Reminder Methods
    @botcmd
    def remind (self, mess, args):
        """remind a user with something when he comes back"""
        from_username = self.get_sender_username(mess)
        new_args = args.split(" ")

        if len(args) > 1:
            target_user = new_args[0]
            target_message = ' '.join(new_args[1:])

            ret_message = "Ich werde " + target_user + " ausrichten dass: " + target_message

            if not self.reminderDict.has_key(target_user.lower()):
                self.reminderDict[target_user.lower()] = []
            self.reminderDict[target_user.lower()].append((from_username, target_message, int(time.time())))

        else:
            ret_message = "Du musst einen Namen gefolgt von der Nachricht angeben."
        return ret_message

    #Cowntdown Methods
    @botcmd
    def count (self, mess, args):
        # self.cowntdownList = (targetTime, longterm (y/n), fromuser, what)
        """Saves a cowntdown to a specified date/time"""
        from_username = self.get_sender_username(mess)
        args = args.split(" ")
        ret_message = ["Die Befehle fuer count sind: add, list, del"]

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
                    ret_message.append("Zaehler gespeichert fuer '%s' (%s)" % (' '.join(args), target_time.strftime("%a, %d %b %Y %H:%M:%S")))
                    # print target_time.strftime("%s")
                else:
                    args = []
                    ret_message.append("Du musst einen namen gefolgt von Zeit/Datum und dann das Event angeben. Beispiele:")
                    ret_message.append("gabi count add 18:15 Es ist viertel nach 6")
                    ret_message.append("gabi count add 31.12.2013 23:59 Das alte Jahr ist Geschichte")
        elif args[0].lower() == "list":
            ret_message = ['Folgende Zaehler sind gesetzt:']
            count = 0
            for (timestamp, longterm, user, message) in self.cowntdownList:
                count += 1
                target_time = datetime.datetime.fromtimestamp(timestamp)
                ret_message.append('%s\t%s\t"%s" von "%s"' % (count, target_time.strftime("%a, %d %b %Y %H:%M:%S"), message, user))
                # print target_time.strftime("%s")
            if count == 0:
                ret_message = ['Es sind keine Zaehler gesetzt.']
        elif args[0].lower() == "del":
            ret_message = ["Unbekannter index. Bitte gib einen zulaessigen index an (count list)."]
            try:
                delIndex = int(args[1]) - 1
                if delIndex >= 0:
                    (timestamp, longterm, user, message) = self.cowntdownList[delIndex]
                    target_time = datetime.datetime.fromtimestamp(timestamp)
                    ret_message = ['%s\t"%s" von "%s" wurde entfernt.' % (target_time.strftime("%a, %d %b %Y %H:%M:%S"), message, user)]
                    self.cowntdownList.pop(delIndex)
            except IndexError:
                pass
        elif args[0].lower() == "per":
            self.periodicCountLastCheck = 0
            ret_message = self.periodicCheckCount(mess)
        else:
            #do the counting and add to ret_message
            now = int(time.time())
            for (timestamp, longterm, user, message) in self.cowntdownList:
                ret_message.append(self.createTimeReturn(now, timestamp, longterm, user, message))


        return '\n'.join(ret_message)
        pass

    """ Support Methods """
    def periodicCheckCount(self, mess):
        showMe = True
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
                    ret_message.append("Jetzt: %s" % (message))
                    if not longterm:
                        removeMe = True
            elif timestamp < now:
                #the event happend
                if not longterm:
                    if target_time.day < now_time.day:
                        removeMe = True
                    else:
                        if showMe:
                            ret_message.append("Vor %s: %s" % (self.getAge(timestamp), message))
                            removeMe = True
                else:
                    if now_time.day == target_time.day and now_time.month == target_time.month:
                        yearsPast = now_time.year - target_time.year
                        if yearsPast == 0:
                            countMessage = "Heute: %s von %s" % (message, user)
                            self.countTopic.append(countMessage)
                            if showMe:
                                ret_message.append(countMessage)
                        else:
                            countMessage = "Vor %s Jahren: %s" % (yearsPast, message)
                            self.countTopic.append(countMessage)
                            if showMe:
                                ret_message.append(countMessage)
                    # check for same date to check yearly stuff
            else:
                # it is in the future
                futureTimeDiff = int(target_time.strftime("%s")) - int(now_time.strftime("%s"))
                dayInSecs = 86400
                if now_time.day == target_time.day and now_time.month == target_time.month:
                    yearsFuture = target_time.year - now_time.year
                    if longterm:
                        if showMe:
                            ret_message.append("In %s Jahren: %s" % (yearsFuture, message))
                            self.countTopic.append("In %s Jahren: %s" % (yearsFuture, message))
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
                elif futureTimeDiff < (dayInSecs * 30):
                    self.countTopic.append(self.createTimeReturn(now, timestamp, longterm, user, message))


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

        ret_line = ["%s Sekunden" % age]

        mins = formatTimeText(int(age / 60), "Minute", "Minuten")
        if mins:
            ret_line.append(mins)

        hours = formatTimeText(int(age / 3600), "Stunde", "Stunden")
        if hours:
            ret_line.append(hours)

        days = formatTimeText(int(age / 86400), "Tag", "Tage")
        if days:
            ret_line.append(days)

        weeks = formatTimeText(int(age / 604800), "Woche", "Wochen")
        if weeks:
            ret_line.append(weeks)

        months = formatTimeText(int(age / 2419200), "Monat", "Monate")
        if months:
            ret_line.append(months)

        years = formatTimeText(int(age / 31449600), "Jahr", "Jahre")
        if years:
            ret_line.append(years)

        if timestamp == now:
            return 'Jetzt! %s' % message
        elif timestamp > now:
            return 'In %s: %s' % (' oder '.join(ret_line), message)
        else:
            return 'Vor %s: %s' % (' oder '.join(ret_line), message)
