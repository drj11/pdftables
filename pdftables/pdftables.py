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

# TODO(pwaller/paulfurley) Specify our public interface here
# (and hide everything else)
# __all__ = ["get_tables"]

import sys
import codecs

from pdf_document import PDFDocument, PDFPage
from config_parameters import ConfigParameters

import collections

from boxes import Box, BoxList, Rectangle
from cStringIO import StringIO
import math
import numpy_subset
from counter import Counter
from operator import attrgetter

IS_TABLE_COLUMN_COUNT_THRESHOLD = 3
IS_TABLE_ROW_COUNT_THRESHOLD = 3


class Table(list):

    def __init__(self, content, page, page_total, table_index,
                 table_index_total):
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
    pdf = PDFDocument.from_fileobj(fh)
    return get_tables_from_document(pdf)


def get_tables_from_document(pdf_document):
    """
    Return a list of 'tables' from the given PDFDocument, where a table is a
    list of rows, and a row is a list of strings.
    """

    result = []

    for i, pdf_page in enumerate(pdf_document.get_pages()):
        #print("Trying page {}".format(i + 1))
        if not page_contains_tables(pdf_page):
            #print("Skipping page {}: no tables.".format(i + 1))
            continue

        (table, _) = page_to_tables(
            pdf_page,
            ConfigParameters(
                extend_y=True,
                atomise=True))
        crop_table(table)
        result.append(Table(table, i + 1, len(pdf_document), 1, 1))

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

    # TODO(pwaller): wtf?
    for row in list(reversed(table)):  # bottom -> top
        if not any(cell.strip() for cell in row):
            table.remove(row)
        else:
            break


def page_contains_tables(pdf_page):
    if not isinstance(pdf_page, PDFPage):
        raise TypeError("Page must be PDFPage, not {}".format(
            pdf_page.__class__))

    box_list = pdf_page.get_boxes(set((PDFPage.BoxPage, PDFPage.BoxLine)))

    boxtop = attrgetter("top")
    yhist = box_list.histogram(boxtop).rounder(1)
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
    if orientation == "row":
        tol = 1
    elif orientation == "column":
        tol = 3

    projection_threshold = threshold_above(projection, threshold)

    projection_threshold = sorted(projection_threshold)
    # need to generate a list of uppers (right or top edges)
    # and a list of lowers (left or bottom edges)

    # uppers = [k for k, v in yhisttop.items() if v > yThreshold]
    # lowers = [k for k, v in yhistbottom.items() if v > yThreshold]
    uppers = []
    lowers = []

    # TODO(pwaller): Use a more readable algorithm, determine purpose, maybe
    #                refactor or use more general approach.
    #
    # What is the + 1 for? Why?
    #
    # for this, next in zip(a, a[1:])
    #     if this + 1 < next:
    #         uppers.append(this)
    #         lowers.append(next)

    lowers.append(projection_threshold[0])
    for i in range(1, len(projection_threshold)):
        if projection_threshold[i] > (
                projection_threshold[i - 1] + 1):
            uppers.append(projection_threshold[i - 1])
            lowers.append(projection_threshold[i])
    uppers.append(projection_threshold[-1])

    comb = comb_from_uppers_and_lowers(uppers, lowers, tol=tol,
                                       projection=projection)
    comb.reverse()

    return comb


def comb_from_uppers_and_lowers(uppers, lowers, tol=1, projection=dict()):
    """
    Called by comb_from_projection to calculate the comb given a set of
    uppers and lowers, which are upper and lower edges of the thresholded
    projection
    """

    # tol is a tolerance to remove very small minima, increasing to 2 fowls up
    # row separation
    assert len(uppers) == len(lowers)
    uppers.sort(reverse=True)
    lowers.sort(reverse=True)
    comb = []
    comb.append(uppers[0])
    for i in range(1, len(uppers)):
        if (lowers[i - 1] - uppers[i]) > tol:
            comb.append(find_minima(lowers[i - 1], uppers[i], projection))
            #comb.append(find_minima(lowers[i - 1], uppers[i]))

    comb.append(lowers[-1])

    return comb


