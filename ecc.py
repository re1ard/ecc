# -*- coding: utf-8 -*-
# External Chat Commands

#######################################
##contact: https://vk.com/id27919760 ##
#######################################

from vk_api import VkApi
from vk_api import Captcha
from vk_api.longpoll import VkLongPoll, VkEventType

from antigate import AntiGate

from json import load, dump

import urllib
import time
import os
import traceback

#t - allow change title
#i - allow invite

class anticaptcha:
	gate = None
	processing = False

	def __init__(self,agkey):
		self.gate = AntiGate(agkey)
		print 'good shit'
		print 'antigate balance: ' + str(self.gate.balance())
		return None

	def captchasolution(self,error):
		link = "./captcha_directory/"+str(time.time())+".jpg"
		urllib.urlretrieve(error.get_url(), link)
		print 'captcha loaded to directory: ' + link
		sid = self.gate.send(link)
		print 'done... lets begin to solution'
		key = self.gate.get(sid)
		print 'ok... this code: ' + key
		os.rename("./captcha_directory/"+key+".jpg")
		return key

	def solution(self,error):
		if self.processing:
			while self.processing:
				time.sleep(3)
			return True,0
			
		else:
			self.processing = True
			id = error.try_again(self.captchasolution(error))
			self.processing = False
			return False,id

class freecaptcha:
	processing = False

	def __init__(self,sleep_time = 90):
		print 'real shit'
		self.sleeping = sleep_time

	def captchasolution(self):
		time.sleep(self.sleeping)
		return True

	def solution(self,error):
		if self.processing:
			while self.processing:
				time.sleep(6)
			return True,0
		else:
			self.processing = True
			self.captchasolution()
			id = error.func(*error.args,**error.kwargs)
			self.processing = False
			return False,id

class methods:	
	def __init__(self,api,agh = ''):
		self.api = api
		if agh:
			self.AG = anticaptcha(agh)
		else:
			self.AG = freecaptcha()

	def send_msg(self,event,text,args_values = {}):
		values = {
			'chat_id': event.chat_id,
			'message': text
			}
		if args_values:
			values.update(args_values)

		try:
			return self.api.method('messages.send', values)
		except Captcha as error:
			self.AG.solution(error)
			return True

	def get_admin(self,event):
		response = self.api.method('messages.getChat',{'chat_id':event.chat_id})
		return response['admin_id']

	def kick_user(self,event,user_id):
		try:
			return self.api.method('messages.removeChatUser',{'chat_id':event.chat_id,'user_id':user_id})
		except Captcha as error:
			self.AG.solution(error)
			return True

class core:
	def __init__(self,l,p,agkey = ''):
		self.api = VkApi(l,p)
		self.api.auth()
		#######################
		self.methods = methods(self.api,agkey)
		#######################
		self.lp = VkLongPoll(self.api)
		#######################
		self.config = self.loadcfg()
		#######################
		self.ecc_arg = u'ecc'
		#######################
		self.chat_admins = {}
		self.chat_users = {}
		#######################
		self.action_cfg = {
			#'chat_title_update':{
			#		'permition': 't',
			#		'try':0
			#			},
			'chat_invite_user':{
					'permition': 'i',
					'try':1
						}
			}
		#######################
		self.chat_cfg = {
			'admin_id':0,
			'moders':{},
			'title':'',
			'enable':True
				}

	def loadcfg(self):
		try:
			with open('ecc.config.json') as data_file:
				return load(data_file)
		except:
			with open('ecc.config.json', 'w') as data_file:
				dump({},data_file)
				return {}

	def savecfg(self):
		with open('ecc.config.json', 'w') as data_file:
			dump(self.config,data_file)
			return True

	def update(self):
		for event in self.lp.listen():
			try:
				self.handler(event)
			except:
				traceback.print_exc()

	def handler(self,event):
		if True:
			if event.type == VkEventType.MESSAGE_NEW:
				if event.from_chat:
					if event.from_me and event.text:
						if event.text == u'on' + self.ecc_arg:
							if not event.chat_id in self.chat_admins:
								self.chat_admins.update({event.chat_id:unicode(self.methods.get_admin(event))})
							if event.user_id == self.chat_admins[event.chat_id]:
								if event.chat_id in self.config:
									if self.config[event.chat_id]['enable']:
										return self.methods.send_msg(event,'already on')
									else:
										self.config[event.chat_id]['enable'] = True
										self.savecfg()
										return self.methods.send_msg(event,'ready on')
								else:
									self.config[event.chat_id] = self.chat_cfg
									self.config[event.chat_id].update({'admin_id':event.user_id})
									self.savecfg()
									return self.methods.send_msg(event,'ready on')

						if event.text == u'off' + self.ecc_arg:
							if not event.chat_id in self.chat_admins:
								self.chat_admins.update({event.chat_id:unicode(self.methods.get_admin(event))})
							if event.user_id == self.chat_admins[event.chat_id]:
								if event.chat_id in self.config:
									if self.config[event.chat_id]['enable']:
										self.config[event.chat_id]['enable'] = False
										self.savecfg()
										return self.methods.send_msg(event,'ready off')
									else:
										return self.methods.send_msg(event,'already off')
								else:
									self.config[event.chat_id] = self.chat_cfg
									self.config[event.chat_id].update({'admin_id':event.user_id})
									self.config[event.chat_id].update({'enable':False})
									self.savecfg()
									return self.methods.send_msg(event,'ready off')

				if event.attachments:
					if 'source_act' in event.attachments and event.attachments['source_act'] in self.action_cfg:
						#######3
						# MOD THIS	#######################	
						#######3
						if event.chat_id in self.config and self.config[event.chat_id]['enable']:
							##########THIS
							if not event.attachments['from'] == self.config[event.chat_id]['admin_id']:
								###########this!!!<<
								self.methods.kick_user(event,event.attachments['source_mid'])
								if event.chat_id in self.chat_users:
									if event.attachments['from'] in self.chat_users[event.chat_id]:
										if self.chat_users[event.chat_id][event.attachments['from']] == 0:
											del self.chat_users[event.chat_id][event.attachments['from']]
											return self.methods.kick_user(event,event.attachments['from'])
										else:
											self.chat_users[event.chat_id][event.attachments['from']] -= 1
											return
									else:
										self.chat_users[event.chat_id][event.attachments['from']] = self.action_cfg[event.attachments['source_act']]['try']
										return
								else:
									self.chat_users[event.chat_id] = {}
									self.chat_users[event.chat_id][event.attachments['from']] = self.action_cfg[event.attachments['source_act']]['try']
									return


def main(main_core):
	main_core.update()

if __name__ == '__main__':
	main(core('login','password'))