#!/usr/bin/env python

from botbase import BotBase, botcmd

import csv

class GabiAdmin(BotBase):
    @botcmd
    def kick (self, mess, args):
        """Kickt einen Nutzer aus dem aktuelle Channel"""
        room = mess.getFrom().getStripped()
        self.do_kick(room, args)

    @botcmd
    def topic (self, mess, args):
        """Setzt die Ueberschrift im aktuellen Channel"""
        room = mess.getFrom().getStripped()
        self.do_topic(room, args)

    @botcmd
    def invite (self, mess, args):
        """Laed einen Nutzer in den Channel ein (jabber-id angeben!)"""
        room = mess.getFrom().getStripped()
        self.do_invite(room, args)

    @botcmd
    def admins (self, mess, args):
        """Zeigt alle admins"""
        msg = 'Admins:\n'
        handler = self.get_csv_admin_users_handler()
        for row in  csv.reader(handler, delimiter=';', quotechar='#'):
            msg += '->\t' + str(row[1]) + " (" + str(row[0]) + ")" + '\n'

        handler.close()
        return msg

    @botcmd
    def quit (self, mess, args):
        """Beendet/Restartet Gabi"""
        exit()
        return 'Exiting/Restarting...'  
