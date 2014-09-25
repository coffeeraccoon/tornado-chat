#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os.path 

import tornado.httpserver 
import tornado.ioloop 
import tornado.options 
import tornado.web
import tornado.websocket

from db_requests import DBRequests

from tornado.options import define, options
define("port", default=5000, help="run on the given port", type=int)

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json

class IndexHandler(tornado.web.RequestHandler): 
    def get_current_user(self):
        return self.get_secure_cookie("user")

    @tornado.web.authenticated
    def get(self):
	request = DBRequests()
	username = request.getUsernameById(self.current_user)["username"]
        self.render('public/index.html', username=username, id_user = "'"+self.current_user+"'")

class LoginHandler(tornado.web.RequestHandler):
        def get_current_user(self):
		return self.get_secure_cookie("user")

	def get(self):
		self.render('public/signin.html')
	def post(self):
		if not self.current_user:
			request = DBRequests()
			auth_response = request.autorize(self.get_argument("login"), self.get_argument("password"))
			if(auth_response["status"] != "OK"):
				self.redirect("/login")
				return
			else:
				self.set_secure_cookie("user", auth_response["id"])
				self.redirect("/")
		else:
			self.redirect("/")

class LogoutHandler(tornado.web.RequestHandler):
	def get(self):
		self.clear_cookie("user")
		self.redirect("/login")

class SignupHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('public/signup.html')
	def post(self):
		login = self.get_argument("login")
		password = self.get_argument("password")
		
		if(login == None or password == None):
			self.redirect("/signup")
			return
		if(login == "" or password == ""):
			self.redirect("/signup")
			return
		
		request = DBRequests()
		response = request.signupUser(login, password)
		if(response["status"] == "OK"):
			self.redirect("/login")
			return
		else:
			self.redirect("/signup")
			

class ChannelsHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("user")

	@tornado.web.authenticated
	def get(self):
		request = DBRequests()
		reqstr = self.get_argument("req", None, True)
		
		response = request.getChannels(reqstr)
		answer = json.dumps(response, separators=(',', ': '))
		self.write(answer)

class MessagesHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("user")

	@tornado.web.authenticated
	def get(self):
		idChannel = self.get_argument("req", None, True)
		if(idChannel == None):
			response = {"messages": []}
			answer = json.dumps(response, separators=(',', ': '))
			self.write(answer)
		else:
			request = DBRequests()
			response = request.getMessagesByChannelId(idChannel)
			answer = json.dumps(response, separators=(',', ': '))
			self.write(answer)

	@tornado.web.authenticated
	def post(self):
		idChannel = self.get_argument("channel", None, True)
		text = self.get_argument("text", None, True)
		
		if(idChannel == None or text == None or idChannel == "" or text == ""):
			self.write("FAIL")
		else:
			request = DBRequests()
			request.writeNewMessage(idChannel, self.current_user, text)
			self.write("OK")

class WebSocket(tornado.websocket.WebSocketHandler):
	def open(self):
		self.application.webSocketsPool.append(self)

	def on_close(self):
		for key, value in enumerate(self.application.webSocketsPool):
			if value == self:
				del self.application.webSocketsPool[key]

	def on_message(self, message):
		msgdict = json.loads(message)
		request = DBRequests()
		request.writeNewMessage(msgdict["id_channel"], msgdict["id_user"], msgdict["text"])
		
		for key, value in enumerate(self.application.webSocketsPool):
			value.ws_connection.write_message(message)

class UsernameHandler(tornado.web.RequestHandler):
	def get(self):
		idUser = self.get_argument("req", None, True)
		if(idUser == None):
			self.write("unknown")
			return
		request = DBRequests()
		name = request.getUsernameById(idUser)["username"]
		self.write(name)

class AddChannelHandler(tornado.web.RequestHandler):
	def get(self):
		channelName = self.get_argument("req", None, True)
		
		if(channelName == None):
			return
		
		request = DBRequests()
		request.addNewChannel(channelName)

class Application(tornado.web.Application):
	def __init__(self):
		self.webSocketsPool = []

		settings = {"cookie_secret": "17c356ec98b72c0ad4b6337beddef772", "login_url": "/login"}
		handlers=[(r'/', IndexHandler),
 (r'/login', LoginHandler),
 (r'/logout', LogoutHandler), 
 (r'/channels', ChannelsHandler),
 (r'/signup', SignupHandler),
 (r'/messages', MessagesHandler),
 (r'/websocket/?', WebSocket),
 (r'/username', UsernameHandler),
 (r'/addchannel', AddChannelHandler),
 (r'/(.*)', tornado.web.StaticFileHandler, {'path': "public/"})]

		tornado.web.Application.__init__(self, handlers, **settings)
		
app = Application()

if __name__ == '__main__':
    tornado.options.parse_command_line() 
    
    http_server = tornado.httpserver.HTTPServer(app) 
    http.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

