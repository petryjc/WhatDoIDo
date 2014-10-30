from utils import Utils
import cherrypy
import json
from datetime import datetime

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
