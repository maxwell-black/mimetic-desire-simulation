"""
Mimetic Desire Simulation v2 -- Emergent Scapegoating
======================================================
Redesign: the scapegoat mechanism is NOT hard-coded. There is no
"crisis mode", no accusation subroutine, no mode-switch.

Instead, there is ONE mimetic update rule applied to TWO domains:
  1. Object-desire: how much do I want object o?
  2. Aggression: how much do I want to exclude agent j?

Both update by the same prestige-weighted imitation:
  d_i(t+1) = alpha * d_i(t) + (1-alpha) * weighted_avg(neighbors' d)

Aggression is SOURCED by rivalry (competing for the same object
generates hostility toward the competitor). But it SPREADS mimetically
(I want to exclude whom my models want to exclude, even if I have
no direct rivalry with the target).

Expulsion occurs when total received aggression exceeds a threshold.
This is a consequence of the dynamics, not a triggered subroutine.

FALSIFIABLE PREDICTIONS:
  - At low alpha (high mimesis): aggression converges on few targets
    (power-law distribution of received aggression). Scapegoating emerges.
  - At high alpha (autonomous agents): aggression stays local to
    actual rivalries, distributes uniformly. No scapegoating.
  - The CONVERGENCE itself is the test. If mimetic aggression-transmission
    produces uniform distribution, Girard's scapegoat mechanism is
    disconfirmed for this class of models.

Additional test:
  - Aggression Gini coefficient: measures inequality of received aggression.
    Girard predicts high Gini (concentrated). Null predicts low Gini (diffuse).
"""

import numpy as np
import networkx as nx
from dataclasses import dataclass, field


@dataclass
class SimConfig:
    # Network
    n_agents: int = 50
    n_neighbors: int = 6
    rewire_prob: float = 0.15

    # Objects
    n_objects: int = 8
    n_rivalrous: int = 5

    # Core parameters
    alpha: float = 0.15           # autonomous vs mimetic (low = Girardian)
    rivalry_to_aggression: float = 0.2   # how much rivalry generates aggression
    aggression_decay: float = 0.03       # natural aggression dissipation
    desire_noise: float = 0.02
    expulsion_threshold: float = 8.0     # total received aggression to trigger expulsion

    # Simulation
    n_steps: int = 500
    seed: int = 42


class Agent:
    def __init__(self, agent_id: int, n_objects: int, n_agents: int,
                 rng: np.random.Generator):
        self.id = agent_id
        self.desires = rng.uniform(0.0, 0.3, size=n_objects)
        self.aggression = np.zeros(n_agents)  # aggression toward each other agent
        self.alive = True

    def received_aggression(self, all_agents: dict) -> float:
        """Total aggression directed at this agent from all living agents."""
        total = 0.0
        for other in all_agents.values():
            if other.alive and other.id != self.id:
                total += other.aggression[self.id]
        return total


