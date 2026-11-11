# Reading list

An annotated path into the literature behind the review, for a reader with a quantum-mechanics
PhD and machine-learning experience but no background in chip manufacturing. Keys refer to
`references.bib`. Read Tier 1 first; it is enough to follow the whole review. Tier 2 is needed to
work on the open problems (§11 of the review). Tier 3 is depth for whoever owns a given problem.

Entries the bibliography marks `verify` were compiled from memory; check details before citing.

## 1. Superconducting circuits and circuit QED

| Tier | Key | Why read it |
|---|---|---|
| 1 | `krantz2019` | The engineer's guide: transmons, couplers, gates, readout and noise in one place. Start here. |
| 1 | `blais2021` | Definitive circuit-QED review; the dispersive regime, Purcell effect and readout physics used throughout §3. |
| 2 | `koch2007` | Origin of the transmon; the \(E_J/E_C\) trade-off and the charge-dispersion formula (eq. 4). |
| 2 | `vool2017` | Clean derivation of circuit quantisation from a Lagrangian; the basis of eq. 1. |
| 2 | `rasmussen2021` | Worked examples of quantising real circuits; good for building intuition quickly. |
| 3 | `devoret1997` | The original Les Houches lectures on quantum circuits. |
| 3 | `manucharyan2009`, `nguyen2019` | Fluxonium, now part of Google's roadmap through Atlantic Quantum. |
| 3 | `rigetti2010`, `sheldon2016`, `yan2018` | Cross-resonance gates and tunable couplers: why collisions and ZZ matter. |

## 2. From layout to Hamiltonian

| Tier | Key | Why read it |
|---|---|---|
| 1 | `minev2021epr` | Energy-participation quantisation, the method behind most present-day extraction (eq. 10). |
| 2 | `nigg2012`, `solgun2014` | Black-box and impedance-based quantisation; the bridge to model-order reduction. |
| 2 | `minev2021lom` | Modular lumped models; how to compose cells, which is relevant to Problem 2. |
| 3 | `shanto2024` | SQuADDS: a validated design database, a seed for learned surrogates. |
| 3 | `menke2021` | Automated circuit discovery with Bayesian optimisation; the closest prior art to inverse design. |
| 3 | `jin2014` | Finite-element electromagnetics, for the numerical-accuracy discussion in §3.4. |

## 3. Variability, frequency collisions and yield

| Tier | Key | Why read it |
|---|---|---|
| 1 | `hertzberg2021` | Laser annealing of junctions and the collision analysis; the central paper for §4. |
| 1 | `brink2018` | Defines frequency collisions as a device-yield problem. |
| 2 | `kreikebaum2020` | Measured wafer-scale junction-resistance variation and how to reduce it. |
| 2 | `morvan2022` | Frequency allocation as optimisation; the baseline for Problem 1. |
| 2 | `zhang2022` | Laser annealing on full processors; the practical precision achieved. |
| 3 | `vandamme2024` | imec's 300 mm superconducting qubits: what changes when the process becomes CMOS-like. |
| 3 | `pelgrom1989`, `stapper1983` | Classical mismatch and yield statistics; the models quantum yield will borrow. |
| 3 | `ambegaokar1963`, `simmons1963` | Junction physics behind eqs. 13–15. |

## 4. Materials and loss

| Tier | Key | Why read it |
|---|---|---|
| 1 | `deleon2021` | Survey of materials problems across modalities. |
| 1 | `mcrae2020` | How loss is measured with resonators; necessary to understand any loss data. |
| 2 | `wang2015`, `gambetta2017` | Surface participation, eq. 23. |
| 2 | `muller2019` | Two-level-system physics. |
| 2 | `place2021` | Tantalum transmons: proof that materials can beat design. |
| 3 | `klimov2018` | \(T_1\) fluctuations: coherence is a random process. |
| 3 | `mcewen2022`, `vepsalainen2020` | Correlated errors from radiation, which matter for QEC. |

