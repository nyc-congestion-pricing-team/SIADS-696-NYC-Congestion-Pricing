# PROJECT_SPEC.md

# NYC Congestion Pricing Mobility Analytics Project

Last Updated: 2026-06-13

---

# 1. Project Overview

## Project Objective

This project evaluates the effects of New York City's Central Business District Tolling Program (CBDTP), commonly known as congestion pricing, using a multimodal mobility-state framework constructed from roadway, transit, and for-hire transportation systems.

Rather than focusing on individual trips, riders, vehicles, or roadway observations, the project seeks to model the overall transportation state of each area of the city at a given point in time. The resulting mobility-state representations are used to study congestion-pricing impacts, discover latent mobility regimes, identify unusual transportation conditions, and support future forecasting and policy-analysis workflows.

Primary analytical goals include:

* Measuring how mobility patterns changed following congestion pricing.
* Understanding the relationships between transportation systems.
* Discovering latent mobility-state structure through representation learning.
* Identifying anomalous mobility states across NYC.
* Supporting future forecasting, causal analysis, and counterfactual evaluation workflows.
* Producing interpretable evidence regarding congestion-pricing impacts across neighborhoods and transportation systems.

---

## Canonical Analytical Grain

The canonical observation unit used throughout the project is:

**Taxi Zone × Date × Temporal Bucket**

Each record represents the observed mobility state of a Taxi Zone during a specific date and temporal bucket.

This grain is preserved throughout:

* Mobility-layer construction
* Feature engineering
* Representation learning
* Clustering
* Anomaly detection
* Visualization
* Congestion-pricing interpretation

Maintaining a consistent analytical grain across transportation systems is one of the core architectural principles of the project.

---

## Canonical Geometry Asset

Downstream anomaly mapping, anomaly visualization, and spatial-review workflows should use:

`1.3.1.final_tables/nyc_taxi_zones_harmonized.parquet`

rather than raw staging geometry assets.

This geometry asset incorporates the project's harmonized Taxi Zone handling and should be considered the authoritative spatial reference layer for downstream analysis.


---
## Modeling Philosophy

The project is intentionally structured around **mobility states** rather than individual transportation events.

The objective is not to determine whether a specific taxi trip, subway rider, or traffic observation is unusual. Instead, the objective is to determine whether the overall transportation conditions observed within a Taxi Zone during a specific period appear unusual relative to expected behavior.

This distinction influences nearly every downstream modeling decision, including:

* Feature engineering
* Representation learning
* Clustering
* Density estimation
* Anomaly detection

The project therefore treats transportation systems as complementary signals describing the same underlying mobility state.

---

## Representation Learning Philosophy

Representation learning and anomaly detection are treated as separate stages.

Representation-learning notebooks seek to answer:

* How does mobility behavior organize itself in feature space?
* Does the feature space compress effectively?
* What latent mobility dimensions exist?
* Which transportation systems contribute most strongly to observed structure?

Anomaly-detection notebooks seek to answer:

* Which mobility states are unusual?
* Which locations exhibit abnormal behavior?
* Which transportation systems contribute to those anomalies?

By separating representation learning from anomaly scoring, the project preserves interpretability and allows multiple anomaly-detection approaches to operate on the same mobility-state representations.

---

## Congestion-Pricing Philosophy

The project treats congestion pricing as an important explanatory variable rather than the sole organizing principle of the analysis.

Although the study ultimately seeks to understand congestion-pricing impacts, the representation-learning pipeline is designed to discover transportation structure without explicitly forcing congestion-pricing outcomes.

This allows the project to answer questions such as:

* Do congestion-pricing effects emerge naturally in latent space?
* Which transportation systems appear most affected?
* Are observed mobility changes geographically concentrated?
* Do mobility states reorganize following implementation?

---

# 2. Study Scope and Standards

## Study Period

The standardized study period spans:

**2023-01-01 through 2026-03-31**

This period provides:

* Approximately two years of pre-congestion-pricing observations.
* Approximately fifteen months of post-congestion-pricing observations.
* Sufficient history for temporal feature engineering and decomposition workflows.

The study period was standardized across transportation systems to maximize comparability and simplify downstream modeling.

---

## Congestion Pricing Boundary

The official congestion-pricing implementation date used throughout the project is:

**2025-01-05**

All observations are assigned one of two canonical labels:

* pre_cp
* post_cp

These labels are used consistently throughout:

* Feature engineering
* Representation learning
* Visualization
* Interpretation
* Future causal-analysis workflows

---

## Temporal Standard

Transportation systems report activity at different temporal resolutions.

To harmonize these sources, all observations are assigned to one of ten canonical temporal buckets:

### Weekday

* weekday_am_peak
* weekday_midday
* weekday_pm_peak
* weekday_evening
* weekday_overnight

### Weekend

* weekend_am_peak
* weekend_midday
* weekend_pm_peak
* weekend_evening
* weekend_overnight

This temporal standard is applied consistently across all mobility systems.

The temporal-bucket framework provides a common behavioral representation that is substantially more interpretable than raw hourly timestamps while preserving meaningful differences between commuting, daytime, evening, and overnight activity patterns.

---

## Spatial Standard

The canonical geographic unit is the NYC Taxi Zone system.

Reasons for choosing Taxi Zones include:

* Existing use throughout TLC datasets.
* Citywide coverage.
* Reasonable neighborhood-level resolution.
* Compatibility with transportation datasets.
* Suitability for map-based visualization.

All mobility systems are ultimately transformed into Taxi Zone observations before entering the integrated mobility layer.

---

## Congestion Pricing Geography

Several spatial classifications are used throughout the project:

### Congestion Pricing Zone

Zones are classified according to whether they lie within the congestion-pricing area.

### CBD Context

Spatial feature engineering introduces CBD-oriented indicators describing:

* CBD membership
* CBD adjacency
* CBD distance relationships

### Gateway Zones

Gateway zones represent major bridge and tunnel landing areas that may experience spillover effects following congestion pricing.

### Transportation Connectivity Network

A transportation-aware network is used throughout spatial feature engineering.

The network combines:

* Geographic adjacency
* Major bridge connections
* Major tunnel connections

This network forms the basis for spillover and connected-neighbor features.

---

# 3. Dataset Registry

## Traffic

### Source

NYC Department of Transportation Traffic Volume Counts

### Purpose

Provides roadway traffic-volume measurements across portions of the city.

### Important Characteristics

* Sparse geographic coverage.
* Irregular temporal coverage.
* Observation dates are not uniformly distributed.
* Sampling behavior varies substantially across locations.

### Important Project Decision

Traffic is retained for:

* Contextual interpretation
* Future supervised-learning workflows
* Congestion validation analyses

Traffic is excluded from default unsupervised modeling feature spaces because its coverage characteristics differ substantially from the remaining transportation systems.

---

## Bus

### Source

MTA Bus Time and bus-speed datasets.

### Purpose

Provides surface-transit demand and mobility-condition signals.

### Key Contributions

* Broad geographic coverage.
* Surface mobility information.
* Bus-speed measurements.
* Bus-demand measurements.

Bus is one of the primary transportation modalities used throughout downstream modeling.

---

## Subway

### Source

MTA Turnstile and ridership datasets.

### Purpose

Provides rail-transit demand information.

### Key Contributions

* High-volume transit demand signal.
* Strong Manhattan coverage.
* Complementary mobility information not captured by roadway systems.

### Important Limitation

Subway coverage is structurally absent in many Taxi Zones.

The absence of subway observations in those areas is treated as a valid geographic condition rather than a data-quality problem.

---

## Taxi

### Sources

NYC TLC Yellow Taxi datasets

NYC TLC Green Taxi datasets

### Purpose

Provides for-hire demand and mobility information.

### Important Project Decision

Taxi is defined as:

**Yellow Taxi + Green Taxi**

The project intentionally combines these systems into a single Taxi modality.

### Key Contributions

* Near-citywide coverage.
* Strong demand signal.
* Trip-volume measures.
* Mobility-condition measures.

