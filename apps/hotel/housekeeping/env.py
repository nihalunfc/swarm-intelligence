"""H2-03 + HARLTON-03: room attendants as a swarm that gets rooms ready in time.

One hotel day from 08:00 to 17:00 in 10-minute steps. Rooms come free as
guests check out (the time is only known when it happens). Each free room has
a "needed by" time from its next guest: the arrival time for guests who bought
an early check-in, else the later of arrival and the 15:00 standard check-in;
rooms with no arrival tonight are needed last.

Every attendant is an agent. When free, it sees the few dirty rooms that
matter most from where it stands (soonest needed, counting the elevator trip)
and picks one to clean, or waits. A room takes 30 minutes, plus 10 when the
attendant changes floor. Two attendants never clean the same room: a later
pick falls through to the next free candidate.

The team reward is minus the guest waiting time: every 10 minutes a guest has
arrived and their room is not ready costs 10 minutes, three times over for an
early check-in that was paid for.
"""

import numpy as np
from swarm.env import SwarmEnv

STEP_MIN = 10
DAY_START, DAY_END = 8 * 60, 17 * 60  # minutes after midnight
STANDARD_CHECKIN = 15 * 60
CLEAN_STEPS, FLOOR_STEPS = 3, 1
NO_ARRIVAL = 24 * 60


