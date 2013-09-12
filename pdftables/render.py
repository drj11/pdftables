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
    'render_annotated_pdf_page',
    'Point',
    'Line',
    'Rectangle',
    'Annotation',
]


def draw_line(context, line):
    raise NotImplementedError()


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
    def __init__(self, pdf_page, svg_filename):
        self._svg_filename = abspath(svg_filename)
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
        #        self._surface.write_to_png("pngs/page-{0:02d}.png".format(i))

        self._surface.flush()
        self._surface.finish()


def render_annotated_pdf_page(pdf_filename, page_number, annotations):
    """
    Render a single page of a pdf with graphical annotations added.


    """
    page = extract_pdf_page(pdf_filename, page_number)
    renderer = CairoPdfPageRenderer(page, 'svgs/page_0.svg')

    for annotation in annotations:
        for shape in annotation.shapes:
            renderer.draw(shape, annotation.colour)

    renderer.flush()


def extract_pdf_page(filename, page_number):
    file_uri = "file://{0}".format(abspath(filename))
    doc = poppler.document_new_from_file(file_uri, "")

    page = doc.get_page(page_number)

    return page


if __name__ == '__main__':
    annotations = [
        Annotation(
            name='',
            colour=Colour(1, 0, 0),
            shapes=[Rectangle(Point(100, 100), Point(200, 200))])
    ]
    render_annotated_pdf_page(sys.argv[1], 0, annotations)
