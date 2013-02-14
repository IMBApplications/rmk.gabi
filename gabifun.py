#!/usr/bin/python

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
        """Etwas ist IMBA"""
        if len(args) > 0:
            return args  + ' ist IMBA!'
        else:
            return 'Ich bin IMBA!'

            
    @botcmd
    def haha (self, mess, args):
        """gabi lacht"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            return 'Hahahaha, ' + args + ' is zum totlachen!'
        else:
            return 'Hahahaha! Man, ' + username  + ', du bist so witzig, ich lach mich tot!'

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

    @botcmd
    def slap (self, mess, args):
        """gabi gibt wem eine ohrfeige"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            return 'Betrachte dich als geohrfeigt, ' + args + '!'
        else:
            return username  + ', wen soll ich ohrfeigen?'

    @botcmd
    def afk (self, mess, args):
        """user away"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            message = args
        else:
            message = "AFK"
        self.afkList[username] = message
        return 'Bis spaeter, ' + username  + '. Viel Spass beim ' + message + '.'

    @botcmd
    def remind (self, mess, args):
        """remind a user with something when he comes back"""
        from_username = self.get_sender_username(mess)
        new_args = args.split(" ")

        if len(args) > 1:
            target_user = new_args[0].encode('ascii', 'replace')
            target_message = new_args[1:].encode('ascii', 'replace')

            ret_message = "Ich werde " + target_user + " ausrichten dass: " + target_message

            try:
                self.reminderDict[target_user].apend((from_username, target_message))
                # if isinstance(self.reminderDict[target_user], list):
                #     self.reminderDict[target_user] = []
            except Exception as e:
                print e

            

        else:
            ret_message = "Du musst einen namen gefolgt von der nachricht angeben."
            print self.reminderDict
        return ret_message

    @botcmd
    def username (self, mess, args):
        return self.get_my_username()

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
    def memo (self, mess, args):
        """sie merkt sich was"""
        username = self.get_sender_username(mess)
        if len(args) > 0:
            self.memList[username] = args;
            return 'Merke mir: "' + args + '".'
        elif username in self.memList:
            return 'Habe mir: "' + self.memList[username] + '" gemerkt.'
        else:
            return 'Ja, was denn?'

    @botcmd
    def werafk (self, mess, args):
        """sagt, was sie sich gemerkt hat"""
        if len(self.afkList) > 0:
            ret = ''
            for username in self.afkList.keys():
                ret = ret + "\n%-10s: %s" % (username, self.afkList[username])
            return ret;
        else:
            return 'Es hat sich niemand abgemeldet.'

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
    def penis (self, mess, args):
        """she flashes her ... aehm ... penis?"""
        return '8=========>'
