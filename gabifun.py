#!/usr/bin/env python

import random

from botbase import BotBase, botcmd

class GabiFun(BotBase):
    @botcmd
    def fetzig (self, mess, args='Aggravate'):
        """Lets fetz"""
        if len(args) > 0:
            return 'Fetzig? Hab ich fetzig gehoert? ' + args  + ' ist fetzig!'
        else:
            return 'Fetzig? Hab ich fetzig gehoert? ICH bin fetzig!'

    @botcmd
    def imba (self, mess, args):
        """Something is IMBA"""
        if len(args) > 0:
            return args  + _(' is IMBA!')
        else:
            return _('I am IMBA!')
            
    @botcmd
    def haha (self, mess, args):
        """gabi lacht"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            return 'Hahahaha, ' + args + ' is zum totlachen!'
        else:
            return 'Hahahaha! Man, ' + username  + ', du bist so witzig, ich lach mich tot!'

    @botcmd
    def slap (self, mess, args):
        """gabi gibt wem eine ohrfeige"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            return 'Betrachte dich als geohrfeigt, ' + args + '!'
        else:
            return username  + ', wen soll ich ohrfeigen?'

    @botcmd
    def baby (self, mess, args):
        """she is nice to you"""
        return 'Ja Schatz, was kann ich fuer dich tun?'

    @botcmd
    def rage (self, mess, args):
        """she rages for you"""
        if len(args) > 0:
            return 'Scheiss ' + args + '! Verkackter Mist, stinkiger!'
        else:
            return 'AARRRG! DRECKSVERWANZTEHURENSCHEISSMISTPIMMELKACKE!'

    @botcmd
    def wie (self, mess, args):
        """use wie gehts? to be nice to her"""
        if args == 'gehts?':
            return 'Alle Systeme arbeiten innerhalb optimaler Parameter, danke der Nachfrage.'

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
        """she flashes her titties"""
        return '( . )( . )'

    @botcmd
    def zoidberg (self, mess, args):
        """she draws zoidberg"""
        return '(\/) (^,,,^) (\/)'