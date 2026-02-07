"""
Scapegoat Convergence Mechanisms
=================================
Three variants testing what additional structure (beyond linear mimesis)
is necessary and sufficient to produce Girardian scapegoat convergence.

All three share the v2 base: mimetic desire, rivalry-sourced aggression,
mimetic aggression spread. They differ ONLY in the aggression transmission
step.

Variant 1: THRESHOLD CONTAGION (Granovetter/Watts)
  - Agent ignores low-level neighbor aggression toward target j
  - Once fraction of neighbors blaming j exceeds personal threshold,
    agent piles on maximally
  - Discontinuous: mob-or-nothing

Variant 2: ATTENTION/SALIENCE
  - Agents have finite attention; they attend to the target their
    neighbors are MOST hostile toward
  - Aggression concentrates on whoever is most "talked about"
  - Winner-take-all attentional dynamics

Variant 3: SIGNS OF THE VICTIM
  - Some agents are structurally marginal (fewer connections, lower prestige)
  - Aggression flows toward the marginal by default
  - Tests whether social structure alone produces convergence

Variant 0: LINEAR BASELINE (from v2, for comparison)
  - Pure linear mimetic averaging
  - Already shown to NOT produce convergence
"""

import numpy as np
import networkx as nx
from dataclasses import dataclass
from typing import Optional


@dataclass
class VariantConfig:
    # Network
    n_agents: int = 50
    n_neighbors: int = 6
    rewire_prob: float = 0.15

    # Objects
    n_objects: int = 8
    n_rivalrous: int = 5

    # Core
    alpha: float = 0.15
    rivalry_to_aggression: float = 0.2
    aggression_decay: float = 0.03
    desire_noise: float = 0.02
    expulsion_threshold: float = 8.0

    # Variant 1: Threshold
    threshold_fraction: float = 0.3   # fraction of neighbors that must blame j
    threshold_boost: float = 0.8      # aggression added when threshold crossed

    # Variant 2: Attention
    attention_slots: int = 3          # how many targets an agent can attend to
    salience_exponent: float = 2.0    # sharpness of attention concentration

    # Variant 3: Signs of the victim
    n_marginal: int = 5               # number of structurally marginal agents
    marginal_prestige_factor: float = 0.3  # their prestige multiplier
    marginal_connection_factor: float = 0.4  # fraction of edges kept

    # Simulation
    n_steps: int = 500
    seed: int = 42


