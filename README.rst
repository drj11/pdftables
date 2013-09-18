.. -*- mode: rst -*-

pdftables - a library for extracting tables from PDF files
==========================================================

.. image:: https://travis-ci.org/scraperwiki/pdftables.png
   :target: https://travis-ci.org/scraperwiki/pdftables
.. image:: https://pypip.in/v/pdftables/badge.png
   :target: https://pypi.python.org/pypi/pdftables

..

`This Readme, and more, is available on ReadTheDocs. <http://pdftables.readthedocs.org/>`_

`This post <http://blog.scraperwiki.com/2013/07/29/pdftables-a-python-library-for-getting-tables-out-of-pdf-files>`_
on the ScraperWiki blog describes the algorithms used in pdftables, and
something of its genesis. This README gives more technical information.

pdftables uses `pdfminer <http://www.unixuser.org/~euske/python/pdfminer/>`_ to get information on the locations of text
elements in a PDF document. pdfminer was chosen as a base because it provides
information on the full range of page elements in PDF files, including
graphical elements such as lines. Although the algorithms currently used do not
use these elements they are planned for future work. As a purely Python library,
pdfminer is very portable. The downside of pdfminer is that it is slow, perhaps
an order of magnitude slower than alternative C based libraries.

Installation
============

You need poppler and Cairo. On a Ubuntu and friends you can go:

.. code:: bash

  sudo apt-get -y install python-poppler python-cairo

Then we can install the ``pip``-able requirements from the ``requirements.txt`` file:

.. code:: bash

  pip install -r requirements.txt

Usage
=====

First we get a file object to a PDF:

.. code:: python

  filepath = 'example.pdf'
  fileobj = open(filepath,'rb')

Then we create a PDF element from the file object:

.. code:: python

  from pdftables.pdf_document import PDFDocument
  doc = PDFDocument.from_fileobj(fileobj)

Then we use the ``get_page()`` method to select a single page from the document:

.. code:: python

  from pdftables.pdftables import page_to_tables
  page = doc.get_page(pagenumber)
  tables = page_to_tables(page)

You can also loop over all pages in the PDF using ``get_pages()``:

.. code:: python

  from pdftables.pdftables import page_to_tables
  for page_number, page in enumerate(doc.get_pages()):
    tables = page_to_tables(page)

Now you have a TableContainer object, you can convert it to ASCII for quick previewing:

.. code:: python

  from pdftables.display import to_string
  for table in tables:
    print to_string(table.data)

``table.data`` is a table that has been found, in the form of a list of lists of strings
(ie: a list of rows, each containing the same number of cells).

Command line tool
=================

pdftables includes a command line tool for diagnostic rendering of pages and tables, called ``pdftables-render``.
This is installed if you ``pip install`` pdftables, or you manually run ``python setup.py``.

.. code:: bash

  $ pdftables-render example.pdf

This creates separate PNG and SVG files for each page of the specified PDF, in ``png/`` and ``svg/``, with three disagnostic displays per page.

Developing pdftables
====================

Files and folders::

  .
  |-fixtures
  | |-sample_data
  |-pdftables
  |-test

*fixtures* contains test fixtures, in particular the sample_data directory
contains PDF files which are installed from a different repository by running
the ``download_test_data.sh`` script.

We're also using data from http://www.tamirhassan.com/competition/dataset-tools.html which is also installed by the download script.

*pdftables* contains the core code files

*test* contains tests

**pdftables.py** - this is the core of the pdftables library

**counter.py** - implements collections.Counter for the benefit of Python 2.6

**display.py** - prettily prints a table by implementing the ``to_string`` function

**numpy_subset.py** - partially implements ``numpy.diff``, ``numpy.arange`` and ``numpy.average`` to avoid a large dependency on numpy.

**pdf_document.py** - implements PDFDocument to abstract away the underlying PDF class, and ease any conversion to a different underlying PDF library to replace PDFminer



