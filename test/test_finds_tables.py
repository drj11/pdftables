#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-17
# -*- coding: utf-8 -*-

"""
Finds tables tests
"""

import sys
sys.path.append('code')

import pdftables

from nose.tools import assert_equals

def test_atomise_does_not_disrupt_table_finding():
    fh = open('fixtures/sample_data/13_06_12_10_36_58_boletim_ingles_junho_2013.pdf', 'rb')
    pdf_page = pdftables.get_pdf_page(fh, 4)
    table1, _ = pdftables.page_to_tables(pdf_page, atomise=True, extend_y=False)
    table2, _ = pdftables.page_to_tables(pdf_page, atomise=False, extend_y=False)
    
    
    assert_equals(table1, table2)
