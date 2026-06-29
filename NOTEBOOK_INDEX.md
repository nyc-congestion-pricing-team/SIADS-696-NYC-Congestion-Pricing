# NOTEBOOK_INDEX.md

# NYC Congestion Pricing Mobility Analytics Project

Last Updated: 2026-06-15

---

# Purpose

This document provides a notebook-level summary of the project pipeline.

For each notebook it records:

* Purpose
* Key outputs
* Major findings
* Important downstream decisions

This document is intended to provide historical context without requiring re-ingestion of entire notebooks.

Implementation details, code, QA tables, and exports are intentionally omitted unless they materially affect downstream work.

---

# 1.1 Source Acquisition and Staging

---

## 1.1.1 Traffic Dataset Acquisition and QA

### Purpose

Acquire and validate roadway traffic-volume observations.

### Key Outputs

* Staged traffic parquet assets
* Coverage summaries
* QA tables

### Key Findings

* Traffic coverage is sparse.
* Observation schedules are irregular.
* Traffic behaves differently from the remaining transportation systems.

### Important Decisions

* Traffic retained as contextual signal.
* Traffic excluded from default unsupervised modeling workflows.

---

## 1.1.2 TLC Taxi and FHVHV Acquisition and QA

### Purpose

Acquire Taxi, FHV, and FHVHV datasets.

### Key Outputs

* Staged Taxi datasets
* Staged FHVHV datasets

### Key Findings

* Taxi and FHVHV provide near-citywide coverage.
* FHV coverage is highly incomplete.

### Important Decisions

* Taxi = Yellow + Green.
* FHV excluded.
* FHVHV retained.

---

## 1.1.3 Subway Dataset Acquisition and QA

### Purpose

Acquire subway ridership datasets.

### Key Outputs

* Staged subway assets
* Coverage summaries

### Key Findings

* Strong transit-demand signal.
* Structural geographic absence in many Taxi Zones.

### Important Decisions

* Subway absence is treated as geographic reality rather than missing data.

---

## 1.1.4 Bus Dataset Acquisition and QA

### Purpose

Acquire bus-demand and bus-speed datasets.

### Key Outputs

* Staged bus assets
* Coverage summaries

### Key Findings

* Broad geographic coverage.
* Valuable surface-transportation signal.

### Important Decisions

* Bus becomes a primary modeling modality.

---

## 1.1.5 Bridge and Tunnel Acquisition and QA

### Purpose

Acquire bridge-and-tunnel crossing datasets.

### Key Outputs

* Staged bridge-and-tunnel assets
* Facility summaries

### Key Findings

* Strong regional mobility context.

### Important Decisions

* Use as contextual feature source rather than standalone modality.

---

## 1.1.6 Taxi Zone Reference Layer

### Purpose

Create canonical spatial reference layer.

### Key Outputs

* Harmonized Taxi Zone layer

### Key Findings

* Multipart geometries require special handling.

### Important Decisions

* Canonical geometry-handling procedures established.

---

# 1.2 Standardization and Harmonization

---

## 1.2.1 Temporal Standardization

### Purpose

Create a common temporal framework.

### Key Outputs

* Standardized timestamps
* Temporal buckets
* pre_cp / post_cp labels

### Key Findings

* Transportation systems vary substantially in temporal granularity.

### Important Decisions

* Ten temporal buckets become canonical project standard.

---

## 1.2.2 Spatial Standardization

### Purpose

Align all systems to Taxi Zones.

### Key Outputs

* Taxi Zone assignments
* Spatial QA outputs

### Key Findings

* Different systems require different assignment strategies.

### Important Decisions

* Taxi Zones become canonical geography.

---

## 1.2.3 TLC Mobility Tables

### Purpose

Create Taxi and FHVHV mobility tables.

### Key Outputs

* Taxi mobility tables
* FHVHV mobility tables

### Key Findings

* Taxi and FHVHV provide strongest citywide demand coverage.

### Important Decisions

* Taxi and FHVHV become core mobility modalities.

---

## 1.2.4 Harmonized Mobility Tables

### Purpose

Create harmonized transportation-system mobility tables.

