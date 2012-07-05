#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2011-2012 Link Care Services
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.
# If not, see <http://www.gnu.org/licenses/gpl.html>
#
"""
Schedule Rules module offer a set of tools used to define and manipulate
scheduled elements, based on date Intervals
(like meetings events, etc..)

It is based on *python-dateutil* and uses the same rrule mecanism as a basis.
But unlike python-datetuil which describes only time-events, Schedule Rules
uses the rrule mecanism to describes time-interval (and of course recurring
time intervals).

Usage of this tool can be limited to define
and work wich :py:class:`schedule.SRules`

Dependancies:
  python-dateutil : http://labix.org/python-dateutil

Useful URL:
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
  return next(((i, x) for i, x in enumerate(_list) if x == _search),
              (None, None))

class Interval(object):
  """Represent an interval (especialy date interval)

    Args:
      :start:   represent the datetime of the period start
      :end:     represent the datetime of the period end
    
  """
  start = None
  end = None
  rank = None

  def __init__(self, start, end):
    """Interval Constructor

    *Args:*
      (see Class Description : :py:class:`schedule.Interval` )

    *Returns:*
      *Nothing*

    """
    if start > end:
      raise ValueError('Start (%s) must not be greater than end (%s)' % \
                                                                 (start, end))
    self.start = start
    self.end = end


  def __unicode__(self):
    """Returns unicode string describting the objects and his content

    *Args:*
      *None*

    *Returns:*
      :unicode: unicode string representation
                of an :py:class:`schedule.Interval`

    """
    return u"%s --> %s" % (self.start, self.end)

  def __repr__(self):
    """Representation of object

    *Args:*
      *None*

    *Returns:*
      :string: string representation of an :py:class:`schedule.Interval`

    """
    return unicode(self).encode('utf-8')

  def __eq__(self, other):
    """'==' operator

    *Usage example:*

    .. code-block:: python

        if Interval1 == Interval2:
          ...

    *Returns:*
      :boolean: True if equal, False if not

    """
    if self.start == other.start and self.end == other.end:
      return True
    else:
      return False
      
  def __cmp__(self, other):
    """comparaison operator

    *Usage example:*

    .. code-block:: python

        if Interval1 > Interval2:
          ...

        if Interval1 <= Interval2:
          ...

    .. warning:: The comparaison operator only compare the start date of the
       interval : because Interval can supoerpose each others, it is not
       possible to compare the full interval. Be careful when using
       comparaisons
    """
    return cmp(self.start, other.start)
      
  def __contains__(self, other):
    """'in' operator

    Test if and interval is contained inside the other

    *Usage example:*

    .. code-block:: python

        if Interval1 in Interval2:
          ...

    *returns:*
      :boolean: True if yes, False if not
    """
    if type(other) == Interval:
      if self.start <= other.start <= other.end <= self.end:
        return True
      else:
        return False
    elif type(other) == datetime.datetime:
      if self.start <= other <= other <= self.end:
        return True
      else:
        return False

  def __and__(self, other):
    """'&' operator

    returns the interval in intersection between the two input intervals
    or None if there is no intersection

    *Usage example:*

    .. code-block:: python

        Interval3 = Interval1 & Interval2


    *return:*
      :Interval: Interval object

    """
    if self.start <= other.start <= other.end <= self.end:
      return Interval(other.start, other.end)
    elif self.start <= other.start <= self.end:
      return Interval(other.start, self.end)
    elif self.start <= other.end <= self.end:
      return Interval(self.start, other.end)
    elif other.start <= self.start <= self.end <= other.end:
      return Interval(self.start, self.end)
    else:
      return None
  
  def __add__(self, other):
    """'+' operator

    Add two Intervals

    *Usage example:*

    .. code-block:: python

        result = Interval1 + Interval2


    *returns:*
      * if intersection, returns a new interval based on max extremities
      * if no intersection : returns a tuple with the 2 intervals given in args

    """
    if self & other:
      return Interval(min(self.start, other.start), 
                      max(self.end, other.end))
    else:
      return self, other
      
  def __sub__(self, other):
    """'-' operator

    Substract two Intervals

    *Usage example:*

    .. code-block:: python

        result = Interval1 - Interval2


    *returns:*
      * if intersection, returns a new (smaller) interval : self - other
      * if other inside self, return 2 new intervals
      * if other outside self, return a tuple (self, other)

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
    """return a hash of the object which should be unique
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
  
  In a Session object it's never authorised to directly manipulate the
  calculated Intervals, because the good behaviour is to update the rules which
  are the only way to define a Session
  
  The Session object provides tools to manipulate the data :

  - it's iterable and gettable:

    .. code-block:: python

      for elt in my_session:
        ...

    .. code-block:: python

      my_session[2:5]
      ...

  - you can add a Session to another Session :

    .. code-block:: python

      my_session + other_session

  - you can substract Session to another Session :

    .. code-block:: python

      my_session - other_session

  - you can compare equality between Sessions :

    .. code-block:: python

      my_session == other_session

  - you can calculate intersection between Sessions :

    .. code-block:: python

      my_session & other_session

  - you can test if object in inside the Session :

    .. code-block:: python

      if datetime.now() in my_session:
        ...

  Some of this calculation result can not be defined inside a Session anymore
  (because it's not anymore only on rrule set and on interval but more than
  one), this calculation results are returned in another object :
  :py:class:`schedule.CalculatedSession`

  To be able to use session correctly, you have to :

  - first to instanciate a Session object
  - Then to add at least one rule using :py:meth:`schedule.Session.add_rule`

  usage example:

  .. code-block:: python

     from shedule import Session
     # instanciace a Session with interval from [11h30 to 13h30]
     my_session = Session("Test", duration=60*2, start_hour=11, start_minute=35)
     my_session.add_rule("Every Day",
                         freq=rrule.DAILY,
                         dtstart=datetime.date(2011,8,15),
                         interval=1,
                         until = datetime.date(2012,6,30)
                        )


  *Args:*
      :session_name: (string) : the (if possible unique)
                     name you choose for this session
      :start_hour: (int [0-23]) :
      :start_minute: (int [0-59]) : the time (hour, minute) of the
        beginning of each period calculated by rules.

      :duration: (int) : duration (in minutes) of each period for this session
      :session_type: (string) : either 'add' or 'exclude' :
                     flags the type of the session.
                     It is used in Srules object : a session
                     'add' will add its values to other sessions
                     and the 'exclude' will remove his values to other
                     sessions
      :session_description: (string) : free text to describe your session

  """

  def __init__(self, session_name="", duration=60, start_hour=0, start_minute=0,
                     session_type='add', session_description=None):
    """Constructor for Session object

    At creation the object is set with initial parameters, but no rule, so
    no 'calculated intervals'
    you'll need to call at least one time the
    :py:meth:`schedule.Session.add_rule` method to add a rule
    
    *Args:*
      (see class description: :py:class:`schedule.Session` )

    *Returns:*
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

  def __unicode__(self):
    """Returns unicode string describting the objects and his content

    *Args:*
      *None*

    *Returns:*
      :unicode: unicode string representation
                of an :py:class:`schedule.Interval`

    """
    return u"%s" % self.session_name

  def __repr__(self):
    """Representation of object

    *Args:*
      *None*

    *Returns:*
      :string: string representation of an :py:class:`schedule.Interval`

    """
    return unicode(self).encode('utf-8')

  def __iter__(self):
    """iterable
    (see :py:meth:`schedule.Session._forward` )
    """
    return self._forward()

  def _forward(self):
    """forward generator, used for iteration

    usage example:

      .. code-block:: python

        for elt in my_session:
          print elt

    """
    current_item = 0
    total_len = len(self.occurences)
    while current_item < total_len:
      interval = self.occurences[current_item]
      current_item += 1
      yield interval
  
  def __len__(self):
    """calculate and return len of Session object

    .. warning:: It returns the number of intervals in this object,
       not the total duration of all Intervals

    usage example:

      .. code-block:: python

        print len(my_session)

    *Args:*
      <none>
      
    *Returns:*
     :int: number of Intervals in this session

    """
    return len(self.occurences)
    
  def __eq__(self, other):
    """'==' operator

    returns a comparaison between self and anoter object
    can compare two objects of same type and also compare object
    to a string
    
    .. warning:: if you compare Session object with a string, it will compare
      the Session object name to that string, so be careful and try to have
      unique names for your sessions if you plan to compare equality by names

    usage examples:

      .. code-block:: python

        if my_session == other_session:
          ...


      .. code-block:: python

        if my_session == "Test Session":
          ...

      .. code-block:: python

        if my_session == any_calculated_session:
          ...

    *Args:*
      :other: can be:
         * Session,
         * CalculatedSession,
         * str

    *Returns:*
      :boolean: True if equal, False if not

    """
    if isinstance(other, Session) or isinstance(other, CalculatedSession):
      return self.occurences == other.occurences
    elif isinstance(other, str):
      return self.session_name == other
    else:
      raise TypeError("Can not compare Session to %s" % type(other))
 
  def __contains__(self, other, return_interval=False):
    """'in' operator

    test if an interval or a datetime is contained inside the session

    usage examples:

      .. code-block:: python

        if an_interval in my_session:
          ...


      .. code-block:: python

        if datetime.datetime.now() in my_session:
          ...

    see also :py:class:`schedule.Session.in_interval`
    
    *Args:*
      :other: can be:
         * Interval
         * datetime
         
      :return_interval: (boolean) : if True return the resulting period instead
                                  of boolean value.
                                  
    *Returns:*
      :boolean: True if other in self, False if not

      or:

      :Interval: matching if other in self, None if not

    """
    if type(other) == Interval:
      for occ in self.occurences:
        if occ.start <= other.start <= other.end <= occ.end:
          if return_interval:
            return occ
          else:
            return True
    elif type(other) == datetime.datetime:
      for occ in self.occurences:
        if occ.start <= other <= occ.end:
          if return_interval:
            return occ
          else:
            return True
    
    if return_interval:
      return None
    else:
      return False

  def in_interval(self, other, return_interval=False):
    """public wrapper for :py:class:`schedule.Session.__contains__`
    mainly used when needed to set *return_interval* to True

    usage examples:

      .. code-block:: python

        result_interval = my_session.in_interval(any_interval, True)
          ...


    *Args:*
      :other: can be:

         * Interval
         * datetime

      :return_interval: (boolean) : if True return the resulting period instead
                                  of boolean value.

    .. note:: The Interval returned when return_interval is set to True is
       the matching Interval in the session which contain entirely the
       tested_interval

    *Returns:*

      * if *return_interval* is set to False:

        :boolean: True if other in self, False if not

      * if *return_interval* is set to True:

        :None: if not match

        or:

        :Interval: matching if other in self

    """
    return self.__contains__(other, return_interval)
    
  def __and__(self, other):
    """'&' operator

    Calculate intersection Session and another object

    usage examples:

      .. code-block:: python

        result = my_session & other_session
          ...

      .. code-block:: python

        result = my_session & other_calculated_session
          ...

      .. code-block:: python

        result = my_session & other_interval
          ...

      .. code-block:: python

        result = my_session & datetime.datetime.now()
          ...


    *Args:*
     :other: can be:

        * Session
        * CalculatedSession
        * Interval
        * datetime
        * None
     
    *Returns:*
    a :py:class:`schedule.CalculatedSession` object with the result
    of the calculation (if no result, the
    :py:class:`schedule.CalculatedSession` is empty, but it's still a
    :py:class:`schedule.CalculatedSession` Object)


    """
    result = []
    if other is None:
      return CalculatedSession([])
    if not len(other):
      return CalculatedSession([])
    if not len(self):
      return CalculatedSession([])
      
    if type(other) == Interval:
      all_occs = sorted(self.occurences + [other])
    elif type(other) == datetime.datetime:
      all_occs = sorted(self.occurences + [Interval(other, other)])
    elif type(other) == Session or type(other) == CalculatedSession:
      all_occs = sorted(self.occurences + other.occurences)
    else:
      raise TypeError("Can not calculate Session and %s" % type(other))

    total_len = len(all_occs)
    for i in range(0, total_len-2):
      _and = all_occs[i] & all_occs[i+1] 
      if _and is not None:
        result.append(_and)
        
    return CalculatedSession(result)
    
  def __add__(self, other):
    """'+' operator

    Calculate addition between Session and other object

    usage examples:

      .. code-block:: python

        result = my_session + other_session
          ...

      .. code-block:: python

        result = my_session + other_calculated_session
          ...

      .. code-block:: python

        result = my_session + other_interval
          ...

      .. code-block:: python

        result = my_session + datetime.datetime.now()
          ...

    .. note:: if you add a datetime to a session, it will in fact add
         an Interval (a very small Interval) with
         start = end = the_given_datetime

    *Args:*
     :other: can be:

        * Session
        * CalculatedSession
        * Interval
        * datetime
        * None
    
    *Returns:*
    a :py:class:`schedule.CalculatedSession` object with the result
    of the calculation (if no result, the
    :py:class:`schedule.CalculatedSession` is empty, but it's still a
    :py:class:`schedule.CalculatedSession` Object)

    """
    if other is None:
      return CalculatedSession(self.occurences)
    if not len(other):
      return CalculatedSession(self.occurences)
    if not len(self):
      return CalculatedSession(other.occurences)
    
    if type(other) == Interval:
      all_occs = sorted(self.occurences + [other])
    elif type(other) == datetime.datetime:
      all_occs = sorted(self.occurences + [Interval(other, other)])
    elif type(other) == Session or type(other) == CalculatedSession:
      all_occs = sorted(self.occurences + other.occurences)
    else:
      raise TypeError("Can not add Session with %s" % type(other))

    result = []
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
    """'-' operator

    Calculate substration between Session and other object
    
    usage examples:

      .. code-block:: python

        result = my_session - other_session
          ...

      .. code-block:: python

        result = my_session - other_calculated_session
          ...

      .. code-block:: python

        result = my_session - other_interval
          ...

      .. code-block:: python

        result = my_session - datetime.datetime.now()
          ...

    .. note:: if you subtract a datetime to a session, it will in fact
         substract an Interval (a very small Interval) with
         start = end = the_given_datetime

    *Args:*
     :other: can be:

        * Session
        * CalculatedSession
        * Interval
        * datetime
        * None

    *Returns:*
    a :py:class:`schedule.CalculatedSession` object with the result
    of the calculation (if no result, the
    :py:class:`schedule.CalculatedSession` is empty, but it's still a
    :py:class:`schedule.CalculatedSession` Object)

    """
    if other is None:
      return CalculatedSession(self.occurences)
    if not len(other):
      return CalculatedSession(self.occurences)
    if not len(self):
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

    result = []
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
          substraction_result = None
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
    """slice operator

    usage examples:

      .. code-block:: python

          interv = my_session[5]

      .. code-block:: python

          print my_session[2:8]

      .. code-block:: python

          print my_session[:5]

      .. code-block:: python

          print my_session[-5:]

    *returns:*
      :Interval: one Interval object

    or

      :list: a list of Interval objects if returns more than one value

    """
    return self.occurences[_slice]
    
  def add_rule(self, label="", **rrule_params):
    """add a recuring rule for this Session

    It uses the http://labix.org/python-dateutil syntax, so please refer
    to the dateutil documentation for more samples and explanation

    a Session object contains a rruleset object (wich is a set of rrules)

    the :py:meth:`schedule.Session.add_rule` method add a rrule to the
    Session rrule set, using the dateutil methods and arguments.

    usage examples:

      .. code-block:: python

          my_session.add_rule("label1",
                              freq=rrule.DAILY,
                              dtstart=datetime.date(2011,8,25),
                              interval = 5,
                              until=datetime.date(2012,1,1)
                             )

    *Args:*
      see python-dateutil documentation
      http://labix.org/python-dateutil#head-cf004ee9a75592797e076752b2a889c10f445418

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
    """exclude a recuring rrule to this Session

    see :py:meth:`schedule.Session.add_rule` for more explanation

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

    This method is used by :py:meth:`schedule.Session.add_rule` and
    :py:meth:`schedule.Session.exclude_rule` in order to maintain
    a static list of Intervals based on the rrule given in input.

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

    *Args:*
      <none>

    *Returns:*
      :list: a list of all the rrules in the rrule set for this session

    """
    return list(self.set)

  def get_occurences(self):
    """Returns the list of all the interval
    calculated based on the input rrules

    *Args:*
      <none>

    *Returns:*
      :list: (Interval) a list of Interval objects

    """
    return self.occurences

  def between(self, start, end, inclusive=True):
    """Return all occurences between two dates

    *Args:*
      :start: (datetime) : the date and time starting the period
      :end: (datetime) : the date and time ending the period
      :inclusive: (boolean) : if True returns also Interval starting or
                              ending by *start* or *end*.
                              To make a mathematic parallel:
                              True is like [start-end]
                              False is like ]start-end[

    +Returns:*
      :CalculatedSession: a :py:class:`schedule.CalculatedSession` containing
        all the Interval within start and end

    """
    occurences = []
    for occ in list(self.set.between(start, end, inclusive)):
      occurences.append(Interval(occ, 
                                 occ+relativedelta(minutes=+self.duration)))
    return CalculatedSession(occurences)
      
  def next_interval(self, the_date=None, inclusive=True):
    """Returns the next interval (Interval) for a given date.
    If the date is inside a period and inclusive is set to True, returns
    the 'current' period. Otherwise, returns the next period
    
    Return None if no period is found

    *Args:*
      :the_date: (datetime), by default if not given : now()
      :inclusive: (boolean)

    *Returns:*
      :Interval: the next Interval

    """
    if the_date is None:
      the_date = datetime.datetime.now()

    period_in = self.__contains__(the_date, return_interval=True)
    if period_in and inclusive:
      return period_in
    else:
      after = self.set.after(the_date, True)
      return Interval(after, after+relativedelta(minutes=+self.duration))
      
  def prev_interval(self, the_date=None, inclusive=True):
    """Returns the previous interval (Interval) for a given date.
    If the date is inside a period and inclusive is set to True, returns
    the 'current' period. Otherwise, returns the previous period
    
    Return None if no period is found

    *Args:*
      :the_date: (datetime), by default if not given : now()
      :inclusive: (boolean)

    *Returns:*
      :Interval: the previos Interval

    """
    if the_date is None:
      the_date = datetime.datetime.now()

    period_in = self.__contains__(the_date, return_interval=True)
    if period_in and inclusive:
      return period_in
    else:
      previous = self.set.before(the_date, True)
      if period_in:
        if period_in.start == previous:
          previous = self.set.before(previous)
      return Interval(previous, previous+relativedelta(minutes=+self.duration))

