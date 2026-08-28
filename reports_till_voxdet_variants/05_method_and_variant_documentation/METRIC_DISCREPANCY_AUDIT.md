# OccuFly SSC metric-discrepancy audit

## Confirmed root cause of the historical FSSC class table

The historical FSSC trainer used the sparse OccuFly raw label IDs directly and
therefore instantiated **37 raw-ID-indexed output channels** (`0..36`). Its
metric export wrote the resulting 37-element `per_class_iou` vector in channel
order. The benchmark-browser ingestion subsequently selected the first 21
vector positions and assigned the 21 non-empty contiguous class names to them.
That operation was not a taxonomy conversion: it shifted class zero and also
misnamed every value after each gap in the sparse raw taxonomy.

This exactly explains the two suspicious values; it is not a hypothesis:

* `0.8778380751609802` is raw channel 0, **empty**, but was displayed as
  `road` (87.7838075%).
* `0.3827239871025085` is raw channel 16, **building**, but vector position 16
  was displayed as `cable_tower` (38.2723987%).

The preserved provenance rows are in
`reports/ssc_benchmark_browser/metric_sources.csv` (the historical ignored
output paths it references are no longer present). The browser table preserving
the values is
`reports/ssc_benchmark_browser/classwise_ssc_comparison_through_variant_3_complete_20260828.csv`.
The generating behavior is visible in the original FSSC training/evaluation
code: class count is inferred from the raw labels and the class vector is
exported by numeric channel index without applying the sparse raw-to-contiguous
mapping.

Consequently, the historical per-class row cannot be averaged to reproduce the
stated mIoU: its labels are wrong, it includes empty at the first displayed
position, it drops later raw channels, and blanks/zeros reflect different
support conventions. The overall historical mIoU came from the evaluator's own
model-dependent union-present mask, not from the 21 browser cells.

## Canonical correction

The corrected evaluator uses one explicit mapping
`(0,1,2,3,4,5,6,7,8,9,11,12,13,14,16,17,21,22,33,34,35,36) -> 0..21`.
Unknown non-ignore labels raise an exception. A 37-channel FSSC prediction is
adapted by selecting precisely those raw-ID-indexed channels before `argmax`;
22-channel models are used directly. A semantic-only 21-channel tensor is
rejected unless its architecture supplies an explicit occupancy adapter.

All reported quantities are derived from one global 22x22 `int64` confusion
matrix after exact, non-padded distributed sharding. The primary semantic metric
is `ssc_miou_gt_present`; fixed-21-zero-filled and legacy-union-present values
are separately named. JSON stores fractions, while presentation percentages
must use explicitly suffixed columns.

## Dataset and axis checks

The split manifests were generated from the dataset implementation rather than
from a hard-coded count. Validation contains 1,965 samples (scenes 06/07) and
test contains 3,842 samples (scenes 08/09), at heights 30/40/50. Their ordered
manifest SHA-256 values are recorded beside the manifests. The FSSC adapter
retains the implemented OccuFly `WHD -> DHW` permutation; the synthetic unique
grid round-trip test proves the inverse conversion is lossless.

## Interpretation boundary

The correction changes reporting and, where required, class-channel mapping; it
does not improve any checkpoint. Differences remaining after canonical
inference are genuine checkpoint/model differences. Models whose original
checkpoints are unavailable are recorded as missing and are never replaced by a
different run.