## 5. Packaging, wiring and control

| Tier | Key | Why read it |
|---|---|---|
| 1 | `huang2021` | Microwave package design for superconducting processors. |
| 1 | `krinner2019` | Heat and noise budgets for wiring at the 100-qubit scale. |
| 2 | `rosenberg2017`, `yost2020` | Bump bonding and through-silicon vias. |
| 3 | `bardin2019`, `xue2021`, `reilly2015` | Cryogenic CMOS control and the quantum–classical interface. |

## 6. Test and calibration

| Tier | Key | Why read it |
|---|---|---|
| 1 | `magesan2011` | Randomised benchmarking. |
| 1 | `kelly2018` | Calibration as a graph of experiments. |
| 2 | `neyens2024` | Intel's 300 mm cryogenic wafer probing: what wafer-scale quantum test data look like. |
| 2 | `wittler2021` | Model-based calibration and characterisation toolset. |
| 3 | `granade2012`, `eisert2020` | Bayesian Hamiltonian learning; certification and benchmarking. |

## 7. Error correction

| Tier | Key | Why read it |
|---|---|---|
| 1 | `fowler2012` | The surface code, in practical terms. |
| 1 | `google2025` | Below-threshold operation; the \(\Lambda = 2.14\) anchor for §9. |
| 2 | `terhal2015` | QEC for memories; decoding backlog and thresholds. |
| 2 | `gidney2021stim` | Stim and detector error models; the interface for Problem 6. |
| 2 | `bravyi2024` | IBM's bivariate bicycle codes: why codes drive chip wiring. |
| 3 | `breuckmann2021` | qLDPC review. |
| 3 | `bausch2024` | Learned decoders (AlphaQubit). |
| 3 | `auger2017`, `strikis2023` | Error correction with fabrication defects; the basis of logical yield. |
| 3 | `beverland2022`, `gidney2025rsa` | Resource estimates that make \(\Lambda\) commercially decisive. |

## 8. Other modalities

| Tier | Key | Why read it |
|---|---|---|
| 1 | `bruzewicz2019` | Trapped-ion progress and challenges. |
| 1 | `burkard2023` | Semiconductor spin qubits. |
| 2 | `wang2020photonics` | Integrated photonic quantum technologies. |
| 2 | `saffman2010`, `bluvstein2024` | Rydberg atoms; logical processors on atom arrays. |
| 3 | `house2008` | Analytic surface-trap model: a ready-made surrogate. |
| 3 | `bourassa2021`, `bartolucci2023` | Photonic fault-tolerance blueprints and loss thresholds. |
| 3 | `nayak2008`, `aghaee2023` | Topological qubits and Microsoft's gap protocol. |

## 9. Lessons from classical EDA

| Tier | Key | Why read it |
|---|---|---|
| 1 | `orshansky2008` | Statistical design and design for manufacturability: the playbook quantum needs. |
| 2 | `blaauw2008` | Statistical timing analysis; the template for statistical sign-off (eq. 22). |
| 2 | `meadconway1980` | How design rules separated design from fabrication. |
| 3 | `odabasioglu1998`, `gustavsen1999`, `antoulas2005`, `toselli2005` | Passive model-order reduction and domain decomposition, for Problem 2. |

## 10. Statistics and machine learning methods

| Tier | Key | Why read it |
|---|---|---|
| 1 | `rasmussen2006` | Gaussian processes, for wafer maps and surrogates. |
| 1 | `angelopoulos2023` | Conformal prediction: calibrated error bars for sign-off. |
| 2 | `rainforth2024` | Modern Bayesian experimental design, for test planning. |
| 2 | `cranmer2020` | Simulation-based inference, for simulator calibration. |
| 2 | `luedtke2008`, `nemirovski2006` | Chance-constrained optimisation, for Problem 1. |
| 3 | `li2021fno`, `lu2021deeponet`, `pfaff2021`, `raissi2019` | Operator learning and mesh-based surrogates. |
