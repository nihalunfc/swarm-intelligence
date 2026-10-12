# Project HARLTON

> **In short: a smarter way to make revenue decisions across several hotels, so that today's quick sale never costs the hotel its most valuable guests tomorrow.**

**Hospitality Asset & Revenue Learning, Tactical Optimization Network**

---

## 1. Executive Summary: The Evolution of Revenue Management

For decades, the hospitality industry has relied on standard Revenue Management Systems (RMS) that optimize for a single, critical metric: **RevPAR** (Revenue Per Available Room). These legacy systems heavily utilize historical booking curves and pick-up pace to forecast demand and adjust daily rates. While effective for short-term, single-night maximization, these linear regression models consistently fail to capture the multi-variable, interconnected realities of a modern mega-resort. 

In today’s market, maximizing tonight's rate is not enough. True profitability is found in optimizing **Customer Lifetime Value (CLV)**, managing complex OTA (Online Travel Agency) commission structures, preserving premium inventory, and ensuring that inter-departmental harmony exists between Sales, Revenue, and Operations. 

**Project HARLTON** is a conceptual architecture designed to move beyond simple forecasting. It is a practical, data-driven framework built to balance short-term daily revenue targets with long-term ecosystem profitability. By utilizing algorithmic matchmaking and multi-scenario displacement testing, HARLTON ensures that chasing a minor revenue bump today doesn't cost the hotel its most valuable, loyal relationships tomorrow.

> **Confidentiality & Technology Notice:** 
> At the core of the HARLTON architecture operates a proprietary "Swarm" data-routing mechanism that I have personally developed. This technique dynamically simulates thousands of booking variables, market shifts, and competing financial interests in real-time. To protect intellectual property, the exact mathematical framework and underlying code of this network mechanism are kept strictly confidential and will not be disclosed publicly in this repository.

---

## 2. The Core Problem: Where Legacy Systems Leak Revenue

Before exploring the HARLTON solutions, it is crucial to understand where large, multi-property hotel groups currently lose revenue despite using premium RMS software:

1.  **Arbitrary Upgrades Diluting Premium Inventory:** When a hotel oversells its base "Standard" category, the front desk is forced to upgrade guests to premium rooms (e.g., suites or high-floor views) for free. This locks out last-minute, high-paying premium demand.
2.  **Short-Sighted Group Quoting:** Standard algorithms often reject group business during high-demand periods because they calculate short-term displacement (turning away full-price transient guests). However, they fail to calculate the long-term value of a recurring group or the ancillary spend (F&B, casino, spa) that the group brings.
3.  **Cross-Departmental Friction:** Revenue Analysts look at raw math; Sales Managers look at relationships. When Revenue rejects a hard-won group block, it creates friction. Spreadsheets do not clearly explain *why* a decision was made.
4.  **Rate Loading & Pick-Up Anomalies:** Human error in rate loading (e.g., dropping a zero to sell a $199 room for $19) or sudden, unexpected spikes in overnight pick-up can cost thousands if not spotted by 9:00 AM the next morning.

---

## 3. Pillar I: Smart Asset & Guest Profiling (The Matchmaker)

Standard inventory systems treat all rooms within a category as identical commodities. A "Standard King" is a "Standard King." HARLTON looks significantly deeper, profiling the granular attributes of both the physical asset and the guest persona.

### The Mechanism
*   **Asset Vectors:** The system logs micro-attributes for every physical room. Does it face the sunset? Is it near the ice machine? Does it share a wall with the elevator? What is the square footage of the bathroom?
*   **Persona Vectors:** Guests are categorized far beyond their rate code. HARLTON evaluates loyalty tier status, historical return frequency, booking window, and demographic trends (e.g., corporate road warrior vs. first-time leisure tourist).

### Scenario: The Free Upgrade Dilemma
Imagine the hotel is oversold on base rooms and must upgrade one guest to a premium view room.
*   **Guest A** is a corporate regular who stays 40 nights a year. They arrive at 9 PM, sleep, and leave at 7 AM. 
*   **Guest B** is a first-time tourist staying for a 3-night anniversary weekend.

