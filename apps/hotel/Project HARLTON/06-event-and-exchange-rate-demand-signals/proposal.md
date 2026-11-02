# HARLTON-06: Event and Exchange-Rate Demand Signals

> **In short: add concerts, holidays, the exchange rate and cross-border travel trends to the forecast, so busy dates are spotted and priced early.**

**Category:** Revenue forecasting
**Optimizes:** Forecast accuracy for room demand, and therefore pricing decisions
**Status:** Proposal

---

## 1. What It Is

A curated set of outside demand signals, fed into the existing forecast and pricing process. These are signals that a standard booking-pace forecast does not see. They cover:

- **Event calendar:** concerts, sports, festivals, fireworks schedules, conventions, and both Canadian and US public holidays, which fall on different dates.
- **Exchange rate:** USD/CAD daily rate and trend.
- **Cross-border travel:** monthly US-resident arrivals by mode (car and air) from Statistics Canada.
- **Weather:** forecast and season.

The output is a daily "demand pressure" indicator for the next 90 days, with the reason for each spike stated in plain language. Examples: "US Thanksgiving weekend plus stadium concert; expect compression."

## 2. Why It Matters

**Events move rates far more than normal seasonality.** During a major concert tour in November 2024:
- downtown Toronto hotels averaged $779 a night on show dates;
- Toronto led Canadian markets with 76.4% occupancy for the month [1];
- downtown Vancouver reached a RevPAR of $1,269, "the highest RevPAR level on record" for that market [1].

A forecast that does not know the event is coming prices those nights too low.

**Cross-border demand shifts, and the exchange rate is only part of it.**
- Statistics Canada found that "a 10% increase in the value of the U.S. dollar only increases Americans' overnight travel to Canada by 3% to 4%" [2]. The exchange rate matters, but less than often assumed.
- US-resident arrivals to Canada fell 2.9% year over year in 2025, to 22.8 million [3].
- By March 2026, US car arrivals were up 4.7% and air arrivals up 3.0% year over year [4].

These swings are large enough to change pricing strategy for a border-market resort, and they are published monthly at no cost.

## 3. How It Will Be Solved

**Step 1: Build the signal table.** One row per future date, with columns for:
- events (with expected attendance);
- holidays in both countries;
- the exchange rate;
- latest cross-border arrival trend;
- weather.

**Step 2: Measure each signal's effect.**
- Back-test against historical occupancy and ADR to estimate how much each signal moved demand in the past.
- Drop signals that add no accuracy.

**Step 3: Demand pressure score.**
- Combine the signals into a daily score.
- Show the drivers next to the score so revenue managers can see why a date is flagged and override it.

**Step 4: Measurement.**
- Forecast error with and without the signals.
- Revenue on flagged dates compared with prior-year equivalents.

**Deliverables:**
- A 90-day demand pressure calendar.
- A weekly "dates to watch" brief.
- An accuracy report.

## 4. Data Required

- Public: Statistics Canada frontier counts, Bank of Canada exchange rates, holiday calendars, public event listings and weather.
- Internal: historical occupancy, ADR and on-the-books pace.

## 5. Risks and Assumptions

- Event effects differ by size and location. A score is only useful if each signal is validated against the property's own history.
- This tool supports the revenue manager's judgement. It does not set prices by itself.

## 6. References

1. Hospitality Net (CoStar data), *Canada's November hotel performance driven by Taylor Swift's Eras Tour* (Dec 2024). https://www.hospitalitynet.org/news/4125212.html
2. Statistics Canada, *The exchange rate and tourism* (2006). https://www150.statcan.gc.ca/n1/pub/11-402-x/2006/4007/ceb4007_001-eng.htm
3. Statistics Canada, *The Daily: Travel between Canada and other countries, December 2025*. https://www150.statcan.gc.ca/n1/daily-quotidien/260223/dq260223a-eng.htm
4. Statistics Canada, *The Daily: Travel between Canada and other countries, March 2026*. https://www150.statcan.gc.ca/n1/daily-quotidien/260521/dq260521a-eng.htm
