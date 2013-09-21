import pdftables.line_segments as line_segments

from nose.tools import assert_equals, raises


def test_segments_generator():
    values = list(line_segments.segments_generator([(1, 4), (2, 3)]))
    assert_equals([(1, (1, 4)), (2, (2, 3)), (3, (2, 3)), (4, (1, 4))], values)


def test_histogram_segments():
    values = list(line_segments.histogram_segments([(1, 4), (2, 3)]))
    assert_equals([((1, 2), 1), ((2, 3), 2), ((3, 4), 1)], values)


def test_segment_histogram():
    values = list(line_segments.segment_histogram([(1, 4), (2, 3)]))
    assert_equals([(1, 2, 3, 4), (1, 2, 1)], values)


@raises(RuntimeError)
def test_malformed_input_segments_generator():
    list(line_segments.segments_generator([(1, -1)]))


@raises(RuntimeError)
def test_malformed_input_histogram_segments():
    list(line_segments.histogram_segments([(1, -1)]))


@raises(RuntimeError)
def test_malformed_input_segment_histogram():
    list(line_segments.segment_histogram([(1, 1)]))
