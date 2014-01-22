#!/usr/bin/env python

import random
from botbase import BotBase, botcmd

class GabiHate(BotBase):

    @botcmd
    def sih (self, mess, args):
        """gabi schiesst wem in den hals"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            return args + ', schiess dir in den Hals!'
        else:
            return username  + ', wem soll ich in den Hals schiessen?'

    @botcmd
    def aids (self, mess, args):
        """gabi wuenscht wem aids"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            return args + ', get AIDS!'
        else:
            return username  + ', wem soll ich AIDS wuenschen?'
