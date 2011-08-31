#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2011 Link Care Services
#
"""TEST rrules dateutil

"""

__authors__ = [
  # alphabetical order by last name
  'Thomas Chiroux',
]

from dateutil.relativedelta import relativedelta
from dateutil import rrule
import datetime

def find(_list, _search):
  """find item in a list an returns the item position and the position itsef
  """
  return next(((i, x) for i, x in enumerate(_list) if x == _search), (None, None))

class Interval(object):
  """Represent an interval (espacialy date interval)
  """
  start = None
  end = None
  
  def __init__(self, start, end):
    if start > end:
      raise ValueError('Start (%s) must not be greater than end (%s)' % (start, end))
    self.start = start
    self.end = end

  def __repr__(self):
    """Representation of object"""
    return "%s --> %s" % (self.start, self.end)

  def eq(self, other):
    """equality operator
    """
    if self.start == other.start and self.end == other.end:
      return True
    else:
      return False
      
  def __contains__(self, other):
    """test if other is contained inside self
    return True if yes or False
    """
    if type(other) == Interval:
      if (self.start <= other.start <= other.end <= self.end):
        return True
      else:
        return False
    elif type(other) == datetime.datetime:
      if (self.start <= other <= other <= self.end):
        return True
      else:
        return False

  def __and__(self, other):
    """returns the interval in intersection between the two input intervals
    or None
    """
    if (self.start <= other.start <= other.end <= self.end):
        return Interval(other.start,other.end)
    elif (self.start <= other.start <= self.end):
        return Interval(other.start,self.end)
    elif (self.start <= other.end <= self.end):
        return Interval(self.start,other.end)
    elif (other.start <= self.start <= self.end <= other.end):
        return Interval(self.start,self.end)
    else:
        return None
  
  def __add__(self, other):
    """if intersection, returns a new interval based on max extremities
    if no intersection : ?? (returns 2 intervals or None ??)
    """
    if self & other:
      return Interval(min(self.start, other.start), 
                      max(self.end, other.end))
    else:
      return (self, other)

class SRules(object):
  """SRule = Schedule Rules object
  
  It store an ordered list of sessions which will be processed in that order
  to generate an occurence list.
  It handle 'add' and 'exclude' sessions.
  
  each session is a set of rules 'normal rules' which indicates periods of
  time that the person should be working. This rules can include 'exclude' rules
  if they are indended to decribe the 'normal' session.
  
  Ex. (person at work)
  session1 (add) = all the week days from 08:00 to 18:00 : aka all the normal working days
  session2 (exclude) = All the days between 1st April and 13th April : holidays
  session3 (add) = sunday 10/07/2011 from 14:00 to 17:00 : an extra day
  ...
  
  """
  name = ""
  sessions = []
  occurences = []
  auto_refresh = True
  total_duration = 0

  def __init__(self, name, auto_refresh=True):
    """SRules constructor
    """
    self.name = name
    self.auto_refresh = auto_refresh

  def __iter__(self):
    """iterable"""
    return self._forward()

  def _forward(self):
    """forward generator"""
    current_item = 0
    while (current_item < len(self.occurences)):
      interval = self.occurences[current_item]
      current_item += 1
      yield interval

  def _in_occurence(self, occurence, _date):
    pass

  def _recalculate_occurences(self):
    """Recalculate all the occurences (static list) in the object
    """
    # after adding a rule, we need to recompute the period list
    new_occurences = []
    new_total_duration = 0
    for session in self.sessions:
      new_occurences2 = []
      if session.session_type == 'add':
        if len(new_occurences) == 0: 
          # first session, add all the occurences
           new_occurences2 = session.get_occurences()
        else:
          for new_occ in new_occurences:
            # on prend chaque occurence de la nouvelle session et on la
            # matche avec chaque occurence des sessions actuelles
            # les occurences sont sensées être ordonnées, donc si la fin de
            # l'occurence actuelle précéde le début des occurences testées, on
            # peut stopper et l'insérer là.
            for occ in session.occurences:
              if occ[0] < new_occ[0]: 
                # la nouvelle commence avant, 2 possibilités :
                #    - elles se recouvrent et il faut merger
                #    - elles ne se recouvrent pas et il faut ajouter
                if occ[1] < new_occ[0]:
                  # ne se recouvrent pas : on ajoute
                  new_occurences2.append(occ)
                  
            
      elif session.session_type == 'exclude':
        if len(new_occurences) == 0:
          # Error, we can not exclude and empty list, skip
          print "an 'exclude' session can not be in first position: skip"
        else:
          pass
      new_occurences = new_occurences2
      
    self.occurences = new_occurences
    self.total_duration = new_total_duration
    #return new_occurences
        
  def add_session(self, session):
    """add new session for this person
    
    description -- sting -- description of the session
    session -- Session object
    
    the session object must be already instanciated
    """
    self.sessions.append(session)
    # here, see if we recalculate all the time of if we recalculate only on 
    # demand
    if self.auto_refresh:
      self._recalculate_occurences()
      
  def remove_session(self, name_or_pos):
    """Remove of session in the list
    you can provide an integer for the position
    or a session name
    """
    if type(name_or_pos) == int:
      self.sessions.pop(name_or_pos)
    elif type(name_or_pos) == str:
      pos, session = find(self.sessions, name_or_pos)
      if pos is not None:
        self.sessions.pop(pos)
    if self.auto_refresh:
      self._recalculate_occurences()

  def move_session(self, old_position, new_position):
    """Move a session in the list
    Used to change the order, and perhaps behaviour of the SRules
    """
    self.sessions.insert(new_position, self.sessions.pop(old_position))
    
    if self.auto_refresh:
      self._recalculate_occurences()
    
  def in_period(self, the_date=datetime.datetime.now(), return_period=False):
    pass
    
  def next_period(self, the_date=datetime.datetime.now(), inclusive=True):
    pass
    
  def prev_period(self, the_date=datetime.datetime.now(), inclusive=True):
    pass
    
