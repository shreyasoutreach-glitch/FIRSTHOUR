import datetime as dt

from app.services.temporal.reasoning import TimeInterval, order_events, relate


def test_precedes():
    a = TimeInterval.from_point(dt.datetime(2026, 1, 1, 10, 0, 0))
    b = TimeInterval.from_point(dt.datetime(2026, 1, 1, 10, 5, 0))
    assert relate(a, b) == "PRECEDES"
    assert relate(b, a) == "FOLLOWS"


def test_overlaps_with_imprecise_source():
    a = TimeInterval.from_point(dt.datetime(2026, 1, 1, 10, 0, 0), precision_seconds=120)
    b = TimeInterval.from_point(dt.datetime(2026, 1, 1, 10, 1, 30), precision_seconds=120)
    assert relate(a, b) == "OVERLAPS"


def test_order_events_chronological():
    base = dt.datetime(2026, 1, 1, 10, 0, 0)
    intervals = [
        ("c", TimeInterval.from_point(base + dt.timedelta(minutes=10))),
        ("a", TimeInterval.from_point(base)),
        ("b", TimeInterval.from_point(base + dt.timedelta(minutes=5))),
    ]
    assert order_events(intervals) == ["a", "b", "c"]
