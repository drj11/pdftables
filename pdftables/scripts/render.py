#!/usr/bin/env python

"""pdftables-render: obtain pdftables debugging information from pdfs

Usage:
    pdftables-render [options] [--] (<pdfpath>[:page])...
    pdftables-render (-h | --help)
    pdftables-render --version
    pdftables-render --check <pdfpath>

Options:
    -h --help     Show this screen.
    --version     Show version.
    -D --debug 		Additional debug information
    -O --output-dir=<path> 	Path to write debug data to
"""

# Use $ pip install --editable pdftables
# to install this util in your path.

import pdftables

from os.path import basename

from docopt import docopt

from pdftables.pdf_document import PDFDocument
from pdftables.diagnostics import render_page, make_annotations
from pdftables.pdftables import page_to_tables


def main():
    arguments = docopt(__doc__, version='pdftables-render experimental')

    if arguments["--debug"]:
        print(arguments)

    if arguments["--check"]:
        return check(arguments["<pdfpath>"][0])

    for pdf_filename in arguments["<pdfpath>"]:
        render_pdf(pdf_filename)


def render_pdf(pdf_filename):
    with open(pdf_filename, "rb") as fd:

        doc = PDFDocument.from_fileobj(fd)

        for page_number, page in enumerate(doc.get_pages()):
            svg_file = 'svgs/{0}_{1:02d}.svg'.format(
                basename(pdf_filename), page_number)
            png_file = 'pngs/{0}_{1:02d}.png'.format(
                basename(pdf_filename), page_number)

            table_container = page_to_tables(page)
            annotations = make_annotations(table_container)

            render_page(
                pdf_filename, page_number, annotations, svg_file, png_file)

            print "Rendered", svg_file, png_file


def check(path):
    fileobj = open(path, 'rb')
    doc = PDFDocument.from_fileobj(fileobj)
    tables = pdftables.page_to_tables(doc.get_page(0))
    print tables
