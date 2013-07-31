#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ScraperWiki Limited
# Ian Hopkinson, 2013-06-04

from __future__ import unicode_literals
"""
Some experiments with pdfminer
http://www.unixuser.org/~euske/python/pdfminer/programming.html
Some help here:
http://denis.papathanasiou.org/2010/08/04/extracting-text-images-from-pdf-files
"""

# TODO Identify multi-column text, for multicolumn text detect per column
# TODO Dynamic / smarter thresholding
# TODO Handle argentina_diputados_voting_record.pdf automatically
# TODO Handle multiple tables on one page


import sys
import codecs

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTPage
from pdfminer.converter import PDFPageAggregator

import collections

from tree import Leaf, LeafList
import requests  # TODO: remove this dependency
from cStringIO import StringIO
import math
import numpy # TODO: remove this dependency
from counter import Counter

IS_TABLE_COLUMN_COUNT_THRESHOLD = 3
IS_TABLE_ROW_COUNT_THRESHOLD = 3

class TableDiagnosticData(object):
    def __init__(self, box_list=LeafList(), top_plot=dict(), left_plot=dict(), x_comb=[], y_comb=[]):
        self.box_list = box_list
        self.top_plot = top_plot
        self.left_plot = left_plot
        self.x_comb = x_comb
        self.y_comb = y_comb

class Table(list):
    def __init__(self, content, page, page_total, table_index, table_index_total):
        super(Table, self).__init__(content)
        self.page_number = page
        self.total_pages = page_total
        self.table_number_on_page = table_index
        self.total_tables_on_page = table_index_total

LEFT = 0
TOP = 3
RIGHT = 2
BOTTOM = 1

def get_tables(fh):
    """
    Return a list of 'tables' from the given file handle, where a table is a
    list of rows, and a row is a list of strings.
    """
    result = []
    doc, interpreter, device = initialize_pdf_miner(fh)
    doc_length = len(list(doc.get_pages()))
    for i, pdf_page in enumerate(doc.get_pages()):
        #print("Trying page {}".format(i + 1))
        if not page_contains_tables(pdf_page, interpreter, device):
            #print("Skipping page {}: no tables.".format(i + 1))
            continue

        # receive the LTPage object for the page.
        interpreter.process_page(pdf_page)
        processed_page = device.get_result()

        (table, _) = page_to_tables(
            processed_page,
            extend_y=True,
            hints=[],
            atomise=True)
        crop_table(table)
        result.append(Table(table,i+1,doc_length,1,1))

    return result


def crop_table(table):
    """
    Remove empty rows from the top and bottom of the table.
    """
    for row in list(table):  # top -> bottom
        if not any(cell.strip() for cell in row):
            table.remove(row)
        else:
            break

    for row in list(reversed(table)):  # bottom -> top
        if not any(cell.strip() for cell in row):
            table.remove(row)
        else:
            break


def initialize_pdf_miner(fh):
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fh)
    # Create a PDF document object that stores the document structure.
    doc = PDFDocument()
    # Connect the parser and document objects.
    parser.set_document(doc)
    doc.set_parser(parser)
    # Supply the password for initialization.
    # (If no password is set, give an empty string.)
    doc.initialize("")
    # Check if the document allows text extraction. If not, abort.
    if not doc.is_extractable:
        raise ValueError("PDFDocument is_extractable was False.")
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    # Create a PDF device object.
    device = PDFDevice(rsrcmgr)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.
    # for page in doc.get_pages():
    #    interpreter.process_page(page)

    # Set parameters for analysis.
    laparams = LAParams()
    laparams.word_margin = 0.0
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    return doc, interpreter, device


def contains_tables(fh):
    """
    contains_tables(fh) takes a file handle and returns a boolean array of the
    length of the document which is true for pages which contains tables
    """
    doc, interpreter, device = initialize_pdf_miner(fh)

    return [page_contains_tables(p, interpreter, device) for
            p in doc.get_pages()]