class BaseSimulation:
    """Shared infrastructure for all variants."""

    def __init__(self, config: VariantConfig, variant: str):
        self.cfg = config
        self.variant = variant
        self.rng = np.random.default_rng(config.seed)
        self.step_num = 0

        # Build network (variant 3 modifies this after)
        self.graph = nx.watts_strogatz_graph(
            config.n_agents, config.n_neighbors, config.rewire_prob,
            seed=config.seed
        )

        # Prestige
        self.prestige: dict[tuple[int, int], float] = {}
        for i, j in self.graph.edges():
            self.prestige[(i, j)] = self.rng.uniform(0.1, 1.0)
            self.prestige[(j, i)] = self.rng.uniform(0.1, 1.0)

        # Mark marginal agents for variant 3
        self.marginal_agents: set[int] = set()
        if variant == 'signs_of_victim':
            self._create_marginal_agents()

        # Distances
        self.distances = dict(nx.all_pairs_shortest_path_length(self.graph))

        # Agents
        self.desires = {}
        self.aggression = {}
        self.alive = {}
        for node in self.graph.nodes():
            self.desires[node] = self.rng.uniform(0.0, 0.3, size=config.n_objects)
            self.aggression[node] = np.zeros(config.n_agents)
            self.alive[node] = True

        # Variant 1: individual thresholds (heterogeneous)
        if variant == 'threshold':
            self.thresholds = {}
            for node in self.graph.nodes():
                self.thresholds[node] = self.rng.uniform(
                    config.threshold_fraction * 0.5,
                    config.threshold_fraction * 1.5
                )

        # History
        self.history = {
            'system_tension': [],
            'mean_desire': [],
            'desire_concentration': [],
            'n_active_agents': [],
            'expulsion_events': [],
            'aggression_gini': [],
            'aggression_max_share': [],
            'aggression_entropy': [],
            'aggression_top3_share': [],
            'mean_aggression': [],
            'top_target_aggression': [],
            'convergence_ratio': [],   # top1 / top2 received aggression
        }

    def _create_marginal_agents(self):
        """Variant 3: Create structurally marginal agents."""
        cfg = self.cfg
        # Pick agents with highest betweenness centrality to be NON-marginal
        # Pick lowest-centrality agents to be marginal
        centrality = nx.betweenness_centrality(self.graph)
        sorted_by_centrality = sorted(centrality.keys(), key=lambda n: centrality[n])
        self.marginal_agents = set(sorted_by_centrality[:cfg.n_marginal])

        # Reduce their connections
        for m in self.marginal_agents:
            neighbors = list(self.graph.neighbors(m))
            n_to_remove = int(len(neighbors) * (1 - cfg.marginal_connection_factor))
            to_remove = self.rng.choice(neighbors, size=min(n_to_remove, len(neighbors) - 1),
                                         replace=False)
            for n in to_remove:
                self.graph.remove_edge(m, n)

        # Reduce their prestige
        for i, j in list(self.prestige.keys()):
            if j in self.marginal_agents:
                # Others have low prestige toward marginal agents
                self.prestige[(i, j)] *= cfg.marginal_prestige_factor

    def _alive_ids(self) -> list[int]:
        return [i for i in self.graph.nodes() if self.alive.get(i, False)]

    def _alive_neighbors(self, i: int) -> list[int]:
        return [n for n in self.graph.neighbors(i) if self.alive.get(n, False)]

    def _prestige_weight(self, subject: int, model: int) -> float:
        return self.prestige.get((subject, model), 0.0)

    def _social_distance(self, i: int, j: int) -> float:
        if j in self.distances.get(i, {}):
            return max(1.0, float(self.distances[i][j]))
        return float('inf')

    # ------------------------------------------------------------------
    # Shared steps
    # ------------------------------------------------------------------
    def step_desire(self):
        cfg = self.cfg
        new_desires = {}
        for i in self._alive_ids():
            neighbors = self._alive_neighbors(i)
            if not neighbors:
                new_desires[i] = self.desires[i].copy()
                continue
            mimetic_pull = np.zeros(cfg.n_objects)
            total_w = 0.0
            for j in neighbors:
                w = self._prestige_weight(i, j)
                mimetic_pull += w * self.desires[j]
                total_w += w
            if total_w > 0:
                mimetic_pull /= total_w
            new_d = cfg.alpha * self.desires[i] + (1 - cfg.alpha) * mimetic_pull
            noise = self.rng.normal(0, cfg.desire_noise, size=cfg.n_objects)
            new_desires[i] = np.clip(new_d + noise, 0.0, None)
        for i, d in new_desires.items():
            self.desires[i] = d

    def step_rivalry_aggression(self):
        cfg = self.cfg
        mimetic_factor = 1.0 - cfg.alpha
        for i in self._alive_ids():
            for j in self._alive_neighbors(i):
                shared = 0.0
                for o in range(cfg.n_rivalrous):
                    shared += min(self.desires[i][o], self.desires[j][o])
                dist = self._social_distance(i, j)
                increment = cfg.rivalry_to_aggression * mimetic_factor * shared / dist
                self.aggression[i][j] += increment

    def step_aggression_spread(self):
        """Override in each variant."""
        raise NotImplementedError

    def step_decay(self):
        for i in self._alive_ids():
            self.aggression[i] *= (1 - self.cfg.aggression_decay)

    def step_expulsion(self):
        cfg = self.cfg
        alive = self._alive_ids()
        received = {}
        for v in alive:
            total = 0.0
            for other in alive:
                if other != v:
                    total += self.aggression[other][v]
            received[v] = total

        if not received:
            return

        most_targeted = max(received, key=received.get)
        if received[most_targeted] >= cfg.expulsion_threshold:
            self.alive[most_targeted] = False
            self.history['expulsion_events'].append(
                (self.step_num, most_targeted, received[most_targeted])
            )
            for i in alive:
                self.aggression[i][most_targeted] = 0.0

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------
    def _received_aggression(self) -> np.ndarray:
        alive = self._alive_ids()
        received = np.zeros(len(alive))
        for idx, v in enumerate(alive):
            for other in alive:
                if other != v:
                    received[idx] += self.aggression[other][v]
        return received

    def _gini(self, values: np.ndarray) -> float:
        if len(values) == 0 or np.sum(values) == 0:
            return 0.0
        sorted_v = np.sort(values)
        n = len(sorted_v)
        index = np.arange(1, n + 1)
        return float((2 * np.sum(index * sorted_v) - (n + 1) * np.sum(sorted_v)) /
                      (n * np.sum(sorted_v)))

    def _entropy(self, values: np.ndarray) -> float:
        s = np.sum(values)
        if s == 0:
            return 0.0
        p = values / s
        p = p[p > 0]
        return -float(np.sum(p * np.log2(p)))

    def _herfindahl(self) -> float:
        total = np.zeros(self.cfg.n_objects)
        for i in self._alive_ids():
            total += self.desires[i]
        s = total.sum()
        if s == 0:
            return 0.0
        shares = total / s
        return float(np.sum(shares ** 2))

    def record_history(self):
        alive = self._alive_ids()
        received = self._received_aggression()
        total_agg = float(np.sum(received))

        self.history['system_tension'].append(total_agg)
        self.history['mean_desire'].append(
            float(np.mean([self.desires[i].mean() for i in alive])) if alive else 0.0
        )
        self.history['desire_concentration'].append(self._herfindahl())
        self.history['n_active_agents'].append(len(alive))
        self.history['aggression_gini'].append(self._gini(received))
        self.history['aggression_entropy'].append(self._entropy(received))
        self.history['mean_aggression'].append(float(np.mean(received)) if len(received) > 0 else 0.0)

        if total_agg > 0:
            self.history['aggression_max_share'].append(float(np.max(received) / total_agg))
        else:
            self.history['aggression_max_share'].append(0.0)

        if len(received) >= 2:
            sorted_r = np.sort(received)[::-1]
            self.history['aggression_top3_share'].append(
                float(np.sum(sorted_r[:3]) / total_agg) if total_agg > 0 else 0.0
            )
            if sorted_r[1] > 0:
                self.history['convergence_ratio'].append(float(sorted_r[0] / sorted_r[1]))
            else:
                self.history['convergence_ratio'].append(float(sorted_r[0]) if sorted_r[0] > 0 else 0.0)
        else:
            self.history['aggression_top3_share'].append(0.0)
            self.history['convergence_ratio'].append(0.0)

        self.history['top_target_aggression'].append(
            float(np.max(received)) if len(received) > 0 else 0.0
        )

    def run(self) -> dict:
        for t in range(self.cfg.n_steps):
            self.step_num = t
            self.step_desire()
            self.step_rivalry_aggression()
            self.step_aggression_spread()
            self.step_decay()
            self.step_expulsion()
            self.record_history()
        return self.history