### Key Outputs

* Harmonized modality tables

### Key Findings

* Coverage is complementary rather than redundant.
* No single transportation system provides complete visibility.

### Important Decisions

* Coverage differences should not automatically be treated as missing-data problems.

---

# 1.3 Integrated Mobility Layer

---

## 1.3.1 Integrated Mobility Layer

### Purpose

Create unified mobility-state panel.

### Key Outputs

* Analysis-ready mobility panel
* Audit mobility panel
* Bridge-and-tunnel panel

### Key Findings

* Multimodal integration provides substantially richer citywide coverage than any individual modality.

### Important Decisions

* Dense mobility panel becomes canonical modeling foundation.

---

# 1.5 Feature Engineering

---

## 1.5.1 Temporal Mobility Features

### Purpose

Create temporal-history features.

### Key Outputs

* Temporal mobility feature panel

### Key Findings

* Traffic requires observation-aware temporal engineering.

### Important Decisions

* Traffic treated separately from standard lag/rolling workflows.

---

## 1.5.2 Spatial Mobility Features

### Purpose

Create geographic-context features.

### Key Outputs

* Spatial mobility feature panel

### Key Findings

* Transportation spillovers extend beyond geographic adjacency.

### Important Decisions

* Transportation-aware connectivity network adopted.

---

## 1.5.3 Multimodal Interaction Features

### Purpose

Create multimodal and contextual mobility features.

### Key Outputs

* Multimodal interaction feature panel

### Key Findings

* Bridge-and-tunnel activity provides meaningful mobility context.

### Important Decisions

* Bridge-and-tunnel metrics integrated through engineered features.

---

## 1.5.4 Decomposition and Residual Features

### Purpose

Separate expected and unusual behavior.

### Key Outputs

* Residualized mobility features

### Key Findings

* Residual signals often provide cleaner anomaly-oriented information.

### Important Decisions

* Residual features retained as core feature family.

---

## 1.5.5 Variability and Anomaly Features

### Purpose

Create deviation-oriented mobility features.

### Key Outputs

* Variability/anomaly feature panel

### Key Findings

* Relative-deviation features provide interpretable anomaly context.

### Important Decisions

* Variability features retained as independent family.

---

## 1.5.6 Modeling Feature Selection

### Purpose

Construct final modeling feature universe.

### Key Outputs

* Modeling feature catalog
* Feature-set definitions

### Key Findings

* Temporal, spatial, decomposition, variability, and multimodal families all contribute meaningful information.

### Important Decisions

* Seven protected mobility metrics identified.
* Feature selection finalized.

---

# 3.1 Modeling Matrix Construction

---

## 3.1.1 Construct Unsupervised Modeling Matrices

### Purpose

Transform selected features into model-ready matrices.

### Key Outputs

* Raw modeling matrices
* Scaled modeling matrices
* Metadata tables
* QA assets

### Key Findings

* Transportation-system absence should not automatically remove observations.
* Modality-specific missingness policies perform better than global filtering.

### Important Decisions

* Traffic excluded from default unsupervised matrices.
* Mobility-only representation spaces adopted for Taxi, FHVHV, and Multimodal workflows.

---

# 3.2 Representation Learning

---

## 3.2.1 Explore Global Feature-Space Structure (PCA)

### Purpose

Evaluate PCA representations.

### Key Outputs

* PCA scores
* PCA loadings
* Explained-variance summaries

### Key Findings

* Single-modality spaces compress well.
* Multimodal space is more diffuse but interpretable.
* Borough structure is visible.
* Congestion-pricing-period structure is weak.

### Important Decisions

* Missingness indicators excluded from default PCA representations.

---

## 3.2.2 PCA Stability Analysis

### Purpose

Evaluate PCA stability across pre/post congestion-pricing periods.

### Key Outputs

* Stability diagnostics
* Pre/post PCA comparisons
* Taxi pre-congestion-pricing PCA modeling scores
* Taxi post-congestion-pricing PCA modeling scores

### Key Findings

