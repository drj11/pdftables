#! /usr/bin/env python

import ctypes
from poppler import *
import poppler

from ctypes import CDLL, POINTER, c_voidp, c_double, c_uint, c_bool
from ctypes import Structure

from weakref import WeakKeyDictionary
wd = WeakKeyDictionary()


class PatchedRectangle(Structure):
    _fields_ = [
        ("x0", c_double),
        ("y0", c_double),
        ("x1", c_double),
        ("y1", c_double),
    ]
PatchedRectangle.ptr = POINTER(PatchedRectangle)

glib = CDLL("libpoppler-glib.so.8")

g_free = glib.g_free
g_free.argtypes = c_voidp,


def page_get_text_layout(page):

    fn = glib.poppler_page_get_text_layout
    fn.argtypes = c_voidp, POINTER(PatchedRectangle.ptr), POINTER(c_uint)
    fn.restype = c_bool

    n = c_uint(0)
    rects = PatchedRectangle.ptr()

    # From python-poppler internals, see also the repr(page)
    page_ptr = hash(page)

    fn(page_ptr, rects, n)
    #return []

    rs = POINTER(PatchedRectangle * n.value).from_address(ctypes.addressof(rects))

    rects = []

    rr = poppler.Rectangle()

    result = []
    for r in rs.contents:
        rect = (r.x0, r.y0, r.x1, r.y1)
        rr.x1, rr.y1, rr.x2, rr.y2 = rect
        text = None
        tw = None
        tw = page.get_selected_text(poppler.SELECTION_GLYPH, rr).decode("utf8")

        if False and result and tw.strip():
            l, _, _ = last = result[-1]
            r = rect
            if (r.x0, r.y0, r.y1) == (l.x1, r.y0, r.y1):
                nrect = l._replace(x1=r.x1)
                result[-1] = nrect, None, last[-1] + tw

        #if result and (r.x0, r.y1) == (result[-1].x1, result[-1].y1)

        result.append((rect, text, tw))

    # TODO(pwaller) check that this free is correct
    g_free(rs)

    return result
