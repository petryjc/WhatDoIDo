import os
import subprocess
import datetime
import random
import json
import uuid
import sys
import platform
from json import *
sys.path.insert(0, '../code')
sys.path.insert(0, '../code/api')
from utils import Utils
from events import Event
import urllib2


class TestScript:

	def __init__(self):
		self.home = ["39.456519","-87.335669", "825 Foxcrest, Terre Haute, IN, 47803", "home"]
		self.work = ["39.483597", "-87.323689", "5500 Wabash Ave, Terre Haute, IN, 47803","work"]
		self.extra = ["39.475398", "-87.350511", "4420 Wabash Ave, Terre Haute, IN 47803", "extra"]
		self.routes = [["39.460346", "-87.332729", "route 1", "route 1"], ["39.478484","-87.334671", "route 2" ,"route 2"]]

		self.home_id = ""
		self.work_id = ""
		self.extra_id = ""
		self.route_ids = []

		self.user_id = ""
		self.token = ""

	def callPostCommand(self,command,location):
		#url = "http://" + platform.node() + ".wlan.rose-hulman.edu/" + location
		url = "http://localhost/" + location
		#url = "http://summary.pneumaticsystem.com/" + location
		headers = {"Content-Type" : 'application/json'}
		req = urllib2.Request(url, command, headers)
		response = urllib2.urlopen(req)  
		the_page = response.read()
	  
		return the_page

	def initLocations(self):


		self.home_id = str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (self.home[0],self.home[1],self.home[2],self.home[3])))
		self.work_id = str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (self.work[0],self.work[1],self.work[2],self.work[3])))
		self.extra_id = str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (self.extra[0],self.extra[1],self.extra[2],self.extra[3])))

		for i in self.routes:
			self.route_ids.append(str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (i[0], i[1],i[2],i[3]))))
		
		return self.home_id

	def initUser(self):

		username  = "CyclesTest"
		password  = "testing"
		email     = "glenngs@rose-hulman.edu"
		
		registerCommand = json.JSONEncoder().encode({
		"username" : username,
		"password" : password,
		"email" : email
		})
		
		registrationResult = json.loads(self.callPostCommand(registerCommand, 'api/register'))

		loginCommand = json.JSONEncoder().encode({
		"username" : username,
		"password" : password,
		})

		loginResult = json.loads(self.callPostCommand(loginCommand, 'api/login'))
		self.token =str(loginResult['token'])

		self.user_id = Utils.validate_user(self.token)[1]
		


	def simpleCycles(self):

		timeCounter = datetime.datetime(2014, 9, 1)
		timeDelta = datetime.timedelta(minutes=5)

		for o in range(0,4):
			for i in range(0, 7):
				if i < 6:
					timeCounter = self.addEvent(self.home_id, timeCounter, 8)
					timeCounter = self.misc(self.route_ids, timeCounter)        
					timeCounter = self.addEvent(self.work_id, timeCounter, 8)
					timeCounter = self.misc(self.route_ids, timeCounter)
				else:
					timeCounter = self.addEvent(self.home_id, timeCounter, 24)
					continue
				if i < 3:
					timeCounter = self.addEvent(self.extra_id, timeCounter, 3)
					timeCounter = self.misc(self.route_ids, timeCounter)

				temp = timeCounter
				while timeCounter.day == temp.day:
					temp = temp + timeDelta
					self.add(self.home_id, temp)
				timeCounter = temp


	def misc(self,routes,timeCounter):
		timeDelta = datetime.timedelta(minutes=5)
		for l in range(0,4):
			timeCounter = timeCounter + timeDelta
			self.add(routes[random.randint(0, len(routes) - 1)], timeCounter)
		return timeCounter


	def addEvent(self,place, timeCounter ,hours):
		timeDelta = datetime.timedelta(minutes=5)
		for k in range(0, hours * 12): 
			timeCounter = timeCounter + timeDelta
			self.add(place, timeCounter)
		return timeCounter

	def add(self,place,time):
		print("hey: ")
		print(place)
		if (place != -1):
			Utils.execute("""INSERT INTO Users_Locations(user_id, location_id, time) VALUES(%s, %s, %s)""", (str(self.user_id), str(place), time))

	def runScript(self):
		self.initUser()
		self.simpleCycles()













#runScript()
