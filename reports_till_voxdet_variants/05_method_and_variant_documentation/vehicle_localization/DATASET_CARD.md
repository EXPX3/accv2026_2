# Dataset card: OccuFly vehicle-positive localization subset

## Source and purpose

This derived dataset contains original OccuFly frames whose canonical semantic
voxel GT includes at least one vehicle voxel. It supports conditional evaluation
of SSC-derived vehicle pseudo-instance localization across preserved official
splits, sequences, scenes, and height metadata.

## Creation status

This repository contains the builder, not generated data. Populate this card on
the DGX after the exhaustive build with:

- source OccuFly version and path;
- source-manifest SHA-256;
- selected frame counts by split/scene/height;
- vehicle voxel and pseudo-instance counts;
- component-size distribution;
- 6/18/26 connectivity sensitivity;
- exact index/coordinate transformations;
- output audit SHA-256.

## Limitations

- Components are inferred from semantic connectivity, not genuine instance IDs.
- Touching vehicles may merge; fragmented vehicles may split.
- Instance IDs are local to a frame and cannot be interpreted as tracks.
- GT-positive selection conditions the evaluation and excludes vehicle-negative
  frames needed for unbiased false-positive measurement.
- Height categories are preserved only when authoritative metadata exists. Pose
  Z must not be relabelled as above-ground altitude without evidence.

## Leakage controls

Official split and sequence assignments must remain unchanged. Any filtering or
post-processing threshold must be selected using training/validation only.
Test labels may define the conditional evaluation subset but are never model
inputs or hyperparameter-selection data.

