import pdftables.line_segments as line_segments

from nose.tools import assert_equals, raises

from pdftables.line_segments import LineSegment


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


def test_hat_point_generator():
    segs = segments([(1, 4), (2, 3)])
    result = list(line_segments.hat_point_generator(segs))

    x = 2.5
    expected = [(1, set()),
                (2, set([LineSegment(start=1, end=4, object=None)])),
                (x, set([LineSegment(start=1, end=4, object=None),
                         LineSegment(start=2, end=3, object=None)])),
                (3, set([LineSegment(start=1, end=4, object=None)])),
                (4, set())]

    assert_equals(expected, result)


def test_hat_generator():
    segs = segments([(0, 4), (1, 3)])
    result = list(line_segments.hat_generator(segs))

    expected = [(0, 0), (1, 0.75), (2.0, 2.0), (3, 0.75), (4, 0)]

    assert_equals(expected, result)