* Most modalities are structurally stable across pre/post congestion-pricing periods.
* Taxi exhibits the strongest policy-period instability.
* Taxi showed meaningful enough structural drift to preserve operationally in downstream anomaly workflows.
* Remaining modalities did not require separate policy-period PCA branches.

### Important Decisions

* Full-period PCA retained as the canonical linear representation.
* Taxi-specific pre/post PCA assets exported for downstream anomaly-detection workflows.

---

## 3.2.3 UMAP and t-SNE Exploration

### Purpose

Evaluate nonlinear representations.

### Key Outputs

* UMAP embeddings
* t-SNE embeddings

### Key Findings

* Congestion-pricing geography is strongest nonlinear structure.
* Borough structure remains visible.
* Daypart and policy-period structure are weaker.

### Important Decisions

* Canonical visualization UMAP:

  * n_neighbors = 50
  * min_dist = 0.10
  * metric = euclidean
  * random_state = 42

* 2D UMAP retained for visualization only.

---

## 3.2.4 Compare Candidate Representation Spaces

### Purpose

Determine which learned representations should advance into downstream anomaly-detection workflows and establish the canonical UMAP modeling workflow.

### Key Outputs

* Downstream-ready PCA representations
* Downstream-ready UMAP representations
* Representation-comparison diagnostics
* Dimensionality-selection summaries
* Workflow-comparison summaries

### Key Findings

* PCA provided the strongest fidelity-preserving reduced representation across modalities.
* UMAP preserved less local neighborhood structure but revealed meaningful nonlinear mobility-state structure.
* Raw and PCA produced highly overlapping anomaly-like behavior.
* UMAP generated a distinct but coherent anomaly surface.
* FHVHV and Multimodal exhibited the largest differences between PCA and UMAP anomaly behavior.
* Subway exhibited the smallest differences.

### Important Decisions

* Downstream anomaly representations:
  * pca_80pct
  * umap_pca_to_umap_10d
* raw_scaled retained as a reference surface but retired as a standalone anomaly-generation branch.
* Selected UMAP workflow:
  * PCA → UMAP
  * 10 dimensions
  * PCA dimensionality selected separately by modality using the 80% cumulative explained variance threshold.
* Full-dataset UMAP exports generated by:
  * Fit on shared 50K evaluation sample
  * Transform full datasets in chunks
  * Avoid full-panel UMAP refits

---

# 3.3 Anomaly Detection Frameworks

---

## 3.3.1 Prepare Anomaly Detection Frameworks

### Purpose

Establish the shared anomaly-detection framework inherited by DBSCAN, Isolation Forest, and Gaussian Mixture Model workflows.

### Key Outputs

* Shared anomaly calibration samples
* Shared anomaly-representation defaults
* Shared anomaly-comparison-universe definitions
* Shared anomaly-framework assets
* Method-invariant anomaly configuration exports
* Taxi pre/post PCA anomaly assets

### Key Findings

* Temporal-bucket-aware anomaly scoring substantially improved interpretability relative to fully global scoring.
* Geography-aware scoring further reduced concentration of anomaly-like behavior within Manhattan and major mobility hubs.
* Temporal-only baselines remained susceptible to CBD concentration, particularly for Subway and Taxi.
* Raw and PCA produced highly overlapping anomaly-like outputs.
* UMAP contributed a distinct but coherent anomaly surface.
* Taxi shared-versus-split PCA comparisons supported retaining split pre/post congestion-pricing PCA handling downstream.

### Important Decisions

* Shared anomaly calibration samples:

  * 50,000 observations per modality
  * Stratified by temporal_bucket
  * Stratified by pre_post_cp
* Shared downstream comparison universe:

  * same_temporal_bucket_and_policy_geography
* Taxi diagnostic comparison universe:

  * same_temporal_bucket_and_pre_post_cp
* Raw retired as a primary anomaly-generation branch.
* Shared downstream anomaly representations:

  * pca_80pct
  * umap_pca_to_umap_10d
* Taxi retains split pre/post PCA handling for downstream anomaly workflows.

* Subsequent anomaly-method calibration notebooks later retained PCA as the operational anomaly representation for DBSCAN, 
Isolation Forest, and GMM workflows.

---