class HousekeepingSwarmEnv(SwarmEnv):
    def __init__(self, rooms=300, floors=10, attendants=8, departure_rate=0.35, arrival_rate=0.85,
                 early_share=0.15, early_weight=3.0, candidates=6, seed=0):
        self.R, self.F = int(rooms), int(floors)
        self.n_agents = int(attendants)
        self.departure_rate, self.arrival_rate = float(departure_rate), float(arrival_rate)
        self.early_share, self.early_weight = float(early_share), float(early_weight)
        self.K = int(candidates)
        self.n_actions = self.K + 1  # clean candidate k, or wait
        self.WAIT = self.K
        self.obs_dim = 6 + 5 * self.K
        self.n_steps = (DAY_END - DAY_START) // STEP_MIN
        self.rng = np.random.default_rng(seed)

    # --- scenario -----------------------------------------------------
    def _scenario(self):
        rng = self.rng
        n = rng.binomial(self.R, self.departure_rate)
        rooms = rng.choice(self.R, n, replace=False)
        self.floor = rooms // (self.R // self.F)
        self.floor = np.minimum(self.floor, self.F - 1)
        self.room_no = (self.floor + 1) * 100 + rooms % (self.R // self.F) + 1
        # Check-out: most guests leave between 9 and 11; a few early or late.
        self.checkout = np.clip(rng.normal(10 * 60, 55, n), 7 * 60, 12 * 60 + 30)
        has_arrival = rng.random(n) < self.arrival_rate
        early = has_arrival & (rng.random(n) < self.early_share)
        arrival = np.where(early, rng.uniform(9 * 60, 12 * 60 + 30, n),
                           np.clip(rng.normal(16 * 60, 100, n), 11 * 60, 23 * 60))
        self.early = early
        self.weight = np.where(early, self.early_weight, 1.0)
        self.arrival = np.where(has_arrival, arrival, NO_ARRIVAL)
        self.needed = np.where(early, arrival, np.where(has_arrival, np.maximum(arrival, STANDARD_CHECKIN), NO_ARRIVAL))
        self.ready_at = np.full(n, np.inf)
        self.claimed = np.zeros(n, dtype=bool)

    # --- SwarmEnv API -------------------------------------------------
    def reset(self, seed=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self._scenario()
        self.t = 0
        # Attendants start on evenly spread floors.
        self.at_floor = (np.arange(self.n_agents) * self.F // self.n_agents).astype(int)
        self.busy = np.zeros(self.n_agents, dtype=int)
        self.job = np.full(self.n_agents, -1)
        self.done_count = np.zeros(self.n_agents, dtype=int)
        self.floor_changes = 0
        self.wait_min = 0.0
        self._cands = self._candidates()
        return self._obs()

    @property
    def now(self) -> float:
        return DAY_START + self.t * STEP_MIN

    def _dirty_free(self):
        return (self.checkout <= self.now) & ~self.claimed & ~np.isfinite(self.ready_at)

    def _candidates(self):
        """Per attendant: the K free dirty rooms with the soonest needed-by time,
        counting the trip from the attendant's floor. -1 pads a short list."""
        free = np.nonzero(self._dirty_free())[0]
        out = np.full((self.n_agents, self.K), -1)
        if len(free) == 0:
            return out
        trip = (self.floor[free][None] != self.at_floor[:, None]) * FLOOR_STEPS * STEP_MIN
        score = self.needed[free][None] + trip + 0.01 * np.abs(self.floor[free][None] - self.at_floor[:, None])
        order = np.argsort(score, axis=1)[:, :self.K]
        out[:, :order.shape[1]] = free[order]
        return out

    def action_mask(self):
        m = np.zeros((self.n_agents, self.n_actions), dtype=bool)
        m[:, self.WAIT] = True
        idle = self.busy == 0
        m[idle, :self.K] = self._cands[idle] >= 0
        return m

    def step(self, actions):
        a = np.asarray(actions)
        # Rules that plan by room rather than by candidate (e.g. fixed floor order) set
        # ``env.override = {attendant: room}`` for this step.
        override, self.override = getattr(self, "override", {}), {}
        # 1. Free attendants pick rooms, in turn; a taken room falls through to the next candidate.
        for i in np.nonzero(self.busy == 0)[0]:
            if i in override:
                room = override[i]
                if self.claimed[room] or not self._dirty_free()[room]:
                    continue
            else:
                if a[i] == self.WAIT:
                    continue
                for k in range(int(a[i]), self.K):
                    room = self._cands[i, k]
                    if room >= 0 and not self.claimed[room]:
                        break
                else:
                    continue
                if room < 0 or self.claimed[room]:
                    continue
            self.claimed[room] = True
            moves = self.floor[room] != self.at_floor[i]
            self.floor_changes += int(moves)
            self.at_floor[i] = self.floor[room]
            self.busy[i] = CLEAN_STEPS + FLOOR_STEPS * moves
            self.job[i] = room
        # 2. Time passes; rooms finish.
        self.t += 1
        working = self.busy > 0
        self.busy[working] -= 1
        finished = working & (self.busy == 0)
        for i in np.nonzero(finished)[0]:
            self.ready_at[self.job[i]] = self.now
            self.done_count[i] += 1
            self.job[i] = -1
        # 3. Guests waiting for a room that is not ready.
        waiting = (self.needed <= self.now) & ~(self.ready_at <= self.now)
        wait = float((self.weight * waiting).sum()) * STEP_MIN
        self.wait_min += wait
        reward = -wait / 60.0 / max(1.0, self.n_agents)

        terminated = self.t >= self.n_steps
        if terminated:
            # Guests still arriving after 17:00 to rooms that never got cleaned wait until the
            # evening crew does them: charge one hour each so leaving rooms dirty never pays.
            left = ~np.isfinite(self.ready_at) & (self.needed < NO_ARRIVAL)
            late = float((self.weight * left).sum()) * 60.0
            self.wait_min += late
            reward -= late / 60.0 / max(1.0, self.n_agents)
        self._cands = self._candidates()
        return self._obs(), reward, terminated, False, {"waiting_guests": int(waiting.sum())}

    def episode_metrics(self):
        ready = np.isfinite(self.ready_at)
        early = self.early
        kept = (self.ready_at[early] <= self.arrival[early]).mean() if early.any() else 1.0
        return {
            "guest_wait_hours": self.wait_min / 60.0,
            "early_promises_kept_pct": float(100 * kept),
            "ready_by_noon_pct": float(100 * (self.ready_at <= 12 * 60).mean()),
            "rooms_cleaned": int(ready.sum()),
            "rooms": len(ready),
            "workload_spread": float(self.done_count.std()),
            "floor_changes": self.floor_changes,
        }

    # --- observations -------------------------------------------------
    def _obs(self):
        n = self.n_agents
        now = self.now
        free = self._dirty_free()
        out = np.zeros((n, self.obs_dim), dtype=np.float32)
        out[:, 0] = (now - DAY_START) / (DAY_END - DAY_START)
        out[:, 1] = self.at_floor / self.F
        out[:, 2] = self.busy / (CLEAN_STEPS + FLOOR_STEPS)
        out[:, 3] = self.done_count / max(1.0, self.done_count.mean() + 1)
        out[:, 4] = free.sum() / max(1, len(free)) * 10
        out[:, 5] = (self.checkout > now).mean()  # share of departures still to come
        c = self._cands
        valid = c >= 0
        safe = np.where(valid, c, 0)
        need = np.minimum(self.needed[safe], DAY_END + 120)
        feats = np.stack([
            valid.astype(float),
            np.where(valid, (need - now) / 240.0, 0.0),
            np.where(valid, self.early[safe], 0.0),
            np.where(valid, np.abs(self.floor[safe] - self.at_floor[:, None]) / self.F, 0.0),
            np.where(valid, self.needed[safe] < NO_ARRIVAL, 0.0),
        ], axis=2)  # (n, K, 5)
        out[:, 6:] = feats.reshape(n, -1)
        return out


def make_env(env_cfg: dict, split: str, seed: int) -> HousekeepingSwarmEnv:
    # Days are generated; evaluation uses unseen seeds.
    return HousekeepingSwarmEnv(seed=seed, **env_cfg)
