# H2-04: Review-to-Maintenance Intelligence

> **In short: read guest reviews every day, pick out real problems such as a noisy air conditioner, and turn them into repair tickets before the next guest complains.**

**Category:** Facilities and guest experience operations
**Optimizes:** Speed of finding and fixing recurring room and facility problems that guests write about
**Status:** Proposal

---

## 1. What It Is

A text-analysis pipeline that reads guest reviews and post-stay surveys every day. It extracts specific, fixable problems with their location, for example "AC loud in 14th floor corner room", "pool too cold" or "slow elevators in the north tower". It then matches them against the maintenance ticket log.

The output is a short daily list of problems that guests are reporting but that have no open work order. It also shows recurring problems by room, floor and tower over time.

## 2. Why It Matters

**Reviews contain operational data that nobody routes to engineering.**
- Peer-reviewed analysis of hotel reviews finds that "cleanliness, indoor air quality, and acoustics had the strongest negative impacts when underperforming" [1].
- A 2025 model of negative reviews identified "seven types of customer complaints, including service, facility, cleanliness, price, location, dining, and noise" [2].
- Facility problems dominate complaints at budget hotels, while service and price dominate at high-end hotels [3].

**Negative comments weigh more than positive ones.** Cornell research analysing 5,830 reviews found that "negative comments carry more weight in a guest's rating than positive ones" [4]. One unfixed noisy air conditioner can depress the scores of every guest assigned to that room until it is repaired.

**Review scores affect pricing power.** Cornell's Center for Hospitality Research found that a one-point increase in review score on a five-point scale allows a hotel to increase its price by 11.2 percent [5]. Fixing what guests complain about protects the rate the revenue team can charge.

**The data already exists but is siloed.** In a 2024 industry study, 69% of respondents named integrating new technology with legacy systems as their top challenge, and 72% highlighted the importance of improving analytics [6].

## 3. How It Will Be Solved

**Step 1: Collect.** Gather daily review and survey text with stay dates and, where available, room numbers. The room is linked through the reservation where the guest identity is known internally.

**Step 2: Extract.**
- Classify each comment into a fixed set of operational categories: HVAC, noise, plumbing, elevator, Wi-Fi, cleanliness, pool and amenities, parking.
- Pull out location cues such as room, floor or tower.

**Step 3: Match.**
- Compare against open and recent maintenance tickets for the same location and category.
- Unmatched issues become suggested work orders.

**Step 4: Trend.**
- Track recurring issues by room and floor.
- A room with three HVAC mentions in a month is flagged for inspection before the next guest.

**Step 5: Measurement.** Time from first mention to ticket, repeat mentions after repair, and category-level review sentiment over time.

**Deliverables:**
- A daily "reported but not ticketed" list.
- A recurring-issue heat map by floor.
- A monthly guest-reported issues report for engineering and the general manager.

## 4. Data Required

- Review and survey text with stay dates, reservation-to-room linkage (internal only), and the maintenance ticket log with locations and categories.

## 5. Risks and Assumptions

- Guest personal information stays inside the hotel's systems. Only categories, locations and dates are reported.
- Many reviews do not mention a room number, so floor or tower-level patterns are the realistic first target.

## 6. References

1. Zhang et al., *Building and Environment* (2025). https://www.sciencedirect.com/science/article/pii/S036013232500616X
2. Xu et al., *International Journal of Hospitality Management* (2025). https://www.sciencedirect.com/science/article/abs/pii/S0278431924003694
3. Hu et al., *Tourism Management* (2019). https://www.sciencedirect.com/science/article/abs/pii/S0261517719300020
4. Cornell Chronicle, *Online reviews only partially reveal what hotel customers think* (Mar 2016). https://news.cornell.edu/stories/2016/03/online-reviews-only-partially-reveal-what-hotel-customers-think
5. C. Anderson, *The Impact of Social Media on Lodging Performance*, Cornell Center for Hospitality Research (2012). https://ecommons.cornell.edu/handle/1813/71194
6. Hospitality Technology, *2024 Lodging Technology Study*. https://hospitalitytech.com/2024-lodging-tech-study