Taxi serves as one of the primary mobility-state modalities.

---

## FHV

### Sources

NYC TLC For-Hire Vehicle datasets

### Important Project Decision

FHV is excluded from downstream modeling.

Reason:

Severe geographic incompleteness and inconsistent coverage patterns reduce its usefulness as a citywide mobility-state signal.

FHV remains part of the historical ingestion record but is not considered a canonical modeling modality.

---

## FHVHV

### Sources

NYC TLC High-Volume For-Hire Vehicle datasets

### Purpose

Provides large-scale ride-hailing demand and mobility information.

### Key Contributions

* Citywide demand coverage.
* Complementary information relative to Taxi.
* Strong post-pandemic transportation signal.

FHVHV remains the primary for-hire mobility modality alongside Taxi.

---

## Bridge & Tunnel

### Sources

MTA Bridges and Tunnels datasets

### Purpose

Provides vehicle-crossing volumes through major bridge and tunnel facilities.

### Role in the Project

Bridge and tunnel observations are not modeled as a standalone transportation modality.

Instead, they are incorporated through engineered contextual and interaction features describing:

* Regional mobility pressure.
* Manhattan connectivity.
* Cross-borough travel conditions.

---

## NYC Taxi Zones

### Purpose

Provides the canonical geographic reference layer.

### Responsibilities

* Spatial joins.
* Distance calculations.
* Adjacency relationships.
* Spatial visualization.
* Connectivity-network construction.

All downstream mobility systems ultimately align to this spatial framework.

---

# 4. Pipeline Architecture

## Architectural Philosophy

The project follows a staged, checkpoint-driven architecture designed to maximize:

* Reproducibility
* Interpretability
* Computational efficiency
* Notebook modularity
* Human-in-the-loop review

The pipeline is intentionally divided into distinct stages so that expensive operations can be reused without requiring repeated full-pipeline execution.

---

## Pipeline Stages

### 1.1 Source Acquisition and Staging

Objectives:

* Acquire source datasets.
* Standardize schemas.
* Perform initial QA.
* Produce staged parquet assets.

---

### 1.2 Standardization and Harmonization

Objectives:

* Standardize temporal structures.
* Standardize spatial structures.
* Create harmonized mobility tables.
* Establish canonical analytical standards.

---

### 1.3 Integrated Mobility Layer

Objectives:

* Merge transportation systems.
* Construct the unified mobility panel.
* Establish the canonical Taxi Zone × Date × Temporal Bucket grain.

---

### 1.5 Feature Engineering

Objectives:

* Create temporal-history features.
* Create spatial-context features.
* Create multimodal interaction features.
* Create decomposition features.
* Create anomaly-oriented features.
* Select final modeling features.

---

### 3.1 Modeling Matrix Construction

Objectives:

* Construct modality-specific modeling matrices.
* Handle missingness policies.
* Scale modeling features.
* Produce model-ready datasets.

---

### 3.2 Representation Learning

Objectives:

* Evaluate PCA representations.
* Evaluate nonlinear embeddings.
* Compare candidate representation spaces.
* Select downstream representations.

---

### 3.3 Clustering and Anomaly Detection

Objectives:

* Establish anomaly-detection frameworks.
* Calibrate DBSCAN, Isolation Forest, and Gaussian Mixture Models.
* Compare candidate anomaly-generation methods.
* Construct a unified anomaly-synthesis package.
* Generate consensus, directional, and modality-participation anomaly layers.
* Produce downstream anomaly handoff assets.

---

### 4.x Interpretation and Reporting

Objectives:

* Interpret mobility-state structure.
* Evaluate congestion-pricing impacts.
* Produce visualizations.
* Support final report generation.

---

## Execution Principles

The project operates primarily within Deepnote and follows several execution conventions:

* Raw datasets remain immutable.
* Expensive operations use rebuild toggles.
* Intermediate outputs are checkpointed to parquet.
* DuckDB is preferred for large-scale processing.
* Pandas is preferred for QA, visualization, and modeling workflows.
* One code block should perform one clear task whenever practical.
* Findings are written only after results exist.

These conventions evolved throughout the project and have become standard practice across all notebooks.

# 5. Notebook History

This section documents the evolution of the project pipeline, major accomplishments within each notebook, important decisions that affected downstream work, and the key outputs produced by each phase.

The purpose of this section is not to reproduce implementation details. Instead, it serves as a historical record explaining how the current mobility-state framework was constructed and why major architectural decisions were made.

---

# 5.1 Source Acquisition and Staging (1.1.x)

The Source Acquisition and Staging phase established the raw data foundation for the project. Each transportation system was ingested independently, standardized into staged parquet assets, subjected to initial quality assurance procedures, and prepared for downstream harmonization.

A guiding principle during this phase was preservation of source fidelity. Raw datasets were retained in their original form whenever possible, while staging outputs focused on schema standardization, quality checks, and efficient parquet-based storage.

---

## 5.1.1 Traffic Dataset Acquisition and QA

### Purpose

Acquire and validate roadway traffic-volume observations for use as a contextual transportation signal.

### Major Accomplishments

* Ingested NYC traffic-volume observations.
* Standardized schemas and timestamp fields.
* Performed temporal coverage assessment.
* Performed geographic coverage assessment.
* Identified observation-frequency patterns.
* Created staged traffic parquet assets.

### Key Findings

Traffic observations exhibited substantially different characteristics from the remaining transportation systems.

Important observations included:

* Sparse geographic coverage.
* Irregular temporal sampling.
* Non-uniform observation schedules.
* Significant gaps between observations in many locations.

These characteristics ultimately influenced later modeling decisions.

### Important Downstream Decision

Traffic remained valuable for contextual interpretation and future supervised-learning workflows but was deemed unsuitable as a default unsupervised modeling modality.

This decision continues to influence all downstream representation-learning and anomaly-detection workflows.

### Key Outputs

* Staged traffic dataset.
* Traffic QA summaries.
* Traffic coverage assessments.

---

## 5.1.2 TLC Taxi and FHVHV Acquisition and QA

### Purpose

Acquire and validate NYC Taxi and FHVHV transportation activity datasets.

### Major Accomplishments

* Ingested Yellow Taxi data.
* Ingested Green Taxi data.
* Ingested FHV data.
* Ingested FHVHV data.
* Standardized source schemas.
* Evaluated spatial coverage.
* Evaluated temporal coverage.
* Created staged parquet assets.

### Key Findings

Taxi and FHVHV provided the most comprehensive citywide mobility coverage among the transportation systems studied.

FHV exhibited substantial geographic incompleteness.

### Important Downstream Decisions

Taxi was defined as:

Yellow Taxi + Green Taxi

FHV was excluded from downstream modeling because geographic coverage limitations significantly reduced its value as a citywide mobility-state signal.

FHVHV was retained as the primary for-hire transportation modality.

### Key Outputs

* Staged Taxi datasets.
* Staged FHVHV datasets.
* Coverage assessments.
* Initial mobility summaries.

---

## 5.1.3 Subway Dataset Acquisition and QA

### Purpose

Acquire and validate subway ridership data for use as a transit-demand signal.

### Major Accomplishments

* Ingested subway ridership files.
* Standardized quarterly source structures.
* Evaluated station coverage.
* Evaluated temporal coverage.
* Created staged subway assets.

### Key Findings

Subway ridership provided a high-volume transit-demand signal with strong Manhattan coverage and substantial value for congestion-pricing analysis.

However, many Taxi Zones lack subway infrastructure entirely.

### Important Downstream Decision

The absence of subway observations in many Taxi Zones was treated as a valid geographic condition rather than a data-quality issue.

This distinction later became important during modeling-matrix construction and missingness handling.

### Key Outputs

* Staged subway datasets.
* Station coverage summaries.
* Ridership QA outputs.

---

## 5.1.4 Bus Dataset Acquisition and QA

### Purpose

Acquire and validate bus-demand and bus-speed datasets.

### Major Accomplishments

* Ingested bus ridership and bus-speed sources.
* Standardized route-level structures.
* Evaluated coverage.
* Created staged bus assets.

