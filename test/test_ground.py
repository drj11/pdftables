from pdftables.pdf_document import PDFDocument
from pdftables.pdftables import page_to_tables
import lxml.etree
from collections import Counter
from nose.tools import assert_equals


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
        response = "<ResultTable: {col}x{row} +{plus} -{minus}>"
        return response.format(col=self.number_of_cols,
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



def _test_ground(filebase, number):
    """tests whether we successfully parse ground truth data:
    see fixtures/eu-dataset"""
    pdf_tables = pdf_results(filebase % (number, ".pdf"))
    xml_tables = xml_results(filebase % (number, "-str.xml"))
    assert_equals(len(pdf_tables), len(xml_tables))
    for i in range(0, len(pdf_tables)):
        pdf_table = pdf_tables[i]
        xml_table = xml_tables[i]
        diff = pdf_table - xml_table
        clean_diff_list = {x:diff.cells[x] for x in diff.cells if diff.cells[x] != 0}
        assert_equals(pdf_table.number_of_cols, xml_table.number_of_cols)
        assert_equals(pdf_table.number_of_rows, xml_table.number_of_rows)
        assert_equals(clean_diff_list, {})

def test_all_eu():
    filebase = "fixtures/eu-dataset/eu-%03d%s"
    for i in range(1,35):  # 1..34
        yield _test_ground, filebase, i

