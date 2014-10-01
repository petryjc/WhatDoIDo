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
