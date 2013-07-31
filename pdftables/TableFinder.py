#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-14
# -*- coding: utf-8 -*-

"""
Code to find tables in PDF files
"""

import os
# import requests
import scraperwiki # pdftoxml does not work on Windows
import lxml.html
import glob
import matplotlib.pyplot as plt
import collections
from counter import Counter

# TODO - Use pdfminer
# TODO

def pdftoxml(filename,options):
    ConverterPath = unicode(r'C:\Users\Ian\BitBucketRepos\0939-AgraInforma\bin\pdftohtml.exe')
    directory = os.path.split(filename)[0]
    tmpxml = os.path.join(directory,"temph.xml")
    if tmpxml in os.listdir('.'):
        os.remove(tmpxml)
    cmd = '%s -xml %s "%s" %s' % (ConverterPath, options, filename, os.path.splitext(tmpxml)[0])

    os.system(cmd)

    f = open(tmpxml,'rb')
    content = f.read()
    f.close()

    return content

def processpage(page):
    left=[]
    width=[]
    top=[]
    right=[]
    for textchunk in (page is not None and page.xpath('text')):
        thisleft = int(textchunk.attrib.get('left'))
        thiswidth = int(textchunk.attrib.get('width'))
        left.append(thisleft)
        width.append(thiswidth)
        top.append(pageheight - int(textchunk.attrib.get('top')))
        right.append(thisleft + thiswidth)

    return pageheight,pagewidth,left,top,right

def plotpage(pageheight,pagewidth,pagenumber,SelectedPDF,left,top,right):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.axis('equal')
    ax1.plot([0,pagewidth,pagewidth,0,0],[0,0,pageheight,pageheight,0])
    ax1.scatter(left, top, s=10, c='b', marker="s")
    ax1.scatter(right, top, s=10, c='r', marker="o")
    fig.suptitle('%s : Page %d' % (SelectedPDF,pagenumber), fontsize=15)
    plt.show()
    return fig

PDF_TEST_FILES = unicode(r'C:\Users\Ian\BitBucketRepos\0939-AgraInforma\fixtures')

# PDFList = glob.glob(os.path.join(PDF_TEST_FILES,'*.pdf'))

# SelectedPDF = 6 # 6 = cit0613.pdf - table is actually an image

# r = requests.get(os.path.join(PDF_TEST_FILES,PDFList[SelectedPDF]))
# options = ""
# xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,PDFList[SelectedPDF]),options)

# xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,"cit0613.pdf"),options) # Works but first page is an image
# xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,"2012.01.PosRpt.pdf"),options) # PDF to HTML does not like
# xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,"COPAWEEKLYJUNE52013.pdf"),options)
# xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,"COPAMONTHLYMay2013.pdf"),options) # lxml doesn't like this one, interleaved <b> and <i> tags
# xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,"13_06_12_10_36_58_boletim_ingles_junho_2013.pdf"),options) # Long document with many tables
# xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,"1359397366Final_Coceral grain estimate_2012_December.pdf"),options)
# xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,"ClinicalResearchDisclosureReport2012Q2.pdf"),options) # throws not allowed
# xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,"argentina_diputados_voting_record.pdf"),options)
# xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,"bo_page24.pdf"),options) # Multi-column text and tables mixed on the page
# xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,"tabla_subsidios.pdf"),options) # Multi-column text and tables mixed on the page
SelectedPDF = "argentina_diputados_voting_record.pdf"

xmldata = pdftoxml(os.path.join(PDF_TEST_FILES,SelectedPDF),options)

root = lxml.etree.fromstring(xmldata)
pages = list(root)

# This is ok but


for page in pages:
    pagenumber = int(page.attrib.get("number"))
    pagewidth = int(page.attrib.get("width"))
    pageheight = int(page.attrib.get("height"))

    pageheight,pagewidth,left,top,right = processpage(page)

    fig = plotpage(pageheight,pagewidth,pagenumber,SelectedPDF,left,top,right)


    # counter=Counter(left)
