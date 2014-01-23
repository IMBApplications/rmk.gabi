#!/usr/bin/env python
# -*- coding: utf-8 -*-

from botbase import BotBase,botcmd
from gabihelp import GabiHelp

import sys, getopt
import urllib
import simplejson

class GabiStarCitizen(BotBase):
    @botcmd
    def sctest(self):
        print "sc test ok"

# ideas: google, image (google)
# count redacted
# with google api: http://stackoverflow.com/questions/4441812/get-the-first-10-google-results-using-googleapi