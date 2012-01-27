#!/usr/bin/python

from gabibase import GabiBase

username = 'user@domain.tld'
password = 'password'
nickname = 'Nickname'

bot = GabiBase(username,password)
bot.join_room('yourdomain@conference.domain.tld', nickname)
bot.serve_forever()

