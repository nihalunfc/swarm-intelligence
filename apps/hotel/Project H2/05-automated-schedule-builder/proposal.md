# H2-05: Automated Schedule Builder

> **In short: build the weekly staff schedule automatically, then publish the same approved schedule to the staff app, to the familiar Excel sheet and on paper for the staff board.**

**Category:** Workforce operations
**Optimizes:** The weekly staff schedule, so that coverage matches demand, labour rules are met and managers stop building it by hand
**Status:** Proposal

---

## 1. What It Is

A scheduling pipeline that builds next week's schedule automatically for each department, then publishes the same approved schedule to three places at once:

1. **The workforce management system**, through its official API, so that employees who use the app see their shifts as they do today.
2. **An Excel workbook** in the exact layout and colour coding the department already uses, so that managers can review and adjust it in a familiar format.
3. **A printable schedule** for the staff board, so that employees who prefer paper, or who are not comfortable with apps, are not left behind.

Today, many departments still build schedules in large, colour-coded spreadsheets every week. The workforce system is used to display the result, not to optimize it. This pipeline removes the manual building. It keeps every channel people rely on.

## 2. Why It Matters

**Manual scheduling takes managers away from managing.**
- Cornell's hospitality scheduling guide notes that the time a manager spends developing a schedule is time not spent managing employees and serving guests [1].
- In a 2025 survey of over 750 managers, 59% reported spending three or more hours on scheduling tasks, and 39% relied on paper or basic software (vendor survey) [2].

**Optimized schedules perform better than hand-built ones.**
- In a hospital study, a centralized optimization model reduced overtime by about 80%, cut costs by just under 11%, and improved how desirable staff found their schedules by about 34% [3].
- Integer programming has been applied to weekly shift schedules in a hotel department, including rest requirements [4].
- In a retail field experiment, more stable, worker-friendly scheduling raised productivity by 5.1% and sales by 3.3%, while labour cost fell 1.8% [5].

**The rules are complex and checking them by hand is error-prone.** In Ontario, every schedule must respect:
- daily and between-shift rest;
- weekly or biweekly rest periods;
- overtime after 44 hours a week;
- the three-hour rule.

All are set out in the Employment Standards Act guide [6][7]. Collective agreements and seniority rules add further constraints.

**Workforce systems can accept schedules automatically.**
- Leading workforce management platforms, such as Dayforce, offer auto-scheduling and demand-based labour forecasting as product features [8][9].
- Dayforce's API accepts employee schedule data, with an option to validate a schedule without saving it [10].
- Where those modules are not licensed or configured, an external optimizer can still feed the system directly. Nothing needs to be replaced.

**Not everyone works best with an app.**
- Statistics Canada found that adults aged 55 to 65 had the lowest scores across literacy, numeracy and adaptive problem solving [11].
- Internet use among seniors was 82.6% in 2022, compared with 95% for all Canadians aged 15 and over [12].
- In hotels, motor hotels and motels, 12.3% of workers were aged 55 to 64 and 4.5% were 65 to 74 in 2023 [13].
- A printed schedule on the wall is a requirement for inclusion, not an old habit.

## 3. How It Will Be Solved

**Step 1: Demand to hours.**
- Convert the forecast into required hours by department, day and shift: occupancy, arrivals, departures, group functions, restaurant covers and events.
- Use labour standards, for example minutes per checkout room and per stayover room in housekeeping, or front desk agents per 100 arrivals.

**Step 2: Constraints and preferences.** Encode:
- the legal rules [6][7];
- collective agreement and seniority rules;
- employee availability and requests;
- skills and certifications;
- fairness rules such as rotating weekends and spreading less popular shifts.

**Step 3: Optimization.**
- The multi-agent coordination engine treats each employee and each required shift as agents.
- It builds a schedule that covers demand at the lowest cost and overtime, honours preferences where possible, and never breaks a hard rule.
- Every shift carries a reason code, for example "covers forecast 412 departures Saturday".

