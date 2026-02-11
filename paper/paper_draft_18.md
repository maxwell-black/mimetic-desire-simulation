# A Computational Test of Girard's Scapegoat Mechanism

**Maxwell J. Black**

A.B., Harvard College; J.D., Boston College Law School

**Draft -- February 2026 (v18)**

---

## Abstract

Girard claims that mimetic crisis resolves through unanimous polarization against a single victim via a "snowball effect" in which mimetic attraction "multiplies with the number of those polarized." We formalize and test this claim using an agent-based model with four variants arranged in a 2x2 design, crossing two hostility-transmission modes (linear vs. convex redistributive) with two hostility sources (object-rivalry vs. status-rivalry). The central finding is that convex redistribution of hostility -- formalized as salience-weighted reallocation that preserves per-agent mimetic throughput (the L1 norm of the pull vector) while amplifying relative differences among targets -- is, across the model family tested here, the decisive condition for scapegoat convergence. The effective phase boundary lies in a narrow interval just above linearity ($`\gamma \in [1.02, 1.03]`$), is invariant across community sizes from 5 to 500 agents, sharpens with increasing $`N`$, and is robust across wide ranges of mimetic susceptibility ($`\alpha \in [0.05, 0.30]`$) and decay rate ($`\delta \in [0.01, 0.10]`$) -- consistent with a mechanism-level critical threshold rather than a finite-size artifact. Comparison with an alternative convex conserving operator (softmax/Boltzmann) confirms that the phase boundary is a generic property of the operator class, but the power-law's scale invariance is uniquely robust to population scaling: the softmax convergence band narrows monotonically with $`N`$ and vanishes entirely at $`N \geq 150`$ (Appendix G). Ablation confirms that convexity without throughput conservation collapses the contagion channel entirely. Switching from an accumulation trigger to a unanimity trigger for expulsion reveals three qualitatively distinct violence topologies above the phase boundary: a boundary-grinding regime of relentless serial purges with zero peace, a supercritical burst regime of paired expulsions separated by long natural peace intervals, and -- at small community sizes -- self-exhaustion of the mimetic cascade through topology destruction. The founding murder is generative -- self-exhausting with majority survival -- only within a viability window at approximately $`N = 15\text{--}50`$, corresponding to primate and early hominid community sizes. Below this range, each expulsion destroys too large a fraction of the group; above it, the mechanism consumes approximately two-thirds of the population. The viability window identifies the community-size boundary above which Girard's "sacred" becomes structurally indispensable. Self-exhaustion is highly reliable at $`N \approx 50`$ (90%) but declines to $`{\sim}30\%`$ at $`N \approx 500`$, marking a graduated transition consistent with the community-size range at which anthropologists locate the emergence of symbolic culture. These regimes map onto distinct conditions in Girard's theoretical apparatus: the grinding regime identifies the condition under which the sacred -- prohibition, ritual, sacrificial substitution -- is structurally indispensable for community survival; the burst regime produces the empirical pattern of periodic paroxysms that ritual manages but did not invent; and the self-exhaustion regime, confined to small communities, identifies a scale at which mimetic violence is self-correcting and the sacred is not yet structurally necessary. The model specifies the formal requirement Girard describes phenomenologically but leaves implicit, identifies topology-dependent conditions under which unanimity requires dense connectivity rather than emerging from any network structure, reproduces his broader typology of crisis outcomes from a single mechanism, and demarcates the boundary between what mimetic dynamics alone can generate and what requires the cultural elaboration Girard calls the sacred.

**Keywords:** mimetic theory, scapegoat mechanism, agent-based modeling, Girard, conflictual mimesis, collective violence

---

## 1. Introduction

Girard's theory of the scapegoat mechanism makes a precise structural prediction: that mimetic dynamics within a community in crisis will produce spontaneous convergence of hostility onto a single victim, whose expulsion restores social peace. This prediction unifies Girard's accounts of archaic religion, sacrifice, myth, and persecution texts across a body of work spanning four decades. Yet its core dynamical claims -- that mimetic transmission of hostility produces convergent targeting, that the victim is arbitrary, that expulsion produces catharsis -- have not been subjected to controlled test. Girard's evidence is drawn from literary criticism, comparative mythology and anthropology, and scriptural interpretation; the theoretical apparatus has generated a rich secondary literature but no formal or computational evaluation.

This paper addresses that gap. We construct an agent-based model that implements Girard's two-phase account of mimetic crisis as described in *Things Hidden Since the Foundation of the World* (Book I, Chapter 1) and *Violence and the Sacred* (Chapter 6), then tests whether the predicted scapegoat convergence emerges from the formalized dynamics. Our approach is not to encode scapegoating as an outcome and observe its preconditions, but to encode the mimetic mechanisms Girard describes and observe whether scapegoating emerges.

The central finding is that Girard's two-phase decomposition -- rivalry generating hostility (acquisitive mimesis), followed by contagion of hostility producing convergence (conflictual mimesis) -- is structurally sound, but requires a formal specification Girard leaves implicit: hostility-transmission must operate as a *convex redistribution* rule, in which each agent's mimetic pull toward competing targets is reallocated by convex attention weights while the total pull magnitude is held constant at the perceived neighborhood hostility. The effective phase boundary lies in a narrow interval just above linearity ($`\gamma \in [1.02, 1.03]`$) and is invariant across community sizes tested (Section 3.2).

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

We implement a family of agent-based models sharing common infrastructure but differing in their hostility-transmission mechanism. All variants operate on a Watts-Strogatz small-world network of $`N = 50`$ agents with mean degree 6 and rewiring probability 0.15. We chose $`N = 50`$ because it is large enough that $`1/N`$ effects do not dominate the convergence metrics, small enough for tractable visualization, and situated in the middle of the range ($`N = 20`$ to $`N = 100`$) across which we verify robustness in Section 3.4. Scaling experiments (Sections 3.2, 3.8, 3.9) use $`N`$ up to 500, with mean degree adapted as $`k = \max(6, \min(\lfloor 0.12N \rfloor, 20))`$ to maintain comparable connectivity density. Baseline results at $`N = 50`$ use fixed $`k = 6`$. Each agent maintains a desire vector over a set of rivalrous and non-rivalrous objects, and an aggression vector over all other agents. The simulation proceeds in discrete timesteps:

1. **Desire step:** agents mimetically absorb neighbors' desires (weighted by prestige).
2. **Aggression-source step:** shared desire for rivalrous objects generates mutual aggression between neighbors (acquisitive mimesis), or status proximity generates rivalry-based aggression (in rivalry variants).
3. **Aggression-spread step:** agents mimetically absorb neighbors' aggression patterns. *This step varies across model variants and constitutes the experimental manipulation.*
4. **Decay step:** all aggression decays by a fixed fraction per timestep.
5. **Expulsion step:** if any agent's total received aggression exceeds a threshold, that agent is removed and all aggression toward them is zeroed.

The expulsion step is a *consequence rule*, not a convergence mechanism: the gamma sweep in Section 3.2 confirms that the sharp phase boundary persists without expulsion. Scapegoat convergence, if it occurs, must emerge from the aggression-spread step.

### 2.2 Variants

We test four model variants designed to isolate the independent contributions of two candidate convergence mechanisms: (i) the character of hostility transmission (linear averaging vs. convex redistributive weighting), and (ii) the source of hostility (shared-object rivalry vs. status-proximity rivalry). Throughout, $`w_{ik}`$ denotes the prestige weight governing how much agent $`i`$ imitates agent $`k`$, while $`a_i(j)`$ denotes the attention weight governing how much of agent $`i`$'s mimetic pull is directed at target $`j`$. The four variants are the cells of a 2x2 design:

|  | Linear spread | Attentional concentration spread |
|---|---|---|
| **Object-rivalry source** | LM (baseline) | AC |
| **Status-rivalry source** | RL | RA |

This design allows us to attribute convergence effects to transmission character, hostility source, or their interaction. **Caveat:** the axes are not perfectly orthogonal. In RL and RA, rivalry dynamics alter prestige and influence weights via status updates, so the "source" dimension has indirect effects on the "spread" dimension. We return to this coupling in Section 4.6; the design nonetheless cleanly separates the primary mechanisms under test.

**LM: Linear Mimesis (baseline).** Agent *i*'s mimetic pull toward target *j* is a prestige-weighted average of neighbors' aggression toward *j*:

$$\text{pull}_i(j) = \frac{\sum_{k \in N(i)} w_{ik} \cdot \text{agg}_k(j)}{\sum_{k \in N(i)} w_{ik}}$$

Updated aggression:

$$\text{agg}_i(j) \leftarrow \alpha \cdot \text{agg}_i(j) + (1 - \alpha) \cdot \text{pull}_i(j)$$

where $`\alpha \in [0, 1]`$ is a global mimetic susceptibility parameter (note: higher $`\alpha`$ means *less* mimesis). At $`\alpha = 0`$, agents are fully mimetic; at $`\alpha = 1`$, fully autonomous. The same parameter governs desire imitation (Step 1), aggression imitation (Step 3), and rivalry-to-aggression conversion (Step 2), consistent with Girard's claim that rivalry is itself a mimetic phenomenon: without mimetic desire ($`\alpha \to 1`$), there is no shared desire, hence no acquisitive rivalry, hence no rivalry-generated aggression.

**AC: Attentional Concentration (Convex Redistribution).** Let $`h_i(j)`$ denote the prestige-weighted mean hostility toward target $`j`$ among $`i`$'s neighbors (computed identically to LM). Let $`H_i = \sum_j h_i(j)`$ be the total perceived neighborhood hostility. Agent $`i`$ constructs attention weights and mimetic pull as follows.

Define attention weights:

$$a_i(j) = \frac{h_i(j)^\gamma}{\sum_k h_i(k)^\gamma}$$

Each target's share of agent $`i`$'s mimetic attention is the target's perceived hostility raised to the power $`\gamma`$, normalized across all targets. Mimetic pull is then:

$$\text{pull}_i(j) = a_i(j) \cdot H_i$$

Agent $`i`$ adopts total mimetic pull equal to $`H_i`$, but distributes that pull across targets according to the convex attention weights.

Two identities characterize this operator.

*Throughput conservation.* Summing over targets:

$$\sum_j \text{pull}_i(j) = H_i$$

The L1 norm of agent $`i`$'s pull vector equals the total hostility it perceives among its neighbors. The spread step does not inflate or deflate this quantity; it redistributes a fixed per-agent throughput across targets. Note that this is a *per-agent, per-step* property (not a system-level conservation law): define total system hostility mass $`M_t = \sum_{i \neq j} A_i(j)`$. What the AC operator conserves is the magnitude of each agent's mimetic intake at each step, ensuring that, conditional on the perceived hostility landscape $`h_i`$ at a given step, varying $`\gamma`$ changes only the *distribution* of pull across targets, not the magnitude of mimetic intake. This is an operator-level property; the system-level hostility mass $`M_t`$ is not conserved, since rivalry sourcing, decay, and expulsions all alter it between steps.

*Ratio identity.* For any two targets $`a, b`$ with $`h_i(b) > 0`$:

$$\frac{\text{pull}_i(a)}{\text{pull}_i(b)} = \left(\frac{h_i(a)}{h_i(b)}\right)^\gamma$$

Relative mimetic pull between any two targets is the ratio of their perceived hostilities raised to the power $`\gamma`$. This captures one precise sense in which mimetic attraction could be "multiplicative" in Girard's terms: a difference in salience becomes an amplified difference in imitative focus. (Whether this is the *only* sense Girard intends is discussed in Section 4.2.) The identity is active only when multiple targets have nonzero perceived hostility -- i.e., the operator's convergence-producing behavior presupposes that the rivalry-sourcing step has already populated the aggression landscape with competing targets.

The operator is equivalent to a softmax (Boltzmann/Gibbs distribution) over log-hostilities: $`a_i(j) = \exp(\gamma \ln h_i(j)) / \sum_k \exp(\gamma \ln h_i(k))`$, with $`\gamma`$ playing the role of inverse temperature. The phase transition near $`\gamma = 1`$ (Section 3.2) corresponds to the transition from the high-temperature (dispersed) to low-temperature (concentrated) regime of this distribution. Appendix G tests the literal softmax operator as an alternative formalization, finding that the phase boundary is a generic property of convex conserving operators but that the power-law's scale invariance eliminates a lower (oscillation) boundary and is uniquely robust to population scaling.

The salience exponent $`\gamma`$ controls the qualitative character of redistribution. When $`\gamma = 1`$, the operator reduces to LM: attention weights are proportional to perceived hostility, and no redistribution occurs. When $`\gamma > 1`$, relative salience differences are amplified (convex redistribution). When $`\gamma < 1`$, differences are compressed (concave redistribution), actively dispersing hostility.

Without throughput conservation, a power transform would implicitly change the effective strength of mimesis by shrinking subunit signals (for $`x \in (0, 1)`$ and $`\gamma > 1`$, $`x^\gamma < x`$). The ablation in Section 3.3 confirms that this conservation is constitutive: removing it collapses the contagion channel entirely.

Updated aggression:

$$\text{agg}_i(j) \leftarrow \alpha \cdot \text{agg}_i(j) + (1 - \alpha) \cdot \text{pull}_i(j)$$

**RL: Rivalry + Linear.** Aggression is sourced from *status rivalry* rather than shared object-desire. Each agent has a status scalar (initialized near 0.5); agents in close status proximity generate mutual aggression, weighted toward upward rivalry. Received aggression degrades the target's status, creating a feedback loop. Aggression *spreads* via linear mimesis (as in LM).

**RA: Rivalry + Attention.** Same status-rivalry dynamics as RL, but aggression spreads via attentional concentration (as in AC).

### 2.3 Measurements

For each simulation run, we record: aggression Gini coefficient (inequality of received aggression), top-target share (fraction absorbed by the most-targeted agent), convergence ratio (top1/top2 received aggression), Shannon entropy of targeting, expulsion count and timing, catharsis (fractional tension drop post-expulsion), victim status at expulsion (rivalry variants), and modal-target agreement (fraction of living agents whose top aggression target is the modal target, excluding agents with total aggression below $`10^{-8}`$).

We define *convergence* as modal-target agreement >= 0.95 sustained for 10 consecutive steps. The theoretical ceiling is $`(N-1)/N = 0.98`$, since self-targeting is excluded. Under the parameterizations tested, the $`10^{-8}`$ exclusion threshold never binds during convergence episodes (all agents maintain nonzero aggression once the rivalry-sourcing step is active), so the effective ceiling is $`(N-1)/N`$ throughout. The 0.95 threshold is somewhat arbitrary; we verified that alternative thresholds of 0.90 and 0.98 do not meaningfully shift the gamma phase boundary identified in Section 3.2.

### 2.4 Metric Definitions

Let $`R(v) = \sum_{i \in \mathcal{L}_t, i \neq v} A_i(v)`$ be the total received aggression for agent $`v`$ at time $`t`$. Let $`\mathbf{r} = (R(v_1), \ldots, R(v_m))`$ be the vector of received aggression for all $`m = |\mathcal{L}_t|`$ living agents, sorted in ascending order.

**Aggression Gini coefficient:**

$$G = \frac{\sum_{i=1}^{m} (2i - m - 1) \cdot r_i}{m \cdot \sum_{i=1}^{m} r_i}$$

computed over living agents only. If $`\sum r_i = 0`$, $`G = 0`$.

**Top-target share:** $`R(v^*) / \sum_v R(v)`$, where $`v^* = \arg\max_v R(v)`$.

**Convergence ratio:** $`R(v^*) / R(v^{**})`$, where $`v^{**}`$ is the second-most-targeted living agent.

**Shannon entropy of targeting:** $`H = -\sum_v p_v \log_2 p_v`$, where $`p_v = R(v) / \sum_v R(v)`$, computed over living agents with $`R(v) > 0`$.

**Modal-target agreement:** Let $`T_i = \arg\max_j A_i(j)`$ be agent $`i`$'s top target. Let $`\mathcal{A}_t = {i \in \mathcal{L}_t : \sum_j A_i(j) > 10^{-8}}`$ be the set of agents with nontrivial aggression. The modal target is $`t^* = \text{mode}({T_i : i \in \mathcal{A}_t})`$. Modal-target agreement is $`|{i \in \mathcal{A}_t : T_i = t^*}| / |\mathcal{A}_t|`$.



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

*Table 1. Summary metrics across 10 runs per variant (seeds spaced by 1000), $`\alpha=0.15`$, salience exponent $`\gamma=2.0`$, 600 timesteps, expulsion threshold $`\tau=8.0`$. Gini, top-target share, and convergence ratio are time-averaged over all 600 timesteps within each run and then averaged across runs (note that this averaging mixes pre- and post-convergence regimes for AC and RA; peak and final-window values are reported in the no-expulsion gamma sweep, Table 2). "Expulsions" reports the mean number of expulsions per run. "Catharsis" reports the mean immediate fractional drop in total received aggression following an expulsion (averaged over expulsions within a run, then averaged across runs). Formally, catharsis for a single expulsion event at step $`t`$ is $`(M_{t^-} - M_{t^+}) / M_{t^-}`$, where $`M_{t^-} = \sum_{v} R(v)`$ is total received aggression immediately before expulsion and $`M_{t^+}`$ is total received aggression immediately after (i.e., after zeroing all aggression toward the expelled agent).*

Under the full dynamics with expulsions enabled at the default threshold ($`\tau = 8.0`$), no variant achieves sustained convergence (Table 1b). This confirms that at low thresholds, expulsion interrupts the convergence process before unanimity -- a finding developed in the threshold-regime analysis of Section 3.6.

| Variant   | Convergence Rate   | Median t₁   |   Fraction Steps Converged |   Mean Peak Modal |
|:----------|:-------------------|:------------|---------------------------:|------------------:|
| LM        | 0%                 | —           |                          0 |             0.249 |
| AC        | 0%                 | —           |                          0 |             0.468 |
| RL        | 0%                 | —           |                          0 |             0.315 |
| RA        | 0%                 | —           |                          0 |             0.564 |

