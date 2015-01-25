import unittest
import os
import subprocess
import time
import json
import uuid
import sys
import platform
from json import *
sys.path.insert(0, '../code')
sys.path.insert(0, '../code/api')
from utils import Utils
from timeutils import Day, Week, Month
from datetime import *
from events import Event
import urllib2

def callPostCommand(command, location):
  #url = "http://" + platform.node() + ".wlan.rose-hulman.edu/" + location
  url = "http://localhost:8080/" + location
  #url = "http://summary.pneumaticsystem.com/" + location
  headers = {"Content-Type" : 'application/json'}
  req = urllib2.Request(url, command, headers)
  response = urllib2.urlopen(req)
  
  the_page = response.read()
  return the_page
  

def add_data(o):
  location_id = Utils.execute_id("""INSERT INTO Locations(address) VALUES('The place I am')""",())
  event_id = Utils.execute_id
  ("""
  SELECT @UserID := user_id FROM User_Sessions WHERE session_token = %s;
  INSERT INTO Events(event_type, user_id, location_id, name, locked, deleted)
  VALUES ('cycle', @UserID, %s, 'test cycle', TRUE, FALSE);""", (o.loginResult['token'], location_id))

  Utils.execute("""
  INSERT INTO Cyclical_Events(event_id,cycle_type,occurances) 
  VALUES (%s,'weekly',%s);""", (event_id, json.JSONEncoder().encode([(1000,2000),(10000,10060)])))

  return {"location_id" : location_id, "event_id" : event_id }
    
  
