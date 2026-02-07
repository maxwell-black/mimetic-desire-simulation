"""
Fine-Grained Gamma Sweep -- Lean Version
==========================================
Focused on the transition zone. Reduced N_RUNS and N_STEPS to stay
within compute budget, with a few anchor points outside the zone.
"""

import numpy as np
from dataclasses import dataclass, replace
from collections import Counter
import sys, warnings
warnings.filterwarnings('ignore')
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convergence_variants import VariantConfig, BaseSimulation


def modal_agreement_fixed(aggression, alive, n_agents, zero_threshold=1e-8):
    alive_ids = [i for i, a in alive.items() if a]
    if len(alive_ids) < 2:
        return 0.0, -1
    top_targets = []
    for i in alive_ids:
        agg = aggression[i].copy()
        agg[i] = 0.0
        for j in range(n_agents):
            if not alive.get(j, False):
                agg[j] = 0.0
        if np.sum(np.abs(agg)) < zero_threshold:
            continue
        top_targets.append(np.argmax(agg))
    if not top_targets:
        return 0.0, -1
    counts = Counter(top_targets)
    modal_target, modal_count = counts.most_common(1)[0]
    return modal_count / len(top_targets), modal_target


@dataclass
class SweepConfig(VariantConfig):
    expulsion_enabled: bool = False


class SweepSim(BaseSimulation):
    def __init__(self, config: SweepConfig):
        super().__init__(config, 'sweep')
        self.scfg = config
        self.history['modal_agreement'] = []

    def step_aggression_spread(self):
        cfg = self.cfg
        alive = self._alive_ids()
        new_agg = {}
        for i in alive:
            neighbors = self._alive_neighbors(i)
            if not neighbors:
                new_agg[i] = self.aggression[i].copy()
                continue
            nh = np.zeros(cfg.n_agents)
            tw = 0.0
            for j in neighbors:
                w = self._prestige_weight(i, j)
                nh += w * self.aggression[j]
                tw += w
            if tw > 0:
                nh /= tw
            nh[i] = 0.0
            for d in range(cfg.n_agents):
                if not self.alive.get(d, False):
                    nh[d] = 0.0
            th = np.sum(nh)
            if th > 0:
                sh = nh ** cfg.salience_exponent
                ts = np.sum(sh)
                if ts > 0:
                    aw = sh / ts
                else:
                    aw = np.zeros(cfg.n_agents)
                mp = aw * th
                res = cfg.alpha * self.aggression[i] + (1 - cfg.alpha) * mp
            else:
                res = cfg.alpha * self.aggression[i]
            res[i] = 0.0
            for d in range(cfg.n_agents):
                if not self.alive.get(d, False):
                    res[d] = 0.0
            new_agg[i] = res
        for i, a in new_agg.items():
            self.aggression[i] = a

    def step_expulsion(self):
        if not self.scfg.expulsion_enabled:
            return
        super().step_expulsion()

    def record_history(self):
        super().record_history()
        agr, _ = modal_agreement_fixed(self.aggression, self.alive, self.cfg.n_agents)
        self.history['modal_agreement'].append(agr)


def time_to_threshold(series, threshold=0.95, consecutive=10):
    n = len(series)
    if n < consecutive:
        return n
    for t in range(n - consecutive + 1):
        if all(series[t + k] >= threshold for k in range(consecutive)):
            return t
    return n


def run_gamma(gamma, n_runs=8, n_steps=600):
    results = []
    for r in range(n_runs):
        cfg = SweepConfig(alpha=0.15, salience_exponent=gamma,
                          n_steps=n_steps, expulsion_enabled=False,
                          seed=42 + r * 1000)
        sim = SweepSim(cfg)
        h = sim.run()
        m = h['modal_agreement']
        results.append({
            'peak_gini': float(np.max(h['aggression_gini'])),
            'peak_modal': float(np.max(m)),
            'final_modal': float(np.mean(m[-50:])),
            'final_gini': float(np.mean(h['aggression_gini'][-50:])),
            'time_to_95': time_to_threshold(m, 0.95, 10),
            'time_to_80': time_to_threshold(m, 0.80, 10),
            'time_to_50': time_to_threshold(m, 0.50, 10),
        })
    return results

