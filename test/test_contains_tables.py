#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-17
# -*- coding: utf-8 -*-

"""
ContainsTables tests
"""

import sys
sys.path.append('code')

import pdftables

from nose.tools import assert_equals


def test_it_finds_no_tables_in_a_pdf_with_no_tables():
    fh = open('fixtures/sample_data/m27-dexpeg2-polymer.pdf', 'rb')
    assert_equals(
        [False, False, False, False, False, False, False, False],
        pdftables.contains_tables(fh))


def test_it_finds_tables_on_all_pages_AlmondBoard():
    fh = open('fixtures/sample_data/2012.01.PosRpt.pdf', 'rb')
    assert_equals(
        [True, True, True, True, True, True, True],
        pdftables.contains_tables(fh))


def test_it_finds_tables_on_some_pages_CONAB():
    fh = open('fixtures/sample_data/13_06_12_10_36_58_boletim_ingles_junho_2013.pdf', 'rb')
    TestList = [False]*32
    TestList[5:8] = [True]*3
    TestList[9:11] = [True]*2
    TestList[12] = True
    TestList[14] = True
    TestList[16:18] = [True]*2
    TestList[19:24] = [True]*5
    TestList[25:30] = [True]*5

    assert_equals(pdftables.contains_tables(fh), TestList)