**Step 4: Manager review.**
- The draft opens in the familiar Excel layout.
- The manager can lock or change any shift. The pipeline re-checks every change against the rules and flags violations immediately.

**Step 5: Publish to all channels.** One approved schedule is:
- pushed to the workforce system through its API, with a validation pass first [10];
- saved as the department's Excel file;
- printed for the staff board.

All three always match because they come from the same source.

**Step 6: Learn.** Actual punches, call-outs and swaps ([H2-01](../01-cross-property-shift-exchange/proposal.md)) feed back into next week's forecast and labour standards.

**Deliverables:**
- A weekly draft schedule per department.
- A rule-check report.
- Synchronized outputs to the workforce system, Excel and print.
- A monthly report on coverage, overtime and schedule stability.

## 4. Data Required

- Employee roster with skills, seniority, availability and contract hours.
- Collective agreement rules.
- Historical schedules and time punches.
- The demand forecast.
- API credentials for the workforce system.
- The current Excel template.

## 5. Risks and Assumptions

- Managers must trust the draft before they stop rebuilding it. The pilot runs one department in parallel with the manual process for several weeks.
- API access must be approved by the system owner. Until then, the Excel and print outputs alone remove most of the manual work.
- Optimization evidence comes from healthcare and retail [3][5]. Hotel-specific gains will be measured in the pilot.

## 6. References

1. Thompson, *Workforce Scheduling: A Guide for the Hospitality Industry*, Cornell Center for Hospitality Research (2004). https://ecommons.cornell.edu/server/api/core/bitstreams/0bfcbe04-b48f-4faf-a884-0696f266ff91/content
2. Yahoo Finance (Legion, vendor), *Legion's 2025 State of the North American Hourly Workforce Report*. https://finance.yahoo.com/news/legion-2025-state-north-american-140000386.html
3. Wright and Mahar, "Centralized nurse scheduling to simultaneously improve schedule cost and nurse satisfaction," *Omega* 41(6), 2013. https://ideas.repec.org/a/eee/jomega/v41y2013i6p1042-1052.html
4. Kassa and Tizazu, "Personnel scheduling using an integer programming model: an application at Avanti Blue-Nile Hotels," *SpringerPlus* (2013). https://pmc.ncbi.nlm.nih.gov/articles/PMC3923920/
5. University of Oregon, *Study finds worker-friendly scheduling boosts bottom line*. https://news.uoregon.edu/content/study-finds-worker-friendly-scheduling-boosts-bottom-line
6. Government of Ontario, *Your guide to the Employment Standards Act: Hours of work*. https://www.ontario.ca/document/your-guide-employment-standards-act-0/hours-work
7. Government of Ontario, *Your guide to the Employment Standards Act: Overtime pay*. https://www.ontario.ca/document/your-guide-employment-standards-act-0/overtime-pay
8. Dayforce (vendor), *Employee Scheduling Software*. https://www.dayforce.com/how-we-help/dayforce/workforce-management-software/employee-scheduling
9. Dayforce (vendor), *Labor Planning and Forecasting Software*. https://www.dayforce.com/how-we-help/dayforce/workforce-management-software/labor-planning
10. Dayforce, *RESTful Web Services Developer Guide: POST Employee Schedules*. https://help.dayforce.com/r/documents/Dayforce-RESTful-Web-Services-Developer-Guide/POST-Employee-Schedules
11. Statistics Canada, *The Daily: Survey of Adult Skills (PIAAC)* (Dec 2024). https://www150.statcan.gc.ca/n1/daily-quotidien/241210/dq241210a-eng.htm
12. Statistics Canada, *Canadian seniors more connected than ever* (2023). https://statcan.gc.ca/o1/en/plus/4288-canadian-seniors-more-connected-ever
13. Statistics Canada, *Workforce insights: Demographics in the travel arrangement, reservation and accommodation services industries, 2017 to 2023*. https://www150.statcan.gc.ca/n1/pub/11-621-m/11-621-m2025009-eng.htm
