#!/usr/bin/env python

import warnings


class ConfigParameters(object):
    """
    Controls how tables are detected, extracted etc.
    Be Careful! If you add a new parameter:

    1) The default value should be equivalent to the previous behaviour
    2) You're committing to retaining its default value forever(ish)! People
       will write code which relies on the default value today, so changing
       that will give them unexpected behaviour.
    """
    def _validate_hint(self, hint):
        return hint

    def __init__(
            self,
            extend_y=False,

            table_top_hint=None,
            table_bottom_hint=None,

            n_glyph_column_threshold=3,
            n_glyph_row_threshold=5
        ):

        self.extend_y = extend_y

        self.table_top_hint = self._validate_hint(table_top_hint)
        self.table_bottom_hint = self._validate_hint(table_bottom_hint)

        self.n_glyph_column_threshold = n_glyph_column_threshold
        self.n_glyph_row_threshold = n_glyph_row_threshold


