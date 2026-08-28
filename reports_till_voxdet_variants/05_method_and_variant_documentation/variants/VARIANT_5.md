# Variant 5 — V-JEPA 2.1/DPT context + corrected VoxNT + fixed SSC evaluation

## Current training contract: v2

The default launcher now uses the versioned Variant 5 v2 training contract
documented in [TRAINING_CONTRACT_V2.md](TRAINING_CONTRACT_V2.md). It adds an
occupied/semantic-decoupled long-tail objective, controlled SSC gradients into
metric depth and depth probabilities, per-step warm-up plus cosine decay, and
full-resolution class-balanced VoxNT supervision for localizable classes. The
trainer owns these components explicitly and no longer monkey-patches Variant 3.

The original Variant 5 v1 result remains the controlled V4 geometry-correction
ablation. V1 and v2 have different objectives and must be reported separately.
V2 uses a new checkpoint tag, training-contract field, and fail-closed output
directory. Use `VARIANT=variant_5_v1` with the evaluation launcher when
re-evaluating an original Variant 5 checkpoint.

Variant 5 is a controlled correctness experiment derived from Variant 4.  It
keeps Variant 4's FiLM-DPT geometry, V-JEPA 2.1/DPT context, FSSC lifting,
128-channel VoxDet decoder, auxiliary/reference losses, optimizer, supervision
weights, split, and seed.  It changes only two geometry contracts and the
metric protocol.  The implementation is isolated in this directory, so it does
not modify the Variant 3 trainer used by an already-running Variant 4 process.

## Why this experiment comes before a new loss or backbone

The reported results separate occupancy quality from semantic quality:

| model | SC IoU (%) | SSC mIoU (%) | tree IoU (%) | building IoU (%) | parking lot IoU (%) |
|---|---:|---:|---:|---:|---:|
| FSSC-VoxDet V1 | **39.473** | **3.446** | **12.590** | **39.653** | **2.339** |
| Monocular VoxDet V2 | 27.089 | 1.774 | 1.973 | 24.983 | 0.447 |
| FSSC-VoxDet V3 | 38.851 | 2.700 | 3.904 | 35.227 | 1.886 |

V3 recovered +11.762 SC-IoU points and +0.926 SSC-mIoU points over V2, which
supports the FSSC lifting/frontend.  Relative to V1, however, V3 retained nearly
all occupancy quality (-0.622 SC-IoU) while losing 0.746 mIoU, dominated by tree
(-8.686 IoU), building (-4.427), vehicle (-2.074), road (-1.924), and walkway
(-1.129).  This is characteristic of a semantic-boundary/aggregation problem,
not simply failed free-space completion.  The audited TDP/VoxNT path contains
two deterministic geometry errors that can directly cause that pattern.

### 1. Full-resolution VoxNT was normalized at low resolution

The stored target is an inclusive directional run length at `[192,128,128]`.
The old loss first downsampled the raw run length to `[48,32,32]` and then
divided by `[48,32,32]`.  A full-width target therefore became `192/48 = 4`,
while the sigmoid predictor can emit only `[0,1]`.  This creates unreachable
targets, pushes the offset logits toward saturation, and weakens useful offset
gradients.

Variant 5 follows the official VoxDet target preparation:

1. divide the full-resolution W/H/D run lengths by full W/H/D;
2. nearest-neighbor resample the resulting dimensionless target;
3. mask ignored voxels and average over the six directions.

The axis divisor is the dimension length, not `length - 1`, matching VoxDet's
inclusive run-length construction and public loss implementation.

### 2. The sampling lattice disagreed with `align_corners=False`

The previous grid used `g(i)=2i/(S-1)-1`, the `align_corners=True` mapping, but
called `grid_sample(..., align_corners=False)`.  Under the actual sampler this
maps a nominal identity coordinate to

`i*S/(S-1) - 0.5`,

introducing a position-dependent half-voxel warp even when the learned offset is
zero.  Variant 5 uses the correct voxel-center mapping

`g(i)=2(i+0.5)/S-1`

and preserves the required PyTorch grid coordinate order `(D,H,W)` for tensors
stored as OccuFly `[B,C,W,H,D]`.