# =====================================================================
# VARIANT 0: LINEAR BASELINE
# =====================================================================

class LinearBaseline(BaseSimulation):
    """Pure linear mimetic averaging. Already shown to not converge."""

    def __init__(self, config: VariantConfig):
        super().__init__(config, 'linear')

    def step_aggression_spread(self):
        cfg = self.cfg
        alive = self._alive_ids()
        new_agg = {}

        for i in alive:
            neighbors = self._alive_neighbors(i)
            if not neighbors:
                new_agg[i] = self.aggression[i].copy()
                continue

            mimetic_pull = np.zeros(cfg.n_agents)
            total_w = 0.0
            for j in neighbors:
                w = self._prestige_weight(i, j)
                mimetic_pull += w * self.aggression[j]
                total_w += w
            if total_w > 0:
                mimetic_pull /= total_w

            result = cfg.alpha * self.aggression[i] + (1 - cfg.alpha) * mimetic_pull
            result[i] = 0.0
            for dead in range(cfg.n_agents):
                if not self.alive.get(dead, False):
                    result[dead] = 0.0
            new_agg[i] = result

        for i, agg in new_agg.items():
            self.aggression[i] = agg


# =====================================================================
# VARIANT 1: THRESHOLD CONTAGION
# =====================================================================

class ThresholdContagion(BaseSimulation):
    """
    Granovetter/Watts threshold model applied to accusation.
    
    Agent i tracks neighbor aggression toward each target v.
    If the FRACTION of i's neighbors who are actively hostile to v
    exceeds i's personal threshold, i piles on with a large boost.
    Below threshold, i maintains only rivalry-sourced aggression.
    
    "Actively hostile" = aggression[j][v] > median aggression level.
    
    This produces discontinuous, mob-like convergence.
    """

    def __init__(self, config: VariantConfig):
        super().__init__(config, 'threshold')

    def step_aggression_spread(self):
        cfg = self.cfg
        alive = self._alive_ids()
        new_agg = {}

        for i in alive:
            neighbors = self._alive_neighbors(i)
            if not neighbors:
                new_agg[i] = self.aggression[i].copy()
                continue

            result = self.aggression[i].copy()
            n_neighbors = len(neighbors)

            for v in alive:
                if v == i:
                    continue

                # Count how many neighbors are actively hostile toward v
                # "Active" = above-median aggression from that neighbor
                neighbor_agg_toward_v = []
                for j in neighbors:
                    neighbor_agg_toward_v.append(self.aggression[j][v])

                if not neighbor_agg_toward_v:
                    continue

                median_agg = np.median(neighbor_agg_toward_v)
                n_hostile = sum(1 for a in neighbor_agg_toward_v if a > median_agg + 0.01)
                fraction_hostile = n_hostile / n_neighbors

                if fraction_hostile >= self.thresholds[i]:
                    # Threshold crossed: pile on
                    # Boost proportional to neighbor consensus
                    boost = cfg.threshold_boost * fraction_hostile
                    result[v] += boost
                else:
                    # Below threshold: slight decay of mimetic aggression
                    # (retain only rivalry-sourced component)
                    result[v] *= 0.95

            result[i] = 0.0
            for dead in range(cfg.n_agents):
                if not self.alive.get(dead, False):
                    result[dead] = 0.0
            new_agg[i] = result

        for i, agg in new_agg.items():
            self.aggression[i] = agg


