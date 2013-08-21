#!/usr/bin/python

from botbase import BotBase, botcmd
import re
import csv
import datetime
import time

class GabiCustom(BotBase):
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
        jidSplit = '{0}'.format(jid).partition('/')
        room = jidSplit[0]
        user = jidSplit[2]

        age = 0
        try:
            if self.lastSeen[user] > 0:
                age = self.lastSeen[user]
        except Exception:
            pass        

        if age > 0:
            hallo = 'Welcome back {0}, dich habe ich schon seit {1} nicht mehr gesehen.'.format(user, self.getAge(age))
        else:
            hallo = 'Hallo {0}, dich sehe ich zum ersten mal hier. Ich bin Gabi der Roboter-Mensch-Kontakter. Gib "gabi help" ein fuer hilfe.'.format(user)

        self.lastSeen[user] = int(time.time())
        self.send(room, hallo, None, 'groupchat')

    def on_gone_offline(self, jid):
        jidSplit = '{0}'.format(jid).partition('/')
        room = jidSplit[0]
        user = jidSplit[2]
        hallo = 'Und da ist {0} weg'.format(user)
        self.lastSeen[user] = int(time.time())

        #self.send(room, hallo, None, 'groupchat')


    @botcmd
    def zuletzt (self, mess, args):
        """Gibt dir an, wann ein Benutzer zuletzt gesehen wurde"""
        if not args:
            return self.get_sender_username(mess) + ', bitte gib einen Benutzer an'
        else:
            lastSeen = 0
            for name in self.lastSeen.keys():
                if name.lower() == args.lower():
                    lastSeen = self.lastSeen[name]
                    userName = name

            if lastSeen > 0:
                return userName + ' habe ich zuletzt vor ' + self.getAge(lastSeen) + ' gesehen.'
            else:
                return args + ' habe ich noch nie gesehen.'