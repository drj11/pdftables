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
    """
    page_number is 1-indexed, as defined in the PDF format
    table_number is 1-indexed
    """
    fh = open('fixtures/sample_data/AnimalExampleTables.pdf', 'rb')
    result = get_tables(fh)
    assert_equals(result[0].total_pages, 4)
    assert_equals(result[0].page_number, 2)
    assert_equals(result[1].total_pages, 4)
    assert_equals(result[1].page_number, 3)
    assert_equals(result[2].total_pages, 4)
    assert_equals(result[2].page_number, 4)

def test_it_includes_table_numbers():
    fh = open('fixtures/sample_data/AnimalExampleTables.pdf', 'rb')
    result = get_tables(fh)
    assert_equals(result[0].table_number_on_page, 1)
    assert_equals(result[0].total_tables_on_page, 1)

