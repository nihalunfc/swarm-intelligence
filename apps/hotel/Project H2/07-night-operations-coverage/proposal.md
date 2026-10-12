# H2-07: Night Operations and Front Desk Coverage

> **In short: staff the overnight hours based on real night-time demand, take routine paperwork off the night desk and keep staff who work alone safe.**

**Category:** Workforce operations and safety
**Optimizes:** Overnight service levels, workload and staff safety at the front desk and across night roles
**Status:** Proposal

---

## 1. What It Is

A plan and supporting tools for the overnight hours, roughly 11 PM to 7 AM. A large resort runs on a small team overnight, and each person covers several jobs:
- night audit;
- late check-ins and walk-ins;
- guest calls;
- noise complaints;
- cash handling;
- lost keys;
- incident response.

The proposal covers four areas:
1. Sizing night staffing from real overnight demand.
2. Automating the night audit's reporting tasks.
3. Reducing avoidable overnight front desk work.
4. Protecting staff who work alone at night.

## 2. Why It Matters

**Night work is hard on people.**
- The Canadian Centre for Occupational Health and Safety reports strong evidence that night, evening, rotating and irregular shifts are associated with an increased risk of occupational injury. It recommends forward-rotating shift patterns [1].
- Being awake for 17 hours affects performance about as much as a blood alcohol content of 0.05. Night workers get about 5 to 7 hours less sleep per week than day workers [2].

**Ontario law requires a risk assessment that covers exactly this role.**
- Employers must assess the risk of workplace violence arising from the nature of the workplace, the type of work and its conditions [3].
- The Ministry's guide lists handling cash, working alone or with few people, and working late nights or early mornings as risk factors [4]. A night auditor typically meets all three.
- Guidance on working alone recommends regular check-in procedures and automated duress devices [5].

**Night teams are small because staff are scarce.** Accommodation employment is still about 14% below pre-pandemic levels [6]. Every overnight hour spent on manual reports or avoidable calls is an hour not spent on guests.

**The night audit is a reporting job.** Much of it involves compiling daily figures and reports that can be generated automatically from the data layer described in the [unified reporting proposal](../proposal.md).

## 3. How It Will Be Solved

**Step 1: Measure overnight demand.** From PMS and phone logs, build an hour-by-hour profile by day type and season of:
- late arrivals and walk-ins;
- guest calls by reason;
- noise complaints and security calls;
- key requests.

**Step 2: Size and share coverage.**
- Set night staffing by demand tier instead of a fixed number.
- Where sister properties are close together, use a shared overnight pool: one roving supervisor and one security responder covering several desks, coordinated by the multi-agent engine so the nearest available person responds.
- Apply forward rotation and protected rest in schedules built by [H2-05](../05-automated-schedule-builder/proposal.md) [1].

**Step 3: Remove avoidable work.**
- Generate audit reports automatically.
- Send pre-arrival messages with check-in details to guests arriving after 11 PM.
- Pre-assign rooms and pre-encode keys for known late arrivals.
- Use self-service key reissue where the property's lock system supports it.
- Route noise complaints with location data straight to security.

**Step 4: Protect lone workers.**
- Do a documented risk assessment for each night role [3][4].
- Set cash-handling limits.
- Run scheduled check-in calls.
- Provide duress devices that alert the shared night responder [5].

**Step 5: Measure.**
- Late-arrival wait time.
- Calls handled per hour.
- Audit completion time.
- Incidents.
- Night staff overtime and turnover.

**Deliverables:**
- An overnight demand profile.
- A night staffing standard by tier.
- Automated audit reports.
- A late-arrival pre-registration process.
- A lone-worker safety protocol.

## 4. Data Required

- PMS arrival times and walk-ins.
- Call logs by reason.
- Security and incident logs.
- Night schedules and punches.
- Current audit checklist and report list.

## 5. Risks and Assumptions

- A shared night pool requires clear response-time standards and must not leave any desk unstaffed against brand or safety requirements.
- No Ontario law requires panic buttons for hotel staff. The safety measures here come from the employer's general duty and risk assessment [3][4].

## 6. References

1. Canadian Centre for Occupational Health and Safety, *Rotational Shiftwork*. https://www.ccohs.ca/oshanswers/ergonomics/shiftwrk.html
2. Canadian Centre for Occupational Health and Safety, *Fatigue*. https://www.ccohs.ca/oshanswers/psychosocial/fatigue.html
3. Government of Ontario, *Understand the law on workplace violence and harassment*. https://www.ontario.ca/page/understand-law-workplace-violence-and-harassment
4. Government of Ontario, *Workplace Violence and Harassment: Understanding the Law*. https://files.ontario.ca/wpvh_guide_english.pdf
5. Canadian Centre for Occupational Health and Safety, *Working Alone: General*. https://www.ccohs.ca/oshanswers/hsprograms/workingalone.html
6. Tourism HR Canada, *Labour Force Survey Snapshot: July 2026*. https://tourismhr.ca/labour-force-survey-snapshot-july-2026/
