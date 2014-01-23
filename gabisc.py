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
# http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=Apple+Cake&start=4

    @botcmd
    def google(self):
        """Google something"""
        return 'nothing'

   	def google_search(searchFor):
	    url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=large&%s" % (searchFor)
	    result = urllib.urlopen(url)
	    json = simplejson.loads(result.read())
	    status = json["responseStatus"]
	    if status == 200:
	        results = json["responseData"]["results"]
	        cursor = json["responseData"]["cursor"]
	        pages = cursor["pages"]
	        for r in results:
	            i = results.index(r) + (index -1) * len(results) + 1
	            u = r["unescapedUrl"]
	            rs.append(u)
	            if not quiet:
	                print("%3d. %s" % (i, u))
	        next_index  = None
	        next_offset = None
	        for p in pages:
	            if p["label"] == index:
	                i = pages.index(p)
	                if i < len(pages) - 1:
	                    next_index  = pages[i+1]["label"]
	                    next_offset = pages[i+1]["start"]
	                break
	        if next_index != None and next_offset != None:
	            if int(next_offset) < min_count:
	                search(query, next_index, next_offset, min_count, quiet, rs)
	    return rs

# def print_usage():
#     s = "usage: " + sys.argv[0] + " "
#     for o in OPTIONS[0]:
#         if o != ":" : s += "[-" + o + "] "
#     print(s + "query_string\n")

# def main():
#     min_count = 64
#     try:
#         opts, args = getopt.getopt(sys.argv[1:], *OPTIONS)
#         for opt, arg in opts:
#             if opt in ("-m", "--min"):
#                 min_count = int(arg)
#         assert len(args) > 0
#     except:
#         print_usage()
#         sys.exit(1)
#     qs = " ".join(args)
#     query = urllib.urlencode({"q" : qs})
#     search(query, 1, "0", min_count)

# if __name__ == "__main__":
#     main()
