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

from fixtures import fixture

from nose.tools import assert_equals


def contains_tables(pdf):
    """
    contains_tables takes a pdf document and returns a boolean array of the
    length of the document which is true for pages which contains tables
    """
    return [pdftables.page_contains_tables(page) for page in pdf.get_pages()]


def test_it_finds_no_tables_in_a_pdf_with_no_tables():
    pdf = fixture('m27-dexpeg2-polymer.pdf')
    assert_equals(
        [False, False, False, False, False, False, False, False],
        contains_tables(pdf))


def test_it_finds_tables_on_all_pages_AlmondBoard():
    pdf = fixture('2012.01.PosRpt.pdf')
    assert_equals(
        [True, True, True, True, True, True, True],
        contains_tables(pdf))


def test_it_finds_tables_on_some_pages_CONAB():
    pdf = fixture('13_06_12_10_36_58_boletim_ingles_junho_2013.pdf')
    TestList = [False] * 32
    TestList[5:8] = [True] * 3
    TestList[9:11] = [True] * 2
    TestList[12] = True
    TestList[14] = True
    TestList[16:18] = [True] * 2
    TestList[19:24] = [True] * 5
    TestList[25:30] = [True] * 5

    assert_equals(contains_tables(pdf), TestList)
