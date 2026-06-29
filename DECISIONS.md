# DECISIONS.md

# NYC Congestion Pricing Mobility Analytics Project

Last Updated: 2026-06-13

---

# Purpose

This document records major project decisions, the reasoning behind those decisions, and their downstream implications.

Unlike PROJECT_SPEC.md, which explains what the project is, this file explains why major choices were made.

Only decisions with meaningful downstream impact should be included.

---

# D-001: Canonical Analytical Grain

## Decision

Use:

**Taxi Zone × Date × Temporal Bucket**

as the canonical observation unit across the entire project.

## Reasoning

Transportation systems report activity at different spatial and temporal resolutions.

A common analytical grain is required to:

* Integrate mobility systems.
* Engineer comparable features.
* Support multimodal modeling.
* Preserve interpretability.

Taxi Zones provide citywide coverage while remaining granular enough to capture neighborhood-level behavior.

Temporal buckets preserve behavioral structure while avoiding excessive hourly sparsity.

## Downstream Impact

Affects:

* Harmonization
* Mobility-layer construction
* Feature engineering
* Representation learning
* Clustering
* Anomaly detection
* Visualization

Status:

**Locked**

---

# D-002: Taxi = Yellow + Green

## Decision

Combine Yellow Taxi and Green Taxi activity into a single Taxi modality.

## Reasoning

The project focuses on mobility states rather than taxi-service segmentation.

Yellow and Green Taxi systems describe the same underlying transportation mode and combining them:

* Simplifies modeling.
* Improves coverage.
* Improves interpretability.
* Reduces unnecessary modality fragmentation.

## Downstream Impact

Affects:

* Mobility tables
* Feature engineering
* Representation learning
* Clustering
* Anomaly detection

Status:

**Locked**

---

# D-003: Exclude FHV

## Decision

Remove FHV from downstream modeling.

## Reasoning

Coverage analysis revealed severe geographic incompleteness.

Including FHV would introduce:

* Coverage artifacts
* Interpretation challenges
* Unnecessary complexity

without providing sufficient mobility-state value.

## Downstream Impact

Canonical modalities become:

* Bus
* Subway
* Taxi
* FHVHV
* Multimodal

Status:

**Locked**

---

# D-004: Retain FHVHV

## Decision

Keep FHVHV as a primary transportation modality.

## Reasoning

FHVHV provides:

* Broad geographic coverage
* Strong demand signal
* Ride-hailing representation
* Complementary information relative to Taxi

## Downstream Impact

FHVHV remains a core modality throughout the project.

Status:

**Locked**

---

# D-005: Traffic Excluded from Default Unsupervised Modeling

## Decision

Traffic remains available but is excluded from default unsupervised feature spaces.

## Reasoning

Traffic observations exhibit:

* Sparse geographic coverage
* Sparse temporal coverage
* Irregular observation schedules

These characteristics differ substantially from the remaining transportation systems.

Including Traffic directly would create:

* Coverage-driven artifacts
* Missingness complications
* Representation distortions

## Alternative Considered

Include Traffic as a fifth primary modality.

Rejected because coverage limitations outweighed benefits.

## Downstream Impact

Traffic may still be used for:

* Contextual interpretation
* Validation
* Supervised-learning targets
* Congestion-pricing analysis

Status:

**Locked**

---

# D-006: Transportation Absence Is Not Automatically Missing Data

## Decision

Treat transportation-system absence as a potentially valid geographic condition.

## Reasoning

Examples:

* Taxi Zones without subway stations
* Low-service transportation environments
* Limited transit-access neighborhoods

These situations reflect real transportation structure rather than data-quality failures.

## Downstream Impact

Influenced:

* Modeling-matrix construction
* Missingness policies
* Multimodal representation design

Status:

**Locked**

---

# D-007: Transportation-Aware Connectivity Network

## Decision

Use a transportation-aware connectivity network rather than pure geographic adjacency.

## Reasoning

Bridge and tunnel corridors create important mobility relationships that adjacency alone cannot capture.

Examples include:

* Battery Park ↔ Brooklyn bridge/tunnel gateways
* Staten Island bridge connections
* Cross-borough transportation corridors

## Downstream Impact

Used throughout:

* Spatial feature engineering
* Spillover calculations
* Connected-zone context features

