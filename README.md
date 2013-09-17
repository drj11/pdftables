# pdftables - a library for extracting tables from PDF files
[![Build Status](https://travis-ci.org/scraperwiki/pdftables.png?branch=master)](https://travis-ci.org/scraperwiki/pdftables)

## Installation

You need poppler and Cairo. On a Ubuntu and friends you can go:

```
sudo apt-get -y install python-poppler python-cairo
```

Then we can install the `pip`-able requirements from the
`requirements.txt` file:

```
pip install -r requirements.txt
```

## Overview

[This post](http://blog.scraperwiki.com/2013/07/29/pdftables-a-python-library-for-getting-tables-out-of-pdf-files/) on the ScraperWiki blog describes the algorithms used in pdftables, and something of its genesis. This README gives more technical information.pdftables uses [pdfminer][1] to get information on the locations of text elements in a PDF document. pdfminer was chosen as a base because it provides information on the full range of page elements in PDF files, including graphical elements such as lines. Although the algorithms currently used do not use these elements they are planned for future work. As a purely Python library, pdfminer is very portable. The downside of pdfminer is that it is slow, perhaps an order of magnitude slower than alternative C based libraries.

## Usage ##
First we get a file handle to a PDF:
```python
filepath = os.path.join(PDF_TEST_FILES,SelectedPDF)
fh = open(filepath,'rb')
```
Then we use our `get_pdf_page` function to selection a single page from the document:
```python
pdf_page = get_pdf_page(fh, pagenumber)    
table,diagnosticData = page_to_tables(pdf_page, extend_y = False, hints = hints, atomise = False)
```
Setting the optional `extend_y` parameter to `True` extends the grid used to extract the table to the full height of the page.
The optional `hints` parameter is a two element string array, the first element should contain unique text at the top of the table,
the second element should contain unique text from the bottom row of the table.
Setting the optional `atomise` parameter to True converts all the text to individual characters this will be slower but will sometimes
split closely separated columns.

`table` is a list of lists of strings. `diagnosticData` is an object containing diagnostic information which can be displayed using
the `plotpage` function:

```python
fig,ax1 = plotpage(diagnosticData)
```
## Files and Folders ##

     .
     |-fixtures
     |---actual_output
     |---expected_output
     |---sample_data
     |-pdftables
     |-test

*fixtures* contains test fixtures, in particular the sample_data directory contains PDF files which are installed from a different repository by running the ```download_test_data.sh``` script. 

The *actual\_output* and *expected\_output* directories are currently unused.

*test* contains tests

*pdftables* contains the core code files

**pdftables.py** - this is the core of the pdftables library. It contains two entry point functions (```page_to_tables``` and ```get_tables```). ```page_to_tables``` handles a single page of a document and allows the use of options in finding the table. ```get_tables``` takes a file handle and returns a list of all the tables in the document.

pdftables can also be run from the commandline:

```pdftables.py <file.pdf>``` 

Will convert all the tables found in <file.pdf> to a string format.

**counter.py** - implements collections.Counter for the benefit of Python 2.6

**display.py** - prettily prints a table by implementing the ```to_string``` function

**numpy_subset.py** - partially implements ```numpy.diff```, ```numpy.arange``` and ```numpy.average``` to avoid a large dependency on numpy.

**pdf_document.py** - implements PDFDocument to abstract away the underlying PDF class, and ease any conversion to a different underlying PDF library to replace PDFminer

**pdftables_analysis.py** - uses the matplotlib library to make visualisations of the elements found in PDF documents and also features of the table analysis algorithm

**runtables.py** - is my scientist-style harness to run pdftables, likely to be depreciated by my more software engineering colleagues!

**tree.py** - implements the structure which holds the PDF document elements on which pdftables operates. 

## Installing test set files ##

Files used in testing are stored in a separate repository and can be installed by executing the script:
```
download_test_data.sh
```

[1]: http://www.unixuser.org/~euske/python/pdfminer/

[![Build Status](https://travis-ci.org/scraperwiki/pdftables.png)](https://travis-ci.org/scraperwiki/pdftables)

