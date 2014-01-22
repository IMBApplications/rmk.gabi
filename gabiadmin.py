#!/usr/bin/env python

from botbase import BotBase, botcmd

import csv
import atexit

class GabiAdmin(BotBase):
    def __init__(self, username, password, timezone='UTC', candy_colors=False, res=None, debug=False, privatedomain=False, acceptownmsgs=False, handlers=None):
        super(GabiAdmin, self).__init__(username, password, timezone, candy_colors, res, debug, privatedomain, acceptownmsgs, handlers)

        self.userTopic = self.loadJSON('topic.dat', [])
        self.AdminAvail = True

    @botcmd
    def topic (self, mess, args):
        """Sets the current topic"""
        room = mess.getFrom().getStripped()
        self.userTopic = args
        self.saveJSON('topic.dat', self.userTopic)
        self.do_topic(room)

    @botcmd
    def admins (self, mess, args):
        """Shows administrators"""
        msg = 'Admins:\n'
        handler = self.get_csv_admin_users_handler()
        for row in  csv.reader(handler, delimiter=';', quotechar='#'):
            msg += '->\t' + str(row[1]) + " (" + str(row[0]) + ")" + '\n'

        handler.close()
        return msg

    @botcmd
    def quit (self, mess, args):
        """Shut me down."""
        exit()
        return 'Shutting down'  
