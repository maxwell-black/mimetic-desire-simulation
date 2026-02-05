"""
Mimetic Desire Simulation
==========================
Agent-based model formalizing Girard's mimetic theory.

Core claims under test:
  A. Triangular desire: agents desire what their models desire
  B. Internal vs external mediation: rivalry intensifies with social proximity
  C. Doubling: mutual modeling creates positive feedback
  D. Mimetic crisis: system-level tension spike from escalating rivalries
  E. Scapegoat resolution: crisis resolves via mimetic convergence of accusation

Architecture:
  - Agents on a Watts-Strogatz small-world graph
  - Desire vectors over objects (some rivalrous, some not)
  - Prestige-weighted mimetic desire update
  - Rivalry escalation inversely proportional to social distance
  - Reflexive doubling above rivalry threshold
  - Crisis detection + scapegoat accusation dynamics
"""

import numpy as np
import networkx as nx
from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class SimConfig:
    # Network
    n_agents: int = 50
    n_neighbors: int = 6          # Watts-Strogatz k
    rewire_prob: float = 0.15     # Watts-Strogatz beta (small-world)

    # Objects
    n_objects: int = 8
    n_rivalrous: int = 5          # first N objects are rivalrous

    # Core parameters
    alpha: float = 0.15           # autonomous desire retention (low = strong Girardian claim)
    beta: float = 0.3             # rivalry escalation rate
    gamma: float = 0.4            # accusation mimesis rate
    doubling_threshold: float = 0.5   # rivalry level triggering reflexive modeling
    crisis_threshold: float = 120.0     # system tension triggering crisis mode
    crisis_cooldown: int = 20          # steps after scapegoating before new crisis can start

    # Dynamics
    desire_noise: float = 0.02    # random perturbation per step
    tension_decay: float = 0.08   # natural tension dissipation
    post_expulsion_reset: float = 0.6  # fraction of tension removed by scapegoating

    # Simulation
    n_steps: int = 500
    seed: int = 42


class Agent:
    def __init__(self, agent_id: int, n_objects: int, rng: np.random.Generator):
        self.id = agent_id
        self.desires = rng.uniform(0.0, 0.3, size=n_objects)  # low initial autonomous desire
        self.rivalries: dict[int, float] = {}
        self.tension: float = 0.0
        self.accusations: dict[int, float] = {}
        self.alive: bool = True  # False = scapegoated/expelled

    def total_rivalry(self) -> float:
        return sum(self.rivalries.values())


