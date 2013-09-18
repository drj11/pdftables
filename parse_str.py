from pdftables.pdf_document import PDFDocument
from pdftables.pdftables import page_to_tables
import lxml.etree
from collections import Counter


class ResultTable(object):
    def __sub__(self, other):
        r = ResultTable()
        r.cells = self.cells
        r.cells.subtract(other.cells)
        r.number_of_rows = self.number_of_rows - other.number_of_rows
        r.number_of_cols = self.number_of_cols - other.number_of_cols
        return r

    def __repr__(self):
        assert self.cells is not None
        return "<ResultTable: {col}x{row} +{plus} -{minus}>".format(col=self.number_of_cols,
                                                                    row=self.number_of_rows,
                                                                    plus=sum(self.cells[x] for x in self.cells if self.cells[x] >= 1),
                                                                    minus=abs(sum(self.cells[x] for x in self.cells if self.cells[x] <= -1)))


def pdf_results(filename):
    def get_cells(table):
        cells = Counter()
        for row in table.data:
            for cell in row:
                cells.update([cell])
        return cells

    doc = PDFDocument.from_fileobj(open(filename, "rb"))
    for page in doc.get_pages():
        table_container = page_to_tables(page)
        builder = []
        for table in table_container:
            r = ResultTable()
            r.cells = get_cells(table)
            r.number_of_rows = len(table.data)
            r.number_of_cols = max(len(row) for row in table.data)
            builder.append(r)
        return builder


def xml_results(filename):
    def max_of_strs(strs):
        return max(map(int, strs))
    root = lxml.etree.fromstring(open(filename, "rb").read())
    builder = []
    for table in root.xpath("//table"):
        r = ResultTable()
        r.cells = Counter(table.xpath("//content/text()"))
        cols = table.xpath("//@end-col")
        cols.extend(table.xpath("//@start-col"))
        rows = table.xpath("//@end-row")
        rows.extend(table.xpath("//@start-row"))
        r.number_of_cols = max_of_strs(cols) + 1  # starts at zero
        r.number_of_rows = max_of_strs(rows) + 1  # starts at zero
        builder.append(r)
    return builder


filebase = "fixtures/eu/eu-001%s"
pdf_tables = pdf_results(filebase % ".pdf")
print "PDF: ", pdf_tables[0]
xml_tables = xml_results(filebase % "-str.xml")
print "XML: ", xml_tables[0]

print list(pdf_tables)[0] - list(xml_tables)[0]
