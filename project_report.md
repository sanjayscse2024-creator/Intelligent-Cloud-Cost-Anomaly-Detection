# Project report: Intelligent Cloud Cost Anomaly Detection

## Implementation checklist

- [x] CSV/Excel ingestion with required-schema validation.
- [x] Duplicate detection, missing-value handling, currency validation, downloadable errors.
- [x] Normalization and aggregation by date, service, project, and region.
- [x] Previous-period, rolling, and median/MAD baselines.
- [x] Spike, drop, deviation, severity, score, method, evidence fields.
- [x] Zero-baseline-safe percentage calculations.
- [x] Cost-driver ranking and optional usage-versus-rate analysis.
- [x] Fact/hypothesis separation and investigation-only recommendations.
- [x] Configurable thresholds, alert acknowledgement/status, reviewer notes, duplicate suppression.
- [x] Interactive Plotly dashboard and investigation tables.
- [x] SQLite persistence and CSV/JSON audit exports.
- [x] Synthetic sample data, tests, README, architecture diagram.

## Design decisions

The implementation favors interpretable, provider-agnostic methods over opaque models. Median/MAD is less sensitive to an isolated billing spike than a mean/std baseline. Previous-period comparison remains available when history is short. Each anomaly carries its baseline, absolute/percentage difference, severity, score, method, direction, and history count so reviewers can assess evidence.

## Verification

The automated test suite covers invalid currencies and duplicates, anomaly spike detection, and SQLite round-tripping. The sample data is deterministic and contains a compute rate/cost spike plus a storage drop. The PDF named in the brief was unavailable in the supplied workspace; the README records this limitation.

## Operational safety

The application does not call cloud provider APIs and performs no infrastructure changes. Exports include assumptions, exclusions, thresholds, methods, and limitations. Reviewers must verify billing-console evidence, usage metrics, credits/refunds, rate-card changes, and period completeness before action.
