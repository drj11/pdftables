#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-17
# -*- coding: utf-8 -*-

"""
getTablesTests
"""

import sys
sys.path.append('code')

from pdftables import get_pdf_page, page_to_tables

from nose.tools import *

def test_it_can_use_hints_AlmondBoard_p1():
    fh = open('fixtures/sample_data/2012.01.PosRpt.pdf', 'rb')
    pdf_page = get_pdf_page(fh, 1)
    table, _ = page_to_tables(pdf_page, hints=[u"% Change", u"Uncommited"])
    assert_equals(
    [['', u'Million Lbs.', u'Kernel Wt.', u'Kernel Wt.', u'% Change'],
     [u'1.  Carryin August 1, 2011', u'254.0', u'253,959,411', u'321,255,129', u'-20.95%'],
     [u'2.  Crop Receipts to Date', u'1,950.0', u'1,914,471,575', u'1,548,685,417', u'23.62%'],
     [u'3.  [3% Loss and Exempt]', u'58.5', u'57,434,147)(', u'46,460,563()', ''],
     [u'4.  New Crop Marketable (2-3)', u'1,891.5', u'1,857,037,428', u'1,502,224,854', u'23.62%'],
     [u'5.  [Reserve]', u'n/a', u'0', u'0', ''],
     [u'6.  Total Supply (1+4-5)', u'2,145.5', u'2,110,996,839', u'1,823,479,983', u'15.77%'],
     [u'7.  Domestic', u'555.0', u'265,796,698', u'255,785,794', u'3.91%'],
     [u'8.  Export', u'1,295.0', u'755,447,255', u'664,175,807', u'13.74%'],
     [u'9.  Total Shipments', u'1,850.0', u'1,021,243,953', u'919,961,601', u'11.01%'],
     [u'10.  Forecasted Carryout', u'295.5', '', '', ''],
     [u'11.  Computed Inventory (6-9)', '', u'1,089,752,886', u'903,518,382', u'20.61%'],
     [u'12.  Domestic', '', u'214,522,238', u'187,492,263', u'14.42%'],
     [u'13.  Export', '', u'226,349,446', u'155,042,764', u'45.99%'],
     [u'14.  Total Commited Shipments', '', u'440,871,684', u'342,535,027', u'28.71%'],
     [u'15.  Uncommited Inventory (11-14)', '', u'648,881,202', u'560,983,355', u'15.67%']]
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
    assert_equals(46, len(table))
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
    [['Variety Name', 'Total ReceiptsTotal Receipts', 'Total Inedibles', '', 'Receipts', '% Rejects'],
     ['Aldrich', '48,455,454', '49,181,261', '405,555', '2.53%', '0.82%'],
     ['Avalon', '7,920,179', '8,032,382', '91,733', '0.41%', '1.14%'],
     ['Butte', '151,830,761', '150,799,510', '1,054,567', '7.93%', '0.70%'],
     ['Butte/Padre', '215,114,812', '218,784,885', '1,145,000', '11.24%', '0.52%'],
     ['Carmel', '179,525,234', '178,912,935', '1,213,790', '9.38%', '0.68%'],
     ['Carrion', '507,833', '358,580', '2,693', '0.03%', '0.75%'],
     ['Fritz', '105,479,433', '106,650,571', '1,209,192', '5.51%', '1.13%'],
     ['Harvey', '58,755', '58,755', '1,416', '0.00%', '2.41%'],
     ['Hashem', '430,319', '430,014', '1,887', '0.02%', '0.44%'],
     ['Le Grand', '0', '0', '0', '0.00%', '0.00%'],
     ['Livingston', '7,985,535', '7,926,910', '186,238', '0.42%', '2.35%'],
     ['Marchini', '363,887', '391,965', '3,675', '0.02%', '0.94%'],
     ['Merced', '65,422', '66,882', '1,167', '0.00%', '1.74%'],
     ['Mission', '19,097,034', '18,851,071', '110,323', '1.00%', '0.59%'],
     ['Mixed', '36,358,011', '36,926,337', '952,264', '1.90%', '2.58%'],
     ['Mono', '757,637', '689,552', '6,785', '0.04%', '0.98%'],
     ['Monterey', '220,713,436', '212,746,409', '2,293,892', '11.53%', '1.08%'],
     ['Morley', '822,529', '825,738', '6,264', '0.04%', '0.76%'],
     ['N43', '156,488', '85,832', '340', '0.01%', '0.40%'],
     ['Neplus', '1,279,599', '1,237,532', '17,388', '0.07%', '1.41%'],
     ['Nonpareil', '741,809,844', '727,286,104', '5,121,465', '38.75%', '0.70%'],
     ['Padre', '62,905,358', '62,417,565', '193,168', '3.29%', '0.31%'],
     ['Peerless', '5,113,472', '5,101,245', '20,792', '0.27%', '0.41%'],
     ['Price', '25,312,529', '25,124,463', '143,983', '1.32%', '0.57%'],
     ['Ruby', '4,163,237', '4,057,470', '35,718', '0.22%', '0.88%'],
     ['Sauret', '55,864', '55,864', '517', '0.00%', '0.93%'],
     ['Savana', '389,317', '390,585', '2,049', '0.02%', '0.52%'],
     ['Sonora', '31,832,025', '33,184,703', '387,848', '1.66%', '1.17%'],
     ['Thompson', '491,026', '487,926', '8,382', '0.03%', '1.72%'],
     ['Tokyo', '783,494', '794,699', '4,511', '0.04%', '0.57%'],
     ['Winters', '5,780,183', '5,756,167', '46,211', '0.30%', '0.80%'],
     ['Wood Colony', '37,458,735', '36,331,907', '189,967', '1.96%', '0.52%'],
     ['Major Varieties Sub Total:', '1,913,017,442', '1,893,945,819', '14,858,780', '99.92%', '0.78%'],
     ['Minor Varieties Total:', '1,454,133', '1,480,800', '34,997', '0.08%', '2.36%'],
     ['Grand Total All Varieties', '1,914,471,575', '1,895,426,619', '14,893,777', '100.00%', '0.79%']]
    , table
    )

