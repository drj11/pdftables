#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-17
# -*- coding: utf-8 -*-

"""
getTablesTests
"""

import sys
sys.path.append('code')

from pdftables import get_pdf_page, page_to_tables, TableDiagnosticData

from nose.tools import *

def test_it_exits_gracefully_when_no_tables_found():
    fh = open('fixtures/sample_data/13_06_12_10_36_58_boletim_ingles_junho_2013.pdf', 'rb')
    pdf_page = get_pdf_page(fh, 5)
    table, table_diagnostic_data = page_to_tables(pdf_page)
    
    assert_equals([],table)
    assert(isinstance(table_diagnostic_data, TableDiagnosticData))
                                                  
def test_it_copes_with_CONAB_p8():
    fh = open('fixtures/sample_data/13_06_12_10_36_58_boletim_ingles_junho_2013.pdf', 'rb')
    pdf_page = get_pdf_page(fh, 8)
    table, _ = page_to_tables(pdf_page, atomise=True)
    
    
def test_it_can_use_hints_AlmondBoard_p1():
    fh = open('fixtures/sample_data/2012.01.PosRpt.pdf', 'rb')
    pdf_page = get_pdf_page(fh, 1)
    table, _ = page_to_tables(pdf_page, hints=[u"% Change", u"Uncommited"])
    assert_equals(
    [[u'', u'Million Lbs.', u'Kernel Wt.', u'Kernel Wt.', u'% Change'], 
     [u'1.  Carryin August 1, 2011', u'254.0', u'253,959,411', u'321,255,129', u'-20.95%'], 
     [u'2.  Crop Receipts to Date', u'1,950.0', u'1,914,471,575', u'1,548,685,417', u'23.62%'], 
     [u'3.  [3% Loss and Exempt]', u'58.5', u'57,434,147)(', u'46,460,563()', u''], 
     [u'4.  New Crop Marketable (2-3)', u'1,891.5', u'1,857,037,428', u'1,502,224,854', u'23.62%'], 
     [u'5.  [Reserve]', u'n/a', u'0', u'0', u''], 
     [u'6.  Total Supply (1+4-5)', u'2,145.5', u'2,110,996,839', u'1,823,479,983', u'15.77%'], 
     [u'Shipments by Handlers7.  Domestic', u'555.0', u'265,796,698', u'255,785,794', u'3.91%'], 
     [u'8.  Export', u'1,295.0', u'755,447,255', u'664,175,807', u'13.74%'], 
     [u'9.  Total Shipments', u'1,850.0', u'1,021,243,953', u'919,961,601', u'11.01%'], 
     [u'10.  Forecasted Carryout', u'295.5', u'', u'', u''], 
     [u'11.  Computed Inventory (6-9)', u'', u'1,089,752,886', u'903,518,382', u'20.61%'], 
     [u'Commitments (sold, not delivered)**12.  Domestic', u'', u'214,522,238', u'187,492,263', u'14.42%'], 
     [u'13.  Export', u'', u'226,349,446', u'155,042,764', u'45.99%'], 
     [u'14.  Total Commited Shipments', u'', u'440,871,684', u'342,535,027', u'28.71%'], 
     [u'15.  Uncommited Inventory (11-14)', u'', u'648,881,202', u'560,983,355', u'15.67%']]
    , table)

def test_it_can_use_one_hint_argentina_by_size():
    fh = open('fixtures/sample_data/argentina_diputados_voting_record.pdf', 'rb')
    pdf_page = get_pdf_page(fh, 1)
    table1, _ = page_to_tables(pdf_page, hints=['Apellido',''])
    #table1,_ = getTable(fh, 2)
    assert_equals(32, len(table1))
    assert_equals(4, len(table1[0]))

def test_it_returns_the_AlmondBoard_p2_table_by_size():
    fh = open('fixtures/sample_data/2012.01.PosRpt.pdf', 'rb')
    pdf_page = get_pdf_page(fh, 2)
    table1, _ = page_to_tables(pdf_page)
    #table1, _ = getTable(fh, 2)
    assert_equals(78, len(table1))
    assert_equals(10, len(table1[0]))

def test_the_atomise_option_works_on_coceral_p1_by_size():
    fh = open('fixtures/sample_data/1359397366Final_Coceral grain estimate_2012_December.pdf', 'rb')
    pdf_page = get_pdf_page(fh, 1)
    table, _ = page_to_tables(pdf_page, atomise=True)
    #table1, _ = getTable(fh, 2)
    assert_equals(43, len(table))
    assert_equals(31, len(table[0]))

def test_it_does_not_crash_on_m30_p5():
    fh = open('fixtures/sample_data/m30-JDent36s15-20.pdf', 'rb')
    pdf_page = get_pdf_page(fh, 5)
    table, _ = page_to_tables(pdf_page)
    """Put this in for more aggressive test"""
    #assert_equals([u'5\n', u'0.75\n', u'0.84\n', u'0.92\n', u'0.94\n', u'evaluation of a novel liquid whitening gel containing 18%\n'],
    #              table[4])
