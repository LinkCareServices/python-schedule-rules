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


class Person(object):
  """A person is an entity wich can have multiple sessions of work
  (each session is a number of past and future occurences)
  
  each session is a set of rules 'normal rules' which indicates periods of
  time that the person should be working. This rules can include 'exclude' rules
  if they are indended to decribe the 'normal' session of work
  The session should not include hollidys, days off, etc...
  
  each exclusion is also a set of rules containing all the abscences of the people:
  holidays, etc...
  
  When processing the time of presence, we will process at first with sessions
  (add time of work) and then with exclusions, resulting a complete time
  of presence.
  
  TODO: Comment gérer les 'échanges de postes' : tester avec les postes à la fidélia.
        si on ajoute en session puis exclusion le meme jour, les heures communes vont s'annuler...
  """
  name = None
  login = None
  password = None
  sessions = []
  
  def __init__(self, name):
    self.name = name
  
  def add_session(self, description, session):
    """add new session for this person
    
    description -- sting -- description of the session
    session -- Session object
    
    the session object must be already instanciated
    """
    self.sessions.append(session)

class Session(object):
  """
  This objects is a representation of a standard 'session' of an employee
  It has a calendar (dateutil) rruleset with one or many rrules inside
  Each Session has a standard 'duration', wich will be used to calculate
  the start and end datetime of each occurence
  
  TODO: regler le pb d'exclusion d'une plage horaire qui ne correspond pas 
    (mais qui peut chevaucher) aux plages de la session.
    Ex: session tous les jours de 8h à 12h
    exclusion lundi 14 de 9h à 10h ==> comment gérer ?
    actuellement, une occurence de session, c'est une date, une heure start et une durée
       (cela peut être plusieurs fois par jour mais chaque occurence aura la meme durée)
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
    
    # "backup" of rules, in order to be able to reprocess them
    self.rules = []

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
      # TODO:here we have two objects to compare we need to compare the occurences..
      return cmp(self.session_name, other.session_name)
    elif isinstance(other, str):
      return cmp(self.session_name, other)
    else:
      return False
 
  def __str__(self):
    """returns a string describing the Session
    """
    return "%s:%s" % (self.session_name, self.session_type)
 
 
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
      occurences.append((occ, occ+relativedelta(minutes=+self.duration)))
    return occurences
    
  def _recalculate_occurences(self):
    """Recalculate all the occurences (static list) in the object
    """
    # after adding a rule, we need to recompute the period list
    new_occurences = []
    for occ in list(self.set):
      new_occurences.append((occ, occ+relativedelta(minutes=+self.duration)))
    self.occurences = new_occurences
    return new_occurences
    
  def get_rules(self):
    return list(self.set)

  def get_occurences(self):
    return self.occurences

  def in_period(self, the_date=datetime.datetime.now()):
    """Returns True if the given date is inside a period defined by
    all the rules of this object
    possible optimization : use between method to filter some occurences
    and test only the filtered occurences
    """
    date_or_now = lambda x: x if x is not None else datetime.datetime.now()
    start = date_or_now(self.set.before(datetime.datetime.now(), True))
    end = date_or_now(self.set.before(datetime.datetime.now(), True))
    
    occurences = self._occurences_in_period(start, end)
    # old 'parse all' method: 
    #occurences = self.occurences

    for period_occurence in self.occurences:
      if period_occurence[0] <= the_date and period_occurence[1] >= the_date:
        return True
    
    return False
    
def test():
  vac = Session(60*7)
  vac.add_rule("1er jour des 6", freq=rrule.DAILY,dtstart=datetime.date.today(), interval=6)
  vac.add_rule("2eme jour des 6", freq=rrule.DAILY,dtstart=datetime.date.today()+relativedelta(days=+1), interval=6)
  vac.add_rule("3eme jour des 6", freq=rrule.DAILY,dtstart=datetime.date.today()+relativedelta(days=+2), interval=6)
  vac.list_rules()