A standard system assigns the upgrade randomly based on check-in time. **HARLTON** algorithmically intervenes. It recognizes that Guest A values *convenience and quiet* over a premium view. It assigns Guest A a base room at the end of the hall (quiet) near the stairs (fast exit). It then offers the premium view upgrade to Guest B. 
*   **The Result:** The corporate guest gets the quiet night they value. The tourist gets a memorable view and is more likely to return. Both guests are better served at no extra cost to the hotel.

---

## 4. Pillar II: Advanced Group Quoting & Displacement Simulator

Quoting a 100-room group block on a busy weekend is one of the most high-stakes decisions a Revenue team makes. Accept it, and you might displace higher-paying transient guests. Reject it, and you might leave the hotel empty if the transient demand fails to materialize.

### The Mechanism
When Sales requests a quote for a group, HARLTON runs an instant, multi-layered simulation to calculate true net profitability (TrevPAR and GOPPAR), rather than just top-line room revenue.

### Variables Automatically Factored:
1.  **Gross Room Revenue:** The requested rate multiplied by the room block.
2.  **Commission Extraction:** Automatically deducting third-party planner commissions or OTA distribution costs.
3.  **Transient Displacement:** Simulating the exact number of full-price guests that will be turned away, factoring in Length of Stay (LOS) restrictions.
4.  **Wash Prediction:** Using historical data to predict how much of the block the group will *actually* pick up, allowing the hotel to safely overbook.
5.  **Future Recurring Value:** Calculating the statistical probability of this specific tour group returning annually. 

### The Output
Instead of a simple "Yes or No," the Revenue Analyst is presented with a dual-metric dashboard:
*   **Short-Term Impact:** "Accepting this group displaces $4,500 in transient revenue for this weekend."
*   **Ecosystem CLV:** "However, their historical 90% pick-up rate and 4-year return frequency yields a projected net ecosystem profit of $135,000."
*   *Decision:* The hotel secures the long-term relationship.

---

## 5. Pillar III: Automated Anomaly Detection & Parity Monitoring

A Revenue Analyst spends a significant portion of their morning pulling reports, checking rate parity across channels, and looking for errors. HARLTON acts as an autonomous auditor running 24/7.

### The Mechanism
*   **Rate Loading Validator:** HARLTON continuously scans the Property Management System (PMS) and Central Reservation System (CRS) for logical anomalies. If a weekend rate drops below a historical threshold, or a 2-night minimum restriction accidentally drops off a holiday weekend, the system instantly flags it before the rooms can be booked.
*   **Pick-Up Alerts:** If an unusual spike in bookings occurs at 3:00 AM (e.g., due to an airline cancellation or a sudden local event announcement), HARLTON detects the anomaly in the morning pick-up report and alerts the Revenue team to instantly raise rates and yield the remaining inventory.

---

## 6. Pillar IV: Data-to-Text Translator for Sales

Numbers only generate profit if the entire executive team is aligned on the strategy. Often, a Revenue Manager will reject a group quote that a Sales Manager spent weeks nurturing, leading to inter-departmental frustration.

### The Mechanism
HARLTON incorporates a communication bridging tool that takes complex displacement math and translates it into clear, strategic business justifications.

### Scenario: The Rejected Wedding Block
Sales requests a quote for a 40-room wedding block at a steep discount during a peak summer weekend. The HARLTON system runs the displacement math and rejects the quote. 

Instead of the Revenue Analyst having to manually explain the math, HARLTON generates a plain-English summary:
> *"Recommendation: DECLINE or COUNTER-OFFER at $249. We cannot accept this group at $150/night. Historical pacing indicates a 98% probability we will sell out these 40 rooms to transient guests at $289/night. Accepting this block would cost the property $5,560 in lost revenue. We recommend counter-offering with our shoulder-date availability."*

### The Result
The Sales team receives a logical, mathematically sound explanation that they can understand and even relay to the client. This builds trust in the Revenue department and ensures the hotel operates as a unified, profit-driven ecosystem.

---
*Developed as a portfolio conceptualization for practical hospitality data analytics and revenue management.*
