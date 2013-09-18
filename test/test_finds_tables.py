#!/usr/bin/env python
# ScraperWiki Limited
# Ian Hopkinson, 2013-06-17
# -*- coding: utf-8 -*-

"""
Finds tables tests
"""

import sys

import pdftables
from pdftables.config_parameters import ConfigParameters

from fixtures import fixture

from nose.tools import assert_equals


def test_atomise_does_not_disrupt_table_finding():
    pdf_page = fixture(
        "13_06_12_10_36_58_boletim_ingles_junho_2013.pdf").get_page(3)
    tables1 = pdftables.page_to_tables(
        pdf_page,
        ConfigParameters(
            atomise=True,
            extend_y=False))
    tables2 = pdftables.page_to_tables(
        pdf_page,
        ConfigParameters(
            atomise=False,
            extend_y=False))

    assert_equals(tables1.tables[0].data, tables2.tables[0].data)