Status:

**Locked**

---

# D-008: Preserve Broad Feature Generation Before Selection

## Decision

Generate broad feature families before conducting feature selection.

## Reasoning

Premature pruning risks eliminating useful mobility-state information.

The project intentionally generated:

* Temporal features
* Spatial features
* Multimodal features
* Decomposition features
* Variability features

before evaluating contribution and redundancy.

## Downstream Impact

Led directly to the 1.5.6 feature-selection framework.

Status:

**Locked**

---

# D-009: Seven Protected Core Mobility Metrics

## Decision

Treat seven mobility metrics as protected signals during feature selection.

## Metrics

* bus_trip_count
* avg_bus_speed
* subway_ridership
* taxi_trip_count
* taxi_avg_trip_speed
* fhvhv_trip_count
* fhvhv_avg_trip_speed

## Reasoning

These metrics represent the primary behavioral dimensions of the mobility system.

Removing them would undermine interpretability and modality coverage.

## Downstream Impact

Guided:

* 1.5.6 feature selection
* Representation learning
* Anomaly-detection planning

Status:

**Locked**

---

# D-010: Freeze Feature Selection After 1.5.6

## Decision

Treat feature selection as complete after Notebook 1.5.6.

## Reasoning

Repeatedly reopening feature-selection decisions creates:

* Scope creep
* Interpretation drift
* Reproducibility problems

Feature selection should remain a completed stage of the pipeline.

## Downstream Impact

3.x notebooks consume selected features rather than revisiting feature engineering.

Status:

**Locked**

---

# D-011: Separate Representation Learning from Anomaly Detection

## Decision

Representation learning and anomaly detection are separate stages.

## Reasoning

PCA and UMAP answer:

"What structure exists?"

Anomaly detection answers:

"What observations are unusual?"

Combining these stages too early obscures interpretation and makes methodology harder to evaluate.

## Downstream Impact

Chapter 3 proceeds in stages:

* Matrix construction
* PCA
* UMAP
* Representation comparison
* Clustering
* Anomaly detection

Status:

**Locked**

---

# D-012: Representation Policy for Downstream Anomaly Detection

## Decision

Raw Scaled remains an upstream reference surface but is not a primary anomaly-generation representation.

PCA became the canonical anomaly-generation representation across all retained anomaly frameworks.

UMAP remains an important representation-learning and visualization asset but is no longer used operationally within retained anomaly-generation workflows.

## Reasoning

Representation-comparison analysis demonstrated:

* PCA provided the strongest fidelity-preserving reduced representation.
* UMAP contributed meaningful nonlinear structure beyond PCA.
* Raw and PCA produced highly overlapping anomaly-like behavior.
* UMAP generated a distinct but coherent anomaly surface.

Subsequent anomaly-generation calibration demonstrated:

* UMAP was unsuitable for DBSCAN due to density heterogeneity.
* PCA consistently outperformed UMAP within Isolation Forest.
* UMAP did not provide sufficient justification to re-enter GMM evaluation.

As a result, PCA became the sole retained anomaly-generation representation across DBSCAN, Isolation Forest, and Gaussian Mixture Models.

## Downstream Impact

Applies to:

* DBSCAN
* Isolation Forest
* Gaussian Mixture Models
* Framework comparison
* Stability evaluation

Raw remains available for auditability and historical comparison.

UMAP remains available for visualization, interpretation, and representation-learning analysis.

Status:

**Locked**

---

# D-013: Exclude Missingness Indicators from Default Representations

## Decision

Exclude missingness indicators from default PCA and UMAP workflows.

## Reasoning

Sensitivity analyses showed:

* Minimal incremental value
* Risk of representation distortion
* Reduced interpretability

Indicators remain useful for auditability but should not dominate representation learning.

## Downstream Impact

Applies to:

* Taxi
* FHVHV
* Multimodal

representation-learning workflows.

Status:

**Locked**

---

# D-014: Global Representation Space

## Decision

Fit PCA and UMAP globally across all observations.

## Reasoning

A shared coordinate system allows:

* Direct comparison of mobility states
* Citywide interpretation
* Consistent visualization

## Alternative Considered

Fit separate representations by temporal bucket.

Rejected for representation learning because it would eliminate the common mobility-state space.

