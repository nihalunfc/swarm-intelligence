# Data Foundation

> **In short: one agreed set of tables, labels and rules that every report uses, so the same question always gets the same, trustworthy answer.**

**Scope:** Shared by [Project HARLTON](../Project%20HARLTON/README.md) and [Project H2](../Project%20H2/README.md)
**Defines:** What data is needed, where it comes from, how it is labelled, and how it is stored and governed
**Status:** Proposal

---

## 1. Purpose

Every module in this repository depends on the same small set of trustworthy data. This document defines that foundation once. Each module can then be built on shared tables instead of its own spreadsheet extract. It follows three industry conventions:
- dimensional modelling for analytics [1][2];
- the hotel industry's standard chart of accounts for departments and expense categories [3];
- established hospitality integration standards for exchanging data between systems [4][5].

It also builds privacy in from the start, under Canada's federal private-sector privacy principles [6].

## 2. Why a Shared Foundation Matters

- **Integration is the main obstacle.** In a 2024 industry study, 69% of respondents named integrating new technology with legacy systems as their top challenge, and 72% highlighted the importance of improving analytics [7].
- **Manual reporting is costly.** An industry distribution study found that 80% of hotels spend up to two days a week on manual reporting [8].
- **Consistent definitions prevent arguments about numbers.** When "room nights", "occupied room" and "department" mean the same thing in every report, results can be compared across properties and trusted by the general manager.

## 3. Data Sources

| Domain | Source system | Key content | Refresh |
| :-- | :-- | :-- | :-- |
| Reservations | Property management system (PMS) | Bookings, daily snapshots, stays, rates, segments, channels, cancellations | Nightly snapshot |
| Revenue | PMS folios, point of sale (POS) | Room, food and beverage, parking, amenity and spa revenue | Daily |
| Groups | Sales and catering system | Blocks, pickup, contracts, function space | Daily |
| Workforce | Workforce management system | Schedules, time punches, roles, skills | Daily |
| Housekeeping | PMS room status, housekeeping app | Room status timestamps, assignments | Real time to hourly |
| Supplies | Sign-out records ([H2-09](../Project%20H2/09-supply-sign-out-accountability/proposal.md)), purchasing | Issues, returns, losses, purchases | Daily |
| Facilities | Maintenance system, building management, utility meters | Work orders, equipment, interval energy and water data | 15-minute to daily |
| Guest feedback | Review sites, post-stay surveys | Text, scores, stay dates | Daily |
| Security | Incident log | Time, zone, type, response | Daily |
| External | IESO, Statistics Canada, Bank of Canada, weather, event listings | Grid demand, travel counts, exchange rates, weather, events | Daily to monthly |

## 4. Data Model

The analytical layer is a star schema. Each fact table is linked to shared dimension tables [2]. Every fact table has a single, written grain, and grains are never mixed in one table [1].

### Fact tables

| Fact table | Grain (one row is...) | Main measures | Used by |
| :-- | :-- | :-- | :-- |
| fact_reservation_snapshot | one booking on one snapshot date | rooms, room nights, revenue on the books, status | HARLTON-02, 10, 11 |
| fact_stay_night | one booking for one occupied night | rooms occupied, room revenue | HARLTON-06, 10, 11 |
| fact_folio_revenue | one revenue posting | amount, department, revenue type | HARLTON-03, 04, 05 |
| fact_group_block | one group block for one night | rooms blocked, rooms picked up | HARLTON-10, 11 |
| fact_shift | one scheduled shift | planned hours, role, location | H2-01, 05, 07 |
| fact_time_punch | one worked shift | actual hours, overtime hours | H2-01, 05 |
| fact_room_status_event | one room status change | timestamp, from-status, to-status | H2-02, 03, 06 |
| fact_supply_issue | one sign-out line | quantity, cost, reason code | HARLTON-09, H2-09, 10 |
| fact_meter_interval | one meter reading interval | kWh, kW, litres | HARLTON-01, 07, 08 |
| fact_work_order | one maintenance ticket | open time, close time, category | H2-04 |
| fact_review_issue | one issue extracted from a review | category, sentiment, location cue | H2-04 |
| fact_incident | one security or safety incident | type, severity, response minutes | H2-07, 08 |

### Dimension tables

| Dimension | Key attributes | Notes |
| :-- | :-- | :-- |
| dim_date | date, weekday, week, month, season, holiday flags (Canada and US), demand tier | Holiday flags for both countries |
| dim_time | hour, quarter-hour, day part | For intraday analysis |
| dim_property | property, brand, address, room count | Anonymized in public examples |
| dim_room | room number, floor, tower, room type, view, bed type, accessible flag, zone | Slowly changing: renovations keep history |
| dim_rate_plan | rate code, rate type, restrictions, fences | |
| dim_segment | market segment, sub-segment | Controlled list, see section 5 |
| dim_channel | channel, commission rate | |
| dim_guest | pseudonymous guest key, loyalty tier, country, repeat flag | No names or contact details in the analytics layer |
| dim_employee | pseudonymous employee key, department, job, seniority band, skills | Slowly changing: job changes keep history |
| dim_department | department and cost centre aligned to USALI [3] | |
| dim_location | zone, floor, area type (guest floor, pool, kitchen, garage) | Shared by supplies, security, housekeeping |
| dim_item | item, category, unit, unit cost, speed class | |
| dim_event | event, venue, expected attendance, type | |
| dim_weather | date, temperature, precipitation, heat flag | |

