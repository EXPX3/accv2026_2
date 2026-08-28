# Methods

## Pseudo-instance definition

For semantic volume `Y`, the vehicle foreground is
`M(i)=1[Y(i)=vehicle]`. A pseudo-instance is a maximal connected component of
`M` under the declared 3D neighborhood. The primary implementation uses
`scipy.ndimage.label` with a centrosymmetric 6-neighborhood. No morphology or
merging is applied by default.

Instance IDs are frame-local. Components are sorted by camera distance and
centroid coordinates when a verified grid-to-camera transform is available;
otherwise grid-metric distance and coordinates are used. They are then named
`vehicle_1`, `vehicle_2`, and so on. These names do not represent temporal
tracking identities.

## Coordinates

For array index vector `i`, the metric voxel centre is

```text
p_grid = T_index_to_grid @ [i + 0.5, 1]
```

Camera/world coordinates use explicitly supplied homogeneous transforms. The
eight voxel-boundary corners define each metric axis-aligned bounding box. This
avoids assuming a particular WHD/XYZ axis permutation or sign.

## Matching

For every frame, all GT/predicted component voxel IoUs are calculated. The
Hungarian algorithm finds a one-to-one assignment maximizing total IoU. Pairs
below the declared threshold are discarded. Remaining unassigned GT and
predicted components are false negatives and false positives respectively.

The protocol reports thresholds 0.25 and 0.50 separately. Localization error is
reported only for matched pairs and must always be accompanied by recall, since
a model could otherwise obtain deceptively low localization error by detecting
only easy vehicles.

## Statistics

Reported localization summaries include mean absolute 3D centroid error, RMSE,
median, standard deviation, and P50/P75/P90/P95. Detection summaries include
TP/FP/FN, precision, recall, F1, and instance-count MAE. Precision/recall/F1
confidence intervals use deterministic sequence-level cluster bootstrap
resampling, rather than treating temporally adjacent frames as independent.

