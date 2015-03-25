import MySQLdb
import MySQLdb.cursors
import json
import traceback

class Utils:
  @staticmethod
  def database():
    return MySQLdb.connect( host="localhost", user="root", passwd="fee9duX3", db="WhatDoIDo", cursorclass=MySQLdb.cursors.DictCursor )

  @staticmethod
  def query(q, p):
    #print q % p
    db = Utils.database()
    cur = db.cursor()
    cur.execute(q, p)
    result = cur.fetchall()
    cur.close()
    db.close()
    return result

  @staticmethod
  def execute(q, p):
    #print q % p
    try:
      db = Utils.database()
      cur = db.cursor()
      cur.execute(q, p)
      count = cur.rowcount
      cur.close()
      db.commit()
      db.close()
      return count
    except Exception:
      traceback.print_exc()
      return -1
      
  @staticmethod
  def execute_id(q, p):
    #print q % p
    try:
      db = Utils.database()
      cur = db.cursor()
      cur.execute(q, p)
      cur.close()
      db.commit()
      result = cur.lastrowid
      db.close()
      return result
    except Exception:
      traceback.print_exc()
      return -1

  @staticmethod
  def arg_check( body, checks):
    errors = ""
    for check in checks:
      if check not in body:
        errors = "%s'%s', " % (errors, check)
    return (len(errors) > 0 , json.JSONEncoder().encode( Utils.status_more( 10, "The following fields were not present: %s" % errors[:-2] )))
  
  @staticmethod
  def validate_user(token):
# Find the user ID of the person making the request.
    results = Utils.query(""" SELECT user_id FROM User_Sessions WHERE session_token = %s; """, token)
    if len( results ) is 0:
      return (1, json.JSONEncoder().encode( Utils.status_more( 11, "No user is associated with that token")))
    return (0, int(results[0]["user_id"]))

  @staticmethod
  def status(code, msg):
    return {
      "code" : code,
      "msg"  : msg
    }

  @staticmethod
  def status_more( code, msg ):
    return {
      "status" : {
        "code" : code,
        "msg"  : msg
      }
    }
    
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
	R = 3958.8 # Earth radius in miles

	dLat = radians(lat2 - lat1)
	dLon = radians(lon2 - lon1)
	lat1 = radians(lat1)
	lat2 = radians(lat2)

	a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
	c = 2*asin(sqrt(a))

	return R * c