### Slowly changing dimensions

- Room attributes, employee jobs and rate plans keep their history, using Type 2 slowly changing dimensions. Last year's revenue can then be analysed against the room type and rate plan as they were then.
- Daily reservation snapshots are stored in full for pace analysis. A separate view keeps only the latest record per booking, for actuals.

## 5. Labels: Controlled Vocabularies

Free text is the main reason hotel data cannot be analysed. Each of the following is a fixed list maintained by a named owner:

| Label set | Example values | Owner |
| :-- | :-- | :-- |
| Market segment | Transient retail, transient discount, corporate, group corporate, group association, group tour, wholesale, contract | Revenue |
| Channel | Direct web, voice, OTA, GDS, wholesaler, walk-in | Revenue |
| Cancellation reason | Guest changed plans, duplicate, rebooked, no-show converted, weather or travel disruption | Front office |
| Demand tier | Compression, high, shoulder, need ([HARLTON-11](../Project%20HARLTON/11-year-round-occupancy-strategy/proposal.md)) | Revenue |
| Room status | Vacant dirty, vacant clean, inspected, occupied, out of order, out of service | Housekeeping |
| Supply reason | Par refill, special request, event, damaged, spilled, expired, returned, unaccounted | Housekeeping and stores |
| Work order category | HVAC, plumbing, electrical, elevator, furniture, Wi-Fi and TV, locks | Engineering |
| Review issue category | Cleanliness, noise, HVAC, plumbing, elevator, Wi-Fi, staff, value, food and beverage, pool and amenities | Guest experience |
| Incident type | Theft, disturbance, medical, trespass, vehicle, lost property, staff safety | Security |
| Shift role | Room attendant, inspector, houseperson, front desk agent, night auditor, security officer | Human resources |

Each label has a code, a definition and an example. Changes are versioned so that historical reports remain comparable.

## 6. Storage and Architecture

**Layers:**
1. **Raw:** source extracts landed unchanged, with load timestamps. Nothing is ever edited here.
2. **Clean:** typed, de-duplicated and validated tables with controlled labels applied.
3. **Mart:** the star schema above, plus summary tables for dashboards.

**Database:**
- A relational SQL database is sufficient for this scale, for example SQL Server or PostgreSQL. Hourly and 15-minute meter data is the only high-volume source.
- Transformations are written in SQL and Python, version-controlled and scheduled.
- Dashboards read only from the mart layer.

**Data quality checks, run on every load:**
- Row counts against source.
- No duplicate keys at the declared grain.
- Totals that must tie: room revenue in the mart against the PMS revenue report, and labour hours against payroll.
- Unknown label values.
- Late or missing feeds.

Failures stop the dashboard refresh and alert the data owner. Numbers on screen are therefore always numbers that tie back to source.

## 7. Privacy and Governance

Personal information is handled according to the ten fair information principles of Canada's federal private-sector privacy law. These cover accountability, identifying purposes, consent, limiting collection, limiting use and retention, accuracy, safeguards, openness, individual access and challenging compliance [6]. In practice:

- The analytics layer uses pseudonymous guest and employee keys. Names, contact details and payment data stay in source systems.
- Guest data is used for the purposes stated in the hotel's privacy notice. Retention periods are set per table.
- Employee-level data, such as punches, sign-outs and assignments, is reported by department or team. Individual reports go only to the employee's manager and human resources.
- Every table has a named business owner and a data dictionary entry.

## 8. References

1. Kimball Group, *Dimensional Modeling Techniques: Grain*. https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/grain/
2. Kimball Group, *Dimensional Modeling Techniques: Star Schemas and OLAP Cubes*. https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/star-schema-olap-cube/
3. Hospitality Financial and Technology Professionals, *Uniform System of Accounts for the Lodging Industry (USALI)*. https://usali.hftp.org/
4. American Hotel and Lodging Association, *AHLA to integrate HTNG* (2021). https://www.ahla.com/news/ahla-integrate-htng-strengthening-technology-expertise-advocacy-focus
5. OpenTravel Alliance, *2018A 2.0 Object Model Publication for Hospitality*. https://opentravel.org/news/opentravel-alliance-releases-2018a-2-0-object-model-publication-for-hospitality/
6. Office of the Privacy Commissioner of Canada, *PIPEDA requirements in brief*. https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/pipeda_brief/
7. Hospitality Technology, *2024 Lodging Technology Study*. https://hospitalitytech.com/2024-lodging-tech-study
8. Hospitality Net (HEDNA, NYU Tisch Center and RateGain), *State of Distribution 2025*. https://www.hospitalitynet.org/news/4127776.html
