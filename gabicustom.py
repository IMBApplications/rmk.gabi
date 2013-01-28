#!/usr/bin/python

from botbase import BotBase, botcmd
import re
import csv
import datetime

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
                        self.send_simple_reply(mess, "wb {0}! Wie wars beim {1}?".format(username, self.afkList[username])
                        del self.afkList[username];
                    else:
                        self.send_simple_reply(mess, "wb {0}!".format(username))
                    return

        #tippfehlerkontrolle
        reg_ex_ac = (r".*?amche", r".*?shcon", r".*?acuh", r".*?dsa", r".*?cih", r".*?ihc")
        autoCorr = { '.*?amche' : 'mache', '.*?shcon': 'schon', '.*?acuh': 'auch', '.*?dsa': 'das', '.*?cih': 'ich', '.*?ihc': 'ich'  }
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
        reg_ex_pn = (r".*?Guten Morgen", r".*?guten morgen")
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
            hallo = 'Hi {0}'.format(user)
            #self.send(room, hallo, None, 'groupchat')

    def on_gone_offline(self, jid):
            jidSplit = '{0}'.format(jid).partition('/')
            room = jidSplit[0]
            user = jidSplit[2]
            hallo = 'Und da ist {0} weg'.format(user)
            #self.send(room, hallo, None, 'groupchat')
   	
