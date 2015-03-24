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
"""session module

Contains:
* Session
* CalculatedSession
"""
from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object

__authors__ = [
    # alphabetical order by last name
    'Thomas Chiroux', ]

from dateutil.relativedelta import relativedelta
from dateutil import rrule
import datetime

from .interval import Interval


class Session(object):
    """ This objects is a representation of a standard 'session'
    It has a calendar (dateutil) rruleset with one or many rrules inside
    Each Session has a start hour and minute and a 'duration' in order to
    calculate periods (called Interval).
    All the Interval in a Session share the same start_hour, minute
    and duration

    The Recuring occurences are calculed by rules (dateutil rrulesets)
    So you only need to specify one or more rule, and the Session class
    will automatically calculate all the resulting Intervals

    In a Session object it's never authorised to directly manipulate the
    calculated Intervals, because the good behaviour is to update the rules
    which are the only way to define a Session

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
       my_session = Session("Test", duration=60*2, start_hour=11,
                            start_minute=35)
       my_session.add_rule("Every Day",
                           freq=rrule.DAILY,
                           dtstart=datetime.date(2011,8,15),
                           interval=1,
                           until = datetime.date(2012,6,30))


    *Args:*
        :session_name: (string) : the (if possible unique)
                       name you choose for this session
        :start_hour: (int [0-23]) :
        :start_minute: (int [0-59]) : the time (hour, minute) of the
          beginning of each period calculated by rules.

        :duration: (int): duration (in minutes) of each period for this session
        :session_type: (string): either 'add' or 'exclude' :
                       flags the type of the session.
                       It is used in Srules object : a session
                       'add' will add its values to other sessions
                       and the 'exclude' will remove his values to other
                       sessions
        :session_description: (string) : free text to describe your session

    """

    def __init__(self, session_name="",
                 duration=60, start_hour=0, start_minute=0,
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
        return str(self).encode('utf-8')

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

        .. warning:: if you compare Session object with a string, it will
           compare the Session object name to that string, so be careful and
           try to have unique names for your sessions if you plan to compare
           equality by names

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

          :return_interval: (boolean): if True return the resulting period
                                       instead of boolean value.

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

          :return_interval: (boolean): if True return the resulting period
                                       instead of boolean value.

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
        while recover:  # continues until only disjoint Intervals are present
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
        while recover:  # continues until only disjoint Intervals are present
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
                        result.append(substraction_result)
                    elif type(substraction_result) == list:
                        for elt in substraction_result:
                            result.append(elt)
                    elif substraction_result is None:
                        pass
                    else:
                        raise TypeError('uknown type result for Interval'
                                        'substraction_result : %s' %
                                        type(substraction_result))
                        #recover = True
                else:
                    if all_occs[i] not in prec_occ:
                        if all_occs[i].rank == 2:
                            result.append(all_occs[i])
                    if i == total_len-2:
                        if all_occs[i+1].rank == 2:
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
            rrule_params.setdefault(
                'until',
                datetime.datetime.now()+relativedelta(years=+5))

        if 'dtstart' in rrule_params:
            if isinstance(rrule_params['dtstart'], datetime.date):
                rrule_params['dtstart'] += relativedelta(
                    hours=self.start_hour,
                    minutes=self.start_minute)
        if 'until' in rrule_params:
            if isinstance(rrule_params['until'], datetime.date):
                rrule_params['until'] += relativedelta(
                    hours=self.start_hour,
                    minutes=self.start_minute)
        self.set.rrule(rrule.rrule(**rrule_params))
        self._recalculate_occurences()
        self.rules.append({'type': 'add',
                           'label': label,
                           'rule': rrule_params})
        return self

    def exclude_rule(self, label="", **rrule_params):
        """exclude a recuring rrule to this Session

        see :py:meth:`schedule.Session.add_rule` for more explanation

        """
        rrule_params.setdefault('freq', rrule.DAILY)
        rrule_params.setdefault('cache', True)

        if 'count' not in rrule_params and 'until' not in rrule_params:
            rrule_params.setdefault(
                'until',
                datetime.datetime.now()+relativedelta(years=+5))

        if 'dtstart' in rrule_params:
            if isinstance(rrule_params['dtstart'], datetime.date):
                rrule_params['dtstart'] += relativedelta(
                    hours=self.start_hour,
                    minutes=self.start_minute)
        if 'until' in rrule_params:
            if isinstance(rrule_params['until'], datetime.date):
                rrule_params['until'] += relativedelta(
                    hours=self.start_hour,
                    minutes=self.start_minute)

        self.set.exrule(rrule.rrule(**rrule_params))
        self._recalculate_occurences()
        self.rules.append({'type': 'exclude',
                           'label': label,
                           'rule': rrule_params})
        return self

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
            new_occurences.append(Interval(
                occ,
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
          :CalculatedSession: a :py:class:`schedule.CalculatedSession`
            containing all the Interval within start and end

        """
        occurences = []
        for occ in list(self.set.between(start, end, inclusive)):
            occurences.append(Interval(
                occ,
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
            return Interval(previous,
                            previous+relativedelta(minutes=+self.duration))


class CalculatedSession(Session):
    """a CalculatedSession is the result of manipulation of one or more
    sessions and when a Session can not be defined by rules anymore

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
    result of some merging / extraction of differents Session, Intervals
    or dates

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
        elif (type(const_list) == Session or
              type(const_list) == CalculatedSession):
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
            "'CalculatedSession' object does not implement "
            "'_recalculate_occurences'")

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
