#!/usr/bin/python

from botbase import BotBase, botcmd
import datetime

class GabiHelp(BotBase):
    @botcmd
    def time( self, mess, args):
        """Zeigt die aktuelle Serverzeit an"""
        return str(datetime.datetime.now())
        
    @botcmd
    def testtime( self, mess, args):
        """Zeigt die aktuelle Serverzeit an"""
        now = datetime.datetime.now()
        return str(now.hour)

    @botcmd
    def ping (self, mess, args):
        """Antwortet mit einem pong"""
        return 'pong'
    
    @botcmd
    def help(self, mess, args):
            """   Returns a help string listing available options.

            Automatically assigned to the "help" command."""
            if not args:
                    if self.__doc__:
                            description = self.__doc__.strip()
                    else:
                            description = 'Available commands:'

                    usage = '\n'.join(sorted([
                            '%s:\t%s' % (name, (command.__doc__ or \
                                    '(undocumented)').strip().split('\n', 1)[0])
                            for (name, command) in self.commands.iteritems() \
                                    if name != 'help' \
                                    and not command._jabberbot_command_hidden
                    ]))
                    usage = '\n\n' + '\n\n'.join(filter(None, [usage, self.MSG_HELP_TAIL]))
            else:
                    description = ''
                    if args in self.commands:
                            usage = (self.commands[args].__doc__ or \
                                    'undocumented').strip()
                    else:
                            usage = self.MSG_HELP_UNDEFINED_COMMAND

            return ''.join(filter(None, [description, usage]))
