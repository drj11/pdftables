"""
Describe box-like data (such as glyphs and rects) in a PDF and helper functions
"""
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-19
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from collections import namedtuple
from counter import Counter


def _rounder(val, tol):
    """
    Utility function to round numbers to arbitrary tolerance
    """
    return round((1.0 * val) / tol) * tol


class Histogram(Counter):

    def rounder(self, tol):
        c = Histogram()
        for item in self:
            c = c + Histogram({_rounder(item, tol): self[item]})
        return c


Rectangle = namedtuple("Rectangle", "x1 y1 x2 y2")


class Box(object):

    def __init__(self, rect, text=None):

        if not isinstance(rect, Rectangle):
            raise RuntimeError("Box(x) expects isinstance(x, Rectangle)")

        self.rect = rect
        self.text = text

        return
        # TODO(pwaller): simplify and reconcile this constructor

        if type(obj) == tuple:
            (self.rect, self.classname, self.text) = obj
        else:
            if obj.__class__.__name__ != 'LTAnon':
                self.rect = obj.rect
            else:
                self.rect = (0, 0, 0, 0)
            self.classname = obj.__class__.__name__
            try:
                self.text = obj.get_text()
            except:
                self.text = ''

    def __repr__(self):
        if self is Box.empty_box:
            return "<Box rect=empty>"
        return "<Box rect={0}>".format(self.rect)

    def clip(self, *rectangles):
        """
        Return the rectangle representing the subset of this Box and all of
        rectangles. If there is no rectangle left, ``Box.empty_box`` is
        returned which always clips to the empty box.
        """

        x1, y1, x2, y2 = self.rect
        for rectangle in rectangles:
            x1 = max(x1, rectangle.left)
            x2 = min(x2, rectangle.right)
            y1 = max(y1, rectangle.top)
            y2 = min(y2, rectangle.bottom)

            if x1 > x2 or y1 > y2:
                # There is no rect left, so return the "empty set"
                return Box.empty_box

        return type(self)(Rectangle(x1=x1, y1=y1, x2=x2, y2=y2))

    @property
    def left(self):
        return self.rect[0]

    @property
    def top(self):
        return self.rect[1]

    @property
    def right(self):
        return self.rect[2]

    @property
    def bottom(self):
        return self.rect[3]

    @property
    def midline(self):
        return (self.right - self.left) / 2.

    @property
    def centreline(self):
        return (self.bottom - self.top) / 2.

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

"""
The empty box. This is necessary because we get one
when we clip two boxes that do not overlap (and
possibly in other situations).

By convention it has left at +Inf, right at -Inf, top
at +Inf, bottom at -Inf.

It is defined this way so that it is invariant under clipping.
"""
Box.empty_box = Box(Rectangle(x1=float("+inf"), y1=float("+inf"),
                              x2=float("-inf"), y2=float("-inf")))


class BoxList(list):

    def inside(self, rect):
        """
        Return a fresh instance that is the subset that is (strictly)
        inside `rect`.
        """

        def is_in_rect(box):
            return (rect.left <= box.left <= box.right <= rect.right and
                    rect.top <= box.top <= box.bottom <= rect.bottom)

        return type(self)(box for box in self if is_in_rect(box))

    def bounds(self):
        """Return the (strictest) bounding box of all elements."""
        return Box(Rectangle(
            x1=min(box.left for box in self),
            y1=min(box.top for box in self),
            x2=max(box.right for box in self),
            y2=max(box.bottom for box in self),
        ))

    def __repr__(self):
        return "BoxList(len={0})".format(len(self))

    def purge_empty_text(self):
        # TODO: BUG: we remove characters without adjusting the width / coords
        #       which is kind of invalid.

        return BoxList(box for box in self if box.text.strip()
                       or box.classname != 'LTTextLineHorizontal')

    def filterByType(self, flt=None):
        if not flt:
            return self
        return BoxList(box for box in self if box.classname in flt)

    def histogram(self, dir_fun):
        # index 0 = left, 1 = top, 2 = right, 3 = bottom
        for item in self:
            assert type(item) == Box, item
        return Histogram(dir_fun(box) for box in self)

    def count(self):
        return Counter(x.classname for x in self)
