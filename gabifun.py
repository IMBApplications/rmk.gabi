#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from botbase import BotBase, botcmd

class GabiFun(BotBase):
    @botcmd
    def groovy (self, mess, args):
        """Lets groove"""
        if len(args) > 0:
            self.send_simple_reply(mess, _('Groovy? Did i hear groovy? {0} is groovy!').format(args))
        else:
            self.send_simple_reply(mess, _('Groovy? Did i hear groovy? I am groovy!'))

    @botcmd
    def imba (self, mess, args):
        """Something is IMBA"""
        if len(args) > 0:
            self.send_simple_reply(mess, _('{0} is IMBA!').format(args))
        else:
            self.send_simple_reply(mess, _('I am IMBA!'))
            
    @botcmd
    def haha (self, mess, args):
        """Laughs"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            self.send_simple_reply(mess, _("{0} is so funny I'm gonna die!").format(args))
        else:
            self.send_simple_reply(mess, _("*ROFL* {0}, you are so funny I'm gonna die!").format(username))

    @botcmd
    def slap (self, mess, args):
        """Slaps someone"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            self.send_simple_reply(mess, _('/me slaps {0}').format(args))
        else:
            self.send_simple_reply(mess, _('Who should i slap, {0}?').format(username))

    @botcmd
    def baby (self, mess, args):
        """Is nice to you"""
        self.send_simple_reply(mess, _('Yes honey, what can i do for you?'))

    @botcmd
    def rage (self, mess, args):
        """Rages for you"""
        if len(args) > 0:
            self.send_simple_reply(mess, _('Fuck {0}! Shit fuck crap!').format(args))
        else:
            self.send_simple_reply(mess, _('AARRRGH! DIRTYFECESPENISPOOPBITCHCRAPSHITFUCK!'))

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
        self.send_simple_reply(mess, str(rmax))

    @botcmd
    def zoidberg (self, mess, args):
        """ASCII Zoidberg"""
        self.send_simple_reply(mess, '(\/) (^,,,^) (\/)')

    @botcmd
    def boobs (self, mess, args):
        """ASCII Flash boobies"""
        self.send_simple_reply(mess, '( . )( . )')

    @botcmd
    def emma (self, mess, args):
        """ASCII Flash emmas boobies"""
        self.send_simple_reply(mess, '( . )||( . )')

    @botcmd
    def flip (self, mess, args):
        """ASCII Flip table"""
        self.send_simple_reply(mess, '(╯°□°）╯︵ ┻━┻')

    @botcmd
    def gimme (self, mess, args):
        """ASCII Give me!"""
        self.send_simple_reply(mess, '༼ つ ◕_◕ ༽つ')

    @botcmd
    def gun (self, mess, args):
        """ASCII Gun"""
        self.send_simple_reply(mess, '︻デ┳═ー')

    @botcmd
    def yay (self, mess, args):
        """ASCII YAY"""
        self.send_simple_reply(mess, '\(._. )/')
