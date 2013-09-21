import pdftables.line_segments as line_segments

from nose.tools import assert_equals, raises


def segments(segments):
    return [line_segments.LineSegment.make(a, b) for a, b in segments]


def test_segments_generator():
    seg1, seg2 = segs = segments([(1, 4), (2, 3)])
    values = list(line_segments.segments_generator(segs))
    assert_equals(
        [(1, seg1, False),
         (2, seg2, False),
         (3, seg2, True),
         (4, seg1, True)],
        values
    )


def test_histogram_segments():
    segs = segments([(1, 4), (2, 3)])
    values = list(line_segments.histogram_segments(segs))
    assert_equals([((1, 2), 1), ((2, 3), 2), ((3, 4), 1)], values)


def test_segment_histogram():
    segs = segments([(1, 4), (2, 3)])
    values = list(line_segments.segment_histogram(segs))
    assert_equals([(1, 2, 3, 4), (1, 2, 1)], values)


@raises(RuntimeError)
def test_malformed_input_segments_generator():
    segs = segments([(1, -1)])
    list(line_segments.segments_generator(segs))
