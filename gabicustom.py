#!/usr/bin/env python

import re
import csv
import datetime
import time
import atexit
import json
import collections

from botbase import BotBase, botcmd

class GabiCustom(BotBase):

    def __init__(self, username, password, candy_colors=False, res=None, debug=False, privatedomain=False, acceptownmsgs=False, handlers=None):
        super(GabiCustom, self).__init__(username, password, candy_colors, res, debug, privatedomain, acceptownmsgs, handlers)

        self.lastSeen = self.loadJSON('db/save_lastSeen.dat', {})
        atexit.register(self.saveJSON, 'db/save_lastSeen.dat', self.lastSeen)
        self.usersNowOffline = {}

        self.memList = self.loadJSON('db/save_memo.dat', {})
        atexit.register(self.saveJSON, 'db/save_memo.dat', self.memList)

        self.afkList = self.loadJSON('db/save_afk.dat', {})
        atexit.register(self.saveJSON, 'db/save_afk.dat', self.afkList)

        self.reminderDict = self.loadJSON('db/save_reminder.dat', {})
        atexit.register(self.saveJSON, 'db/save_reminder.dat', self.reminderDict)

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
                if username in self.afkList:
                    self.send_simple_reply(mess, "wb " + username + "! Wie wars beim " + self.afkList[username] + "?")
                    del self.afkList[username];
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
                now = datetime.datetime.now()
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
                writer.writerow([username, str(datetime.datetime.now()) , url])

        if writer != None:
            handler.close()

    def on_came_online(self, jid):
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
                if self.lastSeen[user] > 0:
                    age = self.lastSeen[user]
            except Exception:
                pass
            self.lastSeen[user] = int(time.time())

            if userWasOffline:
                hallo = None
                if age > 0:
                    if (int(time.time()) - age) > 300:
                        hallo = 'Welcome back {0}, dich habe ich schon seit {1} nicht mehr gesehen.'.format(user, self.getAge(age))
                else:
                    hallo = 'Hallo {0}, dich sehe ich zum ersten mal hier. Ich bin Gabi der Roboter-Mensch-Kontakter. Gib "gabi help" ein fuer hilfe.'.format(user)

                if hallo:
                    self.send(room, hallo, None, 'groupchat')

            # Reminder
            if self.reminderDict.has_key(user.lower()):
                if len(self.reminderDict[user.lower()]) > 0:
                    reminderMessage = '%s, ich soll dir folgendes ausrichten:\n' % user
                    for (sender, message, timestamp) in self.reminderDict[user.lower()]:
                        reminderMessage += 'Von %s: %s\n' % (sender, message)

                    self.reminderDict[user.lower()] = []
                    self.send(room, reminderMessage, None, 'groupchat')
                    

    def on_gone_offline(self, jid):
        strJID = '%s' % jid
        # room = self.list_unicode_cleanup(strJID.split('/'))[0]
        user = self.list_unicode_cleanup(strJID.split('/'))[1]

        if user != self.get_my_username():
            self.lastSeen[user] = int(time.time())
            self.usersNowOffline[user] = True

            # hallo = 'Und da ist {0} weg'.format(user)
            #self.send(room, hallo, None, 'groupchat')

    # LastSeen Methods
    @botcmd
    def zuletzt (self, mess, args):
        """Gibt dir an, wann ein Benutzer zuletzt gesehen wurde"""
        if not args:
            ret = ''
            for name in self.lastSeen.keys():
                ret = ret + name + ' vor ' + self.getAge(self.lastSeen[name]) + '\n'
            return ret
        else:
            lastSeen = 0
            for name in self.lastSeen.keys():
                if name.lower() == args.lower():
                    lastSeen = self.lastSeen[name]
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
            self.memList[username] = args;
            return 'Merke mir: "' + args + '".'
        elif username in self.memList:
            return 'Habe mir: "' + self.memList[username] + '" gemerkt.'
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
        self.afkList[username] = message
        return 'Bis spaeter, ' + username  + '. Viel Spass beim ' + message + '.'

    @botcmd
    def werafk (self, mess, args):
        """sagt, was sie sich gemerkt hat"""
        if len(self.afkList) > 0:
            ret = ''
            for username in self.afkList.keys():
                ret = ret + "\n%-10s: %s" % (username, self.afkList[username])
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
            ret_message = "Du musst einen namen gefolgt von der nachricht angeben."
        return ret_message
