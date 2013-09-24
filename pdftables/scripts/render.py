#!/usr/bin/env python

"""pdftables-render: obtain pdftables debugging information from pdfs

Usage:
    pdftables-render [options] <pdfpath>...
    pdftables-render (-h | --help)
    pdftables-render --version

Example page number lists:

    <pdfpath> may contain a [:page-number-list].

    pdftables-render my.pdf:1
    pdftables-render my.pdf:2,5-10,15-

Example JSON config options:

    '{ "n_glyph_column_threshold": 3, "n_glyph_row_threshold": 5 }'

Options:
    -h --help                   Show this screen.
    --version                   Show version.
    -D --debug                  Additional debug information
    -O --output-dir=<path>      Path to write debug data to
    -a --ascii                  Show ascii table
    -p --pprint                 pprint.pprint() the table
    -i --interactive            jump into an interactive debugger (ipython)
    -c --config=<json>          JSON object of config parameters
    --html                      Make a webpage for the data
    --render-mode=<mode>        Set rendering parameters [default: one]
"""

# Use $ pip install --user --editable pdftables
# to install this util in your path.

import sys
import os
import json

import pdftables

from os.path import basename
from pprint import pprint

from docopt import docopt

from pdftables.pdf_document import PDFDocument
from pdftables.diagnostics import render_page, make_annotations
from pdftables.display import to_string, to_html, get_dimensions
from pdftables.pdftables import page_to_tables
from pdftables.config_parameters import ConfigParameters
import datetime


def main(args=None):

    if args is not None:
        argv = args
    else:
        argv = sys.argv[1:]

    arguments = docopt(
        __doc__,
        argv=argv,
        version='pdftables-render experimental')

    if arguments["--debug"]:
        print(arguments)

    if arguments["--config"]:
        kwargs = json.loads(arguments["--config"])
    else:
        kwargs = {}
    config = ConfigParameters(**kwargs)

    all_files = []
    for pdf_filename in arguments["<pdfpath>"]:
        all_files.extend(render_pdf(arguments, pdf_filename))

    if arguments["--html"]:
        with open("index.html", "w") as index:
            isonow = datetime.datetime.now().isoformat()
            index.write('<h1>{now}</h1>'.format(now=isonow))
            for f, info in all_files:
                index.write("""
                <span style="float:left">
                <div style="text-align:center"><b>{f}</b>
                <a href='html/{f}.html'>{dim}</a></div>
                <a href='svg/{f}.svg'>
                <img src='png/{f}.png'>
                </a>
                </span>
                """.format(f=f, dim=info['dim']))
        print "Created index.html"


def ensure_dirs(dirlist):
    for directory in dirlist:
        try:
            os.mkdir(directory)
        except OSError:
            pass


def parse_page_ranges(range_string, npages):
    ranges = range_string.split(',')
    result = []

    def string_to_pagenumber(s):
        if s == "":
            return npages
        return int(x)

    for r in ranges:
        if '-' not in r:
            result.append(int(r))
        else:
            # Convert 1-based indices to 0-based and make integer.
            points = [string_to_pagenumber(x) for x in r.split('-')]

            if len(points) == 2:
                start, end = points
            else:
                raise RuntimeError(
                    "Malformed range string: {0}"
                    .format(range_string))

            # Plus one because it's (start, end) inclusive
            result.extend(xrange(start, end + 1))

    # Convert from one based to zero based indices
    return [x - 1 for x in result]


def render_pdf(arguments, pdf_filename):
    config = ConfigParameters()
    ensure_dirs(['png', 'svg'])

    page_range_string = ''
    page_set = []
    if ':' in pdf_filename:
        pdf_filename, page_range_string = pdf_filename.split(':')

    doc = PDFDocument.from_path(pdf_filename)

    if page_range_string:
        page_set = parse_page_ranges(page_range_string, len(doc))

    output_files = []
    for page_number, page in enumerate(doc.get_pages()):
        output_file = '{0}_{1:02d}'.format(
            basename(pdf_filename), page_number)

        if page_set and page_number not in page_set:
            # Page ranges have been specified by user, and this page not in
            continue

        svg_file = 'svg/{f}.svg'.format(f=output_file)
        png_file = 'png/{f}.png'.format(f=output_file)
        html_file = 'html/{f}.html'.format(f=output_file)
        table_container = page_to_tables(page, config)
        annotations = make_annotations(table_container)

        render_page(
            pdf_filename, page_number, annotations,
            svg_file, png_file, mode=arguments['--render-mode'])

        print "Rendered", svg_file, png_file

        if arguments["--interactive"]:
            from ipdb import set_trace
            set_trace()

        if arguments["--html"]:
            ensure_dirs(['html'])
            further_info = {'dim': []}
            with open(html_file, "w") as html_handle:

            ## WRITE HEADER, GLOBAL STATS

                for i, table in enumerate(table_container):
                    html_handle.write("\n\n<h2>Tables</h2>\n")
                    dim = get_dimensions(table.data)
                    html_handle.write("%d: %r" % (i, dim))

                for i, table in enumerate(table_container):
                    html_handle.write("\n\n<h2>Table %d</h2>\n" % i)
                    html_handle.write(to_html(table.data))

        for table in table_container:

            if arguments["--ascii"]:
                print to_string(table.data)

            if arguments["--pprint"]:
                pprint(table.data)

            further_info = {"dim": get_dimensions(table.data)}
            output_files.append([output_file, further_info])

    return output_files


def check(path):
    fileobj = open(path, 'rb')
    doc = PDFDocument.from_fileobj(fileobj)
    tables = pdftables.page_to_tables(doc.get_page(0))
    print tables

if __name__ == "__main__":
    main()
