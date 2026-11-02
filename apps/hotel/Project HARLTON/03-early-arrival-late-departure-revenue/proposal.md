# HARLTON-03: Early Arrival and Late Departure Revenue

> **In short: predict how many rooms will be ready early, and sell early check-in and late check-out as paid extras instead of giving them away.**

**Category:** Ancillary revenue
**Optimizes:** Paid early check-in and late check-out revenue, priced against real room readiness
**Status:** Proposal

---

## 1. What It Is

A tool that predicts, for each arrival day, how many rooms of each type will realistically be clean and inspected before standard check-in time, and how many departures can be extended without delaying incoming guests. It then turns those predictions into a limited, priced inventory of early check-in and late check-out slots offered to guests in advance.

Today these are usually given away on request at the desk, or refused, and the decision depends on whoever is on shift. This makes them a product with a price and a capacity.

## 2. Why It Matters

**Guests already pay for this.**
- At limited-service properties, guests "generally will embrace a $20-$30 fee for early check-in or late checkout, and 5-10 percent of all guests will select one of these options" when it is offered digitally [1].
- One London pilot charged £60 for a 9 AM to noon check-in and about 5% of guests took it [2].
- Reported fees at branded hotels range from $40 to $65 for early check-in and up to $150 for a late check-out [3][4].

**Standard times create the gap.**
- Hotels typically "set check-in times at 3 p.m. and checkout ... at 11 a.m. or 12 p.m." [5].
- Early arrivals wait because "prior guests haven't checked out, or housekeeping is taking longer to clean the rooms" [2].
- Without a readiness forecast, the hotel cannot know how many early slots it can safely sell.

**At resort scale, small take-up is real money.** At 5% take-up and a $30 average fee, a 1,000-arrival weekend produces $1,500 in revenue from rooms the hotel already owns. That is before counting the goodwill from replacing an unpredictable desk decision with a confirmed promise.

## 3. How It Will Be Solved

**Step 1: Readiness forecast.**
- From departure lists, historical check-out times and housekeeping capacity, estimate by room type how many rooms will be ready by 10 AM, noon and 2 PM.

**Step 2: Sellable slots.**
- Convert the forecast into a conservative number of early check-in slots.
- Late check-out slots come from rooms whose next arrival is late, or that are vacant tonight.
- The coordination engine balances the two, because every late check-out sold consumes a room that could have served an early arrival.

**Step 3: Pricing.** Set price by day type and demand, for example higher on peak Saturdays, and close sales when the slot limit is reached.

**Step 4: Feedback.** Compare promised readiness with actual readiness and tighten the forecast weekly.

**Deliverables:**
- A daily slot availability table.
- A fee-revenue tracker.
- A "promised vs delivered" reliability report.

## 4. Data Required

- Arrivals and departures with times, room status history (dirty, clean, inspected timestamps) and housekeeping staffing by day.
- Pre-arrival communication or upsell channel.

## 5. Risks and Assumptions

- Over-selling early slots damages trust more than not offering them, so the forecast starts conservative.
- Loyalty programs may entitle top-tier members to late check-out at no charge. Those entitlements are reserved first.
- Some fee data comes from vendor-reported results and travel publications, as marked below, and should be validated in a local pilot.

## 6. References

1. Hotel Management, *7 ways for limited-service properties to drive ancillary revenue* (Mar 2022; quoted figures from a technology vendor co-founder). https://www.hotelmanagement.net/operate/7-ways-limited-service-properties-drive-ancillary-revenue
2. PhocusWire, *Pushing to make early check-ins more than just a free perk* (May 2024). https://www.phocuswire.com/pushing-make-early-check-ins-more-than-free-perk
3. Your Mileage May Vary (travel publication), *Hyatt early check-in fee* (Oct 2025). http://yourmileagemayvary.com/2025/10/21/hyatt-early-check-in-fee/
4. One Mile at a Time (travel publication), *Hotels charging early check-in fees*. https://onemileatatime.com/hotels-early-check-in-fee/
5. Skift, *Check In, Check Out Anytime You'd Like at These Hotels* (Nov 2019). https://skift.com/2019/11/21/check-in-check-out-anytime-youd-like-at-these-hotels/
