#!/usr/bin/env python

"""pdftables-dump: obtain pdftables debugging information from pdfs

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

import pdftables
# Use $ pip install --editable pdftables
# to install this util in your path.

from pdftables.pdf_document import PDFDocument
from pdftables.render import render_annotated_pdf_page
from os.path import basename

from docopt import docopt


def main():
    arguments = docopt(__doc__, version='pdftables-dump experimental')

    if arguments["--debug"]:
        print(arguments)

    if arguments["--check"]:
        return check(arguments["<pdfpath>"][0])


    for pdfpath in arguments["<pdfpath>"]:
        with open(pdfpath, "rb") as fd:
            doc = PDFDocument.from_fileobj(fd)
            print doc
            for page_number, page in enumerate(doc.get_pages()):
                svg_file = 'svgs/{0}_{1}.svg'.format(
                    basename(pdfpath), page_number)
                png_file = 'pngs/{0}_{1}.png'.format(
                    basename(pdfpath), page_number)
                render_annotated_pdf_page(pdfpath, page_number, [],
                                          svg_file, png_file)


def check(path):
    fileobj = open(path, 'rb')
    doc = PDFDocument.from_fileobj(fileobj)
    tables = pdftables.page_to_tables(doc.get_page(0))
    print tables

