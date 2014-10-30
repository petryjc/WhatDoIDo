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

home = ["39.456519","-87.335669", "825 Foxcrest, Terre Haute, IN, 47803", "home"]
work = ["39.483597", "-87.323689", "5500 Wabash Ave, Terre Haute, IN, 47803","work"]
extra = ["39.475398", "-87.350511", "4420 Wabash Ave, Terre Haute, IN 47803", "extra"]
routes = [["39.460346", "-87.332729", "", "route 1"], ["39.478484","-87.334671", "" ,"route 2"]]

home_id = ""
work_id = ""
extra_id = ""
route_ids = []

user_id = ""
token = ""

def callPostCommand(command, location):
	#url = "http://" + platform.node() + ".wlan.rose-hulman.edu/" + location
	url = "http://localhost/" + location
	#url = "http://summary.pneumaticsystem.com/" + location
	headers = {"Content-Type" : 'application/json'}
	req = urllib2.Request(url, command, headers)
	response = urllib2.urlopen(req)  
	the_page = response.read()
  
	return the_page



def initLocations():


	home_id = str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (home[0],home[1],home[2],home[3])))
	work_id = str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (work[0],work[1], work[2], work[3])))
	extra_id = str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (extra[0],extra[1],extra[2], extra[3])))

	for i in routes:
		route_ids.append(str(Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) VALUES(%s, %s, %s, %s)""", (i[0], i[1],i[2],i[3]))))
	
	return home_id

def initUser():

	username  = "CyclesTest"
	password  = "testing"
	email     = "glenngs@rose-hulman.edu"
	device_id = str(uuid.uuid4())	
	
	registerCommand = json.JSONEncoder().encode({
	"username" : username,
	"password" : password,
	"email" : email
	})
	
	registrationResult = json.loads(callPostCommand(registerCommand, 'api/register'))

	loginCommand = json.JSONEncoder().encode({
	"username" : username,
	"password" : password,
	})

	loginResult = json.loads(callPostCommand(loginCommand, 'api/login'))
	token = loginResult['token']

	user_id = Utils.validate_user(token)


def simpleCycles():

	timeCounter = datetime.datetime(2014, 9, 1)
	timeDelta = datetime.timedelta(minutes=5)

	for o in range(0,4):
		for i in range(0, 7):
			if i < 6:
				timeCounter = addEvent(home_id, timeCounter, 8)
				timeCounter = misc(route_ids, timeCounter)        
				timeCounter = addEvent(work_id, timeCounter, 8)
				timeCounter = misc(route_ids, timeCounter)
			else:
				timeCounter = addEvent(home_id, timeCounter, 24)
				continue
			if i < 3:
				timeCounter = addEvent(extra_id, timeCounter, 3)
				timeCounter = misc(route_ids, timeCounter)

			temp = timeCounter
			while timeCounter.day == temp.day:
				temp = temp + timeDelta
				add(home_id, temp)
			timeCounter = temp


def misc(routes, timeCounter):
	timeDelta = datetime.timedelta(minutes=5)
	for l in range(0,4):
		timeCounter = timeCounter + timeDelta
		add(routes[random.randint(0, len(routes) - 1)], timeCounter)
	return timeCounter


def addEvent(place, timeCounter ,hours):
	timeDelta = datetime.timedelta(minutes=5)
	for k in range(0, hours * 12): 
		timeCounter = timeCounter + timeDelta
		add(place, timeCounter)
	return timeCounter

def add(place, time):
	print("hey: ")
	print(place)
	if (place != -1):
		Utils.execute("""INSERT INTO Users_Locations(user_id, location_id, time) VALUES(%s, %s, %s)""", (str(user_id), str(place), time))

def runScript():
	initLocations()
	initUser()
	simpleCycles()













#runScript()
