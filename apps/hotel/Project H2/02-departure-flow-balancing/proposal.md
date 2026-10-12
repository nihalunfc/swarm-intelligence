# H2-02: Departure Flow Balancing

> **In short: spread guest check-outs across the morning with simple offers and messages, so elevators, the front desk and housekeeping are not overwhelmed at 11 AM.**

**Category:** Guest flow operations
**Optimizes:** The morning check-out peak, including elevator queues, front desk lines and the housekeeping start
**Status:** Proposal

---

## 1. What It Is

A system that spreads guest departures more evenly across the morning, instead of letting most of them land between 10:30 and 11:00 AM. It does not take control of elevators or any building equipment. It works by influencing guest choices:

- **Departure-time preference:** guests are asked the evening before when they plan to leave.
- **Express check-out by message:** guests can check out without visiting the desk.
- **Staggered late check-out:** extended check-out times are released floor by floor, so towers do not empty all at once.
- **Service elevator timing:** a recommended plan for luggage, housekeeping and room service lift use that stays off the guest peak.

Each departing room is treated as an agent with a preferred departure window. The coordination engine nudges the group toward a flatter departure curve. This is the same peak-to-average reduction idea used in energy grid balancing, applied to people.

## 2. Why It Matters

**Departures are compressed by design.**
- Hotels typically set check-out "at 11 a.m. or 12 p.m." [1].
- Lift-traffic engineering research on hotels identifies two daily peaks, "one is in the morning when people have breakfast and check out" [2].
- In a high-rise resort, the result is crowded elevators, a queue at the desk and a lobby full of luggage, all within the same 45 minutes.

**The peak passes straight to housekeeping.**
- A room attendant typically needs "between fifteen and thirty minutes to do one room" and is responsible for about 16 rooms per shift [3].
- If most departures happen at 11 AM, the morning is idle and the afternoon is rushed. Early-arriving guests then wait for rooms that could have been ready.

**Guests are willing to self-serve.**
- 70% of American travellers say they are likely to check in using an app or kiosk instead of a front desk (vendor survey) [4].
- 73% say they are more likely to stay at a hotel that offers self-service technology [5].

## 3. How It Will Be Solved

**Step 1: Measure the curve.** From PMS check-out timestamps, build the departure distribution by tower, day of week and season.

**Step 2: Collect intent.** An evening-before message asks for planned departure time and offers express check-out. Responses give a forecast of tomorrow's curve by floor.

**Step 3: Balance.**
- The coordination engine compares the forecast curve with elevator and desk capacity.
- Where a window is overloaded, it recommends targeted offers to the floors that would relieve it most, such as a free 12:30 late check-out.
- It also produces a back-of-house lift-use plan that avoids the peak.

**Step 4: Link to housekeeping.** Rooms that leave early are released to housekeeping first, so cleaning starts earlier and early-arrival rooms are ready sooner. This connects to [H2-03](../03-room-ready-guest-notifications/proposal.md).

**Step 5: Measurement.** Peak-hour departures as a share of total, desk queue length at the peak, time from check-out to room-ready, and guest feedback on check-out.

**Deliverables:**
- A daily departure-curve forecast.
- A targeted offer list.
- A back-of-house lift plan.
- A weekly flow report.

## 4. Data Required

- PMS check-out timestamps, room-to-tower and floor mapping, guest messaging channel, elevator count and capacity, and housekeeping assignment times.

## 5. Risks and Assumptions

- Offers must not conflict with the next day's arrivals or with loyalty entitlements.
- The system only recommends and communicates. It never controls building equipment.
- No survey was found that measures guest demand for flexible check-out in percentage terms, so take-up will be measured in the pilot.

## 6. References

1. Skift, *Check In, Check Out Anytime You'd Like at These Hotels* (Nov 2019). https://skift.com/2019/11/21/check-in-check-out-anytime-youd-like-at-these-hotels/
2. M-L. Siikonen, *Traffic Patterns in Hotels and Residential Buildings* (Elevator and Escalator Symposium paper). https://liftescalatorlibrary.org/paper_indexing/papers/00000051.pdf
3. Canadian Centre for Occupational Health and Safety, *Hotel Housekeeping*. https://www.ccohs.ca/oshanswers/occup_workplace/hotel_housekeeping.html
4. HITEC / HFTP (Mews survey, vendor), *70% of travelers would skip the front desk* (Jun 2025). https://www.hitec.org/news/4127642/70-of-travelers-would-skip-the-front-desk-mews-survey-reveals-the-rise-of-self-check-in-hotels
5. Oracle, *Oracle Hospitality in 2025 consumer research study* (Jun 2022). https://www.oracle.com/news/announcement/oracle-hospitality-in-2025-consumer-research-study-2022-06-01/
