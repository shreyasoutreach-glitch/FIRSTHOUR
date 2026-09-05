"""
Temporal reasoning over events of mixed precision. A bank SMS might only give
a minute; a Razorpay payout record gives a second. Rather than silently
snapping everything to one precision (which quietly invents certainty that
doesn't exist), every timestamp is represented as an interval, and ordering
relations are derived from interval overlap -- never by rewriting the
underlying source timestamp.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass
class TimeInterval:
    start: dt.datetime
    end: dt.datetime
    source_precision: str = "second"  # second/minute/hour
    source_priority: int = 0  # higher = more authoritative (e.g. Razorpay record > SMS)

    @classmethod
    def from_point(cls, ts: dt.datetime, precision_seconds: int = 0, source_priority: int = 0,
                    source_precision: str = "second") -> "TimeInterval":
        pad = dt.timedelta(seconds=precision_seconds)
        return cls(start=ts - pad, end=ts + pad, source_precision=source_precision,
                   source_priority=source_priority)


def relate(a: TimeInterval, b: TimeInterval) -> str:
    """Returns PRECEDES, FOLLOWS, OVERLAPS or SAME_TIME_WINDOW."""
    if a.end < b.start:
        return "PRECEDES"
    if b.end < a.start:
        return "FOLLOWS"
    if a.start == b.start and a.end == b.end:
        return "SAME_TIME_WINDOW"
    return "OVERLAPS"


def order_events(intervals: list[tuple[str, TimeInterval]]) -> list[str]:
    """Stable chronological order. Ties are broken by source_priority (more
    authoritative source sorts first) and then by id, never invented."""
    return [
        eid
        for eid, _ in sorted(
            intervals,
            key=lambda pair: (pair[1].start, -pair[1].source_priority, pair[0]),
        )
    ]
