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

Contains:
* Srules
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