### Key Findings

Bus observations provided substantially broader geographic coverage than traffic and subway datasets.

Bus data offered a valuable surface-transportation perspective not captured by rail systems.

### Key Outputs

* Staged bus datasets.
* Bus coverage assessments.
* Initial QA summaries.

---

## 5.1.5 Bridge and Tunnel Dataset Acquisition and QA

### Purpose

Acquire vehicle-crossing observations from major MTA bridge and tunnel facilities.

### Major Accomplishments

* Ingested MTA bridge-and-tunnel datasets.
* Standardized facility structures.
* Standardized directional observations.
* Evaluated temporal coverage.

### Key Findings

Bridge-and-tunnel crossings provide a useful regional mobility signal and may capture mobility redistribution following congestion pricing.

### Important Downstream Decision

Bridge-and-tunnel data would not become a standalone transportation modality.

Instead, it would later be incorporated through engineered interaction and contextual features.

### Key Outputs

* Staged bridge-and-tunnel datasets.
* Facility summaries.
* Crossing-volume QA outputs.

---

## 5.1.6 Taxi Zone Reference Layer

### Purpose

Create the canonical geographic reference layer used throughout the project.

### Major Accomplishments

* Acquired Taxi Zone geometries.
* Standardized coordinate systems.
* Validated geometry integrity.
* Identified multipart geometries.
* Established canonical spatial reference assets.

### Important Findings

Several Taxi Zones required special handling because of multipart geometry structures.

Examples included:

* Governor's Island / Ellis Island / Liberty Island.
* Corona.

### Important Downstream Decision

Canonical geometry handling procedures were established and later reused throughout spatial standardization and feature engineering workflows.

### Key Outputs

* Harmonized Taxi Zone reference layer.
* Geometry QA outputs.
* Canonical spatial reference assets.

---

# 5.2 Standardization and Harmonization (1.2.x)

The Standardization and Harmonization phase transformed transportation-system-specific datasets into a common analytical framework.

This phase established the project's canonical temporal, spatial, and policy-period standards and represents one of the most important architectural stages in the pipeline.

---

## 5.2.1 Temporal Standardization

### Purpose

Create a consistent temporal framework across all transportation systems.

### Major Accomplishments

* Standardized timestamps.
* Created canonical date fields.
* Created temporal-bucket assignments.
* Created congestion-pricing-period labels.
* Unified temporal naming conventions.

### Important Findings

Transportation systems varied substantially in temporal granularity and reporting conventions.

The temporal-bucket framework provided a common behavioral representation that preserved meaningful commuting and activity patterns while reducing temporal complexity.

### Key Outputs

* Temporally standardized datasets.
* Temporal QA summaries.
* Canonical temporal-bucket assignments.

---

## 5.2.2 Spatial Standardization

### Purpose

Transform transportation-system observations into Taxi Zone geography.

### Major Accomplishments

* Assigned observations to Taxi Zones.
* Standardized coordinate systems.
* Created spatial assignment methodologies.
* Evaluated assignment quality.
* Generated spatial QA outputs.

### Important Findings

Transportation systems required substantially different spatial assignment strategies.

Coverage differences across systems became apparent during this phase and informed later feature-engineering and modeling decisions.

### Key Outputs

* Spatially standardized datasets.
* Spatial assignment QA summaries.
* Taxi Zone-aligned transportation observations.

---

## 5.2.3 TLC Mobility Table Construction

### Purpose

Convert raw TLC observations into Taxi Zone × Date × Temporal Bucket mobility tables.

### Major Accomplishments

* Aggregated Taxi activity.
* Aggregated FHVHV activity.
* Standardized mobility metrics.
* Constructed transportation-system mobility tables.

### Important Findings

Taxi and FHVHV exhibited near-citywide coverage and became the strongest citywide mobility-demand signals available in the project.

### Key Outputs

* Taxi mobility tables.
* FHVHV mobility tables.
* Mobility QA summaries.

---

## 5.2.4 Harmonized Mobility Tables

### Purpose

Construct harmonized mobility tables across all transportation systems using the project's canonical analytical standards.

### Major Accomplishments

* Unified temporal standards.
* Unified spatial standards.
* Unified policy-period standards.
* Harmonized mobility metrics.
* Generated transportation-system mobility tables suitable for integration.

### Important Findings

The various transportation systems provide complementary geographic coverage rather than redundant coverage.

Key observations:

* Traffic provides limited geographic coverage.
* Subway provides moderate geographic coverage.
* Bus provides broad geographic coverage.
* Taxi and FHVHV provide near-citywide coverage.

The complementary nature of these systems became one of the primary motivations for constructing a multimodal mobility-state framework.

### Important Downstream Decision

System-specific coverage limitations should not automatically be interpreted as missing data problems.

This principle later influenced matrix-construction and anomaly-detection design decisions.

### Key Outputs

* Harmonized traffic mobility tables.
* Harmonized bus mobility tables.
* Harmonized subway mobility tables.
* Harmonized Taxi mobility tables.
* Harmonized FHVHV mobility tables.

---

# 5.3 Integrated Mobility Layer (1.3.1)

### Purpose

Create a unified multimodal mobility panel representing transportation conditions across NYC.

### Major Accomplishments

* Integrated all transportation systems.
* Established the canonical Taxi Zone × Date × Temporal Bucket analytical grain.
* Constructed dense and sparse mobility panels.
* Standardized multimodal observations.
* Created final mobility-layer assets.

### Important Findings

The multimodal integration process revealed substantial differences in transportation-system coverage patterns.

No individual transportation system provides complete visibility into citywide transportation behavior.

However, when combined, the transportation systems create a substantially richer representation of mobility conditions than any modality alone.

### Important Architectural Decision

The dense mobility panel became the foundation for all subsequent feature-engineering workflows.

This ensured that downstream modeling operated from a consistent citywide observation universe.

### Key Outputs

* Analysis-ready mobility panel.
* Audit mobility panel.
* Bridge-and-tunnel mobility panel.
* Harmonized Taxi Zone reference layer.

### Legacy Significance

Notebook 1.3.1 established the canonical mobility-state framework used throughout the remainder of the project and serves as the foundation for all subsequent feature engineering, representation learning, clustering, and anomaly-detection workflows.

# 5.4 Feature Engineering History (1.5.x)

The Feature Engineering phase transformed the integrated mobility panel into a modeling-ready representation of transportation conditions across NYC.

Rather than relying solely on observed mobility measurements, the project introduced engineered features describing temporal history, spatial context, multimodal interactions, expected behavior, residual behavior, and anomaly-oriented characteristics.

A key design principle during this phase was the separation of feature generation from feature selection. Broad feature families were initially constructed to maximize flexibility, while downstream notebooks later evaluated redundancy, interpretability, and modeling value.

---

## 5.4.1 Temporal Mobility Features (1.5.1)

### Purpose

Capture recent mobility history and short-term behavioral trends across transportation systems.

### Major Accomplishments

* Created lag features.
* Created rolling-average features.
* Created rolling-variability features.
* Created exponential moving averages.
* Created rate-of-change features.
* Created congestion-pricing comparison features.

### Feature Families

Temporal-history features included:

* Lagged values
* Rolling means
* Rolling standard deviations
* Exponential moving averages
* Absolute changes
* Percentage changes

### Important Findings

Traffic behaved fundamentally differently from the remaining transportation systems because observations occurred on an irregular schedule.

### Important Decision

Traffic-specific temporal features were engineered separately using observation-aware methods rather than treating missing dates as missing observations.

This decision remained important throughout downstream traffic analysis.

### Key Output

* Temporal mobility feature panel

---

## 5.4.2 Spatial Mobility Features (1.5.2)

### Purpose

Capture geographic context surrounding each Taxi Zone.

### Major Accomplishments

* Created CBD indicators.
* Created gateway indicators.
* Created adjacency indicators.
* Created spillover features.
* Created borough context features.
* Created congestion-pricing-zone context features.

### Transportation Connectivity Network

A transportation-aware connectivity network was developed using:

