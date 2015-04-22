from urllib2 import *
import re
from datetime import *
from bs4 import BeautifulSoup
import unicodedata
from utils import Utils
import urllib

class Movie(object):
  @staticmethod
  def get_movies(user_id):
    last_location = Utils.query("SELECT * FROM Users_Locations ul JOIN Locations l ON ul.location_id = l.location_id WHERE user_id = %s ORDER BY time DESC LIMIT 1",(user_id))
    if not last_location:
      return None

    print("http://www.google.com/movies?near=" + urllib.quote_plus(last_location[0]["address"]))
    response = urlopen("http://www.google.com/movies?near=" + urllib.quote_plus(last_location[0]["address"]))
    html = response.read()
    soup = BeautifulSoup(html)
    theaters = soup.find_all("div", {"class": "theater"})
    theater_movie = [(i,len(i.find_all("div",{"class":"movie"}))) for i in theaters]
    
    theater = max(theater_movie,key = lambda x: x[1])[0] #use the theater that has the most movies playing.  It seems like a good idea at least

    s = theater.find("div",{"class":"info"}).get_text()
    m = re.search("(.*) - \(\d\d\d\) \d\d\d-\d\d\d\d",s)
    address = m.group(1)
    now = datetime.now()
    begin = (now + timedelta(minutes=30)).time()
    end = (now + timedelta(hours=2)).time()

    movies = theater.find_all("div",{"class":"movie"})
    movie_results = []
    for movie in movies:
      name = movie.find("div",{"class":"name"}).get_text()
      times = movie.find("div",{"class":"times"}).get_text()
      times = unicodedata.normalize('NFKD', times).encode('ascii','ignore')
      am = []
      pm = []
      if "am" in times:
        times = times.split("am")
        am = times[0].strip().split("  ")
        pm = times[1].strip().replace("pm","").split("  ")
      else:
        pm = times.replace("pm","").split("  ")
      am = [datetime.strptime(a + " AM","%I:%M %p").time() for a in am]
      pm = [datetime.strptime(a + " PM","%I:%M %p").time() for a in pm]
      times = am + pm
      soon_times = [i for i in times if i > begin and i < end]
      if soon_times:
        m = {"name":name,"near_times":[i.isoformat() for i in soon_times]} 
        movie_results.append(m)

    if movie_results:
      results = {"location":address,"movies":movie_results}
    else:
      results = None
    return results
