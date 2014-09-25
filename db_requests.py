#!/usr/bin/env python

import pymongo
from bson.objectid import ObjectId
from md5 import md5
from datetime import datetime
import re

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class DBRequests(object):
	def __init__(self):
		conn = pymongo.MongoClient("mongodb://admin:admin@ds039000.mongolab.com:39000/heroku_app29902999")
		self.database = conn["heroku_app29902999"]

	def autorize(self, login, pswd):
		response = self.database.users.find_one({"login": login})
		
		if (response == None):
			return {"status": "ERR_NO_LOGIN_FOUND", "id": None}
		
		if(response["hash_pswd"] != md5(pswd).hexdigest()):
			return {"status": "ERR_WRONG_PASS", "id": None}
			
		return {"status": "OK", "id": str(response["_id"])}
	
	def getUsernameById(self, idUser):
		response = self.database.users.find_one({"_id": ObjectId(idUser)})
		if(response == None):
			return {"status": "ERR_NO_ID_FOUND", "username": None}
		else:
			return {"status": "OK", "username": response["login"]}
	
	def signupUser(self, username, password):
		response = self.database.users.find_one({"login": username})
		if(response == None):
			response = self.database.users.insert({"login": username, "hash_pswd": md5(password).hexdigest()})	
			return {"status": "OK"}

		else:
			return {"status": "ERR_USERNAME_EXIST"}

	def getChannels(self, reqstr = None):
		if(reqstr == None):
			response = self.database.channels.find().limit(30)
			ans = {"response": [ {"name": i["name"], "id": str(i["_id"])} for i in response ]}
			return ans
		else:
			regex = re.compile(reqstr, flags=re.IGNORECASE)
			response = self.database.channels.find({"name": regex}).limit(30)
			ans = {"response": [ {"name": i["name"], "id": str(i["_id"])} for i in response ]}
			return ans
	
	def getMessagesByChannelId(self, idChannel):
		response = self.database.messages.find({"id_channel": ObjectId(idChannel)}).sort('datetime').limit(30)
		ans = {"messages": []}
		for i in response:
			username = self.database.users.find_one({"_id": ObjectId(i["id_user"])})
			username = username["login"]
			ans["messages"].append(username + ": " + i["text"])
		return ans
	
	def writeNewMessage(self, idChannel, idUser, text):
		response = self.database.messages.insert({"id_channel": ObjectId(idChannel), "id_user": ObjectId(idUser), "datetime": datetime.now(), "text": text})

	def addNewChannel(self, channelName):
		response = self.database.channels.insert({"name": channelName})
