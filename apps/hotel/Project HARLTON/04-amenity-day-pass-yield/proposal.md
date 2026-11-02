# HARLTON-04: Amenity Day-Pass Yield Management

> **In short: on quiet days, sell spare waterpark, pool and spa space to day visitors, while always protecting space for hotel guests.**

**Category:** Ancillary revenue
**Optimizes:** Revenue from unused waterpark, pool and spa capacity on low-occupancy days
**Status:** Proposal

---

## 1. What It Is

A capacity and pricing model for resort amenities, such as an indoor waterpark, pools or a spa. It calculates, for each future day, how much capacity hotel guests are expected to use and how much is left over. It then recommends how many day passes to release to non-staying visitors and at what price.

On busy days, capacity is protected for hotel guests. On quiet days, idle capacity is sold instead of left empty.

## 2. Why It Matters

**Established operators already do this, and tie it to room occupancy.**
- When a major North American waterpark resort chain launched day passes, it stated that "the parks will limit the number of day passes available, based on the projected number of rooms occupied" [1].
- Its current public page shows passes from $35, that "availability is limited," and that sold-out dates cannot be selected [2].
- The method is proven: release capacity as a function of forecast occupancy.

**An amenity's capacity is perishable, just like a room.** An unsold hour of waterpark capacity on a Tuesday in November cannot be stored and sold on a Saturday in July. Resort occupancy is seasonal and peaks at weekends and holidays, so midweek and shoulder-season days carry predictable spare capacity.

**Day visitors spend beyond the pass.** Visitors buy food, parking and retail on site, and a good visit is a low-cost introduction to a future overnight stay.

## 3. How It Will Be Solved

**Step 1: Guest usage model.**
- Estimate amenity attendance per occupied room by day type, season and guest mix (families vs couples, group vs leisure), using historical gate or wristband counts.

**Step 2: Spare capacity forecast.**
- Safe capacity minus forecast guest attendance, by day and session, with a buffer for forecast error.

**Step 3: Release and price.**
- The coordination engine sets the day-pass allocation and price per session.
- Each session is treated as an agent competing for limited lifeguard and space capacity.
- It closes sales automatically if hotel occupancy picks up.

**Step 4: Measurement.**
- Track pass revenue, secondary spend per visitor, guest satisfaction on pass-release days, and any conversion of pass buyers into overnight bookings.

**Deliverables:**
- A 60-day capacity calendar.
- A release and price recommendation per day.
- A weekly yield report.

## 4. Data Required

- Room occupancy forecast, historical amenity attendance by hour, and safe capacity limits (including lifeguard staffing).
- Point-of-sale data for secondary spend.

## 5. Risks and Assumptions

- Guest experience comes first. If guests feel crowded, the program fails, so the release buffer is set conservatively and reviewed against guest feedback.
- Some resorts reserve amenities exclusively for registered guests as a brand promise. This model applies only where day access is part of the strategy.

## 6. References

1. Aquatics International, *Great Wolf Lodge Launches New Day Pass Program*. https://www.aquaticsintl.com/facilities/waterparks-resorts/great-wolf-lodge-launches-new-day-pass-program_o
2. Great Wolf Lodge, *Day Pass* (public pricing page). https://www.greatwolf.com/day-pass
