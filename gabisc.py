#!/usr/bin/env python
# -*- coding: utf-8 -*-


# https://robertsspaceindustries.com/api/stats/getCrowdfundStats


from botbase import BotBase,botcmd
from gabihelp import GabiHelp


import urllib
import urllib2
# from xml.dom.minidom import parse

class GabiStarCitizen(BotBase):
    @botcmd
    def fundstat(self, mess, args):
        """Star Citizen Crowdfunding stats"""
        req = urllib2.Request('https://robertsspaceindustries.com/api/stats/getCrowdfundStats')
        response = urllib2.urlopen(req, data)
        the_page = response.read()
        print the_page
        # self.send_simple_reply(mess, the_page)

# ideas: google, image (google)
# count redacted
# with google api: http://stackoverflow.com/questions/4441812/get-the-first-10-google-results-using-googleapi
# http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=Apple+Cake&start=4

    # @botcmd
    # def google(self):
    #     """Google something"""
    #     return 'nothing'

    # def google_search(searchFor):
         
    #     # &cx=00255077836266642015:u-scht7a-8i
    #     # &start=10
    #     xmlurl = 'http://www.google.com/search?'
    #     xmlsearch = 'q=' + searchFor + '&hl=' + self.localization + '&num=1&output=xml_no_dtd&client=google-csbe'

    #     try:
    #         xml = urllib.urlopen(xmlsearch)
    #         dom = parse(xml)
    #     except e as Exception:
    #         print(e)

    #     print dom

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