* Polygon adjacency
* Major bridge connections
* Major tunnel connections

This network enabled spillover calculations that reflected actual transportation relationships rather than simple geographic proximity.

### Important Findings

Transportation spillovers frequently occur across bridge and tunnel corridors that would not be captured through adjacency alone.

### Important Decision

Transportation-aware connectivity became the canonical network used for all downstream spillover calculations.

### Key Output

* Spatial mobility feature panel

---

## 5.4.3 Multimodal Interaction Features (1.5.3)

### Purpose

Capture relationships between transportation systems and introduce broader mobility context.

### Major Accomplishments

* Added bridge-and-tunnel context metrics.
* Added multimodal interaction features.
* Added traffic-specialized sparse features.
* Added connected-system mobility measures.

### Important Findings

Bridge-and-tunnel activity provides useful context regarding regional transportation pressure and Manhattan connectivity.

Traffic required specialized treatment because sparse observations prevented direct application of standard temporal-history techniques.

### Important Decisions

Bridge-and-tunnel activity was incorporated through engineered context variables rather than treated as a standalone modality.

Traffic remained outside the default multimodal representation space.

### Key Output

* Multimodal interaction feature panel

---

## 5.4.4 Decomposition and Residual Features (1.5.4)

### Purpose

Separate expected mobility behavior from unusual mobility behavior.

### Major Accomplishments

* Evaluated decomposition strategies.
* Generated expected-value features.
* Generated residual features.
* Generated standardized residual measures.
* Compared alternative decomposition approaches.

### Modeling Motivation

Raw mobility metrics often reflect predictable temporal patterns rather than genuinely unusual transportation conditions.

Examples include:

* Morning commute peaks
* Evening commute peaks
* Weekend activity differences
* Seasonal effects

Residualization provides a mechanism for identifying behavior that departs from expected patterns.

### Important Findings

Residual-based features often provided clearer anomaly-oriented signals than raw mobility measurements alone.

### Important Decision

Residual and decomposition-derived features were retained as a core feature family for downstream modeling.

### Key Output

* Decomposition and residual feature panel

---

## 5.4.5 Variability and Anomaly-Severity Features (1.5.5)

### Purpose

Capture the degree to which current mobility conditions deviate from historically typical behavior.

### Major Accomplishments

* Created percentile-rank features.
* Created z-score features.
* Created anomaly-severity features.
* Created relative-deviation features.
* Created standardized anomaly indicators.

### Modeling Motivation

The objective was not to label anomalies directly but to create features describing how unusual current conditions appear relative to historical behavior.

### Important Findings

Variability-oriented features provide useful context for downstream anomaly-detection workflows while remaining interpretable.

### Important Decision

These features were retained as an independent feature family rather than folded into decomposition outputs.

### Key Output

* Variability and anomaly feature panel

---

## 5.4.6 Modeling Feature Selection (1.5.6)

### Purpose

Reduce feature redundancy while preserving mobility-state information.

### Major Accomplishments

* Created feature inventory.
* Evaluated feature redundancy.
* Evaluated feature-family contribution.
* Assessed incremental information value.
* Constructed final modeling feature sets.

### Feature-Selection Philosophy

The project intentionally avoided aggressive pruning.

The goal was not to identify the smallest possible feature set but rather to preserve meaningful mobility information while eliminating obvious redundancy.

### Core Mobility Metrics

Seven mobility metrics were identified as the primary mobility-state signals:

* bus_trip_count
* avg_bus_speed
* subway_ridership
* taxi_trip_count
* taxi_avg_trip_speed
* fhvhv_trip_count
* fhvhv_avg_trip_speed

These metrics became protected mobility signals throughout downstream representation-learning and anomaly-detection workflows.

### Important Findings

Many engineered features remained useful even when derived from correlated raw metrics.

Feature-family contribution analysis suggested that temporal, spatial, decomposition, and variability features all contributed 
meaningful structure beyond raw mobility measurements.

### Important Decisions

Feature selection was finalized in 1.5.6.

Downstream notebooks should not reopen feature-selection decisions without compelling evidence.

### Key Outputs

* Modeling feature catalog
* Feature metadata catalog
* Feature-set definitions
* Final selected modeling feature universe

---

# 6. Current Modeling Assets

The outputs of Chapters 1 and 3.1 constitute the canonical modeling inputs for all downstream representation-learning, clustering, and anomaly-detection workflows.

---

## 6.1 Modeling Matrix Construction (3.1.1)

### Purpose

Transform selected features into model-ready matrices.

### Major Accomplishments

* Constructed modality-specific matrices.
* Constructed multimodal matrices.
* Applied missingness policies.
* Applied feature scaling.
* Created metadata-preserving modeling assets.

### Canonical Modalities

* Bus
* Subway
* Taxi
* FHVHV
* Multimodal

### Important Modeling Philosophy

Transportation-system absence is not automatically a data-quality problem.

Examples:

* A Taxi Zone without subway service should not be discarded because subway observations are unavailable.
* Sparse Taxi activity may itself represent meaningful transportation behavior.

This principle guided missingness handling throughout matrix construction.

### Important Decisions

Traffic remained outside the default unsupervised feature space.

Missingness indicators remained available for auditability and sensitivity testing.

### Key Outputs

* Raw modeling matrices
* Scaled modeling matrices
* Metadata tables
* Scaling metadata
* QA summaries

---

## 6.2 Representation Policy

Current representation-learning policy:

### Bus

Use full selected feature space.

### Subway

Use full selected feature space.

### Taxi

Use mobility-only features.

Exclude missingness indicators.

### FHVHV

Use mobility-only features.

Exclude missingness indicators.

### Multimodal

Use mobility-only features.

Exclude missingness indicators.

This policy emerged from representation-learning analyses conducted in Chapter 3.

Although PCA and UMAP were initially advanced into downstream anomaly-framework evaluation, subsequent anomaly-generation notebooks retained PCA as the operational anomaly-generation representation across DBSCAN, Isolation Forest, and Gaussian Mixture Model workflows.

UMAP remains an important nonlinear representation-learning asset but is no longer a retained anomaly-generation representation.

---

# 7. Representation Learning History

Representation learning seeks to understand the structure of mobility-state space before introducing clustering or anomaly-detection methods.

---

## 7.1 PCA Exploration (3.2.1)

### Purpose

Evaluate whether mobility-state feature spaces compress into meaningful lower-dimensional representations.

### Major Accomplishments

* Evaluated PCA compressibility.
* Evaluated explained variance.
* Interpreted PCA loadings.
* Visualized latent mobility structure.
* Evaluated missingness-indicator sensitivity.

### Major Findings

Single-modality feature spaces compress reasonably well.

Multimodal feature spaces are more diffuse but remain interpretable.

Leading principal components correspond to meaningful mobility phenomena rather than artifacts.

Borough structure is visible within PCA space.

Congestion-pricing-period separation is relatively weak.

### Important Decision

Missingness indicators were excluded from default Taxi, FHVHV, and Multimodal PCA representations.

### Key Outputs

* PCA scores
* PCA loadings
* Explained-variance summaries
* PCA QA assets

---

## 7.2 PCA Stability Analysis (3.2.2)

### Purpose

Evaluate whether PCA structure remains stable across pre- and post-congestion-pricing periods.

### Major Findings

Bus:

* Stable

Subway:

* Moderately stable

Taxi:

* Exhibits greater PC2/PC3 instability

FHVHV:

* Stable

Multimodal:

* Stable

### Important Decision

Full-period PCA remains the canonical linear representation for representation-learning workflows.

Taxi exhibited greater policy-period instability than the remaining modalities. Although full-period PCA 
remains appropriate for representation-learning analyses, downstream anomaly-framework evaluation demonstrated 
sufficient differences between pre- and post-congestion-pricing Taxi structure to justify exporting and retaining 
Taxi-specific pre/post PCA representations for anomaly-detection workflows.

### Key Outputs

* Stability diagnostics
* Pre/post PCA comparisons
* Stability summaries
* Taxi pre-congestion-pricing PCA modeling scores
* Taxi post-congestion-pricing PCA modeling scores