# =====================================================================
# VARIANT 2: ATTENTION / SALIENCE
# =====================================================================

class AttentionSalience(BaseSimulation):
    """
    Agents have finite attention. They concentrate their mimetic
    aggression-absorption on the TOP K targets their neighbors are
    most hostile toward. Other targets get attenuated.
    
    This creates winner-take-all dynamics: the most-accused target
    becomes the most visible, which concentrates further accusation.
    
    The salience_exponent controls how sharply attention concentrates:
    higher = more winner-take-all.
    """

    def __init__(self, config: VariantConfig):
        super().__init__(config, 'attention')

    def step_aggression_spread(self):
        cfg = self.cfg
        alive = self._alive_ids()
        new_agg = {}

        for i in alive:
            neighbors = self._alive_neighbors(i)
            if not neighbors:
                new_agg[i] = self.aggression[i].copy()
                continue

            # Compute aggregate neighbor hostility toward each target
            neighbor_hostility = np.zeros(cfg.n_agents)
            total_w = 0.0
            for j in neighbors:
                w = self._prestige_weight(i, j)
                neighbor_hostility += w * self.aggression[j]
                total_w += w
            if total_w > 0:
                neighbor_hostility /= total_w

            # Zero out self and dead
            neighbor_hostility[i] = 0.0
            for dead in range(cfg.n_agents):
                if not self.alive.get(dead, False):
                    neighbor_hostility[dead] = 0.0

            # Attention weighting: concentrate on top targets
            # Use softmax with temperature controlled by salience_exponent
            hostility_for_alive = neighbor_hostility.copy()
            total_h = np.sum(hostility_for_alive)

            if total_h > 0:
                # Raise to power (sharpens distribution)
                sharpened = hostility_for_alive ** cfg.salience_exponent
                total_sharp = np.sum(sharpened)
                if total_sharp > 0:
                    attention_weights = sharpened / total_sharp
                else:
                    attention_weights = np.zeros(cfg.n_agents)

                # Mimetic pull concentrated by attention
                mimetic_pull = attention_weights * total_h

                result = cfg.alpha * self.aggression[i] + (1 - cfg.alpha) * mimetic_pull
            else:
                result = cfg.alpha * self.aggression[i]

            result[i] = 0.0
            for dead in range(cfg.n_agents):
                if not self.alive.get(dead, False):
                    result[dead] = 0.0
            new_agg[i] = result

        for i, agg in new_agg.items():
            self.aggression[i] = agg


