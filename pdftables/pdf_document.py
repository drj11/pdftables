"""
Backend abstraction for PDFDocuments
"""

import abc
import os

DEFAULT_BACKEND = "pdfminer"
BACKEND = os.environ.get("PDFTABLES_BACKEND", DEFAULT_BACKEND).lower()

# TODO(pwaller): Use abstract base class?
# What does it buy us? Can we enforce that only methods specified in an ABC
# are used by client code?


class PDFDocument(object):
    __metaclass__ = abc.ABCMeta

    @classmethod
    def _get_backend(cls):
        """
        Returns the PDFDocument class to use based on configuration from
        enviornment or pdf_document.BACKEND
        """
        # If `cls` is not already a subclass of the base PDFDocument, pick one
        if not issubclass(cls, PDFDocument):
            return cls

        # Imports have to go inline to avoid circular imports with the backends
        if BACKEND == "pdfminer":
            from pdf_document_pdfminer import PDFDocument as PDFDoc
            return PDFDoc

        elif BACKEND == "poppler":
            from pdf_document_poppler import PDFDocument as PDFDoc
            return PDFDoc

        raise NotImplementedError("Unknown backend '{0}'".format(BACKEND))

    @classmethod
    def from_fileobj(cls, fh):
        Class = cls._get_backend()
        return Class(fh)

    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "Don't use this constructor, use a {0}.from_* method instead!"
            .format(self.__class__.__name__))

    @abc.abstractmethod
    def __len__(self):
        """
        Return the number of pages in the PDF
        """

    @abc.abstractmethod
    def get_page(self, number):
        """
        Return a PDFPage for page `number` (1 indexed!)
        """


class PDFPage(object):
    __metaclass__ = abc.ABCMeta

    class BoxPage:
        "Select page objects"
    class BoxGlyph:
        "Select glyph boxes"
    class BoxWord:
        "Select bounding boxes for words"
    class BoxLine:
        "Select bounding boxes for lines"

    @abc.abstractmethod
    def get_glyphs(self):
        """
        Obtain a list of bounding boxes (Box instances) for all glyphs
        on the page.
        """

    @abc.abstractproperty
    def size(self):
        """
        (width, height) of page
        """
