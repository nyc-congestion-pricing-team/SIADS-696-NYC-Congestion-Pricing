# NYC Congestion Pricing Mobility Analytics Project

Last Updated: 2026-06-18

---

# Current Position

Current Notebook:

* 3.4.1 Evaluate Final Anomaly Surfaces (Near Completion)

Last Completed:

* 3.3.5 Compare Candidate Anomaly Frameworks

Current Phase:

* Final Anomaly Evaluation and Downstream Surface Selection

Next Major Phase:

* 3.5.1 Construct Anomaly Summary Datasets
* 3.5.2 Construct Social-Integration-Ready Mobility Datasets
* Final Report Preparation
* Social Branch Integration

---

# Current Pipeline Status

Completed:

* 1.1 Source Acquisition and Staging
* 1.2 Standardization and Harmonization
* 1.3 Integrated Mobility Layer
* 1.5 Feature Engineering
* 3.1.1 Unsupervised Modeling Matrices
* 3.2.1 PCA Exploration
* 3.2.2 PCA Stability Analysis
* 3.2.3 UMAP and t-SNE Exploration
* 3.2.4 Evaluate Candidate Representation Spaces
* 3.3.1 Prepare Anomaly Detection Frameworks
* 3.3.2 Calibrate and Generate DBSCAN Anomalies
* 3.3.3 Calibrate and Generate Isolation Forest Anomalies
* 3.3.4 Calibrate and Generate Gaussian Mixture Model Anomalies
* 3.3.5 Compare Candidate Anomaly Frameworks

Near Completion:

* 3.4.1 Evaluate Final Anomaly Surfaces

Not Started:

* 3.5.1 Construct Anomaly Summary Datasets
* 3.5.2 Construct Social-Integration-Ready Mobility Datasets
* Forecasting / Counterfactual Analysis

---

# Current Modeling Philosophy

The project detects anomalous mobility states rather than anomalous individual trips, riders, vehicles, roadway observations, or transportation events.

Canonical analytical grain:

Taxi Zone × Date × Temporal Bucket

Canonical modeling modalities:

* Bus
* Subway
* Taxi
* FHVHV
* Multimodal

Traffic remains available as contextual information but is excluded from default unsupervised feature spaces.

Representation learning and anomaly scoring are treated as separate modeling problems.

Global representations remain acceptable for representation learning.

Anomaly interpretation is increasingly focused on identifying mobility states that are:

* recurrent
* persistent
* interpretable
* policy relevant
* externally validated

rather than merely statistically unusual.

---

# Current Retained Anomaly Package

Broad retained anomaly universe:

* Retained anomaly union
* 48,964 rows

Primary policy-facing anomaly package:

* Retained positive-direction subset
* 10,741 rows

Directional interpretive lenses:

* congestion_oriented
* positive_demand_shock

Support layers:

* consensus indicators
* framework-specific flags
* modality participation indicators
* directional labels

Current export package:

* full_comparison_table
* retained_anomaly_working_table
* retained_positive_direction_working_table
* consensus_indicator_table
* directional_label_table
* framework_specific_flag_table
* modality_participation_table
* social_join_focus_table

Export alignment, row-universe consistency, and schema consistency issues identified during early 3.4.1 work have been corrected.

---

# Current Downstream Recommendation

Broad reference surface:

* Retained anomaly union

Primary working anomaly surface:

* Retained positive-direction subset

Preferred high-confidence anomaly core:

* Positive-direction | 2+ methods consensus

Robustness-only refinement:

* Positive-direction | 3 methods consensus

Current evidence indicates that:

* The retained anomaly union is useful as a broad reference surface but is too permissive to serve as the primary downstream anomaly package.
* The retained positive-direction subset provides a more interpretable and policy-relevant anomaly surface.
* Positive-direction | 2+ methods consensus provides the strongest balance of coverage, recurrence, interpretability, and external validation.
* Positive-direction | 3 methods consensus becomes overly restrictive and loses useful signal.

---

# Active Decisions

Remaining Open Questions:

* Which anomaly summaries should become the canonical social-integration features in 3.5.1 and 3.5.2?
* How should consensus and framework-specific anomaly indicators coexist within downstream datasets?
* Which anomaly-intensity metrics should become primary explanatory variables for social-data integration?
* How should directional anomaly lenses be exposed within downstream datasets and final reporting?

Current Expectation:

* Positive-direction | 2+ methods consensus will become the preferred high-confidence downstream anomaly layer.
* The retained positive-direction subset will remain the broader companion layer.
* The retained anomaly union will remain available as a reference surface.
* Positive-demand-shock behavior will play a larger downstream role than originally anticipated.

---

# Recent Findings

## 3.3.5 Framework Synthesis

Key findings:

