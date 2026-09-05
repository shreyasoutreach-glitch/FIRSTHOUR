import datetime as dt

from app.services.financial.baseline import (
    compute_merchant_baseline,
    dormancy_seconds,
    median_absolute_deviation,
    rolling_window_stats,
)


def test_median_absolute_deviation_basic():
    assert median_absolute_deviation([1, 2, 3, 4, 5]) == 1.0


def test_robust_z_zero_at_median():
    baseline = compute_merchant_baseline("M1", [10000, 12000, 18000, 20000, 22000])
    assert baseline.robust_z(baseline.median_payout) == 0.0


def test_robust_z_large_for_extreme_outlier():
    baseline = compute_merchant_baseline("M1", [18000] * 50)
    z = baseline.robust_z(1_00_00_000)
    assert z > 100  # a 555x-median payout must register as an extreme outlier


def test_multiple_of_median():
    baseline = compute_merchant_baseline("M1", [18400] * 20)
    assert baseline.multiple_of_median(1_00_00_000) == 1_00_00_000 / 18400


def test_rolling_window_stats_counts_only_inside_window():
    now = dt.datetime(2026, 1, 1, 10, 56, 21)
    events = [
        (dt.datetime(2026, 1, 1, 10, 47, 13), 1_00_00_000),
        (dt.datetime(2026, 1, 1, 10, 51, 4), 1_00_00_000),
        (dt.datetime(2026, 1, 1, 10, 56, 21), 1_00_00_000),
        (dt.datetime(2026, 1, 1, 9, 0, 0), 18000),  # outside the 10-min window
    ]
    count, total = rolling_window_stats(events, now, window_minutes=10)
    assert count == 3
    assert total == 3_00_00_000


def test_dormancy_seconds_none_is_infinite():
    assert dormancy_seconds(None, dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)) == float("inf")


def test_dormancy_seconds_computed():
    now = dt.datetime(2026, 1, 1, 12, 0, 0)
    last = now - dt.timedelta(days=5)
    assert dormancy_seconds(last, now) == 5 * 86400


def test_empty_history_baseline_has_zero_median():
    baseline = compute_merchant_baseline("M1", [])
    assert baseline.median_payout == 0.0
    assert baseline.mad_payout == 0.0
