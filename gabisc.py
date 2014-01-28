#!/usr/bin/env python
# -*- coding: utf-8 -*-


# https://robertsspaceindustries.com/api/stats/getCrowdfundStats
# '{"chart":"day","fans":true,"funds":true,"alpha_slots":true}'


from botbase import BotBase,botcmd
from gabihelp import GabiHelp


import urllib
import urllib2
import json
import locale
import feedparser

# debian: apt-get install python-feedparser

from xml.dom.minidom import parse

class GabiStarCitizen(BotBase):
    def fetch_json(self, url, values):
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)

        try:
            data = json.loads(response.read())
        except Exception as e:
            self.log.warning("ERROR fetching JSON data from %s: %s" % (url, e))
            self.send_simple_reply(mess, "ERROR fetching JSON data from %s" % url)

        return data        

    @botcmd
    def scfunding(self, mess, args):
        """Star Citizen Crowdfunding stats"""
        locale.setlocale(locale.LC_ALL, '')

        url = 'https://robertsspaceindustries.com/api/stats/getCrowdfundStats'
        values = {'fans' : 'true',
                  'funds' : 'true',
                  'alpha_slots' : 'true' }
        data = self.fetch_json(url, values)

        raised = locale.format("%.0f", (data['data']['funds'] / 100), grouping = True)
        percentage = data['data']['next_goal']['percentage']
        goal = data['data']['next_goal']['goal']
        goalTitle = data['data']['next_goal']['title']
        fans = locale.format("%.0f", data['data']['fans'], grouping = True)

        the_page = _('${0} ({1}%%) raised of {2} ({3}). {4} Star Citizens').format(raised, percentage, goalTitle, goal, fans)
        self.send_simple_reply(mess, the_page)

    @botcmd
    def scnews(self, mess, args):
        url = 'https://robertsspaceindustries.com/comm-link/rss'
        feedData = []
        try:
            rss = feedparser.parse(url)

        except Exception as e:
            self.log.warning("ERROR fetching RSS data from %s: %s" % (url, e))
            self.send_simple_reply(mess, "ERROR fetching RSS data from %s" % url)
            return

        count = 0
        feedData.append(_("<a href='{0}' alt='{1}'>{2}</a>").format(rss.feed.linkr, rss.feed.scription, ss.feed.title))
        for entry in feed.entries:
            feedData.append(_("<a href='{0}' alt='{1}'>{1} {2}</a>").format(entry.link, entry.description, entry.published, entry.title))

        print len(rss.entries)

        self.send_simple_reply(mess, feedData)

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
