
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

__all__ = ["get_tables", "page_to_tables", "page_contains_tables"]

import codecs
import collections
import math
import sys

import numpy_subset

from bisect import bisect
from counter import Counter
from cStringIO import StringIO
from operator import attrgetter

from .boxes import Box, BoxList, Rectangle
from .config_parameters import ConfigParameters
from .linesegments import segment_histogram, above_threshold
from .pdf_document import PDFDocument, PDFPage

IS_TABLE_COLUMN_COUNT_THRESHOLD = 3
IS_TABLE_ROW_COUNT_THRESHOLD = 3

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
    raise NotImplementedError("This interface hasn't been fixed yet, sorry!")

    result = []

    config = ConfigParameters(extend_y=True)

    # TODO(pwaller): Return one table container with all tables on it?

    for i, pdf_page in enumerate(pdf_document.get_pages()):
        if not page_contains_tables(pdf_page):
            continue

        tables = page_to_tables(pdf_page, config)

        # crop_table(table)
        #result.append(Table(table, i + 1, len(pdf_document), 1, 1))

    return result


def crop_table(table):
    """
    Remove empty rows from the top and bottom of the table.

    TODO(pwaller): We may need functionality similar to this, or not?
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


def page_contains_tables(pdf_page):
    if not isinstance(pdf_page, PDFPage):
        raise TypeError("Page must be PDFPage, not {}".format(
            pdf_page.__class__))

    box_list = pdf_page.get_glyphs()

    boxtop = attrgetter("top")
    yhist = box_list.histogram(boxtop).rounder(1)
    test = [k for k, v in yhist.items() if v > IS_TABLE_COLUMN_COUNT_THRESHOLD]
    return len(test) > IS_TABLE_ROW_COUNT_THRESHOLD


def apply_combs(box_list, x_comb, y_comb):
    """
    Allocates text to table cells using the x and y combs
    """

    assert x_comb == sorted(x_comb)
    assert y_comb == sorted(y_comb)

    ncolumns = len(x_comb)
    nrows = len(y_comb)

    table_array = [[''] * ncolumns for j in range(nrows)]

    for box in box_list:
        if box.text is None:
            # Glyph has no text, ignore it.
            continue

        x, y = box.center_x, box.center_y

        # Compute index of "gap" between two combs, rather than the comb itself
        col = bisect(x_comb, x)
        row = bisect(y_comb, y)

        table_array[row][col] += box.text.rstrip('\n\r')

    return table_array


class Table(object):

    """
    Represents a single table on a PDF page.
    """

    def __init__(self):
        # TODO(pwaller): populate this from pdf_page.number
        self.page_number = None
        self.bounding_box = None
        self.glyphs = None
        self.edges = None
        self.row_edges = None
        self.column_edges = None
        self.data = None

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

        self.original_page = None
        self.page_size = None
        self.bounding_boxes = None
        self.all_glyphs = None

    def add(self, table):
        self.tables.append(table)

    def __repr__(self):
        return "TableContainer(" + repr(self.__dict__) + ")"

    def __iter__(self):
        return iter(self.tables)


def page_to_tables(pdf_page, config=None):
    """
    The central algorithm to pdftables, find all the tables on ``pdf_page`` and
    return them in a ```TableContainer``.

    The algorithm is steered with ``config`` which is of type
    ``ConfigParameters``
    """

    if config is None:
        config = ConfigParameters()

    # Avoid local variables; instead use properties of the
    # `tables` object, so that they are exposed for debugging and
    # visualisation.

    tables = TableContainer()

    tables.original_page = pdf_page
    tables.page_size = pdf_page.size
    tables.all_glyphs = pdf_page.get_glyphs()
    tables.bounding_boxes = find_bounding_boxes(tables.all_glyphs, config)

    for box in tables.bounding_boxes:
        table = Table()
        table.bounding_box = box

        table.glyphs = tables.all_glyphs.inside(box)

        # Fetch line-segments
        # h is lines with fixed y, multiple x values
        # v is lines with fixed x, multiple y values
        table._h_segments, table._v_segments = table.glyphs.line_segments()

        # Histogram them
        h = table._h_glyph_histogram = segment_histogram(table._h_segments)
        v = table._v_glyph_histogram = segment_histogram(table._v_segments)

        # Threshold them
        h = table._h_threshold_segs = above_threshold(h, 3)
        v = table._v_threshold_segs = above_threshold(v, 5)

        # Compute edges (the set of edges used to be called a 'comb')
        edges = compute_cell_edges(box, h, v, config)
        table.column_edges, table.row_edges = edges

        if table.column_edges and table.row_edges:
            table.data = compute_table_data(table)
        else:
            table.data = None

        tables.add(table)

    return tables


def find_bounding_boxes(glyphs, config):
    """
    Returns a list of bounding boxes, one per table.
    """

    # TODO(pwaller): One day, this function will find more than one table.

    th, bh = config.table_top_hint, config.table_bottom_hint
    assert(glyphs is not None)
    bbox = find_table_bounding_box(glyphs, th, bh)

    if bbox is Box.empty_box:
        return []

    # Return the one table's bounding box.
    return [bbox]


def compute_cell_edges(box, h_segments, v_segments, config):
    """
    Determines edges of cell content horizontally and vertically. It
    works by binning and thresholding the resulting histogram for
    each of the two axes (x and y).
    """

    # TODO(pwaller): shove this on a config?
    # these need better names before being part of a public API.
    # They specify the minimum amount of space between "threshold-segments"
    # in the histogram of line segments and the minimum length, otherwise
    # they are not considered a gap.
    # units= pdf "points"
    minimum_segment_size = 0.5
    minimum_gap_size = 0.5

    def gap_midpoints(segments):
        return [(b.start + a.end) / 2.
                for a, b in zip(segments, segments[1:])
                if b.start - a.end > minimum_gap_size
                   and b.length > minimum_segment_size
                ]

    column_edges = gap_midpoints(h_segments) + [box.right]
    row_edges = gap_midpoints(v_segments) + [box.bottom]

    return column_edges, row_edges


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

    # TODO(pwaller): These closures are here to make it clear how these things
    #                belong together. At some point it may get broken apart
    #                again, or simplified.

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
        glyphs = [glyph for glyph in box_list if glyph.text is not None]
        if table_top_hint:
            top_box = [box for box in glyphs if table_top_hint in box.text]
            if top_box:
                miny = top_box[0].top

        if table_bottom_hint:
            bottomBox = [box for box in glyphs if table_bottom_hint in box.text]
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
