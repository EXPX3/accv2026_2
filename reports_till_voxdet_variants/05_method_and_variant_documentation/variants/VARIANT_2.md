# Variant 2: VoxDet reference losses and auxiliary supervision on OccuFly

## Purpose

The plain-loss monocular VoxDet baseline collapsed toward the dominant empty
class and a small subset of occupied classes. Variant 2 retains the same
OccuFly monocular lifting, spatially decoupled encoder, TDP and VoxNT pathway,
but restores the reference VoxDet occupancy-loss structure and auxiliary
supervision. These mechanisms mitigate class and occupancy imbalance; they do
not mathematically guarantee that collapse cannot occur.

## Fixed OccuFly contract

- Training scenes: `scene_01` through `scene_05`
- Validation scenes: `scene_06` and `scene_07`
- Test scenes: `scene_08` and `scene_09`
- Altitudes: 30 m, 40 m and 50 m
- Raw semantic IDs: sparse OccuFly IDs remapped to contiguous train IDs `0..21`
- Empty/free train ID: `0`
- Ignore/invalid ID: `255`
- Stored volume: OccuFly `WHD = [192, 128, 128]`
- Axes: camera-right, camera-down, camera-forward
- Metric range: `[-48, 48] x [-32, 32] x [0, 64]` metres
- Voxel size: 0.5 m

Class statistics are computed from remapped, non-ignored voxels in the training
split only. Validation and test labels are never read when constructing loss
weights.

## Imbalance mechanisms

### 1. Inverse-log class weights

For every contiguous OccuFly training class `c`, the frequency audit computes
the valid training-voxel count `N_c` and applies the reference VoxDet formula:

```text
w_c = 1 / log(N_c + 0.001)
```

The resulting fixed vector is supplied to cross-entropy for both prediction
heads. Consequently, voxels from less frequent classes contribute more to the
objective than voxels from dominant classes. The frequency JSON records the
split, scenes, altitudes, raw-ID ordering, class counts, grid geometry, valid
and ignored totals and a hash of the processed sample-UID manifest. The same
artifact and derived weights are embedded in every checkpoint.

The exhaustive audit found no valid training voxels for train ID 17 (raw ID
22) in scenes 01--05. The reference formula is undefined for a zero count. This
class is assigned weight zero rather than introducing an undocumented
pseudocount or reading validation/test labels. It remains part of evaluation,
but the prescribed split provides no supervised examples from which to learn
it. All classes present in training use the exact inverse-log formula above.

### 2. Semantic-scaling loss

For every class present in the current target batch, semantic scaling computes
soft class precision, recall and specificity from the predicted probabilities
and optimizes each quantity toward one. The loss is averaged over present
classes rather than over voxels. This provides class-wise supervision that is
not proportional to raw voxel frequency.

### 3. Geometric-scaling loss

All non-empty semantic classes are combined into occupied probability.
Geometric scaling optimizes occupied precision, occupied recall and empty-space
specificity. This directly constrains the occupied-versus-empty geometry that
collapsed in the unweighted baseline.

### 4. Auxiliary and final heads

The auxiliary occupancy head operates on the lifted 3-D feature volume before
the local voxel encoder. It uses a 3-D convolution, group normalization, ReLU
and a class projection, followed by trilinear resizing to the full OccuFly WHD
grid. This matches the placement of VoxDet's camera auxiliary OccHead.

The final semantic head remains part of the VoxDet task-decoupled predictor
after the local voxel encoder and spatially decoupled FPN. Its class prediction
therefore benefits from the six-direction VoxNT-conditioned instance-centric
feature aggregation.

## Complete training objective

The reference camera configuration uses final-head weights `3/1/1` and
auxiliary-head weights `0.2/0.2/0.2` for cross-entropy, semantic scaling and
geometric scaling, respectively. Variant 2 therefore optimizes:

```text
L = 3.0 * L_main_CE
  + 1.0 * L_main_semantic_scaling
  + 1.0 * L_main_geometric_scaling
  + 0.2 * L_aux_CE
  + 0.2 * L_aux_semantic_scaling
  + 0.2 * L_aux_geometric_scaling
  + 1.0 * L_VoxNT
  + 0.1 * L_depth_teacher
```

Predicted OccuFly metric depth maps are training-only teacher targets for the
learned monocular depth distribution. They are never model inputs and are not
loaded during validation or test.

## Comparison scope

Variant 2 is intended for comparison with other methods evaluated using the
same OccuFly splits, taxonomy, ignore mask, WHD grid and SC/SSC metric code. It
must be described as **Monocular VoxDet adapted to OccuFly with
reference-aligned SSC losses and auxiliary supervision**. Its numerical results
are not directly comparable to the paper's SemanticKITTI or KITTI-360 tables.

## Verified training-frequency artifact

`occufly_train_class_frequencies.json` was generated exhaustively from all
14,804 samples in scenes 01--05 at all three altitudes. Its totals satisfy the
full-grid identity exactly:

```text
valid voxels   = 17,272,039,424
ignored voxels = 29,297,317,888
total voxels   = 46,569,357,312
               = 14,804 * 192 * 128 * 128
```

The processed sample-UID manifest SHA-256 is
`77b9f0ce5c1ef3d7082e1a1b0e66aa39f24797827078a05114f31bd8c32ffaa8`.
The largest present-class weight is assigned to train ID 10 (raw ID 11), with
1,100 valid training voxels. Train ID 17 (raw ID 22) is the sole absent class.

## Verification evidence

- Python compilation passes for all Variant 2 modules.
- Inverse-log unit tests prove that weights increase as counts decrease and
  remain finite; the absent training class is explicitly zero-weighted.
- On identical random logits and targets, Variant 2 semantic-scaling loss is
  numerically identical to the local VoxDet reference implementation.
- Geometric-scaling loss agrees with the reference within `4.8e-7`, attributable
  to the explicit numerical guards.
- Runtime loader checks confirm teacher depth exists in training batches and is
  absent from validation and test batches.
- An eight-GPU distributed smoke run completed end-to-end, wrote `last.pt` and
  `best_val_miou.pt`, and produced finite values for every loss component.
- Backpropagation assertions proved finite non-zero gradients at the learned
  monocular depth logits, auxiliary classifier and final TDP semantic classifier.
