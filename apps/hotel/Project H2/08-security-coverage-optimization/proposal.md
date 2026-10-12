# H2-08: Security Coverage Optimization

> **In short: send security officers where and when problems actually happen, on patrol routes that change every night so they cannot be predicted.**

**Category:** Safety and security operations
**Optimizes:** Where and when security officers patrol, so that coverage matches risk and patrols are not predictable
**Status:** Proposal

---

## 1. What It Is

A risk-based patrol planning tool for a resort campus: towers, parking structures, pools, waterpark, restaurants, retail and connecting walkways. It does three things:
1. Builds a risk map by location and hour from incident history.
2. Allocates officers to zones and hours in proportion to that risk.
3. Generates patrol routes that are randomized within those rules, so that patrol timing cannot be learned by someone watching.

It also coordinates with night operations ([H2-07](../07-night-operations-coverage/proposal.md)) and event nights, when crowd volumes change the risk picture.

## 2. Why It Matters

**Hotel crime is concentrated in predictable forms.**
- A study of police crime reports from 64 hotels found that theft and burglary are the two major crime problems in hotel settings [1].
- A survey of hotels found that security staff availability, electronic locks, in-room safes and monitored cameras were associated with fewer crimes [2].
- Coverage and visibility matter.

**Predictable patrols can be exploited.**
- Research on airport security found that an adversary can observe a fixed patrol policy and plan around it.
- Its system, deployed at Los Angeles International Airport from 2007, used game theory to randomize checkpoints and canine patrol routes while still weighting coverage towards high-value targets [3][4].
- The same principle applies to a resort campus: weighted by risk, unpredictable in timing.

**Officers are licensed and costly, so placement matters.** In Ontario, security guards must hold a valid licence and complete mandatory training and a ministry test. Agencies supplying guards must hold an agency licence [5][6]. Each officer-hour is a significant cost and should be spent where risk is highest.

**Staff safety is part of security.**
- Major hotel companies have committed to providing employee safety devices across around 20,000 US properties [7].
- Some cities require panic buttons for staff who work alone in guest rooms [8].
- A security plan should include responding to those alerts quickly.

## 3. How It Will Be Solved

**Step 1: Risk map.**
- Classify historical incidents by type (theft, disturbance, medical, trespass, vehicle), location zone and hour.
- Weight them by severity.
- Add known drivers such as event nights, pool hours, bar closing times and check-in peaks.

**Step 2: Coverage allocation.**
- The multi-agent coordination engine treats each officer as an agent and each zone-hour as demand for coverage.
- It allocates officer time in proportion to risk, ensures every zone gets a minimum presence, and keeps response time to any point within a target.

**Step 3: Randomized routes.**
- Within each officer's allocation, generate patrol sequences whose timing varies from night to night, following the game-theoretic approach in [3][4].
- Supervisors see the plan. Officers receive their route at the start of the shift.

**Step 4: Response integration.** Staff duress alerts, noise complaints and CCTV alarms are routed to the nearest available officer. Response times are logged.

**Step 5: Measure.**
- Incidents by zone and hour before and after.
- Response times.
- Patrol completion.
- Coverage of high-risk zones.

**Deliverables:**
- A risk heat map by zone and hour.
- Daily officer allocation.
- Randomized patrol routes.
- A response-time report.
- A monthly security review.

## 4. Data Required

- Incident logs with time, location and type.
- Zone map of the campus.
- Officer schedules.
- CCTV coverage map.
- Event calendar.
- Duress alert and response logs.

## 5. Risks and Assumptions

- Incident data is sensitive. Only aggregated zone-hour counts are used for planning, and access is restricted.
- No peer-reviewed source was found for hotel incidents by time of day, so the risk map is built from the property's own history.
- Randomization never reduces coverage below the minimum set by the security manager.

## 6. References

1. Ho, Zhao and Brown, "Examining hotel crimes from police crime reports," *Crime Prevention and Community Safety* (2009). https://www.ojp.gov/ncjrs/virtual-library/abstracts/examining-hotel-crimes-police-crime-reports
2. Bach and Pizam, "Crimes in Hotels," *Hospitality Research Journal* (1996). https://journals.sagepub.com/doi/abs/10.1177/109634809602000205
3. Pita et al., "Deployed ARMOR protection: The application of a game theoretic model for security at the Los Angeles International Airport," AAAI (2008). https://mlanthology.org/aaai/2008/pita2008aaai-armor/
4. Pita et al., *SIGecom Exchanges* 8(2) (2009). https://www.sigecom.org/exchanges/volume_8/2/pita.pdf
5. Government of Ontario, *Private security and investigative services*. https://www.ontario.ca/page/private-security-and-investigative-services
6. Government of Ontario, *Apply for a security guard and private investigator agency licence*. https://www.ontario.ca/page/apply-security-guard-and-private-investigator-agency-licence
7. American Hotel and Lodging Association, *5-Star Promise*. https://www.ahla.com/5-star
8. City of Seattle, *Hotel Employees Safety Ordinance Fact Sheet* (2025). https://www.seattle.gov/documents/Departments/LaborStandards/2025_Hotel_Employees_Safety_Ordinance_Fact_Sheet.pdf
