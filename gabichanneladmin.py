#!/usr/bin/env python

from botbase import BotBase, botcmd

import csv
import atexit

class GabiChannelAdmin(BotBase):
    def __init__(self, username, password, timezone='UTC', candy_colors=False, res=None, debug=False, privatedomain=False, acceptownmsgs=False, handlers=None):
        super(GabiChannelAdmin, self).__init__(username, password, timezone, candy_colors, res, debug, privatedomain, acceptownmsgs, handlers)

    @botcmd
    def kick (self, mess, args):
        """Kicks a user from the channel"""
        room = mess.getFrom().getStripped()
        self.do_kick(room, args)

    @botcmd
    def invite (self, mess, args):
        """Invites a user to the current channel (JID)"""
        room = mess.getFrom().getStripped()
        self.do_invite(room, args)