def page_contains_tables(pdf_page, interpreter, device):
    # TODO: hide doc, interpreter, device inside a higher level Pdf class. It's
    # silly that we have to care about these (see function signature!!)

    interpreter.process_page(pdf_page)
    # receive the LTPage object for the page.
    layout = device.get_result()
    box_list = LeafList().populate(layout)
    for item in box_list:
        assert isinstance(item, Leaf), "NOT LEAF"
    yhist = box_list.histogram(Leaf._top).rounder(1)

    test = [k for k, v in yhist.items() if v > IS_TABLE_COLUMN_COUNT_THRESHOLD]
    return len(test) > IS_TABLE_ROW_COUNT_THRESHOLD


def threshold_above(hist, threshold_value):
    """
    >>> threshold_above(Counter({518: 10, 520: 20, 530: 20, \
                                             525: 17}), 15)
    [520, 530, 525]
    """
    if not isinstance(hist, Counter):
        raise ValueError("requires Counter")  # TypeError then?

    above = [k for k, v in hist.items() if v > threshold_value]
    return above


def comb(combarray, value):
    """
    Takes a sorted array and returns the interval number of the value passed to
    the function
    """
    # Raise an error in combarray not sorted
    if (combarray != sorted(combarray)) and (combarray != sorted(
            combarray, reverse=True)):
        raise Exception("comb: combarray is not sorted")

    index = -1
    if combarray[0] > combarray[-1]:
        for i in range(1, len(combarray)):
            if combarray[i - 1] >= value >= combarray[i]:
                index = i - 1
    else:
        for i in range(1, len(combarray)):
            if combarray[i - 1] <= value <= combarray[i]:
                index = i - 1

    return index


def apply_combs(box_list, x_comb, y_comb):
    """Allocates text to table cells using the x and y combs"""
    ncolumns = len(x_comb) - 1
    nrows = len(y_comb) - 1
    table_array = [[''] * ncolumns for j in range(nrows)]
    for box in box_list:
        y = round(box.midline)
        x = round(box.centreline)
        rowindex = comb(y_comb, y)
        columnindex = comb(x_comb, x)
        if rowindex != -1 and columnindex != -1:
            # there was already some content at this coordinate so we
            # concatenate (in an arbitrary order!)
            table_array[rowindex][columnindex] += box.text.rstrip('\n\r')

    return table_array


def comb_from_projection(projection, threshold, orientation):
    """Calculates the boundaries between cells from the projection of the boxes
    onto either the y axis (for rows) or the x-axis (for columns). These
    boundaries are known as the comb
    """
    if orientation=="row":
        tol=1
    elif orientation=="column":
        tol=3

    projection_threshold = threshold_above(projection, threshold)

    projection_threshold = sorted(projection_threshold)
    # need to generate a list of uppers (right or top edges)
    # and a list of lowers (left or bottom edges)

    # uppers = [k for k, v in yhisttop.items() if v > yThreshold]
    # lowers = [k for k, v in yhistbottom.items() if v > yThreshold]
    uppers = []
    lowers = []

    lowers.append(projection_threshold[0])
    for i in range(1, len(projection_threshold)):
        if projection_threshold[i] > (
                projection_threshold[i-1] + 1):
            uppers.append(projection_threshold[i - 1])
            lowers.append(projection_threshold[i])
    uppers.append(projection_threshold[-1])

    comb = comb_from_uppers_and_lowers(uppers, lowers, tol=tol,
                                       projection = projection)
    comb.reverse()

    return comb


def comb_from_uppers_and_lowers(uppers, lowers, tol=1, projection=dict()):
    """Called by comb_from_projection to calculate the comb given a set of
    uppers and lowers, which are upper and lower edges of the thresholded
    projection"""
    # tol is a tolerance to remove very small minima, increasing to 2 fowls up
    # row separation
    assert len(uppers) == len(lowers)
    uppers.sort(reverse=True)
    lowers.sort(reverse=True)
    comb = []
    comb.append(uppers[0])
    for i in range(1, len(uppers)):
        if (lowers[i - 1]-uppers[i])>tol:
            comb.append(find_minima(lowers[i - 1], uppers[i], projection))
            #comb.append(find_minima(lowers[i - 1], uppers[i]))

    comb.append(lowers[-1])

    return comb