class MimeticSimulationV2:
    def __init__(self, config: SimConfig):
        self.cfg = config
        self.rng = np.random.default_rng(config.seed)
        self.step_num = 0

        # Build network
        self.graph = nx.watts_strogatz_graph(
            config.n_agents, config.n_neighbors, config.rewire_prob,
            seed=config.seed
        )

        # Asymmetric prestige weights
        self.prestige: dict[tuple[int, int], float] = {}
        for i, j in self.graph.edges():
            self.prestige[(i, j)] = self.rng.uniform(0.1, 1.0)
            self.prestige[(j, i)] = self.rng.uniform(0.1, 1.0)

        # Social distances
        self.distances = dict(nx.all_pairs_shortest_path_length(self.graph))

        # Initialize agents
        self.agents: dict[int, Agent] = {}
        for node in self.graph.nodes():
            self.agents[node] = Agent(node, config.n_objects, config.n_agents, self.rng)

        # History
        self.history = {
            'system_tension': [],
            'mean_desire': [],
            'desire_concentration': [],
            'n_active_agents': [],
            'expulsion_events': [],        # (step, victim_id, received_aggression)
            'aggression_gini': [],         # Gini of received aggression distribution
            'aggression_max_share': [],    # max agent's share of total received aggression
            'aggression_entropy': [],      # Shannon entropy of received aggression
            'mean_aggression': [],
            'top_target_aggression': [],   # aggression received by most-targeted agent
            'rivalry_generated_aggression': [],  # aggression from direct rivalry only
            'mimetic_spread_aggression': [],     # aggression from mimetic transmission
        }

    def _alive_ids(self) -> list[int]:
        return [i for i, a in self.agents.items() if a.alive]

    def _get_alive_neighbors(self, agent_id: int) -> list[int]:
        return [n for n in self.graph.neighbors(agent_id) if self.agents[n].alive]

    def _social_distance(self, i: int, j: int) -> float:
        if j in self.distances.get(i, {}):
            return max(1.0, float(self.distances[i][j]))
        return float('inf')

    def _prestige_weight(self, subject: int, model: int) -> float:
        return self.prestige.get((subject, model), 0.0)

    # ------------------------------------------------------------------
    # STEP 1: Mimetic desire update (same as v1)
    # ------------------------------------------------------------------
    def step_desire(self):
        cfg = self.cfg
        new_desires = {}

        for i in self._alive_ids():
            agent = self.agents[i]
            neighbors = self._get_alive_neighbors(i)

            if not neighbors:
                new_desires[i] = agent.desires.copy()
                continue

            mimetic_pull = np.zeros(cfg.n_objects)
            total_w = 0.0
            for j in neighbors:
                w = self._prestige_weight(i, j)
                mimetic_pull += w * self.agents[j].desires
                total_w += w
            if total_w > 0:
                mimetic_pull /= total_w

            new_d = cfg.alpha * agent.desires + (1 - cfg.alpha) * mimetic_pull
            noise = self.rng.normal(0, cfg.desire_noise, size=cfg.n_objects)
            new_desires[i] = np.clip(new_d + noise, 0.0, None)

        for i, d in new_desires.items():
            self.agents[i].desires = d

    # ------------------------------------------------------------------
    # STEP 2: Rivalry -> Aggression sourcing
    # ------------------------------------------------------------------
    def step_rivalry_aggression(self) -> float:
        """
        Direct rivalry over rivalrous objects generates aggression
        toward the rival. This is the LOCAL source of aggression.
        Returns total rivalry-sourced aggression for tracking.
        """
        cfg = self.cfg
        mimetic_factor = (1.0 - cfg.alpha)
        total_sourced = 0.0

        for i in self._alive_ids():
            agent_i = self.agents[i]
            for j in self._get_alive_neighbors(i):
                agent_j = self.agents[j]
                # Shared desire for rivalrous objects
                shared = 0.0
                for o in range(cfg.n_rivalrous):
                    shared += min(agent_i.desires[o], agent_j.desires[o])

                dist = self._social_distance(i, j)
                # Aggression sourced by rivalry, scaled by mimetic factor
                increment = cfg.rivalry_to_aggression * mimetic_factor * shared / dist
                agent_i.aggression[j] += increment
                total_sourced += increment

        return total_sourced

    # ------------------------------------------------------------------
    # STEP 3: Mimetic aggression spread
    # THIS IS THE KEY STEP. Same update rule as desire, but for aggression.
    # "I want to exclude whom my models want to exclude."
    # ------------------------------------------------------------------
    def step_mimetic_aggression(self) -> float:
        """
        Aggression spreads mimetically: I adopt my models' aggression
        targets, weighted by prestige. This is NOT a separate mechanism --
        it's the same imitation rule applied to aggression vectors.
        
        Returns total mimetically-spread aggression for tracking.
        """
        cfg = self.cfg
        alive = self._alive_ids()
        new_aggression = {}
        total_spread = 0.0

        for i in alive:
            agent_i = self.agents[i]
            neighbors = self._get_alive_neighbors(i)

            if not neighbors:
                new_aggression[i] = agent_i.aggression.copy()
                continue

            # Mimetic pull: weighted average of neighbors' aggression vectors
            mimetic_pull = np.zeros(cfg.n_agents)
            total_w = 0.0
            for j in neighbors:
                w = self._prestige_weight(i, j)
                mimetic_pull += w * self.agents[j].aggression
                total_w += w
            if total_w > 0:
                mimetic_pull /= total_w

            # Blend: autonomous aggression retention + mimetic spread
            new_agg = cfg.alpha * agent_i.aggression + (1 - cfg.alpha) * mimetic_pull

            # Can't be aggressive toward yourself or dead agents
            new_agg[i] = 0.0
            for dead_id in range(cfg.n_agents):
                if dead_id not in self.agents or not self.agents[dead_id].alive:
                    new_agg[dead_id] = 0.0

            # Track mimetic spread (difference from purely local aggression)
            spread = np.sum(np.maximum(new_agg - agent_i.aggression, 0))
            total_spread += spread

            new_aggression[i] = new_agg

        for i, agg in new_aggression.items():
            self.agents[i].aggression = agg

        return total_spread

    # ------------------------------------------------------------------
    # STEP 4: Aggression decay
    # ------------------------------------------------------------------
    def step_decay(self):
        cfg = self.cfg
        for i in self._alive_ids():
            self.agents[i].aggression *= (1 - cfg.aggression_decay)

    # ------------------------------------------------------------------
    # STEP 5: Expulsion (consequence, not mechanism)
    # ------------------------------------------------------------------
    def step_expulsion(self):
        """
        If total received aggression exceeds threshold, agent is expelled.
        This is a CONSEQUENCE of the dynamics. We're just saying: if
        enough agents want you gone, you're gone. The question is whether
        the mimetic dynamics produce this convergence or not.
        """
        cfg = self.cfg
        alive = self._alive_ids()

        # Compute received aggression for each agent
        received = {}
        for v in alive:
            received[v] = self.agents[v].received_aggression(self.agents)

        # Find most-targeted agent
        if not received:
            return

        most_targeted = max(received, key=received.get)
        if received[most_targeted] >= cfg.expulsion_threshold:
            self.agents[most_targeted].alive = False
            self.history['expulsion_events'].append(
                (self.step_num, most_targeted, received[most_targeted])
            )
            # Zero out all aggression toward expelled agent
            for agent in self.agents.values():
                if agent.alive:
                    agent.aggression[most_targeted] = 0.0

    # ------------------------------------------------------------------
    # METRICS
    # ------------------------------------------------------------------
    def _gini(self, values: np.ndarray) -> float:
        """Gini coefficient. 0 = perfect equality, 1 = perfect inequality."""
        if len(values) == 0 or np.sum(values) == 0:
            return 0.0
        sorted_v = np.sort(values)
        n = len(sorted_v)
        index = np.arange(1, n + 1)
        return float((2 * np.sum(index * sorted_v) - (n + 1) * np.sum(sorted_v)) /
                      (n * np.sum(sorted_v)))

    def _entropy(self, values: np.ndarray) -> float:
        """Shannon entropy of distribution."""
        s = np.sum(values)
        if s == 0:
            return 0.0
        p = values / s
        p = p[p > 0]
        return -float(np.sum(p * np.log2(p)))

    def _herfindahl(self) -> float:
        total = np.zeros(self.cfg.n_objects)
        for a in self.agents.values():
            if a.alive:
                total += a.desires
        s = total.sum()
        if s == 0:
            return 0.0
        shares = total / s
        return float(np.sum(shares ** 2))

    def record_history(self, rivalry_sourced: float, mimetic_spread: float):
        alive = self._alive_ids()

        # Received aggression distribution
        received = np.array([
            self.agents[v].received_aggression(self.agents) for v in alive
        ])

        total_agg = np.sum(received)
        self.history['system_tension'].append(float(total_agg))
        self.history['mean_desire'].append(
            float(np.mean([self.agents[i].desires.mean() for i in alive])) if alive else 0.0
        )
        self.history['desire_concentration'].append(self._herfindahl())
        self.history['n_active_agents'].append(len(alive))
        self.history['aggression_gini'].append(self._gini(received))
        self.history['aggression_entropy'].append(self._entropy(received))
        self.history['mean_aggression'].append(float(np.mean(received)) if len(received) > 0 else 0.0)
        self.history['rivalry_generated_aggression'].append(rivalry_sourced)
        self.history['mimetic_spread_aggression'].append(mimetic_spread)

        if total_agg > 0:
            self.history['aggression_max_share'].append(float(np.max(received) / total_agg))
        else:
            self.history['aggression_max_share'].append(0.0)

        self.history['top_target_aggression'].append(float(np.max(received)) if len(received) > 0 else 0.0)

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------
    def run(self) -> dict:
        for t in range(self.cfg.n_steps):
            self.step_num = t
            self.step_desire()
            rivalry_sourced = self.step_rivalry_aggression()
            mimetic_spread = self.step_mimetic_aggression()
            self.step_decay()
            self.step_expulsion()
            self.record_history(rivalry_sourced, mimetic_spread)
        return self.history