---

## 7.3 UMAP and t-SNE Exploration (3.2.3)

### Purpose

Explore nonlinear mobility-state structure.

### Major Accomplishments

* Evaluated UMAP sensitivity.
* Evaluated t-SNE structure.
* Compared nonlinear embeddings.
* Identified candidate UMAP configurations.

### Major Findings

Congestion-pricing geography is the strongest nonlinear organizing structure.

Borough structure remains visible.

Daypart structure is relatively weak.

Pre/post congestion-pricing-period structure is relatively weak.

t-SNE broadly confirms major UMAP neighborhood patterns.

### Selected Visualization UMAP

* n_neighbors = 50
* min_dist = 0.10
* metric = euclidean
* random_state = 42

### Important Decision

The selected 2D UMAP representation is considered a visualization asset rather than automatically becoming the preferred anomaly-detection representation.

### Key Outputs

* UMAP embeddings
* t-SNE embeddings
* Embedding comparison assets

---

## 7.4 Representation Comparison (3.2.4)

### Purpose

Compare candidate representation spaces prior to downstream anomaly detection.

### Major Accomplishments

* Compared Raw Scaled, PCA-reduced, and UMAP representations.
* Compared Raw→UMAP and PCA→UMAP workflows.
* Evaluated neighborhood preservation, trustworthiness, density behavior, and representation practicality.
* Evaluated candidate UMAP dimensionalities.
* Selected downstream anomaly-detection representations.

### Major Findings

PCA consistently provided the strongest fidelity-preserving reduced representation across modalities.

UMAP introduced meaningful nonlinear structure but generally preserved local neighborhoods less faithfully than PCA.

Raw Scaled and PCA representations produced highly similar neighborhood structure and anomaly-like behavior across most modalities.

UMAP generated a distinct nonlinear anomaly surface that remained geographically and temporally coherent rather than appearing as random fragmentation.

The Subway modality exhibited the smallest differences between PCA and UMAP behavior, while FHVHV and Multimodal exhibited the largest differences.

### Important Decisions

Downstream anomaly workflows will operate on:

* pca_80pct
* umap_pca_to_umap_10d

Raw Scaled remains an important reference representation but is no longer treated as a standalone anomaly-generation branch.

The selected nonlinear workflow is:

* PCA → UMAP
* 10-dimensional UMAP
* PCA dimensionality selected separately for each modality using the 80% cumulative explained variance threshold

Selected PCA dimensionalities:

* Bus: 14
* Subway: 11
* Taxi: 15
* FHVHV: 13
* Multimodal: 46

Full-dataset UMAP assets are generated using a sample-fit / full-transform workflow:

* Fit on shared 50K evaluation sample
* Transform full datasets in chunks
* Avoid full-panel UMAP refits

### Key Outputs

* PCA modeling representations
* UMAP modeling representations
* Representation-quality diagnostics
* Representation-comparison assets
* Downstream anomaly-representation recommendations

## 7.5 Anomaly Framework Preparation (3.3.1)

### Purpose

Establish the shared anomaly-detection framework inherited by all downstream anomaly-generation notebooks.

### Major Accomplishments

* Evaluated alternative anomaly comparison universes.
* Evaluated temporal-bucket-aware anomaly scoring.
* Evaluated geography-aware anomaly scoring.
* Assessed mobility-state self-normalization behavior.
* Compared anomaly-like behavior across candidate representations.
* Established shared anomaly-framework defaults.
* Selected downstream anomaly representations and comparison universes.

### Major Findings

Global representations remained suitable for representation learning and dimensionality reduction.

However, anomaly scoring benefited from additional context-aware comparison universes.

Temporal-bucket-aware scoring substantially improved anomaly interpretability relative to fully global comparisons.

Geography-aware scoring further reduced concentration of anomaly-like behavior within major Manhattan mobility hubs 
and high-activity regions.

Raw and PCA anomaly-like behavior exhibited substantial overlap across modalities.

UMAP produced a distinct but coherent anomaly surface that appeared to capture complementary nonlinear mobility 
behavior.

### Important Decisions

Shared anomaly calibration samples are constructed using:

* 50,000 observations per modality
* Stratified by temporal bucket
* Stratified by congestion-pricing period

The preferred downstream anomaly comparison universe is:

* same_temporal_bucket_and_policy_geography

A Taxi-specific diagnostic comparison universe is retained:

* same_temporal_bucket_and_pre_post_cp

Downstream anomaly workflows inherit:

* pca_80pct as the primary linear representation
* umap_pca_to_umap_10d as the nonlinear representation

Raw Scaled remains available as an upstream reference surface but is no longer treated as a primary anomaly-generation branch.

Taxi retains split pre/post congestion-pricing PCA representations for downstream anomaly workflows.

Representation learning and anomaly scoring are treated as separate modeling problems. Global representations remain acceptable, 
while anomaly scoring is evaluated using context-aware comparison universes.

### Key Outputs

* Shared anomaly calibration samples
* Comparison-universe definitions
* Anomaly-framework diagnostics
* Representation handoff assets
* Method-specific anomaly notebook inputs

## 7.6 DBSCAN Anomaly Generation (3.3.2)

### Purpose

Calibrate DBSCAN within the shared anomaly framework established in 3.3.1 and generate candidate mobility-state anomaly surfaces.

### Major Accomplishments

* Evaluated DBSCAN density readiness across representations and modalities.
* Calibrated eps and min_samples settings.
* Evaluated density heterogeneity and fragmentation behavior.
* Compared PCA and UMAP suitability for density-based anomaly detection.
* Generated candidate anomaly surfaces across all modeling modalities.
* Conducted aggregate anomaly review and human-in-the-loop anomaly inspection.
* Generated anomaly exports and mapping assets.

### Major Findings

Density heterogeneity varied substantially across modalities and representations.

UMAP representations exhibited significantly greater density heterogeneity than PCA representations and produced unstable density structure for DBSCAN calibration.

PCA representations produced more interpretable and operationally useful density behavior across modalities.

eps acted as the primary DBSCAN stability lever, while min_samples functioned primarily as a refinement parameter.

Human-review and aggregate-review workflows indicated that retained DBSCAN anomaly surfaces were spatially coherent, interpretable, and suitable for downstream framework comparison.

### Important Decisions

UMAP was retired as a DBSCAN representation due to density heterogeneity and calibration instability.

DBSCAN advances downstream using PCA representations only.

Final retained DBSCAN configurations:

* Bus: min_samples = 15, balanced eps band
* Subway: min_samples = 15, balanced eps band
* Taxi: min_samples = 20, tight eps band
* FHVHV: min_samples = 15, balanced eps band
* Multimodal: min_samples = 15, balanced eps band

DBSCAN outputs should be interpreted as candidate anomaly surfaces rather than final validated anomalies.

### Spatial Review Findings

* Bus anomalies concentrated heavily in Jamaica and eastern Queens.
* Subway anomalies concentrated strongly within Manhattan core zones.
* Taxi anomalies exhibited a mixed Manhattan-core and airport-oriented pattern.
* FHVHV anomalies were heavily airport-oriented.
* Multimodal anomalies exhibited strong Queens concentration with a smaller Manhattan-core component.

### Key Outputs

* PCA-based DBSCAN anomaly exports
* Calibration diagnostics
* Stability summaries
* Row-level anomaly tables
* Spatial-review assets
* Human-review summaries
* DBSCAN export manifest

---
7.7 Isolation Forest Anomaly Generation (3.3.3)

Purpose

Calibrate Isolation Forest within the shared anomaly framework established in 3.3.1 and generate candidate isolation-based mobility-state anomaly surfaces.

Major Accomplishments

Calibrated contamination thresholds.
Evaluated PCA and UMAP anomaly behavior.
Evaluated anomaly prevalence and score separation.
Compared Isolation Forest outputs against DBSCAN.
Conducted aggregate anomaly-coherence review.
Generated retained anomaly exports.

Major Findings

