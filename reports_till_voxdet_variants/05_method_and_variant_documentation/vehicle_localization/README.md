# OccuFly vehicle-localization evaluation

This package creates a **GT-vehicle-positive OccuFly subset**, converts semantic
vehicle voxels into deterministic 3D connected-component pseudo-instances, and
applies the identical extraction to saved SSC predictions. It then performs
one-to-one 3D-IoU matching and reports instance detection and metric-centroid
localization errors.

The generated dataset root is exactly:

```text
/datatank/giridhar.vb/repos/datasets/OccuFly_Dataset/vehicle_localization
```

The builder never recursively discovers files: it consumes an audited source
manifest, so it cannot accidentally ingest its own output.

## Scientific scope

OccuFly supplies semantic voxels, not true instance IDs. Connected components
are therefore **pseudo-instances**. Same-class vehicles joined through the
chosen neighborhood are merged; fragmented vehicles can be split. The primary
protocol uses 6-connectivity and records a 6/18/26-connectivity sensitivity
audit for every selected frame.

Selecting frames using GT vehicle presence makes this a conditional
localization subset. Localization and recall are meaningful on that subset,
but full-split precision/false-positive claims require running the same
prediction extractor on every original validation/test frame, including
vehicle-negative frames.

## Fail-closed inputs

The code does not guess dataset layout or geometry. Prepare a CSV based on
`config/source_manifest.example.csv` with one row per original labelled frame.
Required columns are:

```text
sample_uid, split, scene_id, sequence_id, frame_id, image_path, label_path
```

Recommended columns are:

```text
height_m, height_category, scene_category,
grid_to_camera_path, grid_to_world_path
```

Paths may be absolute or relative to the manifest. Transform files must contain
finite homogeneous 4x4 matrices. Relative transform paths are resolved before
the subset manifest is written.

`--index-to-grid` is a 4x4 affine transform from a voxel **boundary index** in
the stored array-axis order to metric grid coordinates. Voxel centres are
transformed at `index + 0.5`. Do not use the example matrix until the actual
OccuFly WHD-to-coordinate convention, origin, signs and voxel size have been
verified.

The checked taxonomy is the canonical 22-class OccuFly training space. In raw
space, raw ID 13 maps to contiguous training ID 12 (`vehicle`), and 255 is the
only ignore value. Unknown IDs raise an error.

## Installation and tests

Use a compatible existing environment under
`/datatank/giridhar.vb/repos/.codex_envs`:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m py_compile vehicle_localization.py
```

## Build the subset

```bash
export SOURCE_MANIFEST=/absolute/path/to/audited_occufly_manifest.csv
export INDEX_TO_GRID=/absolute/path/to/verified_index_to_grid.txt
export LABEL_SPACE=raw        # use train only if label files are already 0..21
export MATERIALIZE=symlink    # or hardlink/copy
bash run_pipeline.sh
```

Output layout:

```text
vehicle_localization/
  images/{split}/
  semantic_gt/{split}/
  instances_gt/{split}/*.npz
  annotations_gt/{split}/*.json
  manifests/vehicle_positive.csv
  audit.json
```

`audit.json` records source/selected counts by split and the number of components
obtained under all three connectivity definitions.

## Evaluate SSC predictions

Predictions must be semantic `[W,H,D]` arrays aligned exactly with GT. The
default path template is `{prediction_root}/{split}/{sample_uid}.npz`, using
NPZ key `pred` and contiguous 22-class IDs.

```bash
python vehicle_localization.py evaluate \
  --subset-manifest /datatank/giridhar.vb/repos/datasets/OccuFly_Dataset/vehicle_localization/manifests/vehicle_positive.csv \
  --prediction-root /absolute/path/to/variant5/predictions \
  --prediction-template '{split}/{sample_uid}.npz' \
  --prediction-key pred \
  --prediction-label-space train \
  --index-to-grid "${INDEX_TO_GRID}" \
  --connectivity 6 \
  --min-pred-voxels 1 \
  --iou-thresholds 0.25 0.50 \
  --output /datatank/giridhar.vb/repos/datasets/OccuFly_Dataset/vehicle_localization/evaluation/variant_5
```

`min-pred-voxels` must remain 1 for the raw result. If filtering is used, choose
the threshold on training/validation data only and report both raw and filtered
results.

Outputs include predicted component volumes/annotations, per-frame TP/FP/FN,
matched-pair 3D IoU and centroid errors, aggregate precision/recall/F1, count
MAE, error percentiles and sequence-cluster bootstrap confidence intervals.

Generate the aggregate figures:

```bash
python vehicle_localization.py plot \
  --matched-metrics /datatank/giridhar.vb/repos/datasets/OccuFly_Dataset/vehicle_localization/evaluation/variant_5/matched_instance_metrics.csv \
  --iou-threshold 0.25 \
  --output /datatank/giridhar.vb/repos/datasets/OccuFly_Dataset/vehicle_localization/evaluation/variant_5/figures
```

Render a matched GT/prediction overlay for a selected failure case:

```bash
python vehicle_localization.py visualize \
  --gt-instances /path/to/instances_gt/test/SAMPLE.npz \
  --pred-instances /path/to/evaluation/instances_pred/test/SAMPLE.npz \
  --gt-annotations /path/to/annotations_gt/test/SAMPLE.json \
  --pred-annotations /path/to/evaluation/annotations_pred/test/SAMPLE.json \
  --image /path/to/images/test/SAMPLE.png \
  --projection-axis 2 \
  --output /path/to/evaluation/figures/SAMPLE_overlay.png
```

## Required DGX checks before claims

1. Verify the original official split manifest and raw-to-train mapping.
2. Verify the actual array order is `[W,H,D]` for both GT and predictions.
3. Verify `index_to_grid`, grid-to-camera, and grid-to-world directions using
   known points and inverse/round-trip tests.
4. Confirm pose Z semantics before calling it height or AGL altitude.
5. Inspect component overlays for all connectivity choices.
6. Run the evaluator on the complete official validation/test split for an
   unbiased false-positive-sensitive result.
7. Store the exact Variant 5 checkpoint SHA/config beside the evaluation.

## Methods and references

See [METHODS.md](METHODS.md), [DATASET_CARD.md](DATASET_CARD.md), and
[REFERENCES.md](REFERENCES.md).
