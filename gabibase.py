#!/usr/bin/python

from botbase import BotBase, botcmd
import datetime
import logging

#http://docs.python.org/library/csv.html
import csv
import re

#logging.basicConfig()
logging.basicConfig(filename='logs/gabi.log',level=logging.DEBUG)

class GabiBase(BotBase):
	def get_csv_admin_users_handler(self):
		return open('db/admins.csv', 'rb')

	def get_handler_csv_urls_write(self):
		return open('db/urls.csv', 'ab')

	def get_handler_csv_urls_read(self):
		return open('db/urls.csv', 'rb')

	@botcmd
	def time( self, mess, args):
		"""Zeigt die aktuelle Serverzeit an"""
		return str(datetime.datetime.now())

	@botcmd
	def ping (self, mess, args):
		"""Antwortet mit einem pong"""
		return 'pong'

	@botcmd
	def fetzig (self, mess, args='Aggravate'):
		"""Lets fetz"""
		return 'Fetzig? Hab ich fetzig gehoert? ' + args  + '  ist fetzig!';

	@botcmd
	def kick (self, mess, args):
		"""Kickt einen Nutzer aus dem aktuelle Channel"""
		room = mess.getFrom().getStripped()
		self.do_kick(room, args)

	@botcmd
	def topic (self, mess, args):
		"""Setzt die Ueberschrift im aktuellen Channel"""
		room = mess.getFrom().getStripped()
		self.do_topic(room, args)

	@botcmd
	def invite (self, mess, args):
		"""Laed einen Nutzer in den Channel ein (jabber-id angeben!)"""
		room = mess.getFrom().getStripped()
		self.do_invite(room, args)

	@botcmd
	def admins (self, mess, args):
		"""Zeigt alle admins"""
		msg = 'Admins:\n'
		handler = self.get_csv_admin_users_handler()
		for row in  csv.reader(handler, delimiter=';', quotechar='#'):
			msg += '->\t' + str(row[1]) + " (" + str(row[0]) + ")" + '\n'

		handler.close()
		return msg

	@botcmd
	def urls (self, mess, args):
		"""Fluestert dir alle URLS"""
		jid = mess.getFrom()
		handler = self.get_handler_csv_urls_read()
		msg = ""
		for row in  csv.reader(handler, delimiter=';', quotechar='#'):
			msg += '-\t' + str(row[0]) + " ( " + str(row[1]) + " ) " + row[2] + ' \n'

		handler.close()
		self.send(jid, msg, None, 'chat')

	@botcmd
	def quit (self, mess, args):
		"""Beendet/Restartet Gabi"""
		exit()
		return 'Exiting/Restarting...'


	@botcmd
	def help(self, mess, args):
		"""   Returns a help string listing available options.

		Automatically assigned to the "help" command."""
		if not args:
			if self.__doc__:
				description = self.__doc__.strip()
			else:
				description = 'Available commands:'

			usage = '\n'.join(sorted([
				'%s:\t%s' % (name, (command.__doc__ or \
					'(undocumented)').strip().split('\n', 1)[0])
				for (name, command) in self.commands.iteritems() \
					if name != 'help' \
					and not command._jabberbot_command_hidden
			]))
			usage = '\n\n' + '\n\n'.join(filter(None, [usage, self.MSG_HELP_TAIL]))
		else:
			description = ''
			if args in self.commands:
				usage = (self.commands[args].__doc__ or \
					'undocumented').strip()
			else:
				usage = self.MSG_HELP_UNDEFINED_COMMAND

		return ''.join(filter(None, [description, usage]))


	def on_not_a_command(self, mess):
		type = mess.getType()
		jid = mess.getFrom()
		props = mess.getProperties()
		text = mess.getBody()
		username = self.get_sender_username(mess)

		#fangen wir mal an mit gucken ob der bb oder was sagen will
		reg_ex_bb = (r".*?bb$", r".*?bin mal weg.*?", r".*?baba")
		for reg in reg_ex_bb:
			c = re.compile(reg)
			if c.match(text) != None:
				self.send_simple_reply(mess, "Bis dann mal {0}".format(username))
				return

		#so jetzt alle URLS
		reg_ex_url = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
		c = re.compile(reg_ex_url)
		writer = None
		handler = None

		for url in c.findall(text):
			if writer == None:
				handler = self.get_handler_csv_urls_write()
				writer = csv.writer(handler, delimiter=';', quotechar='#')
				writer.writerow([username, str(datetime.datetime.now()) , url])

		if writer != None:
			handler.close()

	def on_came_online(self, jid):
		jidSplit = '{0}'.format(jid).partition('/')
		room = jidSplit[0]
		user = jidSplit[2]
		#hallo = 'Hi {0}'.format(user)
		#self.send(room, hallo, None, 'groupchat')

	def on_gone_offline(self, jid):
		jidSplit = '{0}'.format(jid).partition('/')
		room = jidSplit[0]
		user = jidSplit[2]
		hallo = 'Und da ist {0} weg'.format(user)
		self.send(room, hallo, None, 'groupchat')


