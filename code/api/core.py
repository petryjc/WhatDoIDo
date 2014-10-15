from utils import Utils
import cherrypy
import json
import uuid

class API(object):

  @cherrypy.expose
  def index(self):
    return "API"

  @cherrypy.expose
  def login(self):

    body = json.JSONDecoder().decode( cherrypy.request.body.read() )
    
    check = Utils.arg_check(body, ["username","password"])
    if (check[0]):
		return check[1]

    matchingUsers = Utils.query("SELECT * FROM Users u WHERE u.username=%s AND u.password=SHA1(CONCAT(%s, u.salt))", (body["username"], body["password"]))
    
    if(len(matchingUsers) == 0):
      return json.JSONEncoder().encode({
        "status" : Utils.status(324,"Could not locate user")
      })
    elif (len(matchingUsers) == 1):
      sessionID = str(uuid.uuid4())
      Utils.execute("INSERT INTO User_Sessions(user_id, session_token) VALUES(%s, %s)",(matchingUsers[0]["user_id"], sessionID))
      
      return json.JSONEncoder().encode({
        "token": sessionID,
        "status" : Utils.status(0, "OK")
      })
    else:
      return json.JSONEncoder().encode({
        "status" : Utils.status(323,"The system is in an invalid state.")
      })

  @cherrypy.expose
  def logout(self):

    body = json.JSONDecoder().decode( cherrypy.request.body.read() )
    check = Utils.arg_check(body, ["token"])
    
    if (check[0]): 
      return check[1]



    count = Utils.execute("DELETE FROM User_Sessions WHERE session_token = %s",(body["token"]))
    if(count > 0):
      return json.JSONEncoder().encode({
        "status" : Utils.status(0, "OK")
      })
    else:
      return json.JSONEncoder().encode({
        "status" : Utils.status(125, "Could not locate user with provided token")
      })

  @cherrypy.expose
  def register(self):
    body = json.JSONDecoder().decode( cherrypy.request.body.read() )
    
    check = Utils.arg_check(body, ["username","password", "email"])
    if (check[0]):
            return check[1]
    
    
    password_hash = str(uuid.uuid4())
    count = Utils.execute("INSERT INTO Users (username, password, email, salt) VALUES (%s, SHA1(CONCAT(%s, %s)), %s, %s)", (body['username'], body['password'], password_hash, body['email'], password_hash) )
    
    if(count == 1):
      return json.JSONEncoder().encode({
        "status" : Utils.status(0, "OK")
      })
    else:
      return json.JSONEncoder().encode({
        "status" : Utils.status(431, "Could not register user account.")
      })
              
  @cherrypy.expose
  def deleteAccount(self):

    body = json.JSONDecoder().decode( cherrypy.request.body.read() )
    check = Utils.arg_check(body, ["username","password"])
    if (check[0]):
            return check[1]
    
    count = Utils.execute("DELETE u FROM Users u WHERE u.username = %s and u.password = SHA1(CONCAT(%s, u.salt))",(body["username"], body["password"]))
    
    if(count > 0):
      return json.JSONEncoder().encode({
        "status" : Utils.status(0, "OK")
      })
    else:
      return json.JSONEncoder().encode({
        "status" : Utils.status(433, "Could not delete user account.")
      })
    

