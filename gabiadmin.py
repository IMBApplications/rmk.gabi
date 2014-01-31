#!/usr/bin/env python
# -*- coding: utf-8 -*-

from botbase import BotBase, botcmd

import atexit
import time
import datetime
import smtplib
from email.mime.text import MIMEText

class GabiAdmin(BotBase):
    def __init__(self, username, password, timezone='UTC', candy_colors=False, res=None, debug=False, privatedomain=False, acceptownmsgs=False, handlers=None):
        super(GabiAdmin, self).__init__(username, password, timezone, candy_colors, res, debug, privatedomain, acceptownmsgs, handlers)

        self.adminList = self.loadJSON('save_admins.dat', [])
        atexit.register(self.saveJSON, 'save_admins.dat', self.adminList)

        self.adminSettings = self.loadJSON('save_admin_settings.dat', {'bugEmail': "", 'notifyEmail': "", 'emailFrom': "", 'smtpServer': ""})
        atexit.register(self.saveJSON, 'save_admin_settings.dat', self.adminSettings)

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
        self.log.warning("BUGREPORT: %s" % args)
        pass
        
    @botcmd
    def notify (self, mess, args):
        """Notify admins via email about something."""
        channel, srcNick = str(mess.getFrom()).split('/')
        try:
            emailMsg = MIMEText(_("{0} wanted you to know that:\n{1}").format(str(mess.getFrom()), args))
            emailMsg['Subject'] = _('{0} Notification from {1}').format(self.nickname, srcNick)
            emailMsg['From'] = self.adminSettings['emailFrom']
            emailMsg['To'] = self.adminSettings['notifyEmail']
            s = smtplib.SMTP(self.adminSettings['smtpServer'])
            s.sendmail(emailMsg['From'], emailMsg['To'], emailMsg.as_string())
            s.quit()
            self.send_simple_reply(mess, _("Notification email sent."), True)
            self.log.warning("EMAIL sending notify email succeeded.")
        except Exception as e:
            self.send_simple_reply(mess, _("ERROR sending email: %s" % e), True)
            self.log.warning("EMAIL sending notify email failed: %s" % e)

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
                elif arg[0] == "set":
                    if arg[1] in self.adminSettings:
                        if arg[2]:
                            message = _("Setting {0} changed to {1}.").format(arg[1], arg[2:])
                            self.adminSettings[arg[1]] = arg[2:]
                            self.notify(mess, message)
                            self.send_simple_reply(mess, message, True)
                    else:
                        self.send_simple_reply(mess, _("Unknown setting: {0}. View available settings with: !admin showSettings").format(arg[1]), True)
                elif arg[0] == "showSettings":
                    settingsRet = [_("Available admin settings:")]
                    for setting in sorted(self.adminSettings.keys()):
                        settingsRet.append(_("{0}: {1}").format(setting, self.adminSettings[setting]))
                    self.send_simple_reply(mess, settingsRet, True)
            else:
                self.send_simple_reply(mess, _("Please choose from: list, add, remove, set, showSettings"), True)