class Session(object):
  """
  This objects is a representation of a standard 'session'
  It has a calendar (dateutil) rruleset with one or many rrules inside
  Each Session has a standard 'duration' and a start hour and minute,
  wich will be used to calculate the start and end datetime of each occurence
  """

  def __init__(self, session_name, duration=60, start_hour=0, start_minute=0,
                     session_type='add', session_description=None):
    """Constructor object
    
    duration - in minutes
    start_hour and start_minute: if provided and if rrules params dates are
        date and not datetime, will use this values to change date into datetime
    """
    self.session_name = session_name
    self.session_type = session_type
    self.session_description = session_description
    
    self.duration = duration
    self.start_hour = start_hour
    self.start_minute = start_minute
    self.set = rrule.rruleset()
    
    # calculated occurence list:
    self.occurences = []
    self.total_duration = 0
    
    # "backup" of rules, in order to be able to reprocess them
    self.rules = []

  def __iter__(self):
    """iterable"""
    return self._forward()

  def _forward(self):
    """forward generator"""
    current_item = 0
    while (current_item < len(self.occurences)):
      interval = self.occurences[current_item]
      current_item += 1
      yield interval
    	
  def __cmp__(self, other):
    """returns a comparaison between self and anoter object
    can compare two objects of same type and also compare object
    to a string
      cmp is used to test equality, but can also be used to compare and order a list,
      so we need a method to compare (lt and gt) two sessions : which one is greater to the other ??

    TODO:
     if other is string we should only compare 'name'
     if other is object OR if other is rruleset or rrule, 
        we should compare occurences 
        (at least for equality : diffult to say which is greater 
         than the other : the number of hours ? the date-start and date-end ?)
    """
    if isinstance(other, Session):
      # here have two objects to compare we need to compare the occurences..
      # so we compare the total duration of all occurences
      return cmp(self.total_duration, other.total_duration)
    elif isinstance(other, str):
      return cmp(self.session_name, other)
    else:
      return False
 
  def __str__(self):
    """returns a string describing the Session
    """
    return self.session_name
 
  def __contains__(self, other, return_interval=False):
    """test if other is contained inside self
    return True if yes or False
    """
    if type(other) == Interval:
      for occ in self.occurences:
        if (occ.start <= other.start <= other.end <= occ.end):
          if return_interval:
            return occ
          else:
            return True
    elif type(other) == datetime.datetime:
      for occ in self.occurences:
        if (occ.start <= other <= other <= occ.end):
          if return_interval:
            return occ
          else:
            return True
    
    if return_interval:
      return None
    else:
      return False

  def add_rule(self, label="", **rrule_params):
    """add a recuring rule for this set
    """
    rrule_params.setdefault('freq', rrule.DAILY)
    rrule_params.setdefault('cache', True)
    
    if 'count' not in rrule_params and 'until' not in rrule_params:
      rrule_params.setdefault('until', datetime.datetime.now()+relativedelta(years=+10))
    
    if 'dtstart' in rrule_params:
      if isinstance(rrule_params['dtstart'], datetime.date):
        rrule_params['dtstart']+=relativedelta(hours=self.start_hour, 
                                               minutes=self.start_minute)
    if 'until' in rrule_params:
      if isinstance(rrule_params['until'], datetime.date):
         rrule_params['until']+=relativedelta(hours=self.start_hour, 
                                                minutes=self.start_minute)
    self.set.rrule(rrule.rrule(**rrule_params))
    self._recalculate_occurences()
    self.rules.append({ 'type':'add', 'label':label, 'rule':rrule_params})
    
  def exclude_rule(self, label="", **rrule_params):
    """exclure a recuring to the set
    the rule can be set to be only one day
    """
    rrule_params.setdefault('freq', rrule.DAILY)
    rrule_params.setdefault('cache', True)
    
    if 'count' not in rrule_params and 'until' not in rrule_params:
      rrule_params.setdefault('until', datetime.datetime.now()+relativedelta(years=+10))

    if 'dtstart' in rrule_params:
      if isinstance(rrule_params['dtstart'], datetime.date):
        rrule_params['dtstart']+=relativedelta(hours=self.start_hour, 
                                               minutes=self.start_minute)
    if 'until' in rrule_params:
      if isinstance(rrule_params['until'], datetime.date):
         rrule_params['until']+=relativedelta(hours=self.start_hour, 
                                                minutes=self.start_minute)
    
    self.set.exrule(rrule.rrule(**rrule_params))
    self._recalculate_occurences()
    self.rules.append({ 'type':'exclude', 'label':label, 'rule':rrule_params})

  def _occurences_in_period(self, start, end):
    """return a list of occurences within a given period (start and end
    datetime)
    """
    occurences = []
    for occ in list(self.set.between(start, end, True)):
      occurences.append(Interval(occ, occ+relativedelta(minutes=+self.duration)))
    return occurences
    
  def _recalculate_occurences(self):
    """Recalculate all the occurences (static list) in the object
    """
    # after adding a rule, we need to recompute the period list
    new_occurences = []
    new_total_duration = 0
    for occ in list(self.set):
      new_occurences.append(Interval(occ, occ+relativedelta(minutes=+self.duration)))
      new_total_duration += self.duration
    self.occurences = new_occurences
    self.total_duration = new_total_duration
    #return new_occurences
    
  def get_rules(self):
    return list(self.set)

  def get_occurences(self):
    return self.occurences
  
  def next_period(self, the_date=datetime.datetime.now(), inclusive=True):
    """Returns the next period (datetime tuple, start and end)
    for a given date.
    If the date is inside a period and inclusive is set to True, returns
    the 'current' period. Otherwise, returns the next period
    
    Return None if no period is found
    """
    period_in = self.in_period(the_date, return_period=True)
    if  period_in and inclusive:
      return period_in
    else:
      after = self.set.after(the_date, True)
      return Interval(after, after+relativedelta(minutes=+self.duration))
      
  def prev_period(self, the_date=datetime.datetime.now(), inclusive=True):
    """Returns the next period (datetime tuple, start and end)
    for a given date.
    If the date is inside a period and inclusive is set to True, returns
    the 'current' period. Otherwise, returns the next period
    
    Return None if no period is found
    """
    period_in = self.in_period(the_date, return_period=True)
    if  period_in and inclusive:
      return period_in
    else:
      previous = self.set.before(the_date, True)
      if period_in:
        if period_in.start == previous:
          previous = self.set.before(previous, False)
      return Interval(previous, previous+relativedelta(minutes=+self.duration))
