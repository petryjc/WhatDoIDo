from datetime import datetime, timedelta, date, time, MINYEAR, MAXYEAR

class Day:
  MINIMUM_EVENT_ATTENDANCE = 0.8
  MINIMUM_OCCURANCES = 4
  NAME = "daily"
  @staticmethod
  def seconds(t):
    return (t - datetime.combine(t,time(0))).total_seconds()

  @staticmethod
  def time(seconds):
    return str(int(seconds/3600)) + ":" + str(int(seconds%3600/60))

  @staticmethod
  def occurance_rate(cluster, startDate, endDate):
    daygenerator = (startDate + timedelta(x) for x in xrange((endDate - startDate).days))
    return float(len(cluster)) / sum(1 for day in daygenerator)

class Week:
  MINIMUM_EVENT_ATTENDANCE = 0.8
  MINIMUM_OCCURANCES = 2
  NAME = "weekly"
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
  NAME = "monthly"
  @staticmethod
  def seconds(t):
    return t.day*86400 + (t - datetime.combine(t,time(0))).total_seconds()

  @staticmethod
  def time(seconds):
    return str(int(seconds/86400)) + " " + str(int(seconds%86400/3600)) + ":" + str(int(seconds%86400%3600/60))

  @staticmethod
  def occurance_rate(cluster, startDate, endDate):
    daygenerator = (startDate + timedelta(x) for x in xrange((endDate - startDate).days))
    return float(len(cluster)) / sum(1 for day in daygenerator if day.day == startDate.day)


