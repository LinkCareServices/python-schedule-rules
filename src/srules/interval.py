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
"""interval module

Contains:
* Interval
"""
from past.builtins import cmp
from builtins import str
from builtins import object

__authors__ = [
    # alphabetical order by last name
    'Thomas Chiroux', ]

import datetime


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
            raise ValueError('Start (%s) must not be greater than end (%s)' %
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
        return str(self).encode('utf-8')

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

        .. warning:: The comparaison operator only compare the start date of
           the interval: because Interval can supoerpose each others, it is not
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
          * if intersection: returns a new interval based on max extremities
          * if no intersection: returns a tuple with the 2 intervals given
                                in args

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
            return [Interval(self.start, other.start),
                    Interval(other.end, self.end)]
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

    def duration(self):
        """return the duration of the interval in seconds
        """
        return int((self.end - self.start).total_seconds())