# =====================================================================
# VARIANT 3: SIGNS OF THE VICTIM
# =====================================================================

class SignsOfVictim(BaseSimulation):
    """
    Structural marginality as convergence attractor.
    Some agents start with fewer connections and lower prestige.
    Aggression spread uses the same linear mimetic rule as baseline,
    but the network topology and prestige asymmetry produce convergence.
    
    The question: does structural marginality alone produce scapegoating,
    even with linear mimesis?
    """

    def __init__(self, config: VariantConfig):
        super().__init__(config, 'signs_of_victim')

    def step_aggression_spread(self):
        """Same as linear baseline -- the structural difference does the work."""
        cfg = self.cfg
        alive = self._alive_ids()
        new_agg = {}

        for i in alive:
            neighbors = self._alive_neighbors(i)
            if not neighbors:
                new_agg[i] = self.aggression[i].copy()
                continue

            mimetic_pull = np.zeros(cfg.n_agents)
            total_w = 0.0
            for j in neighbors:
                w = self._prestige_weight(i, j)
                mimetic_pull += w * self.aggression[j]
                total_w += w
            if total_w > 0:
                mimetic_pull /= total_w

            result = cfg.alpha * self.aggression[i] + (1 - cfg.alpha) * mimetic_pull
            result[i] = 0.0
            for dead in range(cfg.n_agents):
                if not self.alive.get(dead, False):
                    result[dead] = 0.0
            new_agg[i] = result

        for i, agg in new_agg.items():
            self.aggression[i] = agg


# =====================================================================
# RUNNER
# =====================================================================

def run_variant(variant_class, config: VariantConfig, n_runs: int = 5) -> list[dict]:
    """Run a variant multiple times, collect summary stats."""
    results = []
    for run_idx in range(n_runs):
        cfg = VariantConfig(
            n_agents=config.n_agents, n_neighbors=config.n_neighbors,
            rewire_prob=config.rewire_prob, n_objects=config.n_objects,
            n_rivalrous=config.n_rivalrous, alpha=config.alpha,
            rivalry_to_aggression=config.rivalry_to_aggression,
            aggression_decay=config.aggression_decay,
            desire_noise=config.desire_noise,
            expulsion_threshold=config.expulsion_threshold,
            threshold_fraction=config.threshold_fraction,
            threshold_boost=config.threshold_boost,
            attention_slots=config.attention_slots,
            salience_exponent=config.salience_exponent,
            n_marginal=config.n_marginal,
            marginal_prestige_factor=config.marginal_prestige_factor,
            marginal_connection_factor=config.marginal_connection_factor,
            n_steps=config.n_steps,
            seed=config.seed + run_idx * 1000,
        )
        sim = variant_class(cfg)
        h = sim.run()

        results.append({
            'n_expulsions': len(h['expulsion_events']),
            'mean_gini': float(np.mean(h['aggression_gini'])),
            'peak_gini': max(h['aggression_gini']) if h['aggression_gini'] else 0,
            'mean_max_share': float(np.mean(h['aggression_max_share'])),
            'peak_max_share': max(h['aggression_max_share']) if h['aggression_max_share'] else 0,
            'mean_convergence_ratio': float(np.mean(h['convergence_ratio'])),
            'peak_convergence_ratio': max(h['convergence_ratio']) if h['convergence_ratio'] else 0,
            'mean_top3_share': float(np.mean(h['aggression_top3_share'])),
            'mean_entropy': float(np.mean(h['aggression_entropy'])),
            'agents_remaining': h['n_active_agents'][-1] if h['n_active_agents'] else config.n_agents,
            'expulsion_events': h['expulsion_events'],
            'history': h,
        })
    return results
