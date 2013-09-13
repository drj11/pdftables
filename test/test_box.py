#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-20
# -*- coding: utf-8 -*-

"""
boxes Tests
"""

import sys
sys.path.append('pdftables')

import pdftables
import pdftables.boxes as boxes


from boxes import Box, BoxList, Rectangle

from nose.tools import assert_equals, assert_is_not

inf = float("inf")


def test_basic_boxes():
    box = Box(Rectangle(11, 22, 33, 44), "text")
    assert_equals(box.rect, (11, 22, 33, 44))
    assert_equals((11, 22, 33, 44), box.rect)
    assert_equals(22, box.top)
    assert_equals('text', box.text)


def test_clip_identity():
    """
    Test clipping a box with itself results in the same box
    """
    box1 = Box(Rectangle(-inf, -inf, inf, inf))
    box2 = Box(Rectangle(-inf, -inf, inf, inf))

    clipped = box1.clip(box2)
    assert_is_not(clipped, Box.empty_box)
    assert_equals(clipped.rect, box1.rect)


def test_clip_x_infinite():
    """
    Test correctly clipping (-inf, 0, inf, 10) with (-inf, -inf, inf, inf)
    """
    box1 = Box(Rectangle(-inf, -inf, inf, inf))
    box2 = Box(Rectangle(-inf, 0, inf, 10))

    clipped = box1.clip(box2)
    assert_is_not(clipped, Box.empty_box)
    assert_equals(clipped.rect, (-inf, 0, inf, 10))


def test_boxlist_inside():
    b = BoxList()
    b.append(Box(Rectangle(0, 0, 10, 10)))

    infrect = Box(Rectangle(-inf, -inf, inf, inf))

    assert_equals(1, len(b.inside(infrect)))
    assert_equals(0, len(b.inside(Box.empty_box)))


def test_boxlist_inside_not_inside():
    b = BoxList()
    b.append(Box(Rectangle(0, 0, 10, 10)))

    otherbox = Box(Rectangle(-100, -100, -90, -90))
    assert_equals(0, len(b.inside(otherbox)))
