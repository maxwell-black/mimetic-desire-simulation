# A Computational Test of Girard's Scapegoat Mechanism

**Maxwell J. Black**

Winthrop & Weinstine, P.A., Minneapolis

**Draft -- February 2026 (v14)**

---

## Abstract

Girard claims that mimetic crisis resolves through unanimous polarization against a single victim via a "snowball effect" in which mimetic attraction "multiplies with the number of those polarized." We formalize and test this claim using an agent-based model with four variants arranged in a 2x2 design, crossing two hostility-transmission modes (linear vs. convex redistributive) with two hostility sources (object-rivalry vs. status-rivalry). The central finding is that convex redistribution of hostility -- formalized as salience-weighted reallocation that preserves per-agent mimetic throughput (the L1 norm of the pull vector) while amplifying relative differences among targets -- is, across the model family tested here, the decisive condition for scapegoat convergence. The effective phase boundary lies in a narrow interval just above linearity ($\gamma \in [1.02, 1.05]$). Ablation confirms that convexity without throughput conservation collapses the contagion channel entirely. Under conditions that impede full convergence (larger groups, higher autonomy), the model produces stable factional bifurcation rather than unanimity, an outcome Girard treats as a distinct crisis resolution. The model specifies the formal requirement Girard describes phenomenologically but leaves implicit, and reproduces his broader typology of crisis outcomes from a single mechanism.

**Keywords:** mimetic theory, scapegoat mechanism, agent-based modeling, Girard, conflictual mimesis, collective violence

---

## 1. Introduction

Girard's theory of the scapegoat mechanism makes a precise structural prediction: that mimetic dynamics within a community in crisis will produce spontaneous convergence of hostility onto a single victim, whose expulsion restores social peace. This prediction unifies Girard's accounts of archaic religion, sacrifice, myth, and persecution texts across a body of work spanning four decades. Yet its core dynamical claims -- that mimetic transmission of hostility produces convergent targeting, that the victim is arbitrary, that expulsion produces catharsis -- have not been subjected to controlled test. Girard's evidence is drawn from literary criticism, comparative mythology and anthropology, and scriptural interpretation; the theoretical apparatus has generated a rich secondary literature but no formal or computational evaluation.

This paper addresses that gap. We construct an agent-based model that implements Girard's two-phase account of mimetic crisis as described in *Things Hidden Since the Foundation of the World* (Book I, Chapter 1) and *Violence and the Sacred* (Chapter 6), then tests whether the predicted scapegoat convergence emerges from the formalized dynamics. Our approach is not to encode scapegoating as an outcome and observe its preconditions, but to encode the mimetic mechanisms Girard describes and observe whether scapegoating emerges.

The central finding is that Girard's two-phase decomposition -- rivalry generating hostility (acquisitive mimesis), followed by contagion of hostility producing convergence (conflictual mimesis) -- is structurally sound, but requires a formal specification Girard leaves implicit: hostility-transmission must operate as a *convex redistribution* rule, in which each agent's mimetic pull toward competing targets is reallocated by convex attention weights while the total pull magnitude is held constant at the perceived neighborhood hostility. The effective phase boundary lies in a narrow interval just above linearity ($\gamma \in [1.02, 1.05]$), and applying a convex transform without the throughput-conserving redistribution step collapses the contagion channel entirely (Section 3.3).

### 1.1 Existing Computational Approaches

Computational engagement with Girard's mimetic theory is remarkably sparse. Sack (2021) presents the first agent-based model of mimetic desire in NetLogo, formalizing the triangular structure of subject-mediator-object from *Deceit, Desire, and the Novel*, but addresses only the desire triangle with 3-8 agents and does not extend to collective violence or scapegoating. Gardin (2008) proposes "complex mimetic systems" as a framework but presents no simulation results. Paes (2025) offers a NetLogo model of scapegoating as crisis management, but models crisis and victim-selection as programmatically distinct stages rather than testing whether convergence emerges from mimetic dynamics alone.

Our work differs in two respects. First, we test *emergence*: we encode mimetic transmission rules and observe whether convergent targeting arises as an emergent outcome. Second, we conduct a *mechanism comparison*: we implement multiple candidate convergence mechanisms and test which are necessary and sufficient. This comparative approach isolates the formal structure that does the work in Girard's theory.

### 1.2 Girard's Two-Phase Account

The textual basis for our model is Girard's account in *Things Hidden Since the Foundation of the World* (Book I, Chapter 1).

**Phase 1: Acquisitive Mimesis and the Dissolution of Differences.** Mimetic desire generates rivalry when the desired object is scarce or indivisible. As rivalry intensifies, Girard argues, the rivals "forget about whatever objects are, in principle, the cause of the rivalry and instead become more fascinated with one another" (Girard 1987, 26). In *Violence and the Sacred*, Girard describes this as the crisis of differences: social distinctions that normally prevent direct rivalry dissolve, producing undifferentiation in which "the monstrous double now takes the place of those objects that held the attention of the antagonists at a less advanced stage of the crisis" (Girard 1977, 161).

**Phase 2: Conflictual Mimesis and Unanimous Polarization.** Once objects have dropped away, what remains is mimetic transmission of antagonism itself. The critical dynamical claim:

> Once the object has disappeared and the mimetic frenzy has reached a high degree of intensity, one can expect conflictual mimesis to take over and snowball in its effects. Since the power of mimetic attraction multiplies with the number of those polarized, it is inevitable that at one moment the entire community will find itself unified against a single individual. (Girard 1987, 26)

Two features of this passage are essential for formalization. First, Girard distinguishes the mechanism that produces the crisis (acquisitive mimesis, rivalry over objects) from the mechanism that produces convergence (conflictual mimesis, hostility-transmission). These are structurally different processes. Second, the convergence mechanism is characterized as *multiplicative*: "the power of mimetic attraction *multiplies* with the number of those polarized." Our model tests whether a distinction between linear and convex redistributive hostility-transmission is in fact the formal boundary between crisis-without-convergence and scapegoating.

---

## 2. Model Design

### 2.1 Overview

We implement a family of agent-based models sharing common infrastructure but differing in their hostility-transmission mechanism. All variants operate on a Watts-Strogatz small-world network of $N = 50$ agents with mean degree 6 and rewiring probability 0.15. We chose $N = 50$ because it is large enough that $1/N$ effects do not dominate the convergence metrics, small enough for tractable visualization, and situated in the middle of the range ($N = 20$ to $N = 100$) across which we verify robustness in Section 3.4. Each agent maintains a desire vector over a set of rivalrous and non-rivalrous objects, and an aggression vector over all other agents. The simulation proceeds in discrete timesteps:

1. **Desire step:** agents mimetically absorb neighbors' desires (weighted by prestige).
2. **Aggression-source step:** shared desire for rivalrous objects generates mutual aggression between neighbors (acquisitive mimesis), or status proximity generates rivalry-based aggression (in rivalry variants).
3. **Aggression-spread step:** agents mimetically absorb neighbors' aggression patterns. *This step varies across model variants and constitutes the experimental manipulation.*
4. **Decay step:** all aggression decays by a fixed fraction per timestep.
5. **Expulsion step:** if any agent's total received aggression exceeds a threshold, that agent is removed and all aggression toward them is zeroed.

The expulsion step is a *consequence rule*, not a convergence mechanism: the gamma sweep in Section 3.2 confirms that the sharp phase boundary persists without expulsion. Scapegoat convergence, if it occurs, must emerge from the aggression-spread step.

### 2.2 Variants

We test four model variants designed to isolate the independent contributions of two candidate convergence mechanisms: (i) the character of hostility transmission (linear averaging vs. convex redistributive weighting), and (ii) the source of hostility (shared-object rivalry vs. status-proximity rivalry). Throughout, $w_{ik}$ denotes the prestige weight governing how much agent $i$ imitates agent $k$, while $a_i(j)$ denotes the attention weight governing how much of agent $i$’s mimetic pull is directed at target $j$. The four variants are the cells of a 2x2 design:

|  | Linear spread | Attentional concentration spread |
|---|---|---|
| **Object-rivalry source** | LM (baseline) | AC |
| **Status-rivalry source** | RL | RA |

This design allows us to attribute convergence effects to transmission character, hostility source, or their interaction. **Caveat:** the axes are not perfectly orthogonal. In RL and RA, rivalry dynamics alter prestige and influence weights via status updates, so the "source" dimension has indirect effects on the "spread" dimension. We return to this coupling in Section 4.4; the design nonetheless cleanly separates the primary mechanisms under test.

**LM: Linear Mimesis (baseline).** Agent *i*'s mimetic pull toward target *j* is a prestige-weighted average of neighbors' aggression toward *j*:

$$\text{pull}_i(j) = \frac{\sum_{k \in N(i)} w_{ik} \cdot \text{agg}_k(j)}{\sum_{k \in N(i)} w_{ik}}$$

Updated aggression:

$$\text{agg}_i(j) \leftarrow \alpha \cdot \text{agg}_i(j) + (1 - \alpha) \cdot \text{pull}_i(j)$$

where $\alpha \in [0, 1]$ is a global mimetic susceptibility parameter (note: higher $\alpha$ means *less* mimesis). At $\alpha = 0$, agents are fully mimetic; at $\alpha = 1$, fully autonomous. The same parameter governs desire imitation (Step 1), aggression imitation (Step 3), and rivalry-to-aggression conversion (Step 2), consistent with Girard’s claim that rivalry is itself a mimetic phenomenon: without mimetic desire ($\alpha \to 1$), there is no shared desire, hence no acquisitive rivalry, hence no rivalry-generated aggression.

**AC: Attentional Concentration (Convex Redistribution).** Let $h_i(j)$ denote the prestige-weighted mean hostility toward target $j$ among $i$'s neighbors (computed identically to LM). Let $H_i = \sum_j h_i(j)$ be the total perceived neighborhood hostility. Agent $i$ constructs attention weights and mimetic pull as follows.

Define attention weights:

$$a_i(j) = \frac{h_i(j)^\gamma}{\sum_k h_i(k)^\gamma}$$

Each target's share of agent $i$'s mimetic attention is the target's perceived hostility raised to the power $\gamma$, normalized across all targets. Mimetic pull is then:

$$\text{pull}_i(j) = a_i(j) \cdot H_i$$

Agent $i$ adopts total mimetic pull equal to $H_i$, but distributes that pull across targets according to the convex attention weights.

Two identities characterize this operator.

*Throughput conservation.* Summing over targets:

$$\sum_j \text{pull}_i(j) = H_i$$

The L1 norm of agent $i$'s pull vector equals the total hostility it perceives among its neighbors. The spread step does not inflate or deflate this quantity; it redistributes a fixed per-agent throughput across targets. Note that this is a *per-agent, per-step* property (not a system-level conservation law): define total system hostility mass $M_t = \sum_{i \neq j} A_i(j)$. What the AC operator conserves is the magnitude of each agent's mimetic intake at each step, ensuring that, conditional on the perceived hostility landscape $h_i$ at a given step, varying $\gamma$ changes only the *distribution* of pull across targets, not the magnitude of mimetic intake. This is an operator-level property; the system-level hostility mass $M_t$ is not conserved, since rivalry sourcing, decay, and expulsions all alter it between steps.

*Ratio identity.* For any two targets $a, b$ with $h_i(b) > 0$:

$$\frac{\text{pull}_i(a)}{\text{pull}_i(b)} = \left(\frac{h_i(a)}{h_i(b)}\right)^\gamma$$

Relative mimetic pull between any two targets is the ratio of their perceived hostilities raised to the power $\gamma$. This captures one precise sense in which mimetic attraction could be "multiplicative" in Girard's terms: a difference in salience becomes an amplified difference in imitative focus. (Whether this is the *only* sense Girard intends is discussed in Section 4.2.) The identity is active only when multiple targets have nonzero perceived hostility -- i.e., the operator's convergence-producing behavior presupposes that the rivalry-sourcing step has already populated the aggression landscape with competing targets.

The operator is equivalent to a softmax (Boltzmann/Gibbs distribution) over log-hostilities: $a_i(j) = \exp(\gamma \ln h_i(j)) / \sum_k \exp(\gamma \ln h_i(k))$, with $\gamma$ playing the role of inverse temperature. The phase transition near $\gamma = 1$ (Section 3.2) corresponds to the transition from the high-temperature (dispersed) to low-temperature (concentrated) regime of this distribution.

The salience exponent $\gamma$ controls the qualitative character of redistribution. When $\gamma = 1$, the operator reduces to LM: attention weights are proportional to perceived hostility, and no redistribution occurs. When $\gamma > 1$, relative salience differences are amplified (convex redistribution). When $\gamma < 1$, differences are compressed (concave redistribution), actively dispersing hostility.

Without throughput conservation, a power transform would implicitly change the effective strength of mimesis by shrinking subunit signals (for $x \in (0, 1)$ and $\gamma > 1$, $x^\gamma < x$). The ablation in Section 3.3 confirms that this conservation is constitutive: removing it collapses the contagion channel entirely.

Updated aggression:

$$\text{agg}_i(j) \leftarrow \alpha \cdot \text{agg}_i(j) + (1 - \alpha) \cdot \text{pull}_i(j)$$

**RL: Rivalry + Linear.** Aggression is sourced from *status rivalry* rather than shared object-desire. Each agent has a status scalar (initialized near 0.5); agents in close status proximity generate mutual aggression, weighted toward upward rivalry. Received aggression degrades the target's status, creating a feedback loop. Aggression *spreads* via linear mimesis (as in LM).

**RA: Rivalry + Attention.** Same status-rivalry dynamics as RL, but aggression spreads via attentional concentration (as in AC).

### 2.3 Measurements

For each simulation run, we record: aggression Gini coefficient (inequality of received aggression), top-target share (fraction absorbed by the most-targeted agent), convergence ratio (top1/top2 received aggression), Shannon entropy of targeting, expulsion count and timing, catharsis (fractional tension drop post-expulsion), victim status at expulsion (rivalry variants), and modal-target agreement (fraction of living agents whose top aggression target is the modal target, excluding agents with total aggression below $10^{-8}$).

We define *convergence* as modal-target agreement >= 0.95 sustained for 10 consecutive steps. The theoretical ceiling is $(N-1)/N = 0.98$, since self-targeting is excluded. Under the parameterizations tested, the $10^{-8}$ exclusion threshold never binds during convergence episodes (all agents maintain nonzero aggression once the rivalry-sourcing step is active), so the effective ceiling is $(N-1)/N$ throughout. The 0.95 threshold is somewhat arbitrary; we verified that alternative thresholds of 0.90 and 0.98 do not meaningfully shift the gamma phase boundary identified in Section 3.2.

### 2.4 Metric Definitions

Let $R(v) = \sum_{i \in \mathcal{L}_t, i \neq v} A_i(v)$ be the total received aggression for agent $v$ at time $t$. Let $\mathbf{r} = (R(v_1), \ldots, R(v_m))$ be the vector of received aggression for all $m = |\mathcal{L}_t|$ living agents, sorted in ascending order.

**Aggression Gini coefficient:**

$$G = \frac{\sum_{i=1}^{m} (2i - m - 1) \cdot r_i}{m \cdot \sum_{i=1}^{m} r_i}$$

computed over living agents only. If $\sum r_i = 0$, $G = 0$.

**Top-target share:** $R(v^*) / \sum_v R(v)$, where $v^* = \arg\max_v R(v)$.

**Convergence ratio:** $R(v^*) / R(v^{**})$, where $v^{**}$ is the second-most-targeted living agent.

**Shannon entropy of targeting:** $H = -\sum_v p_v \log_2 p_v$, where $p_v = R(v) / \sum_v R(v)$, computed over living agents with $R(v) > 0$.

**Modal-target agreement:** Let $T_i = \arg\max_j A_i(j)$ be agent $i$’s top target. Let $\mathcal{A}_t = {i \in \mathcal{L}_t : \sum_j A_i(j) > 10^{-8}}$ be the set of agents with nontrivial aggression. The modal target is $t^* = \text{mode}({T_i : i \in \mathcal{A}_t})$. Modal-target agreement is $|{i \in \mathcal{A}_t : T_i = t^*}| / |\mathcal{A}_t|$.



---

## 3. Results

### 3.1 The Convergence Engine: Convex Redistribution

The central result is displayed in Table 1.

| Variant   | Mechanism                 |   Mean Gini |   Top-Target Share |   Convergence Ratio |   Expulsions | Catharsis   |
|:----------|:--------------------------|------------:|-------------------:|--------------------:|-------------:|:------------|
| LM        | Linear mimesis            |       0.115 |              0.041 |                1.05 |         16.6 | 5.6%        |
| AC        | Attentional concentration |       0.739 |              0.31  |                1.62 |         28.8 | 29.6%       |
| RL        | Rivalry + linear          |       0.223 |              0.043 |                1.06 |         14.3 | 6.3%        |
| RA        | Rivalry + attention       |       0.812 |              0.436 |                2.19 |         26.8 | 36.7%       |

