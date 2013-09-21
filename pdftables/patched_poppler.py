#! /usr/bin/env python

import ctypes
import poppler

from ctypes import CDLL, POINTER, c_voidp, c_double, c_uint, c_bool
from ctypes import Structure, addressof

from .boxes import Box, Rectangle


class CRectangle(Structure):
    _fields_ = [
        ("x1", c_double),
        ("y1", c_double),
        ("x2", c_double),
        ("y2", c_double),
    ]
CRectangle.ptr = POINTER(CRectangle)

glib = CDLL("libpoppler-glib.so.8")

g_free = glib.g_free
g_free.argtypes = (c_voidp,)


_c_text_layout = glib.poppler_page_get_text_layout
_c_text_layout.argtypes = (c_voidp, POINTER(CRectangle.ptr), POINTER(c_uint))
_c_text_layout.restype = c_bool

GLYPH = poppler.SELECTION_GLYPH


def poppler_page_get_text_layout(page):
    """
    Wrapper of an underlying c-api function not yet exposed by the
    python-poppler API.

    Returns a list of text rectangles on the pdf `page`
    """

    n = c_uint(0)
    rects = CRectangle.ptr()

    # From python-poppler internals it is known that hash(page) returns the
    # c-pointer to the underlying glib object. See also the repr(page).
    page_ptr = hash(page)

    _c_text_layout(page_ptr, rects, n)

    # Obtain pointer to array of rectangles of the correct length
    rectangles = POINTER(CRectangle * n.value).from_address(addressof(rects))

    get_text = page.get_selected_text

    poppler_rect = poppler.Rectangle()

    result = []
    for crect in rectangles.contents:
        # result.append(Rectangle(
        #   x1=crect.x1, y1=crect.y1, x2=crect.x2, y2=crect.y2))

        _ = (crect.x1, crect.y1, crect.x2, crect.y2)
        poppler_rect.x1, poppler_rect.y1, poppler_rect.x2, poppler_rect.y2 = _

        text = get_text(GLYPH, poppler_rect).decode("utf8")

        if text.endswith(" \n"):
            text = text[:-2]
        elif text.endswith(" ") and len(text) > 1:
            text = text[:-1]
        elif text.endswith("\n"):
            text = text[:-1]

        rect = Box(
            rect=Rectangle(x1=crect.x1, y1=crect.y1, x2=crect.x2, y2=crect.y2),
            text=text,
        )
        result.append(rect)

    # TODO(pwaller): check that this free is correct
    g_free(rectangles)

    return result
