# HARLTON-10: Historical Demand Intelligence

> **In short: study several years of past bookings to learn exactly when guests book, who they are and what was turned away, so every future rate is set from evidence.**

**Category:** Revenue analytics
**Optimizes:** The accuracy of every pricing, inventory and selling decision, by learning from several years of booking history
**Status:** Proposal

---

## 1. What It Is

A structured, repeatable analysis of three to five years of reservation history for every property in a portfolio. It answers the questions a revenue team needs answered before it can sell the next 365 days well:

- When does demand really arrive, and from whom?
- What did we turn away?
- What did we discount that we did not need to?

It is not a single report. It is a set of twelve analyses, each with a defined question, method and output, that refresh automatically. Together they feed the year-round selling strategy in [HARLTON-11](../11-year-round-occupancy-strategy/proposal.md) and the demand signals in [HARLTON-06](../06-event-and-exchange-rate-demand-signals/proposal.md).

## 2. Why It Matters

**The forecast is the foundation of revenue management.**
- Research comparing forecasting methods at two major hotel companies described the arrivals forecast as one of the key inputs to a successful revenue management system [1].
- Methods built on booking history, such as pickup models and exponential smoothing, repeatedly produced the lowest errors [1][2].
- Better forecasts come from better history, organized correctly.

**Demand has several overlapping seasonal cycles.**
- Daily hotel occupancy contains multiple seasonal periods, including weekly, monthly and annual, some of which are not whole numbers. Models that handle this explicitly outperform simpler ones [3].
- One published study used four years of daily room demand to build and test its forecasting models [4].
- One year of history cannot separate a trend from a one-off event. Several years can.

**Recorded bookings understate true demand.**
- When a hotel sells out or closes a rate, demand it turns away is never recorded [5].
- Testing on real hotel and casino data found that ignoring this "unconstraining" step leads to significant revenue losses [6].
- A hotel that only studies what it sold will under-price its best nights year after year.

**Booking behaviour is changing quickly.**
- Leisure booking windows are shortening. Two thirds of rooms are booked in the last month and almost a third in the last week [7].
- A large study of European hotels found cancellation rates rising from 32.9% to 39.6% over four years. Bookings made more than 60 days out were 65 percent more likely to be cancelled (vendor research) [8].
- Pace and cancellation patterns from five years ago need to be re-measured, not assumed.

**Revenue management pays.** Applied well, revenue management has been shown to increase hotel revenue by 2 to 5 percent [9]. For a large resort portfolio, that is a significant amount. It depends entirely on the quality of the analysis behind it.

## 3. How It Will Be Solved: The Twelve Analyses

Each analysis runs per property, per room type and per market segment.

| # | Question | Method | Output |
| :-- | :-- | :-- | :-- |
| 1 | What is the true seasonal shape of demand? | Decompose daily occupancy and ADR into trend, annual, monthly and day-of-week cycles [3] | Seasonality profile and demand tier for every date of the year |
| 2 | How should this year's dates be compared with past years? | Align by weekday (364-day offset) and by moving holidays (Easter, Thanksgiving in both countries); flag disrupted years such as 2020-2021 | A clean "same day last year" calendar |
| 3 | When do bookings arrive? | Build booking pace curves (rooms on the books at 90, 60, 30, 14, 7 and 1 days out) by tier and segment | Pace benchmarks and pickup forecast [1][2] |
| 4 | What did we turn away? | Estimate unconstrained demand on sold-out or closed nights from pace and denial data [5][6] | True demand by date, and nights where rates were set too low |
| 5 | Who books, and through which channel? | Segment and channel mix by tier: transient, group, tour, corporate, OTA, direct, wholesale | Mix targets and acquisition cost by channel |
| 6 | How long do guests stay? | Length-of-stay and arrival-day patterns by tier | Inputs for minimum-stay and closed-to-arrival rules |
| 7 | Who cancels or does not show, and when? | Cancellation and no-show rates by lead time, channel, segment and rate type [8] | Overbooking levels for [HARLTON-02](../02-guest-relocation-revenue-retention/proposal.md) and deposit policies |
| 8 | How sensitive is demand to price? | Compare pickup after rate changes on comparable dates | Price-response estimates by tier |
| 9 | Did discounting help? | Compare dates where rates were held with dates where they were cut, against competitor movement [10] | Evidence on when discounting gained revenue and when it did not |
| 10 | Which groups were worth it? | Group pickup ("wash"), spend and the transient demand they displaced | Group evaluation rules |
| 11 | Who comes back? | Repeat-guest cohorts and the value of returning guests | Target lists for need-period campaigns [11][12] |
| 12 | What happened on event dates? | Event dates compared with matched normal dates | Event uplift factors for [HARLTON-06](../06-event-and-exchange-rate-demand-signals/proposal.md) |