class MimeticSimulation:
    def __init__(self, config: SimConfig):
        self.cfg = config
        self.rng = np.random.default_rng(config.seed)
        self.step = 0
        self.in_crisis = False
        self.crisis_steps = 0
        self.cooldown_remaining = 0

        # Build small-world network
        self.graph = nx.watts_strogatz_graph(
            config.n_agents, config.n_neighbors, config.rewire_prob,
            seed=config.seed
        )

        # Assign prestige weights to edges (asymmetric)
        self.prestige: dict[tuple[int, int], float] = {}
        for i, j in self.graph.edges():
            self.prestige[(i, j)] = self.rng.uniform(0.1, 1.0)
            self.prestige[(j, i)] = self.rng.uniform(0.1, 1.0)

        # Compute shortest-path distances for social distance
        self.distances = dict(nx.all_pairs_shortest_path_length(self.graph))

        # Initialize agents
        self.agents: dict[int, Agent] = {}
        for node in self.graph.nodes():
            self.agents[node] = Agent(node, config.n_objects, self.rng)

        # Track history
        self.history = {
            'system_tension': [],
            'mean_desire': [],          # mean desire intensity across all agents
            'max_rivalry': [],
            'desire_concentration': [], # Herfindahl index over objects
            'n_active_agents': [],
            'crisis_active': [],
            'scapegoat_events': [],     # (step, victim_id)
            'desire_vectors': [],       # full snapshot every N steps
            'rivalry_matrix': [],       # full snapshot every N steps
        }

    def _get_neighbors(self, agent_id: int) -> list[int]:
        """Get alive neighbors of an agent."""
        return [
            n for n in self.graph.neighbors(agent_id)
            if self.agents[n].alive
        ]

    def _social_distance(self, i: int, j: int) -> float:
        """Social distance between agents (graph distance, min 1)."""
        if j in self.distances.get(i, {}):
            return max(1.0, float(self.distances[i][j]))
        return float('inf')

    def _prestige_weight(self, subject: int, model: int) -> float:
        """How much subject is influenced by model."""
        return self.prestige.get((subject, model), 0.0)

    def step_mimetic_desire(self):
        """Step 1: Update desires mimetically."""
        cfg = self.cfg
        new_desires = {}

        for i, agent in self.agents.items():
            if not agent.alive:
                continue

            neighbors = self._get_neighbors(i)
            if not neighbors:
                new_desires[i] = agent.desires.copy()
                continue

            # Weighted sum of neighbor desires
            mimetic_pull = np.zeros(cfg.n_objects)
            total_weight = 0.0
            for j in neighbors:
                w = self._prestige_weight(i, j)
                mimetic_pull += w * self.agents[j].desires
                total_weight += w

            if total_weight > 0:
                mimetic_pull /= total_weight

            # Blend autonomous + mimetic
            new_d = cfg.alpha * agent.desires + (1 - cfg.alpha) * mimetic_pull

            # Add noise (autonomous fluctuation)
            noise = self.rng.normal(0, cfg.desire_noise, size=cfg.n_objects)
            new_d = np.clip(new_d + noise, 0.0, None)

            new_desires[i] = new_d

        # Apply updates
        for i, d in new_desires.items():
            self.agents[i].desires = d

    def step_rivalry(self):
        """Step 2: Update rivalries based on shared desire for rivalrous objects.
        
        Key: rivalry increment is scaled by (1 - alpha) to reflect that
        mimetic convergence (not incidental overlap) drives rivalry.
        At high alpha, agents maintain autonomous desires and don't
        generate rivalry from mere coincidence of preference.
        """
        cfg = self.cfg
        mimetic_factor = (1.0 - cfg.alpha)  # 0 when fully autonomous, 1 when fully mimetic

        for i, agent_i in self.agents.items():
            if not agent_i.alive:
                continue

            for j in self._get_neighbors(i):
                agent_j = self.agents[j]
                if not agent_j.alive:
                    continue

                # Only rivalrous objects generate rivalry
                shared_desire = 0.0
                for o in range(cfg.n_rivalrous):
                    shared_desire += min(agent_i.desires[o], agent_j.desires[o])

                dist = self._social_distance(i, j)
                rivalry_increment = cfg.beta * mimetic_factor * shared_desire / dist

                current = agent_i.rivalries.get(j, 0.0)
                agent_i.rivalries[j] = current + rivalry_increment

    def step_doubling(self):
        """Step 3: Reflexive mimesis -- when rivalry is high, agents start modeling each other.
        
        Scaled by (1-alpha): in a rational world, rivalry doesn't make you
        imitate your rival more. In a mimetic world, it does -- that's the
        distinctive Girardian feedback loop.
        """
        cfg = self.cfg
        mimetic_factor = (1.0 - cfg.alpha)

        new_edges = []
        for i, agent_i in self.agents.items():
            if not agent_i.alive:
                continue

            for j, rivalry_level in agent_i.rivalries.items():
                if rivalry_level > cfg.doubling_threshold:
                    agent_j = self.agents[j]
                    if not agent_j.alive:
                        continue

                    # Increase prestige weight of i for j
                    current_w = self._prestige_weight(j, i)
                    boost = 0.1 * mimetic_factor * (rivalry_level - cfg.doubling_threshold)
                    self.prestige[(j, i)] = min(current_w + boost, 2.0)

                    if not self.graph.has_edge(i, j):
                        new_edges.append((i, j))

        for i, j in new_edges:
            self.graph.add_edge(i, j)

    def step_tension(self):
        """Step 4: Aggregate tension."""
        cfg = self.cfg

        for i, agent in self.agents.items():
            if not agent.alive:
                continue
            agent.tension = agent.total_rivalry()
            # Apply decay
            agent.tension *= (1 - cfg.tension_decay)
            # Update rivalries with decay too
            for j in list(agent.rivalries.keys()):
                agent.rivalries[j] *= (1 - cfg.tension_decay * 0.5)

    def system_tension(self) -> float:
        return sum(a.tension for a in self.agents.values() if a.alive)

    def step_crisis(self):
        """Step 5: Scapegoat dynamics during crisis."""
        cfg = self.cfg
        sys_tension = self.system_tension()

        # Cooldown period after scapegoating
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1
            return

        if not self.in_crisis:
            if sys_tension > cfg.crisis_threshold:
                self.in_crisis = True
                self.crisis_steps = 0
                # Initialize accusations
                for agent in self.agents.values():
                    if agent.alive:
                        agent.accusations = {}
                        # Seed: accuse those you're most rivalrous with
                        for j, r in agent.rivalries.items():
                            agent.accusations[j] = r
            return

        # In crisis mode: mimetic accusation update
        self.crisis_steps += 1
        new_accusations = {}

        alive_ids = [i for i, a in self.agents.items() if a.alive]

        for i in alive_ids:
            agent_i = self.agents[i]
            neighbors = self._get_neighbors(i)

            new_acc = {}
            for v in alive_ids:
                if v == i:
                    continue
                own_acc = agent_i.accusations.get(v, 0.0)
                mimetic_acc = 0.0
                total_w = 0.0
                for j in neighbors:
                    w = self._prestige_weight(i, j)
                    mimetic_acc += w * self.agents[j].accusations.get(v, 0.0)
                    total_w += w
                if total_w > 0:
                    mimetic_acc /= total_w
                new_acc[v] = own_acc + cfg.gamma * mimetic_acc
            new_accusations[i] = new_acc

        for i, acc in new_accusations.items():
            self.agents[i].accusations = acc

        # Check for convergence: is there a clear scapegoat?
        # Sum accusations across all agents for each potential victim
        accusation_totals = {}
        for i in alive_ids:
            for v, a in self.agents[i].accusations.items():
                accusation_totals[v] = accusation_totals.get(v, 0.0) + a

        if accusation_totals:
            scapegoat_id = max(accusation_totals, key=accusation_totals.get)
            max_acc = accusation_totals[scapegoat_id]

            # Convergence criterion: scapegoat has >40% of total accusation
            total_acc = sum(accusation_totals.values())
            if total_acc > 0 and max_acc / total_acc > 0.4:
                self._expel_scapegoat(scapegoat_id)

        # Timeout: if crisis lasts too long without resolution, force expulsion
        if self.in_crisis and self.crisis_steps > 15 and accusation_totals:
            scapegoat_id = max(accusation_totals, key=accusation_totals.get)
            self._expel_scapegoat(scapegoat_id)

    def _expel_scapegoat(self, victim_id: int):
        """Expel the scapegoat and reset tension."""
        cfg = self.cfg

        self.agents[victim_id].alive = False
        self.history['scapegoat_events'].append((self.step, victim_id))

        # Post-expulsion tension relief
        for agent in self.agents.values():
            if agent.alive:
                agent.tension *= (1 - cfg.post_expulsion_reset)
                agent.accusations = {}
                # Reduce rivalries
                for j in list(agent.rivalries.keys()):
                    agent.rivalries[j] *= (1 - cfg.post_expulsion_reset)

        self.in_crisis = False
        self.crisis_steps = 0
        self.cooldown_remaining = self.cfg.crisis_cooldown

    def _compute_desire_concentration(self) -> float:
        """Herfindahl index: how concentrated is aggregate desire across objects?
        High = everyone wants the same thing (mimetic convergence).
        Low = diverse desires."""
        total_desire = np.zeros(self.cfg.n_objects)
        for agent in self.agents.values():
            if agent.alive:
                total_desire += agent.desires
        s = total_desire.sum()
        if s == 0:
            return 0.0
        shares = total_desire / s
        return float(np.sum(shares ** 2))

    def record_history(self):
        alive = [a for a in self.agents.values() if a.alive]
        self.history['system_tension'].append(self.system_tension())
        self.history['mean_desire'].append(
            float(np.mean([a.desires.mean() for a in alive])) if alive else 0.0
        )
        self.history['max_rivalry'].append(
            max((a.total_rivalry() for a in alive), default=0.0)
        )
        self.history['desire_concentration'].append(self._compute_desire_concentration())
        self.history['n_active_agents'].append(len(alive))
        self.history['crisis_active'].append(1 if self.in_crisis else 0)

    def run(self) -> dict:
        """Run the full simulation."""
        for t in range(self.cfg.n_steps):
            self.step = t
            self.step_mimetic_desire()
            self.step_rivalry()
            self.step_doubling()
            self.step_tension()
            self.step_crisis()
            self.record_history()

            # Snapshot every 50 steps
            if t % 50 == 0:
                alive_ids = sorted([i for i, a in self.agents.items() if a.alive])
                desire_snapshot = {i: self.agents[i].desires.tolist() for i in alive_ids}
                self.history['desire_vectors'].append((t, desire_snapshot))

        return self.history


