from utils import Utils
import cherrypy
import json
from datetime import datetime, timedelta, date, time

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

  def generateCyclicalEvents(self, user_id):
    Utils.execute("DELETE FROM Cyclical_Events WHERE user_id = %s", (user_id)) #remove previous eyclical events
    travel_history = Utils.query("""SELECT * FROM Locations l JOIN Users_Locations ul ON l.location_id = ul.location_id WHERE ul.user_id = %s ORDER BY ul.time""", (user_id))
    
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
    for location_block_list in parts.values():
      if (len(location_block_list) >= 3): #it takes at least 3 occurences to show signs of a cycle
        sorter = Week
        loc = location_block_list[0]
        lbl = [(x, sorter.seconds(x.start_time)) for x in location_block_list]
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
          #print 
          if (len(clusters) > sorter.MINIMUM_OCCURANCES and sorter.occurance_rate(cluster, min([x[0].start_time for x in cluster]), endTime) > sorter.MINIMUM_EVENT_ATTENDANCE):
            event_times.append(sum([x[1] for x in cluster]) / float(len(cluster)))
   
        print loc.address
        print [sorter.time(x) for x in event_times]
        Utils.execute("INSERT INTO Cyclical_Events(user_id, location_id, name, cycle_type, occurances) VALUE(%s,%s,%s,%s,%s)", 
        (user_id,loc.location_id,loc.address,"weekly",json.JSONEncoder().encode(event_times)))

class Day:
  MINIMUM_EVENT_ATTENDANCE = 0.8
  MINIMUM_OCCURANCES = 4
  @staticmethod
  def seconds(t):
    return (t - datetime.combine(t,time(0))).total_seconds()/60
  
  @staticmethod
  def time(seconds):
    return str(int(seconds%3600)) + ":" + str(int(seconds%3600/60))
  
  @staticmethod
  def occurance_rate(cluster, startDate, endDate):
    daygenerator = (startDate + timedelta(x) for x in xrange((endDate - startDate).days))
    return float(len(cluster)) / sum(1 for day in daygenerator)

class Week:
  MINIMUM_EVENT_ATTENDANCE = 0.8
  MINIMUM_OCCURANCES = 2
  @staticmethod
  def seconds(t):
    return t.weekday()*86400 + (t - datetime.combine(t,time(0))).total_seconds()

  @staticmethod
  def time(seconds):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[int(seconds/86400)] + " " + str(int(seconds%86400/3600)) + ":" + str(int(seconds%86400%3600/60))
         
  @staticmethod
  def occurance_rate(cluster, startDate, endDate):
    daygenerator = (startDate + timedelta(x) for x in xrange((endDate - startDate).days))
    return float(len(cluster)) / sum(1 for day in daygenerator if day.weekday() == startDate.weekday())

class Month:
  MINIMUM_EVENT_ATTENDANCE = 0.8
  MINIMUM_OCCURANCES = 2
  @staticmethod
  def seconds(t):
    return t.day*86400 + (t - datetime.combine(t,time(0))).total_seconds()

  @staticmethod
  def time(seconds):
    return int(seconds/86400) + " " + str(int(seconds%86400/3600)) + ":" + str(int(seconds%86400%3600/60))

  @staticmethod
  def occurance_rate(cluster, startDate, endDate):
    daygenerator = (startDate + timedelta(x) for x in xrange((endDate - startDate).days))
    return float(len(cluster)) / sum(1 for day in daygenerator if day.day == startDate.day)



