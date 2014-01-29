#!/usr/bin/env python
# -*- coding: utf-8 -*-

from botbase import BotBase, botcmd

import atexit
import time

class GabiAdmin(BotBase):
    def __init__(self, username, password, timezone='UTC', candy_colors=False, res=None, debug=False, privatedomain=False, acceptownmsgs=False, handlers=None):
        super(GabiAdmin, self).__init__(username, password, timezone, candy_colors, res, debug, privatedomain, acceptownmsgs, handlers)

        self.userTopic = self.loadJSON('topic.dat', "")

        self.adminList = self.loadJSON('save_admins.dat', [])
        atexit.register(self.saveJSON, 'save_admins.dat', self.adminList)

        self.messageCount = self.loadJSON('save_stats.dat', 0)
        atexit.register(self.saveJSON, 'save_stats.dat', self.messageCount)

    def isAdmin(self, user):
        adminRights = False
        for (username, since, comment) in self.adminList:
            if user.lower() == username.lower():
                adminRights = True
        return adminRights

    def createAdminList(self):
        msg = []
        if len(self.adminList):
            msg.append(_("The following administrators are registred:"))
            for admin in adminList:
                msg.append(_("{0} since {1}"))
        return msg

    @botcmd
    def quit (self, mess, args):
        """Shut me down."""
        if self.isAdmin(self.get_sender_username(mess)):
            self.send_simple_reply(mess, _('Shutting down.'), False)
            self.quitBot()
        else:
            self.send_simple_reply(mess, _("Sorry, you have no administrative rights."), True)

    @botcmd
    def admin (self, mess, args):
        """Administrative commands"""
        # admin add, list, remove, show
        username = self.get_sender_username(mess)
        if len(self.createAdminList()) == 0:
            if len(args):
                if args[0] == 'add':
                    self.adminList.append((username, time.time(), "Initial Administrator"))
            else:
                self.send_simple_reply(mess, _("No administrators registred. Please register the first with '!admin add'"), True)
                return

        if not self.isAdmin(username):
            self.send_simple_reply(mess, self.createAdminList(), True)
            return
