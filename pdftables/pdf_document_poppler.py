from ctypes import CDLL, POINTER, c_voidp, c_double, c_uint, c_bool
from ctypes import Structure, addressof, pointer
from os.path import abspath


import cairo
import gobject
try:
    import poppler
except ImportError:
    print "Poppler unavailable! Please install it."
    print "  sudo apt-get install python-poppler"
    raise

import patched_poppler

from .boxes import Box, BoxList
from .pdf_document import (
    PDFDocument as BasePDFDocument,
    PDFPage as BasePDFPage,
)


class PDFDocument(BasePDFDocument):

    def __init__(self, file_path, password=""):
        uri = "file://{0}".format(abspath(file_path))
        self._poppler_page = poppler.document_new_from_file(uri, password)

    def __len__(self):
        return self._poppler_page.get_n_pages()

    def get_page(self, n):
        return PDFPage(self, n)

    def get_pages(self):
        return [self.get_page(i) for i in xrange(len(self))]


class PDFPage(BasePDFPage):

    def __init__(self, doc, n):
        self._poppler_page = doc._poppler_page.get_page(n)

    @property
    def size(self):
        return self._poppler_page.get_size()

    def get_glyphs(self):
        gtl = patched_poppler.poppler_page_get_text_layout
        rectangles = gtl(self._poppler_page)

        return BoxList(rectangles)

        # TODO(pwaller): Salvage this.
        #
        # Poppler seems to lie to us because the assertion below fails.
        # It should return the same number of rectangles as there are
        # characters in the text, but it does not.
        # See:
        #
        # http://www.mail-archive.com/poppler
        #        @lists.freedesktop.org/msg06245.html
        # https://github.com/scraperwiki/pdftables/issues/89
        # https://bugs.freedesktop.org/show_bug.cgi?id=69608

        text = self._poppler_page.get_text().decode("utf8")

        # assert len(text) == len(rectangles), (
        #     "t={0}, r={1}".format(len(text), len(rectangles)))

        # assert False

        return BoxList(Box(rect=rect, text=character)
                       for rect, character in zip(rectangles, text))
