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

from nose.tools import assert_equals


def test_basic_boxes():
    leaf = boxes.Box(((11, 22, 33, 44), "class", "text"))
    assert_equals(leaf.bbox, (11, 22, 33, 44))
    assert_equals((11, 22, 33, 44), leaf.bbox)
    assert_equals(22, leaf.bottom)
    assert_equals('class', leaf.classname)
    assert_equals('text', leaf.text)
