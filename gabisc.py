#!/usr/bin/env python

from botbase import BotBase,botcmd
from gabihelp import GabiHelp

import csv

class GabiStarCitizen(BotBase):
    @botcmd
    def sctest(self):
        print "sc test ok"

