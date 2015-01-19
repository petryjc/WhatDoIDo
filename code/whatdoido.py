import cherrypy
import json
import os
import cherrypy.process.plugins
from utils import Utils
from api import *

class Root(object):
    @cherrypy.expose
    def index(self):
        return "Placeholder for web team"

root = Root()

root.api = core.API()
root.api.location = location.Location()
root.api.suggestion = suggestions.Suggestion()
root.api.event = events.Event()
cherrypy.quickstart(root)