Isolation Forest does not rely on density-homogeneity assumptions and therefore allowed UMAP to remain under evaluation during calibration.

However, PCA consistently produced stronger and more interpretable anomaly structure than UMAP.

Contamination behaved primarily as an anomaly-volume control lever.

Lower contamination levels preserved stronger anomaly-tail separation and produced more selective anomaly surfaces.

Isolation Forest produced anomaly surfaces that were meaningfully different from DBSCAN rather than simply reproducing density-based anomalies.

Important Decisions

UMAP was retired for Isolation Forest anomaly generation.

Isolation Forest advances downstream using:

PCA only
contamination = 0.005

One retained configuration was selected per modality.

Human review relied primarily on aggregate coherence checks, concentration diagnostics, and spatial review rather than the heavier row-level inspection workflow used during DBSCAN calibration.

Key Outputs

PCA-based Isolation Forest anomaly exports
Contamination-calibration diagnostics
Framework-comparison diagnostics
Aggregate-review summaries

---

Section 7.8 Gaussian Mixture Model Anomaly Generation (3.3.4)

Purpose

Calibrate Gaussian Mixture Models within the shared anomaly framework established in 3.3.1 and generate probabilistic mobility-state anomaly surfaces.

Major Accomplishments

Evaluated candidate component counts.
Evaluated covariance structures.
Calibrated likelihood-tail thresholds.
Compared GMM outputs against DBSCAN and Isolation Forest.
Conducted aggregate anomaly-coherence review.
Generated retained anomaly exports.

Major Findings

GMM served as the project's probabilistic anomaly-detection framework.

Raw Scaled did not re-enter evaluation.

UMAP did not re-enter evaluation.

All candidate GMM structures converged successfully.

Full covariance consistently outperformed diagonal covariance strongly enough to justify retaining only full-covariance models.

Likelihood-tail threshold 0.005 consistently produced the strongest anomaly-tail separation across modalities.

GMM contributed anomaly structure that was not fully redundant with either DBSCAN or Isolation Forest and therefore remained valuable for downstream framework comparison.

Important Decisions

GMM advances downstream using PCA representations only.

Retained GMM configurations:

Bus: k = 3, full covariance, tail = 0.005
Subway: k = 3, full covariance, tail = 0.005
Taxi: k = 3, full covariance, tail = 0.005
FHVHV: k = 2, full covariance, tail = 0.005
Multimodal: k = 2, full covariance, tail = 0.005

Aggregate coherence review indicated that retained GMM anomaly surfaces were sufficiently interpretable to advance into downstream framework comparison.

Key Outputs

PCA-based GMM anomaly exports
Structure-calibration diagnostics
Tail-calibration diagnostics
Framework-comparison diagnostics
Aggregate-review summaries

---

## 7.9 Candidate Anomaly Framework Comparison (3.3.5)

### Purpose

Synthesize retained DBSCAN, Isolation Forest, and Gaussian Mixture Model anomaly outputs into a unified downstream anomaly package suitable for evaluation, interpretation, and social-data integration.

### Major Accomplishments

* Consolidated retained anomaly outputs across all three anomaly frameworks.
* Constructed framework-overlap diagnostics and consensus indicators.
* Evaluated directional anomaly behavior across retained anomaly surfaces.
* Evaluated modality participation behavior across anomaly frameworks.
* Compared congestion-oriented and demand-oriented anomaly structure.
* Assessed framework-specific and consensus anomaly behavior.
* Selected the downstream anomaly handoff package.

### Major Findings

* DBSCAN, Isolation Forest, and GMM are complementary rather than redundant anomaly frameworks.
* Multi-method agreement exists but is selective rather than universal.
* Congestion-oriented anomalies exhibit stronger cross-framework agreement than the anomaly universe overall.
* PCA remained the dominant retained anomaly representation throughout downstream framework evaluation.
* Multimodal anomalies provide useful context but do not replace modality-specific participation information.
* Retained anomalies are interpretable as recurring mobility events rather than generic statistical outliers.
Additional synthesis work clarified that the retained anomaly package is structured as a layered interpretation framework rather than a single anomaly pool.

The retained anomaly union serves as the broad working anomaly universe and reference surface.

A narrower positive-direction subset captures anomalies aligned with either:

* congestion_oriented
* positive_demand_shock

The positive-direction subset became the primary policy-facing anomaly package used throughout downstream evaluation.

Consensus indicators, directional labels, framework-specific flags, and modality-participation layers are treated as explanatory context rather than competing anomaly surfaces.

### Important Decisions

The final retained anomaly package consists of:

* Retained anomaly union (48,964 rows)
* Positive-direction subset (10,741 rows)
* Congestion-oriented interpretive lens (3,768 rows)
* Positive-demand-shock interpretive lens (7,050 rows)

Support layers include:

* Consensus indicators
* Directional labels
* Framework-specific flags
* Modality participation indicators

The retained anomaly union remains the broad reference universe.

The positive-direction subset became the primary downstream evaluation surface.

Consensus indicators are retained as refinement layers rather than standalone anomaly surfaces.

### Key Outputs

* framework_comparison_full_row_universe.parquet
* retained_anomaly_working_table.parquet
* consensus_anomaly_indicators.parquet
* directional_anomaly_labels.parquet
* framework_specific_anomaly_flags.parquet
* modality_participation_indicators.parquet
* retained_social_join_focus_table.parquet
* framework_synthesis_handoff_manifest.csv

---
## 7.10 Final Anomaly Surface Evaluation (3.4.1)

### Purpose

Evaluate whether retained anomaly surfaces exhibit meaningful recurrence, persistence, policy relevance, and external validity.

### Major Accomplishments

* Evaluated anomaly recurrence and persistence behavior.
* Evaluated consensus versus non-consensus anomaly structure.
* Evaluated directional anomaly behavior.
* Evaluated policy-geography composition.
* Evaluated pre/post congestion-pricing behavior.
* Conducted external validation using NYC crash events.
* Refined downstream anomaly recommendations.

### Major Findings

Retained anomalies exhibit strong recurrence and persistence when evaluated within local operating contexts defined by:

* feature_set
* taxi_zone_id
* temporal_bucket

The positive-direction subset remains highly recurrent but is substantially more selective than the full retained anomaly union.

Consensus refinement produces meaningful tradeoffs between confidence and coverage.

External validation demonstrates that positive-direction anomalies align more strongly with crash activity than the full retained anomaly union.

The strongest crash-aligned anomaly surface is:

* Positive-direction | 2+ methods consensus

while 3-method consensus becomes overly restrictive and loses useful signal.

### Important Decisions

The project shifted from treating the retained anomaly union as the preferred downstream package to a layered recommendation:

* Broad reference surface:
  * Retained anomaly union

* Preferred working anomaly surface:
  * Retained positive-direction subset

* Preferred high-confidence anomaly core:
  * Positive-direction | 2+ methods consensus

* Robustness-only refinement:
  * Positive-direction | 3 methods consensus

Positive-demand-shock emerged as the strongest internally crash-aligned directional lens.

Congestion-oriented remains valuable as an interpretive congestion-facing lens but exhibits weaker external validation performance.

### Key Outputs

* Recurrence and persistence diagnostics
* Consensus evaluation summaries
* Directional evaluation summaries
* Policy-geography evaluation summaries
* Crash-validation outputs
* Final anomaly-surface recommendations

---

# 8. Stable Project Decisions

The following decisions are considered foundational to the project and should not be revisited without compelling evidence.

These decisions were made after extensive exploration, QA, and downstream-impact evaluation.

---

## Transportation Modalities

### Taxi Definition

Taxi is defined as:

* Yellow Taxi
* Green Taxi

combined into a single Taxi modality.

This decision simplifies modeling while preserving the most important taxi-demand and taxi-mobility signals.

---

### FHV Exclusion

FHV is excluded from downstream modeling.

Reason:

* Severe geographic incompleteness.
* Inconsistent coverage patterns.
* Reduced usefulness as a citywide mobility-state signal.

FHV remains part of the historical ingestion record but is not a canonical modeling modality.