def run_alpha_sweep(alphas: list[float], base_config: SimConfig, n_runs: int = 5) -> dict:
    """Sweep over alpha values to find phase transition."""
    results = {}
    for alpha in alphas:
        run_data = []
        for run_idx in range(n_runs):
            cfg = SimConfig(
                n_agents=base_config.n_agents,
                n_neighbors=base_config.n_neighbors,
                rewire_prob=base_config.rewire_prob,
                n_objects=base_config.n_objects,
                n_rivalrous=base_config.n_rivalrous,
                alpha=alpha,
                beta=base_config.beta,
                gamma=base_config.gamma,
                doubling_threshold=base_config.doubling_threshold,
                crisis_threshold=base_config.crisis_threshold,
                desire_noise=base_config.desire_noise,
                tension_decay=base_config.tension_decay,
                post_expulsion_reset=base_config.post_expulsion_reset,
                n_steps=base_config.n_steps,
                seed=base_config.seed + run_idx * 1000,
            )
            sim = MimeticSimulation(cfg)
            history = sim.run()
            run_data.append({
                'peak_tension': max(history['system_tension']),
                'n_crises': sum(1 for i in range(1, len(history['crisis_active']))
                               if history['crisis_active'][i] == 1 and history['crisis_active'][i-1] == 0),
                'n_scapegoats': len(history['scapegoat_events']),
                'final_concentration': history['desire_concentration'][-1],
                'mean_tension': float(np.mean(history['system_tension'])),
                'agents_remaining': history['n_active_agents'][-1],
            })
        results[alpha] = run_data
    return results


if __name__ == '__main__':
    # Quick demo run
    cfg = SimConfig()
    sim = MimeticSimulation(cfg)
    history = sim.run()
    print(f"Peak system tension: {max(history['system_tension']):.2f}")
    print(f"Scapegoat events: {history['scapegoat_events']}")
    print(f"Final agents remaining: {history['n_active_agents'][-1]}")
    print(f"Final desire concentration (Herfindahl): {history['desire_concentration'][-1]:.4f}")
