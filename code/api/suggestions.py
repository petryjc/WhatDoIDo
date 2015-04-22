from utils import Utils
from timeutils import Day, Week, Month
from Queue import PriorityQueue
import cherrypy
import json
from datetime import *
from operator import itemgetter
from movie import Movie

class Suggestion(object):
  @cherrypy.expose
  def index(self):
    return "Suggestion"

  @cherrypy.expose
  def single(self):
    body = json.JSONDecoder().decode( cherrypy.request.body.read() )
    check = Utils.arg_check(body, ["token"])

    if (check[0]):
      return check[1]

    # Find the user ID of the person making the request.
    user_check = Utils.validate_user(body["token"])
    if(user_check[0]):
      return user_check[1]
    user_id = user_check[1]

    t = datetime.now()

    calendar = self.calendar_handler(user_id,t,t)

    #if the user has a current event they are supposed to be doing, tell them to do it    
    for e in calendar:
      print("Inside")
      beginning = datetime.strptime(e["beginning"],"%Y-%m-%dT%H:%M:%S.%f")
      ending = datetime.strptime(e["ending"],"%Y-%m-%dT%H:%M:%S.%f")
      if t > beginning and t < ending:
        return json.JSONEncoder().encode({"location":e["location"],
                                          "name":e["name"],
                                          "beginning":datetime.now().isoformat(),
                                          "status":Utils.status(0,"OK")})      

    #if they don't have a current event, tell them to go to a movie

    movie_results = Movie.get_movies(user_id)
    if movie_results:
      print(movie_results)
      movie_results["name"] = "Movies"
      return json.JSONEncoder().encode(movie_results)

    return json.JSONEncoder().encode({"name":"Nothing Could Be Found","status":Utils.status(0,"OK")})


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

    beginning = datetime.strptime(body["beginning"],"%m-%d-%Y").date()
    ending = datetime.strptime(body["ending"],"%m-%d-%Y").date()

    calendar = self.calendar_handler(user_id,beginning,ending)

    return json.JSONEncoder().encode({"calendar":calendar,"status":Utils.status(0,"OK")})

  def calendar_handler(self,user_id,beginning,ending):
    events = Utils.query("""SELECT *
                            FROM (Events e JOIN Locations l
                            ON e.location_id = l.location_id) JOIN Cyclical_Events ce ON ce.event_id = e.event_id
                            WHERE user_id = %s""", (user_id))

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
                "ending" : (day + timedelta(seconds=occurance[1] - dayStartSeconds)).isoformat()})

    return calendar
    

  def placeSpanningEvents(self, user_id, calendar, beginning, ending):

    sortedCalendar = sorted(calendar, key=itemgetter('beginning'))

    spanningEvents = Utils.query("""SELECT * 
                                    FROM (Events e JOIN Locations l ON e.location_id = l.location_id) 
                                    JOIN Spanning_Events se ON se.event_id = e.event_id
                                    WHERE e.user_id = %s""", (user_id))
    eventsByDaysLeft = []

    for i in range(0, len(spanningEvents)-1):
      lastOccurance = Utils.query("""SELECT time
                                     FROM Users_Locations
                                     ORDER BY time DESC
                                     WHERE user_id = %s
                                     AND location_id = %s
                                     AND is_route = 0
                                     LIMIT 1""", (user_id, spanningEvents[i]["location_id"]))
      spanningEvents[i]["last_occurance"] = lastOccurance
      spanningEvents[i]["last_chance"] = lastOccurance + spanningEvents[i]["min_time_between"] + spanningEvents[i]["range_of_span"]

    pq = PriorityQueue()

    eventsThatCanBePlaced = [e for e in spanningEvents if (e["last_occurance"] + e["min_time_between"]) >= beginning and (e["last_occurance"] + e["min_time_between"]) <= ending]
    sortedEventsToPlace = sorted(eventsThatCanBePlaced, itemgetter('last_chance'))
    pq.put(0,(sortedCalendar,sortedEventsToPlace,[]))
    while not pq.empty():
      (currentScore, (currentCalendar, eventsToPlace, placedEvents)) = pq.get()
      if eventsToPlace.empty(): # We've placed every event in the calendar. Good job!
        return currentCalendar
      for i in range(0, len(currentCalendar) - 2):
        eventEnding = strptime(currentCalendar[i]["ending"], "%Y-%m-%dT%H:%M:%S")
        eventBeginning = strptime(currentCalendar[i+1]["beginning"],"%Y-%m-%dT%H:%M:%S")
        time_between_events = eventBeginning - eventEnding
        num_placed = 0
        for s in range(0, len(eventsToPlace) - 1):
          if eventENding - eventsToPlace[s]["last_occurance"] >= eventsToPlace[s]["min_time_between"] and time_between_events > eventsToPlace[s]["avg_length_of_event"]:
            num_placed += 1
            nextCalendar = list(currentCalendar)
            nextEventsToPlace = list(eventsToPlace)
            nextPlacedEvents = list(placedEvents)
            nextCalendar.insert(i+1,{
              "name" : eventsToPlace[s]["name"],
              "location" : eventsToPlace[s]["address"],
              "event_id" : eventsToPlace[s]["event_id"],
              "event_type" : "spanning",
              "beginning" : eventEnding,
              "ending" : eventEnding + eventsToPlace[s]["avg_length_of_event"]
              })
            nextPlacedEvents.append(nextEventsToPlace.pop(s))
            nextCalendarScore = self.scoreCalendar(nextCalendar)
            pq.put((nextCalendarScore,(nextCalendar,nextEventsToPlace,nextPlacedEvents)))
        if num_placed == 0: # We don't have room for more events.
          return currentCalendar
    print "Well, something done goofed."
    print "Emptied PriorityQueue while placing Spanning Events."        

   # print spanningEvents

  def scoreCalendar(self, calendar):
    sortedCalendar = sorted(calendar, key=itemgetter('beginning'))
    calendarScore = 0
    for i in range(0, len(sortedCalendar) - 1):
        eventScore = 0
        currentEvent = sortedCalendar[i]
        if i < len(sortedCalendar)-1:
            nextEvent == sortedCalendar[i+1]
        if (i < len(sortedCalendar)-1) and self.eventsGetDistanceScored(currentEvent,nextEvent):
            ceLocation = Utils.query("""SELECT latitude, longitude
                                                  FROM Locations
                                                  WHERE address = %s""", (currentEvent["location"]))
            neLocation = Utils.query("""SELECT latitude, longitude
                                               FROM Locations
                                               WHERE address = %s""", (nextEvent["location"]))
            distance = Utils.haversine(ceLocation["latitude"],ceLocation["longitude"],neLocation["latitude"],neLocaiton["longitude"])
            eventScore += distance
        calendarScore += eventScore
    return calendarScore
     
        
  def eventsGetDistanceScore(self, event1, event2):
    return (event1["event_type"] == "spanning") or (event1["event_type"] == "cycle" and event2["event_type"] == "spanning")
            
            
    
