# pdftables - a library for extracting tables from PDF files

pdftables uses [pdfminer][1] to get information on the locations of text elements in a PDF document.

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

[1]: http://www.unixuser.org/~euske/python/pdfminer/
[![Build Status](https://travis-ci.org/scraperwiki/pdftables.png)](https://travis-ci.org/scraperwiki/pdftables)