def find_minima(lower, upper, projection=dict()):

    # print lower, upper, projection
    if len(projection) == 0:
        idx = (lower + upper) / 2.0
    else:
        profile = []
        for i in range(upper, lower):
            # print projection[i]
            profile.append(projection[i])

        val, idx = min((val, idx) for (idx, val) in enumerate(profile))
        #val, idx = min(profile)
        idx = upper + idx

    return idx


def comb_extend(comb, minv, maxv):
    """
    Extend the comb to minv and maxv
    """
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
    rowSpacing = numpy_subset.average(numpy_subset.diff(comb))

    # Extend minimum
    if minv < minc:
        comb.reverse()
        comb.extend(list(numpy_subset.arange(minc, minv, -rowSpacing))[1:])
        comb.reverse()

    # Extend maximum
    if maxv > maxc:
        comb.extend(list(numpy_subset.arange(maxc, maxv, rowSpacing))[1:])

    if reversed:
        comb.reverse()
    return comb


def project_boxes(box_list, orientation, erosion=0):
    """
    Take a set of boxes and project their extent onto an axis
    """
    if orientation == "column":
        first = attrgetter("left")
        second = attrgetter("right")
    elif orientation == "row":
        first = attrgetter("top")
        second = attrgetter("bottom")

    projection = {}
    # ensure some overlap
    minv = round(min([first(box) for box in box_list])) - 2
    maxv = round(max([second(box) for box in box_list])) + 2

    # Initialise projection structure
    # print minv, maxv
    coords = range(int(minv), int(maxv))
    projection = coords

    # print projection
    for box in box_list:
        for i in range(int(round(first(box))) + erosion,
                       int(round(second(box))) - erosion):
            # projection[i] += 1
            projection.append(i)

    return Counter(projection)


def get_pdf_page(fh, pagenumber):
    pdf = PDFDocument.from_fileobj(fh)
    return pdf.get_pages()[pagenumber - 1]


def rounder(val, tol):
    """
    Utility function to round numbers to arbitrary tolerance
    """
    return round((1.0 * val) / tol) * tol


class Table(object):

    """
    Represents a single table on a PDF page.
    """

    def __init__(self):
        self.bounding_box = None
        self.glyphs = None
        self.edges = None
        self.row_edges = None
        self.column_edges = None
        self.data = None
        return

    def __repr__(self):
        d = self.data
        if d is not None:
            # TODO(pwaller): Compute this in a better way.
            h = len(d)
            w = len(d[0])
            return "<Table (w, h)=({0}, {1})>".format(w, h)
        else:
            return "<Table [empty]>"


class TableContainer(object):

    """
    Represents a collection of tables on a PDF page.
    """

    def __init__(self):
        self.tables = []

    def add(self, table):
        self.tables.append(table)

    def __repr__(self):
        return "TableContainer(" + repr(self.__dict__) + ")"

    def __iter__(self):
        return iter(self.tables)


def page_to_tables(pdf_page, config=None):
    """
    Get a rectangular list of list of strings from one page of a document
    """

    # Avoid local variables; instead use properties of the
    # `tables` object, so that they are exposed for debugging and
    # visualisation.

    tables = TableContainer()

    if config is None:
        config = ConfigParameters()

    tables.bounding_boxes = find_bounding_boxes(pdf_page, config)

    tables.all_glyphs = pdf_page.get_glyphs()

    for box in tables.bounding_boxes:
        table = Table()
        table.bounding_box = box
        table.glyphs = tables.all_glyphs.inside(box)
        edges = compute_edges(table.glyphs, box, config)
        (table.column_edges, table.row_edges) = edges
        table.data = compute_table_data(table)
        tables.add(table)

    return tables


