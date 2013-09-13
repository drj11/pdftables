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
from pdftables.pdf_document import PDFDocument

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

def check(path):
    fileobj = open(path, 'rb')
    doc = PDFDocument.from_fileobj(fileobj)
    tables = pdftables.page_to_tables(doc.get_page(0))
    print tables
