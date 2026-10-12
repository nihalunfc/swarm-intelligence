# Project H2

**Hospitality Operations Intelligence**

H2 covers initiatives whose primary objective is operational rather than a direct cash figure: staffing, guest flow, housekeeping, facilities and reporting. Each one ultimately affects revenue and cost, but what it optimizes is time, coverage, capacity or quality. Initiatives measured directly in revenue or expense belong to [Project HARLTON](../Project%20HARLTON/README.md).

The foundation for all H2 modules is the [unified operational BI and automated reporting proposal](./proposal.md): one trusted data layer feeding self-contained dashboards. Each module below is a self-contained proposal covering what the module is, why it matters (with sourced references) and how it will be solved.

## Modules

| ID | Module | Area | Objective |
| :-- | :-- | :-- | :-- |
| 00 | [Unified Executive BI and Automated Reporting](./proposal.md) | Reporting | One data layer and automated packs instead of manual compilation |
| 01 | [Cross-Property Shift Exchange](./01-cross-property-shift-exchange/proposal.md) | Workforce | Fill open shifts with qualified, legally rested staff across properties before overtime or agency |
| 02 | [Departure Flow Balancing](./02-departure-flow-balancing/proposal.md) | Guest flow | Flatten the morning check-out peak at elevators, front desk and housekeeping |
| 03 | [Room-Ready Notifications and Housekeeping Sequencing](./03-room-ready-guest-notifications/proposal.md) | Housekeeping | Clean rooms in the order guests need them and tell guests when they are ready |
| 04 | [Review-to-Maintenance Intelligence](./04-review-to-maintenance-intelligence/proposal.md) | Facilities | Turn guest review text into maintenance work orders and recurring-issue trends |
| 05 | [Automated Schedule Builder](./05-automated-schedule-builder/proposal.md) | Workforce | Build weekly schedules automatically and publish one approved version to the workforce system, Excel and print |
| 06 | [Low-Strain Work Zone Assignment](./06-low-strain-work-zone-assignment/proposal.md) | Workforce and safety | Assign staff to compact areas with balanced physical workload and minimal walking |
| 07 | [Night Operations and Front Desk Coverage](./07-night-operations-coverage/proposal.md) | Workforce and safety | Size overnight coverage from real demand, automate audit reporting and protect lone workers |
| 08 | [Security Coverage Optimization](./08-security-coverage-optimization/proposal.md) | Security | Risk-weighted, unpredictable patrol coverage across the campus |
| 09 | [Centralized Supply Sign-Out and Department Accountability](./09-supply-sign-out-accountability/proposal.md) | Inventory | Record every item issued by department, location, person and reason, in a phased paper-to-scan process |
| 10 | [Decentralized Supply and Amenity Placement](./10-decentralized-supply-placement/proposal.md) | Inventory and layout | Place stock close to where it is used in hotels and restaurants, with par levels and replenishment routes |

Shared data model and labels: [Data Foundation](../Data%20Foundation/proposal.md). Ideas not yet ready for a full proposal: [Further Ideas](../Further%20Ideas/README.md).

## Shared Principles

- **Fit around existing systems.** H2 modules sit on top of the current scheduling, PMS and maintenance tools; they do not replace them.
- **People keep the decision.** Supervisors and managers approve every change the system proposes.
- **Rules are built in.** Employment standards, collective agreements and brand standards are encoded as hard constraints.
- **Proprietary coordination engine.** Modules that balance many independent units against a shared limit use a multi-agent coordination engine developed by the author. Its internal design is not published in this repository.