def find_bounding_boxes(pdf_page, config):
    """Returns a list of bounding boxes."""

    box_list = pdf_page.get_glyphs()
    bbox = find_table_bounding_box(
        box_list, config.table_top_hint, config.table_bottom_hint)

    if bbox is Box.empty_box:
        return []

    return [bbox]


def compute_edges(box_list, bounds, config):
    """
    Determines edges of cell content horizontally and vertically. It
    works by binning and thresholding the resulting histogram for
    each of the two axes (x and y).
    """

    # Project boxes onto horizontal axis
    column_projection = project_boxes(box_list, "column")

    # Project boxes onto vertical axis
    # Erode row height by a fraction of the modal text box height
    erodelevel = int(math.floor(calculate_modal_height(box_list) / 4))
    row_projection = project_boxes(
        box_list, "row",
        erosion=erodelevel)

    rowThreshold = 3
    y_comb = comb_from_projection(row_projection, rowThreshold, "row")
    y_comb.reverse()

    columnThreshold = 5  # 3 works for smaller tables
    x_comb = comb_from_projection(column_projection, columnThreshold, "column")

    x_comb[0] = bounds.left
    x_comb[-1] = bounds.right

    # Extend y_comb to page size if extend_y is true
    if config.extend_y:
        y_comb = comb_extend(y_comb, bounds.top, bounds.bottom)
        # is drj commenting this out correct?
        # filtered_box_list = box_list

    return x_comb, y_comb


def compute_table_data(table):
    """
    Compute the final table data and return a list of lists.
    `table` should have been prepared with a list of glyphs, and a
    list of row_edges and column_edges (see the calling sequence in
    `page_to_tables`).
    """

    # Applying the combs
    table_array = apply_combs(
        table.glyphs, table.column_edges, table.row_edges)

    return table_array


def find_table_bounding_box(box_list, table_top_hint, table_bottom_hint):
    """
    Returns one bounding box (minx, maxx, miny, maxy) for tables based
    on a boxlist
    """

    def threshold_y():
        """
        Try to reduce the y range with a threshold.
        """

        boxtop = attrgetter("top")
        boxbottom = attrgetter("bottom")

        yhisttop = box_list.histogram(boxtop).rounder(2)
        yhistbottom = box_list.histogram(boxbottom).rounder(2)

        try:
            # TODO(pwaller): fix this, remove except block
            threshold = IS_TABLE_COLUMN_COUNT_THRESHOLD
            miny = min(threshold_above(yhisttop, threshold))
            # and the top of the top cell
            maxy = max(threshold_above(yhistbottom, threshold))
        except ValueError:
            # Value errors raised when min and/or max fed empty lists
            miny = None
            maxy = None
            #raise ValueError("table_threshold caught nothing")

        return Box(Rectangle(
            x1=float("-inf"),
            y1=miny,
            x2=float("+inf"),
            y2=maxy,
        ))

    def hints_y():
        miny = float("-inf")
        maxy = float("+inf")
        if table_top_hint:
            top_box = [box for box in box_list if top_string in box.text]
            if top_box:
                miny = top_box[0].top
        if table_bottom_hint:
            bottomBox = [box for box in box_list if bottom_string in box.text]
            if bottomBox:
                maxy = bottomBox[0].bottom
        return Box(Rectangle(
            x1=float("-inf"),
            y1=miny,
            x2=float("+inf"),
            y2=maxy,
        ))

    bounds = box_list.bounds()
    threshold_bounds = threshold_y()
    hinted_bounds = hints_y()

    return bounds.clip(threshold_bounds, hinted_bounds)


def filter_box_list_by_position(box_list, minv, maxv, dir_fun):
    # TODO This should be in tree.py
    filtered_box_list = BoxList()
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
        height_list.append(round(box.bottom - box.top))

    modal_height = Counter(height_list).most_common(1)
    return modal_height[0][0]


def file_handle_from_url(URL):
    import requests
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
