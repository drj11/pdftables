#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-19
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
"""
tree classes which hold the parsed PDF document data
"""

import collections
from counter import Counter

def _rounder(val,tol):
     """
     Utility function to round numbers to arbitrary tolerance
     """
     return round((1.0*val)/tol)*tol

class Histogram(Counter):
    def rounder(self, tol):
        c = Histogram()
        for item in self:
            c = c + Histogram({_rounder(item, tol): self[item]})
        return c

class Leaf(object):
    def __init__(self, obj):
        if type(obj)==tuple:
            (self.bbox, self.classname, self.text) = obj
        else:
            if obj.__class__.__name__ != 'LTAnon':
                self.bbox = obj.bbox
            else:
                self.bbox = (0, 0, 0, 0)
            self.classname = obj.__class__.__name__
            try:
                self.text = obj.get_text()
            except:
                self.text = ''

        (self.left, self.bottom, self.right, self.top) = self.bbox
        self.midline = (self.top+self.bottom)/2.0
        self.centreline = (self.left+self.right)/2.0
        self.width = self.right-self.left

    def __getitem__(self, i):
        """backwards-compatibility helper, don't use it!"""
        error = ("DEPRECATED: don't use leaf[x] - use these instead: "
                 "[0]: bbox, [1]: classname, [2]: text")
        raise RuntimeError(error)

        return [self.bbox, self.classname, self.text][i]

    def _left(self):
        return self.bbox[0]

    def _bottom(self):
        return self.bbox[1]

    def _right(self):
        return self.bbox[2]

    def _top(self):
        return self.bbox[3]

    def _midline(self):
        return self.midline

    def _centreline(self):
        return self.centreline

def children(obj):
    """get all descendants of nested iterables"""
    if isinstance(obj, collections.Iterable):
        for child in obj:
            for node in children(child):
                yield node
    yield obj

class LeafList(list):
    def purge_empty_text(self):
        return LeafList(box for box in self if box.text.strip()
                            or box.classname != 'LTTextLineHorizontal')

    def filterByType(self, flt=None):
        if not flt: return self
        return LeafList(box for box in self if box.classname in flt)

    def histogram(self, dir_fun):
        # index 0 = left, 1 = top, 2 = right, 3 = bottom
        for item in self:
            assert type(item)==Leaf, item
        return Histogram(dir_fun(box) for box in self)

    def populate(self, pdfpage, interested=['LTPage','LTTextLineHorizontal']):
    # def populate(self, pdfpage, interested=['LTPage','LTChar']):
        for obj in children(pdfpage):
            if not interested or obj.__class__.__name__ in interested:
                self.append(Leaf(obj))
        return self

    def count(self):
        return Counter(x.classname for x in self)
