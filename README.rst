python-schedule-rules
=====================

Schedule Rules module (SRules) offer a set of tools used to define and manipulate
scheduled elements, based on date Intervals
(like meetings events, etc..)

SRules stores an ordered list of sessions which will be processed
in that order to generate an occurence list.
It can handle 'add' and 'exclude' sessions.

Each session is a set of rules ('normal rules') which indicates periods of
time. This rules can include 'exclude' rules (in rrule terms)
if they are intended to describe the 'normal' session.

Sample
------

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

Dependencies
------------

  python-dateutil : http://labix.org/python-dateutil

Licence
-------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <http://www.gnu.org/licenses/gpl.html>
