# HARLTON-05: Event-Based Parking Pricing

> **In short: charge more for parking on busy event nights and less on quiet nights, instead of one flat rate all year.**

**Category:** Ancillary revenue
**Optimizes:** Parking revenue per space on high-demand nights
**Status:** Proposal

---

## 1. What It Is

A daily price recommendation for hotel-owned parking, both for registered guests and for public transient parkers. It responds to forecast occupancy, local events and day of week, instead of using one flat rate all year.

The model forecasts parking demand by hour and recommends a rate that fills the lot without turning away registered guests. It also flags nights when public parking should be closed early to protect guest spaces.

## 2. Why It Matters

**Parking is a high-margin, growing revenue line.**
- Across a large sample of US hotels, "parking revenues have increased by 23.1% from 2019 to 2023" [1].
- Average parking revenue was $11.53 per occupied room, and resorts earned the most at $14.85 [1].
- Parking profit margin averaged 61.3% [1].
- In 2022, parking revenue was 3.1% of total revenue for the average hotel studied [2].

**Demand is uneven and event-driven.** Parking operators already recommend "adjusting parking rates in real-time based on demand, seasonality and local events" [3]. In a destination market with concerts, fireworks, festivals and long weekends, the same space is worth far more on some nights than others. A flat rate leaves money behind on those nights and leaves spaces empty on others.

## 3. How It Will Be Solved

**Step 1: Demand forecast.** Model hourly lot occupancy from:
- hotel occupancy;
- the share of arriving guests who bring cars, by segment;
- a local event calendar;
- day of week and weather.

**Step 2: Price recommendation.**
- Set a guest rate and a public rate per day.
- Each lot or zone is treated as an agent with its own capacity.
- The coordination engine balances them so that overflow from one lot is planned, not accidental.

**Step 3: Guardrails.**
- A cap on daily price changes.
- A minimum number of spaces held for late-arriving guests.
- A clear published rate so guests are never surprised.

**Step 4: Measurement.** Revenue per space per night, lot utilization, turn-away counts and guest complaints, compared with the prior year.

**Deliverables:**
- A 30-day parking demand calendar.
- A daily rate sheet.
- A monthly revenue-per-space report.

## 4. Data Required

- Parking transactions or gate entries by hour, lot capacities, hotel occupancy and arrivals, and a local event calendar.

## 5. Risks and Assumptions

- Price changes must be visible to guests before booking where parking is mandatory. Transparency rules on advertised prices must be followed.
- Some figures below come from US data and a parking operator. Local benchmarks should be confirmed in a pilot.

## 6. References

1. Hotel News Resource (CBRE data), *Parking and EV Stations Charge U.S. Hotel Performance* (Sep 2024). https://www.hotelnewsresource.com/article133080.html
2. CBRE, *As Occupancy Stalls, Parking Drives Hotel Revenue Growth* (Jul 2023). https://www.cbre.com/insights/briefs/as-occupancy-stalls-parking-drives-hotel-revenue-growth
3. Hotel Business (Towne Park, parking operator), *Parking as a source of revenue for hotels*. https://hotelbusiness.com/parking-as-a-source-of-revenue-for-hotels/