*Table 1b. Convergence outcomes under full dynamics (expulsions enabled). Convergence is defined as modal-target agreement $`\ge 0.95`$ sustained for 10 consecutive steps. "Median $`t_1`$" reports the first timestep at which a qualifying episode begins (reported only when at least one run converges). "Fraction steps converged" is the share of timesteps lying inside qualifying convergence episodes. "Mean peak modal" is the runwise maximum modal-target agreement averaged across runs; it remains informative even when convergence rate is 0%.*

The transmission-character axis remains the dominant divider. Under linear transmission (LM, RL), hostility remains diffuse: top-target shares stay near $`\sim 0.04`$ and convergence ratios remain near 1.0. Introducing status rivalry under linear spread (RL) modestly increases inequality in received aggression (Mean Gini 0.223 vs 0.115 in LM), but does not produce strong single-target concentration or sustained coordination. By contrast, convex redistributive transmission (AC, RA) sharply concentrates hostility (Mean Gini 0.739--0.812; top-target share 0.310--0.436) and deepens catharsis (29.6--36.7%). Status rivalry under attentional concentration (RA vs AC) further increases concentration and catharsis, consistent with a marginalization feedback, but the redistributive transmission mechanism still does the majority of the convergence work.

With expulsions enabled at $`\tau=8`$, none of the variants satisfy our strict convergence criterion (modal agreement $`\ge 0.95`$ for 10 consecutive steps; Table 1b). Nevertheless, attention-based variants reach substantially higher peak modal agreement (AC 0.468; RA 0.564) than linear variants (LM 0.249; RL 0.315), showing transient movement toward unanimity even when expulsion interrupts sustained convergence.

