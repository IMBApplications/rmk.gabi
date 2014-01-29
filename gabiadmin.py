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
        username = mess.getFrom()
        if self.isAdmin(self.get_sender_username(mess)):
            self.send_simple_reply(mess, _('Shutting down.'), False)
            self.log.warning("ACCESS '%s' issued shutdown command." % username)
            self.quitBot()
        else:
            self.send_simple_reply(mess, _("Sorry, you have no administrative rights."), True)
            self.log.warning("ACCESS '%s' tried admin command without permission." % username)

    @botcmd
    def admin (self, mess, args):
        """Administrative commands"""
        # admin add, list, remove, show
        print "mess.getFrom(): %s" % mess.getFrom()
        realjid = None
        if mess.__getitem__('type') == 'groupchat':
            try:
                # print "test: %s" % self.muc_users[message.getFrom()].split('/')[0]
                realjid = self.muc_users[mess.getFrom()].split('/')[0]
                self.logger.debug("Recieved MUC message from user: %s" % str(mess.getFrom()))
            except Exception:
                self.logger.info("Recieved MUC message from non online user: %s" % str(mess.getFrom()))
        elif message.__getitem__('type') == 'chat':
            realjid = str(mess.getFrom()).split('/')[0]
            self.logger.debug("Recieved chat message from user: %s" % str(mess.getFrom()))
#self.muc_channels

        # check if it is a message from myself
        # print "\n%s != %s" % (str(message.getFrom()), "%s/%s" % (self.muc_room, self.muc_nick))
        # if realjid:
        #     if str(mess.getFrom()) != "%s/%s" % (self.muc_room, self.muc_nick):
        #         admin = False
        #         # check if the user is a admin
        #         for (userJid, username) in self.users:
        #             # print "(userJid, username): %s %s" % (userJid, username)
        #             # userJid = self.plugin.utils.convert_from_unicode(jid)
        #             # print "userJid: %s" % userJid
        #             if userJid == realjid.split('/')[0]:
        #                 admin = True
        #                 # print "admin found on %s" % userJid

        #         if admin:





        username = mess.getFrom()
        if len(self.createAdminList()) == 0:
            if args == 'add':
                self.adminList.append((username, time.time(), "Initial administrator"))
                self.log.warning("ACCESS '%s' was registred as initial administrator." % username)
            else:
                self.send_simple_reply(mess, _("No administrators registred. Please register the first with '!admin add'"), True)
                return

        if not self.isAdmin(username):
            self.send_simple_reply(mess, self.createAdminList(), True)
            return
