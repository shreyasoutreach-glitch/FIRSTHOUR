"""
Merchant behavioral baseline -- the statistics the incident engine measures
every event against. Pure functions over plain numbers/datetimes so they are
trivially unit-testable and have no hidden dependency on the LLM or the API
layer. This is the "deterministic systems establish financial truth" half of
the architecture.
"""
from __future__ import annotations

import datetime as dt
import statistics
from dataclasses import dataclass, field


@dataclass
class MerchantBaseline:
    merchant_id: str
    median_payout: float
    mad_payout: float
    payout_amounts: list[float] = field(default_factory=list)
    normal_hour_start: int = 10
    normal_hour_end: int = 19
    largest_historical_payout: float = 0.0
    beneficiary_count: int = 0

    def robust_z(self, amount) -> float:
        """Robust z-score using the median + Median Absolute Deviation, so a
        single historical outlier can't quietly widen the "normal" band the
        way a mean/stddev baseline would.

        robust_z = 0.6745 * (x - median) / MAD
        """
        if self.mad_payout == 0:
            # No spread in the baseline at all -- fall back to a tiny epsilon
            # so a genuinely different amount still produces a finite,
            # very large z-score instead of a divide-by-zero.
            mad = 1e-6
        else:
            mad = self.mad_payout
        return 0.6745 * (float(amount) - float(self.median_payout)) / float(mad)

    def multiple_of_median(self, amount: float) -> float:
        if self.median_payout <= 0:
            return 0.0
        return amount / self.median_payout


def median_absolute_deviation(values: list[float], median: float | None = None) -> float:
    if not values:
        return 0.0
    m = median if median is not None else statistics.median(values)
    deviations = [abs(v - m) for v in values]
    return statistics.median(deviations)


def compute_merchant_baseline(merchant_id: str, historical_payout_amounts: list[float],
                               beneficiary_count: int = 0) -> MerchantBaseline:
    if not historical_payout_amounts:
        return MerchantBaseline(merchant_id=merchant_id, median_payout=0.0, mad_payout=0.0,
                                 payout_amounts=[], beneficiary_count=beneficiary_count)
    median = statistics.median(historical_payout_amounts)
    mad = median_absolute_deviation(historical_payout_amounts, median)
    return MerchantBaseline(
        merchant_id=merchant_id,
        median_payout=median,
        mad_payout=mad,
        payout_amounts=historical_payout_amounts,
        largest_historical_payout=max(historical_payout_amounts),
        beneficiary_count=beneficiary_count,
    )


def rolling_window_stats(event_timestamps_amounts: list[tuple[dt.datetime, float]],
                          at_time: dt.datetime, window_minutes: int = 10) -> tuple[int, float]:
    """Count and sum of events in the `window_minutes` immediately preceding
    (and including) `at_time`. O(n) here, which is fine at demo scale; a
    production version would use a DB window function / sorted index scan."""
    window_start = at_time - dt.timedelta(minutes=window_minutes)
    in_window = [amt for ts, amt in event_timestamps_amounts if window_start <= ts <= at_time]
    return len(in_window), sum(in_window)


def dormancy_seconds(last_event_time: dt.datetime | None, at_time: dt.datetime) -> float:
    if last_event_time is None:
        return float("inf")
    return (at_time - last_event_time).total_seconds()


def beneficiary_age_seconds(first_seen: dt.datetime | None, at_time: dt.datetime) -> float:
    if first_seen is None:
        return float("inf")
    return (at_time - first_seen).total_seconds()
