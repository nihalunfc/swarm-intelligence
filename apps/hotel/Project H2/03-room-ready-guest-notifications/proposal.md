# H2-03: Room-Ready Notifications and Housekeeping Sequencing

> **In short: clean rooms in the order guests actually need them, and text each guest the moment their room is ready.**

**Category:** Guest flow and housekeeping operations
**Optimizes:** Time from guest arrival to room access, and the number of "is my room ready?" contacts
**Status:** Proposal

---

## 1. What It Is

Two connected pieces.

**Housekeeping sequencing.** Each morning, the order in which rooms are cleaned is set by when they are needed, not by floor number. The ordering uses:
- which guests have already left (see [H2-02](../02-departure-flow-balancing/proposal.md));
- which arriving guests are expected early;
- which arriving guests have bought early check-in (see [HARLTON-03](../../Project%20HARLTON/03-early-arrival-late-departure-revenue/proposal.md)).

Each room attendant's queue is an agent, and the coordination engine balances workload across attendants while respecting floor assignments and travel time.

**Room-ready message.** When a room is marked clean and inspected, the waiting guest receives a text or app message with their room number. Guests who arrive early can leave their bags and enjoy the property instead of waiting in the lobby or calling the desk.

## 2. Why It Matters

**Waiting for rooms is common.**
- In a 2016 guest survey, 66% said they "always" or often have to wait for their room to be ready (vendor survey, small sample) [1].
- A 2026 industry research report found that room readiness delays can affect annual revenue by 8-15%, and that one in three hotel operators cite housekeeping as an operational challenge (vendor research) [2].

**Housekeeping capacity is fixed, so order matters.** A room attendant typically cleans about 16 rooms per shift at 15 to 30 minutes each [3]. With fixed capacity, the only lever is which rooms are cleaned first. Cleaning in floor order can leave an early-arriving family waiting while rooms that are not needed until evening are finished.

**Guests want to be told, not to ask.**
- 77% of travellers are interested in using automated messaging for service requests at hotels [4].
- A proactive room-ready message removes a front desk interaction at the busiest time of day.

## 3. How It Will Be Solved

**Step 1: Need-time per room.**
- For each room due to be cleaned, set a "needed by" time from the next guest's expected arrival.
- Early check-in purchases take the highest priority.
- Unsold rooms are needed last.

**Step 2: Sequencing.**
- The coordination engine produces each attendant's room order.
- It minimizes total guest waiting time weighted by priority, while keeping attendants within their floors and evening out workload.

**Step 3: Live updates.** As actual departures come in, the queue re-sorts. Supervisors see the plan and can override it.

**Step 4: Notification.** The inspected status triggers the guest message through the existing messaging channel.

**Step 5: Measurement.** Minutes from arrival to room access, early-arrival waits, "room ready?" calls to the desk, and the share of early check-in promises kept.

**Deliverables:**
- A morning cleaning sequence per attendant.
- A live room-readiness board.
- An automated guest message.
- A weekly readiness report.

## 4. Data Required

- Departures and arrivals with expected times, room status timestamps (dirty, clean, inspected), attendant assignments and a guest messaging channel.

## 5. Risks and Assumptions

- The tool must fit the existing housekeeping app and how supervisors work today. It suggests an order; it does not replace supervisor judgement.
- Two of the figures below come from vendor surveys and are used only as indicators. The pilot will measure the property's own waiting times.

## 6. References

1. Hotel Online (hospitalityPulse, vendor survey, 2016), *Survey reveals serious flaws in hotel check-in*. https://www.hotel-online.com/news/survey-reveals-serious-flaws-in-hotel-check-in/
2. Lodging Magazine (Access Hospitality research, vendor), *Room readiness delays could cost hotels up to 15 percent of annual revenue* (Aug 2026). https://lodgingmagazine.com/access-hospitality-research-room-readiness-delays-could-cost-hotels-up-to-15-percent-of-annual-revenue/
3. Canadian Centre for Occupational Health and Safety, *Hotel Housekeeping*. https://www.ccohs.ca/oshanswers/occup_workplace/hotel_housekeeping.html
4. Hotel Business (Oracle Hospitality survey, 2022), *73% of travelers want hotels with self-service tech*. https://hotelbusiness.com/73-of-travelers-want-hotels-with-self-service-tech/