## 3.3.2 Calibrate and Generate DBSCAN Anomalies

### Purpose

Calibrate DBSCAN within the shared anomaly framework established in 3.3.1 and generate candidate mobility-state anomaly surfaces.

### Key Outputs

* Selected DBSCAN configurations
* PCA-based DBSCAN anomaly exports
* Row-level anomaly tables by modality
* Calibration diagnostics
* Stability summaries
* Human-review summaries
* Spatial-review assets
* DBSCAN export manifest

### Key Findings

* Local density heterogeneity is substantially greater in UMAP than PCA.
* UMAP density structure proved difficult to calibrate consistently across modalities.
* PCA produced more stable and interpretable density behavior.
* eps emerged as the primary DBSCAN stability lever.
* min_samples acted primarily as a refinement parameter.
* Retained PCA configurations generated structured, interpretable anomaly surfaces suitable for downstream comparison.
* Human-review and aggregate-review workflows supported carrying DBSCAN anomaly outputs forward as candidate anomaly surfaces.

### Spatial Review Findings

* Bus anomalies concentrated heavily in Jamaica and eastern Queens.
* Subway anomalies concentrated strongly in Manhattan core zones.
* Taxi anomalies exhibited a mixed airport and Manhattan-core pattern.
* FHVHV anomalies were heavily airport-oriented.
* Multimodal anomalies exhibited strong Queens concentration with a smaller Manhattan-core component.

### Regime Review Findings

* Subway anomalies were highly concentrated within selected CBD peak regimes.
* Taxi anomalies were elevated in gateway-adjacent regimes.
* Bus, FHVHV, and Multimodal anomalies exhibited more moderate but still clearly non-uniform concentration patterns.

### Important Decisions

* UMAP retired as a DBSCAN representation.

* DBSCAN advances using PCA representations only.

* This became the first anomaly-generation notebook to retire UMAP operationally, although UMAP remained under evaluation at the 
broader anomaly-framework level until later notebooks were completed.

* Final retained configurations:

  * Bus: min_samples = 15, balanced eps band
  * Subway: min_samples = 15, balanced eps band
  * Taxi: min_samples = 20, tight eps band
  * FHVHV: min_samples = 15, balanced eps band
  * Multimodal: min_samples = 15, balanced eps band

* DBSCAN anomaly outputs should be treated as candidate anomaly surfaces rather than final validated anomalies.


---

## 3.3.3 Calibrate and Generate Isolation Forest Anomalies

### Purpose

Calibrate Isolation Forest within the shared anomaly framework established in 3.3.1 and generate candidate isolation-based mobility-state anomaly surfaces.

### Key Outputs

* PCA-based Isolation Forest anomaly exports
* Contamination-calibration diagnostics
* Framework-comparison diagnostics
* Aggregate-review summaries

### Key Findings

* Isolation Forest does not rely on density-homogeneity assumptions and therefore allowed UMAP to remain under evaluation during calibration.
* PCA consistently produced stronger and more interpretable anomaly structure than UMAP.
* Contamination behaved primarily as an anomaly-volume control lever.
* Lower contamination levels preserved stronger anomaly-tail separation.
* Isolation Forest produced anomaly surfaces that were meaningfully different from DBSCAN rather than simply reproducing density-based anomalies.
* Aggregate coherence review supported carrying Isolation Forest outputs forward into downstream framework comparison.

### Important Decisions

* UMAP retired for Isolation Forest.
* Isolation Forest advances using PCA only.
* Final retained contamination:

  * 0.005

* One retained PCA-based configuration selected per modality.

---

## 3.3.4 Calibrate and Generate Gaussian Mixture Model Anomalies

### Purpose

Calibrate Gaussian Mixture Models within the shared anomaly framework established in 3.3.1 and generate probabilistic mobility-state anomaly surfaces.

### Key Outputs

* PCA-based GMM anomaly exports
* Structure-calibration diagnostics
* Tail-calibration diagnostics
* Framework-comparison diagnostics
* Aggregate-review summaries

### Key Findings

