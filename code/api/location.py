from utils import Utils
import json
import cherrypy
import requests
from datetime import datetime
from math import *

class Location(object):
	def index(self):
		return "Location"



	def haversine(self, lat1, lon1, lat2, lon2):
		R = 3958.8 # Earth radius in miles

		dLat = radians(lat2 - lat1)
		dLon = radians(lon2 - lon1)
		lat1 = radians(lat1)
		lat2 = radians(lat2)

		a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
		c = 2*asin(sqrt(a))

		return R * c

	def checkDistance(self, lat1, lon1, lat2, lon2):
		dist = self.haversine(lat1, lon1, lat2, lon2)
		MAX_DISTANCE = 2.5 # 2.5 miles is how far one travels in 5 minutes at 30 mph
		if dist > MAX_DISTANCE:
			return 1
		return 0 	


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
					previousUserLocation = Utils.query("""SELECT location_id FROM Users_Locations 
													WHERE user_id = %s 
													ORDER BY time DESC LIMIT 1""", (user_id))
					previousLocation = Utils.query("""SELECT * FROM Locations WHERE location_id = %s""", (previousUserLocation[0]["location_id"]))
					
					is_route = False
					if len(previousLocation) == 1 and self.checkDistance(previousLocation[0]["latitude"], previousLocation[0]["longitude"],body["latitude"],body["longitude"]) == 1: 
						is_route = True
					Utils.execute("""INSERT INTO Users_Locations(user_id, location_id, time, is_route) 
							VALUES(%s, %s, %s, %s)""",
							(user_id, location_id, datetime.now(), is_route))
					return json.JSONEncoder().encode( Utils.status_more( 0, "OK" ) )
			return json.JSONEncoder().encode( Utils.status_more( 35, "Could not save to database" ) )

		return json.JSONEncoder().encode( Utils.status_more( 33, "Could not retrieve location information" ) )