class CalculatedSession(Session):
  """a CalculatedSession is the result of manipulation of one or more sessions
  and when a Session can not be defined by rules anymore

  usage examples:

    .. code-block:: python

      calc_session = my_session + other_session

    .. code-block:: python

      calc_session = my_session - other_session

  CalculatedSession inherit all methods from Session, so they share all
  method and functionnality **except 3:**

    * *add_rule*
    * *exclude_rule*
    * *_recalculate_occurences*

  Obviously, these 3 method can not apply to a CalculatedSession object
  which is static by construction : a CalculatedSession is not defined
  by rrules anymore, because they are the
  result of some merging / extraction of differents Session, Intervals or dates

  Plase see :py:class:`schedule.Session` for all other object and
  method documentations.

  *Args:*
    can be:
      :Interval list: a list of Intervals
      :Session: a Session object
      :CalculatedSession: another CalculatedSession object
      :None: None object (resulting to an empty CalculatedSession object)

  """
  
  def __init__(self, const_list=None):
    Session.__init__(self)
    
    if type(const_list) == list:
      self.occurences = sorted(const_list)
    elif type(const_list) == Session or type(const_list) == CalculatedSession:
      self.occurences = sorted(const_list.occurences)
      
  def add_rule(self, label="", **rrule_params):
    raise NotImplementedError(
      "'CalculatedSession' object does not implement 'add_rule'")

  def exclude_rule(self, label="", **rrule_params):
    raise NotImplementedError(
      "'CalculatedSession' object does not implement 'exclude_rule'")

  def get_rules(self):
    raise NotImplementedError(
      "'CalculatedSession' object does not implement 'get_rules'")

  def _recalculate_occurences(self):
    raise NotImplementedError(
      "'CalculatedSession' object does not implement '_recalculate_occurences'")
      
  def between(self, start, end, inclusive=True):
    #see :py:meth:`schedule.Session.between`
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

  def next_interval(self, the_date=None, inclusive=True):
    #see :py:meth:`schedule.Session.next_interval`
    # some shotcuts (occurences are sorted):
    if the_date is None:
      the_date = datetime.datetime.now()

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
  
  def prev_interval(self, the_date=None, inclusive=True):
    #see :py:meth:`schedule.Session.prev_interval`
    # some shotcuts (occurences are sorted):
    if the_date is None:
      the_date = datetime.datetime.now()

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
  """SRules : Schedule Rules Class

  SRules stores an ordered list of sessions which will be processed
  in that order to generate an occurence list.
  It can handle 'add' and 'exclude' sessions.

  Each session is a set of rules ('normal rules') which indicates periods of
  time. This rules can include 'exclude' rules (in rrule terms)
  if they are indended to decribe the 'normal' session.

  SRules inherit all methods from CalculatedSession, so they share all
  method and functionnality with **one difference** :

    * *_recalculate_occurences* is again defined.

  SRules has also 3 new methods :

    * :py:class:`schedule.SRules.add_session`
    * :py:class:`schedule.SRules.remove_session`
    * :py:class:`schedule.SRules.move_session`


  .. note:: Ex. (person at work)

    * session1 (add) = all the week days from 08:00 to 18:00 :
      aka all the normal working days

    * session2 (exclude) = All the days between 1st April and 13th April : holidays

    * session3 (add) = sunday 10/07/2011 from 14:00 to 17:00 : an extra day

    code:

    .. code-block:: python

      import datetime
      from schedule import Session, SRules, Interval, CalculatedSession
      from dateutil.relativedelta import relativedelta

      from dateutil import rrule

      ses1 = Session("Work", duration=60*10,start_hour=8, start_minute=00)
      ses1.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,22), interval = 7)
      ses1.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,23), interval = 7)
      ses1.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,24), interval = 7)
      ses1.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,25), interval = 7)
      ses1.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,26), interval = 7)

      ses2 = Session("Hollidays",
                     session_type='exclude',
                     duration=60*24,
                     start_hour=00,
                     start_minute=00)
      ses2.add_rule("",
                    freq=rrule.DAILY,
                    dtstart= datetime.date(2012,4, 1),
                    until = datetime.date(2012,4, 13),
                    interval = 1)

      ses3 = Session("ExtraWorkDay", duration=60*3, start_hour=14, start_minute=00)
      ses3.add_rule("",
                    freq=rrule.DAILY,
                    count = 1,
                    dtstart= datetime.date(2011,7, 10))

      my_srule = SRules("Test")
      my_srule.add_session(ses1)
      my_srule.add_session(ses2)
      my_srule.add_session(ses3)

      datetime.datetime(2012, 4,2,15,30) in my_srule
      Out[26]: False

      my_srule.remove_session("Hollidays")
      datetime.datetime(2012, 4,2,15,30) in my_srule
      Out[29]: True

  *Args:*
    :name:  (string) : a name you choose for this SRules object
    :auto_refresh: (boolean) :

      * if True, _recalculate_occurences will be done
        every time a session is added, removed or moved

      * if False, you'll have to call _recalculate_occurences manually. It can
        save some CPU when creating complex or big SRules.

  """
  name = ""
  sessions = []
  occurences = []
  auto_refresh = True
  total_duration = 0

  def __init__(self, name, auto_refresh=True):
    CalculatedSession.__init__(self)
    
    self.name = name
    self.auto_refresh = auto_refresh

  def add_session(self, session):
    """add new session to SRules object

    usage examples:

    .. code-block:: python

      my_srules.add_session(my_new_session)

    *Args:*
      :session: (Session) the session object you want to add.
        the object needs to be instanciated before adding it to the SRules

    *Returns:*
      <nothing>

    """
    self.sessions.append(session)

    if self.auto_refresh:
      self._recalculate_occurences()

  def remove_session(self, name_or_pos):
    """Remove a (previously added) session of the objects.

    usage examples:

    .. code-block:: python

      my_srules.remove_session("Session Test")

    .. code-block:: python

      my_srules.remove_session(3)


    *Args:*
      :name_or_pos: can be either:

          * *string* : the name of the session you're trying to remove

          * *int* : the position (in the session list) of the session you're
              trying to remove

    *Returns:*
      <nothing>

    """
    if type(name_or_pos) == int:
      self.sessions.pop(name_or_pos)
    elif type(name_or_pos) == str:
      pos, session = find(self.sessions, name_or_pos)
      if pos is not None:
        self.sessions.pop(pos)
      else:
        raise KeyError("No Session '%s' found" % name_or_pos)
    if self.auto_refresh:
      self._recalculate_occurences()

  def move_session(self, old_position, new_position):
    """Move a session in the list
    Used to change the order, and possibliy the behaviour of the SRules

    usage examples:

      .. code-block:: python

        my_srules.move_session(1,3)

    *Args:*
      :old_position: (int) old position of the session in the list
      :new_position: (int) new position of the session in the list

    *Returns:*
      <nothing>

    """
    self.sessions.insert(new_position, self.sessions.pop(old_position))

    if self.auto_refresh:
      self._recalculate_occurences()

  def _recalculate_occurences(self):
    """Recalculate all the occurences (static list) in the object

    This method is used by :py:meth:`schedule.SRules.add_session` and
    :py:meth:`schedule.SRules.remove_session` and
    :py:meth:`schedule.SRules.move_session` in order to maintain
    a static list of Intervals based on the sessions (and session order)
    inside the SRules object.

    it can be called manually, especially when the object is created with
    auto_refresh set to False.

    """
    # after adding a rule, we need to recompute the period list

    new_calc_session = CalculatedSession([])
    new_total_duration = 0
    for _session in self.sessions:
      #new_occurences2 = CalculatedSession(new_occurences)
      if _session.session_type == 'add':
        new_calc_session = new_calc_session + _session
      elif _session.session_type == 'exclude':
        new_calc_session = new_calc_session - _session
      #new_occurences = list(new_occurences2)

    self.occurences = list(new_calc_session) #new_occurences
    self.total_duration = new_total_duration # not used
