from utils import Utils
import cherrypy
import json

class Buddy(object):
  @cherrypy.expose
  def index(self):
    return "Buddies"

  @cherrypy.expose
  def request(self): 
    body = json.JSONDecoder().decode( cherrypy.request.body.read() )
    check = Utils.arg_check(body, ["token","buddy"])

    if (check[0]): 
      return check[1]

    # Find the user ID of the person making the request.
    user_check = Utils.validate_user(body["token"])
    if(user_check[0]):
      return user_check[1]
    user_id = user_check[1]

    matching_users = Utils.query("""SELECT * FROM Users WHERE username=%s OR email=%s""", 
              (body["buddy"],body["buddy"]))
              
    if len(matching_users) == 0:
      return json.JSONEncoder().encode( Utils.status_more( 112, "Could not locate user" ) )
    
    matching_user = matching_users[0]
    
    try:
        Utils.execute("""INSERT INTO Buddies(requester_id, requestee_id, approved) VALUE(%s,%s,0)""",
          (user_id,matching_user["user_id"]))
    except Exception:
        return json.JSONEncoder().encode({"status": Utils.status(3981,"Could not request buddy")})

    return json.JSONEncoder().encode(Utils.status_more(0, "OK"))

  
  @cherrypy.expose
  def pending_requests(self): 
    body = json.JSONDecoder().decode( cherrypy.request.body.read() )
    check = Utils.arg_check(body, ["token"])

    if (check[0]): 
      return check[1]

    # Find the user ID of the person making the request.
    user_check = Utils.validate_user(body["token"])
    if(user_check[0]):
      return user_check[1]
    user_id = user_check[1]

    requests = Utils.query("""SELECT user_id,username,email 
                              FROM Users u
                              JOIN Buddies b ON u.user_id = b.requester_id
                              WHERE b.requestee_id=%s AND b.approved=0""", 
              (user_id))
              
    return json.JSONEncoder().encode( {"status": Utils.status(0,"OK"),"requests":requests } )
    

  @cherrypy.expose
  def accept(self): 
    body = json.JSONDecoder().decode( cherrypy.request.body.read() )
    check = Utils.arg_check(body, ["token","buddy_id"])

    if (check[0]): 
      return check[1]

    # Find the user ID of the person making the request.
    user_check = Utils.validate_user(body["token"])
    if(user_check[0]):
      return user_check[1]
    user_id = user_check[1]

    try:
        Utils.execute("""UPDATE Buddies
                         SET approved=1
                         WHERE requester_id=%s AND requestee_id=%s""",
                         (body["buddy_id"],user_id))
    except Exception:
        return json.JSONEncoder().encode({"status": Utils.status(3981,"Could not approve buddy")})

    return json.JSONEncoder().encode(Utils.status_more(0, "OK"))
    
  @cherrypy.expose
  def list(self):
    body = json.JSONDecoder().decode( cherrypy.request.body.read() )
    check = Utils.arg_check(body, ["token"])

    if (check[0]): 
      return check[1]

    # Find the user ID of the person making the request.
    user_check = Utils.validate_user(body["token"])
    if(user_check[0]):
      return user_check[1]
    user_id = user_check[1]

    requests = Utils.query("""(SELECT user_id,username,email 
                              FROM Users u
                              JOIN Buddies b ON u.user_id = b.requester_id
                              WHERE b.requestee_id=%s AND b.approved=1) UNION
                              (SELECT user_id,username,email 
                              FROM Users u
                              JOIN Buddies b ON u.user_id = b.requestee_id
                              WHERE b.requester_id=%s AND b.approved=1)""",
              (user_id,user_id))
              
    return json.JSONEncoder().encode( {"status": Utils.status(0,"OK"),"requests":requests } )

    