* GMM served as the project's probabilistic anomaly-detection framework.
* Raw Scaled did not re-enter evaluation.
* UMAP did not re-enter evaluation.
* All candidate structures converged successfully.
* Full covariance consistently outperformed diagonal covariance.
* Threshold 0.005 produced the strongest anomaly-tail separation.
* GMM contributed anomaly structure that was not fully redundant with either DBSCAN or Isolation Forest.
* Aggregate coherence review supported carrying GMM outputs forward into downstream framework comparison.

### Important Decisions

* GMM advances using PCA only.
* Full covariance retained.
* Tail threshold retained:

  * 0.005

* Final retained configurations:

  * Bus: k = 3
  * Subway: k = 3
  * Taxi: k = 3
  * FHVHV: k = 2
  * Multimodal: k = 2

---

## 3.3.5 Compare Candidate Anomaly Frameworks

### Purpose

Synthesize retained DBSCAN, Isolation Forest, and Gaussian Mixture Model anomaly outputs into a unified downstream anomaly package and establish the anomaly surfaces that should advance into evaluation, interpretation, and social-data integration workflows.

### Key Outputs

* framework_comparison_full_row_universe.parquet
* retained_anomaly_working_table.parquet
* retained_positive_direction_working_table.parquet
* consensus_anomaly_indicators.parquet
* directional_anomaly_labels.parquet
* framework_specific_anomaly_flags.parquet
* modality_participation_indicators.parquet
* retained_social_join_focus_table.parquet
* framework_synthesis_handoff_manifest.csv

### Key Findings

* DBSCAN, Isolation Forest, and GMM are complementary rather than redundant anomaly frameworks.
* Multi-method agreement is selective rather than universal.
* Congestion-oriented anomalies exhibit stronger framework agreement than the anomaly universe overall.
* Directionality emerged as a first-class interpretive layer.
* Positive-direction anomalies became substantially more important than originally anticipated.
* Multimodal anomalies provide useful context but do not replace modality-specific participation information.
* Retained anomalies are better interpreted as recurring mobility events than generic statistical outliers.

### Important Decisions

* Broad retained anomaly universe:

  * retained_anomaly_union

* Primary directional lenses:

  * congestion_oriented
  * positive_demand_shock

* Consensus indicators, directional labels, framework-specific flags, and modality participation indicators are retained for downstream interpretation.

* The anomaly package advances into downstream evaluation as a layered interpretation framework rather than a single anomaly surface.

* Positive-direction anomalies become a major downstream analysis branch.

---

## 3.4.1 Evaluate Final Anomaly Surfaces

### Purpose

Evaluate the retained anomaly package for recurrence, persistence, consensus behavior, directional structure, policy relevance, and external validity before downstream social integration and final interpretation.

### Key Outputs

* Recurrence diagnostics
* Persistence diagnostics
* Consensus evaluation summaries
* Directional evaluation summaries
* Policy-geography evaluation summaries
* Crash-validation summaries
* Final anomaly-surface recommendations

### Key Findings

* Retained anomalies exhibit strong recurrence and persistence when evaluated within local operating contexts.
* Positive-direction anomalies remain highly recurrent while becoming substantially more selective than the full anomaly union.
* Consensus refinement introduces meaningful confidence-versus-coverage tradeoffs.
* Two-method consensus preserves useful coverage while improving anomaly quality.
* Three-method consensus becomes overly restrictive and loses useful signal.
* Positive-direction anomalies align more strongly with crash activity than the retained anomaly union.
* Positive-demand-shock anomalies exhibit the strongest crash enrichment among evaluated directional lenses.
* Congestion-oriented anomalies remain useful for interpretation but exhibit weaker external validation performance.

### Important Decisions

* Broad reference surface:

  * retained_anomaly_union

* Preferred working anomaly surface:

  * retained_positive_direction_subset

* Preferred high-confidence anomaly core:

  * positive_direction | 2+ methods consensus

* Robustness-only refinement:

  * positive_direction | 3 methods consensus

* Recurrence and persistence become core anomaly-evaluation metrics.

* External validation using NYC crash events becomes part of the project's anomaly-evaluation framework.

* Positive-direction anomalies become the primary downstream anomaly package for interpretation and social integration workflows.
