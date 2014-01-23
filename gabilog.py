#!/usr/bin/env python
# -*- coding: utf-8 -*-

from botbase import BotBase,botcmd
from gabihelp import GabiHelp

import csv

class GabiLog(BotBase):
    @botcmd
    def urls (self, mess, args):
        """Whispers you all URLs that where posted"""
        jid = mess.getFrom()
        """handler = self.get_handler_csv_urls_read()
        msg = ""
        for row in  csv.reader(handler, delimiter=';', quotechar='#'):
                msg += '-\t' + str(row[0]) + " ( " + str(row[1]) + " ) " + row[2] + ' \n'

        handler.close()"""
        self.send(jid, "http://chat.mmojunkies.net/csv-viewer/index.php?file=urls.csv", None, 'chat')
