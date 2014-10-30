import unittest
import sys
import platform
import json
sys.path.insert(0, '../code')
from utils import Utils
from api.events import Event

class Test(unittest.TestCase):
  def test_create_cyclical_event(self):
    print Event().generateCyclicalEvents(1)  

if __name__ == '__main__':
  unittest.main()
