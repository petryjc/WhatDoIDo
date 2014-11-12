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
		self.weekly = ["1.0","1.0", "weekly", "weekly"]
		self.daily = ["0.0", "0.0", "daily", "daily"]
		self.routes = [["39.460346", "-87.332729", "route 1", "route 1"], ["39.478484","-87.334671", "route 2" ,"route 2"]]
		self.randoms = [["4.0","4.0", "random 1", "random 1"],["5.0","5.0", "random 2", "random 2"],["6.0","6.0", "random 3", "random 3"],["7.0","7.0", "random 4", "random 4"]]
		self.monthly = ["30.00", "30.00", "a monthly place", "monthly"]

		self.home_id = "home"
		self.work_id = "work"
		self.extra_id = "extra"
		self.weekly_id = "weekly"
		self.daily_id = "daily"
		self.random_ids = [1,2,3,4]
		self.route_ids = [5,6]
		self.monthly_id = "monthly"

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
		self.weekly_id = str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (self.weekly[0],self.weekly[1],self.weekly[2],self.weekly[3])))
		self.daily_id = str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (self.daily[0],self.daily[1],self.daily[2],self.daily[3])))
		self.monthly_id = str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (self.monthly[0],self.monthly[1],self.monthly[2],self.monthly[3])))
		
		for i in self.routes:
			self.route_ids.append(str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (i[0], i[1],i[2],i[3]))))
		
		for k in self.randoms:
			self.random_ids.append(str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (k[0], k[1],k[2],k[3]))))

		return self.home_id

	def initUser(self):

		username  = "CyclesTest2"
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
					timeCounter = self.addTravel(self.route_ids, timeCounter)        
					timeCounter = self.addEvent(self.work_id, timeCounter, 8)
					timeCounter = self.addTravel(self.route_ids, timeCounter)
				else:
					timeCounter = self.addEvent(self.home_id, timeCounter, 24)
					continue
				if i < 3:
					timeCounter = self.addEvent(self.extra_id, timeCounter, 3)
					timeCounter = self.addTravel(self.route_ids, timeCounter)

				temp = timeCounter
				while timeCounter.day == temp.day:
					temp = temp + timeDelta
					self.add(self.home_id, temp)
				timeCounter = temp

	def complicatedCycles(self):
		timeCounter = datetime.datetime(2014, 9, 1)
		timeDelta = datetime.timedelta(minutes=5)

		for x in range (0,24):
			for o in range(0,4):
				for i in range(0, 7):


					#daily
					if random.randint(0,100) > 15:
						timeCounter = self.addEvent(self.daily_id, timeCounter, 1)
					else:
						timeCounter = self.addEvent(self.home_id, timeCounter, 1)

					if timeCounter.day == 2:
						timeCounter = self.addEvent(self.monthly_id, timeCounter, 1)
					else:
						timeCounter = self.addEvent(self.home_id, timeCounter, 1)						 

					#work
					if i < 6 and random.randint(0,100) > 5:
						timeCounter = self.addEvent(self.home_id, timeCounter, 6)
						timeCounter = self.addTravel(self.route_ids, timeCounter)        
						timeCounter = self.addEvent(self.work_id, timeCounter, 8)
						timeCounter = self.addTravel(self.route_ids, timeCounter)
					#no work
					else:
						#weekly
						if i == 6 and random.randint(0,100) < 10:
							timeCounter = self.addEvent(self.home_id, timeCounter, 10)
							timeCounter = self.addEvent(self.weekly_id, timeCounter, 2)
							timeCounter = self.addEvent(self.home_id, timeCounter, 10)
						else:
							timeCounter = self.addEvent(self.home_id, timeCounter, 8)
							timeCounter = self.addEvent(self.random_ids[random.randint(0,len(self.random_ids) - 1)],timeCounter, 8)
							timeCounter = self.addEvent(self.home_id, timeCounter,6)
						continue

					#extra
					if i < 3 and random.randint(0,100) > 40:
						timeCounter = self.addEvent(self.extra_id, timeCounter, 3)
						timeCounter = self.addTravel(self.route_ids, timeCounter)


					temp = timeCounter
					if random.randint(0,1) == 1:	
						while timeCounter.day == temp.day:
							temp = temp + timeDelta
							self.add(self.home_id, temp)
					else:
						while timeCounter.day == temp.day:
							temp = temp + timeDelta
							self.add(self.random_ids[random.randint(0,len(self.random_ids) - 1)], temp)

					timeCounter = temp


	def addTravel(self,routes,timeCounter):
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
		#print(place)
		if (place != -1):
			Utils.execute("""INSERT INTO Users_Locations(user_id, location_id, time) VALUES(%s, %s, %s)""", (str(self.user_id), str(place), time))

	def runScript(self):
		self.initUser()
		self.simpleCycles()













#runScript()
