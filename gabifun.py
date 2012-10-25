#!/usr/bin/python

import random
from botbase import BotBase, botcmd

class GabiFun(BotBase):   
    @botcmd
    def fetzig (self, mess, args='Aggravate'):
        """Lets fetz"""
        if len(args) > 0:
            return 'Fetzig? Hab ich fetzig gehoert? ' + args  + ' ist fetzig!';
        else:
            return 'Fetzig? Hab ich fetzig gehoert? ICH bin fetzig!';

    @botcmd
    def imba (self, mess, args):
        """Etwas ist IMBA"""
        if len(args) > 0:
            return args  + ' ist IMBA!';
        else:
            return 'Ich bin IMBA!';

    @botcmd
    def afk (self, mess, args):
        """user away"""
        if len(args) > 0:
            return 'Senior ' + args  + ' no here.';

    @botcmd
    def baby (self, mess, args):
        """she is nice to you"""
        return 'Ja Schatz, was kann ich fuer dich tun?';

    @botcmd
    def wie (self, mess, args):
        """be nice to her"""
        if args == 'gehts?':
            return 'Alle Parameter liegen innerhalb optimaler Bereiche, danke der Nachfrage.';

    @botcmd
    def roll (self, mess, args):
        """she rolls dice"""
        if len(args) > 0:
            rmax = random.randint(1, int(args))
            return rmax;
        else:
            rmax = random.randint(1, 6)
            return rmax;

    @botcmd
    def random (self, mess, args):
        """random test"""
        return random.randint(1, 10);