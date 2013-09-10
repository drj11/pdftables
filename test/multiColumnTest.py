#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-24
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
"""
These are tests for multi-column functionality
"""

import sys
sys.path.append('code')

import pdftables

from nose.tools import *

# SelectedPDF = "bo_page24.pdf" # 1 page Multi-column text and tables mixed on the page
# SelectedPDF = "COPAMONTHLYMay2013.pdf" # 1 page
# SelectedPDF = "m29-JDent36s2-7.pdf" # One table, two column text, equations may cause problems?
# pagenumber = 4 # Works OK but some - signs are missed and we need to use extendy


def _test_multicolumn_bo_page24_4col_spanning_table():
    fh = open('fixture/bo_page24.pdf','rb')
    pdfPage = pdftables.getPDFPage(fh, 1)
    ncols, column_bounds = pdftables.multiColumnDetect(pdfPage)
    assert_equals(4,ncols)

def _test_multicolumn_COPAMONTHLY_2col_limited_text():
    fh = open('fixture/COPAMONTHLYMay2013.pdf','rb')
    pdfPage = pdftables.getPDFPage(fh, 1)
    ncols, column_bounds = pdftables.multiColumnDetect(pdfPage)
    assert_equals(2,ncols)

def _test_multicolumn_m29_2col_spanning_table():
    fh = open('fixture/m29-JDent36s2-7.pdf','rb')
    pdfPage = pdftables.getPDFPage(fh, 4)
    ncols, column_bounds = pdftables.multiColumnDetect(pdfPage)
    assert_equals(2,ncols)
    
def _test_it_notices_when_there_is_one_column_of_text():

    fh = open('fixture/13_06_12_10_36_58_boletim_ingles_junho_2013.pdf','rb')
    pdfPage = pdftables.getPDFPage(fh, 4)
    ncols, column_bounds = pdftables.multiColumnDetect(pdfPage)
    assert_equals(1,ncols)
    
def _test_it_notices_when_there_are_no_text_columns():
    fh = open('fixture/2012.01.PosRpt.pdf.pdf','rb')
    pdfPage = pdftables.getPDFPage(fh, 4)
    ncols, column_bounds = pdftables.multiColumnDetect(pdfPage)
    assert_equals(0,ncols)
    
