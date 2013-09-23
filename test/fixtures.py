
from os.path import abspath, dirname, join as pjoin

from pdftables.pdf_document import PDFDocument

memoized = {}


def fixture(filename):
    """
    Obtain a PDFDocument for fixtures/sample_data/{filename}, memoizing the
    return result.
    """
    global memoized

    if filename in memoized:
        return memoized.get(filename)
    here = abspath(dirname(__file__))
    fn = pjoin(here, "..", "fixtures", "sample_data", filename)
    memoized[filename] = PDFDocument.from_path(fn)
    return memoized[filename]
