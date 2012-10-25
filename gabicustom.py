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
        if username == 'gabi':
            return

        #fangen wir mal an mit gucken ob der bb oder was sagen will
        reg_ex_bb = (r".*?bb$", r".*?bin mal weg.*?", r".*?baba")
        for reg in reg_ex_bb:
                c = re.compile(reg)
                if c.match(text) != None:
                        self.send_simple_reply(mess, "Bis dann mal {0}".format(username))
                        return

        #fangen wir mal an mit gucken ob wer penis sagt
        reg_ex_pn = (r".*?penis", r".*?Penis")
        for reg in reg_ex_pn:
                c = re.compile(reg)
                if c.match(text) != None:
                        self.send_simple_reply(mess, "Gnihihi, {0} hat Penis gesagt!".format(username))
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
   	