def find_minima(lower, upper, projection=dict()):

    #print lower, upper, projection
    if len(projection)==0:
        idx = (lower + upper) / 2.0
    else:
        profile = []
        for i in range(upper, lower):
            #print projection[i]
            profile.append(projection[i])

        val, idx = min((val, idx) for (idx, val) in enumerate(profile))
        #val, idx = min(profile)
        idx = upper + idx

    return idx

def comb_extend(comb, minv, maxv):
    """Extend the comb to minv and maxv"""
    # TODO should this truncate if minv>minc or maxc>maxc
    # print y_comb
    # Find sort order of comb, convert to ascending
    reversed = False
    if comb[0] > comb[-1]:
        comb.reverse()
        reversed = True
    # Find min and max of comb
    minc = comb[0]
    maxc = comb[-1]
    # Get average row spacing
    rowSpacing = numpy.average(numpy.diff(comb))
    # Extend minimum
    if minv < minc:
        comb.reverse()
        comb.extend(list(numpy.arange(minc, minv, -rowSpacing))[1:])
        comb.reverse()
    # Extend maximum
    if maxv > maxc:
        comb.extend(list(numpy.arange(maxc, maxv, rowSpacing))[1:])

    if reversed:
        comb.reverse()
    return comb


def project_boxes(box_list, orientation, erosion=0):
    """
    Take a set of boxes and project their extent onto an axis
    """
    if orientation == "column":
        upper = RIGHT
        lower = LEFT
    elif orientation == "row":
        upper = TOP
        lower = BOTTOM

    projection = {}
    minv = round(min([box.bbox[lower]
                 for box in box_list])) - 2  # ensure some overlap
    maxv = round(max([box.bbox[upper] for box in box_list])) + 2

    # Initialise projection structure
    # print minv, maxv
    coords = range(int(minv), int(maxv))
    projection = coords

    # print projection
    for box in box_list:
        for i in range(int(round(box.bbox[lower])) + erosion,
                       int(round(box.bbox[upper])) - erosion):
            # projection[i] += 1
            projection.append(i)

    return Counter(projection)


def get_pdf_page(fh, pagenumber):
    doc, interpreter, device = initialize_pdf_miner(fh)
    pages = list(doc.get_pages())

    try:
        page = pages[pagenumber - 1]
    except IndexError:
        raise IndexError("Invalid page number")

    interpreter.process_page(page)
    # receive the LTPage object for the page.
    processedPage = device.get_result()
    return processedPage

# def getTable(fh, page, extend_y=False, hints=[]):
#    """placeholder for tests, refactor out"""
#    return page_to_tables(get_pdf_page(fh, page), extend_y, hints)


def get_min_and_max_y_from_hints(box_list, top_string, bottom_string):
    miny = None
    maxy = None
    if top_string:
        top_box = [box for box in box_list if top_string in box.text]
        if top_box:
            maxy = top_box[0].top
    if bottom_string:
        bottomBox = [box for box in box_list if bottom_string in box.text]
        if bottomBox:
            miny = bottomBox[0].bottom
    return miny, maxy


def rounder(val, tol):
    """
    Utility function to round numbers to arbitrary tolerance
    """
    return round((1.0 * val) / tol) * tol


#def filter_box_list_by_type(box_list, flt):
#    return [box for box in box_list if box.classname in flt]


