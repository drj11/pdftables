#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-08-02
# -*- coding: utf-8 -*-

"""
Implement numpy.diff, numpy.arange and numpy.average to remove numpy dependency
"""

import math


def diff(input_array):
    '''
    First order differences for an input array

    >>> diff([1,2,3,4])
    [1, 1, 1]
    '''
    result = []
    for i in range(0, len(input_array) - 1):
        result.append(input_array[i + 1] - input_array[i])
    return result


def arange(start, stop, stepv):
    '''
    Generate a list of float values given start, stop and step values

    >>> arange(0, 2, 0.1)
    [ 0. ,  0.1,  0.2,  0.3,  0.4,  0.5,  0.6,  0.7,  0.8,  0.9,  1. ,
        1.1,  1.2,  1.3,  1.4,  1.5,  1.6,  1.7,  1.8,  1.9]
    '''
    count = int(math.ceil(float(stop - start) / float(stepv)))
    result = [None, ] * count
    result[0] = start
    for i in xrange(1, count):
        result[i] = result[i - 1] + stepv

    return result


def average(input_array):
    '''
    Average a 1D array of values

    >>> average([1,2,3,4])
    2.5
    '''
    return float(sum(input_array)) / float(len(input_array))