![Figure 1. Convergence trajectories under linear vs. convex redistributive transmission (no expulsion, seed 42). Under linear mimesis (LM), modal-target agreement fluctuates around 0.12--0.18: the community generates hostility but never coordinates it. Under attentional concentration (AC), the mimetic snowball drives agreement from 0.06 to 0.98 by step 31. The RA variant (dashed) converges faster still, consistent with rivalry's potentiating role. The ceiling of 0.98 = (N-1)/N reflects the excluded self-targeting constraint.](../figures/fig1_trajectories.png)

Applying a convex transform without throughput conservation ($`\text{pull} = h^\gamma`$) does not produce convergence and in fact collapses the contagion channel by attenuating subunit signals (Section 3.3). Convergence requires the full redistributive operator: convex attention weights *plus* throughput conservation of perceived hostility.

### 3.2 The Effective Phase Boundary Near Linearity

To locate the boundary between diffuse crisis and scapegoat convergence, we performed a fine-grained sweep of the salience exponent $`\gamma`$ under the no-expulsion condition, isolating the convergence mechanism from the expulsion consequence rule.

| $`\gamma`$ | Peak Modal (sd) | Final Modal (sd) | Peak Gini | Med $`t_{95}`$ | Convergence Rate |
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

The effective phase boundary is sharp and narrowly localized.[^crit] For $`\gamma \leq 1.01`$, no runs converge. At $`\gamma = 1.02`$, convergence is rare and slow (1 of 8 runs; $`t_{95} = 421`$). By $`\gamma = 1.05`$, convergence is universal (8/8; median $`t_{95} = 116`$). The boundary lies in the interval [1.02, 1.05] at $`N = 50`$: a ~3% departure from purely proportional imitation separates crisis-without-convergence from robust scapegoating.

[^crit]: The critical-slowing pattern near the boundary -- median $`t_{95}`$ jumps from 116 at $`\gamma = 1.05`$ to 421 at $`\gamma = 1.02`$, a fourfold increase for a 3% change in the exponent -- is consistent with a phase-transition-like boundary, though we do not claim a continuous (second-order) phase transition on the basis of finite-horizon data. We use "effective phase boundary" throughout to denote the empirically observed transition interval, without claiming universality-class membership.

Above the boundary, coordination rapidly saturates: peak modal agreement reaches its ceiling of 0.98 for all $`\gamma \geq 1.05`$. But the inequality of hostility mass (peak Gini) continues to increase with $`\gamma`$ -- from 0.810 at $`\gamma = 1.05`$ to 0.972 at $`\gamma = 2.0`$. The exponent governs not only convergence speed but also the depth of hostility concentration.

Decreasing $`\gamma`$ below 1 reduces both peak modal agreement and peak Gini monotonically. Under the normalized attention weighting $`a_i(j) \propto h_i(j)^\gamma`$, values $`\gamma < 1`$ compress relative salience differences, actively pushing hostility toward uniformity.

#### Phase Boundary Invariance Across Community Size

To test whether the phase boundary is a property of the attention-allocation mechanism or an artifact of finite community size, we repeated the fine-grained gamma sweep at $`N = 100`$ and $`N = 200`$ with 20 seeds per condition and 800 steps (no expulsion). Mean degree scales with $`N`$ ($`k = 12`$ at $`N = 100`$, $`k = 20`$ at $`N = 200`$) to maintain comparable connectivity.

| $`N`$ | $`\gamma \leq 1.01`$ | $`\gamma = 1.02`$ | $`\gamma = 1.03`$ | $`\gamma \geq 1.04`$ |
|-----|---------------------|-----------------|-----------------|---------------------|
| 50  | 0%                  | 10%             | 90%             | 100%                |
| 100 | 0%                  | 0%              | 100%            | 100%                |
| 200 | 0%                  | 0%              | 100%            | 100%                |

*Table 2b. Convergence rate by gamma and community size. 20 seeds per condition, 800 steps, no expulsion.*

The boundary does not shift with $`N`$; it *sharpens*. At $`N = 50`$, a fuzzy zone spans $`\gamma \in [1.02, 1.04]`$: 10% convergence at 1.02, 90% at 1.03, 100% at 1.04. At $`N \geq 100`$, the transition collapses to a clean step function between 1.02 (0%) and 1.03 (100%). Convergence speed is also approximately $`N`$-independent: median $`t_{95}`$ at $`\gamma = 1.05`$ is 88, 98, and 102 for $`N = 50, 100, 200`$ respectively.

The $`N`$-invariance strengthens the interpretation that $`\gamma^*`$ is a property of the convex redistribution operator itself, not a finite-size artifact. The slight fuzziness at $`N = 50`$ is the expected signature of a small system near a critical threshold, where stochastic fluctuations occasionally tip individual runs across the boundary. At larger $`N`$, these fluctuations average out and the boundary sharpens.

This $`N`$-invariance is not a generic property of convex conserving operators. When the power-law is replaced by a normalized softmax operator (Appendix G), the convergence region takes the form of a finite temperature band that narrows monotonically with $`N`$ and vanishes entirely at $`N \geq 150`$. The power-law's scale invariance -- the fact that ratios $`h_i(a)/h_i(b)`$ are preserved under uniform rescaling of the hostility vector -- eliminates the argmax-oscillation failure mode that afflicts softmax at low temperatures, producing the open half-line $`[\gamma^*, \infty)`$ rather than a closed band. The $`N`$-invariant phase boundary reported here is therefore a consequence of scale invariance specifically, not of convexity in general.

We accordingly revise our characterization of the effective phase boundary from the $`N = 50`$ interval $`[1.02, 1.05]`$ to the $`N`$-invariant interval $`[1.02, 1.03]`$, noting that the upper bound represents essentially a point transition at $`N \geq 100`$.

#### Phase Boundary Robustness Across Parameters

The $`N`$-invariance results hold alpha and decay at defaults ($`\alpha = 0.15`$, $`\delta = 0.03`$). To test whether the boundary location is fragile to these choices, we swept alpha across $`\{0.05, 0.10, 0.15, 0.20, 0.30\}`$ and decay across $`\{0.01, 0.03, 0.05, 0.10\}`$ in a full 5x4 grid (10 seeds per condition, $`N = 50`$, 800 steps, no expulsion), measuring the gamma value at which convergence first reaches 100%.

| | $`\delta = 0.01`$ | $`\delta = 0.03`$ | $`\delta = 0.05`$ | $`\delta = 0.10`$ |
|---|---|---|---|---|
| $`\alpha = 0.05`$ | 1.01 | 1.03 | 1.05 | 1.10 |
| $`\alpha = 0.10`$ | 1.02 | 1.03 | 1.05 | 1.10 |
| $`\alpha = 0.15`$ | 1.02 | 1.03 | 1.05 | 1.10 |
| $`\alpha = 0.20`$ | 1.02 | 1.03 | 1.05 | 1.10 |
| $`\alpha = 0.30`$ | 1.02 | 1.04 | 1.08 | 1.25 |

*Table 2c. Phase boundary $`\gamma^*`$ (lowest gamma achieving 100% convergence in 10 seeds) across alpha and decay. $`N = 50`$, 800 steps, no expulsion. Produced by `exp3_param_sensitivity.py`.*

The boundary is nearly invariant to $`\alpha`$ for $`\alpha \leq 0.20`$: across the entire range from highly mimetic ($`\alpha = 0.05`$) to predominantly autonomous ($`\alpha = 0.20`$), $`\gamma^*`$ shifts by at most one grid increment. At $`\alpha = 0.30`$, the boundary shifts upward at high decay rates, consistent with a regime where mimetic throughput is too weak to overcome rapid dissipation. The boundary scales monotonically with decay rate -- higher decay requires stronger superlinearity to sustain the cascade against dissipation -- but the scaling is gentle: a ninefold increase in decay (0.01 to 0.09) shifts $`\gamma^*`$ by roughly 0.08 at typical alpha values. A cross-check at $`N = 200`$ with default parameters ($`\alpha = 0.15`$, $`\delta = 0.03`$) confirms $`\gamma^* = 1.03`$, identical to the $`N = 50`$ and $`N = 100`$ values (Table 2b).

This robustness indicates that $`\gamma > 1`$ is a structural property of convex redistribution under L1 conservation, not an artifact of parameter tuning. The boundary *location* depends weakly on the balance between mimetic intake and dissipation, but the *existence* of a sharp transition just above linearity is invariant across the parameter space tested.

![Figure 2. The effective phase boundary near linearity. (a) Convergence rate as a function of salience exponent $`\gamma`$, showing the sharp transition from 0% to 100% within the interval $`\gamma^* \in [1.02, 1.03]`$ (shaded). (b) Median time to convergence ($`t_{95}`$) for converging conditions, with min--max bars across 20 runs. The approximate $`N`$-independence of convergence speed ($`t_{95} \approx 90\text{--}102`$ at $`\gamma = 1.05`$ across all $`N`$) confirms that the mechanism, once triggered, operates on a timescale set by the convex redistribution operator rather than by community size.](../figures/fig2_phase_transition.png)

### 3.3 Operator Ablation

The AC convergence mechanism has two components: the convex power transform ($`h^\gamma`$ with $`\gamma > 1`$) and the redistributive normalization step ($`\div \sum_k h_i(k)^\gamma`$, $`\times \sum_k h_i(k)`$). This ablation isolates their respective contributions.

We define total aggression mass at time $`t`$ as $`M_t = \sum_{i \neq j} \text{agg}_i(t, j)`$.

**Condition 1: Linear baseline ($`\gamma = 1`$).** Hostility spreads but does not converge: peak Gini = 0.115, peak modal = 0.240. Total mass stabilizes at approximately 644, reflecting equilibrium between rivalry-sourcing and decay.

**Condition 2: Raw convex transform ($`h^\gamma`$, no normalization).** One might expect that a superlinear transform alone would produce convergence, since the exponent amplifies differences. It does not. Peak Gini = 0.115, peak modal = 0.113 -- *worse* than linear. Total mass collapses to approximately 9.1, a 98.6% reduction. The explanation is arithmetic: for $`x \in (0, 1)`$ and $`\gamma > 1`$, $`x^\gamma < x`$. Since hostility signals are typically subunit after prestige-weighted averaging, the power transform systematically attenuates the contagion channel. With decay, this attrition bleeds the system dry.[^clip]

**Condition 3: Full AC operator (convex redistribution, throughput conserved).** The normalization step rescales the sharpened weights so total mimetic pull equals total perceived hostility, preventing the attrition of Condition 2. Peak Gini = 0.972, peak modal = 0.980, total mass = 786.

| Condition | Description | Peak Gini | Peak Modal | Final Mass | Max Aggression |
|-----------|-------------|-----------|------------|------------|----------------|
| 1 | Linear baseline ($`\gamma = 1`$) | 0.115 | 0.240 | 644 | 0.646 |
| 2 | Raw $`h^\gamma`$ (no normalization) | 0.115 | 0.113 | 9.1 | 0.053 |
| 3 | Full AC (convex redistribution) | 0.972 | 0.980 | 786 | 19.1 |

*Table 3. Ablation results. All conditions: N=50, alpha=0.15, no expulsion, 600 steps, 8 runs. Conditions 2 and 3 use gamma=2.0.*

The convergence boundary is not "convexity alone"; it is convexity operating as a redistribution rule under throughput conservation.

[^clip]: Clamping $`h^\gamma`$ to $`[0, \text{max-val}]`$ produces results identical to Condition 2, confirming the collapse is due to signal attrition, not numerical overflow.

A further ablation (Appendix D) addresses the natural follow-up: what if the scaling problem is corrected without per-step redistribution? Replacing the AC operator with a fixed-scale convex map $`\text{pull}_i(j) = C \cdot h_i(j)^\gamma`$, with $`C`$ calibrated from a linear burn-in to match total hostility throughput, eliminates signal attrition but yields no stable convergence regime. Below a sharp explosion threshold $`C_{\mathrm{crit}} \approx 0.86 \, C_{\mathrm{cal}}`$, the system behaves identically to the linear baseline; above it, total tension diverges within 7--58 steps. That the explosion threshold falls *below* the calibrated constant means even matching average linear-regime throughput overshoots when applied to a sharpened distribution. The per-step throughput-conserving renormalization is constitutive: it bounds total mimetic pull at $`H_i`$ while redistributing that fixed budget toward the leading target, creating zero-sum cross-target competition that no fixed-scale map can replicate.

### 3.4 Robustness

At $`N = 50`$, convergence under convex redistribution is robust across network topology: Watts-Strogatz, Barabasi-Albert, Erdos-Renyi, and complete graphs all produce 100% convergence at $`\gamma = 2.0`$ (Table E1). Complete graphs yield the fastest convergence (median $`t_{95} = 6`$), consistent with Girard's account of undifferentiation crisis: the absence of structural differentiation accelerates the snowball. At $`N = 20`$, convergence is both universal (100%) and rapid (median $`t_{95} = 10`$), consistent with Girard's claim that the scapegoat mechanism operates most reliably in small archaic communities where "mimetic unanimity" encounters fewer structural impediments.

Convergence is sensitive to group size and mimetic susceptibility. At $`N = 100`$ (Watts-Strogatz, $`\alpha = 0.15`$), convergence drops to 62%. At $`\alpha = 0.50`$, convergence is 88%; at $`\alpha = 0.85`$ (85% autonomous aggression), convergence is 75--88% depending on $`\gamma`$. Extended runs (2400 steps) confirm that these are not time-horizon effects: the non-converging runs are genuinely metastable. The mechanism still concentrates hostility -- peak Gini exceeds 0.80 in all conditions -- but does not always achieve unanimity.

Analysis of the non-converging runs reveals a distinctive failure mode: **stable factional bifurcation**. Rather than collapsing onto a single victim, the attentional cascade splits into two competing scapegoat funnels, each commanding a community faction. Of seven non-converging runs across all conditions, six exhibit clear bifurcation: the two top targets absorb 77--89% of all hostility between them, the targets are graph-distant (3--5 hops, zero shared neighbors in all but one case), and the factions are spatially separated. One run ($`N = 100`$, seed 5042) shows a more fragmented pattern with only 34% top-two share, suggesting a third possible outcome -- disintegration -- under conditions of maximal community size. Table 5 summarizes.

| Condition | Non-conv. | Top-2 share | Faction split | Target dist | Shared $`\mathcal{N}`$ |
|-----------|-----------|-------------|---------------|-------------|----------------------|
| $`N = 100`$, $`\alpha = 0.15`$ | 3/8 | 34--89% | 87/11, 60/38, 55/43 | 2--5 | 0--1 |
| $`N = 50`$, $`\alpha = 0.50`$ | 1/8 | 78% | 30/18 | 4 | 0 |
| $`N = 50`$, $`\alpha = 0.85`$, $`\gamma = 1.5`$ | 1/8 | 78% | 27/21 | 4 | 0 |
| $`N = 50`$, $`\alpha = 0.85`$, $`\gamma = 2.0`$ | 2/8 | 82% | 39/9, 28/20 | 3--4 | 0 |

*Table 5. Structure of non-converging runs. "Top-2 share" is the fraction of total received aggression absorbed by the two most-targeted agents at step 600. "Faction split" counts agents whose primary target is victim 1 vs victim 2 (excluding targets themselves). "Shared $`\mathcal{N}`$" is the number of shared graph neighbors between the two top targets. All conditions use AC variant, no expulsion, 8 runs per condition.*

This is structurally distinct from incomplete convergence: it is *two convergences* that partition the community. We return to the theoretical significance of this outcome in Section 4.1. The bifurcation analysis above was conducted at $`N = 50\text{--}100`$ on small-world networks and represents a failure mode distinct from the topology-dependent effects that emerge at larger scales.

#### Topology Dependence at Scale

At $`N = 200`$ ($`\gamma = 2.0`$, 10 seeds, 5000 steps, unanimity-triggered expulsion with 5-step cooldown), topology effects emerge sharply.

| Topology | Mean Degree | Clustering | Med. Expulsions | Consumed | Conv. Rate | Peak Modal | Exhausted |
|---|---|---|---|---|---|---|---|
| Watts-Strogatz ($`k = 20`$) | 20.0 | 0.458 | 172 | 85.8% | 0% | 0.832 | 7/10 |
| Barabasi-Albert ($`m = 3`$) | 5.9 | 0.101 | 90 | 45.2% | 0% | 0.510 | 6/10 |
| Erdos-Renyi ($`p = k/(N-1)`$) | 19.8 | 0.102 | 164 | 82.2% | 0% | 0.995 | 9/10 |
| Complete | 199.0 | 1.000 | 197 | 98.5% | 100% | 0.995 | 10/10 |

*Table E1b. Topology robustness at $`N = 200`$. AC variant, $`\gamma = 2.0`$, unanimity-triggered expulsion (0.95 threshold, 5-step cooldown), 10 seeds, 5000 steps. Convergence defined as modal agreement $`\geq 0.95`$ sustained for 10 consecutive steps. Produced by `exp5_topology_n200.py`.*

Only the complete graph achieves formal convergence at $`N = 200`$ (10/10 seeds, peak modal 0.995). The Erdos-Renyi graph is the most instructive negative case: it matches the complete graph's peak modal agreement (0.995 in every seed) and consumes 82% of the population, but achieves 0% formal convergence. The mechanism reaches near-unanimity repeatedly but cannot sustain it for 10 consecutive steps. The explanation lies in the clustering coefficient: ER at this density has clustering $`C = 0.102`$ versus 0.458 for Watts-Strogatz. Without local clustering to stabilize the attentional cascade, the momentary consensus target rotates too rapidly -- the community achieves 99.5% agreement on *who to target* but the "who" changes before the 10-step criterion is met.

Barabasi-Albert presents a different failure mode. Degree heterogeneity (a few high-degree hubs connected to many low-degree peripherals) prevents the cascade from propagating uniformly: hubs dominate local dynamics but cannot synchronize across the network's degree-heterogeneous regions. Peak modal agreement is only 0.510 -- the mechanism never approaches unanimity. Only 45% of the population is consumed, versus 82--99% for the other topologies.

The implication for Girard's theory is that "all against one" is not guaranteed by convex redistribution alone. It requires either small $`N`$ (where all topologies are effectively dense) or sufficient connectivity for the mimetic cascade to saturate the population before the expulsion threshold is crossed. Sparse or heterogeneous networks at scale produce "most against a sequence of ones" -- high transient agreement that cycles rapidly through targets -- rather than the sustained unanimity Girard describes. This suggests a structural role for the "crisis of undifferentiation" Girard emphasizes: the dissolution of social differentiation functionally increases effective connectivity, creating complete-graph-like dynamics even in communities with heterogeneous structure. Ritual, spectacle, and shared narrative may serve the same homogenizing function at larger scales.

### 3.5 Catharsis Dynamics

Expulsion produces measurable tension reduction. Under the default parameterization ($`\gamma = 2.0`$, $`\tau = 8.0`$), the mean immediate fractional drop in total received aggression following an expulsion is 29.6% in AC and 36.7% in RA (Table 1), with attention-based variants producing substantially deeper catharsis than their linear counterparts (LM: 5.6%, RL: 6.3%). The system exhibits crisis-relief-reaccumulation cycles with clustered inter-expulsion intervals (runs of rapid expulsions separated by extended quiet periods). The immediate tension drop is partly arithmetic (removing the most-targeted agent eliminates their share of total received aggression), but the emergent finding is that tension does not immediately redirect: the attentional funnel requires time to reconstitute after losing its focal point, and this temporal gap constitutes the emergent catharsis. These metrics reflect the default threshold of 8.0; Section 3.6 shows qualitatively different cycle structures at higher thresholds, and Section 3.8 shows that the cycle topology depends on the distance from the phase boundary.

### 3.6 Expulsion Threshold and the Conditions for the Founding Murder

The expulsion threshold determines whether the community's capacity for collective violence exceeds its capacity for mimetic convergence. This ratio produces qualitatively distinct regimes.

In the no-expulsion condition, the AC mechanism drives modal agreement to 0.98 by approximately step 50, and total received aggression for the modal target stabilizes at roughly 700--900. This equilibrium ceiling bounds the threshold values at which expulsion can fire. We tested thresholds from 8 to 750 across 12 runs of 1500 steps and identified three regimes.

*Regime 1: Low threshold (8.0).* Expulsion fires at step 4, when modal agreement is approximately 0.13. The community acts before convergence has begun, producing rapid serial purges (~30 per run) with no unanimity and no sustained peace. Victims are selected by proximity to the threshold rather than collective consensus.

*Regime 2: High threshold (500).* Expulsion fires at approximately step 36, when modal agreement has reached 0.97. The community converges to near-total unanimity before acting: the victim is selected by the mimetic snowball, and the expulsion is singular rather than serial. This is the structural precondition Girard identifies for the founding murder -- total participation leaves no external vantage point from which to recognize the selection as arbitrary.

The founding murder produces genuine but transient peace. Modal agreement drops from 0.98 to approximately 0.06 post-expulsion, and total system tension collapses by roughly 95%. Modal agreement remains below 0.50 for a median of 17 steps. But the mimetic dynamics then reconstitute: agreement climbs back through 0.80 at step ~30 and reaches 0.98 by step ~50. The system produces 6 expulsions over 1500 steps in a rhythm of crisis-unanimity-expulsion-peace-reconvergence cycles -- qualitatively different from Regime 1's continuous grind, but not the permanent resolution Girard associates with the founding murder. Section 4.3 addresses what is missing.

*Regime 3: Threshold above equilibrium ceiling (750+).* The community achieves and sustains unanimous targeting but expulsion fires rarely or not at all. This is permanent crisis without resolution.

| Threshold | Expulsions | 1st Exp Step | Pre-Exp Modal | Peace (steps) | Reconverge $`t_{95}`$ | Gap to 2nd |
|-----------|-----------|-------------|--------------|--------------|-------------------|-----------|
| 8 | 29.8 | 4 | 0.13 | 0 | -- | 1 |
| 200 | 15.3 | 20 | 0.63 | 3 | 15 | 11 |
| 500 | 6.2 | 36 | 0.97 | 17 | 49 | 59 |
| 750 | 2.0 | 132 | 0.98 | 25 | -- | 260+ |

*Table 4. Post-expulsion dynamics across threshold regimes. 12 runs x 1500 steps, gamma = 2.0, alpha = 0.15. Peace = consecutive steps with modal agreement < 0.50 after first expulsion.*

The three regimes are produced by a single parameter controlling the ratio of violence capacity to convergence capacity. Girard's founding murder implicitly assumes Regime 2. The model makes this assumption explicit and shows it is non-trivial: if the threshold is too low, the result is serial violence without unanimity; if too high, unanimity without discharge. The founding murder occupies a specific parameter region.

![Figure 3. Expulsion threshold regimes. (a) At $`\tau = 8`$ (Regime 1), expulsion fires before convergence begins, producing rapid serial purges with no sustained unanimity. (b) At $`\tau = 500`$ (Regime 2), the community converges to near-total unanimity before each expulsion (red vertical lines). Post-expulsion, modal agreement collapses and a transient peace phase ensues before the mimetic snowball reconstitutes. The repeating sawtooth pattern -- crisis, unanimity, expulsion, peace, reconvergence -- corresponds to the cycle structure Girard describes, minus the institutional stabilization of the sacred (Section 4.3).](../figures/fig3_founding_murder.png)

### 3.7 The Arbitrariness and Endogenous Marginality of the Victim

In AC (no rivalry), victims are statistically indistinguishable from the general population across all measured network properties: degree centrality (0.125 vs 0.122, $`p = 0.10`$), betweenness centrality (0.037 vs 0.036, $`p = 0.38`$), clustering coefficient (0.388 vs 0.395, $`p = 0.54`$; Mann-Whitney $`U`$, all nonsignificant; $`n_{\text{victims}} = 288`$ across 10 runs). The victim's identity is a contingent outcome of the attentional cascade, not a structural property of the network. Initial symmetry-breaking is driven by stochastic fluctuations: small differences in early-timestep aggression patterns (arising from random desire initialization, prestige-weight asymmetries, and noise) give one target a transient salience advantage that the convex redistribution operator amplifies into a lock-in. Different random seeds produce different victims with no systematic network-structural bias.

In RA (rivalry + attention), victims have a mean status of 0.451 (95% CI [0.441, 0.460]) at expulsion, against a population mean of 0.487 -- a deficit of 0.036 ($`p < 0.001`$, Mann-Whitney $`U`$, one-sided; $`n_{\text{victims}} = 268`$). Although the deficit is modest in absolute terms, it is highly significant and entirely endogenous: status was initialized uniformly around 0.5. The victim's lower status is produced by the mechanism itself -- they were targeted, which degraded their status, which reduced their prestige and capacity to resist further targeting. The "signs of the victim" -- visible markers of difference that retrospectively justify the community's violence -- are *produced* by the mechanism, not presupposed by it.

In RL (rivalry + linear), the victim status deficit is larger in absolute terms (0.063, $`p < 0.001`$) but occurs against a background of globally collapsed status: mean population status under RL is 0.173 (vs 0.487 under RA), because diffuse aggression degrades all agents roughly equally. The endogenous *targeting* of status degradation -- selective damage to victims against a backdrop of otherwise-stable population status -- requires the convergence mechanism (convex redistribution). Rivalry provides the degradation channel; convex redistribution provides the selectivity.

### 3.8 Violence Topologies Under Unanimity-Triggered Expulsion

The threshold-regime analysis of Section 3.6 varies the community's *capacity* for collective violence. This section varies the *intensity* of the mimetic transmission mechanism itself by sweeping $`\gamma`$ above the phase boundary under a unanimity trigger (expulsion fires when modal agreement $`\geq 0.95`$, with a 5-step cooldown). This isolates the consequences of distance from the phase boundary for the topology of violence cycles, independent of an arbitrary accumulation threshold.

Three qualitatively distinct regimes emerge.

**Subcritical ($`\gamma < 1.03`$).** No expulsions occur. The community never achieves the unanimity required to trigger collective action. Hostility remains diffuse; the "crisis" is real but the snowball never completes. This is Girard's "crisis of undifferentiation" arrested before it reaches its resolution in the founding murder.

**Boundary grinding ($`\gamma \approx 1.03`$--$`1.10`$).** The snowball completes: unanimity is achieved and the victim is expelled. But the mimetic cascade reconstitutes almost instantly. Modal-target entropy analysis (Appendix H) quantifies the pre-convergence dynamics: at $`\gamma = 1.05`$, the modal target oscillates among potential victims for approximately 22 steps before locking in, with sliding-window entropy dropping from 1.32 to near zero. At $`\gamma = 1.10`$, lock-in takes 14 steps; at $`\gamma = 2.0`$, only 3. Once the cycle is established, however, the inter-expulsion gap reflects the cooldown rather than this transient: at $`N = 200`$, $`\gamma = 1.05`$, 95 expulsions in 1500 steps, reconvergence time of 1 step, effective cycle length of 7 steps (the 5-step cooldown plus 2 steps to reconverge). The community identifies a new victim essentially at the moment the cooldown expires. Peace duration is zero. At $`N = 500`$, $`\gamma = 1.05`$: 52 expulsions, same 7-step cycle gap, no deceleration. Given enough time, this regime grinds through approximately two-thirds of the population before the cascade's topology is sufficiently damaged to slow further targeting (Section 3.9).

| $`N`$ | $`\gamma`$ | Med. Expulsions | Med. Reconverge | Med. Cycle Gap | Pct. Consumed |
|-----|----------|-----------------|-----------------|----------------|---------------|
| 50  | 1.05     | 19              | 44              | 44             | 38%           |
| 100 | 1.05     | 39              | 14              | 14             | 39%           |
| 200 | 1.05     | 70              | 1               | 7              | 35%           |
| 500 | 1.05     | 69              | 1               | 7              | 14%           |
| 50  | 1.10     | 21              | 22              | 22             | 41%           |
| 100 | 1.10     | 56              | 10              | 10             | 56%           |
| 200 | 1.10     | 92              | 2               | 7              | 46%           |
| 500 | 1.10     | 75              | 4               | 7              | 15%           |

*Table 6. Boundary-grinding regime: unanimity-triggered expulsion near the phase boundary. 8 runs per condition, 1500 steps, unanimity threshold 0.95, cooldown 5. "Med. Reconverge" is the median number of steps after an expulsion before modal agreement returns to 0.95. "Med. Cycle Gap" is the median steps between consecutive expulsions. At $`N \geq 200`$, the cycle gap converges on 7 steps -- the cooldown plus minimal reconvergence time.*

**Supercritical bursts ($`\gamma \gg 1`$, e.g., 1.5--2.0).** Violence occurs in discrete *paired* expulsions separated by long natural peace intervals. At $`N = 500`$, $`\gamma = 2.0`$ (seed 42): 9 expulsions in 1500 steps. The trace reveals a characteristic structure:

```
Exp 1 t= 284, gap   7   ← pair
Exp 2 t= 291, gap 459   ← long peace
Exp 3 t= 750, gap   7   ← pair
Exp 4 t= 757, gap 337   ← long peace
Exp 5 t=1094, gap  14   ← triple
Exp 6 t=1108, gap   7
Exp 7 t=1115, gap 349   ← long peace
Exp 8 t=1464, gap   7   ← pair
Exp 9 t=1471             ← (sim ends)
```

The mechanism fires in bursts of 2--3, each burst separated by 300--450 steps of genuine peace (modal agreement below 0.50). The first expulsion within a burst disrupts the cascade enough that it immediately reconverges onto a nearby target (gap 7 = cooldown), fires again, and then the *combined* topological disruption of two removals is sufficient to break the cascade for hundreds of steps. The inter-burst peace intervals are not an artifact of the cooldown; they reflect the time required for the mimetic snowball to reconstitute across a network that has lost two adjacent focal nodes.

| $`N`$ | $`\gamma`$ | Med. Expulsions | Med. Peace | Med. Reconverge | Pct. Consumed |
|-----|----------|-----------------|------------|-----------------|---------------|
| 50  | 1.50     | 16              | 4          | 13              | 32%           |
| 100 | 1.50     | 48              | 3          | 12              | 48%           |
| 200 | 1.50     | 55              | 0          | 10              | 27%           |
| 500 | 1.50     | 15              | 1          | 8               | 3%$`^\dagger`$  |
| 50  | 2.00     | 9               | 3          | 10              | 17%           |
| 100 | 2.00     | 29              | 3          | 10              | 29%           |
| 200 | 2.00     | 30              | 1          | 4               | 15%           |
| 500 | 2.00     | 6               | 1          | 4               | 1.2%$`^\dagger`$ |

*Table 7. Supercritical burst regime: unanimity-triggered expulsion at high gamma. Same conditions as Table 6. Peace intervals emerge naturally from topology disruption and increase with both $`\gamma`$ and $`N`$. $`\dagger`$ The $`N = 500`$ consumed fractions (3% and 1.2%) are censored at 1500 steps. Extended runs (Section 3.9) show that the supercritical burst regime at $`N = 500`$ eventually consumes $`{\sim}64\%`$ of the population when run to completion.*

The paired-burst structure provides a mechanical substrate for Girard's concept of "doubles" -- the paired victims who appear in founding myths (Cain and Abel, Romulus and Remus, Eteocles and Polynices). In the model, the pairing is not psychological (the two victims do not fight each other) but structural: at high $`\gamma`$, the hostility landscape is so steep that when the primary victim is removed, the runner-up is already primed as the consensus target. The group's attention snaps to the second victim with no intervening deliberation. The model produces the *fact* of paired victims; myth, in Girard's account, provides the retrospective narrative that makes sense of it. Whether the mythological pattern of founding doubles reflects a structural feature of the underlying violence (as the model suggests) or is a purely narrative device is a question the model cannot resolve, but the mechanical availability of the pattern is worth noting.

### 3.9 Community Scale and Self-Exhaustion

At high $`\gamma`$, the paired-burst regime interacts with community size to produce a further qualitative distinction: at small $`N`$, the mimetic cascade permanently exhausts itself.

At $`N = 50`$, $`\gamma = 2.0`$ (20 seeds, 10,000 steps each): median 12 expulsions (24% consumed), last expulsion at median step 269, followed by a median 9,730 steps of silence -- no reconvergence, no further expulsions. Of 20 seeds, 18 show genuine self-exhaustion, 2 produce no expulsions at all (modal agreement never reaches 0.95), and zero show perpetual cycling. The expulsion count ranges from 0 to 19 (mean 10.0). Seed 46 is instructive: it shows a 732-step gap between its sixth and seventh expulsions -- long enough to appear exhausted at shorter time horizons -- before one final paired burst at steps 953--960 and then genuine permanent silence. Even the latest possible reconvergence self-terminates. The network topology is damaged sufficiently by the removal of ~12 focal nodes that the mimetic cascade cannot reconstitute. At $`N = 100`$, $`\gamma = 2.0`$ (single seed, 1,500 steps): 9 expulsions (9%), last at step 274, followed by 1,226 steps of silence -- consistent with self-exhaustion but not yet verified at multi-seed scale.

At larger $`N`$, self-exhaustion becomes progressively less reliable, but the fraction of the population consumed stabilizes at a characteristic value. We ran a systematic interpolation across $`N \in \{200, 300, 400, 500\}`$ at both $`\gamma = 1.5`$ and $`\gamma = 2.0`$ (20 seeds per condition, 5000 steps, unanimity-triggered expulsion).

| $`N`$ | $`\gamma`$ | Med. Expulsions | Pct. Consumed | Genuine Exhaustion | Censored | Med. Silence |
|---|---|---|---|---|---|---|
| 50 | 2.0 | 12 | 24% | 18/20 (90%) | 0/20 | 9,730 |
| 200 | 1.5 | 129 | 64.5% | 16/20 (80%) | 4/20 | 1,396 |
| 200 | 2.0 | 128 | 63.8% | 13/20 (65%) | 7/20 | 1,248 |
| 300 | 1.5 | 190 | 63.3% | 11/20 (55%) | 9/20 | 1,240 |
| 300 | 2.0 | 192 | 64.0% | 7/20 (35%) | 13/20 | 841 |
| 400 | 1.5 | 255 | 63.7% | 12/20 (60%) | 8/20 | 1,182 |
| 400 | 2.0 | 258 | 64.5% | 6/20 (30%) | 14/20 | 941 |
| 500 | 1.5 | 320 | 63.9% | 10/20 (50%) | 10/20 | 773 |
| 500 | 2.0 | 319 | 63.8% | 6/20 (30%) | 14/20 | 732 |

*Table 8. Self-exhaustion across community sizes. $`N = 50`$ results: 20 seeds, 10,000 steps, threshold-triggered expulsion ($`\tau = 8.0`$). $`N = 200\text{--}500`$ results: 20 seeds, 5,000 steps, unanimity-triggered expulsion (0.95 threshold, 5-step cooldown). "Genuine exhaustion" requires $`\geq 2000`$ steps of post-final-expulsion silence. "Censored" indicates the simulation ended before the 2000-step silence criterion could be evaluated. Produced by `self_exhaustion_interpolation.py`.*

Two patterns emerge. First, the consumed fraction converges to a narrow band around 64% for all $`N \geq 200`$, independent of both $`N`$ and $`\gamma`$. The range across all 160 runs at $`N \geq 200`$ is 62.3--66.2%, with the median at 64.0%. This is an emergent constant of the dynamics: no parameter was tuned to produce it. The mechanism consumes approximately two-thirds of the population before the accumulated topological damage -- the removal of cascade-sustaining nodes and the fragmentation of the network's mimetic pathways -- halts further convergence. The remaining one-third survives not because of any intrinsic property but because the network can no longer support the coordinated attention required for unanimity.

Second, the probability of genuine self-exhaustion declines continuously with $`N`$ and is lower at $`\gamma = 2.0`$ than at $`\gamma = 1.5`$. At $`N = 200`$, $`\gamma = 1.5`$: 80% of seeds exhaust genuinely. At $`N = 500`$, $`\gamma = 2.0`$: only 30% do, with the remainder still active (or in long inter-burst gaps) when the simulation ends at 5000 steps. The mechanism's self-correcting capacity weakens as the surviving population grows large enough to absorb topological damage and reconstitute the cascade. Crucially, no seeds at any condition show perpetual cycling -- the distinction is between genuine exhaustion and censoring (ambiguous), not between exhaustion and confirmed perpetual activity.

The $`N = 50`$ result (90% exhaustion, 24% consumed) differs from the $`N \geq 200`$ pattern (64% consumed) because the $`N = 50`$ runs used threshold-triggered rather than unanimity-triggered expulsion. Under threshold-triggered expulsion, agents are expelled before full unanimity, reducing the per-cycle damage and allowing the cascade to exhaust at a lower consumed fraction. The 64% consumed fraction is characteristic of the unanimity-triggered regime specifically.

The self-exhaustion phenomenon exists only in the supercritical burst regime ($`\gamma \gg 1`$). In the boundary-grinding regime ($`\gamma \approx 1.03`$--$`1.10`$), no self-exhaustion occurs at any $`N`$ tested: the cycle gap remains constant at 7 steps and the grinding continues indefinitely. The grinding regime's reconvergence is so rapid that topological damage from a single expulsion is repaired before it can accumulate across cycles.

### 3.10 The 2x2 Design at Community Scale

The baseline 2x2 results (Table 1) were obtained at $`N = 50`$ with threshold-triggered expulsion. To test whether the transmission-character dominance holds at scale, we repeated the full 2x2 design at $`N = 200`$ ($`\gamma = 2.0`$, $`k = 20`$, 20 seeds, 5000 steps, unanimity-triggered expulsion).

| Variant | Source | Spread | Med. Expulsions | Consumed | Conv. Rate | Peak Modal | Peak Gini | Exhausted | Med. Catharsis |
|---|---|---|---|---|---|---|---|---|---|
| LM | object | linear | 156 | 78.0% | 0% | 0.156 | 0.221 | 8/20 | 1.7% |
| AC | object | attention | 172 | 85.8% | 0% | 0.827 | 0.929 | 15/20 | 21.1% |
| RL | status | linear | 150 | 75.0% | 0% | 0.167 | 0.234 | 20/20 | 1.8% |
| RA | status | attention | 167 | 83.5% | 0% | 0.814 | 0.930 | 20/20 | 23.0% |

*Table 9. The 2x2 design at $`N = 200`$. 20 seeds, 5000 steps, unanimity-triggered expulsion. Produced by `exp4_2x2_n200.py`.*

The transmission-character axis remains the dominant divider at scale: attention-based variants (AC, RA) produce peak modal agreement of 0.81--0.83 and peak Gini of 0.93, while linear variants (LM, RL) remain at peak modal 0.16--0.17 and Gini 0.22--0.23. The gap between linear and attention variants is slightly wider at $`N = 200`$ than at $`N = 50`$, consistent with the phase boundary sharpening documented in Section 3.2.

However, no variant achieves formal convergence (0% across all four cells). The attention variants reach 80--94% peak modal agreement but cannot sustain 0.95 for 10 consecutive steps, because at $`N = 200`$ the unanimity-triggered expulsion preempts sustained convergence: the mechanism reaches near-unanimity, fires, and the resulting topological disruption prevents the 10-step sustained criterion from being met before the next cycle begins. This is not mechanism failure but convergence preempted by self-exhaustion -- a qualitative distinction from the linear variants, which never approach unanimity at any point. Peak modal agreement, rather than convergence rate, is the informative metric in the self-exhaustion regime.

### 3.11 The Founding Murder at Small Community Sizes

The self-exhaustion results (Section 3.9) and the 2x2 replication at $`N = 200`$ (Section 3.10) establish that mimetic violence becomes progressively more destructive as community size increases: at $`N = 50`$, 90% of runs self-exhaust after consuming 24% of the population; at $`N = 200\text{--}500`$, the mechanism consumes approximately 64% before halting. This section extends the analysis in the opposite direction, testing whether the founding murder is *generative* -- capable of producing the conditions for social reorganization rather than merely destroying the community -- at the small population sizes corresponding to primate and early hominid social groups.

#### 3.11.1 Adaptive Unanimity Threshold

Sections 3.8--3.10 use a fixed unanimity threshold of 0.95 (95% of surviving agents targeting the same victim). At $`N = 50`$, this requires 47 of 50 agents -- functionally "all but a few holdouts." At $`N = 5`$, however, 0.95 requires 4.75 agents, which rounds to 5 of 5 -- a condition strictly stronger than unanimity-minus-one. To preserve the phenomenological meaning of the threshold ("all but at most one holdout") across community sizes, we adopt an adaptive specification:

$`\theta(N) = \min\!\bigl(0.95,\; (N - 1)/N\bigr)`$

At $`N \geq 20`$, $`(N - 1)/N \geq 0.95`$, so $`\theta = 0.95`$ and all results in Sections 3.8--3.10 are unaffected. At smaller $`N`$: $`\theta(15) = 0.933`$, $`\theta(10) = 0.900`$, $`\theta(5) = 0.800`$. Each value operationalizes the same requirement -- agreement from all agents except at most one -- adjusted for the discrete granularity of small populations. All experiments in this section use the adaptive threshold with a 5-step cooldown, matching the specification in Section 3.8.

#### 3.11.2 Viability of the Founding Murder

We define a *viability index* for the founding murder: a simulation run is classified as "generative" if it satisfies three conditions simultaneously: (1) genuine self-exhaustion occurs (no expulsions for the final 2000+ steps), (2) less than 50% of the original population is consumed by expulsions, and (3) at least one expulsion occurs. A generative founding murder is one where the community enacts collective violence, the violence terminates itself, and a majority of the community survives to reorganize. The viability index is the fraction of seeds meeting all three criteria.

Table 10 reports the viability index for the two convex-redistribution variants (AC, RA) across $`N \in \{5, 10, 15, 20, 25, 30, 35, 40\}`$ and $`\gamma \in \{1.05, 1.5, 2.0\}`$ (20 seeds per condition, 5000 steps, unanimity-triggered expulsion with adaptive threshold).

| Variant | $`\gamma`$ | $`N = 5`$ | $`N = 10`$ | $`N = 15`$ | $`N = 20`$ | $`N = 25`$ | $`N = 30`$ | $`N = 35`$ | $`N = 40`$ |
|---------|----------|---------|----------|----------|----------|----------|----------|----------|----------|
| AC | 1.05 | 25% | 75% | 65% | 90% | 95% | 85% | 85% | 90% |
| AC | 1.50 | 0% | 0% | 55% | 60% | 90% | 85% | 95% | 95% |
| AC | 2.00 | 0% | 5% | 50% | 65% | 85% | 70% | 90% | 80% |
| RA | 1.05 | 0% | 25% | 85% | 85% | 60% | 80% | 90% | 80% |
| RA | 1.50 | 0% | 0% | 25% | 65% | 80% | 85% | 100% | 90% |
| RA | 2.00 | 0% | 0% | 30% | 75% | 80% | 95% | 90% | 65% |

*Table 10. Viability index for the founding murder at small community sizes. "Generative" requires genuine self-exhaustion, < 50% consumed, and at least one expulsion. AC = object-rivalry + convex redistribution; RA = status-rivalry + convex redistribution. 20 seeds per cell, 5000 steps, adaptive unanimity threshold, 5-step cooldown. Produced by `exp_small_n_viability.py`.*

Three patterns emerge. First, *the founding murder is almost never generative below $`N = 15`$.* At $`N = 5`$, the maximum viability across all conditions is 25% (AC, $`\gamma = 1.05`$), and most cells show 0%. The arithmetic is decisive: each expulsion removes 20% of a five-agent community, so two expulsions breach the 50% consumption threshold regardless of self-exhaustion timing. The community is too small to absorb the cost of its own collective violence. At $`N = 10`$, viability is bimodal: AC at $`\gamma = 1.05`$ achieves 75% (most seeds produce one or two expulsions and then exhaust), but at $`\gamma \geq 1.5`$ viability collapses to 0--5% because the unanimity-expulsion cycle churns through six to eight of ten agents before exhausting.

Second, *viability increases sharply between $`N = 15`$ and $`N = 25`$*, reaching 80--95% in most cells by $`N = 25`$. The transition reflects a threshold effect: as each expulsion becomes a smaller fraction of the population, the community can sustain the founding murder's violence while retaining a viable remnant. At $`N = 25`$, each expulsion removes 4% of the population; the mechanism typically produces four to eight expulsions (16--32% consumed) before exhausting, leaving the majority intact.

Third, there is a *$`\gamma \times N`$ interaction* that reverses at intermediate community sizes. At $`N \leq 10`$, higher $`\gamma`$ is destructive: sharper convergence produces faster cycling and more total expulsions before exhaustion. At $`N \geq 25`$, higher $`\gamma`$ is often protective: sharper convergence means fewer total expulsions are needed before the topological disruption accumulates sufficiently to halt the cascade. At $`N = 40`$, AC with $`\gamma = 1.05`$ produces a median 16 expulsions (38.8% consumed), while $`\gamma = 2.0`$ produces only 11 (27.5% consumed). Stronger convexity concentrates violence on fewer victims when the community is large enough to absorb each individual expulsion.

The linear variants (LM, RL) serve as a diagnostic control. At $`N = 5`$, the adaptive threshold ($`\theta = 0.800`$) can be reached by random fluctuation in modal agreement, producing occasional expulsions even under linear transmission. But at $`N \geq 15`$, linear variants produce zero expulsions uniformly: peak modal agreement falls well below the adaptive threshold (0.375 at $`N = 40`$), confirming that convex redistribution remains the necessary condition for unanimity at every community size tested.

#### 3.11.3 Phase Boundary at Small $`N`$

To test whether the phase boundary shifts at small community sizes, we swept $`\gamma`$ from 0.95 to 2.0 at each $`N \in \{5, 10, 15, 20, 25, 30, 35, 40\}`$ (AC variant, no expulsion, 20 seeds, 800 steps). Table 11 reports the lowest $`\gamma`$ at which $`\geq 50\%`$ of seeds achieve convergence (modal agreement $`\geq 0.95`$).

| $`N`$ | $`k`$ | $`\theta`$ | $`\gamma^*`$ |
|-----|-----|----------|------------|
| 5 | 4 | 0.800 | 1.03 |
| 10 | 6 | 0.900 | 1.03 |
| 15 | 6 | 0.933 | 1.05 |
| 20 | 6 | 0.950 | 1.04 |
| 25 | 6 | 0.950 | 1.03 |
| 30 | 6 | 0.950 | 1.03 |
| 35 | 6 | 0.950 | 1.03 |
| 40 | 6 | 0.950 | 1.03 |

*Table 11. Phase boundary at small community sizes. $`\gamma^*`$ is the lowest tested $`\gamma`$ at which $`\geq 50\%`$ of 20 seeds converge (modal agreement $`\geq 0.95`$) within 800 steps. AC variant, no expulsion. $`k`$ is the Watts-Strogatz mean degree, $`\theta`$ the adaptive unanimity threshold. Produced by `exp_small_n_phase_boundary.py`.*

The phase boundary remains in the narrow range $`\gamma^* \in [1.03, 1.05]`$ across all tested community sizes, extending the $`N`$-invariance documented in Section 3.2 downward by a full order of magnitude ($`N = 5\text{--}40`$ vs. $`N = 50\text{--}500`$). The convexity threshold is a property of the redistribution operator, not of the population.

One caveat: at $`N = 5`$, below-threshold convergence rates are elevated (35% at $`\gamma = 0.95`$, 40% at $`\gamma = 1.0`$) relative to larger $`N`$ ($`< 5\%`$ for $`N \geq 15`$). This reflects the low adaptive threshold ($`\theta = 0.800`$): with five agents, random fluctuation can produce four-of-five agreement without mimetic coordination. The jump to reliable convergence nonetheless occurs at $`\gamma = 1.03`$, so the boundary location is preserved even though below-threshold noise is higher.

#### 3.11.4 Network Structure and the Necessity of Imperfect Information

The founding murder's viability depends not only on community size but on network structure. Table 12 reports viability across four topologies at small $`N`$ (AC variant, $`\gamma = 2.0`$, 10 seeds, 5000 steps, adaptive unanimity threshold).

| Topology | $`N = 15`$ | $`N = 20`$ | $`N = 30`$ | $`N = 40`$ |
|----------|----------|----------|----------|----------|
| Watts-Strogatz | 70% | 70% | 80% | 90% |
| Barabasi-Albert | 90% | 90% | 100% | 100% |
| Erdos-Renyi | 70% | 90% | 90% | 100% |
| Complete | 0% | 0% | 0% | 0% |

*Table 12. Topology dependence of founding-murder viability at small $`N`$. AC variant, $`\gamma = 2.0`$, 10 seeds, 5000 steps, adaptive unanimity threshold. "Viability" defined as in Table 10 (genuine exhaustion, < 50% consumed, $`\geq 1`$ expulsion). Produced by `exp_small_n_topology.py`.*

Three findings are notable. First, all sparse topologies (Watts-Strogatz, Barabasi-Albert, Erdos-Renyi) support generative founding murder at rates of 70--100%, confirming that the mechanism is robust to network structure provided connectivity is incomplete. Second, the complete graph produces 0% viability at every $`N`$ tested. On a complete graph, every agent observes every other agent simultaneously; unanimity forms instantly, the expulsion fires, and the cascade reconverges equally instantly onto the next target. At $`N = 15`$ and $`N = 20`$, the complete graph produces perpetual cycling (still targeting at simulation end); at $`N = 30`$ and $`N = 40`$, it achieves convergence without exhaustion, consuming 86--95% of the community. The founding murder occurs, but it is purely destructive.

This constitutes a demarcation result: **imperfect information propagation -- the fact that mimetic contagion must traverse a network rather than arriving simultaneously -- is a necessary condition for the founding murder to be generative.** Network structure is not incidental to the mechanism; it is what allows the community to survive its own violence. The graduated propagation of accusation through social connections creates the temporal gap between one expulsion and the reconstitution of the next cascade -- the gap in which topological damage accumulates faster than the cascade can repair itself.

Third, the Barabasi-Albert topology (scale-free, hub-and-spoke) outperforms all other sparse topologies at every $`N`$ tested, achieving 90--100% viability. Scale-free networks, in which a few high-degree nodes connect to many low-degree peripherals, produce faster initial convergence (hubs serve as natural focal points for the attentional cascade) while simultaneously limiting the speed of reconvergence (the low-degree periphery propagates mimetic signals more slowly). Each expulsion removes a hub, inflicting disproportionate topological damage that extends the inter-cycle peace interval. We return to the implications of this finding in Section 4.4.

#### 3.11.5 Scaling Law Extension

Section 3.9 documented self-exhaustion timing at $`N = 50\text{--}500`$. The small-$`N`$ experiments extend the scaling law downward. For the AC variant at $`\gamma = 1.5`$, the power-law fit $`T_{\text{exhaust}} \sim c \cdot N^k`$ yields $`T_{\text{exhaust}} \approx 2.39 \cdot N^{1.324}`$ ($`R^2 = 0.951`$) across $`N = 15\text{--}100`$. At $`\gamma = 2.0`$: $`T_{\text{exhaust}} \approx 1.53 \cdot N^{1.397}`$ ($`R^2 = 0.934`$). Both exponents are consistent with the superlinear scaling expected from cumulative topological damage: exhaustion time grows faster than linearly with population because each additional agent adds both a potential victim and a potential cascade sustainer.

Below $`N = 15`$, the scaling law breaks down: exhaustion becomes unreliable at $`N = 10`$ (60--100% exhaustion rate depending on $`\gamma`$) and unstable at $`N = 5`$ (perpetual cycling in most seeds). The power-law regime and the viability window share a common lower bound at approximately $`N = 15`$.

---

## 4. Discussion

### 4.1 What the Model Specifies Beyond Girard

Girard correctly identified the two-phase structure (rivalry-driven hostility generation, then hostility-contagion-driven convergence), correctly predicted the emergent properties (arbitrariness and retrospective marginalization of the victim, cathartic relief), and correctly characterized the convergence mechanism as multiplicative. What the model adds is the identification of the precise formal property that produces convergence: convex redistribution of hostility under per-agent throughput conservation.

The ratio identity $`\text{pull}_i(a)/\text{pull}_i(b) = (h_i(a)/h_i(b))^\gamma`$ captures one sense in which mimetic attraction could be "multiplicative": relative salience differences are amplified by the exponent. But Girard's formulation -- "multiplies with the *number* of those polarized" -- also admits an interpretation involving increasing returns to group size or recruitment, which the AC operator does not directly model. What the operator *does* model is the finite-attention mechanism by which an individual, perceiving heterogeneous hostility among neighbors, disproportionately imitates the leading target. Whether Girard's "multiplies" refers to this individual-level salience amplification, to group-level recruitment dynamics, or to both, is a question the text underdetermines. Our contribution is to show that the individual-level mechanism alone suffices for convergence.

The ablation results (Section 3.3) reveal that the convergence boundary is not "convexity" generically but convexity operating as a *budget allocation rule*. The AC operator does not create hostility mass; it gives existing mass a direction. Raw convex amplification (Condition 2) destroys the contagion channel; fixed-scale correction (Appendix D) produces either baseline behavior or runaway explosion. Only per-step throughput-conserving redistribution creates the zero-sum cross-target competition that drives convergence. This aligns with Girard's phenomenology more precisely than a naive "amplification" reading: in Girard, mimetic crisis is already a high-energy field of undifferentiated violence; the scapegoat mechanism *organizes* that field into unanimity rather than intensifying it.

The 2x2 design clarifies the relative dynamical weight of the two phases: the AC mechanism accounts for the overwhelming majority of convergence, while rivalry contributes an additional ~8% Gini concentration and the endogenous marginality effect. Rivalry is a potentiator, not the primary driver. The model also reveals that minimal mimetic susceptibility suffices: even populations with 85% autonomous aggression produce scapegoats if the remaining 15% of mimetic transmission has convex redistributive character -- though at reduced rates, as discussed below.

#### Crisis Typology

The robustness analysis (Section 3.4) reveals that the model reproduces not just the scapegoat mechanism but a broader typology of crisis outcomes that Girard himself describes. Under conditions favoring convergence (small $`N`$, low $`\alpha`$), the model produces unanimity: the founding murder. Under conditions that impede convergence (large $`N`$, high $`\alpha`$), the model produces stable factional bifurcation: two competing scapegoat cascades that partition the community, each faction internally unanimous against its own victim. Girard treats both outcomes as possible consequences of the same dynamics. In *Violence and the Sacred*, he writes that "violence precedes either the division of an original group into two exogamous moieties, or the association of two groups of strangers" (Girard 1977, 228), and describes how "the interminable vengeance engulfing two rival tribes may be read as an obscure metaphor for vengeance that has been effectively shifted from the interior of the community to the exterior... the tribes have come to an agreement never to agree" (Girard 1977, 266). In the Oughourlian dialogue in *Things Hidden*, Girard acknowledges that unanimity is not inevitable: "It is possible to think that numerous human communities have disintegrated under the pressure of a violence that never led to the mechanism I have just described" (Girard 1987, 27).

The model's bifurcation regime maps onto the pre-resolution factional crisis Girard describes: rival doubles, symmetric antagonism, the "thousand individual conflicts" between "a thousand enemy brothers" that have not yet collapsed into "all against one" (*Violence and the Sacred*, 79). The implication is that larger or more autonomous communities require either stronger mimetic pressure or additional mechanisms -- category generalization, institutional channeling, or what Girard calls the "crisis of differences" that produces full undifferentiation -- to achieve the unanimity the founding murder presupposes. The model makes the boundary between these regimes quantitatively precise.

The topology experiments at $`N = 200`$ (Section 3.4) reveal additional failure modes beyond bifurcation. On Erdos-Renyi graphs with low clustering, the mechanism achieves near-unanimous momentary agreement (peak modal 0.995) but the consensus target rotates too rapidly for sustained convergence -- a "flickering unanimity" in which the community agrees on a victim but cannot hold the agreement long enough to act. On Barabasi-Albert graphs with degree heterogeneity, the cascade cannot propagate uniformly at all: peak modal agreement reaches only 0.51. These are structurally distinct from the factional bifurcation observed at $`N = 50\text{--}100`$ on small-world networks, where two stable scapegoat cascades partition the community. The full typology of non-convergence outcomes thus includes: (i) diffuse crisis without focusing (linear transmission), (ii) factional bifurcation (convex transmission, moderate $`N`$, small-world topology), (iii) flickering unanimity (convex transmission, large $`N`$, low-clustering topology), and (iv) cascade fragmentation (convex transmission, degree-heterogeneous topology).

### 4.2 Structural Analogies in the Empirical Attention Literature

The AC operator is formally a budget allocation rule -- fixed total perceived mass, convex reallocation among competing targets -- which is the mathematical backbone of finite-attention models. The cognitive infrastructure it assumes is empirically grounded. Hodas and Lerman (2014) find that the probability of sharing content scales with the *fraction* of contacts who have shared it, not the absolute count: a consequence of competition for finite attention that produces naturally superlinear concentration on popular items. Weng et al. (2012) demonstrate that competition for limited user attention, combined with network structure, suffices to produce heavy-tailed popularity distributions. Lorenz-Spreen et al. (2019) document accelerating collective attention dynamics across multiple domains, consistent with sharpening winner-take-all effects. These findings establish that finite attention, salience-driven filtering, and mimetic absorption of neighbors' priorities are empirically operative in the domain of content diffusion.

Whether the same dynamics operate in hostile targeting is a theoretical extrapolation. The most relevant bridge is Bauer, Cahlíková, Chytilová, and Želinský (2018), who demonstrate social contagion of ethnic hostility in a field experiment, establishing that hostility *is* contagious and differentially so for outgroup targets. However, Bauer et al. do not measure whether the adoption function is linear or superlinear in the fraction of hostile contacts -- exactly the distinction our model identifies as decisive.

An experimental design adapting Bauer et al.'s paradigm to measure the dose-response functional form of hostility adoption -- specifically, whether it is linear or superlinear in the fraction of hostile contacts -- would constitute a direct empirical test of the model's core mechanism. We develop this proposal and its complications in Section 4.6.

### 4.3 The Missing Sacred and the Structural Necessity of Cultural Elaboration

The unanimity-trigger experiments (Section 3.8) reveal that crossing the phase boundary does not uniformly produce "the founding murder." It produces three qualitatively distinct violence topologies, each corresponding to a different condition in Girard's theoretical apparatus, and each bearing a different relationship to the cultural structures Girard calls the sacred.

**The boundary-grinding regime and the origin of the sacred.** At gamma values just above the phase boundary ($`\gamma \approx 1.03`$--$`1.10`$), the mechanism *works* -- unanimity is achieved, the victim is expelled -- but the peace phase is zero. The mimetic cascade reconstitutes within a single timestep. The community passes from crisis to unanimity to expulsion to crisis without any interval in which social order could exist. Even in the grinding regime, however, the mechanism does not consume the entire population. Extended runs show that the cascade grinds through approximately 64% of the community before accumulated topological damage halts further targeting (Section 3.9). The sacred is needed not only to provide peace intervals but because the mechanism, left to run indefinitely, produces neither complete annihilation nor genuine resolution -- only a two-thirds casualty rate and a surviving remnant too fragmented to sustain further coordinated violence. A community trapped in this regime can do nothing except identify and expel victims in a continuous loop. This is the condition under which the sacred is not merely useful but structurally indispensable for survival. Prohibition -- the injunction against the behavior that precipitated the crisis -- functions as a brake on instantaneous reconvergence, buying time before the next cascade ignites. Ritual -- the controlled, scheduled repetition of the founding murder in symbolic form -- channels the reconvergence energy into a managed discharge rather than allowing it to find a new real victim the moment the cooldown expires.

**The supercritical burst regime and the raw material of ritual.** At high $`\gamma`$ ($`\geq 1.5`$), the violence topology changes. Discrete paired expulsions are separated by long natural peace intervals (300+ steps at $`N = 500`$). At $`N = 500`$ and $`\gamma = 2.0`$, only 30% of simulation runs show genuine self-exhaustion within 5000 steps; the remainder exhibit stable periodic burst patterns with long inter-burst intervals. The burst regime at large $`N`$ is predominantly perpetual rather than self-exhausting. The sacred did not create these intervals; they are a mechanical consequence of the topological damage inflicted by removing two adjacent focal nodes. But the intervals are stochastic (varying from 200 to 500 steps), unpredictable from the community's perspective, and the target of the next burst is determined by network topology at the moment of reconvergence -- essentially arbitrary from the inside. The sacred converts this stochastic pattern into a deterministic institution: ritual puts the violence on a calendar (predictability), designates in advance who will be sacrificed (target control), and limits the count (dosage). What mechanical periodicity provides is the empirical pattern -- periodic paroxysms of collective violence -- that the community retrospectively interprets and then deliberately manages. The sacred does not invent the periodicity; it domesticates it.

**The founding murder requires a phenomenological gap.** Both regimes produce unanimity and expulsion. But the founding murder, as Girard describes it, requires something more: the community must *notice* that peace followed the killing. In the boundary-grinding regime, there is nothing to notice -- the next crisis is already underway. In the supercritical burst regime, the peace intervals are long enough that the connection between the killing and the calm could, in principle, register. The entropy transient data (Appendix H) adds a further dimension: the pre-convergence oscillation phase -- during which the community's hostility oscillates among interchangeable potential victims, the condition Girard describes as "monstrous doubles" -- lasts approximately 18--22 steps near the boundary but only 3--5 steps at high $`\gamma`$. The founding murder requires not only a post-expulsion peace interval but a pre-convergence crisis intense enough, and brief enough, to produce the *experience* of sudden resolution rather than gradual drift. This suggests a constraint on the mechanism's parameter range: for the founding murder to be generative -- to produce the "double transference" in which the victim is retrospectively credited with both the crisis and its resolution -- the mimetic transmission intensity must be supercritical, not merely above the phase boundary. The sacred arises from the founding murder, and the founding murder requires a peace interval long enough for attribution to occur.

**What the model cannot produce.** In Girard's account, the "double transference" converts the founding murder into a generative institution: because the community was unanimous, no member recognizes the selection as arbitrary, and the victim is retrospectively attributed causal power over both crisis and resolution. This attribution requires representational capacities beyond mimetic imitation -- memory of the event, causal reasoning, intentional repetition -- that the model lacks and should lack. The model's failure to produce lasting peace is therefore a positive demarcation result: it identifies the boundary between what mimetic dynamics alone can generate (the raw cycle of crisis, unanimity, expulsion, transient peace, reconvergence) and what requires the cultural elaboration that Girard locates at the origin of human symbolic life. The sacred is the cultural technology that converts a stochastic, uncontrollable mechanical process into a predictable, manageable institutional one. The model shows why the raw material exists; Girard's theory explains why the technology was necessary.

Regime 3 of the threshold analysis (Section 3.6) -- unanimous hostility without discharge -- bears a structural resemblance to the condition Girard describes in *I See Satan Fall Like Lightning*, in which the scapegoat mechanism has been "revealed" but the community cannot resolve its crisis through other means. We note the parallel without claiming the model captures that condition's full phenomenology.

### 4.4 Community Scale and the Structural Necessity of the Sacred

The self-exhaustion results (Section 3.9) and small-$`N`$ analysis (Section 3.11) jointly identify a *viability window* for the founding murder: a range of community sizes within which mimetic violence is both mechanically available (the cascade achieves unanimity and expels) and generatively functional (the community survives the violence and can reorganize). Below the window ($`N < 15`$), each expulsion consumes too large a fraction of the population for the community to survive the mechanism's operation. Above the window ($`N > 100\text{--}200`$), the mechanism either fails to self-exhaust (boundary-grinding regime) or consumes approximately two-thirds of the population before halting (supercritical burst regime at extended timescales). The viability window falls at approximately $`N = 15\text{--}50`$: within this range, 65--95% of simulation runs produce genuine self-exhaustion with majority survival.

This window corresponds, at least in order of magnitude, to the community sizes characteristic of primate social organization and early hominid bands. Chimpanzee communities -- the closest living model for the ancestral hominid social unit -- comprise 40--80 individuals (Dunbar 1993). Hunter-gatherer bands typically range from 25 to 50 (Kelly 2013). At these scales, the model predicts that high-intensity mimetic crises are self-correcting: violence erupts, burns through a small fraction of the group, and stops without cultural management.

The topology finding (Section 3.11.4) adds a further dimension. The Barabasi-Albert (scale-free, hub-and-spoke) topology produces the highest founding-murder viability across all tested community sizes, outperforming Watts-Strogatz and Erdos-Renyi networks. Scale-free hub-and-spoke organization is precisely the structure observed in primate dominance hierarchies, in which a dominant individual occupies a high-connectivity node and subordinates maintain fewer lateral connections (de Waal 1982; Sueur et al. 2011). The model was not designed to favor any particular topology; the Barabasi-Albert graph was included as a robustness check. That the topology most closely resembling observed primate social structure produces the most favorable conditions for generative founding murder is an emergent alignment between the model's predictions and the ecological niche in which Girard's mechanism must operate.

The interpolation data (Table 8) make the upper transition quantitatively precise. Genuine self-exhaustion probability declines continuously: 90% at $`N = 50`$, 80% at $`N = 200`$ ($`\gamma = 1.5`$), 55% at $`N = 300`$, and 30% at $`N = 500`$ ($`\gamma = 2.0`$). The transition zone -- where exhaustion shifts from probable to improbable -- falls in the range $`N \approx 200\text{--}500`$, overlapping with the community sizes (Dunbar's number, $`{\sim}150`$, through mega-bands of $`{\sim}500`$) at which anthropologists locate the emergence of distinctly human symbolic and ritual organization. Meanwhile, the consumed fraction stabilizes at $`{\sim}64\%`$ regardless of $`N`$: the mechanism inflicts the same proportional damage whether the community has 200 or 500 members. What changes is whether the damage is sufficient to permanently halt the cascade.

The viability window thus identifies three regimes with distinct implications for the origin of the sacred. Below the window ($`N < 15`$): communities are too fragile for the founding murder to serve any social function -- the violence destroys the group. Within the window ($`N = 15\text{--}50`$): the founding murder is self-limiting and leaves a surviving majority that could, given the representational capacities the model lacks (Section 4.3), recognize the connection between the killing and the subsequent peace. Above the window ($`N > 200`$): the founding murder is mechanically available but destructive, consuming two-thirds of the community. The sacred -- prohibition, ritual, sacrificial substitution -- is structurally indispensable at this scale not merely because the violence does not stop on its own, but because when it does stop, the damage is catastrophic.

The claim is not that the model proves the sacred emerged at a specific group size. That is beyond what an agent-based model can establish. The claim is narrower: the model identifies a community-size window within which the scapegoat mechanism is both operative and survivable, and this window is consistent with the range at which anthropologists and primatologists locate both primate social organization and early hominid band sizes. The structural problem the model makes visible -- the transition from survivable to catastrophic mimetic violence -- is precisely the problem that Girard's theory of the sacred is designed to solve.

Dunbar (1993) argues that language evolved because groups needed to grow beyond the grooming limit ($`{\sim}50\text{--}80`$) -- grooming can maintain one relationship at a time, but speech addresses multiple listeners simultaneously, enabling groups of $`{\sim}150`$. Girard argues that the sacred -- which is, in his account, the origin of symbolism, prohibition, ritual, and ultimately language -- emerged from the founding murder. The model suggests a mechanism connecting these claims: as ecological pressures pushed community size beyond the range where mimetic violence was self-correcting, the founding murder stopped being a one-off cathartic event and started being the opening of an indefinite cycle. The selective pressure for cultural management of violence -- the sacred -- arose precisely at the scale where the mechanical self-correction failed.

### 4.5 Empirical Predictions

The model generates several testable predictions, ranging from directly accessible to requiring novel experimental designs.

**Prediction 1: Human mimetic transmission is supercritical.** If the model is correct, the parameter governing attentional concentration in hostile mimesis must lie above the phase boundary ($`\gamma > 1.03`$), and indeed well above it, since the founding murder requires peace intervals long enough for the double transference to occur (Section 4.3). The measurable proxy is whether attention to a target scales linearly or superlinearly with the number of people already attending to that target. Centola (2010) demonstrates that behavioral adoption in online networks requires reinforcement from multiple contacts -- a form of superlinear threshold consistent with this prediction. Social media pile-on dynamics (Bakshy et al. 2011) exhibit concentration patterns consistent with superlinear attention allocation. A direct measurement of the dose-response curve in the domain of collective hostility (rather than content adoption) remains to be conducted.

**Prediction 2: The phase boundary is universal.** The $`N`$-invariance of the phase boundary (Section 3.2) predicts that the critical threshold for scapegoat convergence should not depend on group size. If a controlled experiment identified a community size below which scapegoating does not occur despite identical mimetic transmission intensity, this would disconfirm the $`N`$-invariance finding.

**Prediction 3: Graduated self-exhaustion by community scale.** The model predicts a continuous decline in the probability of self-limiting violence as community size increases, not a binary threshold. Communities of $`{\sim}50`$ individuals experiencing intense mimetic crises should show self-terminating violence (90% probability) consuming roughly a quarter of the group. Communities of $`{\sim}200`$ should still show self-termination in the majority of cases but with a characteristic two-thirds casualty rate. Communities of $`{\sim}500`$ should show self-termination in only $`{\sim}30\%`$ of cases, with the remainder exhibiting perpetual periodic violence. The consumed fraction ($`{\sim}64\%`$) is predicted to be approximately scale-invariant above $`N \approx 200`$.

**Prediction 4: Topology-dependent convergence.** Communities with dense, homogeneous social connectivity should achieve unanimous scapegoating at larger scales than communities with sparse or heterogeneous connectivity. Specifically, the model predicts that degree-heterogeneous social networks (where a few individuals have disproportionately many connections) will resist scapegoat convergence even when mimetic transmission is strongly superlinear. This is testable against ethnographic data on violence patterns in societies with different network structures: egalitarian band societies (approximating homogeneous, dense local connectivity) versus hierarchical chiefdoms (approximating degree-heterogeneous networks).

**Prediction 5: Network topology modulates founding-murder viability.** The model predicts that scale-free (hub-and-spoke) social networks produce more viable founding murders than homogeneous networks at every community size. This generates a testable claim about primate social organization: species with more hierarchical (hub-and-spoke) dominance structures should exhibit more effective collective aggression resolution -- shorter conflict durations, fewer total casualties per episode, and longer post-conflict peace intervals -- than species with more egalitarian (homogeneous-degree) social networks. The complete-graph result adds a further prediction: communities in which social information is fully public (everyone observes everyone in real time) should show *less* effective violence resolution than communities with mediated information propagation, because the absence of propagation delay eliminates the temporal gap required for topological damage to accumulate.

### 4.6 Limitations, Objections, and Falsifiability

#### Objections

**Circularity.** A natural objection is that the model builds superlinearity into the transmission rule and then discovers that superlinearity produces convergence. The response is that the finding cuts in both directions. The *positive* result -- superlinear transmission produces convergence -- is indeed built into the functional form. The *negative* result -- linear transmission does not produce convergence, ever, under any parameterization tested -- is not. Linear mimesis (LM) was a serious candidate mechanism: if prestige-weighted averaging of neighbors' aggression sufficed for convergence, the model would have shown it. It does not. The phase boundary's sharpness and $`N`$-invariance are also not built in; they are emergent properties of the interaction between the convex redistribution operator and the network dynamics. Girard does not distinguish linear from superlinear transmission; the model does, and shows that the distinction is the formal boundary between crisis and scapegoating.

**Ecological validity.** The model's agents are nodes on a Watts-Strogatz graph with a power-law aggression-spread rule. Real human mimesis involves cognition, language, emotion, historical grievance, institutional structure, and cultural meaning -- none of which the model represents. The response is that the model tests a *structural* claim, not a realistic one. The question is whether the mechanism Girard describes -- mimetic transmission of hostility producing convergent targeting -- is mathematically coherent: whether it can, in principle, produce the outcome Girard predicts. The model is a proof of concept, not a simulation of an actual community. Its value lies in specifying the formal conditions under which Girard's predicted outcome obtains, not in reproducing any particular historical instance of scapegoating.

**Alternative mechanisms.** Real scapegoating may operate through rational coordination (joining the mob is individually safer than resisting it), authority (a leader designates the victim), structural position (marginalized groups are targeted because of pre-existing power differentials), or some combination. The model does not exclude these mechanisms; it shows that mimetic transmission is *sufficient* for convergence without requiring them. Girard's specific theoretical contribution is the mimetic account of convergence. The model tests that account and finds it formally viable. Whether mimetic transmission is the *actual* mechanism in any given historical case is an empirical question the model does not address.

**Overfitting.** With enough free parameters ($`\gamma`$, $`\alpha`$, network topology, threshold, $`N`$), one might worry that any behavior could be produced by tuning. The 2x2 design is the primary response: all four variants share identical parameters; only the mechanism (source x spread) varies. Convergence is produced by one specific combination (superlinear attention) and not others. The parameter sweep (Section 3.2) shows that convergence is robust across a wide range of $`\gamma`$ values above the boundary and absent across an equally wide range below it. The robustness analysis (Section 3.4) shows convergence across four network topologies and multiple susceptibility levels. The result is not fragile.

**Gamma as a free parameter.** The power-law functional form ($`h^\gamma`$) is a modeling choice, not a derivation from first principles. A critic could argue that the result is an artifact of this specific parameterization. Our response is twofold. First, the linear/superlinear distinction is the minimal structural claim: we do not commit to the specific functional form, only to the qualitative property that mimetic attraction toward a target grows faster than linearly with the target's perceived salience. Second, we have now tested an alternative convex conserving operator -- a normalized softmax (Boltzmann/Gibbs) with temperature parameter $`T`$ controlling sharpness (Appendix G). The softmax produces the same sharp upper boundary separating diffuse crisis from convergence, confirming that the phase transition is a generic property of the operator class. However, the softmax also exhibits a *lower* boundary (argmax oscillation at low $`T`$), producing a finite convergence band rather than the power-law's open half-line. This band narrows monotonically with population size and vanishes entirely at $`N \geq 150`$. The power-law's scale invariance -- which eliminates the lower boundary -- is therefore not merely convenient but necessary for the mechanism to operate at anthropologically relevant population sizes. The sharp, $`N`$-invariant phase boundary at $`\gamma^* \approx 1.03`$ is a consequence of scale invariance specifically, not of convexity in general.

#### Design Limitations

The model treats the transition from acquisitive to conflictual mimesis as structurally given rather than endogenous. A richer model might formalize the conditions under which agents shift from object-focused rivalry to objectless hostility-transmission. The model also lacks institutional or ritual structures that, in Girard's later work, prevent or channel mimetic crisis. The RL/RA status-prestige coupling means the 2x2 axes are not perfectly orthogonal; disentangling the rivalry-source mechanism from its indirect effects on influence structure is a natural extension. The model assumes a single community without external relations. The bifurcation outcome (Section 3.4) suggests that group-level scapegoating -- where hostility toward one member of a perceived category generalizes to others sharing that category -- requires a category-transfer mechanism the model lacks. Real-world instances (pogroms, ethnic cleansing) involve category structure absent from the model's individual-targeting dynamics.

#### Simulation-Length Censoring

Extended simulations (5000 steps, 20 seeds per condition) have largely resolved the simulation-length censoring concern flagged in earlier drafts. At $`N = 200`$, 65--80% of seeds show genuine exhaustion with post-final-expulsion silence exceeding 2000 steps; the remainder are censored but none show confirmed perpetual cycling. At $`N = 500`$, censoring remains an issue -- 50--70% of seeds are censored at 5000 steps, particularly at $`\gamma = 2.0`$ -- but the consistent consumed fraction ($`{\sim}64\%`$) across both exhausted and censored runs suggests that the mechanism's long-run behavior is similar in both cases: grind through two-thirds of the population, then either halt permanently or enter long quiescent periods punctuated by rare further bursts. Ultra-long runs at $`N = 500`$ (50,000 steps, 8 seeds) confirm 7/8 exhaustion at $`\gamma = 1.5`$ and 3/8 at $`\gamma = 2.0`$, though these runs used a non-standard degree parameter and should be treated as indicative rather than definitive pending replication with the adaptive $`k`$ specification used elsewhere.[^k-note]

[^k-note]: The ultra-long runs at $`N = 500`$ (`exp1_ultralong_n500.py`) used a fixed or differently-computed $`k`$ value. A rerun with the adaptive $`k = \max(6, \min(\lfloor 0.12N \rfloor, 20))`$ specification used in the interpolation experiments is planned.

**Convergence metrics in the self-exhaustion regime.** The 2x2 results at $`N = 200`$ (Table 9) reveal a metric limitation: the strict convergence criterion (modal agreement $`\geq 0.95`$ sustained for 10 steps) registers 0% convergence for all variants, including the attention-based variants that reach peak modal agreement of 0.81--0.94. This is because unanimity-triggered expulsion preempts the sustained-agreement criterion: the mechanism converges, fires, and disrupts the cascade before 10 consecutive steps of agreement can accumulate. This "convergence preempted by exhaustion" is qualitatively distinct from the linear variants' failure to converge at all (peak modal 0.16). Peak modal agreement is the more informative metric when self-exhaustion operates, and the transmission-character distinction remains the dominant axis by this measure.

#### Alternative Formalizations

"Attentional concentration" is one possible formalization of convex redistributive hostility-transmission. Threshold models, information-cascade models, or explicit "fascination" dynamics might produce convergence with different properties. The softmax comparison (Appendix G) confirms that the qualitative property -- budget-conserving convex reallocation -- matters more than the specific functional form: both operators produce a sharp boundary separating crisis from convergence. The operators differ in regime structure (open half-line vs. finite band) and in robustness to population scaling, with the power-law uniquely robust due to scale invariance. Whether threshold or cascade models produce yet different regime structures is a natural extension; the present results establish the baseline comparison between the two canonical convex forms.

#### Falsifiability

The model's core claim is that hostility convergence requires superlinear (convex redistributive) transmission. This would be disconfirmed by observation of scapegoating convergence in a population where hostility transmission is demonstrably linear in homogeneous transmission settings.

Two complications bear on empirical tractability. First, the most relevant experimental work -- Bauer et al. (2018) -- establishes hostility contagion but does not measure whether adoption is linear or superlinear in the fraction of hostile contacts. Second, St-Onge, Hebert-Dufresne, and Allard (2024) show that genuinely linear contagion produces apparent superlinearity in observed data when transmission settings are heterogeneous (varying group sizes, local rates, or contact patterns). This complicates falsification in both directions: apparent superlinearity in naturalistic data could be artifactual, and demonstrating genuinely linear transmission requires controlling for heterogeneity.

The falsifiability criterion must therefore be stated precisely. The model predicts that convergent scapegoating cannot emerge from transmission that is both (a) genuinely linear at the individual cognitive level and (b) operating in homogeneous transmission settings. The most promising experimental design would adapt Bauer et al.'s field-experiment paradigm to measure the dose-response curve of hostility adoption as a function of the *fraction* (not merely the presence) of hostile contacts, under controlled conditions where setting heterogeneity is minimized. Specifically: expose subjects to varying proportions of hostile confederates or primed peers, and test whether the probability of adopting hostile attitudes toward an outgroup target scales linearly or superlinearly with the hostile fraction. A linear dose-response under homogeneous conditions, combined with observed convergent scapegoating, would falsify the model. A superlinear dose-response would provide direct cognitive-level evidence for the mechanism the model formalizes.

---

## 5. Conclusion

Girard writes that "the power of mimetic attraction multiplies with the number of those polarized." We formalized that sentence and tested it. The formalization reveals that the multiplicative character of mimetic attraction in hostile contexts -- convex redistributive transmission, where each agent's fixed mimetic throughput is reallocated among targets by sharpened attention weights -- is, within this model family, the formal condition separating diffuse crisis from scapegoat convergence. Linear transmission produces crisis without resolution; convex redistributive transmission, with the effective phase boundary at $`\gamma^* \approx 1.03`$ and invariant across community sizes from 5 to 500 agents, produces convergence onto an arbitrary victim, cathartic tension reduction upon expulsion, and -- when combined with status-rivalry dynamics -- endogenous production of the "signs of the victim." The phase boundary is a generic property of convex conserving operators, confirmed by comparison with a softmax alternative (Appendix G), but the power-law's scale invariance is uniquely robust to population scaling -- the softmax convergence band vanishes at $`N \geq 150`$, whereas the power-law boundary is $`N`$-invariant. The mechanism is not amplification but organization: the operator does not create hostility mass; it focuses existing mass through zero-sum cross-target competition under per-agent throughput conservation.

Above the phase boundary, the model reveals a further structure that Girard's phenomenological account describes but does not formally distinguish. Near the boundary, the scapegoat mechanism grinds: it achieves unanimity and expels the victim, but reconverges instantly, producing relentless serial purges with no peace. Far above the boundary, it detonates: discrete paired expulsions shatter the mimetic cascade, producing long natural peace intervals before the next paroxysm. The grinding regime is where the sacred -- prohibition, ritual, sacrificial substitution -- is structurally indispensable: without cultural intervention, the community has no respite between crises. The burst regime is where the sacred becomes a technology of management rather than survival: it domesticates a stochastic pattern of periodic violence into a predictable institution. The founding murder's generative potential is confined to a viability window at approximately $`N = 15\text{--}50`$: below this range, each expulsion is too costly a fraction of the population; above it, the cascade either grinds indefinitely or consumes approximately two-thirds of the community before halting. Within the window, 65--95% of simulations produce self-exhaustion with majority survival -- a founding murder that is both mechanically operative and socially survivable. The viability window corresponds to primate and early hominid community sizes, and the network topology most favorable to generative founding murder (scale-free hub-and-spoke) corresponds to observed primate dominance hierarchies. At larger community sizes, the burst regime cycles indefinitely -- consuming a characteristic $`{\sim}64\%`$ of the population regardless of scale, an emergent constant of the unanimity-triggered dynamics. The threshold between self-exhaustion and perpetual cycling is consistent with the community-size range at which anthropologists locate the transition from primate social organization to distinctly human symbolic culture. At the network level, sustained unanimity requires dense or homogeneous connectivity: sparse and degree-heterogeneous networks produce high transient agreement without sustained convergence, suggesting that the "crisis of undifferentiation" Girard describes may function as a connectivity-homogenizing precondition for the founding murder.

Girard correctly identified the two-phase structure, predicted the emergent properties, and characterized the convergence mechanism as multiplicative. The model adds the demonstration that this multiplicative character, formalized as budget-conserving convex reallocation, is the precise formal boundary between crisis and scapegoating -- and that the same mechanism produces Girard's full typology of crisis outcomes: unanimity (the founding murder) in small, highly mimetic communities; stable factional bifurcation (moiety formation, externalized violence) in larger or more autonomous ones; and diffuse crisis without resolution under linear transmission. It reproduces the structural conditions under which the sacred becomes necessary and the conditions under which the violence, left to its own devices, resolves itself. The model demarcates where mimetic dynamics end and the institutional structures of the sacred must begin.

---

## References

Bakshy, E., Hofman, J. M., Mason, W. A., & Watts, D. J. (2011). Everyone's an influencer: Quantifying influence on Twitter. *Proceedings of the Fourth ACM International Conference on Web Search and Data Mining*, 65-74.

Bauer, M., Cahlíková, J., Chytilová, J., & Želinský, T. (2018). Social contagion of ethnic hostility. *Proceedings of the National Academy of Sciences*, 115(19), 4881-4886. https://doi.org/10.1073/pnas.1720317115

Centola, D. (2010). The spread of behavior in an online social network experiment. *Science*, 329(5996), 1194-1197.

de Waal, F. (1982). *Chimpanzee Politics: Power and Sex among Apes*. Jonathan Cape.

Dunbar, R. I. M. (1993). Coevolution of neocortical size, group size and language in humans. *Behavioral and Brain Sciences*, 16(4), 681-694.

Gardin, A. (2008). Complex mimetic systems. *Contagion: Journal of Violence, Mimesis, and Culture*, 15/16, 25-42.

Girard, R. (1965). *Deceit, Desire, and the Novel: Self and Other in Literary Structure*. Trans. Y. Freccero. Johns Hopkins University Press.

Girard, R. (1977). *Violence and the Sacred*. Trans. P. Gregory. Johns Hopkins University Press.

Girard, R. (1986). *The Scapegoat*. Trans. Y. Freccero. Johns Hopkins University Press.

Girard, R. (1987). *Things Hidden Since the Foundation of the World*. Trans. S. Bann and M. Metteer. Stanford University Press.

Girard, R. (2001). *I See Satan Fall Like Lightning*. Trans. J. G. Williams. Orbis Books.

Granovetter, M. (1978). Threshold models of collective behavior. *American Journal of Sociology*, 83(6), 1420-1443.

Hodas, N. O., & Lerman, K. (2014). The simple rules of social contagion. *Scientific Reports*, 4, 4343.

Kelly, R. L. (2013). *The Lifeways of Hunter-Gatherers: The Foraging Spectrum*. Cambridge University Press.

Lorenz-Spreen, P., Moensted, B. M., Hovel, P., & Lehmann, S. (2019). Accelerating dynamics of collective attention. *Nature Communications*, 10, 1759.

O'Higgins Norman, J., & Connolly, J. (2011). Mimetic theory and scapegoating in the age of cyberbullying. *Pastoral Care in Education*, 29(4), 287-300.

Paes, L. (2025). An agent-based model of scapegoating. Unpublished manuscript. [NetLogo model.]

Sack, G. A. (2021). Geometries of desire: A computational approach to Girardian mimetic theory. *Contagion: Journal of Violence, Mimesis, and Culture*, 28, 81-112.

Sueur, C., Petit, O., De Marco, A., Jacobs, A. T., Watanabe, K., & Thierry, B. (2011). A comparative network analysis of social style in macaques. *Animal Behaviour*, 82(4), 845-852.

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
| Adaptive unanimity threshold | $`\min(0.95, (N-1)/N)`$ | Used for $`N < 20`$ in Section 3.11; equivalent to 0.95 at $`N \geq 20`$ |
| Runs per condition | 10 (Tables 1, 1b, G1, G1b); 8 (Tables 2, 3, 5, D1, E1); 12 (Table 4); 20 (Table 2b, H1, H2); 8 (Tables 6, 7, 8); 20 (Table 10); 20 (Table 11); 10 (Tables 12, G2, G3) | Replications for summary statistics |

## Appendix B: Code Availability

All simulations are implemented in Python using NumPy and NetworkX. Source code, runner scripts, and figure-generation code are available at: https://github.com/maxwell-black/mimetic-desire-simulation (commit `1378c780bed316c7e9b9740acdc072b6902a9201`, tagged `v15`).

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

**Network.** A Watts-Strogatz graph $`G = (V, E)`$ with $`|V| = N`$, mean degree $`k`$, and rewiring probability $`p`$. Let $`\mathcal{N}(i)`$ denote the neighbors of $`i`$ in $`G`$.

**Prestige weights.** For each directed edge $`(i, k)`$ where $`\{i, k\} \in E`$, a base prestige weight $`w^0_{ik} \in [0.1, 1.0]`$ is drawn uniformly at random at initialization. Prestige is asymmetric: $`w^0_{ik} \neq w^0_{ki}`$ in general. For object-rivalry variants (LM, AC), the prestige weight $`w_{ik} = w^0_{ik}`$ is static. For status-rivalry variants (RL, RA), the effective prestige weight is status-dependent and recomputed each timestep:

$$w_{ik}(t) = w^0_{ik} \cdot (c_{\text{status}} + S_k(t))$$

where $`c_{\text{status}}`$ is a baseline floor ensuring that even zero-status agents retain some prestige influence. The prestige weight $`w_{ik}`$ governs how much agent $`i`$ imitates agent $`k`$.

**Desire vectors.** Each agent $`i`$ maintains $`D_i \in \mathbb{R}_{\geq 0}^{n_{\text{obj}}}`$, initialized $`D_i(o) \sim \text{Uniform}(0, 0.3)`$.

**Aggression vectors.** Each agent $`i`$ maintains $`A_i \in \mathbb{R}_{\geq 0}^{N}`$ with $`A_i(i) = 0`$ (no self-aggression) and $`A_i(j) = 0`$ for all dead agents $`j`$.

**Alive set.** $`\mathcal{L}_t \subseteq V`$ denotes agents alive at time $`t`$.

### C.3 Step 1: Desire Update

For each agent $`i \in \mathcal{L}_t`$:

$$D_i \leftarrow \alpha \cdot D_i + (1 - \alpha) \cdot \frac{\sum_{k \in \mathcal{N}(i) \cap \mathcal{L}_t} w_{ik} \cdot D_k}{\sum_{k \in \mathcal{N}(i) \cap \mathcal{L}_t} w_{ik}} + \epsilon_i$$

where $`\epsilon_i \sim \mathcal{N}(0, \sigma_{\text{noise}}^2)`$ elementwise, and the result is clamped to $`[0, \infty)`$.

**Edge case:** If agent $`i`$ has no living neighbors, $`D_i`$ is unchanged.

### C.4 Step 2: Aggression Source

#### Object-rivalry source (LM, AC)

For each pair $`(i, k)`$ where $`k \in \mathcal{N}(i) \cap \mathcal{L}_t`$:

$$A_i(k) \leftarrow A_i(k) + \rho \cdot (1 - \alpha) \cdot \frac{\text{SharedDesire}(i, k)}{d(i, k)}$$

where $`\rho`$ is the rivalry-to-aggression parameter, $`d(i, k) = \max(1, \text{shortest-path-length}(i, k))`$, and:

**Implementation note:** Because rivalry updates are applied only to network neighbors, $`d(i,k) = 1`$ in all simulations reported here and the distance factor has no effect. It is retained in the formalism for generality.

$$\text{SharedDesire}(i, k) = \sum_{o=1}^{n_{\text{riv}}} \min(D_i(o),\; D_k(o))$$

summing over rivalrous objects only.

#### Status-rivalry source (RL, RA)

Each agent $`i`$ has a status scalar $`S_i \in [0, 1]`$, initialized $`S_i \sim \text{Uniform}(0.4, 0.6)`$. For each pair $`(i, k)`$ with $`k \in \mathcal{N}(i) \cap \mathcal{L}_t`$:

$$A_i(k) \leftarrow A_i(k) + \rho_{\text{riv}} \cdot (1 - \alpha) \cdot \text{UpwardBias}(S_i, S_k) \cdot f(|S_i - S_k|)$$

where

$$f(\Delta S) = \exp\!\left(-\frac{\Delta S}{\sigma_S}\right), \qquad \text{UpwardBias}(S_i, S_k) = 1 + \beta_\uparrow \cdot \max(0,\; S_k - S_i)$$

$`f`$ is a decreasing function of status distance (agents in close status proximity generate more rivalry), $`\text{UpwardBias}`$ weights rivalry toward agents of equal or higher status, and the $`(1-\alpha)`$ factor ensures rivalry-generated aggression vanishes in the fully autonomous limit $`\alpha \to 1`$. Status is updated once per timestep after expulsion (Step 6, Section C.7a), creating a feedback loop: targeting degrades status, degraded status reduces prestige, reduced prestige reduces the target's capacity to resist further targeting.

### C.5 Step 3: Aggression Spread

#### LM and RL (linear spread)

For each agent $`i \in \mathcal{L}_t`$ and each living target $`j \neq i`$:

$$\text{pull}_i(j) = \frac{\sum_{k \in \mathcal{N}(i) \cap \mathcal{L}_t} w_{ik} \cdot A_k(j)}{\sum_{k \in \mathcal{N}(i) \cap \mathcal{L}_t} w_{ik}}$$

$$A_i(j) \leftarrow \alpha \cdot A_i(j) + (1-\alpha) \cdot \text{pull}_i(j)$$

#### AC and RA (attentional concentration spread)

For each agent $`i \in \mathcal{L}_t`$:

1. Compute perceived hostility landscape: $`h_i(j) = \frac{\sum_{k} w_{ik} A_k(j)}{\sum_{k} w_{ik}}`$ for each living $`j \neq i`$

2. Total perceived hostility: $`H_i = \sum_j h_i(j)`$

3. Attention weights: $`a_i(j) = h_i(j)^\gamma \;/\; \sum_k h_i(k)^\gamma`$

4. Mimetic pull: $`\text{pull}_i(j) = a_i(j) \cdot H_i`$

5. Update: $`A_i(j) \leftarrow \alpha \cdot A_i(j) + (1-\alpha) \cdot \text{pull}_i(j)`$

**Edge case:** If $`H_i = 0`$ or all $`h_i(j)`$ are equal (within numerical tolerance $`\varepsilon`$), agent $`i`$ applies uniform attention weights $`a_i(j) = 1/(n_{\text{targets}})`$.

### C.6 Step 4: Decay

For all $`i, j`$:

$$A_i(j) \leftarrow A_i(j) \cdot (1 - \delta)$$

### C.7 Step 5: Expulsion

Let $`R(v) = \sum_{i \in \mathcal{L}_t,\, i \neq v} A_i(v)`$. If $`R(v) \geq \tau`$ for any $`v \in \mathcal{L}_t`$:

1. Select $`v^* = \arg\max_v R(v)`$ (tie-breaking by lowest index).
2. Set $`v^*`$ to dead: $`\mathcal{L}_{t+1} = \mathcal{L}_t \setminus \{v^*\}`$.
3. Zero all aggression toward $`v^*`$: $`A_i(v^*) = 0`$ for all $`i`$.
4. Zero all aggression from $`v^*`$: $`A_{v^*}(j) = 0`$ for all $`j`$.

Only one agent is expelled per timestep (the maximally targeted).

#### C.7a Step 6: Status Update (RL, RA only)

Let $`\mathcal{L}'_t`$ denote the alive set *after* any expulsion in step 5. Let $`R(k) = \sum_{i \in \mathcal{L}'_t,\, i \neq k} A_i(k)`$ (recomputed post-expulsion). Let $`R_{\max} = \max_{k \in \mathcal{L}'_t} R(k)`$.

For each agent $`k \in \mathcal{L}'_t`$:

$$S_k \leftarrow \text{clamp}\!\left(S_k - \lambda \cdot \frac{R(k)}{\max(R_{\max},\; \varepsilon)},\; 0,\; 1\right)$$

where $`\lambda`$ is the status loss rate and $`\varepsilon = 10^{-12}`$ prevents division by zero. The normalization by $`R_{\max}`$ ensures that the maximally targeted agent loses status at rate $`\lambda`$ per step, with all other agents losing proportionally less. This occurs after expulsion so that expelled agents do not receive status updates and the post-expulsion hostility landscape (not the pre-expulsion one) determines status degradation.

### C.8 Parameter Summary

| Symbol | Parameter | Default |
|--------|-----------|---------|
| $`N`$ | Number of agents | 50 |
| $`k`$ | Mean degree (Watts-Strogatz) | 6 |
| $`p`$ | Rewiring probability | 0.15 |
| $`\alpha`$ | Global mimetic susceptibility (0 = fully mimetic, 1 = fully autonomous). | 0.15 |
| $`\gamma`$ | Salience exponent (AC, RA) | 2.0 |
| $`\rho`$ | Rivalry-to-aggression rate | 0.2 |
| $`\delta`$ | Aggression decay rate | 0.03 |
| $`\sigma_{\text{noise}}`$ | Desire noise std. dev. | 0.02 |
| $`\tau`$ | Expulsion threshold | 8.0 |
| $`\lambda`$ | Status loss rate (RL, RA) | 0.005 |
| $`\rho_{\text{riv}}`$ | Rivalry intensity (RL, RA) | 0.15 |
| $`\sigma_S`$ | Status proximity scale (RL, RA) | 0.10 |
| $`\beta_\uparrow`$ | Upward bias coefficient (RL, RA) | 1.0 |
| $`c_{\text{status}}`$ | Prestige status baseline (RL, RA) | 0.50 |
| $`\varepsilon`$ | Numerical floor | $`10^{-12}`$ |
| $`n_{\text{obj}}`$ | Total objects | 8 |
| $`n_{\text{riv}}`$ | Rivalrous objects | 5 |
| $`T`$ | Timesteps | 600 (baseline); extended runs use 5,000--50,000 |

## Appendix D: Fixed-Scale Convex Map Ablation

This appendix reports the fixed-scale ablation referenced in Section 3.3. We replace the AC operator's per-step throughput-conserving normalization with a fixed multiplicative constant:

$$\text{pull}_i(j) = C \cdot h_i(j)^\gamma$$

where $`C`$ is calibrated from a 100-step linear burn-in as $`C = \bar{H} / \overline{\sum_j h_j^\gamma}`$, matching mean total throughput between the fixed-scale and AC operators during the burn-in phase ($`C_{\text{cal}} \approx 3.94`$ at default parameters).

We swept $`C`$ from $`0.5 C_{\text{cal}}`$ to $`2.0 C_{\text{cal}}`$ in 20 increments across 8 runs of 600 steps (no expulsion, $`\gamma = 2.0`$, all other parameters at defaults).

| $`C / C_{\text{cal}}`$ | Peak Modal | Peak Gini | Diverged |
|---|---|---|---|
| 0.50 -- 0.82 | 0.103 | 0.13 -- 0.17 | 0/8 |
| 0.86 -- 0.97 | 0.29 -- 0.34 | 0.48 -- 0.58 | 3--4/8 |
| 1.05+ | 0.44 -- 0.68 | 0.88 -- 0.98 | 7--8/8 |

*Table D1. Fixed-scale ablation results by $`C / C_{\text{cal}}`$ band.*

Below a sharp explosion threshold $`C_{\text{crit}} \approx 0.86 \, C_{\text{cal}}`$, the system behaves like the linear baseline: peak modal agreement remains near 0.10 and peak Gini below 0.17. Above $`C_{\text{crit}}`$, total system tension diverges, with aggression values exceeding $`10^4`$ within 7--58 steps depending on the magnitude of overshoot ($`C / C_{\text{cal}} = 2.0`$: divergence in 7--9 steps; $`C / C_{\text{cal}} = 1.2`$: divergence in 17--58 steps). No intermediate regime of stable convergence exists.

That $`C_{\text{crit}} < C_{\text{cal}}`$ is itself significant: even a constant calibrated to match the linear regime's *average* throughput overshoots when applied to a sharpened distribution, because the convex transform concentrates pull on already-high targets while the fixed constant cannot adapt to the evolving hostility landscape.

The per-step throughput-conserving renormalization is therefore constitutive: it bounds total mimetic pull at $`H_i`$ while redistributing that fixed budget toward the leading target, creating zero-sum cross-target competition that no fixed-scale map can replicate. A fixed $`C`$ either underdrives the system (reproducing the linear baseline) or overdrives it (producing explosion), because it cannot adapt to the changing hostility landscape at each step.


## Appendix E: Robustness Grid

Table E1 reports convergence outcomes across the conditions referenced in Section 3.4. All runs use the AC variant with no expulsion, 600 steps, 8 runs per condition. Default parameters unless otherwise noted.

|Topology       |$`N`$|$`k`$|$`\alpha`$|$`\gamma`$|Conv. Rate|Median $`t_{95}`$|Peak Gini|
|---------------|---|---|--------|--------|----------|---------------|---------|
|Watts-Strogatz |20 |6  |0.15    |2.0     |100%      |10             |0.936    |
|Watts-Strogatz |50 |6  |0.15    |2.0     |100%      |29             |0.972    |
|Watts-Strogatz |100|6  |0.15    |2.0     |62%       |84             |0.973    |
|Barabasi-Albert|50 |3  |0.15    |2.0     |100%      |7              |0.973    |
|Erdos-Renyi    |50 |6  |0.15    |2.0     |100%      |9              |0.972    |
|Complete       |50 |49 |0.15    |2.0     |100%      |3              |0.972    |
|Watts-Strogatz |50 |6  |0.50    |2.0     |88%       |81             |0.941    |
|Watts-Strogatz |50 |6  |0.85    |1.5     |88%       |106            |0.804    |
|Watts-Strogatz |50 |6  |0.85    |2.0     |75%       |192            |0.822    |

*Table E1. Robustness of convergence across topologies, group sizes, and mimetic susceptibility levels. Convergence rate is the fraction of 8 runs achieving modal agreement $`\geq 0.95`$ within 600 steps. Median $`t_{95}`$ is computed over converging runs only. Extended runs (2400 steps) confirm that non-converging runs are genuinely metastable, not time-horizon artifacts. Results produced by `reproduce_table_e1.py` using `girard_2x2_v3.py` with graph-type support for all four topologies (Watts-Strogatz, Barabasi-Albert with $`m = 3`$, Erdos-Renyi with $`p = k/(N-1)`$, and complete graph).*

| Topology | Mean Degree | Clustering | Med. Expulsions | Consumed | Conv. Rate | Peak Modal | Exhausted |
|---|---|---|---|---|---|---|---|
| Watts-Strogatz ($`k = 20`$) | 20.0 | 0.458 | 172 | 85.8% | 0% | 0.832 | 7/10 |
| Barabasi-Albert ($`m = 3`$) | 5.9 | 0.101 | 90 | 45.2% | 0% | 0.510 | 6/10 |
| Erdos-Renyi ($`p = k/(N-1)`$) | 19.8 | 0.102 | 164 | 82.2% | 0% | 0.995 | 9/10 |
| Complete | 199.0 | 1.000 | 197 | 98.5% | 100% | 0.995 | 10/10 |

*Table E1b. Topology robustness at $`N = 200`$, corresponding to the analysis in Section 3.4. The qualitative shift from universal convergence at $`N = 50`$ (Table E1) to topology-dependent convergence at $`N = 200`$ is the central finding of the scaling analysis. AC variant, $`\gamma = 2.0`$, unanimity-triggered expulsion (0.95 threshold, 5-step cooldown), 10 seeds, 5000 steps. Produced by `exp5_topology_n200.py`.*

## Appendix F: Parameter Sensitivity at Small $`N`$

Table F1 reports the phase boundary $`\gamma^*`$ under varying $`(\alpha, d)`$ combinations at $`N = 10`$ and $`N = 20`$ (AC variant, no expulsion, 20 seeds, 800 steps, $`\gamma`$ swept from 0.95 to 2.0 in the same grid as Section 3.2).

| $`\alpha`$ | Decay | $`\gamma^*`$ ($`N = 10`$) | $`\gamma^*`$ ($`N = 20`$) |
|----------|-------|----------------------|----------------------|
| 0.05 | 0.01 | 1.00 | 1.02 |
| 0.05 | 0.03 | 1.00 | 1.04 |
| 0.05 | 0.05 | 1.02 | 1.05 |
| 0.05 | 0.10 | 1.05 | 1.10 |
| 0.10 | 0.01 | 1.00 | 1.02 |
| 0.10 | 0.03 | 1.00 | 1.04 |
| 0.10 | 0.05 | 1.02 | 1.08 |
| 0.10 | 0.10 | 1.04 | 1.10 |
| 0.15 | 0.01 | 1.00 | 1.02 |
| 0.15 | 0.03 | 1.00 | 1.04 |
| 0.15 | 0.05 | 1.02 | 1.08 |
| 0.15 | 0.10 | 1.05 | 1.10 |
| 0.20 | 0.01 | 1.00 | 1.02 |
| 0.20 | 0.03 | 1.00 | 1.04 |
| 0.20 | 0.05 | 1.00 | 1.08 |
| 0.20 | 0.10 | 1.08 | 1.25 |
| 0.30 | 0.01 | 1.00 | 1.02 |
| 0.30 | 0.03 | 1.00 | 1.04 |
| 0.30 | 0.05 | 1.00 | 1.08 |
| 0.30 | 0.10 | 1.08 | 1.25 |

*Table F1. Parameter sensitivity of the phase boundary at small $`N`$. $`\gamma^*`$ is the lowest tested $`\gamma`$ at which $`\geq 50\%`$ of seeds converge within 800 steps (10 seeds per condition). The phase boundary is more sensitive to the decay parameter at small $`N`$ than at $`N = 50`$ (Section 3.2), particularly at $`N = 20`$ with decay $`= 0.10`$, where the boundary shifts upward to $`\gamma^* = 1.10`$--$`1.25`$. At $`N = 10`$, the boundary is generally lower (median $`\gamma^* = 1.00`$) because convergence is easier with fewer agents to coordinate, though below-threshold noise is higher (see Section 3.11.3). Produced by `exp_small_n_param_sensitivity.py`.*


## Appendix G: Operator Universality -- Softmax Comparison

The power-law operator $`a_i(j) \propto h_i(j)^\gamma`$ is one member of the class of convex throughput-conserving operators. This appendix tests whether the phase boundary documented in Section 3.2 is specific to the power-law functional form or is a generic property of the operator class. We replace the power-law with a normalized softmax (Boltzmann/Gibbs) operator and test convergence across a sweep of the temperature parameter $`T`$ and across population sizes $`N`$.

### G.1 Softmax Operator Definition

The softmax operator replaces the power-law attention weights with exponential weights:

$$a_i(j) = \frac{\exp\!\bigl(\tilde{h}_i(j) / T\bigr)}{\sum_k \exp\!\bigl(\tilde{h}_i(k) / T\bigr)}$$

where $`\tilde{h}_i(j) = h_i(j) / \max_k h_i(k)`$ normalizes the perceived hostility vector to $`[0, 1]`$ before applying the softmax. This normalization is essential for a fair comparison: the power-law is inherently scale-invariant (ratios $`h_i(a)/h_i(b)`$ are preserved under uniform rescaling), whereas raw softmax sharpness depends on absolute hostility magnitudes, which grow over the simulation. Throughput is conserved identically to the AC operator: $`\text{pull}_i(j) = a_i(j) \cdot H_i`$, where $`H_i = \sum_j h_i(j)`$.

The temperature parameter $`T`$ controls sharpness. Low $`T`$ concentrates mass on the highest-hostility target (approaching argmax); high $`T`$ distributes mass uniformly (approaching the linear baseline). The parameter plays a role analogous to $`\gamma`$ in the power-law, but with inverted polarity: low $`T`$ corresponds to high $`\gamma`$.

### G.2 Softmax Sweep at $`N = 50`$

Table G1 reports convergence outcomes across a fine temperature grid ($`N = 50`$, 10 seeds per temperature, 800 steps, no expulsion). The reference power-law sweep at identical parameters is reproduced for comparison.

| $`T`$ | Peak Modal (sd) | Peak Gini | Med $`t_{95}`$ | Conv. Rate |
|-----|-----------------|-----------|---------------|------------|
| 0.05 | 0.514 (0.214) | 0.936 | 25 | 10% |
| 0.10 | 0.718 (0.247) | 0.952 | 20 | 30% |
| 0.15 | 0.638 (0.236) | 0.892 | 217 | 20% |
| 0.20 | 0.712 (0.291) | 0.708 | 39 | 50% |
| 0.25 | 0.858 (0.211) | 0.490 | 42 | 70% |
| 0.30 | 0.980 (0.000) | 0.326 | 50 | 100% |
| 0.40 | 0.980 (0.000) | 0.156 | 56 | 100% |
| 0.50 | 0.934 (0.138) | 0.106 | 71 | 90% |
| 0.55 | 0.980 (0.000) | 0.102 | 83 | 100% |
| 0.60 | 0.980 (0.000) | 0.100 | 117 | 100% |
| 0.65 | 0.762 (0.269) | 0.099 | 128 | 60% |
| 0.70 | 0.498 (0.287) | 0.097 | 59 | 10% |
| 0.80 | 0.258 (0.149) | 0.096 | -- | 0% |
| 1.00 | 0.142 (0.017) | 0.095 | -- | 0% |

*Table G1. Softmax operator sweep at $`N = 50`$. Convergence criterion: modal agreement $`\geq 0.95`$ for 10 consecutive steps. Produced by `exp_softmax_operator_sweep.py`.*

| $`\gamma`$ | Conv. Rate | Peak Modal |
|-----------|------------|------------|
| 0.95 | 0% | 0.182 |
| 1.00 | 0% | 0.250 |
| 1.02 | 10% | 0.500 |
| 1.03 | 80% | 0.968 |
| 1.05 | 100% | 0.980 |
| 1.10 | 100% | 0.980 |
| 2.00 | 100% | 0.980 |

*Table G1b. Reference power-law sweep at the same $`N`$, seeds, and step count. Produced by the same script.*

The softmax produces a convergence **band** $`T \in [0.20, 0.65]`$, bounded on both sides, whereas the power-law produces an open **half-line** $`\gamma \in [\sim\!1.03, \infty)`$. The two operators share an **upper boundary** (too flat $`\to`$ no convergence): both require sufficient convexity to concentrate mass on the leading target. This shared boundary confirms that the phase transition is a generic property of convex conserving operators, not an artifact of the power-law parameterization.

The asymmetry lies at the lower end. The power-law has no lower boundary: arbitrarily high $`\gamma`$ always converges. The softmax has a lower boundary at $`T \approx 0.20`$: below this temperature, convergence degrades despite extreme Gini concentration (peak Gini = 0.936 at $`T = 0.05`$). The failure mode is **argmax oscillation**: at very low $`T`$, the softmax approximates argmax, allocating nearly all mimetic pull to whichever target has the highest perceived hostility at that step. Small stochastic perturbations flip the argmax identity between steps, preventing stable lock-in. The power-law avoids this because it is multiplicatively scale-invariant: the ratio $`\text{pull}_i(a)/\text{pull}_i(b) = (h_i(a)/h_i(b))^\gamma`$ depends only on the hostility *ratio*, which is stable under perturbation even when $`\gamma`$ is large. The softmax, operating on normalized absolute values, is vulnerable to perturbations that change which target sits at the maximum.

### G.3 Band $`N`$-Dependence

The convergence band's dependence on population size is the critical test. If the band is $`N`$-invariant, the softmax is as viable as the power-law. If it narrows or vanishes, the power-law's scale invariance is necessary at scale.

Table G2 reports convergence rates across $`N`$ and $`T`$ (10 seeds per cell, steps scaled as $`\max(400, 10N)`$, no expulsion).

| $`N`$ | $`T = 0.05`$ | $`T = 0.15`$ | $`T = 0.20`$ | $`T = 0.30`$ | $`T = 0.40`$ | $`T = 0.50`$ | $`T = 0.60`$ | $`T = 0.65`$ | $`T = 0.70`$ | $`T = 0.80`$ |
|-----|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
| 10  | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| 20  | 70% | 60% | 60% | 80% | 100% | 100% | 100% | 100% | 100% | 50% |
| 30  | 50% | 80% | 70% | 100% | 100% | 100% | 100% | 90% | 80% | 10% |
| 50  | 10% | 20% | 50% | 100% | 100% | 80% | 100% | 60% | 10% | 0% |
| 75  | 0% | 30% | 30% | 20% | 70% | 80% | 30% | 10% | 0% | 0% |
| 100 | 0% | 0% | 10% | 40% | 30% | 60% | 10% | 0% | 0% | 0% |
| 150 | 0% | 0% | 0% | 0% | 20% | 0% | 0% | 0% | 0% | 0% |
| 200 | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |

*Table G2. Convergence rate heatmap: $`N`$ (rows) $`\times`$ $`T`$ (columns). Produced by `exp_softmax_band_n_dependence.py`.*

Phase boundaries (interpolated at 50% convergence threshold):

| $`N`$ | $`T_{\text{lower}}`$ | $`T_{\text{upper}}`$ | Band Width |
|-----|---------------------|---------------------|------------|
| 30 | 0.093 | 0.775 | 0.682 |
| 50 | 0.200 | 0.660 | 0.460 |
| 75 | 0.367 | 0.550 | 0.183 |
| 100 | 0.450 | 0.517 | 0.067 |
| 150 | -- | -- | 0 (no $`T`$ converges) |
| 200 | -- | -- | 0 (no $`T`$ converges) |

*Table G3. Softmax convergence band as a function of population size. Band width is monotonically decreasing. Both boundaries squeeze inward: $`T_{\text{lower}}`$ increases (argmax oscillation worsens with more targets) and $`T_{\text{upper}}`$ decreases (higher entropy of the uniform distribution requires sharper concentration to overcome). Produced by `exp_softmax_band_n_dependence.py`.*

The band narrows monotonically and vanishes at $`N \geq 150`$. The softmax operator cannot produce scapegoat convergence at population sizes above approximately 100, regardless of temperature. By contrast, the power-law phase boundary is $`N`$-invariant from $`N = 5`$ to $`N = 500`$ (Sections 3.2, 3.11.3).

The narrowing is driven by both boundaries. $`T_{\text{lower}}`$ rises because more potential targets increase the probability of stochastic argmax flipping at low temperatures. $`T_{\text{upper}}`$ falls because the entropy of the uniform distribution over $`N`$ targets grows as $`\log N`$: overcoming a more entropic baseline requires sharper concentration, but sharper concentration pushes into the oscillation zone. The two constraints squeeze the viable band from both sides until it collapses.

At $`N = 10`$, convergence is 0% across all temperatures, but peak modal agreement is 0.90 throughout the range $`T \in [0.08, 0.75]`$. This is an artifact of metric discretization, not mechanism failure: at $`N = 10`$, modal agreement takes values in $`\{k/10\}`$, and the convergence threshold of 0.95 requires $`k \geq 10`$ (perfect unanimity sustained for 10 steps). The mechanism produces robust 9-of-10 agreement but cannot sustain 10-of-10 for the requisite duration.[^n10]

[^n10]: This discretization effect is specific to the convergence *criterion*, not the mechanism. The adaptive threshold introduced in Section 3.11.1 ($`\theta(N) = \min(0.95, (N-1)/N)`$) would register $`N = 10`$ convergence at $`\theta = 0.90`$, but was not applied in these softmax experiments, which use the fixed 0.95 threshold for consistency with the power-law sweep.

### G.4 Interpretation

The comparison yields three findings. First, the phase boundary separating diffuse crisis from scapegoat convergence is a **generic property of convex throughput-conserving operators**, not an artifact of the power-law functional form. Both operators exhibit a sharp transition from 0% to 100% convergence within a narrow parameter interval. The qualitative claim -- that budget-conserving convex reallocation is the formal condition for convergence -- is confirmed as operator-independent.

Second, the power-law and softmax differ in **regime structure**. The power-law produces an open half-line $`[\gamma^*, \infty)`$: once the convexity threshold is crossed, convergence is robust at any degree of superlinearity. The softmax produces a closed band $`[T_{\text{lower}}, T_{\text{upper}}]`$: too little sharpness fails to concentrate, too much sharpness oscillates. The power-law's half-line structure is a direct consequence of its multiplicative scale invariance, which preserves ordinal rankings under arbitrary rescaling and thereby prevents the argmax-oscillation failure mode.

Third, the power-law's scale invariance is **necessary for the mechanism to operate at anthropologically relevant population sizes**. The softmax band vanishes at $`N \geq 150`$ -- well below the community sizes ($`N = 200\text{--}500`$) at which the most theoretically consequential dynamics (the grinding/burst transition, the self-exhaustion threshold, the viability window's upper bound) operate. An operator that fails at $`N = 150`$ cannot formalize a mechanism that must function at the scale of archaic human communities. The $`N`$-invariant phase boundary reported in Section 3.2 is not a trivial property of convexity; it is a substantive consequence of scale invariance that distinguishes the power-law from other members of the operator class.


## Appendix H: Modal-Target Entropy Transient

The violence topology analysis (Section 3.8) distinguishes boundary-grinding from supercritical-burst regimes by their inter-expulsion dynamics. This appendix examines the *pre-convergence* dynamics: the transient phase during which the community's hostility oscillates among potential victims before locking onto one. This phase corresponds to Girard's description of "monstrous doubles" -- interchangeable antagonists whose identities have not yet crystallized into a single victim.

### H.1 Method

For each simulation run ($`N = 50`$, 20 seeds per $`\gamma`$, 400 steps, no expulsion), we record the modal target identity at each step and compute two sliding-window statistics (window width $`W = 15`$):

*Sliding-window entropy.* Shannon entropy (base 2) of the modal-target identity sequence within each window. High entropy indicates the modal target is switching among multiple candidates; zero entropy indicates stable lock-in.

*Settle time.* The first step at which the mean sliding-window entropy drops below 0.5 and remains below 0.5 for 10 consecutive steps. This operationalizes the moment at which oscillation among "monstrous doubles" resolves into a stable scapegoat.

### H.2 Results

Table H1 reports convergence rates, entropy statistics, and settle times across $`\gamma`$ values spanning the sub-threshold control ($`\gamma = 0.95, 1.00`$), the phase boundary ($`\gamma = 1.03`$--$`1.10`$), and the deep supercritical regime ($`\gamma = 1.25`$--$`2.00`$).

| $`\gamma`$ | Conv. Rate | Early Entropy | Late Entropy | Settle Step |
|-----------|------------|---------------|--------------|-------------|
| 0.95 | 0% | 0.581 | 0.435 | 45 |
| 1.00 | 0% | 0.539 | 0.240 | 15 |
| 1.03 | 70% | 0.522 | 0.040 | 18 |
| 1.05 | 100% | 0.551 | 0.011 | 22 |
| 1.08 | 100% | 0.532 | 0.000 | 20 |
| 1.10 | 100% | 0.468 | 0.000 | 14 |
| 1.15 | 100% | 0.431 | 0.000 | 16 |
| 1.25 | 100% | 0.277 | 0.000 | 9 |
| 1.50 | 100% | 0.176 | 0.005 | 5 |
| 2.00 | 90% | 0.122 | 0.000 | 3 |

*Table H1. Modal-target entropy transient. "Early Entropy" is the mean sliding-window entropy over steps 5--30; "Late Entropy" over steps 100--200. "Settle Step" is defined as in Section H.1. 20 seeds per $`\gamma`$, $`N = 50`$, 400 steps, no expulsion. Produced by `exp_modal_entropy_transient.py`.*

The entropy trajectory reveals the transient structure directly. Table H2 reports mean entropy at 25-step intervals.

| $`\gamma`$ | $`t = 0`$ | $`t = 25`$ | $`t = 50`$ | $`t = 75`$ | $`t = 100`$ | $`t = 150`$ | $`t = 200`$ |
|-----------|---------|----------|----------|----------|-----------|-----------|-----------|
| 0.95 | 1.212 | 0.558 | 0.397 | 0.419 | 0.381 | 0.445 | 0.418 |
| 1.00 | 1.272 | 0.473 | 0.354 | 0.304 | 0.222 | 0.241 | 0.210 |
| 1.03 | 1.308 | 0.366 | 0.131 | 0.155 | 0.036 | 0.050 | 0.000 |
| 1.05 | 1.323 | 0.402 | 0.109 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1.08 | 1.351 | 0.267 | 0.092 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1.10 | 1.315 | 0.296 | 0.042 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1.25 | 1.263 | 0.112 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1.50 | 1.090 | 0.077 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2.00 | 0.988 | 0.092 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

*Table H2. Entropy trajectories (mean over 20 seeds, sampled every 25 steps). All runs begin at high entropy ($`{\sim}1.0\text{--}1.3`$) reflecting the initially random hostility landscape. The decay to zero -- the resolution of the "monstrous doubles" into a single victim -- is progressively faster at higher $`\gamma`$. Produced by `exp_modal_entropy_transient.py`.*

### H.3 Interpretation

Three patterns are notable.

First, the **settle time decreases monotonically with $`\gamma`$** (with minor noise): 22 steps at $`\gamma = 1.05`$, 14 at $`\gamma = 1.10`$, 9 at $`\gamma = 1.25`$, 3 at $`\gamma = 2.00`$. Higher superlinearity shortens the pre-convergence crisis, consistent with Girard's characterization of the scapegoat mechanism as self-accelerating. The oscillation phase is not a discrete regime that switches off at some threshold; it is a continuous gradient in crisis duration that compresses toward zero as the convex redistribution operator sharpens.

Second, the **early-phase entropy decreases with $`\gamma`$**: 0.551 at $`\gamma = 1.05`$ versus 0.122 at $`\gamma = 2.00`$. At high $`\gamma`$, even the initial oscillation is muted -- the hostility landscape is steep enough from the first steps that few targets are ever serious contenders. At near-boundary $`\gamma`$, the initial landscape is flatter and more targets compete, producing a genuine period of interchangeable potential victims before one emerges as the attractor.

Third, the **sub-threshold controls ($`\gamma = 0.95, 1.00`$) show elevated entropy throughout** the simulation. At $`\gamma = 0.95`$, late entropy is 0.435 -- the modal target never stabilizes. At $`\gamma = 1.00`$, late entropy drops to 0.240 but remains well above zero, and the settle step of 15 reflects a partial reduction in volatility that never reaches lock-in. The transition from persistent oscillation ($`\gamma \leq 1.00`$) to eventual lock-in ($`\gamma \geq 1.03`$) is the entropy-space signature of the phase boundary.

The transient oscillation phase provides a quantitative proxy for the duration of Girard's "mimetic crisis" -- the period during which "the monstrous double now takes the place of those objects that held the attention of the antagonists" (*Violence and the Sacred*, 161) and the community has not yet collapsed its diffuse hostility onto a single victim. The settle time measures how long the community dwells in the undifferentiated state before the scapegoat mechanism resolves it. Near the phase boundary, this dwelling time is longest -- the mechanism barely overcomes the entropic pull toward diffusion -- and the crisis is most prolonged. Deep in the supercritical regime, resolution is nearly instantaneous: the victim is identified within a few steps. The phenomenological gap required for the founding murder (Section 4.3) thus has two temporal components: a pre-convergence oscillation phase (measured here) and a post-expulsion peace phase (measured in Section 3.8). The founding murder requires both to be of sufficient duration for the community to experience the sequence crisis $`\to`$ resolution $`\to`$ peace as a coherent event attributable to the victim.
