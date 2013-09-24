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

Dependencies:
  python-dateutil : http://labix.org/python-dateutil

Useful URL:
  python operators : http://docs.python.org/library/operator.html

"""

from srules.interval import Interval
from srules.session import Session, CalculatedSession
from srules.schedule import SRules

__all__ = 'Interval Session CalculatedSession SRules'.split()
