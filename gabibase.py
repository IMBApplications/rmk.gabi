#!/usr/bin/python

from botbase import BotBase, botcmd
from gabiadmin import GabiAdmin
from gabicustom import GabiCustom
from gabifun import GabiFun
from gabilog import GabiLog
from gabihelp import GabiHelp
from gabihate import GabiHate

import logging

#http://docs.python.org/library/csv.html
import csv
import re

logging.basicConfig()
#logging.basicConfig(filename='logs/gabi.log',level=logging.DEBUG)

class GabiBase(GabiAdmin, GabiCustom, GabiFun, GabiHelp, GabiLog):
    def test(self):
        print "test"
