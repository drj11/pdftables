#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-20
# -*- coding: utf-8 -*-

"""
tree Tests
"""

import sys
sys.path.append('pdftables')

import pdftables
#from tree import Leaf, LeafList
#import tree

from nose.tools import *

def test_basic_tree():
    leaf = pdftables.tree.Leaf(((11,22,33,44),"class","text"))
    assert_equals(leaf.bbox, (11,22,33,44))
    assert_equals((11, 22, 33, 44), leaf.bbox)
    assert_equals(22, leaf.bottom)
    assert_equals('class', leaf.classname)
    assert_equals('text', leaf.text)

def test_children():
    x = [1, [2, [[3, 4]]]]
    assert_equals(len(list(pdftables.tree.children(x))), 8)
