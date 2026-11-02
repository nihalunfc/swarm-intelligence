# HARLTON-11: Year-Round Occupancy and Room Sales Strategy

> **In short: a plan for every night of the year that prices busy nights correctly and fills quiet nights with the right guests, groups and packages.**

**Category:** Revenue strategy
**Optimizes:** Total room revenue across all 365 nights and all properties, by filling low-demand periods and pricing high-demand periods correctly
**Status:** Proposal

---

## 1. What It Is

A 365-day selling plan for a multi-property resort portfolio. It turns the findings of [HARLTON-10](../10-historical-demand-intelligence/proposal.md) into concrete actions for every date. Each date is assigned a demand tier, and each tier has its own playbook for:
- pricing;
- stay restrictions;
- channels;
- group sales;
- packages;
- targeted marketing.

The aim is not simply to be full every night. A hotel that is full every night is almost certainly charging too little on its busiest nights. The aim is:
- the highest total revenue across the year;
- full occupancy on the nights where demand allows a strong rate;
- deliberate, profitable base business on the nights that would otherwise be empty.

## 2. Why It Matters

**Occupancy alone is the wrong target.**
- A Cornell study of more than 6,000 hotels found that hotels pricing above their competitive set ran lower occupancy but higher RevPAR. Hotels that discounted gained occupancy without gaining RevPAR [1].
- Industry guidance makes the same point: a property running 70 to 80 percent occupancy at a high ADR can be more profitable than one that is fuller at a lower rate (vendor-authored) [2].
- The right goal is revenue and profit, measured across every revenue centre. This is what total hotel revenue management means [3].

**Demand in Canada is strongly seasonal.**
- Canadian hotel occupancy was 51.5% in January 2026 [4], against 80.7% in August 2025, the highest August since 2014 [5].
- For 2025 as a whole, national occupancy was 66.1% at an ADR of CAD 216.10. Ontario was the only province where occupancy declined [6].
- A resort portfolio therefore has a short window when it can command its highest rates and long stretches when it must create demand.

**Events create compression that must be priced, not just filled.**
- In June 2026, Toronto ADR rose 19.0% to CAD 321.27 with FIFA World Cup matches in the city [7].
- In October 2025, the World Series lifted Toronto ADR by 14.8% [8].
- Selling those dates at normal rates, or to discounted groups, leaves revenue that cannot be recovered.

**The low season is fillable, but only with targeted effort.**
- Revenue management research recommends targeting specific, profitable past guests in low-demand periods instead of sending mass discounts to everyone [9].
- Loyalty programme members generated about 50 percent more revenue than non-members in a Cornell study [10].
- Sport tourism in Canada was worth CAD 6.8 billion in spending in 2018 [11]. Tournaments, meetings and tour groups are a natural base for shoulder and winter dates.

**The selling levers are well understood.**
- Price and stay length are the two strategic levers of yield management [12].
- Hotels can close dates to arrival, require minimum stays or set maximum stays to shape demand [13].
- What is usually missing is applying them consistently, date by date and property by property, from evidence.

**Channel choice affects net revenue.**
- OTA commissions typically run 15 to 25 percent of the room rate, while direct bookings cost a small fraction of that [14].
- OTA bookings also cancel at much higher rates than direct bookings: 50% for one major OTA against 18.2% for direct, in one European study (vendor research) [15].

## 3. How It Will Be Solved

### Step 1: Assign a demand tier to every date

Using unconstrained demand, pace and event signals from [HARLTON-10](../10-historical-demand-intelligence/proposal.md) and [HARLTON-06](../06-event-and-exchange-rate-demand-signals/proposal.md), label every date for the next 365 days as one of four tiers:

| Tier | Definition | Typical dates |
| :-- | :-- | :-- |
| Compression | Unconstrained demand well above capacity | Summer Saturdays, major events, long weekends |
| High | Demand near capacity | Summer weekdays, shoulder-season weekends |
| Shoulder | Demand clearly below capacity but responsive | Spring and autumn weekdays |
| Need | Demand far below capacity | Winter weekdays outside holidays |

### Step 2: Apply the tier playbook

| Lever | Compression | High | Shoulder | Need |
| :-- | :-- | :-- | :-- | :-- |
| Price | Hold or raise; no discounting [1] | Hold, adjust to pace | Targeted offers behind rate fences | Packages rather than visible rate cuts |
| Stay rules | Minimum stay, closed to arrival on peak night [13] | Minimum stay on peak night only | None | Encourage longer stays with value-adds |
| Groups | Only groups that beat displaced transient revenue | Selective, priced on displacement | Actively pursue | Base business: tournaments, tours, meetings, training [11] |
| Channel | Favour direct; limit OTA allocation [14] | Balanced | Open all channels | Open all channels plus wholesale for base |
| Marketing | None needed | Loyalty early access | Repeat-guest targeting [9][10] | Repeat-guest and regional drive-market campaigns |
| Ancillary | Parking and amenity pricing ([HARLTON-04](../04-amenity-day-pass-yield/proposal.md), [HARLTON-05](../05-event-based-parking-pricing/proposal.md)) | Upsell early/late stays ([HARLTON-03](../03-early-arrival-late-departure-revenue/proposal.md)) | Bundles with dining and attractions | Day passes and packages to drive spend |

### Step 3: Coordinate across the portfolio

