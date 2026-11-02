# HARLTON-01: Peak-Hour Energy Cost Reduction

> **In short: predict the few hottest hours of the year that set the hotel's electricity bill, and quietly shift equipment use out of those hours to save money.**

**Category:** Expense optimization
**Optimizes:** Annual electricity cost, specifically the Global Adjustment portion of the bill
**Status:** Proposal

---

## 1. What It Is

A planning and alerting system that forecasts the few hours each year that set a large resort's electricity cost and coordinates the property's flexible equipment so that load is moved out of those hours. Guest comfort and operations are left unchanged.

The flexible loads are chillers that can pre-cool, pool and waterpark heating, commercial laundry, kitchen pre-heating, ice machines, EV chargers and back-of-house ventilation. Each is treated as an independent agent with its own physical limits. A coordination engine decides which agent shifts how much load and when, so that the property's combined demand is lowest during the predicted peak hours.

## 2. Why It Matters

**The bill is set by five hours.** In Ontario, Class A electricity customers pay the Global Adjustment (GA) according to "their percentage contribution to the top five peak hours over a 12-month period" [1]. A customer that is consuming little during those five hours pays a smaller share for the whole year.

**Large resorts can qualify.** Customers with average monthly peak demand between 1 MW and 5 MW may opt in to Class A, and customers above 5 MW are enrolled automatically [1]. A multi-tower resort with indoor pools, a waterpark and central plant equipment is a realistic candidate.

**The amount is material.** In 2025 the Class B Global Adjustment averaged 4.56 ¢/kWh against a total cost of power of 10.96 ¢/kWh, and in 2024 it was 7.01 ¢/kWh against 10.38 ¢/kWh [2]. GA is therefore a large share of every kilowatt-hour a hotel buys.

**The peaks are predictable in type.** Ontario is a summer-peaking province, and the five peak hours "tend to be during hot, humid days and/or during a heatwave" [1]. The 2025-26 peaks all fell on summer weekday afternoons or early evenings, between 16:00 and 19:00 [3]. This is also when resort occupancy and cooling load are high, so doing nothing is the most expensive option.

**Hotels have flexible load.** Heating and cooling represent "almost 40 percent of the electricity" used by hotels [4], and hotels spend about 6 percent of operating costs on energy [4]. Much of that load can be shifted by one to three hours without guests noticing, for example by pre-cooling common areas or delaying laundry cycles.

**Public data exists.** The system operator publishes hourly Ontario demand data [5] and a Peak Tracker that forecasts the next 24 hours and flags possible peak hours [6]. The forecasting side of this project can be built and back-tested entirely on public data.

## 3. How It Will Be Solved

**Step 1: Peak-hour risk forecast.**
- Train a model on historical hourly Ontario demand and weather.
- Each day, output the probability that each upcoming hour will be one of the year's top five.
- Validate it on past base periods (May 1 to April 30): how many of the true top-five hours would have been flagged, and how many false alarms per summer.

**Step 2: Flexible-load inventory.**
- For each piece of equipment, record how much load can move, for how long, how early it must start, and its comfort or operating limits. Examples: chiller pre-cool window, laundry batch length, pool temperature tolerance.
- This comes from engineering and operations staff, not from new sensors.

**Step 3: Coordinated response.**
- When an alert fires, the coordination engine builds a schedule across all flexible loads that minimizes property demand during the risk window and respects every limit.
- Each load acts as an agent. The engine resolves conflicts, for example so that laundry and pre-cooling do not both rebound into the same hour.

**Step 4: Measurement.**
- Compare the actual property load in the true peak hours with a no-action baseline.
- Convert the reduction into dollars using the published peak demand factor method.

**Deliverables:**
- A peak-risk dashboard for engineering and finance.
- A daily alert with a recommended load plan.
- A year-end savings report that ties back to the utility bill.

## 4. Data Required

- Public: hourly Ontario demand and the Peak Tracker [5][6], and historical weather.
- Internal: 15-minute or hourly interval meter data for the property, an equipment list with ratings, and operating schedules for laundry and pools.

## 5. Risks and Assumptions

- The property must meet Class A eligibility and elect to participate [1]. If it is Class B, the same engine still reduces on-peak consumption under time-of-use pricing, but the savings are smaller.
- Missing one of the five peaks reduces savings for that year, so the alert threshold is a trade-off between response fatigue and coverage.
- No guest-facing change is proposed. All actions are back-of-house or within existing comfort setpoint ranges.

## 6. References

1. IESO, *Industrial Conservation Initiative Backgrounder and FAQs* (May 2025). https://www.ieso.ca/-/media/files/ieso/document-library/global-adjustment/ici-backgrounder.pdf?la=en
2. IESO, *Year in Review: Year-End Data*. https://www.ieso.ca/corporate-ieso/media/year-end-data
3. IESO, *Global Adjustment and Peak Demand Factor*. https://www.ieso.ca/sector-participants/settlements/global-adjustment-and-peak-demand-factor
4. ENERGY STAR, *Energy Savings Tips for Small Businesses: Lodging*. https://www.energystar.gov/buildings/resources-audience/small-biz/lodging
5. IESO, *Data Directory* (hourly Ontario demand). https://www.ieso.ca/power-data/data-directory
6. IESO, *Peak Tracker*. https://ieso.ca/Sector-Participants/Settlements/Peak-Tracker
