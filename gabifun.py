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
        username = self.get_sender_username(mess)
        if len(args) > 0:
            return 'Senior ' + username  + ' no here. He ' + args + '.';
        else:
            return 'Senior ' + username  + ' no here.';

    @botcmd
    def username (self, mess, args):
        return self.get_my_username();

    @botcmd
    def baby (self, mess, args):
        """she is nice to you"""
        return 'Ja Schatz, was kann ich fuer dich tun?';

    @botcmd
    def rage (self, mess, args):
        """she rages for you"""
        if len(args) > 0:
            return 'Scheiss ' + args + '! Verkackter Mist, stinkiger!';
        else:
            return 'AARRRG! DRECKSVERWANZTEHURENSCHEISSMISTPIMMELKACKE!';

    @botcmd
    def wie (self, mess, args):
        """use wie gehts? to be nice to her"""
        if args == 'gehts?':
            return 'Alle Systeme arbeiten innerhalb optimaler Parameter, danke der Nachfrage.';

    @botcmd
    def roll (self, mess, args):
        """she rolls dice"""
        if len(args) > 0:
            rmax = random.randint(1, int(args))
        else:
            rmax = random.randint(1, 6)
        return str(rmax);

    @botcmd
    def titten (self, mess, args):
        """she flashes"""
        return '( . )( . )';
