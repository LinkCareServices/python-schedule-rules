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
Test for Session class
"""

__authors__ = [
    # alphabetical order by last name
    'Thomas Chiroux', ]

import unittest
import datetime

# dependancies imports
from dateutil.relativedelta import relativedelta
from dateutil import rrule

# import here the module / classes to be tested
from srules import Session, Interval, CalculatedSession


class TestSession(unittest.TestCase):
    def setUp(self):
        self.ses_p = Session("Test", duration=60*8,
                             start_hour=13, start_minute=30)
        self.ses_p.add_rule("1er jour des 6",
                            freq=rrule.DAILY,
                            dtstart=datetime.date(2011, 8, 20),
                            interval=6,
                            until=datetime.date(2021, 8, 30))
        self.ses_p.add_rule(
            "2eme jour des 6",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 8, 20) + relativedelta(days=+1),
            interval=6,
            until=datetime.date(2021, 8, 30))
        self.ses_p.add_rule(
            "3eme jour des 6",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 8, 20) + relativedelta(days=+2),
            interval=6,
            until=datetime.date(2021, 8, 30))


class TestSessionSimpleRule1(TestSession):
    def setUp(self):
        TestSession.setUp(self)

    def runTest(self):
        ses = Session("Test", 60*7)
        ses.add_rule("1er jour des 6",
                     freq=rrule.DAILY,
                     dtstart=datetime.date(2011, 8, 20),
                     interval=6,
                     until=datetime.date(2021, 8, 30))
        result_expected = 256620
        result = ses.total_duration
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)


class TestSessionSimpleRule2(TestSession):
    def setUp(self):
        TestSession.setUp(self)

    def runTest(self):
        ses = Session("Test", 60*9)
        ses.add_rule(
            "2eme jour des 3",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 8, 20) + relativedelta(days=+1),
            interval=3,
            until=datetime.date(2021, 8, 30))
        result_expected = 659340
        result = ses.total_duration
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)


class TestSessionAddRule1(TestSession):
    def setUp(self):
        TestSession.setUp(self)

    def runTest(self):
        ses = Session("Test", 60*8)
        ses.add_rule(
            "1er jour des 6",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 8, 20),
            interval=6,
            until=datetime.date(2021, 8, 30))
        ses.add_rule(
            "2eme jour des 3",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 8, 20) + relativedelta(days=+1),
            interval=3,
            until=datetime.date(2021, 8, 30))
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
                     dtstart=datetime.date(2011, 8, 20),
                     interval=6,
                     until=datetime.date(2021, 8, 30))
        ses.add_rule(
            "2eme jour des 6",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 8, 20) + relativedelta(days=+1),
            interval=6,
            until=datetime.date(2021, 8, 30))
        ses.add_rule(
            "3eme jour des 6",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 8, 20) + relativedelta(days=+2),
            interval=6,
            until=datetime.date(2021, 8, 30))
        result_expected = 879840
        result = ses.total_duration
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)


class TestSessionInPeriod(TestSession):
    def setUp(self):
        TestSession.setUp(self)

    def test_1(self):
        result_expected = True
        result = datetime.datetime(2011, 9, 27, 15, 40) in self.ses_p
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

    def test_2(self):
        result_expected = Interval(datetime.datetime(2011, 9, 27, 13, 30),
                                   datetime.datetime(2011, 9, 27, 21, 30))
        result = self.ses_p.__contains__(
            datetime.datetime(2011, 9, 27, 15, 40),
            True)
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

    def test_3(self):
        result_expected = False
        result = datetime.datetime(2011, 9, 28, 15, 40) in self.ses_p
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

    def test_4(self):
        result_expected = None
        result = self.ses_p.__contains__(
            datetime.datetime(2011, 9, 28, 15, 40),
            True)
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)


class TestSessionNextinterval1(TestSession):
    def setUp(self):
        TestSession.setUp(self)

    def test_1(self):
        result_expected = Interval(datetime.datetime(2011, 9, 27, 13, 30),
                                   datetime.datetime(2011, 9, 27, 21, 30))
        result = self.ses_p.next_interval(
            datetime.datetime(2011, 9, 27, 15, 40))
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

    def test_2(self):
        result_expected = Interval(datetime.datetime(2011, 10, 1, 13, 30),
                                   datetime.datetime(2011, 10, 1, 21, 30))
        result = self.ses_p.next_interval(
            datetime.datetime(2011, 9, 27, 15, 40),
            False)
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

    def test_3(self):
        result_expected = Interval(datetime.datetime(2011, 10, 1, 13, 30),
                                   datetime.datetime(2011, 10, 1, 21, 30))
        result = self.ses_p.next_interval(
            datetime.datetime(2011, 9, 28, 15, 40))
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)


class TestSessionPrevinterval1(TestSession):
    def setUp(self):
        TestSession.setUp(self)

    def test_1(self):
        result_expected = Interval(datetime.datetime(2011, 9, 27, 13, 30),
                                   datetime.datetime(2011, 9, 27, 21, 30))
        result = self.ses_p.prev_interval(
            datetime.datetime(2011, 9, 27, 15, 40))
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

    def test_2(self):
        result_expected = Interval(datetime.datetime(2011, 9, 26, 13, 30),
                                   datetime.datetime(2011, 9, 26, 21, 30))
        result = self.ses_p.prev_interval(
            datetime.datetime(2011, 9, 27, 15, 40),
            False)
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)

    def test_3(self):
        result_expected = Interval(datetime.datetime(2011, 9, 27, 13, 30),
                                   datetime.datetime(2011, 9, 27, 21, 30))
        result = self.ses_p.prev_interval(
            datetime.datetime(2011, 9, 28, 15, 40))
        assert result == result_expected, "bad result ? got %s instead of %s" % (result, result_expected)


class TestSessionAdd1(TestSession):
    def setUp(self):
        TestSession.setUp(self)
        self.ses_p2 = Session("Test2", duration=60*3,
                              start_hour=11, start_minute=30)
        self.ses_p2.add_rule(
            "Tous les jours",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 8, 30),
            interval=1,
            until=datetime.date(2015, 8, 30))
        self.result_list = self.ses_p + self.ses_p2

    def test_1(self):
        assert datetime.datetime(2011, 8, 20, 15, 00) in self.result_list

    def test_2(self):
        assert datetime.datetime(2011, 8, 20, 11, 00) not in self.result_list

    def test_3(self):
        assert datetime.datetime(2011, 8, 23, 15, 00) not in self.result_list

    def test_4(self):
        assert datetime.datetime(2011, 8, 30, 12, 00) in self.result_list

    def test_5(self):
        assert datetime.datetime(2011, 8, 30, 15, 00) not in self.result_list

    def test_6(self):
        assert datetime.datetime(2011, 9, 1, 15, 00) in self.result_list

    def test_7(self):
        assert datetime.datetime(2015, 8, 30, 12, 00) in self.result_list

    def test_8(self):
        assert datetime.datetime(2015, 8, 30, 15, 00) in self.result_list

    def test_9(self):
        assert datetime.datetime(2021, 8, 29, 15, 00) in self.result_list

    def test_10(self):
        assert datetime.datetime(2021, 8, 29, 12, 00) not in self.result_list


class TestSessionAdd2(TestSession):
    def setUp(self):
        TestSession.setUp(self)
        self.ses_p2 = Session("Test2", duration=60*3,
                              start_hour=11, start_minute=30)
        self.ses_p2.add_rule(
            "Tous les jours",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 8, 15),
            interval=1,
            until=datetime.date(2012, 11, 30))
        self.result_list = self.ses_p + self.ses_p2

    def test_1(self):
        assert datetime.datetime(2011, 8, 15, 15, 00) not in self.result_list

    def test_2(self):
        assert datetime.datetime(2011, 8, 15, 11, 45) in self.result_list

    def test_3(self):
        assert datetime.datetime(2011, 8, 20, 15, 00) in self.result_list

    def test_4(self):
        assert datetime.datetime(2011, 8, 20, 11, 00) not in self.result_list

    def test_5(self):
        assert datetime.datetime(2011, 8, 23, 15, 00) not in self.result_list

    def test_6(self):
        assert datetime.datetime(2011, 8, 30, 12, 00) in self.result_list

    def test_7(self):
        assert datetime.datetime(2011, 8, 30, 15, 00) not in self.result_list

    def test_8(self):
        assert datetime.datetime(2011, 9, 1, 15, 00) in self.result_list

    def test_9(self):
        assert datetime.datetime(2012, 11, 30, 12, 00) in self.result_list

    def test_10(self):
        assert datetime.datetime(2012, 11, 30, 15, 00) in self.result_list

    def test_11(self):
        assert datetime.datetime(2021, 8, 29, 15, 00) in self.result_list

    def test_12(self):
        assert datetime.datetime(2021, 8, 29, 12, 00) not in self.result_list


class TestSessionAdd3(TestSession):
    def setUp(self):
        TestSession.setUp(self)
        self.ses_p2 = Session("Test2", duration=60*3,
                              start_hour=11, start_minute=30)
        self.ses_p2.add_rule(
            "Tous les jours",
            freq=rrule.DAILY,
            dtstart=datetime.date(2021, 8, 15),
            interval=1,
            until=datetime.date(2022, 6, 30))
        self.result_list = self.ses_p + self.ses_p2

    def test_1(self):
        assert datetime.datetime(2011, 8, 20, 15, 00) in self.result_list

    def test_2(self):
        assert datetime.datetime(2011, 8, 20, 11, 00) not in self.result_list

    def test_3(self):
        assert datetime.datetime(2011, 8, 20, 15, 00) in self.result_list

    def test_4(self):
        assert datetime.datetime(2011, 8, 23, 15, 00) not in self.result_list

    def test_5(self):
        assert datetime.datetime(2011, 8, 30, 12, 00) not in self.result_list

    def test_6(self):
        assert datetime.datetime(2011, 8, 30, 15, 00) not in self.result_list

    def test_7(self):
        assert datetime.datetime(2011, 9, 1, 15, 00) in self.result_list

    def test_8(self):
        assert datetime.datetime(2021, 8, 29, 15, 00) in self.result_list

    def test_9(self):
        assert datetime.datetime(2022, 6, 30, 11, 55) in self.result_list

    def test_10(self):
        assert datetime.datetime(2022, 6, 30, 11, 00) not in self.result_list


class TestSessionAddSpecialCases(TestSession):
    def setUp(self):
        TestSession.setUp(self)
        self.ses_p2 = Session("Test2", duration=60*3,
                              start_hour=11, start_minute=30)
        self.ses_p2.add_rule(
            "Tous les jours",
            freq=rrule.DAILY,
            dtstart=datetime.date(2021, 8, 15),
            interval=1,
            until=datetime.date(2022, 6, 30))
        self.result_list = self.ses_p + self.ses_p2

    def test_1(self):
        assert self.ses_p + None == self.ses_p

    def test_2(self):
        assert self.ses_p + self.ses_p == self.ses_p


class TestSessionSub1(TestSession):
    def setUp(self):
        TestSession.setUp(self)
        self.ses_p2 = Session("Test2", duration=60*3,
                              start_hour=11, start_minute=30)
        self.ses_p2.add_rule(
            "Tous les jours",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 8, 30),
            interval=1,
            until=datetime.date(2015, 8, 30))
        self.result_list = self.ses_p - self.ses_p2

    def test_1(self):
        assert datetime.datetime(2011, 8, 20, 15, 00) in self.result_list

    def test_2(self):
        assert datetime.datetime(2011, 8, 20, 11, 00) not in self.result_list

    def test_3(self):
        assert datetime.datetime(2011, 8, 23, 15, 00) not in self.result_list

    def test_4(self):
        assert datetime.datetime(2011, 8, 30, 13, 45) not in self.result_list

    def test_5(self):
        assert datetime.datetime(2011, 9, 1, 13, 45) not in self.result_list

    def test_6(self):
        assert datetime.datetime(2011, 9, 1, 15, 00) in self.result_list

    def test_7(self):
        assert datetime.datetime(2015, 8, 30, 13, 45) not in self.result_list

    def test_8(self):
        assert datetime.datetime(2015, 8, 30, 15, 00) in self.result_list

    def test_9(self):
        assert datetime.datetime(2021, 8, 29, 15, 00) in self.result_list

    def test_10(self):
        assert datetime.datetime(2021, 8, 29, 12, 00) not in self.result_list


class TestSessionSub2(TestSession):
    def setUp(self):
        TestSession.setUp(self)
        self.ses_p2 = Session("Test2", duration=60*3,
                              start_hour=11, start_minute=30)
        self.ses_p2.add_rule(
            "Tous les jours",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 8, 15),
            interval=1,
            until=datetime.date(2012, 11, 30))
        self.result_list = self.ses_p - self.ses_p2

    def test_1(self):
        assert datetime.datetime(2011, 8, 15, 15, 00) not in self.result_list

    def test_2(self):
        assert datetime.datetime(2011, 8, 15, 11, 45) not in self.result_list

    def test_3(self):
        assert datetime.datetime(2011, 8, 20, 15, 00) in self.result_list

    def test_4(self):
        assert datetime.datetime(2011, 8, 20, 13, 45) not in self.result_list

    def test_5(self):
        assert datetime.datetime(2011, 8, 23, 15, 00) not in self.result_list

    def test_6(self):
        assert datetime.datetime(2011, 8, 30, 12, 00) not in self.result_list

    def test_7(self):
        assert datetime.datetime(2011, 8, 30, 15, 00) not in self.result_list

    def test_8(self):
        assert datetime.datetime(2011, 9, 1, 15, 00) in self.result_list

    def test_8bis(self):
        assert datetime.datetime(2011, 9, 1, 13, 45) not in self.result_list

    def test_9(self):
        assert datetime.datetime(2012, 11, 30, 13, 45) not in self.result_list

    def test_10(self):
        assert datetime.datetime(2012, 11, 30, 15, 00) in self.result_list

    def test_11(self):
        assert datetime.datetime(2021, 8, 29, 15, 00) in self.result_list

    def test_12(self):
        assert datetime.datetime(2021, 8, 29, 12, 00) not in self.result_list


class TestSessionSub3(TestSession):
    def setUp(self):
        TestSession.setUp(self)
        self.ses_p2 = Session("Test2", duration=60*3,
                              start_hour=11, start_minute=30)
        self.ses_p2.add_rule(
            "Tous les jours",
            freq=rrule.DAILY,
            dtstart=datetime.date(2021, 8, 15),
            interval=1,
            until=datetime.date(2022, 6, 30))
        self.result_list = self.ses_p - self.ses_p2

    def test_1(self):
        assert datetime.datetime(2011, 8, 20, 13, 45) in self.result_list

    def test_2(self):
        assert datetime.datetime(2011, 8, 20, 11, 00) not in self.result_list

    def test_3(self):
        assert datetime.datetime(2011, 8, 20, 13, 45) in self.result_list

    def test_4(self):
        assert datetime.datetime(2011, 8, 23, 15, 00) not in self.result_list

    def test_5(self):
        assert datetime.datetime(2011, 8, 30, 12, 00) not in self.result_list

    def test_6(self):
        assert datetime.datetime(2011, 8, 30, 15, 00) not in self.result_list

    def test_7(self):
        assert datetime.datetime(2011, 9, 1, 13, 45) in self.result_list

    def test_8(self):
        assert datetime.datetime(2021, 8, 15, 15, 00) in self.result_list

    def test_9(self):
        assert datetime.datetime(2021, 8, 15, 13, 45) not in self.result_list

    def test_10(self):
        assert datetime.datetime(2021, 8, 29, 15, 00) in self.result_list

    def test_11(self):
        assert datetime.datetime(2021, 8, 29, 13, 45) not in self.result_list

    def test_12(self):
        assert datetime.datetime(2022, 6, 30, 13, 45) not in self.result_list

    def test_13(self):
        assert datetime.datetime(2022, 6, 30, 11, 00) not in self.result_list


class TestSessionSub4(TestSession):
    """In this test, the B interval is within A, so sub should result in
    spltting this results in two intervals"""
    def setUp(self):
        TestSession.setUp(self)
        self.ses_p2 = Session("Test2", duration=37,
                              start_hour=15, start_minute=30)
        self.ses_p2.add_rule(
            "Tous les jours",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 9, 15),
            interval=1,
            until=datetime.date(2011, 12, 30))
        self.result_list = self.ses_p - self.ses_p2

    def test_1(self):
        assert datetime.datetime(2011, 9, 15, 13, 45) in self.result_list

    def test_2(self):
        assert datetime.datetime(2011, 9, 15, 15, 45) not in self.result_list

    def test_3(self):
        assert datetime.datetime(2011, 9, 15, 16, 45) in self.result_list


class TestSessionSub5(TestSession):
    """In this test, the intervals are completely disjoints,
    so a - b == a and b - a == b
    """
    def setUp(self):
        TestSession.setUp(self)
        self.ses_p2 = Session("Test2", duration=32,
                              start_hour=11, start_minute=00)
        self.ses_p2.add_rule(
            "Tous les jours",
            freq=rrule.DAILY,
            dtstart=datetime.date(2011, 9, 15),
            interval=1,
            until=datetime.date(2011, 12, 30))
        self.result_list = self.ses_p - self.ses_p2

    def test_1(self):
        assert self.result_list == self.ses_p

    def test_2(self):
        result2 = self.ses_p2 - self.ses_p
        assert result2 == self.ses_p2


class TestSessionSubSpecialCases(TestSession):
    def setUp(self):
        TestSession.setUp(self)
        self.ses_p2 = Session("Test2", duration=60*3,
                              start_hour=11, start_minute=30)
        self.ses_p2.add_rule(
            "Tous les jours",
            freq=rrule.DAILY,
            dtstart=datetime.date(2021, 8, 15),
            interval=1,
            until=datetime.date(2022, 6, 30))
        self.result_list = self.ses_p + self.ses_p2

    def test_1(self):
        assert self.ses_p - None == self.ses_p

    def test_2(self):
        assert len(self.ses_p - self.ses_p) == 0

    #def test_3(self):
    #  assert None - self.ses_p == None


if __name__ == "__main__":
    import sys
    suite = unittest.findTestCases(sys.modules[__name__])
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestSessionSub5)
    unittest.TextTestRunner(verbosity=2).run(suite)