## Downstream Impact

Applies to:

* PCA
* UMAP
* Representation comparison

Status:

**Locked**

---

# D-015: Context-Aware Anomaly Scoring

## Decision

Representation learning remains global, but anomaly scoring should be context-aware.

The preferred downstream anomaly comparison universe is:

* same_temporal_bucket_and_policy_geography

Taxi additionally retains a targeted diagnostic comparison universe:

* same_temporal_bucket_and_pre_post_cp

## Reasoning

Temporal-only anomaly scoring improved interpretability relative to fully global scoring.

However, evaluation in 3.3.1 demonstrated that temporal-only scoring still produced meaningful concentration of anomaly-like behavior within major Manhattan mobility hubs and congestion-pricing geographies.

Adding policy-geography context materially reduced this concentration while preserving anomaly interpretability.

## Downstream Impact

Applies to:

* DBSCAN
* Isolation Forest
* Gaussian Mixture Models
* Anomaly-framework evaluation

Status:

**Locked**

---

# D-016: Global Representations, Context-Aware Scoring

## Decision

Representation learning and anomaly scoring are treated as separate modeling problems.

Global learned representations are acceptable, but anomaly scoring should remain context-aware.

## Reasoning

Representation-learning methods seek to learn a shared mobility-state space.

Anomaly-detection methods seek to identify unusual observations relative to an appropriate comparison universe.

The optimal representation-learning strategy and the optimal anomaly-scoring strategy do not necessarily require the same assumptions.

## Downstream Impact

Applies to:

* PCA
* UMAP
* DBSCAN
* Isolation Forest
* Gaussian Mixture Models

Status:

**Locked**

---
# D-017: 2D UMAP Is a Visualization Asset

## Decision

Treat the selected 2D UMAP as a visualization representation rather than automatically adopting it for anomaly detection.

## Selected Configuration

* n_neighbors = 50
* min_dist = 0.10
* metric = euclidean
* random_state = 42

## Reasoning

The best visualization representation is not necessarily the best anomaly-detection representation.

Higher-dimensional UMAP spaces may preserve more useful structure.

## Downstream Impact

Motivated:

* UMAP dimensionality evaluation
* Representation comparison workflows

Status:

**Locked**

---

## Downstream Impact

Applies to:

* Representation learning
* UMAP visualization workflows
* Representation comparison

The selected PCA→UMAP workflow remains the project's canonical nonlinear representation-learning workflow.

However, subsequent anomaly-generation calibration retired UMAP from DBSCAN, Isolation Forest, and Gaussian Mixture Model anomaly generation.

Status:

**Locked**

---

# D-019: Taxi-Specific PCA Handling

## Decision

Taxi retains split pre/post congestion-pricing PCA representations for downstream anomaly workflows.

## Reasoning

Taxi exhibited greater policy-period structural drift than the remaining modalities.

Framework-preparation analysis demonstrated that preserving separate pre/post PCA handling provided meaningful downstream value.

Other modalities did not demonstrate sufficient instability to justify separate policy-period PCA branches.

## Downstream Impact

Applies to:

* Taxi anomaly workflows
* DBSCAN
* Isolation Forest
* Gaussian Mixture Models

Status:

**Locked**

---

# D-020: Standard Rebuild Pattern

## Decision

Expensive notebook blocks should use:

should_rebuild = REBUILD_SOMETHING or (not output_path.exists())

## Reasoning

Outputs should automatically rebuild when missing even when rebuild toggles are disabled.

This eliminates unnecessary toggle management and reduces accidental execution failures caused by missing intermediate assets.

## Downstream Impact

Applies to:

* Representation-learning notebooks
* Anomaly-detection notebooks
* Export workflows
* Calibration workflows

Status:

**Locked**

---

# D-021: DBSCAN Representation Policy

## Decision

DBSCAN anomaly generation uses PCA representations only.

## Reasoning

DBSCAN calibration revealed substantially greater density heterogeneity within UMAP representations than within PCA representations.

This density behavior made UMAP difficult to calibrate consistently across modalities and produced unstable density-based anomaly behavior.

PCA representations produced more interpretable and operationally useful density structure for DBSCAN.

## Downstream Impact

Applies to:

