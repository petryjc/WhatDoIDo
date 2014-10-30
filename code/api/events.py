from utils import Utils
import cherrypy
import json
from datetime import datetime
from datetime import timedelta

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
    travel_history = Utils.query("""SELECT * FROM Locations l JOIN Users_Locations ul ON l.location_id = ul.location_id WHERE ul.user_id = %s ORDER BY ul.time""", (user_id))
    location_blocks = [LocationBlock(list(travel_history).pop(0))]
    for d in travel_history:
      if (d["location_id"] == location_blocks[-1].location_id):
        location_blocks[-1].end_time = d["time"]
      else:
        location_blocks.append(LocationBlock(d))

    print ", ".join(str(x.start_time) for x in location_blocks)
    #print "\n".join[str(x.location_id) for x in location_blocks]
    parts = partition(location_blocks, "location_id")
    print parts.keys()
    
    maxsep = timedelta(minutes = 10) 
    for location_block_list in parts.values():
      if (len(location_block_list) >= 3): #it takes at least 3 occurences to show signs of a cycle
        sorted_on_time = sorted(location_block_list,key=lambda x: x.start_time.time())
        clusters = []
        previous = None

        for block in sorted_on_time: #cluster the events that are within maxsep time apart
          if (previous and previous.start_time.time() - block.start_time.time() < maxsep):
            clusters[-1].append(block)
          else:
            clusters.append([block])
          previous = block
         
         
      
