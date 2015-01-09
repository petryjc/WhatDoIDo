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
  def list(self):
    #TODO
    return "List (TODO)"

  def generateCyclicalEvents(self, user_id, start_time = datetime(1900,1,1), end_time = datetime(MAXYEAR,12,31)):
    #Utils.execute("DELETE FROM Cyclical_Events WHERE user_id = %s", (user_id)) #remove previous eyclical events
    travel_history = Utils.query("""SELECT * FROM Locations l JOIN Users_Locations ul ON l.location_id = ul.location_id WHERE ul.user_id = %s AND time BETWEEN %s AND %s ORDER BY ul.time""", (user_id, start_time, end_time))
    
    if(len(travel_history) < 2):
      return "Requires at least 2 data points"
    endTime = travel_history[-1]["time"]

    location_blocks = [LocationBlock(list(travel_history).pop(0))]
    for d in travel_history:
      if (d["location_id"] == location_blocks[-1].location_id):
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
        if (len(location_block_list) >= 3): #it takes at least 3 occurences to show signs of a cycle
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

  def generateSpanningEvents(self, user_id, location_block_list, start_time = datetime(1900,1,1), end_time = datetime(MAXYEAR,12,31)):):
    for loc in location_block_list:
        location_history = Utils.query("""SELECT * FROM Locations l JOIN Users_Locations ul ON l.location_id = ul.location_id WHERE ul.user_id = %s AND l.location_id = %s AND time BETWEEN %s AND %s ORDER BY ul.time""", (user_id, loc.location_id, start_time, end_time))
        min_time_between = ()
        max_time_between = None
        for i in range(len(location_history)-1):
          time_between = location_history(i+1).start_time - location_history(i).end_time
          if time_between < min_time_between:
            min_time_between = time_between
          if time_between > max_time_between:
            max_time_between = time_between
        range_median_time = (max_time_between + min_time_between)/2
        print range_median_time;