def avg(r, k): return float(np.mean([x[k] for x in r]))
def sd(r, k):  return float(np.std([x[k] for x in r]))
def med(r, k): return float(np.median([x[k] for x in r]))
def pconv(r, n_steps):  return sum(1 for x in r if x['time_to_95'] < n_steps) / len(r)


if __name__ == '__main__':
    N_RUNS = 8
    N_STEPS = 600

    # Anchors + fine transition zone
    gammas = [0.75, 0.90, 0.95, 1.00,
              1.01, 1.02, 1.05, 1.08, 1.10, 1.15,
              1.25, 1.50, 2.00]

    print("=" * 95)
    print(f"FINE-GRAINED GAMMA SWEEP  (no expulsion, fixed modal metric, "
          f"N={N_RUNS} runs x {N_STEPS} steps)")
    print("=" * 95)

    all_res = {}
    for g in gammas:
        print(f"  gamma={g:.2f} ... ", end='', flush=True)
        r = run_gamma(g, N_RUNS, N_STEPS)
        all_res[g] = r
        print(f"peak_modal={avg(r,'peak_modal'):.3f}  "
              f"final_modal={avg(r,'final_modal'):.3f}  "
              f"peak_gini={avg(r,'peak_gini'):.3f}  "
              f"t95_med={med(r,'time_to_95'):.0f}  "
              f"conv={pconv(r, N_STEPS):.0%}")

    # ---- Full table ----
    print("\n" + "=" * 95)
    print("RESULTS TABLE")
    print("=" * 95)
    hdr = (f"{'gamma':>6} | {'Pk Modal':>8} {'(sd)':>6} | {'Fin Modal':>9} {'(sd)':>6} | "
           f"{'Pk Gini':>7} | {'t50':>5} | {'t80':>5} | {'t95':>5} | {'%Conv':>5}")
    print(hdr)
    print("-" * 95)
    for g in gammas:
        r = all_res[g]
        print(f"{g:>6.2f} | {avg(r,'peak_modal'):>8.3f} {sd(r,'peak_modal'):>5.3f} | "
              f"{avg(r,'final_modal'):>9.3f} {sd(r,'final_modal'):>5.3f} | "
              f"{avg(r,'peak_gini'):>7.3f} | "
              f"{med(r,'time_to_50'):>5.0f} | {med(r,'time_to_80'):>5.0f} | "
              f"{med(r,'time_to_95'):>5.0f} | {pconv(r, N_STEPS):>5.0%}")

    # ---- Critical slowing down ----
    print("\n" + "=" * 95)
    print("CRITICAL SLOWING DOWN  (median t_95 for converging runs only)")
    print("=" * 95)
    for g in gammas:
        if g < 1.0:
            continue
        r = all_res[g]
        t95s = [x['time_to_95'] for x in r if x['time_to_95'] < N_STEPS]
        if t95s:
            print(f"  gamma={g:.2f}:  med={np.median(t95s):>5.0f}  "
                  f"mean={np.mean(t95s):>5.0f}  "
                  f"range=[{min(t95s):>3d}, {max(t95s):>3d}]  "
                  f"({len(t95s)}/{len(r)} converged)")
        else:
            print(f"  gamma={g:.2f}:  no runs reached 95% within {N_STEPS} steps")

    # ---- Phase boundary ----
    print("\n" + "=" * 95)
    print("PHASE BOUNDARY")
    print("=" * 95)
    for i in range(len(gammas) - 1):
        lo, hi = gammas[i], gammas[i+1]
        clo, chi = pconv(all_res[lo], N_STEPS), pconv(all_res[hi], N_STEPS)
        if clo < 0.5 and chi >= 0.5:
            print(f"  Transition: gamma={lo:.2f} ({clo:.0%}) -> "
                  f"gamma={hi:.2f} ({chi:.0%})")