def run_alpha_sweep(alphas: list[float], base: SimConfig, n_runs: int = 5) -> dict:
    """Sweep alpha to find phase transition in emergent scapegoating."""
    results = {}
    for alpha in alphas:
        run_data = []
        for run_idx in range(n_runs):
            cfg = SimConfig(
                n_agents=base.n_agents, n_neighbors=base.n_neighbors,
                rewire_prob=base.rewire_prob, n_objects=base.n_objects,
                n_rivalrous=base.n_rivalrous, alpha=alpha,
                rivalry_to_aggression=base.rivalry_to_aggression,
                aggression_decay=base.aggression_decay,
                desire_noise=base.desire_noise,
                expulsion_threshold=base.expulsion_threshold,
                n_steps=base.n_steps,
                seed=base.seed + run_idx * 1000,
            )
            sim = MimeticSimulationV2(cfg)
            h = sim.run()
            run_data.append({
                'n_expulsions': len(h['expulsion_events']),
                'peak_tension': max(h['system_tension']) if h['system_tension'] else 0,
                'mean_gini': float(np.mean(h['aggression_gini'])),
                'peak_gini': max(h['aggression_gini']) if h['aggression_gini'] else 0,
                'mean_max_share': float(np.mean(h['aggression_max_share'])),
                'mean_entropy': float(np.mean(h['aggression_entropy'])),
                'final_concentration': h['desire_concentration'][-1] if h['desire_concentration'] else 0,
                'agents_remaining': h['n_active_agents'][-1] if h['n_active_agents'] else base.n_agents,
            })
        results[alpha] = run_data
    return results