def multi_column_detect(page):
    #TODO This function is under construction
    """
    Test for multiColumns from a box_list, returns an integer number of columns
    and a set of (left, right) pairs delineating any columns
    """
    # Ways to identify multicolumns:
    # 1. High fill factor compared to tables
    # 2. Gullies at textwidth/2, (textwidth/3, 2*textwidth/3)...
    # 3. Histogram of boxwidths with peak at some fraction of page width
    # This is like project_boxes but we are projecting the length of the
    # textbox onto the axis
    box_list = LeafList().populate(
        page, ['LTPage', 'LTTextLineHorizontal']).purge_empty_text()

    # Should use the LTPage object to get page bounding box
    box_list = filter_box_list_by_type(box_list, 'LTTextLineHorizontal')
    pile = {}
    vstep = 5  # should be scaled by modal row height
    minv = rounder(
        min([box.bottom for box in box_list]),
        5)  # ensure some overlap
    maxv = rounder(max([box.top for box in box_list]), 5)

    minx = round(min([box.left for box in box_list]))  # ensure some overlap
    maxx = round(max([box.right for box in box_list]))

    # Initialise projection structure
    # print minv, maxv

    coords = range(int(minv), int(maxv) + vstep, vstep)

    pile = collections.OrderedDict(zip(coords, [0] * len(coords)))
    # print projection
    for box in box_list:
        # print int(rounder(box.midline, 30)), box.width
        pile[int(rounder(box.midline, vstep))] += box.width

    for key, value in pile.items():
        pile[key] = value / (maxx - minx)

    # Box width histogram
    bstep = 10
    boxhist = {}
    boxwidthmin = rounder(min([box.width for box in box_list]), bstep)
    boxwidthmax = rounder(max([box.width for box in box_list]), bstep)

    coords = range(int(boxwidthmin), int(boxwidthmax) + bstep, bstep)
    boxhist = collections.OrderedDict(zip(coords, [0] * len(coords)))
    for box in box_list:
        # print int(rounder(box.midline, 30)), box.width
        boxhist[int(rounder(box.width, bstep))] += 1

    nboxes = len(box_list)
    for key, value in boxhist.items():
        boxhist[key] = float(value) / float(nboxes)
    # TODO: plt undefined
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(map(float, boxhist.keys()),
             map(float, boxhist.values()), color='red')
    plt.show()

    # This is old fashion projection
    projection = project_boxes(box_list, 'column')
    # process key and value
    # print projection
    # projection = Counter(projection)
    # print projection
    return pile, projection


def page_to_tables(page, extend_y=False, hints=[], atomise=False):
    """
    Get a rectangular list of list of strings from one page of a document
    """
    if not isinstance(page, LTPage):
        raise TypeError("Page must be LTPage, not {}".format(page.__class__))

    table_array = []

    # For LTTextLine horizontal column and row thresholds of 3 work ok
    columnThreshold = 5  # 3 works for smaller tables
    rowThreshold = 3

    if atomise:
        flt = ['LTPage', 'LTTextLineHorizontal', 'LTChar']
    else:
        flt = ['LTPage', 'LTTextLineHorizontal']
    # flt = ['LTPage', 'LTTextLineHorizontal', 'LTFigure']
    box_list = LeafList().populate(page, flt).purge_empty_text()

    (minx, maxx, miny, maxy) = find_table_bounding_box(box_list, hints=hints)

    """If miny and maxy are None then we found no tables and should exit"""
    if miny is None and maxy is None:
       print "found no tables"
       return table_array, TableDiagnosticData()

    if atomise:
        box_list = box_list.filterByType(['LTPage', 'LTChar'])

    filtered_box_list = filter_box_list_by_position(
        box_list,
        miny,
        maxy,
        Leaf._midline)

    filtered_box_list = filter_box_list_by_position(
        filtered_box_list,
        minx,
        maxx,
        Leaf._centreline)

    # Project boxes onto horizontal axis
    column_projection = project_boxes(filtered_box_list, "column")

    # Project boxes onto vertical axis
    # Erode row height by a fraction of the modal text box height
    erodelevel = int(math.floor(calculate_modal_height(filtered_box_list) / 4))
    row_projection = project_boxes(
        filtered_box_list, "row",
        erosion=erodelevel)

    #
    y_comb = comb_from_projection(row_projection, rowThreshold, "row")
    y_comb.reverse()

    # columnThreshold = max(len(y_comb)*0.75,5)
    x_comb = comb_from_projection(column_projection, columnThreshold, "column")

    x_comb[0] = minx
    x_comb[-1] = maxx

    # Extend y_comb to page size if extend_y is true
    if extend_y:
        pageminy = min([box.bottom for box in box_list])
        pagemaxy = max([box.top for box in box_list])
        y_comb = comb_extend(y_comb, pageminy, pagemaxy)
        filtered_box_list = box_list

    # Applying the combs
    table_array = apply_combs(box_list, x_comb, y_comb)

    # Strip out leading and trailing spaces when atomise true
    if atomise:
        tmp_table = []
        for row in table_array:
            stripped_row = map(unicode.strip,row)
            tmp_table.append(stripped_row)
        table_array = tmp_table

    diagnostic_data = TableDiagnosticData(
        filtered_box_list,
        column_projection,
        row_projection,
        x_comb,
        y_comb)

    return table_array, diagnostic_data

