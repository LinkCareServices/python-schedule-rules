#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2011 Link Care Services
#
"""
Test for SRules class
"""

__authors__ = [
  # alphabetical order by last name
  'Thomas Chiroux',
]

import unittest
import datetime

# dependancies imports
from dateutil.relativedelta import relativedelta
from dateutil import rrule

# import here the module / classes to be tested
from schedule import Session, SRules

class TestSRules(unittest.TestCase):
  def setUp(self):
    self.ses1 = Session("Test1", duration=60*8,start_hour=13, start_minute=30)
    self.ses2 = Session("Test2", duration=60*3,start_hour=12, start_minute=00)
    self.ses3 = Session("Test3", duration=60*3,start_hour=15, start_minute=00)
    self.ses4 = Session("Test4", duration=60*3,start_hour=20, start_minute=00)
    self.ses5 = Session("Test5", duration=60*3,start_hour=23, start_minute=00)
    self.ses1.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,20), interval = 2)
    self.ses2.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,20), interval = 2)
    self.ses3.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,20), interval = 2)
    self.ses4.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,20), interval = 2)
    self.ses5.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,20), interval = 2)
      
class TestIntersection1(TestSRules):
  def setUp(self):
    TestSRules.setUp(self)
    self.srule = SRules("Test")
    self.srule.add_session(self.ses1)
    self.srule.add_session(self.ses2)
  def test_1(self):
    pass
    
if __name__ == "__main__":
  import sys
  suite = unittest.findTestCases(sys.modules[__name__])  
  #suite = unittest.TestLoader().loadTestsFromTestCase(Test)
  unittest.TextTestRunner(verbosity=2).run(suite)