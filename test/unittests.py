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
from utils import Utils
import urllib2

def callPostCommand(command, location):
  #url = "http://" + platform.node() + ".wlan.rose-hulman.edu/" + location
  url = "http://localhost/" + location
  #url = "http://summary.pneumaticsystem.com/" + location
  headers = {"Content-Type" : 'application/json'}
  req = urllib2.Request(url, command, headers)
  response = urllib2.urlopen(req)
  
  the_page = response.read()
  return the_page
  
class TestBackendService(unittest.TestCase):

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
      "password"  : self.password,
      "device_id" : self.device_id
    })
    self.loginResult = json.loads(callPostCommand(self.loginCommand, 'api/login'))

  def test_registration(self):
    self.assertEqual(self.registrationResult['status']['code'],0)
    self.assertEqual(self.registrationResult['status']['msg'],"OK")
    
  def test_fail_registration_duplicate_user(self):
    newRegistrationResult = json.loads(callPostCommand(self.registerCommand, 'api/register'))
    self.assertEqual(newRegistrationResult['status']['code'],431)
    self.assertEqual(newRegistrationResult['status']['msg'], "Could not register user account.")
    
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
    
  def tearDown(self):
    deleteAccountCommand = json.JSONEncoder().encode({
      "username" : self.username,
      "password" : self.password
    })
    td = json.loads(callPostCommand(deleteAccountCommand, 'api/deleteAccount'))
    self.assertEqual(td['status']['code'],0)

if __name__ == '__main__':
  unittest.main()

