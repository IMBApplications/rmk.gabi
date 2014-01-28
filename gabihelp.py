#!/usr/bin/env python
# -*- coding: utf-8 -*-

from botbase import BotBase, botcmd
import datetime

class GabiHelp(BotBase):
    @botcmd
    def time( self, mess, args):
        """Shows the current time"""
        self.send_simple_reply(mess, str(datetime.datetime.now()), True)
        
    @botcmd
    def ping (self, mess, args):
        """Answers with a pong"""
        self.send_simple_reply(mess, 'pong', True)
    
    @botcmd
    def help(self, mess, args):
        """Returns a help string listing available options.

        Automatically assigned to the "help" command."""
        if not args:
            if self.__doc__:
                description = self.__doc__.strip()
            else:
                description = _('Available commands:')

            usage = sorted(['%s:\t%s' % (name, (command.__doc__ or \
                                '(undocumented)').strip().split('\n', 1)[0])
                    for (name, command) in self.commands.iteritems() \
                        if name != 'help' \
                        and not command._jabberbot_command_hidden
            ])
            #usage = '\n\n' + '\n\n'.join(filter(None, [usage, self.MSG_HELP_TAIL]))
            usage = usage + [self.MSG_HELP_TAIL]
        else:
            description = ''
            if args in self.commands:
                usage = (self.commands[args].__doc__ or \
                        'undocumented').strip()
            else:
                usage = [self.MSG_HELP_UNDEFINED_COMMAND]

        # return [description] + usage
        self.send_simple_reply(mess, [description] + usage, True)
