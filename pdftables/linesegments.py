"""
Algorithms for processing line segments

segments_generator

    Yield segments in order of their start/end.

    [(1, 4), (2, 3)] => [(1, (1, 4)), (2, (2, 3)), (3, (2, 3)), (4, (1, 4))]

histogram_segments

    Number of line segments present in each given range

    [(1, 4), (2, 3)] => [((1, 2), 1), ((2, 3), 2), ((3, 4), 1)]

segment_histogram

    Binning for a histogram and the number of counts in each bin

    [(1, 4), (2, 3)] => [(1, 2, 3, 4), (1, 2, 1)]
"""

from collections import defaultdict
from heapq import heappush, heapreplace, heappop

def segments_generator(line_segments):
    """
    Given the a list of segment ranges [(start, stop)...], yield the list of
    coordinates where any line segment starts or ends along with the line
    segment which starts/ends at that coordinate.

    In [1]: list(linesegments.segments_generator([(1, 4), (2, 3)]))
    Out[1]: [(1, (1, 4)), (2, (2, 3)), (3, (2, 3)), (4, (1, 4))]

    """

    # Queue contains a list of outstanding segments to process. It is a list
    # of tuples, [(position, (start, end)], where (start, end) represents one
    # line-segment. `position` is the coordinate at which the line-segment) is
    # to be considered again.
    queue = []

    # (Note, this has the effect of sorting line_segments in start order)
    for segment in line_segments:
        start, end = segment
        if not start < end:
            raise RuntimeError("Malformed line segment input")
        heappush(queue, (start, (segment)))
    
    # Process outstanding segments
    while queue:
        # Get the next segment to consider and the position at which we're
        # considering it
        position, segment = heappop(queue)
        
        yield position, segment

        start, end = segment
        if position == start:
            # This is the `start` of the line segment. It needs to be considered
            # again at the `end`, so schedule it.
            heappush(queue, (end, segment))

def histogram_segments(segments):
    """
    Given a list of histogram segments returns ((start, end), n_segments)
    which represents a histogram projection of the number of segments onto a line.

    In [1]: list(linesegments.histogram_segments([(1, 4), (2, 3)]))
    Out[1]: [((1, 2), 1), ((2, 3), 2), ((3, 4), 1)]
    """

    # sum(.values()) is the number of segments within (start, end)
    active_segments = defaultdict(int)

    consider_segments = list(segments_generator(segments))

    # Look ahead to the next start, and that's the end of the interesting range
    for this, next in zip(consider_segments, consider_segments[1:]):

        # (start, end) is the range until the next segment
        (start, seg), (end, _) = this, next

        # The (seg_start, seg_end) of the segment being considered
        seg_start, seg_end = seg

        # Did the segment appear or disappear? Key on the segment coordinates
        if start == seg_start:
            active_segments[seg] += 1

        elif start == seg_end:
            active_segments[seg] -= 1

        else:
            raise RuntimeError("Malformed input")
        
        if start == end:
            # This happens if a segment appears more than once.
            # Then we don't care about considering this zero-length range.
            continue


        n_active_segments = sum(active_segments.values())
        yield (start, end), n_active_segments

def segment_histogram(line_segments):
    """
    Binning for a histogram and the number of counts in each bin.
    Can be used to make a numpy.histogram.

    In [1]: list(linesegments.histogram_segments([(1, 4), (2, 3)]))
    Out[1]: [(1, 2, 3, 4), (1, 2, 1)]
    """
    data = histogram_segments(line_segments)
    x, counts = zip(*data)
    starts, ends = zip(*x)

    return starts + (ends[-1],), counts
