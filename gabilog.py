#!/usr/bin/env python
# -*- coding: utf-8 -*-

from botbase import BotBase,botcmd
from gabihelp import GabiHelp

import cgi

class GabiLog(BotBase):
    @botcmd
    def urls (self, mess, args):
        """Whispers you the last 20 URLs that where posted if no search term is supplied."""
        # srcJid = mess.getFrom()
        retUrls = []
        retMsg = []

        count = 0
        for (username, timestamp, url, title) in reversed(self.urlList):
            if args in url or args in title:
                retUrls.append((username, timestamp, url, title))
                count += 1
                if count >= 20:
                    break

        for (username, timestamp, url, title) in reversed(retUrls):
            if not title:
                title = url
            
            username = cgi.escape(self.encode_message(username)).encode("ascii", "replace")
            url = cgi.escape(self.encode_message(url)).encode("ascii", "replace")
            title = self.encode_message(title).encode("ascii", "replace")
            print title
            try:
                #newTitle = cgi.escape(unicode(str(title), "utf-8"))
                retMsg.append(_("{0} {1}: <a href='{2}'>{3}</a>").format(username, timestamp, url, title))
            except Exception, e:
                self.log.warning('Error while building URLS message with %s: %s' % (title, e))


        # self.send(srcJid, "http://chat.mmojunkies.net/csv-viewer/index.php?file=urls.csv", None, 'chat')
        self.send_simple_reply(mess, retMsg, True)