---

### FHVHV Retention

FHVHV remains the primary ride-hailing modality.

Reasons:

* Broad geographic coverage.
* Consistent reporting.
* Strong mobility-demand signal.

---

### Traffic Treatment

Traffic remains available throughout the project but is excluded from default unsupervised modeling workflows.

Traffic is instead treated as:

* Contextual information.
* Validation signal.
* Future supervised-learning target.
* Congestion-pricing interpretation layer.

Reason:

Traffic observations exhibit sparse and irregular observation schedules that differ substantially from the remaining transportation systems.

---

## Analytical Grain

The canonical analytical grain is:

Taxi Zone × Date × Temporal Bucket

All downstream modeling, visualization, interpretation, clustering, and anomaly detection should preserve this grain whenever possible.

---

## Feature Selection

Feature selection was finalized in Notebook 1.5.6.

Downstream notebooks should not reopen feature-selection decisions unless new evidence demonstrates a significant deficiency in the selected feature universe.

Feature engineering and feature selection are intentionally treated as completed phases.

---

## Representation Learning

Representation learning and anomaly detection are treated as separate problems.

Representation-learning notebooks should focus on:

* Structure discovery.
* Compressibility.
* Neighborhood preservation.
* Representation quality.

Anomaly notebooks should focus on:

* Density estimation.
* Clustering.
* Outlier detection.
* Anomaly interpretation.

---

## Anomaly Framework Policy

The anomaly-framework preparation stage initially advanced both PCA and UMAP into downstream method evaluation.

Subsequent calibration notebooks demonstrated that PCA consistently produced the most stable and interpretable anomaly behavior across 
DBSCAN, Isolation Forest, and Gaussian Mixture Model workflows.

Subsequent anomaly-generation notebooks demonstrated that PCA consistently produced the most stable, interpretable, and operationally useful anomaly behavior across DBSCAN, Isolation Forest, and Gaussian Mixture Model workflows.

As a result:

* Raw Scaled was retired as a primary downstream anomaly-generation branch.
* UMAP was ultimately retired as an operational anomaly-generation representation.
* PCA became the sole retained anomaly-generation representation across all retained anomaly frameworks.

Raw Scaled remains an important upstream reference surface, while UMAP remains valuable for representation-learning interpretation and historical comparison.

PCA therefore became the canonical anomaly-generation representation across all retained anomaly frameworks.

---

## Canonical Anomaly Package

Retained anomaly frameworks:

* DBSCAN
* Isolation Forest
* Gaussian Mixture Model

Primary retained anomaly layers:

* Retained anomaly union
* Retained positive-direction subset
* Positive-direction | 2+ methods consensus

The retained anomaly union serves as the broad reference universe.

The retained positive-direction subset serves as the primary policy-facing anomaly package.

Positive-direction | 2+ methods consensus serves as the preferred high-confidence anomaly core.

Positive-direction | 3 methods consensus is retained as a robustness reference rather than a primary downstream surface.

---

## Directionality Policy

Directionality is treated as a first-class interpretation layer throughout downstream anomaly synthesis and evaluation workflows.

Primary downstream directional lenses:

* congestion_oriented
* positive_demand_shock

Additional directional labels remain useful for diagnostic purposes:

* decongestion_oriented
* negative_demand_shock
* mixed
* ambiguous

Directionality is used to interpret retained anomalies rather than replace anomaly detection itself.

---

## Consensus Policy

Consensus indicators evolved from descriptive annotations into active downstream evaluation layers.

External validation demonstrated that:

* 2+ methods consensus improves crash enrichment while preserving meaningful coverage.
* 3-method consensus sacrifices too much coverage and weakens practical usefulness.

Current downstream recommendation:

* Preferred high-confidence core:
  * Positive-direction | 2+ methods consensus

* Preferred broader companion layer:
  * Retained positive-direction subset

* Broad reference surface:
  * Retained anomaly union

Consensus should therefore be interpreted as a selective refinement mechanism rather than a requirement for anomaly validity.

---

## External Validation Policy

External validation is performed at the canonical project grain:

Taxi Zone × Date × Temporal Bucket

Crash validation uses:

* Any crash occurrence
* Crash counts
* Injury-linked crash occurrence

Fatal crashes are retained for descriptive review but are too sparse to serve as primary validation targets.

Spatial crash linkage uses:

* Point-in-polygon assignment (0m buffer)
* Targeted bridge-and-tunnel rescue logic

Broader buffer-based assignment strategies were evaluated but introduced substantial multi-zone ambiguity with limited coverage benefit.

Current evidence indicates:

* The retained anomaly union is too broad to exhibit strong crash alignment.
* Positive-direction narrowing materially improves crash enrichment.
* Positive-direction | 2+ methods consensus provides the strongest balance between crash alignment and retained coverage.

---

## Modality Participation Policy

Multimodal anomaly participation is informative but is not considered a sufficient replacement for modality-specific anomaly participation.

Downstream interpretation should preserve modality participation context whenever possible, including:

* Bus participation
* Subway participation
* Taxi participation
* FHVHV participation
* Multimodal participation

This allows anomaly interpretation to distinguish between system-specific and system-spanning mobility irregularities.

---

## DBSCAN Representation Policy

DBSCAN anomaly generation uses PCA representations only.

Although both PCA and UMAP remain project-level anomaly representations, DBSCAN calibration demonstrated that UMAP produces substantially greater density heterogeneity and less stable density structure.

As a result:

* PCA remains the canonical DBSCAN representation.
* UMAP remains an important historical representation-learning asset and a useful nonlinear visualization framework.

However, downstream anomaly-generation calibration ultimately retained PCA as the operational representation for DBSCAN, 
Isolation Forest, and Gaussian Mixture Model workflows.

As a result:

* PCA remains the canonical anomaly-detection representation.
* UMAP remains valuable for representation-learning interpretation and historical comparison.
* Raw Scaled remains an upstream reference surface rather than a primary anomaly-generation branch.

---

Isolation Forest Representation Policy

Isolation Forest anomaly generation uses PCA representations only.

Although UMAP remained under evaluation during Isolation Forest calibration, PCA consistently produced stronger anomaly-tail separation, 
more interpretable concentration patterns, and more coherent anomaly structure.

Final retained Isolation Forest configuration:

PCA only
contamination = 0.005

---

Gaussian Mixture Model Representation Policy

Gaussian Mixture Model anomaly generation uses PCA representations only.

Raw Scaled and UMAP were not retained for downstream GMM calibration.

Final retained GMM policy:

PCA only
Full covariance only
Modality-specific component counts
Tail threshold = 0.005

GMM serves as the project's probabilistic anomaly-detection framework.

---

## Missingness Indicators

Missingness indicators remain valuable for:

* Auditability.
* Data lineage.
* Sensitivity analysis.

However, they are excluded from default PCA and UMAP representations because representation-learning analyses demonstrated limited incremental value relative to mobility features themselves.

---

## PCA Policy

Full-period PCA remains the canonical linear representation.

Pre/post congestion-pricing PCA stability analysis revealed meaningful Taxi instability.

Full-period PCA remains appropriate for representation-learning workflows, but downstream anomaly workflows use split pre/post 
congestion-pricing Taxi PCA assets.

---

## UMAP Policy

UMAP played an important role during representation-learning and anomaly-framework preparation by demonstrating that nonlinear mobility 
structure existed beyond PCA.

However, downstream anomaly-generation calibration ultimately retired UMAP from DBSCAN, Isolation Forest, and Gaussian Mixture Model 
workflows.

UMAP therefore remains:

* the project's primary nonlinear visualization representation,
* an important historical representation-learning asset,
* a useful comparison surface for methodological interpretation,

but not a retained operational anomaly-generation representation.

---

## Congestion-Pricing Interpretation

Congestion-pricing geography consistently emerges as one of the strongest organizing structures within nonlinear embeddings.

As a result:

* Congestion-pricing overlays should remain a standard interpretation tool.
* Geography should remain a primary explanation layer throughout downstream analysis.

---