def find_table_bounding_box(box_list, hints=[]):
    """ Returns one bounding box (minx, maxx, miny, maxy) for tables based
    on a boxlist
    """

    miny = min([box.bottom for box in box_list])
    maxy = max([box.top for box in box_list])
    minx = min([box.left for box in box_list])
    maxx = max([box.right for box in box_list])

    """ Get rid of LTChar for this stage """
    textLine_boxlist = box_list.filterByType('LTTextLineHorizontal')

    """ Try to reduce the y range with a threshold, wouldn't work for x"""
    yhisttop = textLine_boxlist.histogram(Leaf._top).rounder(2)
    yhistbottom = textLine_boxlist.histogram(Leaf._bottom).rounder(2)

    try:
        miny = min(threshold_above(yhistbottom, IS_TABLE_COLUMN_COUNT_THRESHOLD))
    # and the top of the top cell
        maxy = max(threshold_above(yhisttop, IS_TABLE_COLUMN_COUNT_THRESHOLD))
    except ValueError:
        # Value errors raised when min and/or max fed empty lists
        miny = None
        maxy = None
        #raise ValueError("table_threshold caught nothing")

    """The table miny and maxy can be modified by hints"""
    if hints:
        top_string = hints[0]  # "% Change"
        bottom_string = hints[1]  # "15.67%"
        hintedminy, hintedmaxy = get_min_and_max_y_from_hints(
            textLine_boxlist, top_string, bottom_string)
        if hintedminy:
            miny = hintedminy
        if hintedmaxy:
            maxy = hintedmaxy
    """Modify table minx and maxx with hints? """

    return (minx, maxx, miny, maxy)

def filter_box_list_by_position(box_list, minv, maxv, dir_fun):
    #TODO This should be in tree.py
    filtered_box_list = LeafList()
    # print minv, maxv, index
    for box in box_list:
        # box = boxstruct[0]
        if dir_fun(box) >= minv and dir_fun(box) <= maxv:
            # print box
            filtered_box_list.append(box)

    return filtered_box_list


def calculate_modal_height(box_list):
    height_list = []
    for box in box_list:
        if box.classname in ('LTTextLineHorizontal', 'LTChar'):
            height_list.append(round(box.bbox[TOP] - box.bbox[BOTTOM]))

    modal_height = Counter(height_list).most_common(1)
    return modal_height[0][0]


def file_handle_from_url(URL):
    # TODO: move this function to a helper library
    response = requests.get(URL)
    fh = StringIO(response.content)
    return fh


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    if len(sys.argv) > 1:
        from display import to_string
        with open(sys.argv[1], 'rb') as f:
            tables = get_tables(f)
            for i, table in enumerate(tables):
                print("---- TABLE {} ----".format(i + 1))
                print(to_string(table))
    else:
        print("Usage: {} <file.pdf>".format(sys.argv[0]))