The implementation was cross-checked against the public
[VoxDet repository](https://github.com/vita-epfl/VoxDet), especially its
directional target generation and dense-head target normalization, and against
PyTorch's [`grid_sample` contract](https://pytorch.org/docs/stable/generated/torch.nn.functional.grid_sample.html).

## Metric discrepancy and the fixed protocol

The older evaluator selected SSC classes with `union > 0`.  Because union
depends on predictions, two models evaluated on the same test labels could be
averaged over different class sets.  This is visible in the supplied table:
V1's reported 3.446% is the mean of 20 nonblank class IoUs, whereas V3's 2.700%
is the mean of 19.  A model can therefore change the denominator by predicting
an otherwise absent class.

Variant 5 defines the headline `ssc_miou_gt_present` as the macro IoU over the 21 non-empty
semantic classes that have ground-truth support in the evaluated split.  This
mask is independent of model predictions.  The evaluator also reports:

- `ssc_miou_all_21_zero_filled`: secondary strict-taxonomy result with a fixed
  denominator over every non-empty class;
- `ssc_miou_legacy_union_present`: historical audit only, never model ranking;
- `ssc_fw_iou_nonempty`: semantic frequency-weighted IoU, excluding empty and
  normalized by occupied semantic ground-truth support;
- `fw_iou_all_22_including_empty`: optional all-voxel diagnostic, explicitly
  including the usually dominant empty class;
- SC precision, recall, and IoU;
- overall accuracy;
- per-class support, prediction count, TP/FP/FN, precision, recall, F1, and IoU;
- the complete 22x22 confusion matrix with explicit row/column orientation.

The comparison CSV contains historical blank cells and at least one implausible
cross-family class association (for example, 38.272% under `cable_tower` for an
FSSC run).  Do not use those columns for claims until the corresponding
checkpoint is re-evaluated under the contiguous 22-class taxonomy.  The new
evaluator can directly re-score Variants 3, 4, and 5.

## Files

- `core.py`: corrected sampling grids, VoxNT loss, and fixed metrics.
- `train_variant_5.py`: isolated Variant 5 model/trainer splice.
- `evaluate_checkpoint.py`: exact, non-padding distributed evaluator for V3–V5.
- `test_variant_5_core.py`: CPU identity, axis, normalization, gradient, and
  prediction-independent mIoU tests.
- `test_variant_5_wiring.py`: import-level trainer override and CLI preflight.
- `run_train_8gpu.sh` and `run_evaluate_8gpu.sh`: fail-closed launchers.

## Run

From this directory:

```bash
./run_train_8gpu.sh
```

The launcher runs the CPU contract tests before allocating the eight-GPU job
and refuses to reuse a non-empty output directory.  Paths can be overridden via
`PY`, `DATASET_ROOT`, `VOXNT_ROOT`, `TEACHER_DEPTH_ROOT`, `DEPTH_CHECKPOINT`,
`FREQUENCIES`, `OUT`, and `CUDA_VISIBLE_DEVICES`.

After training:

```bash
./run_evaluate_8gpu.sh
```

To re-score an older checkpoint with the same protocol:

```bash
VARIANT=variant_4 \
CHECKPOINT=/path/to/variant_4/best_val_miou.pt \
EVAL_OUT=/path/to/new/fixed_test_metrics \
./run_evaluate_8gpu.sh
```

Use `VARIANT=variant_3`, `variant_4`, or `variant_5`.  Evaluation uses an exact
distributed sampler without padding, so no sample is duplicated when the split
size is not divisible by eight.

## Scientific comparison protocol

1. Let the running V4 finish unchanged; do not transfer its optimizer state to
   V5 because the corrected auxiliary target changes the objective.
2. Train V5 with the checked-in seed-42 command and compare V4/V5 using the new
   evaluator on both validation and test checkpoints.
3. Report `ssc_miou_gt_present` as primary, `ssc_miou_all_21_zero_filled` as
   secondary, `ssc_fw_iou_nonempty` as the frequency-weighted semantic result,
   SC IoU, and the full
   class table.  Never compare the legacy union-present mIoU across methods as a
   headline number.
4. If V5 improves seed 42, reproduce V4 and V5 with at least seeds 43 and 44 and
   report mean, standard deviation, and paired per-seed differences.
5. Only after this geometry ablation should a long-tail Variant 6 change class
   weighting or add a region-aware semantic loss.  Combining those changes in
   V5 would make the source of any gain unidentifiable.

Primary acceptance criterion: V5 must improve fixed-protocol validation SSC
mIoU over V4 without a material SC-IoU regression.  Secondary criteria are
recovery of tree, vehicle, road/walkway, and parking-lot IoU, plus finite,
non-zero gradients in every trainer-checked module.
