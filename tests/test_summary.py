from datetime import date

from app.models import Trip
from app.summary import calculate_summary


def test_calculate_summary_for_selected_day() -> None:
    trips = [
        Trip(
            id="t1",
            start="2026-10-01T08:10:00+05:00",
            end="2026-10-01T08:32:00+05:00",
            amount=2400,
            payment="card",
            commission=360,
        ),
        Trip(
            id="t2",
            start="2026-10-01T09:05:00+05:00",
            end="2026-10-01T09:20:00+05:00",
            amount=1500,
            payment="cash",
            commission=225,
        ),
        Trip(
            id="other-day",
            start="2026-10-02T09:00:00+05:00",
            end="2026-10-02T09:20:00+05:00",
            amount=900,
            payment="cash",
            commission=90,
        ),
    ]

    summary = calculate_summary(trips, date(2026, 10, 1))

    assert summary.trips_count == 2
    assert summary.revenue == 3900
    assert summary.commission == 585
    assert summary.net == 3315
    assert summary.cash.trips_count == 1
    assert summary.cash.revenue == 1500
    assert summary.cash.net == 1275
    assert summary.card.trips_count == 1
    assert summary.card.revenue == 2400
    assert summary.card.net == 2040
