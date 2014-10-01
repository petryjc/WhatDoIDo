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

cherrypy.quickstart(root)
