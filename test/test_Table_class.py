#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-07-30
# -*- coding: utf-8 -*-

"""
Tests the Table class which contains metadata
"""
import sys
sys.path.append('code')

from pdftables import get_tables

from nose.tools import *

def test_it_includes_page_numbers():
    fh = open('fixtures/sample_data/AnimalExampleTables.pdf', 'rb')
    result = get_tables(fh)
    assert_equals(result[0].page_total, 4)
    assert_equals(result[0].page, 2)
    assert_equals(result[1].page_total, 4)
    assert_equals(result[1].page, 3)
    assert_equals(result[2].page_total, 4)
    assert_equals(result[2].page, 4)