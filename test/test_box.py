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
#from boxes import Leaf, LeafList
#import boxes

from nose.tools import assert_equals, assert_is_not

inf = float("inf")


def test_basic_boxes():
    leaf = boxes.Box(((11, 22, 33, 44), "class", "text"))
    assert_equals(leaf.bbox, (11, 22, 33, 44))
    assert_equals((11, 22, 33, 44), leaf.bbox)
    assert_equals(22, leaf.top)
    assert_equals('class', leaf.classname)
    assert_equals('text', leaf.text)


def test_clip_identity():
    """
    Test clipping a box with itself results in the same box
    """
    box1 = boxes.Box(((-inf, -inf, inf, inf), None, None))
    box2 = boxes.Box(((-inf, -inf, inf, inf), None, None))

    clipped = box1.clip(box2)
    assert_is_not(clipped, boxes.Box.empty_box)
    assert_equals(clipped.bbox, box1.bbox)


def test_clip_x_infinite():
    """
    Test correctly clipping (-inf, 0, inf, 10) with (-inf, -inf, inf, inf)
    """
    box1 = boxes.Box(((-inf, -inf, inf, inf), None, None))
    box2 = boxes.Box(((-inf, 0, inf, 10), None, None))

    clipped = box1.clip(box2)
    assert_is_not(clipped, boxes.Box.empty_box)
    assert_equals(clipped.bbox, (-inf, 0, inf, 10))
