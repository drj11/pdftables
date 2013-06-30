#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-17
# -*- coding: utf-8 -*-

"""
comb tests
"""

import sys
sys.path.append('code')

from pdftables import (comb, comb_extend, 
                       comb_from_uppers_and_lowers,
                       find_minima)

from nose.tools import assert_equals, raises

def test_find_minima_works_in_simplest_case():
    projection = {5:2,6:1,7:2}
    assert_equals(6,find_minima(7, 5, projection=projection))
    
def test_find_minima_function_copes_with_multiple_values_at_minima():
    pass

def test_an_ascending_comb_is_extended_correctly():
    combarray = [2, 3, 4]
    assert_equals(
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        comb_extend(combarray, 0.1, 10.5))


def test_a_descending_comb_is_extended_correctly():
    combarray = [5, 4, 3]
    assert_equals(comb_extend(combarray, 0.1, 8), [7, 6, 5, 4, 3, 2, 1])


def test_it_returns_minus_one_for_values_below_comb():
    combarray = [0, 1, 2, 3, 4, 5]
    assert_equals(comb(combarray, -1), -1)


def test_it_returns_minus_one_for_values_above_comb():
    combarray = [0, 1, 2, 3, 4, 5]
    assert_equals(comb(combarray, 6), -1)


def test_it_returns_correct_index_comb_ascending():
    combarray = [0, 1, 2, 3, 4, 5]
    assert_equals(comb(combarray, 0.5), 0)
    assert_equals(comb(combarray, 1.5), 1)
    assert_equals(comb(combarray, 4.5), 4)


def test_it_returns_correct_index_comb_descending():
    combarray = [5, 4, 3, 2, 1, 0]
    assert_equals(comb(combarray, 0.5), 4)
    assert_equals(comb(combarray, 1.5), 3)
    assert_equals(comb(combarray, 4.5), 0)


def test_comb_correctly_created_from_uppers_and_lowers():
    uppers = [100, 80, 60, 40, 20]
    lowers = [86, 66, 46, 26, 6]
    assert_equals(comb_from_uppers_and_lowers(uppers, lowers),
                  [100, 83, 63, 43, 23, 6])


@raises(Exception)
def test_raises_an_exception_for_an_unsorted_combarray():
    combarray = [5, 3, 4, 2, 1, 0]
    comb(combarray, 0.5)