**Validation.** Every forecast built from these analyses is back-tested. It is trained on earlier years, tested on a later year, and its error is reported by tier and lead time. A method is adopted only if it beats the current approach on held-out data.

**The coordination engine's role.** Analyses 3, 4 and 10 produce the inputs the multi-agent coordination engine needs: arrival forecasts, true demand and group value. It uses them to allocate inventory across dates, room types, segments and properties in [HARLTON-11](../11-year-round-occupancy-strategy/proposal.md).

**Deliverables:**
- A demand calendar for the next 365 days with tier labels.
- A pace dashboard comparing on-the-books with history.
- An unconstrained-demand report.
- A quarterly "what history tells us" brief for the revenue and sales teams.

## 4. Data Required

- Daily reservation snapshots for at least three years, so that on-the-books can be reconstructed for any past date and lead time.
- Final stay records with rate, segment, channel, room type and length of stay.
- Cancellations and no-shows with timestamps.
- Group blocks and pickup.
- Denial or turnaway logs where available.
- Competitor rate history where available.

The [Data Foundation](../../Data%20Foundation/proposal.md) defines the tables and labels.

## 5. Risks and Assumptions

- Snapshot history must be stored correctly. Actuals use the latest record for each booking, while pace analysis needs every snapshot.
- Pandemic-era years distort seasonality and are flagged or excluded rather than averaged in.
- The effect of dynamic pricing varies between studies, from meaningful RevPAR gains [13] to small improvements [14]. Local back-testing decides how much weight each analysis carries.

## 6. References

1. Weatherford and Kimes, "A comparison of forecasting methods for hotel revenue management," *International Journal of Forecasting* 19(3), 2003. https://www.sciencedirect.com/science/article/abs/pii/S0169207002000110
2. Weatherford, Kimes and Scott, *Forecasting for Hotel Revenue Management: Testing Aggregation Against Disaggregation*, Cornell University (2001). https://ecommons.cornell.edu/server/api/core/bitstreams/0a6a2f32-71c4-416b-b784-c32c1643733a/content
3. Pereira, "An introduction to helpful forecasting methods for hotel revenue management," *International Journal of Hospitality Management* 58, 2016. https://www.sciencedirect.com/science/article/abs/pii/S027843191630086X
4. Phumchusri and Suwatanapongched, *Journal of Revenue and Pricing Management* (2021). https://link.springer.com/article/10.1057/s41272-021-00363-6
5. "Demand Unconstraining," *Advances in Operations Research* (2012). https://www.hindawi.com/journals/aor/2012/270910/
6. Ferguson, Crystal, Higbie and Kapoor, *A Comparison of Unconstraining Methods to Improve Revenue Management Systems*, Georgia Tech (2007). https://repository.gatech.edu/entities/publication/02d562ce-c7ef-4305-9177-49a41fedbc49
7. CoStar, *Shorter booking windows and experience-driven demand shift hoteliers' leisure revenue strategies* (2026). https://www.costar.com/article/1869193417/shorter-booking-windows-experience-driven-demand-shift-hoteliers-leisure-revenue-strategies
8. Hotel Management (D-EDGE study, vendor), *Cancellation rate at 40% as OTAs push free change policy*. https://www.hotelmanagement.net/tech/study-cancelation-rate-at-40-as-otas-push-free-change-policy
9. Kimes and Anderson, *Revenue Management for Enhanced Profitability*, Cornell University (2011). https://ecommons.cornell.edu/entities/publication/1f129c17-7a21-49bc-845f-0fd7787c4d66
10. Canina, Enz and Lomanno, *Why Discounting Doesn't Work: A Hotel Pricing Update*, Cornell Center for Hospitality Research (2006). https://ecommons.cornell.edu/entities/publication/58885f90-3d7b-461f-927b-ad9cb826a241
11. Noone, Kimes and Renaghan, *Integrating Customer Relationship Management and Revenue Management: A Hotel Perspective*, Cornell University. https://ecommons.cornell.edu/server/api/core/bitstreams/0a97c6cb-a00f-469e-ac6b-3c850900e97b/content
12. Hospitality Net, *Cornell Study Demonstrates the Value of Hotel Loyalty Programs* (2014). https://www.hospitalitynet.org/news/4063852.html
13. Abrate, Nicolau and Viglia, "The Impact of Dynamic Price Variability on Revenue Maximization," *Tourism Management* (2019). https://vtechworks.lib.vt.edu/bitstreams/8b25d47f-854c-414e-b678-e97118b29e8c/download
14. Cho, Lee, Rust and Yu, *Optimal Dynamic Hotel Pricing* (working paper, 2018). https://economics.sas.upenn.edu/index.php/system/files/2018-04/hp_final_update.pdf