* DBSCAN calibration
* DBSCAN anomaly generation
* DBSCAN anomaly interpretation

Status:

**Locked**

---

# D-022: Canonical Geometry Asset for Anomaly Mapping

## Decision

Use:

1.3.1.final_tables/nyc_taxi_zones_harmonized.parquet

as the authoritative geometry asset for downstream anomaly mapping and spatial-review workflows.

## Reasoning

The harmonized geometry asset reflects the project's final Taxi Zone handling and avoids inconsistencies associated with earlier staging assets.

This decision emerged during anomaly-review and mapping workflows.

## Downstream Impact

Applies to:

* DBSCAN mapping
* Isolation Forest mapping
* Gaussian Mixture Model mapping
* Spatial anomaly review
* Congestion-pricing interpretation

Status:

**Locked**

---

# D-023: Isolation Forest Representation Policy

## Decision

Isolation Forest anomaly generation uses PCA representations only.

Final retained Isolation Forest configuration:

* PCA only
* contamination = 0.005

## Reasoning

Isolation Forest does not rely on density-homogeneity assumptions and therefore allowed UMAP to remain under evaluation during calibration.

However, PCA consistently produced stronger anomaly-tail separation, more interpretable anomaly concentration patterns, and more coherent anomaly structure.

UMAP produced flatter anomaly surfaces and exhibited very low overlap with PCA anomaly outputs.

PCA provided the stronger operational anomaly surface.

## Downstream Impact

Applies to:

* Isolation Forest calibration
* Isolation Forest anomaly generation
* Isolation Forest anomaly interpretation

Status:

**Locked**

---

# D-024: Gaussian Mixture Model Representation Policy

## Decision

Gaussian Mixture Model anomaly generation uses PCA representations only.

Final retained GMM policy:

* PCA only
* Full covariance only
* Modality-specific component counts
* Tail threshold = 0.005

## Reasoning

GMM was intentionally scoped as a probabilistic anomaly framework rather than a new representation-selection exercise.

Raw Scaled did not re-enter evaluation.

UMAP did not re-enter evaluation.

Full covariance consistently outperformed diagonal covariance and produced stronger probabilistic anomaly surfaces.

Likelihood-tail threshold 0.005 produced the strongest anomaly-tail separation across modalities.

## Downstream Impact

Applies to:

* GMM calibration
* GMM anomaly generation
* GMM anomaly interpretation

Status:

**Locked**

--- 

# D-025: Human Review Philosophy

## Decision

Human-review depth should be proportional to methodological uncertainty.

## Reasoning

DBSCAN required extensive review because density suitability, density heterogeneity, and representation appropriateness were active 
methodological questions.

Isolation Forest and Gaussian Mixture Models used lighter aggregate-review workflows because representation evaluation, 
anomaly-framework preparation, and cross-framework diagnostics had already resolved many of the major methodological uncertainties.

Future anomaly notebooks should not automatically repeat DBSCAN-style deep row-level review unless a specific methodological concern 
justifies it.

## Downstream Impact

Applies to:

* Isolation Forest
* Gaussian Mixture Models
* Framework comparison
* Future anomaly workflows

Status:

**Locked**

---

# D-026: Retained Anomaly Framework Configurations

## Decision

The retained anomaly-generation configurations are:

DBSCAN

* Bus: min_samples = 15, balanced eps band
* Subway: min_samples = 15, balanced eps band
* Taxi: min_samples = 20, tight eps band
* FHVHV: min_samples = 15, balanced eps band
* Multimodal: min_samples = 15, balanced eps band

Isolation Forest

* PCA only
* contamination = 0.005

Gaussian Mixture Models

* Bus: k = 3, full covariance, tail = 0.005
* Subway: k = 3, full covariance, tail = 0.005
* Taxi: k = 3, full covariance, tail = 0.005
* FHVHV: k = 2, full covariance, tail = 0.005
* Multimodal: k = 2, full covariance, tail = 0.005

## Reasoning

These configurations produced the strongest balance of stability, interpretability, anomaly-tail separation, and framework-specific 
value during calibration.

## Downstream Impact

These configurations should be treated as the canonical anomaly-framework inputs for downstream stability evaluation, policy 
interpretation, and social-data integration unless a strong justification exists for reopening calibration.

Status:

**Locked**

---

