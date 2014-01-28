#!/usr/bin/env python
# -*- coding: utf-8 -*-

from botbase import BotBase, botcmd

import atexit

class GabiChannelAdmin(BotBase):
    def __init__(self, username, password, timezone='UTC', candy_colors=False, res=None, debug=False, privatedomain=False, acceptownmsgs=False, handlers=None):
        super(GabiChannelAdmin, self).__init__(username, password, timezone, candy_colors, res, debug, privatedomain, acceptownmsgs, handlers)

    @botcmd
    def kick (self, mess, args):
        """Kick a user from the channel"""
        room = mess.getFrom().getStripped()
        self.do_kick(room, args)

    @botcmd
    def invite (self, mess, args):
        """Invite a user to the current channel (JID)"""
        room = mess.getFrom().getStripped()
        self.do_invite(room, args)

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