*Table 1. Summary metrics across 10 runs per variant (seeds spaced by 1000), $\alpha=0.15$, salience exponent $\gamma=2.0$, 600 timesteps, expulsion threshold $\tau=8.0$. Gini, top-target share, and convergence ratio are time-averaged over all 600 timesteps within each run and then averaged across runs (note that this averaging mixes pre- and post-convergence regimes for AC and RA; peak and final-window values are reported in the no-expulsion gamma sweep, Table 2). “Expulsions” reports the mean number of expulsions per run. “Catharsis” reports the mean immediate fractional drop in total received aggression following an expulsion (averaged over expulsions within a run, then averaged across runs). Formally, catharsis for a single expulsion event at step $t$ is $(M_{t^-} - M_{t^+}) / M_{t^-}$, where $M_{t^-} = \sum_{v} R(v)$ is total received aggression immediately before expulsion and $M_{t^+}$ is total received aggression immediately after (i.e., after zeroing all aggression toward the expelled agent).*

Under the full dynamics with expulsions enabled at the default threshold ($\tau = 8.0$), no variant achieves sustained convergence (Table 1b). This confirms that at low thresholds, expulsion interrupts the convergence process before unanimity -- a finding developed in the threshold-regime analysis of Section 3.6.

| Variant   | Convergence Rate   | Median t₁   |   Fraction Steps Converged |   Mean Peak Modal |
|:----------|:-------------------|:------------|---------------------------:|------------------:|
| LM        | 0%                 | —           |                          0 |             0.249 |
| AC        | 0%                 | —           |                          0 |             0.468 |
| RL        | 0%                 | —           |                          0 |             0.315 |
| RA        | 0%                 | —           |                          0 |             0.564 |

*Table 1b. Convergence outcomes under full dynamics (expulsions enabled). Convergence is defined as modal-target agreement $\ge 0.95$ sustained for 10 consecutive steps. “Median $t_1$” reports the first timestep at which a qualifying episode begins (reported only when at least one run converges). “Fraction steps converged” is the share of timesteps lying inside qualifying convergence episodes. “Mean peak modal” is the runwise maximum modal-target agreement averaged across runs; it remains informative even when convergence rate is 0%.*

The transmission-character axis remains the dominant divider. Under linear transmission (LM, RL), hostility remains diffuse: top-target shares stay near $\sim 0.04$ and convergence ratios remain near 1.0. Introducing status rivalry under linear spread (RL) modestly increases inequality in received aggression (Mean Gini 0.223 vs 0.115 in LM), but does not produce strong single-target concentration or sustained coordination. By contrast, convex redistributive transmission (AC, RA) sharply concentrates hostility (Mean Gini 0.739–0.812; top-target share 0.310–0.436) and deepens catharsis (29.6–36.7%). Status rivalry under attentional concentration (RA vs AC) further increases concentration and catharsis, consistent with a marginalization feedback, but the redistributive transmission mechanism still does the majority of the convergence work.

With expulsions enabled at $\tau=8$, none of the variants satisfy our strict convergence criterion (modal agreement $\ge 0.95$ for 10 consecutive steps; Table 1b). Nevertheless, attention-based variants reach substantially higher peak modal agreement (AC 0.468; RA 0.564) than linear variants (LM 0.249; RL 0.315), showing transient movement toward unanimity even when expulsion interrupts sustained convergence.