# D-027: Canonical Downstream Anomaly Package

## Decision

The downstream anomaly package is organized as a layered interpretation framework.

Primary retained anomaly layers:

* Retained anomaly union
* Retained positive-direction subset
* Positive-direction | 2+ methods consensus

Additional support layers:

* Consensus indicators
* Directional anomaly labels
* Framework-specific anomaly flags
* Modality participation indicators

## Reasoning

Framework comparison demonstrated that DBSCAN, Isolation Forest, and Gaussian Mixture Models are complementary rather than redundant.

Subsequent anomaly evaluation demonstrated that:

* The retained anomaly union provides broad anomaly coverage.
* Positive-direction filtering substantially improves policy relevance and external validation behavior.
* Two-method consensus improves confidence while preserving useful coverage.
* Three-method consensus becomes overly restrictive and loses useful signal.

No single anomaly surface adequately serves every downstream use case.

A layered anomaly package preserves both sensitivity and interpretability.

## Downstream Impact

Broad reference surface:

* Retained anomaly union

Primary working anomaly surface:

* Retained positive-direction subset

Preferred high-confidence anomaly core:

* Positive-direction | 2+ methods consensus

Robustness-only refinement:

* Positive-direction | 3 methods consensus

Status:

**Locked**


---

# D-028: Directionality Policy

## Decision

Directionality is treated as a first-class interpretation layer throughout downstream anomaly evaluation.

Primary downstream directional lenses are:

* congestion_oriented
* positive_demand_shock

Additional directional labels remain available for diagnostic purposes:

* decongestion_oriented
* negative_demand_shock
* mixed
* ambiguous

## Reasoning

Framework-comparison analysis demonstrated that not all anomalies are equally relevant to congestion-pricing interpretation.

Separating congestion-oriented anomalies from broader anomaly behavior improves interpretability and allows downstream analyses to focus on mobility states most relevant to transportation-system performance.

## Downstream Impact

Applies to:

* Framework comparison
* Stability evaluation
* Congestion-pricing interpretation
* Social-data integration

Status:

**Locked**

---

# D-029: Modality Participation Policy

## Decision

Multimodal anomaly participation is informative but should not replace modality-specific anomaly participation.

Downstream anomaly interpretation should preserve participation indicators for:

* Bus
* Subway
* Taxi
* FHVHV
* Multimodal

## Reasoning

Framework-comparison analysis demonstrated that modality participation contains important information about the nature of mobility irregularities.

Multimodal anomalies provide useful context but do not fully capture the transportation-system composition of anomalous mobility states.

Preserving modality participation improves interpretability and supports downstream policy analysis.

## Downstream Impact

Applies to:

* Framework comparison
* Stability evaluation
* Congestion-pricing interpretation
* Social-data integration

Status:

**Locked**

---

# D-030: Consensus Policy

## Decision

Consensus is treated as a refinement mechanism rather than a requirement for anomaly validity.

Preferred consensus layer:

* Positive-direction | 2+ methods consensus

Three-method consensus is retained only as a robustness reference.

## Reasoning

Consensus evaluation demonstrated that:

* Two-method consensus improves anomaly quality while preserving meaningful coverage.
* Three-method consensus sacrifices too much coverage.
* Increasing agreement requirements does not automatically improve downstream utility.

Consensus therefore functions best as a confidence layer rather than a replacement for the broader anomaly package.

## Downstream Impact

Applies to:

* 3.4 anomaly evaluation
* 3.5 dataset construction
* Social-data integration
* Final report interpretation

Status:

**Locked**

---

# D-031: Recurrence and Persistence Policy

## Decision

Recurrence and persistence are treated as primary anomaly-quality metrics.

Canonical recurrence context:

* feature_set
* taxi_zone_id
* temporal_bucket

Canonical persistence definition:

* Another anomaly occurring within the same local context within 7 days.

## Reasoning

The project seeks to identify meaningful mobility irregularities rather than isolated statistical outliers.

Recurring and persistent anomaly behavior provides stronger evidence that anomaly surfaces reflect real mobility phenomena.

The 7-day persistence window balances sensitivity and interpretability while remaining aligned with weekly mobility cycles.

## Downstream Impact

Applies to:

* Anomaly evaluation
* Anomaly interpretation
* Framework synthesis
* Final reporting