* DBSCAN, Isolation Forest, and GMM are complementary rather than redundant.
* Consensus agreement exists but is selective.
* Directionality emerged as a first-class interpretation layer.
* Positive-direction anomalies became substantially more important than originally expected.
* Modality participation remains important for anomaly interpretation.

Final retained package:

* Retained anomaly union
* Positive-direction subset
* Congestion-oriented lens
* Positive-demand-shock lens
* Consensus indicators
* Framework-specific flags
* Modality participation indicators

---

## 3.4.1.3 Recurrence and Persistence

Recurrence context:

* feature_set
* taxi_zone_id
* temporal_bucket

Final persistence definition:

* another anomaly in the same local context within 7 days

Key findings:

Retained anomaly union:

* recurrent_share = 96.4%
* persistent_within_7d_share = 73.0%

Retained positive-direction subset:

* recurrent_share = 88.9%
* persistent_within_7d_share = 48.1%

Interpretation:

The positive-direction subset remains strongly recurrent while becoming substantially more selective and less continuously active than the full anomaly union.

This was interpreted as signal sharpening rather than signal loss.

---

## 3.4.1.4 Consensus Evaluation

Coverage:

* Positive-direction subset = 10,741 rows
* Positive-direction | 2+ consensus = 4,792 rows
* Positive-direction | 3-method consensus = 1,903 rows

Key findings:

* 2+ consensus remains behaviorally useful.
* 3-method consensus becomes overly restrictive.
* Stricter consensus does not automatically improve all evaluation metrics.
* Consensus evolved from a descriptive annotation into an important downstream design choice.

---

## 3.4.1.5 Directional and Policy-Relevance Evaluation

Key findings:

* Positive-direction anomalies remain predominantly outside core policy geographies.
* Positive-demand-shock anomalies carry greater CBD representation than congestion-oriented anomalies.
* Post-congestion-pricing behavior exhibits modest increases in normalized anomaly frequency.
* Positive-demand-shock behavior drives more of the observed post-CP increase than congestion-oriented behavior.
* Later-day and PM-peak activity became important components of the policy-relevance story.

Interpretation remains descriptive rather than causal.

---

## 3.4.1.6 External Validation Using NYC Crash Events

Validation grain:

* taxi_zone_id
* date
* temporal_bucket

Validation signals:

* any crash occurrence
* crash count
* injury-linked crash occurrence

Key findings:

Retained anomaly union:

* underperforms crash baseline

Retained positive-direction subset:

* materially improves crash alignment

Consensus refinement:

* Positive-direction | 2+ methods consensus provides the strongest crash enrichment
* Positive-direction | 3 methods consensus loses useful signal

Directional findings:

* Positive-demand-shock is the strongest internally crash-aligned directional lens.
* Congestion-oriented remains useful for interpretation but exhibits weaker external validation performance.

This chapter materially changed the preferred downstream recommendation.

---

# Notebook Hardening and Reproducibility

Recent work substantially improved notebook robustness.

Key improvements:

* Removed brittle dependencies on phantom intermediate variables.
* Eliminated stale export assumptions.
* Corrected row-alignment issues.
* Corrected schema inconsistencies.
* Corrected export-manifest mismatches.
* Rewired interpretation blocks to depend on authoritative upstream assets.

Notebook reruns are now substantially more reliable than earlier 3.4.1 versions.

---

# Current Notebook Goals

## 3.4.1 Evaluate Final Anomaly Surfaces

Remaining objectives:

* Complete final synthesis chapter.
* Finalize anomaly-surface recommendations.
* Finalize downstream handoff guidance.
* Prepare anomaly package recommendations for 3.5.x.
* Prepare final-report evaluation summaries.

Out of Scope:

* New anomaly-generation methods
* Hyperparameter calibration
* Representation redesign
* Social-data integration implementation
* Forecasting

---

# Important Implementation Rules

* Do not reopen feature engineering.
* Do not reopen feature selection.
* Do not reopen representation-selection decisions.
* PCA remains the canonical anomaly-generation representation.
* Preserve anomaly-package row alignment across all exports.
* Preserve traceability from downstream summaries back to row-level anomaly records.
* Use 7-day persistence as the canonical persistence definition.
* Use crash validation at Taxi Zone × Date × Temporal Bucket grain.
* Treat Positive-Direction | 2+ Methods Consensus as the preferred high-confidence anomaly core unless contradictory evidence emerges.

---

# Context Loading Guidance

For implementation work, load:

1. PROJECT_STATE.md
2. NOTEBOOK_INDEX.md
3. Current notebook

Consult PROJECT_SPEC.md for historical context.

Consult DECISIONS.md for settled methodological decisions.

Avoid reopening previously settled representation, calibration, or anomaly-generation decisions unless new evidence clearly justifies doing so.
