#!/usr/bin/env python

import sys
from collections import namedtuple
import poppler
import cairo

from os.path import abspath

Point = namedtuple('Point', ['x', 'y'])
Line = namedtuple('Line', ['start', 'end'])
Polygon = namedtuple('Polygon', 'points')
Rectangle = namedtuple('Rectangle', ['top_left', 'bottom_right'])
AnnotationGroup = namedtuple('AnnotationGroup', ['name', 'color', 'shapes'])
Color = namedtuple('Color', ['red', 'green', 'blue'])

__all__ = [
    'render_page',
    'make_annotations',
]


def draw_line(context, line):
    context.move_to(line.start.x, line.start.y)
    context.line_to(line.end.x, line.end.y)
    context.stroke()


def draw_polygon(context, polygon):
    if len(polygon.points) == 0:
        return

    first_point = polygon.points[0]

    context.move_to(first_point.x, first_point.y)
    for line in polygon.points[1:]:
        context.line_to(line.x, line.y)

    context.stroke()


def draw_rectangle(context, rectangle):
    width = abs(rectangle.bottom_right.x - rectangle.top_left.x)
    height = abs(rectangle.bottom_right.y - rectangle.top_left.y)

    context.rectangle(rectangle.top_left.x,
                      rectangle.top_left.y,
                      width,
                      height)
    context.stroke()


RENDERERS = {}
RENDERERS[Line] = draw_line
RENDERERS[Rectangle] = draw_rectangle
RENDERERS[Polygon] = draw_polygon


class CairoPdfPageRenderer(object):

    def __init__(self, pdf_page, svg_filename, png_filename):
        self._svg_filename = abspath(svg_filename)
        self._png_filename = abspath(png_filename) if png_filename else None
        self._context, self._surface = self._get_context(
            svg_filename, *pdf_page.get_size())

        white = poppler.Color()
        white.red = white.green = white.blue = 65535
        black = poppler.Color()
        black.red = black.green = black.blue = 0
        # red = poppler.Color()
        # red.red = red.green = red.blue = 0
        # red.red = 65535

        width = pdf_page.get_size()[0]

        # We render everything 3 times, moving
        # one page-width to the right each time.
        self._offset_colors = [
            (0, white, white, True),
            (width, black, white, True),
            (2 * width, black, black, False)
        ]

        for offset, fg_color, bg_color, render_graphics in self._offset_colors:
            # Render into context, with a different offset
            # each time.
            self._context.save()
            self._context.translate(offset, 0)

            sel = poppler.Rectangle()
            sel.x1, sel.y1 = (0, 0)
            sel.x2, sel.y2 = pdf_page.get_size()

            if render_graphics:
                pdf_page.render(self._context)

            pdf_page.render_selection(
                self._context, sel, sel, poppler.SELECTION_GLYPH,
                fg_color, bg_color)

            self._context.restore()

    @staticmethod
    def _get_context(filename, width, height):
        SCALE = 1
        # left, middle, right
        N_RENDERINGS = 3

        surface = cairo.SVGSurface(
            filename, N_RENDERINGS * width * SCALE, height * SCALE)
        # srf = cairo.ImageSurface(
        #          cairo.FORMAT_RGB24, int(w*SCALE), int(h*SCALE))

        context = cairo.Context(surface)
        context.scale(SCALE, SCALE)

        # Set background color to white
        context.set_source_rgb(1, 1, 1)
        context.paint()

        return context, surface

    def draw(self, shape, color):
        self._context.save()
        self._context.set_line_width(1)
        self._context.set_source_rgba(color.red,
                                      color.green,
                                      color.blue,
                                      0.5)
        self._context.translate(self._offset_colors[1][0], 0)
        RENDERERS[type(shape)](self._context, shape)
        self._context.restore()

    def flush(self):
        if self._png_filename is not None:
            self._surface.write_to_png(self._png_filename)

        # NOTE! The flush is rather expensive, since it writes out the svg
        # data. The profile will show a large amount of time spent inside it.
        # Removing it won't help the execution time at all, it will just move
        # it somewhere that the profiler can't see it
        # (at garbage collection time)
        self._surface.flush()
        self._surface.finish()


def render_page(pdf_filename, page_number, annotations, svg_file=None,
                png_file=None):
    """
    Render a single page of a pdf with graphical annotations added.
    """

    page = extract_pdf_page(pdf_filename, page_number)

    renderer = CairoPdfPageRenderer(page, svg_file, png_file)
    for annotation in annotations:
        assert isinstance(annotation, AnnotationGroup), (
            "annotations: {0}, annotation: {1}".format(
                annotations, annotation))
        for shape in annotation.shapes:
            renderer.draw(shape, annotation.color)

    renderer.flush()


def extract_pdf_page(filename, page_number):
    file_uri = "file://{0}".format(abspath(filename))
    doc = poppler.document_new_from_file(file_uri, "")

    page = doc.get_page(page_number)

    return page


