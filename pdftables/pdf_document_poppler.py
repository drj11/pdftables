import gobject
try:
    import poppler as P
except ImportError:
    print "Poppler unavailable! Please install it."
    print "  sudo apt-get install python-poppler"
    raise

from ctypes import CDLL, POINTER, c_voidp, c_double, c_uint, c_bool, pointer
from ctypes import Structure


from .pdf_document import (
    PDFDocument as BasePDFDocument,
    PDFPage as BasePDFPage,
)

from .boxes import Box, BoxList


class PDFDocument(BasePDFDocument):

    def __init__(self, filehandle):
        old_pos = filehandle.tell()
        filehandle.seek(0)
        data = filehandle.read()
        filehandle.seek(old_pos)

        self._poppler = P.document_new_from_data(data)

    def __len__(self):
        return self._poppler.get_n_pages()

    def get_page(self, n):
        return PDFPage(self, n)


class PDFPage(BasePDFPage):

    def __init__(self, doc, n):
        self._poppler = doc.get_page(n)


#
# What follows is all related to the poppler internal API
#

class Rectangle(Structure):
    _fields_ = [
        ("x1", c_double),
        ("y1", c_double),
        ("x2", c_double),
        ("y2", c_double),
    ]
Rectangle.ptr = POINTER(Rectangle)

# TODO(pwaller): generalization? windows?
glib = CDLL("libpoppler-glib.so")

g_free = glib.g_free
g_free.argtypes = c_voidp,

_c_text_layout = glib.poppler_page_get_text_layout
_c_text_layout.argtypes = c_voidp, POINTER(Rectangle.ptr), POINTER(c_uint)
_c_text_layout.restype = c_bool


def poppler_page_get_text_layout(page):
    """
    Wrapper of an underlying c-api function not yet exposed by the
    python-poppler API.

    Returns a list of text rectangles on the pdf `page`
    """

    n = c_uint(0)
    rects = Rectangle.ptr()

    # From python-poppler internals it is known that hash(page) returns the
    # c-pointer to the underlying glib object. See also the repr(page).
    page_ptr = hash(page)

    c_text_layout(page_ptr, rects, n)

    # Obtain pointer to array of rectangles of the correct length
    rs = POINTER(Rectangle * n.value).from_address(ctypes.addressof(rects))

    rr = P.Rectangle()
    Rect = tuple

    result = []
    for r in rs.contents:
        rect = (r.x1, r.y1, r.x2, r.y2)
        rr.x1, rr.y1, rr.x2, rr.y2 = rect
        text = page.get_selected_text(P.SELECTION_GLYPH, rr).decode("utf8")

        if False and result and tw.strip():
            # TODO(pwaller): rectangle joining
            l, _, _ = last = result[-1]
            r = rect
            if (r.x1, r.y1, r.y2) == (l.x2, r.y1, r.y2):
                nrect = l._replace(x2=r.x2)
                result[-1] = nrect, None, last[-1] + text

        result.append((rect, text))

    # TODO(pwaller): check that this free is correct
    g_free(rs)

    return result
