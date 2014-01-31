#!/usr/bin/env python
# -*- coding: utf-8 -*-

from botbase import BotBase, botcmd

import atexit
import time
import datetime

class GabiAdmin(BotBase):
    def __init__(self, username, password, timezone='UTC', candy_colors=False, res=None, debug=False, privatedomain=False, acceptownmsgs=False, handlers=None):
        super(GabiAdmin, self).__init__(username, password, timezone, candy_colors, res, debug, privatedomain, acceptownmsgs, handlers)

        self.adminList = self.loadJSON('save_admins.dat', [])
        atexit.register(self.saveJSON, 'save_admins.dat', self.adminList)

    def isAdmin(self, srcChannel, srcUsername):
        adminRights = False
        for (username, channel, since, comment) in self.adminList:
            if srcUsername.lower() == username.lower() and channel.lower() == srcChannel.lower():
                adminRights = True
        return adminRights

    def createAdminList(self, srcChannel):
        msg = []
        initAdminExists = False
        for (username, channel, since, comment) in self.adminList:
            if channel == srcChannel:
                initAdminExists = True
        if initAdminExists:
            msg.append(_("The following administrators are registred for this channel:"))
            for (username, channel, since, comment) in self.adminList:
                if channel == srcChannel:
                    msg.append(_("{0} since {1} ({2})").format(username, datetime.datetime.fromtimestamp(since).strftime('%Y-%m-%d %H:%M:%S'), comment))
        return msg

    @botcmd
    def quit (self, mess, args):
        """Shut me down (admin)."""
        channel, srcNick = str(mess.getFrom()).split('/')
        if self.isAdmin(channel, srcNick):
            self.send_simple_reply(mess, _('Shutting down.'), False)
            self.log.warning("ACCESS '%s' issued shutdown command." % srcNick)
            self.quitBot()
        else:
            self.send_simple_reply(mess, _("Sorry, you have no administrative rights."), True)
            self.log.warning("ACCESS '%s' tried admin command without permission." % srcNick)

    @botcmd
    def bug (self, mess, args):
        """Report a bug to the developer."""
        pass
        
    @botcmd
    def notify (self, mess, args):
        """Notify admins via email about something."""
        pass

    @botcmd
    def admin (self, mess, args):
        """Administrative commands"""
        # admin add, list, remove, show, status (away, dnd, online, invis), bug, notify
        #self.muc_channels all connected rooms
        channel, srcNick = str(mess.getFrom()).split('/')
        if len(self.createAdminList(channel)) == 0:
            if args == 'initial':
                self.adminList.append((srcNick, channel, time.time(), "Initial administrator"))
                self.log.warning("ACCESS '%s' was registred as initial administrator for channel %s." % (srcNick, channel))
            else:
                self.send_simple_reply(mess, _("No administrators registred. Please register the first with '!admin initial'"), True)
                return

        if not self.isAdmin(channel, srcNick):
            self.send_simple_reply(mess, self.createAdminList(channel), True)
            return
        else:
            arg = args.split()
            if len(arg) != 0:
                if arg[0] == "list":
                    self.send_simple_reply(mess, self.createAdminList(channel), True)
                elif arg[0] == "add":
                    pass
                elif arg[0] == "remove":
                    pass
            else:
                self.send_simple_reply(mess, _("Please choose from: list, add, remove"), True)