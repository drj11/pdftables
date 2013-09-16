#!/usr/bin/env python
from __future__ import unicode_literals
from collections import defaultdict
from StringIO import StringIO


def to_string(table):
    """
    Returns a list of the maximum width for each column across all rows
    >>> type(to_string([['foo', 'goodbye'], ['llama', 'bar']]))
    <type 'unicode'>
    """
    result = StringIO()

    (columns, rows) = get_dimensions(table)
        
    result.write("     {} columns, {} rows\n".format(columns, rows))
    col_widths = find_column_widths(table)
    table_width = sum(col_widths) + len(col_widths) + 2
    hbar = '    {}\n'.format('-' * table_width)

    result.write("      {}\n".format(' '.join(
        [unicode(col_index).rjust(width, ' ') for (col_index, width)
         in enumerate(col_widths)])))

    result.write(hbar)
    for row_index, row in enumerate(table):
        cells = [cell.rjust(width, ' ') for (cell, width)
                 in zip(row, col_widths)]
        result.write("{:>3} | {}|\n".format(row_index, '|'.join(cells)))
    result.write(hbar)
    result.seek(0)
    return unicode(result.read())


def get_dimensions(table):
    """
    Returns columns, rows for a table.
    >>> get_dimensions([['row1', 'apple', 'llama'], ['row2', 'plum', 'goat']])
    (3, 2)
    >>> get_dimensions([['row1', 'apple', 'llama'], ['row2', 'banana']])
    (3, 2)
    """
    rows = len(table)
    try:
        cols = max(len(row) for row in table)
    except ValueError:
        cols = 0
    return (cols, rows)


def find_column_widths(table):
    """
    Returns a list of the maximum width for each column across all rows
    >>> find_column_widths([['foo', 'goodbye'], ['llama', 'bar']])
    [5, 7]
    """
    col_widths = defaultdict(lambda: 0)
    for row_index, row in enumerate(table):
        for column_index, cell in enumerate(row):
            col_widths[column_index] = max(col_widths[column_index], len(cell))
    return [col_widths[col] for col in sorted(col_widths)]

if __name__ == '__main__':
    print(to_string([['foo', 'goodbye'], ['llama', 'bar']]))
