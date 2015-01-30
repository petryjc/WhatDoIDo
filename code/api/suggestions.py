from utils import Utils
from timeutils import Day, Week, Month
import cherrypy
import json
from datetime import *
from operator import itemgetter

class Suggestion(object):
  @cherrypy.expose
  def index(self):
    return "Suggestion"

  @cherrypy.expose
  def single(self):
    #TODO
    return json.JSONEncoder().encode(
      {
        "title":"Test Title",
        "description":"This is a hard coded, test event for UI testing purposes only",
        "location":"5500 Wabash Avenue",
        "justification":"Clearly it's a big deal",
        "time":datetime.now().isoformat(),
        "cost":11
      }
    )

  @cherrypy.expose
  def calendar(self): 
    body = json.JSONDecoder().decode( cherrypy.request.body.read() )
    check = Utils.arg_check(body, ["token","beginning","ending"])

    if (check[0]): 
      return check[1]

    # Find the user ID of the person making the request.
    user_check = Utils.validate_user(body["token"])
    if(user_check[0]):
      return user_check[1]
    user_id = user_check[1]

    events = Utils.query("""SELECT * 
                            FROM (Events e JOIN Locations l 
                            ON e.location_id = l.location_id) JOIN Cyclical_Events ce ON ce.event_id = e.event_id
                            WHERE user_id = %s""", (user_id))

    beginning = datetime.strptime(body["beginning"],"%m-%d-%Y").date()
    ending = datetime.strptime(body["ending"],"%m-%d-%Y").date()

    calendar = []

    for day in [datetime.combine(beginning + timedelta(n), datetime.min.time()) for n in range((ending-beginning).days + 1)]:
      for cycleType in [Day,Week,Month]:
        dayStartSeconds = cycleType.seconds(day)
        dayEndSeconds = cycleType.seconds(day + timedelta(hours=23, minutes=59))
        events_of_type = [i for i in events if i["cycle_type"] == cycleType.NAME]
        for event in events_of_type:
          for occurance in json.loads(event["occurances"]):
            if occurance[0] > dayStartSeconds and occurance[0] < dayEndSeconds:
              calendar.append({
                "name" : event["name"],
                "location" : event["address"],
                "event_id" : event["event_id"],
                "event_type" : "cycle",
                "beginning" : (day + timedelta(seconds=occurance[0] - dayStartSeconds)).isoformat(),
                "ending" : (day + timedelta(seconds=occurance[1] - dayStartSeconds)).isoformat()
              })
    """print "CALENDAR"
    print calendar
    print "=========="
    self.placeSpanningEvents(user_id, sorted(calendar,key=itemgetter('beginning'))
    print "=========="""
    
    return json.JSONEncoder().encode({"calendar":calendar,"status":Utils.status(0,"OK")})

  # def placeSpanningEvents(self, user_id, calendar):

    # spanningEvents = Utils.query("""SELECT * 
                                    # FROM (Events e JOIN Locations l ON e.location_id = l.location_id) 
                                    # JOIN Spanning_Events se ON se.event_id = e.event_id
                                    # WHERE e.user_id = %s""", (user_id))
    
    # for i in range(0, len(calendar) - 1):
      # freeTime = calendar[i+1]["beginning"] - calendar[i]["ending"]
      # for spanningEvent in spanningEvents:
        # if freeTime > spanningEvent["avg_length_of_event"]
          # calendar.append({
                # "name" : spanningEvent["name"],
                # "location" : spanningEvent["address"],
                # "event_id" : spanningEvent["event_id"],
                # "event_type" : "spanning",
                # "beginning" : calendar[i]["ending"],
                # "ending" : calendar[i+1]["beginning"]
              # })
        

    # print spanningEvents
