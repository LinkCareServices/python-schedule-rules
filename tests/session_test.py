#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2011 Link Care Services
#
"""
Test for Session class
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
from schedule import Session

class TestSession(unittest.TestCase):
  def setUp(self):
    self.ses_p = Session("Test", duration=60*8,start_hour=13, start_minute=30)
    self.ses_p.add_rule("1er jour des 6", 
                 freq=rrule.DAILY,
                 dtstart=datetime.date(2011,8,20), 
                 interval=6 
                )
    self.ses_p.add_rule("2eme jour des 6", 
                 freq=rrule.DAILY,
                 dtstart=datetime.date(2011,8,20)+relativedelta(days=+1), 
                 interval=6 
                )
    self.ses_p.add_rule("3eme jour des 6", 
                 freq=rrule.DAILY,
                 dtstart=datetime.date(2011,8,20)+relativedelta(days=+2), 
                 interval=6 
                ) 
      
class TestSessionSimpleRule1(TestSession):
  def setUp(self):
    TestSession.setUp(self)
    
  def runTest(self):
    ses = Session("Test", 60*7)
    ses.add_rule("1er jour des 6", 
                 freq=rrule.DAILY,
                 dtstart=datetime.date(2011,8,20), 
                 interval=6 
                )
    result_expected = 256620
    result = ses.total_duration
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

class TestSessionSimpleRule2(TestSession):
  def setUp(self):
    TestSession.setUp(self)
    
  def runTest(self):
    ses = Session("Test", 60*9)
    ses.add_rule("2eme jour des 3", 
                 freq=rrule.DAILY,
                 dtstart=datetime.date(2011,8,20)+relativedelta(days=+1), 
                 interval=3 
                )
    result_expected = 659340
    result = ses.total_duration
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

class TestSessionAddRule1(TestSession):
  def setUp(self):
    TestSession.setUp(self)
    
  def runTest(self):
    ses = Session("Test", 60*8)
    ses.add_rule("1er jour des 6", 
                 freq=rrule.DAILY,
                 dtstart=datetime.date(2011,8,20), 
                 interval=6 
                )
    ses.add_rule("2eme jour des 3", 
                 freq=rrule.DAILY,
                 dtstart=datetime.date(2011,8,20)+relativedelta(days=+1), 
                 interval=3 
                )
    result_expected = 879360
    result = ses.total_duration
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

class TestSessionAddRule2(TestSession):
  def setUp(self):
    TestSession.setUp(self)
    
  def runTest(self):
    ses = Session("Test", 60*8)
    ses.add_rule("1er jour des 6", 
                 freq=rrule.DAILY,
                 dtstart=datetime.date(2011,8,20), 
                 interval=6 
                )
    ses.add_rule("2eme jour des 6", 
                 freq=rrule.DAILY,
                 dtstart=datetime.date(2011,8,20)+relativedelta(days=+1), 
                 interval=6 
                )
    ses.add_rule("3eme jour des 6", 
                 freq=rrule.DAILY,
                 dtstart=datetime.date(2011,8,20)+relativedelta(days=+2), 
                 interval=6 
                )            
    result_expected = 879840
    result = ses.total_duration
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

class TestSessionInPeriod(TestSession):
  def setUp(self):
    TestSession.setUp(self)
    
  def test_1(self):
    result_expected = True
    result = self.ses_p.in_period(datetime.datetime(2011,9,27,15,40))
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

  def test_2(self):
    result_expected = (datetime.datetime(2011,9,27,13,30), datetime.datetime(2011,9,27,21,30))
    result = self.ses_p.in_period(datetime.datetime(2011,9,27,15,40), True)
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

  def test_3(self):
    result_expected = False
    result = self.ses_p.in_period(datetime.datetime(2011,9,28,15,40))
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

  def test_4(self):
    result_expected = ()
    result = self.ses_p.in_period(datetime.datetime(2011,9,28,15,40), True)
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)


class TestSessionNextPeriod1(TestSession):
  def setUp(self):
    TestSession.setUp(self)
    
  def test_1(self):
    result_expected = (datetime.datetime(2011,9,27,13,30), datetime.datetime(2011,9,27,21,30))
    result = self.ses_p.next_period(datetime.datetime(2011,9,27,15,40))
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

  def test_2(self):
    result_expected = (datetime.datetime(2011,10,1,13,30), datetime.datetime(2011,10,1,21,30))
    result = self.ses_p.next_period(datetime.datetime(2011,9,27,15,40), False)
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

  def test_3(self):
    result_expected = (datetime.datetime(2011,10,1,13,30), datetime.datetime(2011,10,1,21,30))
    result = self.ses_p.next_period(datetime.datetime(2011,9,28,15,40))
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)
    
class TestSessionPrevPeriod1(TestSession):
  def setUp(self):
    TestSession.setUp(self)
    
  def test_1(self):
    result_expected = (datetime.datetime(2011,9,27,13,30), datetime.datetime(2011,9,27,21,30))
    result = self.ses_p.prev_period(datetime.datetime(2011,9,27,15,40))
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

  def test_2(self):
    result_expected = (datetime.datetime(2011,9,26,13,30), datetime.datetime(2011,9,26,21,30))
    result = self.ses_p.prev_period(datetime.datetime(2011,9,27,15,40), False)
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

  def test_3(self):
    result_expected = (datetime.datetime(2011,9,27,13,30), datetime.datetime(2011,9,27,21,30))
    result = self.ses_p.prev_period(datetime.datetime(2011,9,28,15,40))
    assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)
     
if __name__ == "__main__":
  import sys
  suite = unittest.findTestCases(sys.modules[__name__])  
  #suite = unittest.TestLoader().loadTestsFromTestCase(Test)
  unittest.TextTestRunner(verbosity=2).run(suite)