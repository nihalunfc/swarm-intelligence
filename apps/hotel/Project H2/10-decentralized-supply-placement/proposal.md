# H2-10: Decentralized Supply and Amenity Placement

> **In short: keep supplies close to where they are used, in hotels and restaurants alike, so staff spend less time walking to the storeroom.**

**Category:** Inventory and layout operations (hotels and restaurants)
**Optimizes:** Where supplies are stored and how much is kept at each point, so staff walk less and stock is always where it is needed
**Status:** Proposal

---

## 1. What It Is

A placement plan for supplies across a resort, covering both hotel and restaurant operations. It replaces two common extremes:

- **Over-centralized:** one main storeroom far from the work, with long trips to restock.
- **Uncontrolled decentralized:** stock hoarded in carts, closets and back corners, with nobody knowing what is where.

The proposal decentralizes stock to well-placed points close to where it is used: floor closets, pool-deck towel stations, restaurant prep stations and banquet pantries. Each point has a defined par level and replenishment route, and the sign-out control of [H2-09](../09-supply-sign-out-accountability/proposal.md) applies at every point.

## 2. Why It Matters

**Travel is the largest hidden cost of fetching things.**
- In warehouse operations, order picking can account for up to 55 percent of operating expense, and travel is typically the dominant part of a picker's time. A widely cited breakdown puts it at about half [1].
- A room attendant or line cook walking to a distant storeroom is doing the same unproductive travel.

**Kitchens show the same pattern.**
- Food service teaching material notes that changes to mise en place can reduce meal preparation time during busy periods. It recommends placing storage areas next to the preparation areas that use them [2].
- Kitchen ergonomics studies list excessive distance between storage and workstations as a recurring problem [3].

**Placement affects strain as well as time.** Housekeeping already has the highest injury rate of any hotel role [4]. Shorter carries and fewer heavy restocking trips reduce both time and physical load, which links directly to [H2-06](../06-low-strain-work-zone-assignment/proposal.md).

**Amenity formats are changing.** Major chains are moving to bulk dispensers, removing hundreds of millions of small bottles a year [5]. This changes what needs to be stored on each floor and how often it is replenished.

## 3. How It Will Be Solved

**Step 1: Map demand by location.** From occupancy, room mix and the sign-out records of [H2-09](../09-supply-sign-out-accountability/proposal.md), estimate daily use of each item at each point:
- each floor;
- the pool deck;
- each restaurant station;
- each banquet room.

**Step 2: Classify items by speed.** Fast movers used every shift (towels, amenity refills, glassware) go closest to the work. Slow movers and bulk stock stay central. This is the slotting principle used in warehouses [1].

**Step 3: Place and size.**
- The multi-agent coordination engine treats each storage point as an agent with limited space.
- It decides which items each point holds and at what par level, minimizing total staff walking plus replenishment trips. Shelf space and security are constraints.
- In kitchens, the same model places prep stock next to the station that uses it [2].

**Step 4: Replenishment routes.** Runners restock decentralized points on a fixed route outside peak hours. Restocking is planned work instead of an interruption.

**Step 5: Measure.**
- Stock-outs at each point.
- Trips to the central storeroom.
- Restocking labour hours.
- Time per room or per cover.
- Supply variance from [H2-09](../09-supply-sign-out-accountability/proposal.md).

**Deliverables:**
- A placement map per building and kitchen.
- Par levels per point.
- A replenishment route and schedule.
- A quarterly re-slotting review as usage changes.

## 4. Data Required

- Floor plans and kitchen layouts with storage locations and capacities.
- Item list with sizes.
- Sign-out and usage records.
- Occupancy and room mix.
- Restaurant covers by station.
- Banquet calendar.

## 5. Risks and Assumptions

- More storage points means more places for stock to go missing. Decentralization only works together with the sign-out control in [H2-09](../09-supply-sign-out-accountability/proposal.md).
- No quantitative study of walking time in hotel housekeeping or restaurant kitchens was found. Warehouse research is used as the analogy, and the pilot measures actual savings.
- Fire codes and food safety rules limit what can be stored in corridors and near preparation areas.

## 6. References

1. de Koster, Le-Duc and Roodbergen, "Design and control of warehouse order picking: a literature review," *European Journal of Operational Research* 182 (2007). https://pure.eur.nl/ws/portalfiles/portal/46713708/DesignandControl_2007.pdf
2. BC Cook Articulation Committee, *Working in the Food Service Industry: Principles of Organization and Time Management*. https://opentextbc.ca/workinginfoodserviceindustry/chapter/principles-of-organization-and-time-management/
3. Ismail, Osman and Rahman, "Ergonomics Kitchen: A Better Place to Work," *International Journal of Academic Research in Business and Social Sciences* (2021). https://hrmars.com/papers_submitted/8501/ergonomics-kitchen-a-better-place-to-work.pdf
4. Buchanan et al., "Occupational injury disparities in the US hotel industry," *American Journal of Industrial Medicine* (2010). https://onlinelibrary.wiley.com/doi/abs/10.1002/ajim.20724
5. Canadian Geographic, *Hotel chains are phasing out single-use plastic*. https://canadiangeographic.ca/articles/hotel-chains-are-phasing-out-single-use-plastic/
