# H2-09: Centralized Supply Sign-Out and Department Accountability

> **In short: a simple sign-out sheet, later a tablet, that records who took which supplies, for which department and why, so waste and loss can be traced and reduced.**

**Category:** Inventory operations
**Optimizes:** Control of supplies from storeroom to use: who took what, for which department and area, and why any of it was lost
**Status:** Proposal

---

## 1. What It Is

A single sign-out process for every item that leaves a storeroom or linen room. It covers guest amenities, cleaning chemicals, linen, paper goods, minibar stock and restaurant dry goods. Every issue records:

| Field | Example |
| :-- | :-- |
| Item and quantity | 2 cases bath tissue |
| Department | Housekeeping, tower B |
| Location | Floor 14 supply closet |
| Person | Employee ID of the person collecting |
| Purpose | Par refill / special request / event |
| Return or loss reason | Returned, damaged, spilled, expired, unaccounted |

Recording against department and location makes loss visible at the level where it can be managed. This is the operational side of [HARLTON-09](../../Project%20HARLTON/09-linen-and-amenity-loss-control/proposal.md), which measures the cost.

## 2. Why It Matters

**Supplies are a major rooms-department cost.** In CBRE data, laundry, linen and guest supplies made up 10.1 percent of rooms-department expenses, second only to labour [1]. Benchmarking practice is to measure these costs per occupied room, so that rising use can be separated from rising occupancy [2].

**Losses are often internal, and controls prevent them.**
- A hospitality teaching case summarizes research finding that most business losses come from internal sources rather than external ones [3].
- Across industries, organizations lose an estimated 5 percent of revenue to occupational fraud, and a lack of internal controls is the most common weakness. Food service and hospitality cases had a median loss of USD 100,000 [4].

**The basic tools are well established.**
- Food service management teaching materials state that every item leaving a storeroom should be recorded on a requisition.
- Each area should hold a defined par stock.
- Storage should be accessible to a limited number of people [5].
- What is missing in many hotels is applying this consistently, recording department and location, and analysing the records.

**Single-use amenities are changing.** Large chains are moving from small toiletry bottles to bulk dispensers [6], and New York has banned small plastic toiletry bottles in hotels [7]. Tracking consumption by area shows where bulk dispensers would save the most.

## 3. How It Will Be Solved

The process is phased so that every employee can use it from the first day, whatever their comfort with technology.

**Phase 1: Paper, with structure.**
- A standard sign-out sheet at each storeroom, with columns for each field above.
- A pre-printed list of departments, locations and reason codes.
- Sheets are entered daily by the storeroom attendant.

**Phase 2: Shared kiosk.**
- A tablet at the storeroom door. Employees tap their ID badge, pick items from a picture menu and choose a reason.
- Paper remains available as a fallback.

**Phase 3: Scanning.** Barcode or QR labels on shelves and closets. High-value items such as robes and linen can later move to RFID where [HARLTON-09](../../Project%20HARLTON/09-linen-and-amenity-loss-control/proposal.md) shows a business case.

**Analysis**, which is the same in every phase:
- Expected use per area is calculated from occupancy and standards, for example amenity sets per checkout.
- Variance against actual issues is reported by department, location and week.
- The multi-agent coordination engine sets par levels per closet, with each closet as an agent, so that stock is neither short nor hoarded.
- Outliers trigger a review, not an accusation.

**Deliverables:**
- A sign-out sheet and reason-code list.
- A kiosk workflow.
- A weekly variance report by department and location.
- A par-level recommendation per closet.
- A monthly cost-per-occupied-room trend.

## 4. Data Required

- Item master with unit costs.
- Storeroom and closet locations.
- Department and cost-centre codes, aligned to the hotel's chart of accounts.
- Employee IDs.
- Occupancy and room-type data.
- Purchase records.

## 5. Risks and Assumptions

- The process must be fast. If signing out takes longer than a minute, it will be skipped. Kiosk design is tested with staff before rollout.
- Records are used to find process problems, such as wrong par levels or storage that encourages waste, not to target individuals. This is communicated clearly to staff and, where applicable, to the union.
- No authoritative benchmark was found for hotel supply cost per occupied room, so the property's own baseline is established first.

## 6. References

1. Lodging Magazine (CBRE data), *Trends in Rooms Department Costs: Fixed and Variable Expenses* (Dec 2021). https://lodgingmagazine.com/trends-in-rooms-department-costs-a-study-in-fixed-and-variable-expenses/
2. HotStats (benchmarking firm), *PAR or POR? A Guide to Interpreting Hotel Operational Ratios*. https://www.hotstats.com/blog/par-or-por-a-guide-to-interpreting-hotel-operational-ratios
3. Lee and Lee, "Cases of Employee Theft in the Hospitality Industry," *Journal of Hospitality and Tourism Cases*, I-CHRIE. https://www.chrie.org/assets/docs/JHTC-case-notes/JHTC-vol-9/JHTC_9_2_Lee_Case.pdf
4. Association of Certified Fraud Examiners, *Occupational Fraud 2024: A Report to the Nations*. https://www.acfe.com/en-us/-/media/files/acfe/pdfs/rttn/2024/2024-report-to-the-nations.pdf
5. BC Cook Articulation Committee, *Basic Kitchen and Food Service Management*, Chapter 10. https://psu.pb.unizin.org/hmd329/chapter/ch10/
6. Canadian Geographic, *Hotel chains are phasing out single-use plastic*. https://canadiangeographic.ca/articles/hotel-chains-are-phasing-out-single-use-plastic/
7. New York State Empire State Development, *NYS Prohibition on Hospitality Personal Care Products* (advisory). https://esd.ny.gov/sites/default/files/media/document/SBESO-Personal-Care-Bottles-Flyer-1162026.pdf
