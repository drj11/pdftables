"""
pdftables public interface
"""

from __future__ import unicode_literals
"""
Some experiments with pdfminer
http://www.unixuser.org/~euske/python/pdfminer/programming.html
Some help here:
http://denis.papathanasiou.org/2010/08/04/extracting-text-images-from-pdf-files
"""

# TODO(IanHopkinson) Identify multi-column text, for multicolumn text detect
#                    per column
# TODO(IanHopkinson) Dynamic / smarter thresholding
# TODO(IanHopkinson) Handle argentina_diputados_voting_record.pdf automatically
# TODO(IanHopkinson) Handle multiple tables on one page

__all__ = ["get_tables", "page_to_tables", "page_contains_tables"]

import codecs
import collections
import math
import sys

import numpy_subset

from bisect import bisect_left
from collections import defaultdict
from counter import Counter
from cStringIO import StringIO
from operator import attrgetter

from .boxes import Box, BoxList, Rectangle
from .config_parameters import ConfigParameters
from .line_segments import (segment_histogram, above_threshold, hat_generator,
                            find_peaks, normal_hat_with_max_length,
                            midpoint, start_end, LineSegment,
                            segments_generator)
from .pdf_document import PDFDocument, PDFPage

IS_TABLE_COLUMN_COUNT_THRESHOLD = 3
IS_TABLE_ROW_COUNT_THRESHOLD = 3

LEFT = 0
TOP = 3
RIGHT = 2
BOTTOM = 1


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

    config = ConfigParameters()

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

    # TODO(pwaller):
    #
    # I would prefer if this function was defined in terms of `page_to_tables`
    # so that the logic cannot diverge.
    #
    # What should the test be?
    #   len(page_to_tables(page)) > 0?
    #   Number of tables left after filtering ones that have no data > 0?

    box_list = pdf_page.get_glyphs()

    boxtop = attrgetter("top")
    yhist = box_list.histogram(boxtop).rounder(1)
    test = [k for k, v in yhist.items() if v > IS_TABLE_COLUMN_COUNT_THRESHOLD]
    return len(test) > IS_TABLE_ROW_COUNT_THRESHOLD


def make_words(glyphs):
    """
    A word is a series of glyphs which are visually connected to each other.
    """

    def ordering(box):
        assert box.barycenter_y is not None, (
            "Box belongs to no barycenter. Has assign_barycenters been run?")
        return (box.barycenter_y, box.center_x)

    words = []
    glyphs = [g for g in glyphs if g.barycenter_y is not None]

    for glyph in sorted(glyphs, key=ordering):

        if len(words) > 0 and words[-1].is_connected_to(glyph):
            words[-1].extend(glyph)

        else:
            words.append(Box.copy(glyph))

    return words


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

    tables._x_segments, tables._y_segments = tables.all_glyphs.line_segments()
    # Find candidate text centerlines and compute some properties of them.
    (tables._y_point_values,
     tables._center_lines,
     tables._barycenter_maxheights) = (
         determine_text_centerlines(tables._y_segments)
     )

    assign_barycenters(tables._y_segments,
                       tables._center_lines,
                       tables._barycenter_maxheights)

    # Note: word computation must come after barycenter computation
    tables.all_words = make_words(tables.all_glyphs)

    tables.bounding_boxes = find_bounding_boxes(tables.all_glyphs, config)

    for box in tables.bounding_boxes:
        table = Table()
        table.bounding_box = box

        table.glyphs = tables.all_glyphs.inside(box)

        if len(table.glyphs) == 0:
            # If this happens, then find_bounding_boxes returned somewhere with
            # no glyphs inside it. Wat.
            raise RuntimeError("This is an empty table bounding box. "
                               "That shouldn't happen.")

        # Fetch line-segments

        # h is lines with fixed y, multiple x values
        # v is lines with fixed x, multiple y values
        # TODO(pwaller): compute for whole page, then get subset belonging to
        # this table.
        table._x_segments, table._y_segments = table.glyphs.line_segments()

        # Histogram them
        xs = table._x_glyph_histogram = segment_histogram(table._x_segments)
        ys = table._y_glyph_histogram = segment_histogram(table._y_segments)

        thres_nc = config.n_glyph_column_threshold
        thres_nr = config.n_glyph_row_threshold
        # Threshold them
        xs = table._x_threshold_segs = above_threshold(xs, thres_nc)
        ys = table._y_threshold_segs = above_threshold(ys, thres_nr)

        # Compute edges (the set of edges used to be called a 'comb')
        edges = compute_cell_edges(box, xs, ys, config)
        table.column_edges, table.row_edges = edges

        if table.column_edges and table.row_edges:
            table.data = compute_table_data(table)
        else:
            table.data = None

        tables.add(table)

    return tables


