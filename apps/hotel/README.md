# Hospitality Data Architecture and Business Intelligence

A portfolio of proposals and working tools for multi-property resort hotels. The aim is to turn data hotels already collect into decisions that protect revenue, remove avoidable cost and make daily operations run more smoothly. Every proposal states what the problem is, why it matters, with linked sources, and how it would be solved and measured.

## Live Demos

**Start here: [nihalunfc.github.io/hotel-business](https://nihalunfc.github.io/hotel-business/)**

| Demo | What it shows |
| :-- | :-- |
| [Revenue Command Centre](https://nihalunfc.github.io/hotel-business/revenue.html) | Three years of booking history turned into a 365-night demand calendar, a weekly selling brief, booking pace against last year, demand turned away on sold-out nights, channel net rates, cancellations, and a forecast accuracy check. |
| [Staff Schedule Builder](https://nihalunfc.github.io/hotel-business/schedule.html) | A housekeeping schedule built from expected workload, checked against Ontario labour rules, compared with a fixed weekly pattern, and exported to Excel, print and a staff-app shift list. |

Both demos run on one shared sample dataset of five fictional hotels (about 640,000 bookings over four years). The code that builds it, the SQL warehouse, the quality checks and the tests are in [analytics/](./analytics). A small extract of the sample data is in [data/sample/](./data/sample).

## Projects

### [Project HARLTON](./Project%20HARLTON/README.md): Revenue, Profit and Expense
**Hospitality Asset & Revenue Learning, Tactical Optimization Network.** Initiatives measured directly in money.

| ID | Module | Lever |
| :-- | :-- | :-- |
| 01 | [Peak-Hour Energy Cost Reduction](./Project%20HARLTON/01-peak-hour-energy-cost/proposal.md) | Expense |
| 02 | [Guest Relocation and Revenue Retention](./Project%20HARLTON/02-guest-relocation-revenue-retention/proposal.md) | Revenue protection |
| 03 | [Early Arrival and Late Departure Revenue](./Project%20HARLTON/03-early-arrival-late-departure-revenue/proposal.md) | Ancillary revenue |
| 04 | [Amenity Day-Pass Yield Management](./Project%20HARLTON/04-amenity-day-pass-yield/proposal.md) | Ancillary revenue |
| 05 | [Event-Based Parking Pricing](./Project%20HARLTON/05-event-based-parking-pricing/proposal.md) | Ancillary revenue |
| 06 | [Event and Exchange-Rate Demand Signals](./Project%20HARLTON/06-event-and-exchange-rate-demand-signals/proposal.md) | Revenue forecasting |
| 07 | [Vacant-Room Energy Setback](./Project%20HARLTON/07-vacant-room-energy-setback/proposal.md) | Expense |
| 08 | [Water Leak Detection from Meter Data](./Project%20HARLTON/08-water-leak-detection/proposal.md) | Expense |
| 09 | [Linen and Amenity Loss Control](./Project%20HARLTON/09-linen-and-amenity-loss-control/proposal.md) | Expense |
| 10 | [Historical Demand Intelligence](./Project%20HARLTON/10-historical-demand-intelligence/proposal.md) | Revenue analytics |
| 11 | [Year-Round Occupancy and Room Sales Strategy](./Project%20HARLTON/11-year-round-occupancy-strategy/proposal.md) | Revenue strategy |

Master architecture: [HARLTON proposal](./Project%20HARLTON/proposal/proposal.md)

### [Project H2](./Project%20H2/README.md): Operations Intelligence
Initiatives that optimize staffing, guest flow, housekeeping and facilities. They affect revenue indirectly, but their direct objective is operational.

| ID | Module | Area |
| :-- | :-- | :-- |
| 00 | [Unified Executive BI and Automated Reporting](./Project%20H2/proposal.md) | Reporting |
| 01 | [Cross-Property Shift Exchange](./Project%20H2/01-cross-property-shift-exchange/proposal.md) | Workforce |
| 02 | [Departure Flow Balancing](./Project%20H2/02-departure-flow-balancing/proposal.md) | Guest flow |
| 03 | [Room-Ready Notifications and Housekeeping Sequencing](./Project%20H2/03-room-ready-guest-notifications/proposal.md) | Housekeeping |
| 04 | [Review-to-Maintenance Intelligence](./Project%20H2/04-review-to-maintenance-intelligence/proposal.md) | Facilities |
| 05 | [Automated Schedule Builder](./Project%20H2/05-automated-schedule-builder/proposal.md) | Workforce |
| 06 | [Low-Strain Work Zone Assignment](./Project%20H2/06-low-strain-work-zone-assignment/proposal.md) | Workforce and safety |
| 07 | [Night Operations and Front Desk Coverage](./Project%20H2/07-night-operations-coverage/proposal.md) | Workforce and safety |
| 08 | [Security Coverage Optimization](./Project%20H2/08-security-coverage-optimization/proposal.md) | Security |
| 09 | [Centralized Supply Sign-Out and Department Accountability](./Project%20H2/09-supply-sign-out-accountability/proposal.md) | Inventory |
| 10 | [Decentralized Supply and Amenity Placement](./Project%20H2/10-decentralized-supply-placement/proposal.md) | Inventory and layout |

### [Data Foundation](./Data%20Foundation/proposal.md)
The shared data layer behind both projects: data sources, star-schema fact and dimension tables, controlled label sets, database layers, data quality checks and privacy governance.

### [Further Ideas](./Further%20Ideas/README.md)
Ideas with real potential that are not yet ready for a full proposal, each listed with what it lacks and what would make it viable.

## Repository Layout

| Folder | Contents |
| :-- | :-- |
| [Project HARLTON](./Project%20HARLTON/README.md) | Revenue, profit and expense proposals |
| [Project H2](./Project%20H2/README.md) | Operations proposals |
| [Data Foundation](./Data%20Foundation/proposal.md) | Shared data model, labels and governance |
| [Further Ideas](./Further%20Ideas/README.md) | Ideas with their limitations |
| [analytics](./analytics) | Python and SQL pipeline behind the demos, with tests |
| [docs](./docs) | The demo website (GitHub Pages) |
| [data/sample](./data/sample) | Small extracts of the generated sample data |
| [June 2026](./June%202026) | Earlier booking snapshot analysis |

## Credits and Tools

The ideas, direction, judgement calls and final review in this repository are my own. I used AI assistants throughout, the same way I would use them on the job, and I want that to be clear.

**AI assistants**
- **Claude** (Anthropic), working through the Claude app with **Claude Code** as the agent environment: research and fact-checking of every cited source, drafting and editing of the module proposals, the Data Foundation, the analytics package, the demo website, tests and repository organization.
- **Gemini** (Google), used inside **Google Antigravity**: the first versions of the HARLTON and H2 proposals, the repository setup, and the initial Python analysis in the June 2026 folder.

**Platforms and services**
- **GitHub** and **GitHub Pages** for version control and hosting the demos.
- **Kaggle Notebooks** for running the June 2026 analysis.

**Open-source software**
- Python, pandas, NumPy, python-dateutil and SQLite for data processing and the warehouse.
- PuLP with the COIN-OR CBC solver for schedule optimization.
- openpyxl for Excel output.
- pytest for tests.
- Chart.js for charts.
- The Inter typeface via Google Fonts.
- Playwright with Chromium for checking how the pages render.

**Sources.** The public research and data behind each proposal are cited, with links, at the end of that proposal.

---
*All proposals use public, cited sources and synthetic or anonymized examples. No employer data is included. The multi-agent coordination engine referenced in several modules is the author's own work and is not published here.*