class Test(unittest.TestCase):

  def setUp(self):
    self.username  = str(uuid.uuid4())
    self.password  = str(uuid.uuid4())
    self.email     = str(uuid.uuid4())
    self.device_id = str(uuid.uuid4())
    
    self.registerCommand = json.JSONEncoder().encode({
      "username" : self.username,
      "password" : self.password,
      "email"    : self.email
    })
    self.registrationResult = json.loads(callPostCommand(self.registerCommand, 'api/register'))
    
    self.loginCommand = json.JSONEncoder().encode({
      "username"  : self.username,
      "password"  : self.password
    })
    self.loginResult = json.loads(callPostCommand(self.loginCommand, 'api/login'))

  def test_registration(self):
    self.assertEqual(self.registrationResult['status']['code'],0)
    self.assertEqual(self.registrationResult['status']['msg'],"OK")
    
  def test_fail_registration_duplicate_user(self):
    callPostCommand(self.registerCommand, 'api/register')
    #self.assertEqual(newRegistrationResult['status']['code'],431)
    #self.assertEqual(newRegistrationResult['status']['msg'], "Could not register user account.")
    
  def test_username_case_sensitivity(self):
    registerCommand = json.loads(self.registerCommand)
    email = str(uuid.uuid4())
    
    #Get user name with same characters but different case
    origional = str(registerCommand['username'])
    username = str.upper(origional)
    if  username == origional:
      username = str.lower(origional)

    registerCmd = json.JSONEncoder().encode({
      "username" : username,
      "password" : registerCommand['password'],
      "email"    : email
    })
    result = json.loads(callPostCommand(registerCmd, 'api/register'))
    self.assertEqual(result['status']['code'],0)

    deleteAccountCommand = json.JSONEncoder().encode({
      "username" : username,
      "password" : registerCommand['password']
    })
    td = json.loads(callPostCommand(deleteAccountCommand, 'api/deleteAccount'))
    self.assertEqual(td['status']['code'],0)
    
  def test_login(self):
    self.assertEqual(self.loginResult['status']['code'],0)
    self.assertEqual(self.loginResult['status']['msg'],"OK")
    self.assertTrue(self.loginResult['token'])    
     
  def test_fail_login_nonexistent_user(self):
    loginCommand = json.JSONEncoder().encode({
      "username" : str(uuid.uuid4()),
      "password" : str(uuid.uuid4())
    })
    newLoginResult = json.loads(callPostCommand(loginCommand, 'api/login'))
    self.assertEqual(newLoginResult['status']['code'],324)
    self.assertEqual(newLoginResult['status']['msg'], "Could not locate user")
    self.assertFalse('token' in newLoginResult)
    
  def test_logout(self):
    logoutCommand = json.JSONEncoder().encode({
      "token" : self.loginResult['token']
    })
    logoutResult = json.loads(callPostCommand(logoutCommand, 'api/logout'))
    self.assertEqual(logoutResult['status']['code'],0)
    self.assertEqual(logoutResult['status']['msg'],"OK")
    
    #then relog in so we can delete the user account
    self.loginResult = json.loads(callPostCommand(self.loginCommand, 'api/login'))
    
  def test_fail_logout_nonexistent_token(self):
    logoutCommand = json.JSONEncoder().encode({
      "token" : str(uuid.uuid4())
    })
    logoutResult = json.loads(callPostCommand(logoutCommand, 'api/logout'))
    self.assertEqual(logoutResult['status']['code'],125)
    self.assertEqual(logoutResult['status']['msg'],"Could not locate user with provided token")
  
  def test_location_save(self):
    locationSaveCommand = json.JSONEncoder().encode({
      "latitude" : 39.485661,
      "longitude" : -87.332014,
      "token" : self.loginResult["token"]
    })  
    locationResult = json.loads(callPostCommand(locationSaveCommand, 'api/location/add'))
    self.assertEqual(locationResult['status']['code'],0)
    
  def test_suggestion_single(self):
    self.assertTrue( callPostCommand("", 'api/suggestion/single'))

  def test_calendar(self):
    data = add_data(self)
     
    command = json.JSONEncoder().encode({
      "token" : self.loginResult["token"],
      "beginning" : "12-01-2014",
      "ending" : "12-31-2014"
    })
    result = json.loads(callPostCommand(command, 'api/suggestion/calendar'))
    self.assertEqual(result['status']['code'],0)
    self.assertEqual(len(result['calendar']),10)
    self.assertEqual(result['calendar'][0]["name"],"test cycle")
    
  def test_event_list(self):
    data = add_data(self)
    
    command = json.JSONEncoder().encode({
      "token" : self.loginResult['token']
    })  
    result = json.loads(callPostCommand(command, 'api/event/list'))
    self.assertEqual(result['status']['code'],0)
    self.assertEqual(len(result['events']),1)
    self.assertEqual(result['events'][0]['event_id'],data["event_id"])
    self.assertEqual(result['events'][0]['deleted'], False)
    self.assertEqual(result['events'][0]['locked'], True)
    self.assertEqual(result['events'][0]['event_type'], 'cycle')
    self.assertEqual(result['events'][0]['cycle_type'], 'weekly')
    self.assertEqual(result['events'][0]['address'], 'The place I am')
    self.assertEqual(result['events'][0]['name'], 'test cycle')
    self.assertEqual(len(result['events'][0]['occurances']), 2)
    self.assertEqual(len(result['events'][0]['occurances'][0]), 2)
    
  def test_event_get(self):
    data = add_data(self)
    
    command = json.JSONEncoder().encode({
      "token"      : self.loginResult['token'],
      "event_id"   : data["event_id"],
      "event_type" : "cycle"
    })  
    result = json.loads(callPostCommand(command, 'api/event/get'))
    self.assertEqual(result['status']['code'],0)
    self.assertEqual(result['event_id'],data["event_id"])
    self.assertEqual(result['deleted'], False)
    self.assertEqual(result['locked'], True)
    self.assertEqual(result['event_type'], 'cycle')
    self.assertEqual(result['cycle_type'], 'weekly')
    self.assertEqual(result['address'], 'The place I am')
    self.assertEqual(result['name'], 'test cycle')
    self.assertEqual(len(result['occurances']), 2)
    self.assertEqual(len(result['occurances'][0]), 2)
    
    
  def test_event_update(self):
    
    data = add_data(self)
    
    command1 = json.JSONEncoder().encode({
      "token" : self.loginResult['token'],
      "event_id" : data["event_id"],
      "event_type" : "cycle",
      "locked" : 0,
      "deleted" : 1,
      "name" : "This is a new name",
      "occurances" : [("Monday 12:30","Monday 14:00"),("Saturday 3:00","Saturday 7:00")],
      "cycle_type" : "weekly"
    })  
    
    result1 = json.loads(callPostCommand(command1, 'api/event/update'))
    self.assertEqual(result1['status']['code'],0)
    
    command = json.JSONEncoder().encode({
      "token" : self.loginResult['token']
    })  
    result = json.loads(callPostCommand(command, 'api/event/list'))
    self.assertEqual(result['status']['code'],0)
    self.assertEqual(len(result['events']),1)
    self.assertEqual(result['events'][0]['event_id'],data["event_id"])
    self.assertEqual(result['events'][0]['deleted'], True)
    self.assertEqual(result['events'][0]['locked'], False)
    self.assertEqual(result['events'][0]['event_type'], 'cycle')
    self.assertEqual(result['events'][0]['cycle_type'], 'weekly')
    self.assertEqual(result['events'][0]['address'], 'The place I am')
    self.assertEqual(result['events'][0]['name'], 'This is a new name')
    self.assertEqual(result['events'][0]['occurances'], [["Monday 12:30","Monday 14:00"],["Saturday 3:00","Saturday 7:00"]])
    
  def test_timeutils(self):
    t1 = datetime.now()
    s1 = Day.seconds(t1)
    t1p = Day.time(s1)
    s11 = Day.time_to_seconds(t1p)
    self.assertTrue(abs(s11-s1) < 60)
    
    s2 = Week.seconds(t1)
    t2p = Week.time(s2)
    s21 = Week.time_to_seconds(t2p)
    self.assertTrue(abs(s21-s2) < 60)
    
    s3 =  Month.seconds(t1)
    t3p = Month.time(s3)
    s31 = Month.time_to_seconds(t3p)
    self.assertTrue(abs(s31-s3) < 60)
    
  def tearDown(self):
    deleteAccountCommand = json.JSONEncoder().encode({
      "username" : self.username,
      "password" : self.password
    })
    td = json.loads(callPostCommand(deleteAccountCommand, 'api/deleteAccount'))
    self.assertEqual(td['status']['code'],0)

if __name__ == '__main__':
  unittest.main()

