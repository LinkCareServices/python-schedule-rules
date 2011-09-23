#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2011 Link Care Services
#
"""Schedule Rules

Useful urls:
python-dateutil : http://labix.org/python-dateutil
python operators : http://docs.python.org/library/operator.html

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
  return next(((i, x) for i, x in enumerate(_list) if x == _search), \
                                                                 (None, None))

class Interval(object):
  """Represent an interval (espacialy date interval)
  
  start : represent the datetime of the period start
    end : represent the datetime of the period end
    
  rank : usually not used, but can be set with a value (numeric values)
         this will prioritize Intervals between them if in the same list
         (used for substracting interval lists)
  """
  start = None
  end = None
  rank = None
  
  def __init__(self, start, end):
    if start > end:
      raise ValueError('Start (%s) must not be greater than end (%s)' % \
                                                                 (start, end))
    self.start = start
    self.end = end

  def __repr__(self):
    """Representation of object"""
    return "%s --> %s" % (self.start, self.end)

  def __eq__(self, other):
    """equality operator
    """
    if self.start == other.start and self.end == other.end:
      return True
    else:
      return False
      
  def __cmp__(self, other):
    return cmp(self.start, other.start)
      
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
      return Interval(other.start, other.end)
    elif (self.start <= other.start <= self.end):
      return Interval(other.start, self.end)
    elif (self.start <= other.end <= self.end):
      return Interval(self.start, other.end)
    elif (other.start <= self.start <= self.end <= other.end):
      return Interval(self.start, self.end)
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
      
  def __sub__(self, other): # chercher si il y a un operateur comme pour __add__
    """if intersection, returns a new (smaller) interval : self - other
    if other inside self, can return 2 new intervals
    if other ouside self, return a tuple (self, other)
    """
    if other == self:
      return None 
    elif other in self:
      return [Interval(self.start, other.start), Interval(other.end, self.end)]
    elif self in other:
      return None
    elif self & other:
      if self.start <= other.start:
        return Interval(self.start, other.start)
      else:
        return Interval(other.end, self.end)
    else:
      if self.start < other.start:
        return [self, other]
      else:
        return [other, self]
        
  def __hash__(self):
    """return a hash of the object wich should be unique
    """
    return hash((self.start, self.end))
   
class Session(object):
  """ This objects is a representation of a standard 'session'
  It has a calendar (dateutil) rruleset with one or many rrules inside
  Each Session has a start hour and minute and a 'duration' in order to 
  calculate periods (called Interval). 
  All the Interval in a Session share the same start_hour, minute and duration
  
  The Recuring occurences are calculed by rules (dateutil rrulesets)
  So you only need to specify one or more rule, and the Session class
  will automatically calculate all the resulting Intervals
  
  In a Session object it never authorised to directly manipulate the
  calculated Intervals, because the good behaviour is to update the rules which
  are the only way to define a Session
  
  The Session object provides tools to manipulate the data :
  - it's iterable and gettable: for elt in my_session: ... 
                                my_session[2:5]
  - you can add a Session to another Session : my_session + other_session
  - you can substract Session to another Session : my_session - other_session
  - you can compare equality between Sessions : my_session == other_session
  - you can calculate intersection between Sessions : my_session & other_session
  - you can test if object in inside the Session : if datetime.now() in my_session:
  
  Some of this calculation result can not be defined inside a Session anymore
  (because it's not anymore only on rrule set and onr interval but more than
  one), this calculation results are returned with another object : 
  CalculatedSession (see documentation of this object for more infos)
  
  usage example:
  
  from shedule import Session
  # instanciace a Session with interval from [11h30 to 13h30]
  my_session = Session("Test", duration=60*2, start_hour=11, start_minute=35)
  my_session.add_rule("Every Day", 
                      freq=rrule.DAILY,
                      dtstart=datetime.date(2011,8,15), 
                      interval=1,
                      until = datetime.date(2012,6,30)  
                      )
  """

  def __init__(self, session_name="", duration=60, start_hour=0, start_minute=0,
                     session_type='add', session_description=None):
    """Constructor for Session object

    At creation the object is set with initial parameters, but no rule, so
    no 'calculated intervals'
    you'll need to call at least one time the .add_rule() method to add a rule
    
    Args:
      session_name -- str : the (if possible unique) name you choose for this
                            session
      start_hour -- int ([0-23])  
      start_minute -- int ([0-59]) : the time (hour, minute) of the
        beginning of each period calculated by rules.
      
      duration -- int : duration (in minutes) of each period for this session
      session_tyoe -- str : either 'add' or 'exclude' : flags the type of the
                            session. It is used in Srules object : an session
                            'add' will add his values to other sessions
                            and the 'exclude' will remove his values to other
                            sessions
      session_description -- str : free text to describe your session
      
    Returns:
      <nothing>
    """
    self.session_name = session_name
    self.session_type = session_type
    self.session_description = session_description
    
    self.duration = duration
    if int(start_hour) < 0 or int(start_hour) >= 60:
      raise ValueError("start_hour should be between 0 and 23")
    self.start_hour = int(start_hour)
    
    if int(start_minute) < 0 or int(start_minute) >= 60:
      raise ValueError("start_minute should be between 0 and 59")

    self.start_minute = int(start_minute)
    self.set = rrule.rruleset()
    
    # calculated occurence list:
    self.occurences = []
    self.total_duration = 0
    
    # "backup" of rules, in order to be able to reprocess them
    self.rules = []

  def __iter__(self):
    """iterable
    (see _forward)
    """
    return self._forward()

  def _forward(self):
    """forward generator, used for iteration
    (like in this sample :
    for elt in my_session:
      print elt 
    )
    """
    current_item = 0
    total_len = len(self.occurences)
    while (current_item < total_len):
      interval = self.occurences[current_item]
      current_item += 1
      yield interval
  
  def __len__(self):
    """calculate and return len of Session object
    Warning: It returns the number of intervals in this object, not the total duration
    of all Intervals
    
    Args:
      <none>
      
    Returns:
     int -- number of Intervals in this session
    """
    return len(self.occurences)
    
  def __eq__(self, other):
    """returns a comparaison between self and anoter object
    can compare two objects of same type and also compare object
    to a string
    
    Warning, if you compare Session object with a string, it will compare
    the Session object name to that string, so be careful and try to have
    unique names for your sessions if you plan to compare equality by names
    
    Args:
      other -- can be:
         Session,
         CalculatedSession,
         str
    """
    if isinstance(other, Session) or isinstance(other, CalculatedSession):
      return self.occurences == other.occurences
    elif isinstance(other, str):
      return self.session_name == other
    else:
      raise TypeError("Can not compare Session to %s" % type(other))
 
  def __str__(self):
    """returns a string describing the Session
    """
    return self.session_name
 
  def __contains__(self, other, return_interval=False):
    """test if an interval or a datetime is contained inside self
    
    use with 'in' keyword:
       if my_interval in my_session:
         
    for method use, prefer 'in_interval()'
    
    return True if yes or False if not
    
    Args:
     other -- can be:
         Interval,
         datetime
         
     return_interval -- boolean : if True return the resulting period instead
                                  of boolean value.
                                  
    Returns:
      boolean: True if other in self, False if not
    or:
      Interval: matching if other in self, None if not
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
        if (occ.start <= other <= occ.end):
          if return_interval:
            return occ
          else:
            return True
    
    if return_interval:
      return None
    else:
      return False

  def in_interval(self, other, return_interval=False):
    """public wrapper for __contains__
    mainly used when needed to set return_interval to True
    
    Args:
     other -- can be: (see __contains__)
     return_interval -- boolean : if True return the resulting interval instead
                                  of boolean value.
                                  
    Returns:
      boolean: True if other in self, False if not
    or:
      Interval: matching if other in self, None if not
    """
    return self.__contains__(other, return_interval)
    
  def __and__(self, other):
    """Calculate intersection Session and another object

    Args:
     other -- can be:
        Session,
        CalculatedSession,
        Interval,
        datetime,
        None
     
    returns:
    a CalculatedSession object with the result of the calculation
     (if no result, the CalculatedSession is empty, but it's still a
     CalculatedSession Object)
    """
    result = []
    if other is None:
      return CalculatedSession([])
    if len(other) == 0:
      return CalculatedSession([])
    if len(self) == 0:
      return CalculatedSession([])
      
    if type(other) == Interval:
      all_occs = sorted(self.occurences + [other])
    elif type(other) == datetime.datetime:
      all_occs = sorted(self.occurences + [Interval(other, other)])
    elif type(other) == Session or type(other) == CalculatedSession:
      all_occs = sorted(self.occurences + other.occurences)
    else:
      raise TypeError("Can not calculate Session and %s" % type(other))
      
    all_occs = sorted(self.occurences + other.occurences)
    total_len = len(all_occs)
    for i in range(0, total_len-2):
      _and = all_occs[i] & all_occs[i+1] 
      if _and is not None:
        result.append(_and)
        
    return CalculatedSession(result)
    
  def __add__(self, other):
    """Calculate addition between Session and other object
    
    other can be : 
     Session,
     CalculatedSession
     Interval,
     datetime,
     None
    
    returns:
     a CalculatedSession object with the result of the calculation
     (if no result, the CalculatedSession is empty, but it's still a
     CalculatedSession Object)
    """
    if other is None:
      return CalculatedSession(self.occurences)
    if len(other) == 0:
      return CalculatedSession(self.occurences)
    if len(self) == 0:
      return CalculatedSession(other.occurences)
    
    if type(other) == Interval:
      all_occs = sorted(self.occurences + [other])
    elif type(other) == datetime.datetime:
      all_occs = sorted(self.occurences + [Interval(other, other)])
    elif type(other) == Session or type(other) == CalculatedSession:
      all_occs = sorted(self.occurences + other.occurences)
    else:
      raise TypeError("Can not add Session with %s" % type(other))
      
    recover = True
    while recover: # continues until only disjoint Intervals are present
      total_len = len(all_occs)
      prec_occ = []
      result = []
      recover = False
      for i in range(total_len-1):
        try:
          #print "i:%s, %s, %s" % (i, all_occs[i], all_occs[i+1]) 
          _and = all_occs[i] & all_occs[i+1] 
        except IndexError:
          # index out of range (because of i+1): we are at the end
          #print "i:%s, %s, --" % (i, all_occs[i])
          _and = None
        if _and is not None:
          prec_occ = all_occs[i] + all_occs[i+1]
          result.append(prec_occ)
          recover = True
        else:
          if all_occs[i] not in prec_occ: 
            result.append(all_occs[i])
          if i == total_len-2:
            result.append(all_occs[i+1])
      all_occs = sorted(result)

    return CalculatedSession(result)
    
  def __sub__(self, other):
    """Calculate substration between Session and other object
    
    other can be : 
     Session,
     CalculatedSession
     Interval,
     datetime,
     None
    
    returns:
     a CalculatedSession object with the result of the calculation
     (if no result, the CalculatedSession is empty, but it's still a
     CalculatedSession Object)
    """
    if other is None:
      return CalculatedSession(self.occurences)
    if len(other) == 0:
      return CalculatedSession(self.occurences)
    if len(self) == 0:
      return CalculatedSession([])
    
    for occ in self.occurences:
      occ.rank = 2
    
    if type(other) == Interval:
      other.rank = 1
      all_occs = sorted(self.occurences + [other])
    elif type(other) == datetime.datetime:
      interv = Interval(other, other)
      interv.rank = 1
      all_occs = sorted(self.occurences + [interv])
    elif type(other) == Session or type(other) == CalculatedSession:
      for occ in other.occurences:
        occ.rank = 1
      all_occs = sorted(self.occurences + other.occurences)
    else:
      raise TypeError("Can not substract Session with %s" % type(other))    
  
    recover = True
    while recover: # continues until only disjoint Intervals are present
      #print "----- new loop ------"
      #print all_occs
      #print "---------------------"
      total_len = len(all_occs)
      prec_occ = []
      result = []
      recover = False
      for i in range(0, total_len-1):
        _and = all_occs[i] & all_occs[i+1] 
        if _and is not None:
          if all_occs[i].rank == 2 and all_occs[i+1].rank == 1:
            substraction_result = all_occs[i] - all_occs[i+1]
            prec_occ = all_occs[i]
          elif all_occs[i].rank == 1 and all_occs[i+1].rank == 2:
            # the interval to be subtracted begins before
            substraction_result = all_occs[i+1] - all_occs[i]
            prec_occ = all_occs[i+1]
          elif all_occs[i].rank == 1 and all_occs[i+1].rank == 1:
            # no substraction at all here: what should we do ? 
            # (should not happen)
            substraction_result = None
          
          if type(substraction_result) == Interval:
            #print 'append sub: %s (i=%s)' % (substraction_result,i)
            #prec_occ = substraction_result
            result.append(substraction_result)
          elif type(substraction_result) == list:
            for elt in substraction_result:
              #print 'append sub multiple result: %s (i=%s)' % (elt,i)
              result.append(elt)
          elif substraction_result is None:
            pass
          else:
            raise TypeError('uknown type result for Interval \
substraction_result : %s' % type(substraction_result))
          #recover = True
        else:
          if all_occs[i] not in prec_occ: 
            if all_occs[i].rank == 2:
              #print 'append alone: %s (i=%s)' % (all_occs[i],i)
              result.append(all_occs[i])
          if i == total_len-2:
            if all_occs[i+1].rank == 2:
              #print 'append last: %s (i=%s)' % (all_occs[i+1],i)
              result.append(all_occs[i+1])
            
      all_occs = sorted(result)
          
    for occ in self.occurences:
      occ.rank = None
      
    return CalculatedSession(result)
    
  def __getitem__(self, _slice):
    """Returns and Interval object
    
    usage examples: 
      my_session[5]
      my_session[2:8]
      my_session[:5]
      my_session[-5:]
      ...
    """
    return self.occurences[_slice]
    
  def add_rule(self, label="", **rrule_params):
    """add a recuring rule for this Session
    """
    rrule_params.setdefault('freq', rrule.DAILY)
    rrule_params.setdefault('cache', True)
    
    if 'count' not in rrule_params and 'until' not in rrule_params:
      rrule_params.setdefault('until', 
                              datetime.datetime.now()+relativedelta(years=+5))
    
    if 'dtstart' in rrule_params:
      if isinstance(rrule_params['dtstart'], datetime.date):
        rrule_params['dtstart'] += relativedelta(hours=self.start_hour, 
                                                 minutes=self.start_minute)
    if 'until' in rrule_params:
      if isinstance(rrule_params['until'], datetime.date):
        rrule_params['until'] += relativedelta(hours=self.start_hour, 
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
      rrule_params.setdefault('until', 
                              datetime.datetime.now()+relativedelta(years=+5))

    if 'dtstart' in rrule_params:
      if isinstance(rrule_params['dtstart'], datetime.date):
        rrule_params['dtstart'] += relativedelta(hours=self.start_hour, 
                                                 minutes=self.start_minute)
    if 'until' in rrule_params:
      if isinstance(rrule_params['until'], datetime.date):
        rrule_params['until'] += relativedelta(hours=self.start_hour, 
                                               minutes=self.start_minute)
    
    self.set.exrule(rrule.rrule(**rrule_params))
    self._recalculate_occurences()
    self.rules.append({ 'type':'exclude', 'label':label, 'rule':rrule_params})
    
  def _recalculate_occurences(self):
    """Recalculate all the occurences (static list) in the object
    """
    # after adding a rule, we need to recompute the interval list
    new_occurences = []
    new_total_duration = 0
    for occ in list(self.set):
      new_occurences.append(Interval(occ, 
                                     occ+relativedelta(minutes=+self.duration)))
      new_total_duration += self.duration
    self.occurences = new_occurences
    self.total_duration = new_total_duration
    
  def get_rules(self):
    """Returns the list of rrules
    """
    return list(self.set)

  def get_occurences(self):
    """Returns the list of all the interval
    calculated based on the input rrules
    """
    return self.occurences

  def between(self, start, end, inclusive=True):
    """return a list of occurences within a given interval (start and end
    datetime)
    """
    occurences = []
    for occ in list(self.set.between(start, end, inclusive)):
      occurences.append(Interval(occ, 
                                 occ+relativedelta(minutes=+self.duration)))
    return CalculatedSession(occurences)
      
  def next_interval(self, the_date=datetime.datetime.now(), inclusive=True):
    """Returns the next interval (Interval)
    for a given date.
    If the date is inside a period and inclusive is set to True, returns
    the 'current' period. Otherwise, returns the next period
    
    Return None if no period is found
    """
    period_in = self.__contains__(the_date, return_interval=True)
    if  period_in and inclusive:
      return period_in
    else:
      after = self.set.after(the_date, True)
      return Interval(after, after+relativedelta(minutes=+self.duration))
      
  def prev_interval(self, the_date=datetime.datetime.now(), inclusive=True):
    """Returns the next interval (Interval)
    for a given date.
    If the date is inside a period and inclusive is set to True, returns
    the 'current' period. Otherwise, returns the next period
    
    Return None if no period is found
    """
    period_in = self.__contains__(the_date, return_interval=True)
    if  period_in and inclusive:
      return period_in
    else:
      previous = self.set.before(the_date, True)
      if period_in:
        if period_in.start == previous:
          previous = self.set.before(previous, False)
      return Interval(previous, previous+relativedelta(minutes=+self.duration))

class CalculatedSession(Session):
  """a CalculatedSession is the result of manipulation of one or more sessions
  and when a Session can not be defined by rules anymore
  ex:
  Session + Session = CalculatedSession
  Session - Session = CalculatedSession
  
  Sessions and CalculatedSessions share same method (like __add__, __sub__, etc..)
  but not others (like "add_rule" and all the other rules related methods)
  
  A CalculatedSession is not defined by rrules anymore, because they are the
  result of some merging / extraction of differents Session, Intervals or dates
  """
  
  def __init__(self, const_list=None):
    """Initalisation is done by giving :
      a list of Intervals 
      a Session object
      a CalculatedSession object
      
     (or None if the list will be added later)
    """
    Session.__init__(self)
    
    if type(const_list) == list:
      self.occurences = sorted(const_list)
    elif type(const_list) == Session or type(const_list) == CalculatedSession:
      self.occurences = sorted(const_list.occurences)
      
  def add_rule(self, label="", **rrule_params):
    """cancel this method"""
    return None
    
  def exclude_rule(self, label="", **rrule_params):
    """cancel this method"""
    return None

  def _recalculate_occurences(self):
    """cancel this method"""
    return None
      
  def between(self, start, end, inclusive=True):
    """Returns All Intervals between start and end date
    
    Args:
      start     -- datetime : date and time of the beginning of the period
      end       -- datetime : date and time of the end of the period
      inclusive -- boolean  : if True and if start or end is inside an
                              Interval, it will include the resulting Intervals  
    
    Returns:
      CalculatedSession -- containing all the Interval between start and end
      if no result, returns and 'empty' CalculatedSession object.
    """
    start_interv = self.next_interval(start, inclusive)
    end_interv = self.prev_interval(end, inclusive)
    result = []
    start_to_add = False
    for interv in self.occurences:
      if interv == start_interv:
        start_to_add = True
      if start_to_add:
        result.append(interv)
      if interv == end_interv:
        start_to_add = False
    return CalculatedSession(result)

  def next_interval(self, the_date=datetime.datetime.now(), inclusive=True):
    """Returns the next period (Interval)
    for a given date.
    If the date is inside a period and inclusive is set to True, returns
    the 'current' period. Otherwise, returns the next period
    
    Args:
      the_date -- datetime : date and time to be tested
      inclusive -- boolean : if True and if the_date is inside an
                             Interval, it will return this Interval
    Returns:
      Interval -- and Interval object if found                         
      None if no interval is found
    
    note: this CalculatedSession version can not use rules to find the period
    so, it iter the Interval list
    """
    # some shotcuts (occurences are sorted):
    if self.occurences[0].start > the_date:
      return None
    if self.occurences[-1].end < the_date:
      return None
    return_next = False
    for elt in self.occurences:
      if return_next:
        return elt
      if the_date in elt and inclusive:
        return elt
      if elt.end < the_date:
        continue
      if elt.end >= the_date:
        if elt.start > the_date:
          return elt
        else:
          return_next = True     
    return None
  
  def prev_interval(self, the_date=datetime.datetime.now(), inclusive=True):
    """Returns the previous period (Interval)
    for a given date.
    If the date is inside a period and inclusive is set to True, returns
    the 'current' period. Otherwise, returns the prev period
    
    Return None if no period is found
    
    note: this CalculatedSession version can not use rules to find the period
    so, it iter the Interval list
    """
    # some shotcuts (occurences are sorted):
    if self.occurences[0].start > the_date:
      return None
    if self.occurences[-1].end < the_date:
      return None
    last_period = None
    for elt in self.occurences:
      if the_date in elt and inclusive:
        return elt
      if the_date in elt and not inclusive:
        return last_period
      if the_date < elt.start:
        return last_period
      last_period = elt
    return None

class SRules(CalculatedSession):
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
    CalculatedSession.__init__(self)
    
    self.name = name
    self.auto_refresh = auto_refresh

  def add_rule(self, label="", **rrule_params):
    """cancel this method"""
    return None

  def exclude_rule(self, label="", **rrule_params):
    """cancel this method"""
    return None

  def add_session(self, session):
    """add new session for this person

    description -- string -- description of the session
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

  def _recalculate_occurences(self):
    """Recalculate all the occurences (static list) in the object
    """
    # after adding a rule, we need to recompute the period list
    new_occurences = []
    new_total_duration = 0
    for _session in self.sessions:
      new_occurences2 = CalculatedSession(new_occurences)
      if _session.session_type == 'add':
        new_occurences2 = new_occurences2 + _session
      elif _session.session_type == 'exclude':
        new_occurences2 = new_occurences2 - _session
      new_occurences = list(new_occurences2)

    self.occurences = new_occurences
    self.total_duration = new_total_duration
    #return new_occurences
