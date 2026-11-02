# H2-01: Cross-Property Shift Exchange

> **In short: when a shift opens, automatically find a qualified, rested employee, first at the same hotel and then at sister hotels, before paying overtime or agency staff.**

**Category:** Workforce operations
**Optimizes:** Coverage of open shifts with the right people, at the lowest overtime and agency use, within employment law
**Status:** Proposal

---

## 1. What It Is

A coordination layer that sits on top of the existing scheduling and timekeeping system. It does not replace it. When a shift opens anywhere in a multi-property group, the system finds qualified staff who can legally and fairly take it. Shifts open when someone calls in sick, a swap is requested or forecast occupancy jumps. The search covers the home property first, then sister properties within walking distance, and the shift goes to that list before overtime or agency staff are booked.

Each open shift and each available employee is treated as an agent. A coordination engine matches them on several criteria:
- skills and certifications, such as pool lifeguard, banquet or room attendant;
- labour-law rest rules;
- weekly hours;
- seniority or fairness rules;
- the employee's stated preferences.

## 2. Why It Matters

**Staff are scarce.**
- In March 2026, accommodation and food services had a 4.3% job vacancy rate, against 2.8% for all industries in Canada [1].
- The accommodation workforce remains "around 14% smaller than it was before the disruptions of the pandemic" [2].
- In the US, 65% of surveyed hotels report shortages, most often in housekeeping (38%) and front desk (26%) [3].

**Labour is the largest cost, and gaps are filled expensively.**
- Labour is "the single biggest expense within a hotel", at 42.4% of total expenses in 2019 [4].
- Hotels are using more contract labour, which "comes at a significant premium" [5].
- Wage cost per occupied room rose 12.8% from 2024 to 2025 [6].

**Ontario rules make last-minute changes hard to do by hand.** A supervisor filling a shift at 6 AM must respect:
- "at least 11 consecutive hours off work each day" [7];
- "at least eight hours off work between shifts", unless both shifts total no more than 13 hours [7];
- weekly or biweekly rest periods [7];
- overtime at 1.5 times pay after 44 hours a week [8];
- the three-hour minimum pay rule [9].

Checking all of this across several properties under time pressure is exactly the kind of task that should be automated.

**Self-service shift trading works when it is well designed.**
- In a randomized study at a major retailer, 62% of part-time associates in stores with a shift-trading app posted or picked up a shift.
- 72% of shifts posted a week in advance were picked up [10].
- The same study's broader stable-scheduling changes increased median sales by 7% and labour productivity by 5% [10].

## 3. How It Will Be Solved

**Step 1: Demand-linked staffing need.**
- Convert forecast occupancy, arrivals, departures and events into required hours by department and property, for example room attendants per departure.
- Show the gap against the published schedule.

**Step 2: Eligibility engine.**
- For each open shift, compute the list of employees who are qualified and available.
- Each candidate must be legally rested under the rules above and stay under overtime limits after taking the shift.

**Step 3: Matching.**
- The coordination engine ranks matches.
- It honours seniority or union rules and spreads extra hours fairly.
- It prefers home-property staff before cross-property moves.

**Step 4: Offer and confirm.**
- Push the offer through the existing staff app or by text message. First qualified acceptance wins.
- The confirmed change is written back to the scheduling system.

**Step 5: Measurement.** Fill rate, time to fill, overtime hours, agency hours and repeat-burden on individual employees, by property and month.

**Deliverables:**
- An open-shift board for managers.
- An automatic eligibility check.
- A monthly coverage and overtime report.

## 4. Data Required

- Schedules, time punches, employee skills and certifications, availability preferences, collective agreement rules where applicable, and the occupancy and arrivals forecast.

## 5. Risks and Assumptions

- Cross-property moves depend on common employment entity, collective agreements and payroll setup. The pilot starts within one property and expands only where the rules allow it.
- The tool recommends and records. Managers keep final approval.
- The retail study did not show an overall reduction in turnover [10]. No turnover claim is made here until local data supports it.

## 6. References

1. Statistics Canada, *Payroll employment, earnings and hours, and job vacancies, March 2026*. https://www150.statcan.gc.ca/n1/daily-quotidien/260528/dq260528b-eng.pdf
2. Tourism HR Canada, *Labour Force Survey Snapshot: July 2026*. https://tourismhr.ca/labour-force-survey-snapshot-july-2026/
3. American Hotel and Lodging Association, *65% of surveyed hotels report staffing shortages* (Feb 2025). https://www.ahla.com/news/65-surveyed-hotels-report-staffing-shortages
4. CBRE, *Investing in Training Hotel Employees*. https://www.cbre.com/insights/briefs/investing-in-training-hotel-employees
5. CBRE, *All Eyes on Operating Costs in 2025*. https://www.cbre.com/insights/articles/all-eyes-on-operating-costs-in-2025-lessons-learned-in-2024
6. Hotel Management, *Hotel labor costs are rising faster than productivity gains* (Mar 2026). https://www.hotelmanagement.net/data-trends/hotel-labor-costs-are-rising-faster-productivity-gains
7. Government of Ontario, *Your guide to the Employment Standards Act: Hours of work*. https://www.ontario.ca/document/your-guide-employment-standards-act-0/hours-work
8. Government of Ontario, *Your guide to the Employment Standards Act: Overtime pay*. https://www.ontario.ca/document/your-guide-employment-standards-act-0/overtime-pay
9. Government of Ontario, *ESA Policy and Interpretation Manual, Part VII.1: Three hour rule*. https://www.ontario.ca/document/employment-standard-act-policy-and-interpretation-manual/part-vii1-three-hour-rule
10. WorkLife Law, *The Stable Scheduling Study*. https://worklifelaw.org/publications/Stable-Scheduling-Study-Report.pdf
