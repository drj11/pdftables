#!/usr/bin/env python
from __future__ import unicode_literals
from collections import defaultdict


def to_string(table):
    """
    Returns a list of the maximum width for each column across all rows
    >>> to_string([['foo', 'goodbye'], ['llama', 'bar']])
    None
    """
    result = ''
    col_widths = find_column_widths(table)
    table_width = sum(col_widths) + len(col_widths) + 2
    hbar = '     {}\n'.format('-' * table_width)
    result += hbar
    for row_index, row in enumerate(table):
        cells = [cell.rjust(width, ' ') for (cell, width)
                 in zip(row, col_widths)]
        result += "{:>3}: | {}|\n".format(row_index, '|'.join(cells))
    result += hbar

    return result


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
