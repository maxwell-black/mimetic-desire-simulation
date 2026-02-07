"""
Girard 2×2 Convergence Module
============================

Implements the paper's core 2×2 design:

  Spread (conflictual mimesis):   linear   vs   attention/salience (convex redistributive)
  Source (acquisitive mimesis):   object rivalry   vs   status rivalry

Variants:
  LM = source: object, spread: linear
  AC = source: object, spread: attention
  RL = source: status, spread: linear
  RA = source: status, spread: attention

Design choices:
- Single simulation class with two flags (source, spread) for debuggability.
- Status-weighted prestige is recomputed each timestep before BOTH the desire step
  and the aggression-spread step (both consume prestige weights).
- Status is updated once per timestep AFTER expulsion (per Appendix C in the draft).

This file is intended as reproducible research code, not a general-purpose library.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, List, Literal, Optional, Tuple

import numpy as np
import networkx as nx


SourceMode = Literal["object", "status"]
SpreadMode = Literal["linear", "attention"]


# Canonical paper variant names (LM/AC/RL/RA) mapped to (source, spread)
VARIANT_MAP: dict[str, tuple[SourceMode, SpreadMode]] = {
    "LM": ("object", "linear"),
    "AC": ("object", "attention"),
    "RL": ("status", "linear"),
    "RA": ("status", "attention"),
}


@dataclass(frozen=True)
class GirardConfig:
    # --------------------
    # Network
    # --------------------
    n_agents: int = 50
    n_neighbors: int = 6
    rewire_prob: float = 0.15

    # --------------------
    # Objects / desire
    # --------------------
    n_objects: int = 8
    n_rivalrous: int = 5
    desire_init_max: float = 0.3
    desire_noise: float = 0.02

    # --------------------
    # Core dynamics
    # --------------------
    alpha: float = 0.15  # used in BOTH desire and aggression updates (paper's choice)
    rivalry_to_aggression: float = 0.2  # object rivalry increment coefficient
    aggression_decay: float = 0.03
    expulsion_threshold: Optional[float] = 8.0

    # --------------------
    # Attention/salience spread (AC/RA)
    # --------------------
    salience_exponent: float = 2.0  # gamma

    # --------------------
    # Status rivalry (RL/RA) parameters
    # --------------------
    rivalry_intensity: float = 0.15  # rho_riv
    sigma_status: float = 0.10       # sigma_S in f(ΔS)=exp(-ΔS/sigma_S)
    beta_up: float = 1.0             # beta_↑ in UpwardBias
    c_status: float = 0.50           # prestige baseline c_status in w ∝ w0(c_status+S_k)
    status_init_low: float = 0.4
    status_init_high: float = 0.6
    status_loss_rate: float = 0.005  # λ (max per-step status loss at current most-targeted agent)
    eps: float = 1e-12               # protects normalization in status update

    # --------------------
    # Simulation
    # --------------------
    n_steps: int = 600
    record_history: bool = True
    seed: int = 42


class GirardSimulation:
    """
    Core simulator for the Girard 2×2 design.

    Two knobs:
      source: 'object' | 'status'
      spread: 'linear' | 'attention'
    """

    def __init__(self, cfg: GirardConfig, source: SourceMode, spread: SpreadMode):
        if source not in ("object", "status"):
            raise ValueError(f"Invalid source mode: {source}")
        if spread not in ("linear", "attention"):
            raise ValueError(f"Invalid spread mode: {spread}")
        self.cfg = cfg
        self.source: SourceMode = source
        self.spread: SpreadMode = spread

        self.rng = np.random.default_rng(cfg.seed)
        self.step_num: int = 0

        # Build network
        self.graph = nx.watts_strogatz_graph(
            cfg.n_agents, cfg.n_neighbors, cfg.rewire_prob, seed=cfg.seed
        )

        # Distances (used only for d(i,k) in object-rivalry; for neighbors this is 1)
        self.distances = dict(nx.all_pairs_shortest_path_length(self.graph))

        # Baseline prestige weights w0_ik on directed edges
        self.prestige_base: Dict[Tuple[int, int], float] = {}
        for i, j in self.graph.edges():
            self.prestige_base[(i, j)] = float(self.rng.uniform(0.1, 1.0))
            self.prestige_base[(j, i)] = float(self.rng.uniform(0.1, 1.0))

        # Dynamic prestige weights w_ik(t) (equal to base for object-source variants)
        self.prestige: Dict[Tuple[int, int], float] = dict(self.prestige_base)

        # Agents
        self.alive: Dict[int, bool] = {i: True for i in self.graph.nodes()}
        self.desires: Dict[int, np.ndarray] = {
            i: self.rng.uniform(0.0, cfg.desire_init_max, size=cfg.n_objects).astype(float)
            for i in self.graph.nodes()
        }
        self.aggression: Dict[int, np.ndarray] = {
            i: np.zeros(cfg.n_agents, dtype=float) for i in self.graph.nodes()
        }

        # Status scalars (only for status-source variants)
        self.status: Optional[Dict[int, float]] = None
        if self.source == "status":
            self.status = {
                i: float(self.rng.uniform(cfg.status_init_low, cfg.status_init_high))
                for i in self.graph.nodes()
            }

        # History
        # If cfg.record_history is False, we still record expulsion events (needed for cycle stats),
        # but we skip per-step metric time series for speed.
        self.record_history: bool = bool(cfg.record_history)

        self.history: Dict[str, list] = {
            "expulsion_events": [],      # (step, victim_id, received_aggression)
            "catharsis_events": [],      # (step, victim_id, fractional_drop)
            # Per-step time series (populated only when record_history=True)
            "system_tension": [],        # sum received aggression (alive targets)
            "n_active_agents": [],       # number alive
            "aggression_gini": [],       # Gini of received aggression
            "aggression_max_share": [],  # max(received)/sum(received)
            "convergence_ratio": [],     # top1/top2 (received)
            "aggression_entropy": [],    # Shannon entropy of received distribution
            "top_target_aggression": [], # max(received)
            "mean_aggression": [],       # mean(received)
            "modal_agreement": [],       # fraction of agents whose top target is the modal target
            "eligible_agents": [],       # count of agents eligible for modal_agreement
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _alive_ids(self) -> List[int]:
        return [i for i in self.graph.nodes() if self.alive.get(i, False)]

    def _alive_neighbors(self, i: int) -> List[int]:
        return [n for n in self.graph.neighbors(i) if self.alive.get(n, False)]

    def _social_distance(self, i: int, j: int) -> float:
        # In current experiments, rivalry updates occur only on edges, so d(i,j)=1.
        if j in self.distances.get(i, {}):
            return max(1.0, float(self.distances[i][j]))
        return float("inf")

    def _refresh_prestige(self) -> None:
        """
        Recompute prestige weights w_ik(t).

        For object-source variants: w_ik(t) = w0_ik (static).
        For status-source variants: w_ik(t) ∝ w0_ik * (c_status + S_k(t)).

        Called before BOTH desire and spread in each timestep.
        """
        if self.source != "status":
            # Static prestige weights already set.
            return
        assert self.status is not None
        cfg = self.cfg
        # Recompute directed weights on existing directed edges
        for (i, k), w0 in self.prestige_base.items():
            self.prestige[(i, k)] = w0 * (cfg.c_status + self.status[k])

    def _prestige_weight(self, subject: int, model: int) -> float:
        return self.prestige.get((subject, model), 0.0)

    def _received_aggression_by_alive(self) -> Dict[int, float]:
        alive = self._alive_ids()
        received: Dict[int, float] = {}
        for v in alive:
            total = 0.0
            for other in alive:
                if other != v:
                    total += float(self.aggression[other][v])
            received[v] = total
        return received

    def _received_aggression_vector(self) -> Tuple[List[int], np.ndarray]:
        """Return (alive_ids, received_aggression_vector aligned to alive_ids)."""
        alive = self._alive_ids()
        received = np.zeros(len(alive), dtype=float)
        for idx, v in enumerate(alive):
            total = 0.0
            for other in alive:
                if other != v:
                    total += float(self.aggression[other][v])
            received[idx] = total
        return alive, received

    @staticmethod
    def _gini(values: np.ndarray) -> float:
        """Gini coefficient over nonnegative values."""
        if values.size == 0:
            return 0.0
        s = float(np.sum(values))
        if s <= 0.0:
            return 0.0
        sorted_v = np.sort(values)
        n = sorted_v.size
        index = np.arange(1, n + 1, dtype=float)
        return float((2.0 * np.sum(index * sorted_v) - (n + 1.0) * np.sum(sorted_v)) / (n * s))

    @staticmethod
    def _entropy(values: np.ndarray) -> float:
        """Shannon entropy (base 2) of a nonnegative vector."""
        s = float(np.sum(values))
        if s <= 0.0:
            return 0.0
        p = values / s
        p = p[p > 0.0]
        return -float(np.sum(p * np.log2(p)))

    def record_metrics(self) -> None:
        """Append per-step metrics to history (called when record_history=True)."""
        alive, received = self._received_aggression_vector()
        total_agg = float(np.sum(received))

        self.history["system_tension"].append(total_agg)
        self.history["n_active_agents"].append(len(alive))
        self.history["aggression_gini"].append(self._gini(received))
        self.history["aggression_entropy"].append(self._entropy(received))
        self.history["mean_aggression"].append(float(np.mean(received)) if received.size > 0 else 0.0)
        self.history["top_target_aggression"].append(float(np.max(received)) if received.size > 0 else 0.0)

        if total_agg > 0.0 and received.size > 0:
            self.history["aggression_max_share"].append(float(np.max(received) / total_agg))
        else:
            self.history["aggression_max_share"].append(0.0)

        if received.size >= 2:
            sorted_r = np.sort(received)[::-1]
            if sorted_r[1] > 0.0:
                self.history["convergence_ratio"].append(float(sorted_r[0] / sorted_r[1]))
            else:
                self.history["convergence_ratio"].append(float(sorted_r[0]) if sorted_r[0] > 0.0 else 0.0)
        else:
            self.history["convergence_ratio"].append(0.0)

        # Modal-target agreement: fraction of (eligible) agents whose top target equals the modal target.
        eligible = 0
        top_targets: List[int] = []
        thresh = 1e-8
        for i in alive:
            targets = [j for j in alive if j != i]
            if not targets:
                continue
            vec = self.aggression[i][targets]
            if float(np.sum(vec)) < thresh:
                continue
            eligible += 1
            top_j = targets[int(np.argmax(vec))]
            top_targets.append(top_j)

        self.history["eligible_agents"].append(eligible)
        if eligible == 0:
            self.history["modal_agreement"].append(0.0)
        else:
            counts: Dict[int, int] = {}
            for j in top_targets:
                counts[j] = counts.get(j, 0) + 1
            modal_target = max(counts, key=counts.get)
            self.history["modal_agreement"].append(float(counts[modal_target] / eligible))

    # ------------------------------------------------------------------
    # Steps
    # ------------------------------------------------------------------
    def step_desire(self) -> None:
        cfg = self.cfg
        new_desires: Dict[int, np.ndarray] = {}
        for i in self._alive_ids():
            neighbors = self._alive_neighbors(i)
            if not neighbors:
                new_desires[i] = self.desires[i].copy()
                continue

            mimetic_pull = np.zeros(cfg.n_objects, dtype=float)
            total_w = 0.0
            for k in neighbors:
                w = self._prestige_weight(i, k)
                mimetic_pull += w * self.desires[k]
                total_w += w
            if total_w > 0:
                mimetic_pull /= total_w

            new_d = cfg.alpha * self.desires[i] + (1.0 - cfg.alpha) * mimetic_pull
            noise = self.rng.normal(0.0, cfg.desire_noise, size=cfg.n_objects)
            new_desires[i] = np.clip(new_d + noise, 0.0, None)

        for i, d in new_desires.items():
            self.desires[i] = d

    def step_aggression_source(self) -> None:
        cfg = self.cfg
        mimetic_factor = 1.0 - cfg.alpha

        if self.source == "object":
            for i in self._alive_ids():
                for k in self._alive_neighbors(i):
                    # Shared desire over rivalrous objects
                    shared = 0.0
                    di = self.desires[i]
                    dk = self.desires[k]
                    for o in range(cfg.n_rivalrous):
                        shared += float(min(di[o], dk[o]))

                    dist = self._social_distance(i, k)  # =1 for neighbors
                    inc = cfg.rivalry_to_aggression * mimetic_factor * shared / dist
                    self.aggression[i][k] += inc

        elif self.source == "status":
            assert self.status is not None
            for i in self._alive_ids():
                Si = self.status[i]
                for k in self._alive_neighbors(i):
                    Sk = self.status[k]
                    delta = abs(Si - Sk)
                    f = float(np.exp(-delta / cfg.sigma_status))
                    upward = 1.0 + cfg.beta_up * max(0.0, Sk - Si)
                    inc = cfg.rivalry_intensity * mimetic_factor * upward * f
                    self.aggression[i][k] += inc

        else:
            raise RuntimeError("Unreachable source mode")

    def step_aggression_spread(self) -> None:
        cfg = self.cfg
        alive = self._alive_ids()
        new_agg: Dict[int, np.ndarray] = {}

        for i in alive:
            neighbors = self._alive_neighbors(i)
            if not neighbors:
                new_agg[i] = self.aggression[i].copy()
                continue

            # Prestige-weighted mean neighbor aggression vector
            neighbor_hostility = np.zeros(cfg.n_agents, dtype=float)
            total_w = 0.0
            for k in neighbors:
                w = self._prestige_weight(i, k)
                neighbor_hostility += w * self.aggression[k]
                total_w += w
            if total_w > 0:
                neighbor_hostility /= total_w

            # Exclude self and dead targets
            neighbor_hostility[i] = 0.0
            for dead in range(cfg.n_agents):
                if not self.alive.get(dead, False):
                    neighbor_hostility[dead] = 0.0

            if self.spread == "linear":
                mimetic_pull = neighbor_hostility
                result = cfg.alpha * self.aggression[i] + (1.0 - cfg.alpha) * mimetic_pull

            elif self.spread == "attention":
                total_h = float(np.sum(neighbor_hostility))
                if total_h > 0.0:
                    sharpened = neighbor_hostility ** cfg.salience_exponent
                    total_sharp = float(np.sum(sharpened))
                    if total_sharp > 0.0:
                        weights = sharpened / total_sharp
                    else:
                        weights = np.zeros(cfg.n_agents, dtype=float)
                    mimetic_pull = weights * total_h  # throughput conserved at total_h
                    result = cfg.alpha * self.aggression[i] + (1.0 - cfg.alpha) * mimetic_pull
                else:
                    # no perceived hostility: only autonomy term remains
                    result = cfg.alpha * self.aggression[i]

            else:
                raise RuntimeError("Unreachable spread mode")

            # Enforce constraints
            result[i] = 0.0
            for dead in range(cfg.n_agents):
                if not self.alive.get(dead, False):
                    result[dead] = 0.0
            new_agg[i] = result

        for i, agg in new_agg.items():
            self.aggression[i] = agg

    def step_decay(self) -> None:
        cfg = self.cfg
        factor = 1.0 - cfg.aggression_decay
        for i in self._alive_ids():
            self.aggression[i] *= factor

    def step_expulsion(self) -> None:
        cfg = self.cfg
        if cfg.expulsion_threshold is None:
            return

        received = self._received_aggression_by_alive()
        if not received:
            return

        most_targeted = max(received, key=received.get)
        if received[most_targeted] >= cfg.expulsion_threshold:
            # Catharsis is the fractional drop in total received aggression
            # caused by expulsion (computed on the post-decay state within this timestep).
            pre_tension = float(sum(received.values()))

            self.alive[most_targeted] = False
            self.history["expulsion_events"].append(
                (self.step_num, most_targeted, float(received[most_targeted]))
            )

            # Zero hostility toward expelled agent (column), for all remaining alive agents.
            for other in self._alive_ids():
                self.aggression[other][most_targeted] = 0.0
            # Zero the expelled agent's own aggression row.
            self.aggression[most_targeted] *= 0.0

            if pre_tension > 0.0:
                post_received = self._received_aggression_by_alive()
                post_tension = float(sum(post_received.values())) if post_received else 0.0
                drop = max(0.0, (pre_tension - post_tension) / pre_tension)
            else:
                drop = 0.0
            self.history["catharsis_events"].append((self.step_num, most_targeted, float(drop)))

    def step_status_update(self) -> None:
        """
        RL/RA only: status update AFTER expulsion (Appendix C in paper_draft_8).
        """
        if self.source != "status":
            return
        assert self.status is not None
        cfg = self.cfg
        received = self._received_aggression_by_alive()
        if not received:
            return
        r_max = max(received.values())
        denom = max(r_max, cfg.eps)
        for k, r in received.items():
            new_s = self.status[k] - cfg.status_loss_rate * (float(r) / denom)
            self.status[k] = float(min(1.0, max(0.0, new_s)))

    # ------------------------------------------------------------------
    # Run loop
    # ------------------------------------------------------------------
    def step(self) -> None:
        # Prestige weights depend on status and are used in desire + spread.
        self._refresh_prestige()
        self.step_desire()

        self.step_aggression_source()

        # Recompute prestige again before spread (explicitly, for clarity/debuggability).
        self._refresh_prestige()
        self.step_aggression_spread()

        self.step_decay()
        self.step_expulsion()

        # Status update is defined after expulsion (paper spec).
        self.step_status_update()


        if self.record_history:
            self.record_metrics()

        self.step_num += 1

    def run(self, n_steps: Optional[int] = None) -> None:
        steps = self.cfg.n_steps if n_steps is None else int(n_steps)
        for _ in range(steps):
            self.step()



def make_variant(cfg: GirardConfig, variant: str) -> GirardSimulation:
    """
    Factory: create a simulation from the paper's canonical variant name.

    variant ∈ {'LM','AC','RL','RA'}.
    """
    if variant not in VARIANT_MAP:
        raise ValueError(f"Unknown variant '{variant}'. Expected one of {sorted(VARIANT_MAP)}.")
    source, spread = VARIANT_MAP[variant]
    return GirardSimulation(cfg, source=source, spread=spread)


def run_many(
    cfg: GirardConfig,
    source: SourceMode,
    spread: SpreadMode,
    n_runs: int = 10,
    seed0: Optional[int] = None,
) -> List[GirardSimulation]:
    """
    Convenience helper: run n_runs simulations with different seeds.

    Returns the list of simulation objects (with history + final state).
    """
    sims: List[GirardSimulation] = []
    base_seed = cfg.seed if seed0 is None else int(seed0)
    for r in range(n_runs):
        sim_cfg = replace(cfg, seed=base_seed + r * 1000)
        sim = GirardSimulation(sim_cfg, source=source, spread=spread)
        sim.run()
        sims.append(sim)
    return sims
