from ctypes import CDLL, POINTER, c_voidp, c_double, c_uint, c_bool
from ctypes import Structure, addressof, pointer
from os.path import abspath

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
        self._poppler = poppler.document_new_from_file(uri, password)

    def __len__(self):
        return self._poppler.get_n_pages()

    def get_page(self, n):
        return PDFPage(self, n)

    def get_pages(self):
        return [self.get_page(i) for i in xrange(len(self))]


class PDFPage(BasePDFPage):

    def __init__(self, doc, n):
        self._poppler = doc._poppler.get_page(n)

    @property
    def size(self):
        return self._poppler.get_size()

    def get_glyphs(self):
        # TODO(pwaller): Result of this should be memoized onto the PDFPage
        #                instance.

        text = self._poppler.get_text().decode("utf8")
        rectangles = patched_poppler.poppler_page_get_text_layout(self._poppler)

        return BoxList(Box(rect=rect, text=character)
                       for rect, character in zip(rectangles, text))
