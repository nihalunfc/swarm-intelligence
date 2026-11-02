# Project HARLTON

**Hospitality Asset & Revenue Learning, Tactical Optimization Network**

HARLTON covers every initiative whose objective is measured directly in money: revenue gained, revenue protected from loss, or expense removed. Operational initiatives whose primary objective is not a cash figure, such as staffing, guest flow and facilities, belong to [Project H2](../Project%20H2/README.md).

The overall architecture is described in the [HARLTON master proposal](./proposal/proposal.md). Each module below is a self-contained proposal covering what the module is, why it matters (with sourced references) and how it will be solved.

## Modules

| ID | Module | Lever | Objective |
| :-- | :-- | :-- | :-- |
| 01 | [Peak-Hour Energy Cost Reduction](./01-peak-hour-energy-cost/proposal.md) | Expense | Move flexible load out of the five provincial peak hours that set the Global Adjustment charge |
| 02 | [Guest Relocation and Revenue Retention](./02-guest-relocation-revenue-retention/proposal.md) | Revenue protection | Keep oversold guests and their revenue inside the portfolio |
| 03 | [Early Arrival and Late Departure Revenue](./03-early-arrival-late-departure-revenue/proposal.md) | Ancillary revenue | Sell early check-in and late check-out against forecast room readiness |
| 04 | [Amenity Day-Pass Yield Management](./04-amenity-day-pass-yield/proposal.md) | Ancillary revenue | Sell spare waterpark, pool and spa capacity on low-occupancy days |
| 05 | [Event-Based Parking Pricing](./05-event-based-parking-pricing/proposal.md) | Ancillary revenue | Price parking by forecast demand and local events |
| 06 | [Event and Exchange-Rate Demand Signals](./06-event-and-exchange-rate-demand-signals/proposal.md) | Revenue forecasting | Add events, holidays, USD/CAD and cross-border travel to the demand forecast |
| 07 | [Vacant-Room Energy Setback](./07-vacant-room-energy-setback/proposal.md) | Expense | Relax heating and cooling in unsold rooms using PMS room status |
| 08 | [Water Leak Detection from Meter Data](./08-water-leak-detection/proposal.md) | Expense | Detect leaks from overnight minimum flow |
| 09 | [Linen and Amenity Loss Control](./09-linen-and-amenity-loss-control/proposal.md) | Expense | Measure and locate linen and amenity loss |
| 10 | [Historical Demand Intelligence](./10-historical-demand-intelligence/proposal.md) | Revenue analytics | Twelve repeatable analyses of multi-year booking history: seasonality, pace, unconstrained demand, segments, cancellations, price response |
| 11 | [Year-Round Occupancy and Room Sales Strategy](./11-year-round-occupancy-strategy/proposal.md) | Revenue strategy | A 365-day demand-tier calendar and selling playbook to price peaks correctly and fill need periods profitably |

Shared data model and labels: [Data Foundation](../Data%20Foundation/proposal.md). Ideas not yet ready for a full proposal: [Further Ideas](../Further%20Ideas/README.md).

## Shared Principles

- **Decision support first.** Every module recommends and explains; people approve.
- **Existing data first.** Modules start from data hotels already hold (PMS, POS, meters, schedules) before any new hardware.
- **Measured savings.** Each module ends with a measurement step that ties results back to the ledger.
- **Proprietary coordination engine.** Modules that allocate a shared, limited resource across many independent units use a multi-agent coordination engine developed by the author. Its internal design is not published in this repository.
