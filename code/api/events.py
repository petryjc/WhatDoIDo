from timeutils import Day, Week, Month
from utils import Utils
import cherrypy
import json
from datetime import datetime, timedelta, date, time, MINYEAR, MAXYEAR

def partition(l, attr):
    d = {}
    [d[getattr(i, attr)].append(i) if getattr(i, attr) in d else d.update({getattr(i ,attr): [i]}) for i in l]
    return d

class LocationBlock(object):
  def __init__(self, loc):
    self.location_id = loc["location_id"]
    self.address = loc["address"]
    self.start_time = loc["time"]
    self.end_time = loc["time"]
  def __str__(self):
    return self.addresss + " " + self.start_time

class Event(object):
  @cherrypy.expose
  def index(self):
    return "Event"

  @cherrypy.expose
  def get(self):
    body = json.JSONDecoder().decode( cherrypy.request.body.read() )

    check = Utils.arg_check(body, ["token","event_id","event_type"])
    if (check[0]):
        return check[1]
    if body.get( "token", None ) is None:
        return json.JSONEncoder().encode( Utils.status_more( 10, "No session token present" ) )

     # Find the user ID of the person making the request.
    user_check = Utils.validate_user(body["token"])
    if(user_check[0]):
      return user_check[1]
    user_id = user_check[1]

    if body["event_type"] == "cycle":
      results = Utils.query(
              """ SELECT ce.event_id, name, address, cycle_type, occurances, locked, deleted 
                  FROM (Events e JOIN Cyclical_Events ce ON e.event_id = ce.event_id)  
                  JOIN Locations l ON e.location_id = l.location_id
                  WHERE user_id = %s AND ce.event_id = %s;
              """,
              (user_id,body["event_id"]))
            
      type_to_class = {"daily":Day,"weekly":Week,"monthly":Month}
      
      if len(results) == 1:
        res = results[0]
        cycle_class = type_to_class[res["cycle_type"]]
        res["occurances"] = [(cycle_class.time(x[0]),cycle_class.time(x[1])) for x in json.JSONDecoder().decode(res["occurances"])]        
        res["event_type"] = 'cycle'
        res.update( Utils.status_more( 0, "OK" ) )
        return json.JSONEncoder().encode( res )
      else:
        return json.JSONEncoder().encode( Utils.status_more( 111, "Could not locate event" ) )
    
    elif body["event_type"] == "spanning":
        results = Utils.query(
              """ SELECT se.event_id, name, address, min_time_between, range_of_span, avg_length_of_event, locked, deleted 
                  FROM (Events e JOIN Spanning_Events se ON e.event_id = se.event_id)  
                  JOIN Locations l ON e.location_id = l.location_id
                  WHERE user_id = %s AND se.event_id = %s;
              """,
              (user_id,body["event_id"]))
	if len(results) == 1:
		res = results[0]        
		res["event_type"] = 'spanning'
		res.update( Utils.status_more( 0, "OK" ) )
        	return json.JSONEncoder().encode( res )
      	else:
        	return json.JSONEncoder().encode( Utils.status_more( 111, "Could not locate event" ) )

    return json.JSONEncoder().encode( Utils.status_more( 111, "Event type {0} not available".format(body["event_type"]) ) )
    
  @cherrypy.expose
  def list(self):
    body = json.JSONDecoder().decode( cherrypy.request.body.read() )
    print "GOT HERE"

    check = Utils.arg_check(body, ["token"])
    if (check[0]):
        return check[1]
    if body.get( "token", None ) is None:
        return json.JSONEncoder().encode( Utils.status_more( 10, "No session token present" ) )

     # Find the user ID of the person making the request.
    user_check = Utils.validate_user(body["token"])
    if(user_check[0]):
      return user_check[1]
    user_id = user_check[1]

    resultsCycle = list(Utils.query(
              """ SELECT ce.event_id, event_type, name, address, cycle_type, occurances, locked, deleted 
                  FROM (Events e JOIN Cyclical_Events ce ON e.event_id = ce.event_id)  
                  JOIN Locations l ON e.location_id = l.location_id
                  WHERE user_id = %s;
              """,
              (user_id)))
 
    
    resultsSpanning = list(Utils.query(
                    """ SELECT se.event_id, event_type, name, address, min_time_between, range_of_span, avg_length_of_event, locked, deleted 
                        FROM (Events e JOIN Spanning_Events se ON e.event_id = se.event_id)  
                        JOIN Locations l ON e.location_id = l.location_id
                        WHERE user_id = %s;
                    """, (user_id)))

    resultsCycle.extend(resultsSpanning)

    results = resultsCycle

    type_to_class = {"daily":Day,"weekly":Week,"monthly":Month}
    
    if results:
      for row in results:
        if row["event_type"] == "cycle"  
          cycle_class = type_to_class[row["cycle_type"]]
          row["occurances"] = [(cycle_class.time(x[0]),cycle_class.time(x[1])) for x in json.JSONDecoder().decode(row["occurances"])]
        
    ret = {
            "events" : results
            }
    ret.update( Utils.status_more( 0, "OK" ) )

    return json.JSONEncoder().encode( ret )
    
  @cherrypy.expose
  def update(self):
    body = json.JSONDecoder().decode( cherrypy.request.body.read() )

    check = Utils.arg_check(body, ["token","event_id","event_type","locked","deleted","name"])
    if (check[0]):
        return check[1]
    if body.get( "token", None ) is None:
        return json.JSONEncoder().encode( Utils.status_more( 10, "No session token present" ) )

     # Find the user ID of the person making the request.
    user_check = Utils.validate_user(body["token"])
    if(user_check[0]):
      return user_check[1]
    user_id = user_check[1]

    
    if body["event_type"] == "cycle":
      #extra parameters required for cyclical events
      check = Utils.arg_check(body, ["occurances","cycle_type"])
      if (check[0]):
        return check[1]
        
      event_user_id = Utils.query(""" SELECT user_id FROM Events WHERE event_id = %s;""", body["event_id"] )[0]["user_id"]
      
      if user_id != event_user_id:
        return json.JSONEncoder().encode( Utils.status_more( 100, "Permission Denied" ) )
              
      type_to_class = {"daily":Day,"weekly":Week,"monthly":Month}
      cycle_class = type_to_class[body["cycle_type"]]
      occurances = [(cycle_class.time_to_seconds(x[0]),cycle_class.time_to_seconds(x[1])) for x in body["occurances"]]        
          
      try:
        Utils.execute("""UPDATE Events 
                         SET locked = %s ,
                             deleted = %s,
                             name = %s
                         WHERE event_id = %s""",
         (body["locked"],body["deleted"],body["name"],body["event_id"]))
        Utils.execute("""UPDATE Cyclical_Events
                         SET occurances = %s,
                             cycle_type = %s
                         WHERE event_id = %s""", (json.JSONEncoder().encode(occurances),cycle_class,body["event_id"]))
      except Exception:
        return json.JSONEncoder().encode({"status": Utils.status(3981,"Could not update event")})

      return json.JSONEncoder().encode(Utils.status_more(0, "OK"))
    
    elif body["event_type"] == "spanning":
      check = Utils.arg_check(body, ["min_time_between", "range_of_span", "avg_length_of_event"])
      if (check[0]):
        return check[1]

      event_user_id = Utils.query(""" SELECT user_id FROM Events WHERE event_id = %s;""", body["event_id"] )[0]["user_id"]
      
      if user_id != event_user_id:
        return json.JSONEncoder().encode( Utils.status_more( 100, "Permission Denied" ))

      try:
        Utils.execute("""UPDATE Events 
                 SET locked = %s ,
                     deleted = %s,
                     name = %s
                 WHERE event_id = %s""",
        (body["locked"],body["deleted"],body["name"],body["event_id"]))
        Utils.execute("""UPDATE Spanning_Events
                          SET min_time_between = %s,
                              range_of_span = %s,
                              avg_length_of_event = %s
                          WHERE event_id = %s""",(body["min_time_between"],body["range_of_span"],body["avg_length_of_event"],body["event_id"]))
      except Exception:
        return json.JSONEncoder().encode({"status": Utils.status(3981,"Could not update event")})

      return json.JSONEncoder().encode(Utils.status_more(0, "OK"))

    return json.JSONEncoder().encode(Utils.status_more(333, "Unidentified event type"))


  def generateCyclicalEvents(self, user_id, start_time = datetime(1900,1,1), end_time = datetime(MAXYEAR,12,31)):
    #Utils.execute("DELETE FROM Cyclical_Events WHERE user_id = %s", (user_id)) #remove previous eyclical events
    travel_history = Utils.query("""SELECT * FROM Locations l JOIN Users_Locations ul ON l.location_id = ul.location_id WHERE ul.user_id = %s AND time BETWEEN %s AND %s ORDER BY ul.time""", (user_id, start_time, end_time))
    
    if(len(travel_history) < 2):
      return "Requires at least 2 data points"
    endTime = travel_history[-1]["time"]

    location_blocks = [LocationBlock(list(travel_history).pop(0))]
    for d in travel_history:
      if (d["location_id"] == location_blocks[-1].location_id):
        if (d["time"] - location_blocks[-1].end_time) >= timedelta(minutes=20):
            # Spent at least 20 minutes away. This is a new event.
            location_blocks.append(LocationBlock(d))
        location_blocks[-1].end_time = d["time"]
      else:
        location_blocks.append(LocationBlock(d))

    parts = partition(location_blocks, "location_id")
    
    maxsep = 600 #separation in seconds between entries in the same cycle 
    cycle_event_list = []
    non_cyclic_list = []
    for location_block_list in parts.values():
      loc = location_block_list[0]
      for sorter in [Day, Week, Month]:
        if (len(location_block_list) >= 3): #it takes at least 3 occurances to show signs of a cycle
          lbl = [(x, sorter.seconds(x.start_time), sorter.seconds(x.end_time)) for x in location_block_list]
          sorted_on_time = sorted(lbl, key = lambda x: x[1])
          clusters = []
          previous = None

          for block in sorted_on_time: #cluster the events that are within maxsep time apart
            if (previous and block[1] - previous[1] < maxsep):
              if (not any(filter(lambda x: x[0].start_time.date() == block[0].start_time.date(), clusters[-1]))): #can't have the same event twice in the same day.  This would mean you were at a, left a, and returned to a within the event span, which we shouldn't count twice
                clusters[-1].append(block)
            else:
              clusters.append([block])
            previous = block
        
          event_times = []
          for cluster in clusters: #every cluster with at least 5 entries is an event.  We will set the time for that event to be the average of the times 
            if (len(cluster) > sorter.MINIMUM_OCCURANCES and sorter.occurance_rate(cluster, min([x[0].start_time for x in cluster]), endTime) > sorter.MINIMUM_EVENT_ATTENDANCE):
              begin_average = sum([x[1] for x in cluster]) / float(len(cluster))
              end_average = sum([x[2] for x in cluster]) / float(len(cluster))
              event_times.append((begin_average,end_average))
              for elm in cluster: #remove these entries from the possibilities so that they don't also show up in higher cycles
                location_block_list.remove(elm[0])
   
          if event_times:
            print sorter.__name__
            print loc.address
            print ["[" + str(sorter.time(x[0])) + "," + str(sorter.time(x[1])) + "]" for x in event_times]
            event = {"user_id":user_id,"location_id":loc.location_id,"address":loc.address,"cycle_type":sorter.NAME,"occurances":event_times}
            cycle_event_list.append(event)
    #Now that we found all of the events, we need to compare them to what is already in the database and delete any cycles that are no longer going, update ones that have new occurance, etc.
    cyclical_events = Utils.query("""SELECT * FROM Cyclical_Events WHERE user_id = %s""",(user_id))
    for cycle in cyclical_events:
      matches = [x for x in cycle_event_list if x["location_id"] == cycle["location_id"] and x["cycle_type"] == cycle["cycle_type"]]
      if matches:
        #there could only be one match
        match = matches[0]
        if not cycle["locked"]:
          Utils.execute("""UPDATE Cyclical_Events SET occurances = %s WHERE event_id = %s""", (json.JSONEncoder().encode(match["occurances"]),cycle["event_id"]))
        cycle_event_list.remove(match)
      else:
        if not cycle["locked"]:
          Utils.execute("""UPDATE Cyclical_Events SET occurances = %s WHERE event_id = %s""", (json.JSONEncoder().encode([]),cycle["event_id"]))
    
    #now go through the remaining "new" events and add them to the events
    for remaining_event in cycle_event_list:
      Utils.execute("INSERT INTO Cyclical_Events(user_id, location_id, name, cycle_type, occurances) VALUE(%s,%s,%s,%s,%s)",
            (remaining_event["user_id"],remaining_event["location_id"],remaining_event["address"],remaining_event["cycle_type"],json.JSONEncoder().encode(remaining_event["occurances"])))

    return location_block_list

  def generateSpanningEvents(self, user_id, location_block_list, start_time = datetime(1900,1,1), end_time = datetime(MAXYEAR,12,31)):
    parts = partition(location_blocks, "location_id")
    for loc_id in parts:
      block_list = parts[loc_id]
      min_time_between = timedelta.max
      max_time_between = timedelta.min
      min_length = timedelta.max
      max_length = timedelta.min
      for i in range(len(block_list)-1):
        length = block_list[i].end_time - block_list[i].start_time
        time_between = block_list[i+1].start_time - block_list[i].end_time
        if time_between < min_time_between:
          min_time_between = time_between
        if time_between > max_time_between:
          max_time_between = time_between
        if length < min_length:
          min_length = length
        if length > max_length:
          max_length = length
      time_between_range = max_time_between-min_time_between
      avg_length = (min_length + max_length)/2
      storeSpanningEvent(user_id, loc_id, block_list[0].address, min_time_between, time_between_range, avg_length)

  def storeSpanningEvent(user_id, loc_id, address, min_time_between, time_between_range, avg_length):
    old_event_at_location = Utils.query("""SELECT * FROM Events WHERE user_id = %s AND location_id = %s""", (user_id, loc_id))
    if old_event_at_location == ():
      new_entry_id = Utils.execute_id("""INSERT INTO Events (event_type, user_id, location_id, name, locked, deleted) VALUE (%s,%s,%s,%s,%s,%s)""",
                        ('spanning',user_id,loc_id,address,0,0))
      Utils.execute("""INSERT INTO Spanning_Events (event_id,min_time_between,time_between_range,avg_length) VALUE (%s,%s,%s,%s)""",
            (new_entry_id, min_time_between,time_between_range,avg_length))
    elif old_event_at_location[5] != 1: # If the event is not locked
      Utils.execute("""UPDATE Spanning_Events SET min_time_between = %s, time_between_range = %s, avg_length = %s WHERE event_id = %s""",
            (min_time_between, time_between_range, avg_length, old_event_at_location[0]))
