#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from botbase import BotBase, botcmd

class GabiHate(BotBase):

    @botcmd
    def sih (self, mess, args):
        """Shoot someone trough the throat"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            return _('{0}, shoot trough your throat!').format(args)
        else:
            return _('{0}, who should i shoot trough the throat?').format(username)

    @botcmd
    def aids (self, mess, args):
        """Get AIDS"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            return _('{0}, get AIDS!').format(args)
        else:
            return _('{0}, who should get AIDS?').format(username)
