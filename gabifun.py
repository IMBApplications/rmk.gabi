#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from botbase import BotBase, botcmd

class GabiFun(BotBase):
    @botcmd
    def groovy (self, mess, args):
        """Lets groove"""
        if len(args) > 0:
            return _('Groovy? Did i hear groovy? {0} is groovy!').format(args)
        else:
            return _('Groovy? Did i hear groovy? I am groovy!')

    @botcmd
    def imba (self, mess, args):
        """Something is IMBA"""
        if len(args) > 0:
            return _('{0} is IMBA!').format(args)
        else:
            return _('I am IMBA!')
            
    @botcmd
    def haha (self, mess, args):
        """Laughs"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            return _("{0} is so funny I'm gonna die!").format(args)
        else:
            return _("*ROFL* {0}, you are so funny I'm gonna die!").format(username)

    @botcmd
    def slap (self, mess, args):
        """Slaps someone"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            return _('/me slaps {0}').format(args)
        else:
            return _('Who should i slap, {0}?').format(username)

    @botcmd
    def baby (self, mess, args):
        """Is nice to you"""
        self.send_simple_reply(mess, _('Yes honey, what can i do for you?'))

    @botcmd
    def rage (self, mess, args):
        """Rages for you"""
        if len(args) > 0:
            return _('Fuck {0}! Shit fuck crap!').format(args)
        else:
            return _('AARRRGH! DIRTYFECESPENISPOOPBITCHCRAPSHITFUCK!')

    @botcmd
    def how (self, mess, args):
        """How am I?"""
        self.send_simple_reply(mess, _('All systems are in perfect condition, thanks for asking.'))
        
    @botcmd
    def roll (self, mess, args):
        """Rolling dice"""
        if len(args) > 0:
            rmax = random.randint(1, int(args))
        else:
            rmax = random.randint(1, 6)
        return str(rmax);

    @botcmd
    def zoidberg (self, mess, args):
        """Drawing Zoidberg"""
        return '(\/) (^,,,^) (\/)'

    @botcmd
    def boobs (self, mess, args):
        """Flashing her boobies"""
        return '( . )( . )'