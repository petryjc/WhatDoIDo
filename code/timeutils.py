from datetime import datetime, timedelta, date, time, MINYEAR, MAXYEAR
import re

class Day:
  MINIMUM_EVENT_ATTENDANCE = 0.8
  MINIMUM_OCCURANCES = 4
  NAME = "daily"
  @staticmethod
  def seconds(t):
    return (t - datetime.combine(t,time(0))).total_seconds()

  @staticmethod
  def time(seconds):
    return "{0}:{1:02d}".format(int(seconds/3600), int(seconds%3600/60))
    
  @staticmethod
  def time_to_seconds(time):
    m = re.match(r'(\d*):(\d*)',time)
    hours = int(m.group(1))
    minutes = int(m.group(2))
    return hours * 3600 + minutes * 60
  
  @staticmethod
  def occurance_rate(cluster, startDate, endDate):
    daygenerator = (startDate + timedelta(x) for x in xrange((endDate - startDate).days))
    return float(len(cluster)) / sum(1 for day in daygenerator)

class Week:
  MINIMUM_EVENT_ATTENDANCE = 0.8
  MINIMUM_OCCURANCES = 2
  NAME = "weekly"
  days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  
  @staticmethod
  def seconds(t):
    return t.weekday()*86400 + (t - datetime.combine(t,time(0))).total_seconds()

  @staticmethod
  def time(seconds):
    return "{0} {1}:{2:02d}".format(Week.days[int(seconds/86400)],int(seconds%86400/3600),int(seconds%86400%3600/60))

  @staticmethod
  def time_to_seconds(time):
    m = re.match(r'(.*) (\d*):(\d*)',time)
    day = m.group(1)
    hours = int(m.group(2))
    minutes = int(m.group(3))
    return Week.days.index(day)*86400 + hours*3600 + minutes*60
    
  @staticmethod
  def occurance_rate(cluster, startDate, endDate):
    daygenerator = (startDate + timedelta(x) for x in xrange((endDate - startDate).days))
    return float(len(cluster)) / sum(1 for day in daygenerator if day.weekday() == startDate.weekday())

class Month:
  MINIMUM_EVENT_ATTENDANCE = 0.8
  MINIMUM_OCCURANCES = 2
  NAME = "monthly"
  @staticmethod
  def seconds(t):
    return t.day*86400 + (t - datetime.combine(t,time(0))).total_seconds()

  @staticmethod
  def time(seconds):
    return "{0} {1}:{2:02d}".format(int(seconds/86400), int(seconds%86400/3600),int(seconds%86400%3600/60))

  @staticmethod
  def time_to_seconds(time):
    m = re.match(r'(\d*) (\d*):(\d*)',time)
    days = int(m.group(1))
    hours = int(m.group(2))
    minutes = int(m.group(3))
    return days*86400 + hours*3600 + minutes*60
  
  @staticmethod
  def occurance_rate(cluster, startDate, endDate):
    daygenerator = (startDate + timedelta(x) for x in xrange((endDate - startDate).days))
    return float(len(cluster)) / sum(1 for day in daygenerator if day.day == startDate.day)


