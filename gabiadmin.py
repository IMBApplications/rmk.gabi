#!/usr/bin/env python
# -*- coding: utf-8 -*-

from botbase import BotBase, botcmd

import atexit
import time
import datetime
import smtplib
import traceback
from email.mime.text import MIMEText

class GabiAdmin(BotBase):
    def __init__(self, username, password, timezone='UTC', candy_colors=False, res=None, debug=False, privatedomain=False, acceptownmsgs=False, handlers=None):
        super(GabiAdmin, self).__init__(username, password, timezone, candy_colors, res, debug, privatedomain, acceptownmsgs, handlers)

        self.adminList = self.loadJSON('save_admins.dat', [])
        atexit.register(self.saveJSON, 'save_admins.dat', self.adminList)

        self.adminSettings = self.loadJSON('save_admin_settings.dat', {'suggestionEmail': "", 'notifyEmail': "", 'emailFrom': "", 'smtpServer': ""})
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
                    msg.append(_("{0} since {1} ({2})").format(username, datetime.datetime.fromtimestamp(since).strftime('%Y-%m-%d %H:%M:%S'), ' '.join(comment)))
        return msg

    @botcmd
    def suggestion (self, mess, args):
        """Report a suggestion or bug to the developer"""
        if not mess:
            mess = xmpp.Message()

        try:
            channel, srcNick = str(mess.getFrom()).split('/')
        except:
            pass

        if not srcNick:
            srcNick = "Anonymous"
            channel = "Unknown channel"

        if args:
            if isinstance(args, list):
                args = ' '.join(args)
            try:
                emailMsg = MIMEText(_("{0} wanted you to know that:\n{1}").format(str(mess.getFrom()), args))
                emailMsg['Subject'] = _('{0} Suggestion from {1}').format(self.nickname, srcNick)
                emailMsg['From'] = ''.join(self.adminSettings['emailFrom'])
                if isinstance(self.adminSettings['suggestionEmail'], list):
                    emailTo = ', '.join(self.adminSettings['suggestionEmail'])
                else:
                    emailTo = self.adminSettings['suggestionEmail']
                emailMsg['To'] = emailTo
                s = smtplib.SMTP(self.adminSettings['smtpServer'])
                s.sendmail(emailMsg['From'], emailMsg['To'], emailMsg.as_string())
                s.quit()
                self.send_simple_reply(mess, _("Suggestion email sent."), True)
                self.log.info("Sending suggestion email succeeded.")
            except Exception as e:
                self.send_simple_reply(mess, _("Error sending suggestion email: {0}").format(e), True)
                self.log.warning("Sending suggestion email failed: %s\n%s" % (e, traceback.format_exc(type_, value_, traceback_)))
        elif srcNick != "Anonymous":
            self.send_simple_reply(mess, _("You have to supply a message"), True)
        
    @botcmd
    def notify (self, mess, args):
        """Notify admins via email about something."""
        channel, srcNick = str(mess.getFrom()).split('/')
        if args:
            if isinstance(args, list):
                args = ' '.join(args)
            try:
                emailMsg = MIMEText(_("{0} wanted you to know that:\n{1}").format(str(mess.getFrom()), args))
                emailMsg['Subject'] = _('{0} Notification from {1}').format(self.nickname, srcNick)
                emailMsg['From'] = ''.join(self.adminSettings['emailFrom'])
                if isinstance(self.adminSettings['suggestionEmail'], list):
                    emailTo = ', '.join(self.adminSettings['suggestionEmail'])
                else:
                    emailTo = self.adminSettings['suggestionEmail']
                emailMsg['To'] = emailTo
                s = smtplib.SMTP(self.adminSettings['smtpServer'])
                s.sendmail(emailMsg['From'], emailMsg['To'], emailMsg.as_string())
                s.quit()
                self.send_simple_reply(mess, _("Notification email sent."), True)
                self.log.info("Sending notify email succeeded.")
            except Exception as e:
                self.send_simple_reply(mess, _("Error sending notification email: {0}").format(e), True)
                self.log.warning("Sending notify email failed: %s\n%s" % (e, traceback.format_exc(type_, value_, traceback_)))
        else:
            self.send_simple_reply(mess, _("You have to supply a message"), True)

    @botcmd
    def admin (self, mess, args):
        """Administrative commands"""
        # admin add, list, remove, show, status (away, dnd, online, invis), bug, notify, quit
        #self.muc_channels all connected rooms
        channel, srcNick = str(mess.getFrom()).split('/')
        if len(self.createAdminList(channel)) == 0:
            if args == 'initial':
                self.adminList.append((srcNick, channel, time.time(), ["Initial", "administrator"]))
                self.log.warning("%s was registred as initial administrator for channel %s." % (srcNick, channel))
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
                    if self.isAdmin(channel, arg[1]):
                        message = _("{0} is already admin.").format(arg[1])
                        self.log.info(message)
                        self.send_simple_reply(mess, message, True)
                    else:
                        #i will NOT work with spaces in names...
                        message = _("{0} is now admin.").format(arg[1])
                        self.log.info(message)
                        self.adminList.append((arg[1], channel, time.time(), arg[2:]))
                        self.send_simple_reply(mess, message, True)
                elif arg[0] == "remove":
                    for (admin, channel, since, comment) in self.adminList:
                        if arg[1].lower() == admin.lower():
                            message = _("{0} is no longer admin.").format(arg[1])
                            self.log.info(message)
                            self.adminList.pop(self.adminList.index((admin, channel, since, comment)))
                            self.send_simple_reply(mess, message, True)
                        else:
                            message = _("{0} not found in admin list.").format(arg[1])
                            self.log.info(message)
                            self.send_simple_reply(mess, message, True)
                elif arg[0] == "set":
                    if arg[1] in self.adminSettings:
                        if arg[2]:
                            message = _("Setting {0} changed to {1}.").format(arg[1], arg[2:])
                            self.log.info(message)
                            self.adminSettings[arg[1]] = arg[2:]
                            self.notify(mess, message)
                            self.send_simple_reply(mess, message, True)
                    else:
                        self.send_simple_reply(mess, _("Unknown setting: {0}. View available settings with: !admin showSettings").format(arg[1]), True)
                elif arg[0] == "quit":
                    message = _('{0} issued a shutdown.').format(srcNick)
                    self.send_simple_reply(mess, message, False)
                    self.log.warning(message)
                    self.quitBot()
                elif arg[0] == "showSettings":
                    settingsRet = [_("Available admin settings:")]
                    for setting in sorted(self.adminSettings.keys()):
                        settingsRet.append(_("{0}: {1}").format(setting, self.adminSettings[setting]))
                    self.send_simple_reply(mess, settingsRet, True)
                elif arg[0] == "lang":
                    message = _("Available languages: {0}").format(', '.join(self.localizations))
                    if len(arg) > 1:
                        if arg[1] in self.localizations:
                            self.loadLocalization(arg[1])
                            message = _("Loaded languages: {0}").format(arg[1])
                    self.send_simple_reply(mess, message, True)

            else:
                self.send_simple_reply(mess, _("Please choose from: list, add, remove, set, lang, showSettings, quit"), True)