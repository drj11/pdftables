#!/usr/bin/env python
"""
PDFDocument backend based on pdfminer
"""

import collections

import pdfminer.pdfparser
import pdfminer.pdfinterp
import pdfminer.pdfdevice
import pdfminer.layout
import pdfminer.converter

from .pdf_document import (
    PDFDocument as BasePDFDocument,
    PDFPage as BasePDFPage,
)

from .boxes import Box, BoxList


class PDFDocument(BasePDFDocument):

    """
    Wrapper to abstract away underlying PDF class. This is partly to simplify
    the concepts in the rest of the code to just the ones we need. And partly
    so we can, for example, change from PDFMiner to pdftoxml later if
    necessary.
    """

    @staticmethod
    def _initialise(fh):
        (doc, parser) = (pdfminer.pdfparser.PDFDocument(),
                         pdfminer.pdfparser.PDFParser(fh))

        parser.set_document(doc)
        doc.set_parser(parser)

        doc.initialize('')
        if not doc.is_extractable:
            raise ValueError(
                "pdfminer.pdfparser.PDFDocument is_extractable != True")
        la_params = pdfminer.layout.LAParams()
        la_params.word_margin = 0.0

        resource_manager = pdfminer.pdfinterp.PDFResourceManager()
        aggregator = pdfminer.converter.PDFPageAggregator(
            resource_manager, laparams=la_params)

        interpreter = pdfminer.pdfinterp.PDFPageInterpreter(
            resource_manager, aggregator)

        return doc, interpreter, aggregator

    def __init__(self, fh):
        self._pages = None

        (self._doc, self._interpreter, self._device) = self._initialise(fh)

    def __len__(self):
        return len(self.get_pages())

    def get_creator(self):
        return self._doc.info[0]['Creator']  # TODO: what's doc.info ?

    def get_pages(self):
        """
        Returns a list of lazy pages (parsed on demand)
        """
        if not self._pages:
            self._construct_pages()

        return self._pages

    def get_page(self, page_number):
        """
        1-based page getter
        """
        pages = self.get_pages()
        if 1 <= page_number <= len(pages):
            return pages[page_number - 1]
        raise IndexError("Invalid page. Reminder: get_page() is 1-indexed "
                         "(there are {0} pages)!".format(len(pages)))

    def _construct_pages(self):
        self._pages = [PDFPage(self, page) for page in self._doc.get_pages()]


def children(obj):
    """
    get all descendants of nested iterables
    """
    if isinstance(obj, collections.Iterable):
        for child in obj:
            for node in children(child):
                yield node
    yield obj


class PDFPage(BasePDFPage):

    """
    Lazy page processor.
    """

    item_type_map = {
        "LTPage": BasePDFPage.BoxPage,
        "LTTextLineHorizontal": BasePDFPage.BoxLine,
        # "TODO(pwaller)": BasePDFPage.BoxWord
        "LTChar": BasePDFPage.BoxGlyph,
    }

    def __init__(self, parent_pdf_document, page):
        assert isinstance(page, pdfminer.pdfparser.PDFPage), page.__class__

        self.pdf_document = parent_pdf_document
        self._page = page
        self._lt_page = None

    def get_boxes(self, box_types):
        """
        Obtain a list of bounding boxes for objects on the page.

        box_types can be used to specify which objects to retrieve or None
        indicates that bounding boxes of all available types will be obtained.
        """

        items = children(self.lt_page())

        if box_types is None:
            return BoxList(Box(obj) for obj in items)

        def keep(o):
            cn = o.__class__.__name__
            if cn in self.item_type_map:
                return self.item_type_map[cn] in box_types
            return False

        def make_box(obj):
            # TODO: Invert y coordinates
            return Box(obj)

        return BoxList(make_box(obj) for obj in items if keep(obj))

    def lt_page(self):
        if not self._lt_page:
            self._parse_page()
        return self._lt_page

    def _parse_page(self):
        self.pdf_document._interpreter.process_page(self._page)
        self._lt_page = self.pdf_document._device.get_result()
        assert isinstance(self._lt_page, pdfminer.layout.LTPage), (
            self._lt_page.__class__)
