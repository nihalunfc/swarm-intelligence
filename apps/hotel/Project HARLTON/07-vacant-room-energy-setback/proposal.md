# HARLTON-07: Vacant-Room Energy Setback

> **In short: use the booking system to turn down heating and cooling in rooms nobody has booked tonight, with no new sensors needed.**

**Category:** Expense optimization
**Optimizes:** Heating and cooling cost in unsold and unoccupied guest rooms
**Status:** Proposal

---

## 1. What It Is

A rule set that uses information the hotel already has, room status from the property management system (PMS), to relax heating and cooling in rooms that are not sold tonight. In rooms that are sold, it pre-conditions the room shortly before the guest's expected arrival.

No occupancy sensors are required, which makes this practical for older buildings.

## 2. Why It Matters

**Guest rooms are conditioned when nobody is in them.**
- Heating and cooling represent "almost 40 percent of the electricity and more than half of the natural gas used by hotels and motels" [1].
- Hotel rooms "are unoccupied for 12 hours each day on average" [1].

**Building codes already expect this.**
- The 2018 US model energy code requires setpoints to move by 4°F when rented rooms are unoccupied.
- Unrented rooms must go to 60°F for heating or 80°F for cooling, with ventilation turned off [2].
- The US national lab that analyses building codes modelled energy-cost savings from these provisions of 9.3% for a small hotel and 1.7% for a large hotel [2].
- California's code-change analysis estimated savings of "12%-25% of annual guest room HVAC energy use" from guest room occupancy controls [3].

**The PMS knows more than a sensor does.** A motion sensor knows whether someone is in the room now. The PMS knows whether the room is sold tonight, when the guest is expected and when they leave. For unsold rooms, the most common case on a quiet night, this is the more useful signal and costs nothing to collect.

## 3. How It Will Be Solved

**Step 1: Room-state feed.** A scheduled extract of room status (vacant unsold, vacant sold arriving today, occupied, out of order) by room.

**Step 2: Setback rules.**
- Unsold rooms go to the code-level setback.
- Sold rooms recover to the guest setpoint within a set time before the expected arrival.
- Occupied rooms are left to the guest's control.
- Where thermostats are networked, the rules are applied automatically. Where they are not, the system produces a nightly floor-by-floor list for engineering or housekeeping.

**Step 3: Block allocation.**
- On low-occupancy nights, rooms are assigned to the fewest floors or wings possible.
- Whole zones can then be set back, which also simplifies housekeeping routes.

**Step 4: Measurement.**
- Compare energy use on setback nights against matched baseline nights, adjusted for weather and occupancy.

**Deliverables:**
- A nightly setback list or automated schedule.
- A floor-consolidation recommendation.
- A monthly verified savings report.

## 4. Data Required

- PMS room status and arrival times, room-to-zone mapping, thermostat or building management system access where available, and utility interval data.

## 5. Risks and Assumptions

- Recovery time must be measured per building so that rooms are comfortable at arrival. A complaint costs more than the energy saved.
- Savings vary by building type, climate and HVAC system [2][3]. The pilot will establish the property's own figure before any savings are claimed.

## 6. References

1. ENERGY STAR, *Energy Savings Tips for Small Businesses: Lodging*. https://www.energystar.gov/buildings/resources-audience/small-biz/lodging
2. Pacific Northwest National Laboratory, *Energy and Energy Cost Savings Analysis of the 2018 IECC for Commercial Buildings* (PNNL-28125). https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-28125.pdf
3. California Statewide Utility Codes and Standards Program, *Guest Room Occupancy Controls, 2013 California Building Energy Efficiency Standards* (CASE Report). https://title24stakeholders.com/wp-content/uploads/2020/01/2013_CASE-Report_Guest-Room-Occupancy-Controls-2.pdf
