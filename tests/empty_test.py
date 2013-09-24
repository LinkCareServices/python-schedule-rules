#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2011 Link Care Services
#
"""
Test for XXXXX class
"""

__authors__ = [
    # alphabetical order by last name
    'Thomas Chiroux', ]

import unittest
# import here the module / classes to be tested
import srules


class TestXXXXXXXXXX(unittest.TestCase):
    def setUp(self):
        pass


class TestXXXXXXXXXX(TestXXXXXXX):
    def runTest(self):
        pass


if __name__ == "__main__":
    import sys
    suite = unittest.findTestCases(sys.modules[__name__])
    #suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
