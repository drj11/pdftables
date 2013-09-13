#!/usr/bin/env python

import sys
from collections import namedtuple
import patched_poppler as poppler
import cairo

from os.path import abspath

Point = namedtuple('Point', ['x', 'y'])
Line = namedtuple('Line', ['start', 'end'])
Rectangle = namedtuple('Rectangle', ['top_left', 'bottom_right'])
Annotation = namedtuple('Annotation', ['name', 'colour', 'shapes'])
Colour = namedtuple('Colour', ['red', 'green', 'blue'])

__all__ = [
    'render_page',
    'make_annotations',
]


def draw_line(context, line):
    context.move_to(line.start.x, line.start.y)
    context.line_to(line.end.x, line.end.y)


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


class CairoPdfPageRenderer(object):
    def __init__(self, pdf_page, svg_filename, png_filename):
        self._svg_filename = abspath(svg_filename)
        self._png_filename = abspath(png_filename) if png_filename else None
        self._context, self._surface = self._get_context(
            svg_filename, *pdf_page.get_size())

        pdf_page.render(self._context)

    @staticmethod
    def _get_context(filename, width, height):
        scale = 1
        surface = cairo.SVGSurface(
            filename, width * scale, height * scale)
        #srf = cairo.ImageSurface(
        #          cairo.FORMAT_RGB24, int(w*scale), int(h*scale))
        context = cairo.Context(surface)
        context.scale(scale, scale)

        context.set_source_rgb(1, 1, 1)
        context.paint()

        return context, surface

    def draw(self, shape, colour):
        self._context.set_line_width(1)
        self._context.set_source_rgba(colour.red,
                                      colour.green,
                                      colour.blue,
                                      0.5)
        RENDERERS[type(shape)](self._context, shape)

    def flush(self):
        if self._png_filename is not None:
            self._surface.write_to_png(self._png_filename)

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
        for shape in annotation.shapes:
            renderer.draw(shape, annotation.colour)

    renderer.flush()


def extract_pdf_page(filename, page_number):
    file_uri = "file://{0}".format(abspath(filename))
    doc = poppler.document_new_from_file(file_uri, "")

    page = doc.get_page(page_number)

    return page


def make_annotations(table_container):
    """
    Take the output of the table-finding algorithm (TableFinder) and create
    Annotations. These can be drawn on top of the original PDF page to
    visualise how the algorithm arrived at its output.
    """

    annotations = []

    annotations.append(
        Annotation(
            name='table_bounding_boxes',
            colour=Colour(1, 0, 0),
            shapes=convert_rectangles(table_container.bounding_boxes)))

    annotations.append(
        Annotation(
            name='all_glyphs',
            colour=Colour(0, 1, 0),
            shapes=convert_rectangles(table_container.all_glyphs)))

    for table in table_container:
        annotation = Annotation(
            name='row_edges',
            colour=Colour(0, 0, 1),
            shapes=convert_horizontal_lines(
                table.row_edges, table.bounding_box))
        print(annotation)
        annotations.append(annotation)

        annotations.extend(
            Annotation(
                name='column_edges',
                colour=Colour(0, 0, 1),
                shapes=convert_vertical_lines(
                    table.column_edges, table.bounding_box)))

    return annotations


def convert_rectangles(boxes):
    return [Rectangle(Point(b.left, b.top), Point(b.right, b.bottom))
            for b in boxes]


def convert_horizontal_lines(y_edges, bbox):
    return [Line(Point(bbox.left, y), Point(bbox.right, y))
            for y in y_edges]


def convert_vertical_lines(x_edges, bbox):
    return [Line(Point(x, bbox.top), Point(x, bbox.bottom))
            for x in x_edges]

if __name__ == '__main__':
    annotations = [
        Annotation(
            name='',
            colour=Colour(1, 0, 0),
            shapes=[Rectangle(Point(100, 100), Point(200, 200))])
    ]
    render_page(sys.argv[1], 0, annotations)