def determine_text_centerlines(v_segments):
    """
    Find candidate centerlines to snap glyphs to.
    """

    _ = hat_generator(v_segments, value_function=normal_hat_with_max_length)
    y_hat_points = list(_)

    if not y_hat_points:
        # No text on the page?
        return [], [], []

    points, values_maxlengths = zip(*y_hat_points)
    values, max_lengths = zip(*values_maxlengths)

    point_values = zip(points, values)

    # y-positions of "good" center lines vertically
    # ("good" is determined using the /\ ("hat") function)
    center_lines = list(find_peaks(point_values))

    # mapping of y-position (at each hat-point) to maximum glyph
    # height over that point
    barycenter_maxheights = dict(
        (barycenter, maxheight)
        for barycenter, maxheight in zip(points, max_lengths)
        if maxheight is not None)

    return point_values, center_lines, barycenter_maxheights


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

    column_edges = [box.left] + gap_midpoints(h_segments) + [box.right]
    row_edges = [box.top] + gap_midpoints(v_segments) + [box.bottom]

    return column_edges, row_edges


def compute_table_data(table):
    """
    Compute the final table data and return a list of lists.
    `table` should have been prepared with a list of glyphs, and a
    list of row_edges and column_edges (see the calling sequence in
    `page_to_tables`).
    """

    ncolumns = len(table.column_edges)
    nrows = len(table.row_edges)

    # This contains a list of `boxes` at each table cell
    box_table = [[list() for i in range(ncolumns)] for j in range(nrows)]

    for box in table.glyphs:
        if box.text is None:
            # Glyph has no text, ignore it.
            continue

        x, y = box.center_x, box.center_y

        # Compute index of "gap" between two combs, rather than the comb itself
        col = bisect_left(table.column_edges, x)
        row = bisect_left(table.row_edges, y)

        # If this blows up, please check what "box" is when it blows up.
        # Is it a "\n" ?
        box_table[row][col].append(box)

    def compute_text(boxes):

        def ordering(box):
            return (box.barycenter_y, box.center_x)
        sorted_boxes = sorted(boxes, key=ordering)

        result = []

        for this, next in zip(sorted_boxes, sorted_boxes[1:] + [None]):
            result.append(this.text)
            if next is None:
                continue
            centerline_distance = next.center_y - this.center_y
            # Maximum separation is when the two barycenters are far enough
            # away that the two characters don't overlap anymore
            max_separation = this.height / 2 + next.height / 2

            if centerline_distance >= max_separation:
                result.append('\n')

        return ''.join(result)

    table_array = []
    for row in box_table:
        table_array.append([compute_text(boxes) for boxes in row])

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

        return box_list.bounds()

        # TODO(pwaller): Reconcile the below code

        boxtop = attrgetter("top")
        boxbottom = attrgetter("bottom")

        # Note: (pwaller) this rounding excludes stuff I'm not sure we should
        # be excluding. (e.g, in the unica- dataset)

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
            bottomBox = [box for box in glyphs
                         if table_bottom_hint in box.text]
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


class Baseline(LineSegment):
    pass


def assign_barycenters(y_segments, barycenters, barycenter_heightmap):
    """
    Assign the glyph.barycenter and .barycenter_y to their "preferred"
    barycenter. "Preferred" is currently defined as closest.

    Here we use the term "barycenter" because it is the center of the glyph
    weighted according to nearby glyphs in Y. It is used to determine which
    word glyphs belong to, and which order text should be inserted into a cell.
    """
    result = list()
    # Compute a list of barycenter line segments, which are long enough to
    # overlap all glyphs which are long enough overlap it.
    for barycenter in barycenters:
        maxheight = barycenter_heightmap[barycenter]
        result.append(Baseline.make(barycenter - maxheight / 2,
                                    barycenter + maxheight / 2))

    to_visit = {LineSegment: midpoint, Baseline: start_end}

    active_barycenters = set()

    segments = segments_generator(result + y_segments, to_visit)
    for position, glyph, disappearing in segments:
        # Maintain a list of barycenters vs position
        if isinstance(glyph, Baseline):
            if not disappearing:
                active_barycenters.add(glyph)
            else:
                active_barycenters.remove(glyph)
            continue

        if len(active_barycenters) == 0:
            # There is no barycenter this glyph might belong to.
            # TODO(pwaller): huh? This should surely never happen.
            # Investigate why by turning this assert on.
            # assert False
            continue

        # Pick the barycenter closest to our position (== glyph.center_y)
        barycenter = min(active_barycenters,
                         key=lambda b: abs(b.midpoint - position))

        glyph.object.barycenter = barycenter
        glyph.object.barycenter_y = barycenter.midpoint
