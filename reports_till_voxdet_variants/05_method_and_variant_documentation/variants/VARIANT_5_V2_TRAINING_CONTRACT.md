# Variant 5 training contract v2

This contract retains the corrected VoxNT target normalization, corrected TDP
sampling lattice, V-JEPA2.1/DPT context, canonical 22-class taxonomy, and fixed
evaluation protocol. It replaces the original Variant 5 training objective and
optimization contract to address the remaining confirmed bottlenecks.

Existing Variant 5 v1 results remain valid as the controlled V4 geometry
correction. They must not be mixed with v2 results. V2 checkpoints use the tag
variant_5_v2_longtail_depthgrad_fullres_voxnt_cosine and record
training_contract_version = 2.

## Long-tail factorization

The SSC objective is factorized into:

1. dataset-balanced occupied/free-space BCE;
2. occupied-only 21-way focal semantic CE;
3. macro soft Dice over semantic classes present in the batch.

The binary positive weight is computed from the exhaustive training-only
frequency artifact and capped at 25. Semantic weights use capped square-root
inverse frequency, are normalized to mean one over supported classes, and assign
zero weight to classes absent from training. Empty voxels never enter the
conditional semantic objective.

The auxiliary head uses the same factorization at lower weights. This preserves
early 3D-volume supervision without allowing its loss to dominate the final
head.

## Controlled SSC gradients into depth

Depth probabilities and metric dense depth keep their exact forward values.
SSC gradients are stopped for the first epoch, linearly ramped for three epochs,
and capped at 0.1. The teacher-depth loss remains unscaled and the depth
parameter group retains its low learning rate of 1e-6. This permits geometric
correction from SSC without allowing the noisy semantic objective to destroy
the pretrained metric-depth solution.

## Full-resolution, class-balanced VoxNT

The predicted low-resolution six-direction field is interpolated to the
full-resolution target lattice. Loss is evaluated at every eligible
full-resolution voxel, averaged within each class, then averaged across classes.
Small objects therefore cannot disappear through nearest-neighbour target
selection, and large building/tree regions cannot dominate the loss by voxel
count.

The default localizable class train IDs are 8 tree, 9 ground_obstacle, 10
person, 11 bicycle, 12 vehicle, 14 building, 16 cable, 19 construction, 20
crane, and 21 truck.

Road, walkway, dirt, gravel, rock, grass, vegetation, water, roof, and parking
lot are excluded because contiguous semantic runs are not reliable
instance-like targets for these amorphous surfaces.

## Optimization

AdamW uses per-step linear warm-up for one epoch followed by cosine decay to 5%
of each parameter group base learning rate. Scheduler state and global step are
checkpointed and restored strictly.

## Reproducibility and checkpoint selection

- The trainer is explicit and does not monkey-patch Variant 3.
- Every v2 checkpoint records the loss contract, semantic weights, localizable
  VoxNT classes, scheduler state, depth-gradient schedule, and source frequency
  artifact.
- Checkpoints are selected only by validation ssc_miou_gt_present.
- The default output directory is new and fail-closed.
- Test evaluation must be run once after validation checkpoint selection.

Run ./run_train_8gpu.sh. The launcher runs test_variant_5_v2.py before
allocating GPUs.

## Required ablations

Because v2 changes several mechanisms, academic reporting must retain v1 as the
controlled geometry ablation and separately report v2. At minimum run:

1. v2 with VoxNT weight 0;
2. v2 with localizable-class VoxNT weight 1;
3. v2 with SSC-to-depth gradient maximum 0;
4. the full v2 configuration;
5. three seeds for the best configuration.