The portfolio's room inventory is a grid of property, room type and date. The multi-agent coordination engine treats each cell as an agent with its own forecast demand and price response. Agents negotiate so that:
- groups are steered to the property and dates where they displace the least transient revenue;
- overflow on compression nights moves between sister properties instead of to competitors ([HARLTON-02](../02-guest-relocation-revenue-retention/proposal.md));
- need-period campaigns are spread across properties so they do not compete with each other.

### Step 4: Weekly selling rhythm

A one-page weekly brief for the revenue meeting:
- dates whose tier has changed;
- dates where pace is behind or ahead of history;
- recommended actions for each, with the evidence;
- group requests scored against displacement.

The revenue manager decides. The brief makes the decision faster and consistent across properties.

### Step 5: Measure

Track the following and report them monthly:
- RevPAR and RevPAR index against the competitive set, by tier;
- need-period occupancy and revenue;
- compression-night ADR;
- group displacement accuracy;
- net revenue after acquisition cost, by channel.

**Deliverables:**
- A 365-day tier calendar.
- A tier playbook.
- A weekly selling brief.
- A portfolio group-placement recommendation.
- A monthly performance report by tier.

## 4. Data Required

- Everything listed in [HARLTON-10](../10-historical-demand-intelligence/proposal.md).
- Current rate plans and restrictions.
- Channel costs.
- Group pipeline from sales.
- Competitor rates.
- Loyalty and guest history for targeting, under the privacy controls in the [Data Foundation](../../Data%20Foundation/proposal.md).

## 5. Risks and Assumptions

- Demand tiers must be reviewed weekly. A date can move from Shoulder to Compression when an event is announced.
- Minimum-stay and closed-to-arrival rules must be applied carefully and explained to guests. Overuse can push demand to competitors.
- Brand standards, franchise agreements and existing contracts with groups and wholesalers limit how far each lever can move.
- National and provincial figures below describe the market. Property-level history from HARLTON-10 replaces them as soon as it is available.

## 6. References

1. Canina, Enz and Lomanno, *Why Discounting Doesn't Work: A Hotel Pricing Update*, Cornell Center for Hospitality Research (2006). https://ecommons.cornell.edu/entities/publication/58885f90-3d7b-461f-927b-ad9cb826a241
2. HSMAI (vendor-authored insight), *Evolving Revenue Management: Total Revenue Management and Profit Optimization*. https://global.hsmai.org/insight/evolving-revenue-management-total-revenue-management-profit-optimization/
3. Noone, Enz and Glassmire, *Total Hotel Revenue Management: A Strategic Profit Perspective*, Cornell Center for Hospitality Research (2017). https://ecommons.cornell.edu/server/api/core/bitstreams/b5fa740e-fbe8-4044-a2cc-395b86dc479c/content
4. Hospitality Net (CoStar data), *Canada hotels report highest occupancy gain since July 2025* (2026). https://www.hospitalitynet.org/news/4131171/canada-hotels-report-highest-occupancy-gain-since-july-2025
5. Destination Canada, *Canadian tourism delivers almost $60B this summer*. https://www.destinationcanada.com/en-ca/news/canadian-tourism-delivers-almost-60b-this-summer-driving-national-wealth-and-unprecedented-dispersion-across-the-country
6. CoStar, *Canada hotels post record-setting performance in 2025* (Jan 2026). https://www.costar.com/products/str-benchmark/resources/press-releases/canada-hotels-post-record-setting-performance-2025
7. CoStar, *Canada hotels report first monthly occupancy ...* (June 2026 performance). https://www.costar.com/products/str-benchmark/resources/press-releases/canada-hotels-report-first-monthly-occupancy
8. Hospitality Net (CoStar data), October 2025 Canada hotel performance. https://www.hospitalitynet.org/news/4129909.html
9. Noone, Kimes and Renaghan, *Integrating Customer Relationship Management and Revenue Management: A Hotel Perspective*, Cornell University. https://ecommons.cornell.edu/server/api/core/bitstreams/0a97c6cb-a00f-469e-ac6b-3c850900e97b/content
10. Hospitality Net, *Cornell Study Demonstrates the Value of Hotel Loyalty Programs* (2014). https://www.hospitalitynet.org/news/4063852.html
11. Sport Tourism Canada, *Sport tourism spending in Canada holds steady at $6.8 billion*. https://sporttourismcanada.com/sport-tourism-spending-in-canada-holds-steady-at-6-8-billion/
12. Kimes and Chase, "The Strategic Levers of Yield Management," *Journal of Service Research* (1998). https://journals.sagepub.com/doi/10.1177/109467059800100205
13. Rohlfs and Kimes, *Best-Available-Rate Pricing at Hotels: A Study of Customer Perceptions and Reactions*, Cornell Center for Hospitality Research (2005). https://ecommons.cornell.edu/server/api/core/bitstreams/cccedfc6-b113-4ff0-9190-d4afecfdce66/content
14. Hotel Online, *What OTAs Actually Cost in 2026*. https://www.hotel-online.com/news/what-otas-actually-cost-in-2026
15. Hotel Management (D-EDGE study, vendor), *Cancellation rate at 40% as OTAs push free change policy*. https://www.hotelmanagement.net/tech/study-cancelation-rate-at-40-as-otas-push-free-change-policy
