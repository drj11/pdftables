"""pdftables-dump: obtain pdftables debugging information from pdfs

Usage:
  pdftables-dump [options] [--] (<pdfpath>[:page])...
  pdftables-dump (-h | --help)
  pdftables-dump --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  -D --debug 		Additional debug information
  -O --output-dir=<path> 	Path to write debug data to
"""

from pdftables.pdf_document import PDFDocument

from docopt import docopt


def main():
    arguments = docopt(__doc__, version='pdftables-dump experimental')

    if arguments["--debug"]:
        print(arguments)

    for pdfpath in arguments["<pdfpath>"]:
        with open(pdfpath, "rb") as fd:
            doc = PDFDocument.from_fileobj(fd)
            print doc
