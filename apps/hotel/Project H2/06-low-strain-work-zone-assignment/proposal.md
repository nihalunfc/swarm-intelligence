# H2-06: Low-Strain Work Zone Assignment

> **In short: give each staff member a compact work area with a fair share of heavy tasks, so nobody walks or lifts more than necessary.**

**Category:** Workforce operations and safety
**Optimizes:** Daily assignment of staff to areas, so that walking, carrying and physical strain are minimized and shared fairly
**Status:** Proposal

---

## 1. What It Is

A daily assignment tool that decides who works where. It starts with housekeeping room boards and extends to banquets, room service, public areas and engineering. It considers:

- where each task is;
- how physically demanding it is;
- where supplies and elevators are;
- each employee's recent workload.

It then produces assignments that keep each person in a compact area with a balanced, fair amount of heavy work.

Today, room boards are often built by floor order or habit. One attendant may get a run of checkout suites at opposite ends of a tower, while another gets light stayovers next to the linen room.

## 2. Why It Matters

**Housekeeping is the most injury-prone job in the hotel.**
- In a study of 50 hotels covering more than 55,000 worker-years, housekeepers had the highest injury rate of any hotel job, at 7.9 per 100 workers, and the highest rate of musculoskeletal disorders, at 3.2 per 100 [1].
- The Canadian Centre for Occupational Health and Safety notes that a housekeeper changes body position about every three seconds and adopts around 8,000 postures in a shift. It lists heavy physical workload and working alone as key hazards [2].

**Not all rooms are equal.**
- A field study measured an average of about 18 minutes per room, ranging from about 15 minutes for a stayover to about 27 minutes for a suite checkout. Attendants were assigned between 13 and 19 rooms a day [3].
- A board that counts rooms but ignores room type hides large differences in effort.

**Regulators already treat workload as a hazard.** California's hotel housekeeping injury-prevention standard requires employers to evaluate excessive work rates and inadequate recovery time [4]. Ontario has no equivalent rule, but the principle is the same.

**Walking is waste.** Warehouse research shows that travel is typically the largest single share of a picker's time, about half [5]. The same logic applies to an attendant walking between scattered rooms and a distant supply closet.

## 3. How It Will Be Solved

**Step 1: Map the building.** Create a simple location model of floors, room positions, elevators, linen and supply closets ([H2-10](../10-decentralized-supply-placement/proposal.md)) and service corridors. This is done once per property.

**Step 2: Weight the work.** Give every task an effort score from measured times and physical load, for example:
- checkout or stayover;
- room size;
- extra beds or cribs;
- deep-clean flags;
- distance from supplies.

**Step 3: Assign.**
- The multi-agent coordination engine treats each employee as an agent and each room or task as work to be claimed.
- It minimizes total walking and elevator trips while keeping effort balanced across the team.
- Heavy tasks are rotated across the week, so the same person does not repeatedly get the hardest section.
- Constraints include section preferences, language pairing for training, and accessibility needs.

**Step 4: Adjust during the day.** As early departures and late check-outs come in ([H2-02](../02-departure-flow-balancing/proposal.md)), the board re-balances. Supervisors can override it.

**Step 5: Measure.**
- Rooms per hour by room type.
- Effort balance across staff.
- Strain-related incident reports.
- Staff feedback through a short weekly pulse.

**Deliverables:**
- A daily assignment board, printed and digital.
- A weekly workload-balance report.
- A quarterly ergonomics review with health and safety.

## 4. Data Required

- Floor plans with room positions and supply locations.
- Room attributes.
- Daily departures, stayovers and special requests.
- Historical room-clean times by room type.
- Staff roster and preferences.
- Incident and injury records, summarized by department only.

## 5. Risks and Assumptions

- Room credit systems may be defined in collective agreements. The tool works within them.
- No authoritative source was found for distance walked per housekeeping shift. The pilot will measure it, for example with voluntary step counts, before and after.
- Effort scores are reviewed with experienced attendants so they reflect real work.

## 6. References

1. Buchanan et al., "Occupational injury disparities in the US hotel industry," *American Journal of Industrial Medicine* (2010). https://onlinelibrary.wiley.com/doi/abs/10.1002/ajim.20724
2. Canadian Centre for Occupational Health and Safety, *Hotel Housekeeping*. https://www.ccohs.ca/oshanswers/occup_workplace/hotel_housekeeping.html
3. Aguilar-Escobar et al., *Journal of Industrial Engineering and Management* (2021). https://www.jiem.org/index.php/jiem/article/download/3441/983
4. California Code of Regulations, Title 8, Section 3345, *Hotel Housekeeping Musculoskeletal Injury Prevention*. https://www.dir.ca.gov/title8/3345.html
5. de Koster, Le-Duc and Roodbergen, "Design and control of warehouse order picking: a literature review," *European Journal of Operational Research* 182 (2007). https://pure.eur.nl/ws/portalfiles/portal/46713708/DesignandControl_2007.pdf