## Downstream Handoff Policy

The canonical downstream anomaly package consists of:

* Retained anomaly union
* Consensus indicators
* Directional labels
* Framework-specific flags
* Modality participation indicators

These assets should be treated as the default inputs for downstream evaluation, policy interpretation, spatial-temporal analysis, and social-data integration workflows.

---

## Human Review Philosophy

Human review requirements vary by notebook objective.

DBSCAN required the most extensive human review because density suitability, density heterogeneity, and representation appropriateness 
were active methodological questions.

Isolation Forest and GMM used lighter aggregate-review workflows because anomaly-framework preparation, representation evaluation, and 
cross-framework diagnostics had already resolved many of the major methodological uncertainties.

Future anomaly notebooks should not automatically repeat DBSCAN-style deep row-level review unless a specific methodological concern 
justifies additional inspection.

---

# 9. Known Limitations

The project intentionally prioritizes interpretability and practical execution over perfect coverage or methodological completeness.

The following limitations should be considered during interpretation.

---

## Traffic Coverage Limitations

Traffic exhibits:

* Sparse geographic coverage.
* Sparse temporal coverage.
* Irregular observation schedules.

Traffic observations should therefore be interpreted differently from Bus, Subway, Taxi, and FHVHV observations.

---

## Transportation-System Coverage Differences

Transportation systems observe different portions of the city.

Examples:

* Subway coverage is concentrated around subway-accessible areas.
* Traffic coverage reflects sensor placement.
* Taxi and FHVHV provide near-citywide coverage.

Absence of observations does not necessarily imply absence of transportation activity.

---

## Congestion-Pricing Observation Window

Post-congestion-pricing observations currently cover a substantially shorter period than pre-congestion-pricing observations.

This imbalance may influence:

* Stability analyses.
* Representation-learning results.
* Future anomaly-detection behavior.

---

## Representation-Learning Assumptions

PCA and UMAP are unsupervised methods.

Observed latent structure does not automatically imply causal relationships.

Any congestion-pricing interpretation must therefore be supported through additional analysis rather than inferred solely from representation-learning outputs.

---

## Spatial Aggregation

Taxi Zones provide a useful neighborhood-level geography but do not perfectly represent transportation behavior.

Important within-zone variation is inevitably lost during aggregation.

This tradeoff is accepted because a common spatial framework is required across transportation systems.

---

# 10. Deferred Ideas and Future Work

Throughout the project several ideas were intentionally deferred to preserve MVP scope.

These remain potential future extensions.

---

## Forecasting

Potential forecasting workflows include:

* Traffic prediction.
* Transit-demand forecasting.
* Mobility-state forecasting.
* Representation-space forecasting.

Forecasting remains outside current project scope.

---

## Counterfactual Analysis

Potential extensions include:

* Synthetic-control methods.
* Counterfactual mobility forecasting.
* Alternative congestion-pricing scenarios.

---

## Difference-in-Differences

Future work may evaluate:

* Parallel-trend assumptions.
* Treatment and comparison geographies.
* Congestion-pricing causal effects.

Representation-learning and anomaly-detection phases should be completed before pursuing formal causal analysis.

---

## Advanced Representation Learning

Potential future approaches include:

* Autoencoders.
* Variational autoencoders.
* Graph-based representations.
* Transportation-network embeddings.

The current project focuses on PCA and UMAP because they offer strong interpretability.

---

## Advanced Anomaly Detection

Potential future methods include:

* Ensemble anomaly frameworks.
* Graph-based anomaly detection.
* Temporal anomaly detection.
* Sequence-based anomaly detection.

---

## Traffic Prediction Workflows

Traffic remains a promising supervised-learning target because:

* It is difficult to observe directly.
* It may benefit from multimodal predictors.
* Congestion-pricing impacts may ultimately manifest through traffic outcomes.

---

# 11. Execution Lessons

Several practical lessons emerged during development.

These lessons are preserved because they influence future notebook design and implementation strategy.

---

## Deepnote Constraints

The project operates under practical memory limitations.

Successful execution frequently depended upon:

* Incremental processing.
* Parquet checkpoints.
* DuckDB-backed operations.
* Rebuild toggles.

Large in-memory workflows should be avoided whenever practical.

---

## DuckDB First

DuckDB consistently proved to be the most effective solution for:

* Large joins.
* Aggregations.
* Coverage calculations.
* Export pipelines.

Whenever large-scale transformations are required, DuckDB should generally be considered before Pandas.

---

## Modular Notebook Design

The most reliable notebook pattern was:

One block = one task.

This approach improved:

* Debuggability.
* Human review.
* Codex collaboration.
* Reproducibility.

---

## Human-in-the-Loop Checkpoints

Many important modeling decisions emerged through iterative review rather than fully automated selection.

Examples include:

* Feature-selection decisions.
* Representation-selection decisions.
* UMAP sensitivity interpretation.
* Congestion-pricing interpretation.

Future notebooks should continue using explicit decision checkpoints.

---

## Findings Philosophy

Findings should be written only after reviewing actual results.

Avoid placeholder findings.

Prefer concise, interpretation-focused observations rather than lengthy academic narratives.

---

## Codex Collaboration Lessons

The most successful Codex interactions occurred when:

* Scope was narrowly defined.
* Notebook objectives were explicit.
* Existing outputs were treated as authoritative.
* Historical context was supplied through project-memory artifacts rather than notebook re-ingestion.

These lessons directly motivated the project's memory-management architecture.

---

# 12. Project Memory Architecture

As the project grew, repeated notebook ingestion became increasingly expensive and inefficient.

A layered memory architecture was therefore adopted.

---

## PROJECT_SPEC.md

Purpose:

Long-lived project encyclopedia.

Contains:

* Methodology.
* Architecture.
* Dataset registry.
* Notebook history.
* Major findings.
* Stable project decisions.
* Known limitations.
* Future roadmap.

Update frequency:

Infrequent.

Only update when major architectural or methodological changes occur.

---

## PROJECT_STATE.md

Purpose:

Current project snapshot.

Contains:

* Current notebook.
* Current phase.
* Active decisions.
* Open questions.
* Immediate objectives.

Update frequency:

Frequent.

Typically updated after notebook completion.

---

## NOTEBOOK_INDEX.md

Purpose:

Notebook-level historical reference.

Contains:

* Notebook purpose.
* Key outputs.
* Key findings.
* Important decisions.

Does not contain implementation details.

Update frequency:

After notebook completion.

---

## DECISIONS.md

Purpose:

Chronological decision log.

Contains:

* Decision date.
* Decision rationale.
* Downstream implications.

Examples:

* Traffic removal from default unsupervised workflows.
* Feature-selection finalization.
* PCA representation policy.
* Temporal-bucket-aware anomaly-scoring preference.

Update frequency:

Only when significant decisions occur.

---

## Recommended Context Strategy

For implementation tasks:

Read:

1. PROJECT_STATE.md
2. NOTEBOOK_INDEX.md
3. Current notebook

Consult PROJECT_SPEC.md only if additional architectural context is required.

---

For planning tasks:

Read:

1. PROJECT_STATE.md
2. NOTEBOOK_INDEX.md
3. PROJECT_SPEC.md
4. Current notebook

This strategy minimizes context usage while preserving project continuity and historical awareness.

--- 
## What Changed Since the Previous Memory Snapshot

* Completed anomaly-framework synthesis in 3.3.5.
* Introduced the positive-direction anomaly lens as a major downstream concept.
* Stabilized the retained anomaly export package and corrected row-alignment issues.
* Completed recurrence and persistence evaluation using 7-day persistence.
* Completed consensus-versus-coverage evaluation.
* Completed directional and policy-relevance evaluation.
* Added external validation using NYC crash events.
* Shifted preferred downstream anomaly recommendation from the retained anomaly union toward Positive-Direction | 2+ Methods Consensus.
* Identified positive-demand-shock as the strongest internally crash-aligned directional lens.
* Hardened notebook execution by removing brittle dependencies, stale intermediate assumptions, and export inconsistencies.

