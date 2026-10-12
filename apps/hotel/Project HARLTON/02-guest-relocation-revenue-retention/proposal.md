# HARLTON-02: Guest Relocation and Revenue Retention

> **In short: when one hotel is overbooked, move guests to a sister hotel instead of a competitor, so the guest and the money stay in the group.**

**Category:** Revenue protection
**Optimizes:** Revenue kept inside the portfolio when a property is oversold
**Status:** Proposal

---

## 1. What It Is

A decision tool for the nights when one property in a multi-hotel portfolio holds more confirmed reservations than rooms. Today, "walking" a guest usually means sending them to whichever hotel nearby has a room, often a competitor.

This system treats every affected reservation and every open room across the sister properties as agents. It produces a relocation plan that:
- keeps the guest and the revenue within the portfolio;
- protects the most valuable relationships, so loyalty members, group attendees and multi-night stays are moved last;
- gives the front desk a ready-to-use script and compensation recommendation.

## 2. Why It Matters

**Overbooking is rational, and it is what creates walks.**
- A 2025 study in the *International Journal of Hospitality Management* found that "overbooking hotels appear to outperform those that don't" [1].
- Industry estimates put the no-show rate commonly "between 1-5%" [2].
- Hotels that overbook to cover that gap will, on some nights, have more guests than rooms.

**A walk is expensive beyond the room.**
- A walked guest may need "a free meal ... transportation ... a voucher" [3].
- More importantly, cited research indicates that "70% of customers who have been walked don't want to go back to the hotel again" [3].
- The real cost is the guest's future stays, not just tonight's compensation.

**A portfolio has an advantage a single hotel does not.** When sister properties sit within walking distance, an oversold night at one hotel is rarely an oversold night for the group. The loss happens because the decision is made property by property, late in the evening, under time pressure.

## 3. How It Will Be Solved

**Step 1: Early warning.**
- From the reservation system, project each property's position for the next 1 to 7 nights: reservations minus expected cancellations and no-shows, compared with rooms available.
- Flag nights where the probability of an oversell exceeds a set threshold.

**Step 2: Relocation plan.**
- For a flagged night, list:
  - every reservation that could be moved, with its room type, rate, length of stay, loyalty tier and group code;
  - every open room across the portfolio.
- The coordination engine assigns guests to rooms. It minimizes the total cost: compensation, transport, downgrade or upgrade cost, and an estimate of future value at risk.
- Hard rules are respected:
  - group blocks stay together;
  - accessibility requirements are honoured;
  - multi-night stays are not split across properties without consent.

**Step 3: Proactive outreach.** Where possible, guests are offered the move before arrival, with an incentive, rather than at the front desk at 11 PM.

**Step 4: Measurement.**
- Track walks to outside hotels against portfolio relocations, the revenue kept, and the rate at which relocated guests return.

**Deliverables:**
- An oversell-risk view by property and night.
- A recommended relocation list.
- A monthly report of revenue retained.

## 4. Data Required

- Reservation snapshots (on-the-books by night), cancellation and no-show history, and room inventory by type.
- Loyalty tier and group codes.
- A distance and transport matrix between properties.

## 5. Risks and Assumptions

- Relocation between sister properties must fit brand standards and franchise agreements. Some brands require walking within the brand.
- Future-value estimates should start simple (tier, stay history) and be calibrated against actual return behaviour.

## 6. References

1. Schwartz, Webb, Altin and Riasi, "Overbooking and performance in hotel revenue management," *International Journal of Hospitality Management*, vol. 129 (2025). https://www.sciencedirect.com/science/article/abs/pii/S027843192500115X
2. Hospitality Net (D-EDGE, vendor), *How to prevent hotel no-show and last-minute cancellations?* (Oct 2024). https://www.hospitalitynet.org/news/4124422/how-to-prevent-hotel-no-show-and-last-minute-cancellations
3. eCornell (S. Kimes), *The Cheapest and Best Approach to Overbooking*. https://ecornell-impact.cornell.edu/the-cheapest-and-best-approach-to-overbooking/