def make_annotations(table_container):
    """
    Take the output of the table-finding algorithm (TableFinder) and create
    AnnotationGroups. These can be drawn on top of the original PDF page to
    visualise how the algorithm arrived at its output.
    """

    annotations = []

    annotations.append(
        AnnotationGroup(
            name='all_glyphs',
            color=Color(0, 1, 0),
            shapes=convert_rectangles(table_container.all_glyphs)))

    annotations.append(
        AnnotationGroup(
            name='all_words',
            color=Color(0, 0, 1),
            shapes=convert_rectangles(table_container.all_words)))

    annotations.append(
        AnnotationGroup(
            name='text_barycenters',
            color=Color(0, 0, 1),
            shapes=convert_barycenters(table_container.all_glyphs)))

    annotations.append(
        AnnotationGroup(
            name='hat_graph_vertical',
            color=Color(0, 1, 0),
            shapes=make_hat_graph(
                table_container._y_point_values,
                table_container._center_lines,
                direction="vertical")))

    for table in table_container:
        annotations.append(
            AnnotationGroup(
                name='row_edges',
                color=Color(1, 0, 0),
                shapes=convert_horizontal_lines(
                    table.row_edges, table.bounding_box)))

        annotations.append(
            AnnotationGroup(
                name='column_edges',
                color=Color(1, 0, 0),
                shapes=convert_vertical_lines(
                    table.column_edges, table.bounding_box)))

        annotations.append(
            AnnotationGroup(
                name='glyph_histogram_horizontal',
                color=Color(1, 0, 0),
                shapes=make_glyph_histogram(
                    table._x_glyph_histogram, table.bounding_box,
                    direction="horizontal")))

        annotations.append(
            AnnotationGroup(
                name='glyph_histogram_vertical',
                color=Color(1, 0, 0),
                shapes=make_glyph_histogram(
                    table._y_glyph_histogram, table.bounding_box,
                    direction="vertical")))

        annotations.append(
            AnnotationGroup(
                name='horizontal_glyph_above_threshold',
                color=Color(0, 0, 0),
                shapes=make_thresholds(
                    table._x_threshold_segs, table.bounding_box,
                    direction="horizontal")))

        annotations.append(
            AnnotationGroup(
                name='vertical_glyph_above_threshold',
                color=Color(0, 0, 0),
                shapes=make_thresholds(
                    table._y_threshold_segs, table.bounding_box,
                    direction="vertical")))

    # Draw bounding boxes last so that they appear on top
    annotations.append(
        AnnotationGroup(
            name='table_bounding_boxes',
            color=Color(0, 0, 1),
            shapes=convert_rectangles(table_container.bounding_boxes)))

    return annotations


def make_thresholds(segments, box, direction):
    lines = []

    for segment in segments:

        if direction == "horizontal":
            lines.append(Line(Point(segment.start, box.bottom + 10),
                              Point(segment.end, box.bottom + 10)))
        else:
            lines.append(Line(Point(10, segment.start),
                              Point(10, segment.end)))

    return lines


def make_hat_graph(hats, center_lines, direction):
    """
    Draw estimated text barycenter
    """

    max_value = max(v for _, v in hats)
    DISPLAY_WIDTH = 25

    points = []
    polygon = Polygon(points)

    def point(x, y):
        points.append(Point(x, y))

    for position, value in hats:
        point(((value / max_value - 1) * DISPLAY_WIDTH), position)

    lines = []
    for position in center_lines:
        lines.append(Line(Point(-DISPLAY_WIDTH, position),
                          Point(0, position)))

    return [polygon] + lines


def make_glyph_histogram(histogram, box, direction):

    # if direction == "vertical":
        # return []

    bin_edges, bin_values = histogram

    if not bin_edges:
        # There are no glyphs, and nothing to render!
        return []

    points = []
    polygon = Polygon(points)

    def point(x, y):
        points.append(Point(x, y))

    # def line(*args):
        # lines.append(Line(*args))
    previous_value = 0 if direction == "horizontal" else box.bottom

    x = zip(bin_edges, bin_values)
    for edge, value in x:

        if direction == "horizontal":
            value *= 0.75
            value = box.bottom - value

            point(edge, previous_value)
            point(edge, value)

        else:
            value *= 0.25
            value += 7  # shift pixels to the right

            point(previous_value, edge)
            point(value, edge)

        previous_value = value

    # Final point is at 0
    if direction == "horizontal":
        point(edge, 0)
    else:
        point(box.bottom, edge)

    # Draw edge density plot (not terribly interesting, should probably be
    #  deleted)
    # lines = []
    # if direction == "horizontal":
    #     for edge in bin_edges:
    #         lines.append(Line(Point(edge, box.bottom),
    #                           Point(edge, box.bottom + 5)))
    # else:
    #     for edge in bin_edges:
    #         lines.append(Line(Point(0, edge), Point(5, edge)))
    return [polygon]  # + lines


def convert_rectangles(boxes):
    return [Rectangle(Point(b.left, b.top), Point(b.right, b.bottom))
            for b in boxes]


def convert_barycenters(boxes):
    return [Line(Point(b.left, b.barycenter.midpoint),
                 Point(b.right, b.barycenter.midpoint))
            for b in boxes if b.barycenter is not None]


def convert_horizontal_lines(y_edges, bbox):
    return [Line(Point(bbox.left, y), Point(bbox.right, y))
            for y in y_edges]


def convert_vertical_lines(x_edges, bbox):
    return [Line(Point(x, bbox.top), Point(x, bbox.bottom))
            for x in x_edges]

if __name__ == '__main__':
    annotations = [
        AnnotationGroup(
            name='',
            color=Color(1, 0, 0),
            shapes=[Rectangle(Point(100, 100), Point(200, 200))])
    ]
    render_page(sys.argv[1], 0, annotations)
