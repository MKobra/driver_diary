from collections.abc import Iterable
from datetime import date

from app.models import DaySummary, PaymentSummary, Trip


def calculate_summary(trips: Iterable[Trip], selected_date: date) -> DaySummary:
    daily_trips = [trip for trip in trips if trip.start.date() == selected_date]
    payment_totals = {
        "cash": PaymentSummary(),
        "card": PaymentSummary(),
    }

    for trip in daily_trips:
        payment_summary = payment_totals[trip.payment]
        payment_summary.trips_count += 1
        payment_summary.revenue += trip.amount
        payment_summary.commission += trip.commission
        payment_summary.net += trip.amount - trip.commission

    revenue = sum(trip.amount for trip in daily_trips)
    commission = sum(trip.commission for trip in daily_trips)
    return DaySummary(
        date=selected_date,
        trips_count=len(daily_trips),
        revenue=revenue,
        commission=commission,
        net=revenue - commission,
        cash=payment_totals["cash"],
        card=payment_totals["card"],
    )
