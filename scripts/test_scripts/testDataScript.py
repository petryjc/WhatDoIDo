import os
import subprocess
import datetime
import random
import json
import uuid
import sys
import platform
from json import *
sys.path.insert(0, '../../code')
sys.path.insert(0, '../../code/api')
from utils import Utils
from events import Event
import urllib2


class TestScript:

	def __init__(self):

		self.home = ["39.456519","-87.335669", "825 Foxcrest, Terre Haute, IN, 47803", "home"]
		self.work = ["39.483597", "-87.323689", "5500 Wabash Ave, Terre Haute, IN, 47803","work"]
		self.extra = ["39.475398", "-87.350511", "4420 Wabash Ave, Terre Haute, IN 47803", "extra"]
		self.routes = [["40", "80", "route 1", "route 1"], ["50","80", "route 2" ,"route 2"], ["60","80","route 3", "route 3"]]

		self.home_id = ""
		self.work_id = ""
		self.extra_id = ""
		self.route_ids = []

	def initLocs(self):
		self.home_id = self.getLocationID(self.home)
		self.work_id = self.getLocationID(self.work)
		self.extra_id = self.getLocationID(self.extra)
		
		for route in self.routes:
			self.route_ids.append(self.getLocationID(route))

	def callPostCommand(self,command,location):
		#url = "http://" + platform.node() + ".wlan.rose-hulman.edu/" + location
		url = "http://localhost/" + location
		#url = "http://summary.pneumaticsystem.com/" + location
		headers = {"Content-Type" : 'application/json'}
		req = urllib2.Request(url, command, headers)
		response = urllib2.urlopen(req)  
		the_page = response.read()
	  
		return the_page

	def initUser(self):

		username  = "DemoTest"
		password  = "testing"
		email     = "test@rose-hulman.edu"

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
		print(loginResult)
                print registrationResult
		self.token =str(loginResult['token'])

		self.user_id = Utils.validate_user(self.token)[1] 

	def getLocationID(self, location):
		
		loc_id = Utils.query("SELECT location_id FROM Locations WHERE place = %s", (location[3]))
		
		if len(loc_id) > 0:
			return loc_id[0]["location_id"]
		else:
			return Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) 
			VALUES(%s, %s, %s, %s)""", (location[0], location[1], location[2], location[3]))
	
	def simpleCycles(self):

		timeCounter = datetime.datetime(2014, 12, 1)
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
		if (place != -1):
			Utils.execute("""INSERT INTO Users_Locations(user_id, location_id, time) 
								VALUES(%s, %s, %s)""", (str(self.user_id), str(place), time))

	def runScript(self):	
		self.initUser()
		self.initLocs()
		self.simpleCycles()