![Figure 1. Convergence trajectories under linear vs. convex redistributive transmission (no expulsion, seed 42). Under linear mimesis (LM), modal-target agreement fluctuates around 0.12--0.18: the community generates hostility but never coordinates it. Under attentional concentration (AC), the mimetic snowball drives agreement from 0.06 to 0.98 by step 31. The RA variant (dashed) converges faster still, consistent with rivalry's potentiating role. The ceiling of 0.98 = (N-1)/N reflects the excluded self-targeting constraint.](../figures/fig1_trajectories.png)

Applying a convex transform without throughput conservation ($\text{pull} = h^\gamma$) does not produce convergence and in fact collapses the contagion channel by attenuating subunit signals (Section 3.3). Convergence requires the full redistributive operator: convex attention weights *plus* throughput conservation of perceived hostility.

### 3.2 The Effective Phase Boundary Near Linearity

To locate the boundary between diffuse crisis and scapegoat convergence, we performed a fine-grained sweep of the salience exponent $\gamma$ under the no-expulsion condition, isolating the convergence mechanism from the expulsion consequence rule.

| $\gamma$ | Peak Modal (sd) | Final Modal (sd) | Peak Gini | Med $t_{95}$ | Convergence Rate |
|-----------|-----------------|------------------|-----------|---------------|------------------|
| 0.75 | 0.125 (0.017) | 0.098 (0.017) | 0.100 | -- | 0% |
| 0.90 | 0.150 (0.020) | 0.122 (0.027) | 0.103 | -- | 0% |
| 0.95 | 0.172 (0.032) | 0.136 (0.029) | 0.104 | -- | 0% |
| 1.00 | 0.240 (0.074) | 0.194 (0.057) | 0.115 | -- | 0% |
| 1.01 | 0.305 (0.118) | 0.218 (0.071) | 0.132 | -- | 0% |
| 1.02 | 0.463 (0.260) | 0.356 (0.221) | 0.166 | 421 | 12.5% |
| 1.05 | 0.980 (0.000) | 0.980 (0.000) | 0.810 | 116 | 100% |
| 1.08 | 0.980 (0.000) | 0.980 (0.000) | 0.881 | 74 | 100% |
| 1.10 | 0.980 (0.000) | 0.980 (0.000) | 0.906 | 62 | 100% |
| 1.15 | 0.980 (0.000) | 0.980 (0.000) | 0.937 | 43 | 100% |
| 1.25 | 0.980 (0.000) | 0.980 (0.000) | 0.959 | 30 | 100% |
| 1.50 | 0.980 (0.000) | 0.980 (0.000) | 0.970 | 29 | 100% |
| 2.00 | 0.980 (0.000) | 0.980 (0.000) | 0.972 | 30 | 100% |

*Table 2. Fine-grained gamma-sweep results. N=50 agents, Watts-Strogatz k=6, p=0.15, alpha=0.15, no expulsion, 8 runs x 600 steps per condition.*

The effective phase boundary is sharp and narrowly localized.[^crit] For $\gamma \leq 1.01$, no runs converge. At $\gamma = 1.02$, convergence is rare and slow (1 of 8 runs; $t_{95} = 421$). By $\gamma = 1.05$, convergence is universal (8/8; median $t_{95} = 116$). The boundary lies in the interval [1.02, 1.05]: a ~3% departure from purely proportional imitation separates crisis-without-convergence from robust scapegoating.

[^crit]: The critical-slowing pattern near the boundary -- median $t_{95}$ jumps from 116 at $\gamma = 1.05$ to 421 at $\gamma = 1.02$, a fourfold increase for a 3% change in the exponent -- is consistent with a phase-transition-like boundary, though we do not claim a continuous (second-order) phase transition on the basis of finite-horizon data. We use "effective phase boundary" throughout to denote the empirically observed transition interval, without claiming universality-class membership.

Above the boundary, coordination rapidly saturates: peak modal agreement reaches its ceiling of 0.98 for all $\gamma \geq 1.05$. But the inequality of hostility mass (peak Gini) continues to increase with $\gamma$ -- from 0.810 at $\gamma = 1.05$ to 0.972 at $\gamma = 2.0$. The exponent governs not only convergence speed but also the depth of hostility concentration.

Decreasing $\gamma$ below 1 reduces both peak modal agreement and peak Gini monotonically. Under the normalized attention weighting $a_i(j) \propto h_i(j)^\gamma$, values $\gamma < 1$ compress relative salience differences, actively pushing hostility toward uniformity.

![Figure 2. The effective phase boundary near linearity. (a) Convergence rate as a function of salience exponent $\gamma$, showing the sharp transition from 0% to 100% within the interval $\gamma^* \in [1.02, 1.05]$ (shaded). (b) Median time to convergence ($t_{95}$) for converging conditions, with min--max bars across 8 runs. The fourfold increase from $t_{95} = 30$ at $\gamma = 1.25$ to $t_{95} = 421$ at $\gamma = 1.02$ is consistent with critical slowing down near a phase-transition-like boundary.](../figures/fig2_phase_transition.png)

### 3.3 Operator Ablation

The AC convergence mechanism has two components: the convex power transform ($h^\gamma$ with $\gamma > 1$) and the redistributive normalization step ($\div \sum_k h_i(k)^\gamma$, $\times \sum_k h_i(k)$). This ablation isolates their respective contributions.

We define total aggression mass at time $t$ as $M_t = \sum_{i \neq j} \text{agg}_i(t, j)$.

**Condition 1: Linear baseline ($\gamma = 1$).** Hostility spreads but does not converge: peak Gini = 0.115, peak modal = 0.240. Total mass stabilizes at approximately 644, reflecting equilibrium between rivalry-sourcing and decay.

**Condition 2: Raw convex transform ($h^\gamma$, no normalization).** One might expect that a superlinear transform alone would produce convergence, since the exponent amplifies differences. It does not. Peak Gini = 0.115, peak modal = 0.113 -- *worse* than linear. Total mass collapses to approximately 9.1, a 98.6% reduction. The explanation is arithmetic: for $x \in (0, 1)$ and $\gamma > 1$, $x^\gamma < x$. Since hostility signals are typically subunit after prestige-weighted averaging, the power transform systematically attenuates the contagion channel. With decay, this attrition bleeds the system dry.[^clip]

**Condition 3: Full AC operator (convex redistribution, throughput conserved).** The normalization step rescales the sharpened weights so total mimetic pull equals total perceived hostility, preventing the attrition of Condition 2. Peak Gini = 0.972, peak modal = 0.980, total mass = 786.

| Condition | Description | Peak Gini | Peak Modal | Final Mass | Max Aggression |
|-----------|-------------|-----------|------------|------------|----------------|
| 1 | Linear baseline ($\gamma = 1$) | 0.115 | 0.240 | 644 | 0.646 |
| 2 | Raw $h^\gamma$ (no normalization) | 0.115 | 0.113 | 9.1 | 0.053 |
| 3 | Full AC (convex redistribution) | 0.972 | 0.980 | 786 | 19.1 |

*Table 3. Ablation results. All conditions: N=50, alpha=0.15, no expulsion, 600 steps, 8 runs. Conditions 2 and 3 use gamma=2.0.*

The convergence boundary is not "convexity alone"; it is convexity operating as a redistribution rule under throughput conservation.

[^clip]: Clamping $h^\gamma$ to $[0, \text{max-val}]$ produces results identical to Condition 2, confirming the collapse is due to signal attrition, not numerical overflow.

A further ablation (Appendix D) addresses the natural follow-up: what if the scaling problem is corrected without per-step redistribution? Replacing the AC operator with a fixed-scale convex map $\text{pull}_i(j) = C \cdot h_i(j)^\gamma$, with $C$ calibrated from a linear burn-in to match total hostility throughput, eliminates signal attrition but yields no stable convergence regime. Below a sharp explosion threshold $C_{\mathrm{crit}} \approx 0.86 \, C_{\mathrm{cal}}$, the system behaves identically to the linear baseline; above it, total tension diverges within 7--58 steps. That the explosion threshold falls *below* the calibrated constant means even matching average linear-regime throughput overshoots when applied to a sharpened distribution. The per-step throughput-conserving renormalization is constitutive: it bounds total mimetic pull at $H_i$ while redistributing that fixed budget toward the leading target, creating zero-sum cross-target competition that no fixed-scale map can replicate.

### 3.4 Robustness

Convergence under convex redistribution is robust across network topology: Watts-Strogatz, Barabasi-Albert, Erdos-Renyi, and complete graphs all produce 100% convergence at $\gamma = 2.0$ and $N = 50$ (Table E1). Complete graphs yield the fastest convergence (median $t_{95} = 6$), consistent with Girard's account of undifferentiation crisis: the absence of structural differentiation accelerates the snowball. At $N = 20$, convergence is both universal (100%) and rapid (median $t_{95} = 10$), consistent with Girard's claim that the scapegoat mechanism operates most reliably in small archaic communities where "mimetic unanimity" encounters fewer structural impediments.

Convergence is sensitive to group size and mimetic susceptibility. At $N = 100$ (Watts-Strogatz, $\alpha = 0.15$), convergence drops to 62%. At $\alpha = 0.50$, convergence is 88%; at $\alpha = 0.85$ (85% autonomous aggression), convergence is 75--88% depending on $\gamma$. Extended runs (2400 steps) confirm that these are not time-horizon effects: the non-converging runs are genuinely metastable. The mechanism still concentrates hostility -- peak Gini exceeds 0.80 in all conditions -- but does not always achieve unanimity.

Analysis of the non-converging runs reveals a distinctive failure mode: **stable factional bifurcation**. Rather than collapsing onto a single victim, the attentional cascade splits into two competing scapegoat funnels, each commanding a community faction. Of seven non-converging runs across all conditions, six exhibit clear bifurcation: the two top targets absorb 77--89% of all hostility between them, the targets are graph-distant (3--5 hops, zero shared neighbors in all but one case), and the factions are spatially separated. One run ($N = 100$, seed 5042) shows a more fragmented pattern with only 34% top-two share, suggesting a third possible outcome -- disintegration -- under conditions of maximal community size. Table 5 summarizes.

| Condition | Non-conv. | Top-2 share | Faction split | Target dist | Shared $\mathcal{N}$ |
|-----------|-----------|-------------|---------------|-------------|----------------------|
| $N = 100$, $\alpha = 0.15$ | 3/8 | 34--89% | 87/11, 60/38, 55/43 | 2--5 | 0--1 |
| $N = 50$, $\alpha = 0.50$ | 1/8 | 78% | 30/18 | 4 | 0 |
| $N = 50$, $\alpha = 0.85$, $\gamma = 1.5$ | 1/8 | 78% | 27/21 | 4 | 0 |
| $N = 50$, $\alpha = 0.85$, $\gamma = 2.0$ | 2/8 | 82% | 39/9, 28/20 | 3--4 | 0 |

*Table 5. Structure of non-converging runs. "Top-2 share" is the fraction of total received aggression absorbed by the two most-targeted agents at step 600. "Faction split" counts agents whose primary target is victim 1 vs victim 2 (excluding targets themselves). "Shared $\mathcal{N}$" is the number of shared graph neighbors between the two top targets. All conditions use AC variant, no expulsion, 8 runs per condition.*

This is structurally distinct from incomplete convergence: it is *two convergences* that partition the community. We return to the theoretical significance of this outcome in Section 4.1.

### 3.5 Catharsis Dynamics

Expulsion produces measurable tension reduction. Under the default parameterization ($\gamma = 2.0$, $\tau = 8.0$), the mean immediate fractional drop in total received aggression following an expulsion is 29.6% in AC and 36.7% in RA (Table 1), with attention-based variants producing substantially deeper catharsis than their linear counterparts (LM: 5.6%, RL: 6.3%). The system exhibits crisis-relief-reaccumulation cycles with clustered inter-expulsion intervals (runs of rapid expulsions separated by extended quiet periods). The immediate tension drop is partly arithmetic (removing the most-targeted agent eliminates their share of total received aggression), but the emergent finding is that tension does not immediately redirect: the attentional funnel requires time to reconstitute after losing its focal point, and this temporal gap constitutes the emergent catharsis. These metrics reflect the default threshold of 8.0; Section 3.6 shows qualitatively different cycle structures at higher thresholds.

### 3.6 Expulsion Threshold and the Conditions for the Founding Murder

The expulsion threshold determines whether the community's capacity for collective violence exceeds its capacity for mimetic convergence. This ratio produces qualitatively distinct regimes.

In the no-expulsion condition, the AC mechanism drives modal agreement to 0.98 by approximately step 50, and total received aggression for the modal target stabilizes at roughly 700--900. This equilibrium ceiling bounds the threshold values at which expulsion can fire. We tested thresholds from 8 to 750 across 12 runs of 1500 steps and identified three regimes.

*Regime 1: Low threshold (8.0).* Expulsion fires at step 4, when modal agreement is approximately 0.13. The community acts before convergence has begun, producing rapid serial purges (~30 per run) with no unanimity and no sustained peace. Victims are selected by proximity to the threshold rather than collective consensus.

*Regime 2: High threshold (500).* Expulsion fires at approximately step 36, when modal agreement has reached 0.97. The community converges to near-total unanimity before acting: the victim is selected by the mimetic snowball, and the expulsion is singular rather than serial. This is the structural precondition Girard identifies for the founding murder -- total participation leaves no external vantage point from which to recognize the selection as arbitrary.

The founding murder produces genuine but transient peace. Modal agreement drops from 0.98 to approximately 0.06 post-expulsion, and total system tension collapses by roughly 95%. Modal agreement remains below 0.50 for a median of 17 steps. But the mimetic dynamics then reconstitute: agreement climbs back through 0.80 at step ~30 and reaches 0.98 by step ~50. The system produces 6 expulsions over 1500 steps in a rhythm of crisis-unanimity-expulsion-peace-reconvergence cycles -- qualitatively different from Regime 1's continuous grind, but not the permanent resolution Girard associates with the founding murder. Section 4.3 addresses what is missing.

*Regime 3: Threshold above equilibrium ceiling (750+).* The community achieves and sustains unanimous targeting but expulsion fires rarely or not at all. This is permanent crisis without resolution.

| Threshold | Expulsions | 1st Exp Step | Pre-Exp Modal | Peace (steps) | Reconverge $t_{95}$ | Gap to 2nd |
|-----------|-----------|-------------|--------------|--------------|-------------------|-----------|
| 8 | 29.8 | 4 | 0.13 | 0 | -- | 1 |
| 200 | 15.3 | 20 | 0.63 | 3 | 15 | 11 |
| 500 | 6.2 | 36 | 0.97 | 17 | 49 | 59 |
| 750 | 2.0 | 132 | 0.98 | 25 | -- | 260+ |

*Table 4. Post-expulsion dynamics across threshold regimes. 12 runs x 1500 steps, gamma = 2.0, alpha = 0.15. Peace = consecutive steps with modal agreement < 0.50 after first expulsion.*

The three regimes are produced by a single parameter controlling the ratio of violence capacity to convergence capacity. Girard's founding murder implicitly assumes Regime 2. The model makes this assumption explicit and shows it is non-trivial: if the threshold is too low, the result is serial violence without unanimity; if too high, unanimity without discharge. The founding murder occupies a specific parameter region.

![Figure 3. Expulsion threshold regimes. (a) At $\tau = 8$ (Regime 1), expulsion fires before convergence begins, producing rapid serial purges with no sustained unanimity. (b) At $\tau = 500$ (Regime 2), the community converges to near-total unanimity before each expulsion (red vertical lines). Post-expulsion, modal agreement collapses and a transient peace phase ensues before the mimetic snowball reconstitutes. The repeating sawtooth pattern -- crisis, unanimity, expulsion, peace, reconvergence -- corresponds to the cycle structure Girard describes, minus the institutional stabilization of the sacred (Section 4.3).](../figures/fig3_founding_murder.png)

### 3.7 The Arbitrariness and Endogenous Marginality of the Victim

In AC (no rivalry), victims are statistically indistinguishable from the general population across all measured network properties: degree centrality (0.125 vs 0.122, $p = 0.10$), betweenness centrality (0.037 vs 0.036, $p = 0.38$), clustering coefficient (0.388 vs 0.395, $p = 0.54$; Mann-Whitney $U$, all nonsignificant; $n_{\text{victims}} = 288$ across 10 runs). The victim's identity is a contingent outcome of the attentional cascade, not a structural property of the network. Initial symmetry-breaking is driven by stochastic fluctuations: small differences in early-timestep aggression patterns (arising from random desire initialization, prestige-weight asymmetries, and noise) give one target a transient salience advantage that the convex redistribution operator amplifies into a lock-in. Different random seeds produce different victims with no systematic network-structural bias.

In RA (rivalry + attention), victims have a mean status of 0.451 (95% CI [0.441, 0.460]) at expulsion, against a population mean of 0.487 -- a deficit of 0.036 ($p < 0.001$, Mann-Whitney $U$, one-sided; $n_{\text{victims}} = 268$). Although the deficit is modest in absolute terms, it is highly significant and entirely endogenous: status was initialized uniformly around 0.5. The victim's lower status is produced by the mechanism itself -- they were targeted, which degraded their status, which reduced their prestige and capacity to resist further targeting. The "signs of the victim" -- visible markers of difference that retrospectively justify the community's violence -- are *produced* by the mechanism, not presupposed by it.

In RL (rivalry + linear), the victim status deficit is larger in absolute terms (0.063, $p < 0.001$) but occurs against a background of globally collapsed status: mean population status under RL is 0.173 (vs 0.487 under RA), because diffuse aggression degrades all agents roughly equally. The endogenous *targeting* of status degradation -- selective damage to victims against a backdrop of otherwise-stable population status -- requires the convergence mechanism (convex redistribution). Rivalry provides the degradation channel; convex redistribution provides the selectivity.

---

## 4. Discussion

### 4.1 What the Model Specifies Beyond Girard

Girard correctly identified the two-phase structure (rivalry-driven hostility generation, then hostility-contagion-driven convergence), correctly predicted the emergent properties (arbitrariness and retrospective marginalization of the victim, cathartic relief), and correctly characterized the convergence mechanism as multiplicative. What the model adds is the identification of the precise formal property that produces convergence: convex redistribution of hostility under per-agent throughput conservation.

The ratio identity $\text{pull}_i(a)/\text{pull}_i(b) = (h_i(a)/h_i(b))^\gamma$ captures one sense in which mimetic attraction could be "multiplicative": relative salience differences are amplified by the exponent. But Girard's formulation -- "multiplies with the *number* of those polarized" -- also admits an interpretation involving increasing returns to group size or recruitment, which the AC operator does not directly model. What the operator *does* model is the finite-attention mechanism by which an individual, perceiving heterogeneous hostility among neighbors, disproportionately imitates the leading target. Whether Girard's "multiplies" refers to this individual-level salience amplification, to group-level recruitment dynamics, or to both, is a question the text underdetermines. Our contribution is to show that the individual-level mechanism alone suffices for convergence.

The ablation results (Section 3.3) reveal that the convergence boundary is not "convexity" generically but convexity operating as a *budget allocation rule*. The AC operator does not create hostility mass; it gives existing mass a direction. Raw convex amplification (Condition 2) destroys the contagion channel; fixed-scale correction (Appendix D) produces either baseline behavior or runaway explosion. Only per-step throughput-conserving redistribution creates the zero-sum cross-target competition that drives convergence. This aligns with Girard's phenomenology more precisely than a naive "amplification" reading: in Girard, mimetic crisis is already a high-energy field of undifferentiated violence; the scapegoat mechanism *organizes* that field into unanimity rather than intensifying it.

The 2x2 design clarifies the relative dynamical weight of the two phases: the AC mechanism accounts for the overwhelming majority of convergence, while rivalry contributes an additional ~8% Gini concentration and the endogenous marginality effect. Rivalry is a potentiator, not the primary driver. The model also reveals that minimal mimetic susceptibility suffices: even populations with 85% autonomous aggression produce scapegoats if the remaining 15% of mimetic transmission has convex redistributive character -- though at reduced rates, as discussed below.

#### Crisis Typology

The robustness analysis (Section 3.4) reveals that the model reproduces not just the scapegoat mechanism but a broader typology of crisis outcomes that Girard himself describes. Under conditions favoring convergence (small $N$, low $\alpha$), the model produces unanimity: the founding murder. Under conditions that impede convergence (large $N$, high $\alpha$), the model produces stable factional bifurcation: two competing scapegoat cascades that partition the community, each faction internally unanimous against its own victim. Girard treats both outcomes as possible consequences of the same dynamics. In *Violence and the Sacred*, he writes that "violence precedes either the division of an original group into two exogamous moieties, or the association of two groups of strangers" (Girard 1977, 228), and describes how "the interminable vengeance engulfing two rival tribes may be read as an obscure metaphor for vengeance that has been effectively shifted from the interior of the community to the exterior... the tribes have come to an agreement never to agree" (Girard 1977, 266). In the Oughourlian dialogue in *Things Hidden*, Girard acknowledges that unanimity is not inevitable: "It is possible to think that numerous human communities have disintegrated under the pressure of a violence that never led to the mechanism I have just described" (Girard 1987, 27).

The model's bifurcation regime maps onto the pre-resolution factional crisis Girard describes: rival doubles, symmetric antagonism, the "thousand individual conflicts" between "a thousand enemy brothers" that have not yet collapsed into "all against one" (*Violence and the Sacred*, 79). The implication is that larger or more autonomous communities require either stronger mimetic pressure or additional mechanisms -- category generalization, institutional channeling, or what Girard calls the "crisis of differences" that produces full undifferentiation -- to achieve the unanimity the founding murder presupposes. The model makes the boundary between these regimes quantitatively precise.

### 4.2 Structural Analogies in the Empirical Attention Literature

The AC operator is formally a budget allocation rule -- fixed total perceived mass, convex reallocation among competing targets -- which is the mathematical backbone of finite-attention models. The cognitive infrastructure it assumes is empirically grounded. Hodas and Lerman (2014) find that the probability of sharing content scales with the *fraction* of contacts who have shared it, not the absolute count: a consequence of competition for finite attention that produces naturally superlinear concentration on popular items. Weng et al. (2012) demonstrate that competition for limited user attention, combined with network structure, suffices to produce heavy-tailed popularity distributions. Lorenz-Spreen et al. (2019) document accelerating collective attention dynamics across multiple domains, consistent with sharpening winner-take-all effects. These findings establish that finite attention, salience-driven filtering, and mimetic absorption of neighbors' priorities are empirically operative in the domain of content diffusion.

Whether the same dynamics operate in hostile targeting is a theoretical extrapolation. The most relevant bridge is Bauer, Cahlíková, Chytilová, and Želinský (2018), who demonstrate social contagion of ethnic hostility in a field experiment, establishing that hostility *is* contagious and differentially so for outgroup targets. However, Bauer et al. do not measure whether the adoption function is linear or superlinear in the fraction of hostile contacts -- exactly the distinction our model identifies as decisive.

An experimental design adapting Bauer et al.'s paradigm to measure the dose-response functional form of hostility adoption -- specifically, whether it is linear or superlinear in the fraction of hostile contacts -- would constitute a direct empirical test of the model's core mechanism. We develop this proposal and its complications in Section 4.4.

### 4.3 The Missing Sacred

The threshold-regime analysis (Section 3.6) demarcates what mimetic dynamics alone can generate. In Regime 2, the model produces the full cycle structure -- convergence to unanimity, expulsion, genuine peace, reconvergence -- but the peace phase is transient (~17 steps) and the cycle repeats indefinitely. What the model does not produce is the stable social order Girard attributes to the founding murder.

In Girard's account, the "double transference" converts the founding murder into a generative institution: because the community was unanimous, no member recognizes the selection as arbitrary, and the victim is retrospectively attributed causal power over both crisis and resolution. This attribution becomes the basis of the sacred -- prohibition, ritual, and sacrificial substitution -- requiring representational capacities beyond mimetic imitation: memory, causal attribution, institutional repetition.

The model's failure to produce lasting peace is therefore a positive demarcation result. Mimetic dynamics generate the raw material of the scapegoat cycle but not the institutional overlay that stabilizes it. The sacred is the missing layer, and its absence tells us where mimetic theory's explanatory work ends and cultural theory's begins.

Regime 3 -- unanimous hostility without discharge -- bears a structural resemblance to the condition Girard describes in *I See Satan Fall Like Lightning*, in which the scapegoat mechanism has been "revealed" but the community cannot resolve its crisis through other means. We note the parallel without claiming the model captures that condition's full phenomenology.

### 4.4 Limitations and Falsifiability

**Design limitations.** The model treats the transition from acquisitive to conflictual mimesis as structurally given rather than endogenous. A richer model might formalize the conditions under which agents shift from object-focused rivalry to objectless hostility-transmission. The model also lacks institutional or ritual structures that, in Girard's later work, prevent or channel mimetic crisis. The RL/RA status-prestige coupling means the 2x2 axes are not perfectly orthogonal; disentangling the rivalry-source mechanism from its indirect effects on influence structure is a natural extension. The model assumes a single community without external relations. The bifurcation outcome (Section 3.4) suggests that group-level scapegoating -- where hostility toward one member of a perceived category generalizes to others sharing that category -- requires a category-transfer mechanism the model lacks. Real-world instances (pogroms, ethnic cleansing) involve category structure absent from the model's individual-targeting dynamics.

**Alternative formalizations.** "Attentional concentration" is one possible formalization of convex redistributive hostility-transmission. Threshold models, information-cascade models, or explicit "fascination" dynamics might produce convergence with different properties. Our finding that any degree of superlinearity suffices suggests that the specific functional form matters less than the qualitative property of budget-conserving convex reallocation, but systematic comparison is warranted.

**Falsifiability.** The model's core claim is that hostility convergence requires superlinear (convex redistributive) transmission. This would be disconfirmed by observation of scapegoating convergence in a population where hostility transmission is demonstrably linear in homogeneous transmission settings.

Two complications bear on empirical tractability. First, the most relevant experimental work -- Bauer et al. (2018) -- establishes hostility contagion but does not measure whether adoption is linear or superlinear in the fraction of hostile contacts. Second, St-Onge, Hebert-Dufresne, and Allard (2024) show that genuinely linear contagion produces apparent superlinearity in observed data when transmission settings are heterogeneous (varying group sizes, local rates, or contact patterns). This complicates falsification in both directions: apparent superlinearity in naturalistic data could be artifactual, and demonstrating genuinely linear transmission requires controlling for heterogeneity.

The falsifiability criterion must therefore be stated precisely. The model predicts that convergent scapegoating cannot emerge from transmission that is both (a) genuinely linear at the individual cognitive level and (b) operating in homogeneous transmission settings. The most promising experimental design would adapt Bauer et al.'s field-experiment paradigm to measure the dose-response curve of hostility adoption as a function of the *fraction* (not merely the presence) of hostile contacts, under controlled conditions where setting heterogeneity is minimized. Specifically: expose subjects to varying proportions of hostile confederates or primed peers, and test whether the probability of adopting hostile attitudes toward an outgroup target scales linearly or superlinearly with the hostile fraction. A linear dose-response under homogeneous conditions, combined with observed convergent scapegoating, would falsify the model. A superlinear dose-response would provide direct cognitive-level evidence for the mechanism the model formalizes.

---

## 5. Conclusion

Girard writes that "the power of mimetic attraction multiplies with the number of those polarized." We formalized that sentence and tested it. The formalization reveals that the multiplicative character of mimetic attraction in hostile contexts -- convex redistributive transmission, where each agent's fixed mimetic throughput is reallocated among targets by sharpened attention weights -- is, within this model family, the formal condition separating diffuse crisis from scapegoat convergence. Linear transmission produces crisis without resolution; convex redistributive transmission, with the effective phase boundary lying between $\gamma = 1.02$ and $\gamma = 1.05$, produces convergence onto an arbitrary victim, cathartic tension reduction upon expulsion, and -- when combined with status-rivalry dynamics -- endogenous production of the "signs of the victim." The mechanism is not amplification but organization: the operator does not create hostility mass; it focuses existing mass through zero-sum cross-target competition under per-agent throughput conservation.

Girard correctly identified the two-phase structure, predicted the emergent properties, and characterized the convergence mechanism as multiplicative. The model adds the demonstration that this multiplicative character, formalized as budget-conserving convex reallocation, is the precise formal boundary between crisis and scapegoating -- and that the same mechanism produces Girard's full typology of crisis outcomes: unanimity (the founding murder) in small, highly mimetic communities; stable factional bifurcation (moiety formation, externalized violence) in larger or more autonomous ones; and diffuse crisis without resolution under linear transmission. The model demarcates where mimetic dynamics end and the institutional structures of the sacred must begin.

---

## References

Bakshy, E., Hofman, J. M., Mason, W. A., & Watts, D. J. (2011). Everyone's an influencer: Quantifying influence on Twitter. *Proceedings of the Fourth ACM International Conference on Web Search and Data Mining*, 65-74.

Bauer, M., Cahlíková, J., Chytilová, J., & Želinský, T. (2018). Social contagion of ethnic hostility. *Proceedings of the National Academy of Sciences*, 115(19), 4881-4886. https://doi.org/10.1073/pnas.1720317115

Centola, D. (2010). The spread of behavior in an online social network experiment. *Science*, 329(5996), 1194-1197.

Gardin, A. (2008). Complex mimetic systems. *Contagion: Journal of Violence, Mimesis, and Culture*, 15/16, 25-42.

Girard, R. (1965). *Deceit, Desire, and the Novel: Self and Other in Literary Structure*. Trans. Y. Freccero. Johns Hopkins University Press.

Girard, R. (1977). *Violence and the Sacred*. Trans. P. Gregory. Johns Hopkins University Press.

Girard, R. (1986). *The Scapegoat*. Trans. Y. Freccero. Johns Hopkins University Press.

Girard, R. (1987). *Things Hidden Since the Foundation of the World*. Trans. S. Bann and M. Metteer. Stanford University Press.

Girard, R. (2001). *I See Satan Fall Like Lightning*. Trans. J. G. Williams. Orbis Books.

Granovetter, M. (1978). Threshold models of collective behavior. *American Journal of Sociology*, 83(6), 1420-1443.

Hodas, N. O., & Lerman, K. (2014). The simple rules of social contagion. *Scientific Reports*, 4, 4343.

Lorenz-Spreen, P., Moensted, B. M., Hovel, P., & Lehmann, S. (2019). Accelerating dynamics of collective attention. *Nature Communications*, 10, 1759.

O'Higgins Norman, J., & Connolly, J. (2011). Mimetic theory and scapegoating in the age of cyberbullying. *Pastoral Care in Education*, 29(4), 287-300.

Paes, L. (2025). An agent-based model of scapegoating. Unpublished manuscript. [NetLogo model.]

Sack, G. A. (2021). Geometries of desire: A computational approach to Girardian mimetic theory. *Contagion: Journal of Violence, Mimesis, and Culture*, 28, 81-112.

Sprague, D. A., & House, T. (2017). Evidence for complex contagion models of social contagion from observational data. *PLOS ONE*, 12(7), e0180802.

St-Onge, G., Hebert-Dufresne, L., & Allard, A. (2024). Nonlinear bias toward complex contagion in uncertain transmission settings. *Proceedings of the National Academy of Sciences*, 121(1), e2312202121. https://doi.org/10.1073/pnas.2312202121

Weng, L., Flammini, A., Vespignani, A., & Menczer, F. (2012). Competition among memes in a world with limited attention. *Scientific Reports*, 2, 335.

---

## Appendix A: Model Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| N | 50 | Number of agents |
| k | 6 | Mean degree (Watts-Strogatz) |
| p | 0.15 | Rewiring probability |
| alpha | 0.15 | Global mimetic susceptibility (0 = fully mimetic, 1 = fully autonomous). |
| gamma | 2.0 | Salience exponent (AC, RA) |
| Objects | 8 (5 rivalrous) | Number of desire objects |
| Rivalry-to-aggression | 0.2 | Aggression increment from shared desire |
| Aggression decay | 0.03 | Per-step decay fraction |
| Expulsion threshold | 8.0 (default) | Received aggression triggering removal (see Section 3.6) |
| Status loss rate | 0.005 | Aggression-to-status degradation (RL, RA) |
| Rivalry intensity | 0.15 | Rivalry-to-aggression conversion (RL, RA) |
| Timesteps | 600 | Simulation duration |
| Runs per condition | 10 (Tables 1, 1b); 8 (Tables 2, 3, 5, D1, E1); 12 (Table 4) | Replications for summary statistics |

## Appendix B: Code Availability

All simulations are implemented in Python using NumPy and NetworkX. Source code, runner scripts, and figure-generation code are available at: https://github.com/maxwell-black/mimetic-desire-simulation (commit `a5541440098f7f9d69bd8a2ac00796d1d865cba8`, tagged `v12`).

## Appendix C: Pseudocode and Definitions

This appendix provides a complete specification of the per-timestep update rules sufficient to reimplement the model without reference to the source code. All variants share the same timestep structure; they differ only in the aggression-spread step (Step 3).

### C.1 Timestep Loop

```
For t = 1 to T:
    1a. Refresh prestige weights   (RL, RA: recompute w_ik from status; LM, AC: no-op)
    1b. Desire step                (all variants)
    2.  Aggression-source step     (all variants; object-rivalry or status-rivalry)
    3a. Refresh prestige weights   (RL, RA: recompute w_ik from status; LM, AC: no-op)
        [Note: status has not changed since step 1a within this timestep;
         this refresh is defensive and currently a no-op for all variants.]
    3b. Aggression-spread step     (VARIES BY VARIANT: LM, AC, RL, RA)
    4.  Decay step                 (all variants)
    5.  Expulsion step             (all variants)
    6.  Status update step         (RL, RA only; updates status AFTER expulsion)
    7.  Record metrics
```

All updates within a step are computed from the state at the beginning of that step and applied simultaneously (batch update). The prestige refresh occurs twice per timestep (before steps 1b and 3b) so that status-dependent prestige weights in RL/RA reflect the most recent status values before both the desire step and the aggression-spread step. For object-rivalry variants (LM, AC), prestige weights are static and the refresh is a no-op.

### C.2 Definitions

**Network.** A Watts-Strogatz graph $G = (V, E)$ with $|V| = N$, mean degree $k$, and rewiring probability $p$. Let $\mathcal{N}(i)$ denote the neighbors of $i$ in $G$.

**Prestige weights.** For each directed edge $(i, k)$ where $\{i, k\} \in E$, a base prestige weight $w^0_{ik} \in [0.1, 1.0]$ is drawn uniformly at random at initialization. Prestige is asymmetric: $w^0_{ik} \neq w^0_{ki}$ in general. For object-rivalry variants (LM, AC), the prestige weight $w_{ik} = w^0_{ik}$ is static. For status-rivalry variants (RL, RA), the effective prestige weight is status-dependent and recomputed each timestep:

$$w_{ik}(t) = w^0_{ik} \cdot (c_{\text{status}} + S_k(t))$$

where $c_{\text{status}}$ is a baseline floor ensuring that even zero-status agents retain some prestige influence. The prestige weight $w_{ik}$ governs how much agent $i$ imitates agent $k$.

**Desire vectors.** Each agent $i$ maintains $D_i \in \mathbb{R}_{\geq 0}^{n_{\text{obj}}}$, initialized $D_i(o) \sim \text{Uniform}(0, 0.3)$.

**Aggression vectors.** Each agent $i$ maintains $A_i \in \mathbb{R}_{\geq 0}^{N}$ with $A_i(i) = 0$ (no self-aggression) and $A_i(j) = 0$ for all dead agents $j$.

**Alive set.** $\mathcal{L}_t \subseteq V$ denotes agents alive at time $t$.

### C.3 Step 1: Desire Update

For each agent $i \in \mathcal{L}_t$:

$$D_i \leftarrow \alpha \cdot D_i + (1 - \alpha) \cdot \frac{\sum_{k \in \mathcal{N}(i) \cap \mathcal{L}_t} w_{ik} \cdot D_k}{\sum_{k \in \mathcal{N}(i) \cap \mathcal{L}_t} w_{ik}} + \epsilon_i$$

where $\epsilon_i \sim \mathcal{N}(0, \sigma_{\text{noise}}^2)$ elementwise, and the result is clamped to $[0, \infty)$.

**Edge case:** If agent $i$ has no living neighbors, $D_i$ is unchanged.

### C.4 Step 2: Aggression Source

#### Object-rivalry source (LM, AC)

For each pair $(i, k)$ where $k \in \mathcal{N}(i) \cap \mathcal{L}_t$:

$$A_i(k) \leftarrow A_i(k) + \rho \cdot (1 - \alpha) \cdot \frac{\text{SharedDesire}(i, k)}{d(i, k)}$$

where $\rho$ is the rivalry-to-aggression parameter, $d(i, k) = \max(1, \text{shortest-path-length}(i, k))$, and:

**Implementation note:** Because rivalry updates are applied only to network neighbors, $d(i,k) = 1$ in all simulations reported here and the distance factor has no effect. It is retained in the formalism for generality.

$$\text{SharedDesire}(i, k) = \sum_{o=1}^{n_{\text{riv}}} \min(D_i(o),\; D_k(o))$$

summing over rivalrous objects only.

#### Status-rivalry source (RL, RA)

Each agent $i$ has a status scalar $S_i \in [0, 1]$, initialized $S_i \sim \text{Uniform}(0.4, 0.6)$. For each pair $(i, k)$ with $k \in \mathcal{N}(i) \cap \mathcal{L}_t$:

$$A_i(k) \leftarrow A_i(k) + \rho_{\text{riv}} \cdot (1 - \alpha) \cdot \text{UpwardBias}(S_i, S_k) \cdot f(|S_i - S_k|)$$

where

$$f(\Delta S) = \exp\!\left(-\frac{\Delta S}{\sigma_S}\right), \qquad \text{UpwardBias}(S_i, S_k) = 1 + \beta_\uparrow \cdot \max(0,\; S_k - S_i)$$

$f$ is a decreasing function of status distance (agents in close status proximity generate more rivalry), $\text{UpwardBias}$ weights rivalry toward agents of equal or higher status, and the $(1-\alpha)$ factor ensures rivalry-generated aggression vanishes in the fully autonomous limit $\alpha \to 1$. Status is updated once per timestep after expulsion (Step 6, Section C.7a), creating a feedback loop: targeting degrades status, degraded status reduces prestige, reduced prestige reduces the target's capacity to resist further targeting.

### C.5 Step 3: Aggression Spread

For each agent $i \in \mathcal{L}_t$, define the prestige-weighted mean neighbor hostility toward each target $j$:

$$h_i(j) = \frac{\sum_{k \in \mathcal{N}(i) \cap \mathcal{L}_t} w_{ik} \cdot A_k(j)}{\sum_{k \in \mathcal{N}(i) \cap \mathcal{L}_t} w_{ik}}$$

with $h_i(i) = 0$ and $h_i(j) = 0$ for dead $j$.

**Edge case:** If $i$ has no living neighbors, $A_i$ is unchanged for this step.

#### LM and RL (Linear spread)

$$A_i(j) \leftarrow \alpha \cdot A_i(j) + (1 - \alpha) \cdot h_i(j)$$

#### AC and RA (Attentional concentration spread)

Let $H_i = \sum_{j} h_i(j)$ (total perceived neighborhood hostility).

If $H_i > 0$:

Compute sharpened salience: $s_i(j) = h_i(j)^{\gamma}$ for all $j$.

Let $Z_i = \sum_{j} s_i(j)$.

**Edge case:** If $Z_i = 0$ (possible when all $h_i(j) = 0$ despite $H_i > 0$ due to floating-point; or after expulsions leave only zero-aggression targets), set $\text{pull}_i(j) = 0$ for all $j$.

Otherwise, compute attention weights and mimetic pull:

$$a_i(j) = \frac{s_i(j)}{Z_i}, \qquad \text{pull}_i(j) = a_i(j) \cdot H_i$$

Update:

$$A_i(j) \leftarrow \alpha \cdot A_i(j) + (1 - \alpha) \cdot \text{pull}_i(j)$$

If $H_i = 0$: $A_i(j) \leftarrow \alpha \cdot A_i(j)$ for all $j$.

After the update, enforce $A_i(i) = 0$ and $A_i(j) = 0$ for all dead $j$.

**Key identities of the AC operator (when $H_i > 0$ and $Z_i > 0$):**

- *Throughput conservation:* $\sum_j \text{pull}_i(j) = H_i$. The L1 norm of the pull vector equals the total perceived neighborhood hostility. This is a per-agent, per-step property; total system hostility mass $M_t$ is not conserved across timesteps.
- *Ratio identity:* $\text{pull}_i(a) / \text{pull}_i(b) = (h_i(a) / h_i(b))^{\gamma}$ for $h_i(b) > 0$

### C.6 Step 4: Decay

For each agent $i \in \mathcal{L}_t$:

$$A_i \leftarrow (1 - \delta) \cdot A_i$$

where $\delta$ is the per-step decay fraction.

### C.7 Step 5: Expulsion

Compute total received aggression for each potential victim $v \in \mathcal{L}_t$:

$$R(v) = \sum_{i \in \mathcal{L}_t,\; i \neq v} A_i(v)$$

If $\max_v R(v) \geq \tau$ (expulsion threshold):

1. Let $v^* = \arg\max_v R(v)$.
2. Remove $v^*$: set $v^* \notin \mathcal{L}_{t+1}$.
   Define $\mathcal{L}'_t = \mathcal{L}_t \setminus \{v^*\}$ as the post-expulsion living set for this timestep.
3. Zero all aggression toward $v^*$: $A_i(v^*) \leftarrow 0$ for all $i$.

At most one agent is expelled per timestep.

### C.7a Step 6: Status Update (RL, RA only)

After expulsion, update status for all living agents. Let $R(k) = \sum_{i \in \mathcal{L}'_t, i \neq k} A_i(k)$ be the total received aggression of agent $k$ (computed on the post-expulsion state). Let $R_{\max} = \max_{k \in \mathcal{L}'_t} R(k)$.

For each agent $k \in \mathcal{L}'_t$:

$$S_k \leftarrow \text{clamp}\!\left(S_k - \lambda \cdot \frac{R(k)}{\max(R_{\max},\; \varepsilon)},\; 0,\; 1\right)$$

where $\lambda$ is the status loss rate and $\varepsilon = 10^{-12}$ prevents division by zero. The normalization by $R_{\max}$ ensures that the maximally targeted agent loses status at rate $\lambda$ per step, with all other agents losing proportionally less. This occurs after expulsion so that expelled agents do not receive status updates and the post-expulsion hostility landscape (not the pre-expulsion one) determines status degradation.

### C.8 Parameter Summary

| Symbol | Parameter | Default |
|--------|-----------|---------|
| $N$ | Number of agents | 50 |
| $k$ | Mean degree (Watts-Strogatz) | 6 |
| $p$ | Rewiring probability | 0.15 |
| $\alpha$ | Global mimetic susceptibility (0 = fully mimetic, 1 = fully autonomous). | 0.15 |
| $\gamma$ | Salience exponent (AC, RA) | 2.0 |
| $\rho$ | Rivalry-to-aggression rate | 0.2 |
| $\delta$ | Aggression decay rate | 0.03 |
| $\sigma_{\text{noise}}$ | Desire noise std. dev. | 0.02 |
| $\tau$ | Expulsion threshold | 8.0 |
| $\lambda$ | Status loss rate (RL, RA) | 0.005 |
| $\rho_{\text{riv}}$ | Rivalry intensity (RL, RA) | 0.15 |
| $\sigma_S$ | Status proximity scale (RL, RA) | 0.10 |
| $\beta_\uparrow$ | Upward bias coefficient (RL, RA) | 1.0 |
| $c_{\text{status}}$ | Prestige status baseline (RL, RA) | 0.50 |
| $\varepsilon$ | Numerical floor | $10^{-12}$ |
| $n_{\text{obj}}$ | Total objects | 8 |
| $n_{\text{riv}}$ | Rivalrous objects | 5 |
| $T$ | Timesteps | 600 |

## Appendix D: Fixed-Scale Convex Map Ablation

This appendix reports the fixed-scale ablation referenced in Section 3.3. We replace the AC operator's per-step throughput-conserving normalization with a fixed multiplicative constant:

$$\text{pull}_i(j) = C \cdot h_i(j)^\gamma$$

where $C$ is calibrated from a 100-step linear burn-in as $C = \bar{H} / \overline{\sum_j h_j^\gamma}$, matching mean total throughput between the fixed-scale and AC operators during the burn-in phase ($C_{\text{cal}} \approx 3.94$ at default parameters).

We swept $C$ from $0.5 C_{\text{cal}}$ to $2.0 C_{\text{cal}}$ in 20 increments across 8 runs of 600 steps (no expulsion, $\gamma = 2.0$, all other parameters at defaults).

| $C / C_{\text{cal}}$ | Peak Modal | Peak Gini | Diverged |
|---|---|---|---|
| 0.50 -- 0.82 | 0.103 | 0.13 -- 0.17 | 0/8 |
| 0.86 -- 0.97 | 0.29 -- 0.34 | 0.48 -- 0.58 | 3--4/8 |
| 1.05+ | 0.44 -- 0.68 | 0.88 -- 0.98 | 7--8/8 |

*Table D1. Fixed-scale ablation results by $C / C_{\text{cal}}$ band.*

Below a sharp explosion threshold $C_{\text{crit}} \approx 0.86 \, C_{\text{cal}}$, the system behaves like the linear baseline: peak modal agreement remains near 0.10 and peak Gini below 0.17. Above $C_{\text{crit}}$, total system tension diverges, with aggression values exceeding $10^4$ within 7--58 steps depending on the magnitude of overshoot ($C / C_{\text{cal}} = 2.0$: divergence in 7--9 steps; $C / C_{\text{cal}} = 1.2$: divergence in 17--58 steps). No intermediate regime of stable convergence exists.

That $C_{\text{crit}} < C_{\text{cal}}$ is itself significant: even a constant calibrated to match the linear regime's *average* throughput overshoots when applied to a sharpened distribution, because the convex transform concentrates pull on already-high targets while the fixed constant cannot adapt to the evolving hostility landscape.

The per-step throughput-conserving renormalization is therefore constitutive: it bounds total mimetic pull at $H_i$ while redistributing that fixed budget toward the leading target, creating zero-sum cross-target competition that no fixed-scale map can replicate. A fixed $C$ either underdrives the system (reproducing the linear baseline) or overdrives it (producing explosion), because it cannot adapt to the changing hostility landscape at each step.


## Appendix E: Robustness Grid

Table E1 reports convergence outcomes across the conditions referenced in Section 3.4. All runs use the AC variant with no expulsion, 600 steps, 8 runs per condition. Default parameters unless otherwise noted.

|Topology       |$N$|$k$|$\alpha$|$\gamma$|Conv. Rate|Median $t_{95}$|Peak Gini|
|---------------|---|---|--------|--------|----------|---------------|---------|
|Watts-Strogatz |20 |6  |0.15    |2.0     |100%      |10             |0.936    |
|Watts-Strogatz |50 |6  |0.15    |2.0     |100%      |30             |0.972    |
|Watts-Strogatz |100|6  |0.15    |2.0     |62%       |84             |0.973    |
|Barabasi-Albert|50 |3  |0.15    |2.0     |100%      |6              |0.973    |
|Erdos-Renyi    |50 |6  |0.15    |2.0     |100%      |8              |0.973    |
|Complete       |50 |49 |0.15    |2.0     |100%      |6              |0.972    |
|Watts-Strogatz |50 |6  |0.50    |2.0     |88%       |81             |0.941    |
|Watts-Strogatz |50 |6  |0.85    |1.5     |88%       |106            |0.804    |
|Watts-Strogatz |50 |6  |0.85    |2.0     |75%       |192            |0.822    |

*Table E1. Robustness of convergence across topologies, group sizes, and mimetic susceptibility levels. Convergence rate is the fraction of 8 runs achieving modal agreement $\geq 0.95$ within 600 steps. Median $t_{95}$ is computed over converging runs only. Extended runs (2400 steps) confirm that non-converging runs are genuinely metastable, not time-horizon artifacts.*

