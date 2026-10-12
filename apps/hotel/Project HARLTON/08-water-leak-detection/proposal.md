# HARLTON-08: Water Leak Detection from Meter Data

> **In short: check the water meter every night at 3 AM; if water is still flowing, something is leaking, and the system says roughly where.**

**Category:** Expense optimization
**Optimizes:** Water and sewer cost lost to undetected leaks
**Status:** Proposal

---

## 1. What It Is

A daily automated check of the property's water meter readings in the quiet hours of the night. When consumption at 3 to 4 AM stays above the property's normal baseline, the system raises an alert that a toilet, valve or pipe is probably leaking. It then narrows down where, using sub-meters or the pattern of the excess flow.

## 2. Why It Matters

**Hotels are heavy water users.**
- Lodging accounts for "approximately 15 percent of the total water use in commercial and institutional buildings" in the United States [1].
- Restrooms and domestic use are the largest single end use, at about 30%, followed by laundry and landscaping at 16% each [2].

**Small leaks are expensive and invisible.**
- The US EPA gives an example of a single toilet leaking 0.5 gallons per minute costing about $2,100 per year [3].
- A resort with thousands of fixtures can carry several such leaks for months, because no one sees a running toilet in a vacant room.

**The method is standard and cheap.**
- The EPA recommends reading the facility meter "during off-peak hours when all water-using equipment can be turned off" [3].
- The US Department of Energy advises monitoring minimum flow "during unoccupied periods where flow is at the lowest level, which is typically around 3 a.m. or 4 a.m." [4].
- The hotel already has the meter. What is missing is someone checking it every night.

## 3. How It Will Be Solved

**Step 1: Baseline.**
- From hourly or 15-minute meter data, learn each meter's normal minimum night flow by season.
- Account for scheduled loads such as overnight laundry, pool top-up and irrigation.

**Step 2: Detection.**
- Flag nights where minimum flow exceeds the baseline by more than a set margin for two or more consecutive nights.
- Estimate the excess volume and its annual cost.

**Step 3: Location.**
- Where sub-meters exist (by tower, laundry, pool, kitchen), identify which one carries the excess.
- Where they do not, produce a targeted inspection list ranked by likelihood, for example floors with recent maintenance tickets.

**Step 4: Close the loop.** Record the repair and confirm that the night flow returned to baseline, so savings are verified rather than assumed.

**Deliverables:**
- A nightly leak alert.
- A cost-of-leak estimate.
- A monthly verified-savings log.

## 4. Data Required

- Interval water meter data (utility smart meter or building management system), sub-meter readings where available, and the schedule of planned overnight water use.

## 5. Risks and Assumptions

- No authoritative industry figure was found for the share of hotel water lost to leaks. The business case is therefore built from the property's own meter data during the pilot, not from a benchmark.
- Properties without interval metering may need a low-cost meter data logger.

## 6. References

1. US EPA WaterSense, *Saving Water in Hotels* (fact sheet, 2016; archived). https://19january2017snapshot.epa.gov/www3/watersense/docs/saving-water-in-hotels_fact%20sheet_508_Mar2016.pdf
2. US EPA, *Water Efficiency in the Commercial and Institutional Sector* (2009; archived). https://19january2017snapshot.epa.gov/www3/watersense/docs/ci_whitepaper.pdf
3. US EPA, *WaterSense at Work, Section 2.3: Leak Detection and Repair*. https://www.epa.gov/system/files/documents/2023-05/ws-commercial-watersense-at-work_Section_2.3_Leak_detection.pdf
4. US Department of Energy, FEMP, *Best Management Practice #3: Distribution System Audits, Leak Detection, and Repair*. https://www.energy.gov/cmei/femp/best-management-practice-3-distribution-system-audits-leak-detection-and-repair