Status:

**Locked**

---

# D-032: External Validation Policy

## Decision

External validation is performed using NYC crash events at the canonical project grain:

Taxi Zone × Date × Temporal Bucket

Primary validation targets:

* Any crash occurrence
* Crash counts
* Injury-linked crash occurrence

Fatal crashes remain descriptive-only validation signals due to extreme sparsity.

## Reasoning

Anomaly quality should not be evaluated solely through internal model behavior.

Crash events provide an independent transportation-system signal capable of assessing whether detected anomalies align with real-world disruption and mobility stress.

External validation demonstrated meaningful differences between anomaly surfaces that appeared similar under internal evaluation alone.

## Downstream Impact

Applies to:

* 3.4 anomaly evaluation
* 3.5 dataset construction
* Final report interpretation

Status:

**Locked**

---

# D-033: Positive-Direction Interpretation Policy

## Decision

Positive-direction anomalies are the preferred policy-facing anomaly package.

Primary directional lenses:

* positive_demand_shock
* congestion_oriented

Positive-demand-shock becomes the strongest externally validated directional lens.

## Reasoning

3.4.1 evaluation demonstrated that:

* Positive-direction filtering materially improves anomaly quality.
* Positive-direction anomalies exhibit stronger crash alignment than the retained anomaly union.
* Positive-demand-shock exhibits the strongest external-validation performance among evaluated directional categories.

Not all anomalies are equally relevant to congestion-pricing interpretation.

Positive-direction anomalies provide the clearest connection to transportation-system stress, demand concentration, and potential policy-relevant mobility conditions.

## Downstream Impact

Applies to:

* Anomaly evaluation
* Congestion-pricing interpretation
* Social-data integration
* Final reporting

Status:

**Locked**

---

# Workflow Decision: Codex Model Routing Guidelines

Purpose:

Reduce Codex credit consumption while preserving reasoning quality for important project decisions.

## Default Policy

Use the cheapest capable model for the task.

Escalate only when reasoning complexity justifies the additional cost.

---

## GPT-5.4-Mini

Preferred for:

* Single-cell implementations
* Export logic
* Plot generation
* QA tables
* Findings generation
* Small bug fixes
* Mechanical refactors
* File I/O changes
* Manifest updates
* Formatting tasks

Default reasoning:

* Low
* Medium

---

## GPT-5.4

Preferred for:

* Multi-cell implementations
* Moderate debugging
* Notebook section development
* Refactors within a notebook
* Data-validation workflows

Default reasoning:

* Medium

---

## GPT-5.5

Preferred for:

* Methodology decisions
* New notebook planning
* Cross-notebook debugging
* Representation-learning design
* Feature-engineering design
* Architecture changes
* Unexpected analytical findings
* Complex root-cause analysis

Default reasoning:

* High

Use Extra High only when the problem genuinely requires extended reasoning.

---

## Escalation Strategy

Start with the lowest-cost model likely to succeed.

Escalate only if:

* The model repeatedly fails.
* The root cause is unclear.
* The issue spans multiple notebooks.
* The issue may change project methodology.
* The issue may alter downstream modeling decisions.

---

## Context Strategy

Implementation Tasks:

Read:

1. PROJECT_STATE.md
2. NOTEBOOK_INDEX.md
3. Current notebook

Planning Tasks:

Read:

1. PROJECT_STATE.md
2. NOTEBOOK_INDEX.md
3. DECISIONS.md
4. PROJECT_SPEC.md
5. Current notebook

Avoid opening prior notebooks unless implementation details are required.


---

## Documentation Hierarchy

PROJECT_STATE.md

* Current operational state
* Current notebook
* Active decisions
* Immediate next steps

NOTEBOOK_INDEX.md

* Notebook-level history
* Key findings
* Major exports
* Important decisions

DECISIONS.md

* Long-lived methodological and architectural decisions
* Choices that should not be reopened without strong justification

PROJECT_SPEC.md

* Complete project encyclopedia
* Pipeline design
* Historical rationale
* Architectural reference

Implementation tasks should generally begin with PROJECT_STATE.md and NOTEBOOK_INDEX.md.

Planning and methodology work should additionally review DECISIONS.md and PROJECT_SPEC.md.