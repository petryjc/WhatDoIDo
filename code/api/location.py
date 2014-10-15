from utils import Utils
import json
import cherrypy
import requests
from datetime import datetime

class Location(object):
	def index(self):
		return "Location"

	@cherrypy.expose
	def add(self):
		body = json.loads( cherrypy.request.body.read() )
    
		check = Utils.arg_check(body, ['token', 'latitude', 'longitude'])	
		if (check[0]):
			return check[1]
		
		user_check = Utils.validate_user(body["token"])
		if(user_check[0]):
			return user_check[1]
		user_id = user_check[1]
		
		base = "http://maps.googleapis.com/maps/api/geocode/json?"
		params = "latlng={lat},{lon}&sensor={sen}".format(
			lat=body['latitude'],
			lon=body['longitude'],
			sen=True
		)
		url = "{base}{params}".format(base=base, params=params)
		response = requests.get(url)
		
		if (response):
			content = response.json()
			if (content and content['results'] and content['results'][0] and content['results'][0]['formatted_address']):
				savedLocations = Utils.query("""SELECT * FROM Locations WHERE address = %s""",
							    (content['results'][0]['formatted_address']))
				#print savedLocations
				if (len(savedLocations) == 1):
					location_id = savedLocations[0]["location_id"]
				elif (len(savedLocations) > 1):
					return json.JSONEncoder().encode( Utils.status_more( 34, "Inconsistet database" ) )
				else:
					location_id  = Utils.execute_id("""INSERT INTO Locations(latitude, longitude, address, place) 
							 VALUES(%s, %s, %s, %s)""", 
							(body["latitude"], body["longitude"], content['results'][0]['formatted_address'], "I don't know"))
				if (location_id  != -1):
					Utils.execute("""INSERT INTO Users_Locations(user_id, location_id, time) 
							VALUES(%s, %s, %s)""",
							(user_id, location_id, datetime.now()))
					return json.JSONEncoder().encode( Utils.status_more( 0, "OK" ) )
			return json.JSONEncoder().encode( Utils.status_more( 35, "Could not save to database" ) )

		return json.JSONEncoder().encode( Utils.status_more( 33, "Could not retrieve location information" ) )