def test_it_returns_the_AlmondBoard_p4_table():
    fh = open('fixtures/sample_data/2012.01.PosRpt.pdf', 'rb')
    pdf_page = get_pdf_page(fh, 4)
    table, _ = page_to_tables(pdf_page, extend_y=False)
    assert_equals(
    [[u'Variety Name', u'Total Receipts', u'Total Receipts', u'Total Inedibles', u'Receipts', u'% Rejects'], 
     [u'Aldrich', u'48,455,454', u'49,181,261', u'405,555', u'2.53%', u'0.82%'], 
     [u'Avalon', u'7,920,179', u'8,032,382', u'91,733', u'0.41%', u'1.14%'], 
     [u'Butte', u'151,830,761', u'150,799,510', u'1,054,567', u'7.93%', u'0.70%'], 
     [u'Butte/Padre', u'215,114,812', u'218,784,885', u'1,145,000', u'11.24%', u'0.52%'], 
     [u'Carmel', u'179,525,234', u'178,912,935', u'1,213,790', u'9.38%', u'0.68%'], 
     [u'Carrion', u'507,833', u'358,580', u'2,693', u'0.03%', u'0.75%'], 
     [u'Fritz', u'105,479,433', u'106,650,571', u'1,209,192', u'5.51%', u'1.13%'], 
     [u'Harvey', u'58,755', u'58,755', u'1,416', u'0.00%', u'2.41%'], 
     [u'Hashem', u'430,319', u'430,014', u'1,887', u'0.02%', u'0.44%'], 
     [u'Le Grand', u'0', u'0', u'0', u'0.00%', u'0.00%'], 
     [u'Livingston', u'7,985,535', u'7,926,910', u'186,238', u'0.42%', u'2.35%'], 
     [u'Marchini', u'363,887', u'391,965', u'3,675', u'0.02%', u'0.94%'], 
     [u'Merced', u'65,422', u'66,882', u'1,167', u'0.00%', u'1.74%'], 
     [u'Mission', u'19,097,034', u'18,851,071', u'110,323', u'1.00%', u'0.59%'], 
     [u'Mixed', u'36,358,011', u'36,926,337', u'952,264', u'1.90%', u'2.58%'], 
     [u'Mono', u'757,637', u'689,552', u'6,785', u'0.04%', u'0.98%'], 
     [u'Monterey', u'220,713,436', u'212,746,409', u'2,293,892', u'11.53%', u'1.08%'], 
     [u'Morley', u'822,529', u'825,738', u'6,264', u'0.04%', u'0.76%'], 
     [u'N43', u'156,488', u'85,832', u'340', u'0.01%', u'0.40%'], 
     [u'Neplus', u'1,279,599', u'1,237,532', u'17,388', u'0.07%', u'1.41%'], 
     [u'Nonpareil', u'741,809,844', u'727,286,104', u'5,121,465', u'38.75%', u'0.70%'], 
     [u'Padre', u'62,905,358', u'62,417,565', u'193,168', u'3.29%', u'0.31%'], 
     [u'Peerless', u'5,113,472', u'5,101,245', u'20,792', u'0.27%', u'0.41%'], 
     [u'Price', u'25,312,529', u'25,124,463', u'143,983', u'1.32%', u'0.57%'], 
     [u'Ruby', u'4,163,237', u'4,057,470', u'35,718', u'0.22%', u'0.88%'], 
     [u'Sauret', u'55,864', u'55,864', u'517', u'0.00%', u'0.93%'], 
     [u'Savana', u'389,317', u'390,585', u'2,049', u'0.02%', u'0.52%'], 
     [u'Sonora', u'31,832,025', u'33,184,703', u'387,848', u'1.66%', u'1.17%'], 
     [u'Thompson', u'491,026', u'487,926', u'8,382', u'0.03%', u'1.72%'], 
     [u'Tokyo', u'783,494', u'794,699', u'4,511', u'0.04%', u'0.57%'], 
     [u'Winters', u'5,780,183', u'5,756,167', u'46,211', u'0.30%', u'0.80%'], 
     [u'Wood Colony', u'37,458,735', u'36,331,907', u'189,967', u'1.96%', u'0.52%'], 
     [u'Major Varieties Sub Total:', u'1,913,017,442', u'1,893,945,819', u'14,858,780', u'99.92%', u'0.78%'], 
     [u'Minor Varieties Total:', u'1,454,133', u'1,480,800', u'34,997', u'0.08%', u'2.36%'], 
     [u'Grand Total All Varieties', u'1,914,471,575', u'1,895,426,619', u'14,893,777', u'100.00%', u'0.79%']]
    , table
    )

