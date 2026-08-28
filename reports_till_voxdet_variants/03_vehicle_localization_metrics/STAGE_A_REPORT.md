# Stage A Completion Report

Status: exhaustive build and machine validation complete on DGX 5.

- Source frames: 20,611 (train 14,804; val 1,965; test 3,842).
- GT-vehicle-positive frames: 13,072 (train 7,936; val 1,912; test 3,224).
- Six-connected semantic pseudo-instances: 103,888.
- Vehicle voxels: 20,847,359.
- Grid: [W,H,D]=[192,128,128], camera right/down/forward, 0.5 m, bounds [-48,48] x [-32,32] x [0,64].
- Taxonomy: raw vehicle 13 -> contiguous vehicle 12; ignore 255.
- Pose: per-frame world_from_camera. Grid-to-camera is identity.
- Height values 30/40/50 are dataset altitude categories; no AGL claim is made.

All links, annotations, instance IDs, raw-to-training mapping, mask reconstructions, metric ranges, and connectivity records passed exhaustive validation. See validation_summary.json. Connected components remain semantic pseudo-instances rather than true instances. This is conditional vehicle localization on GT-vehicle-positive OccuFly frames and cannot yield an unbiased full-split false-positive rate.

Visual artifacts were generated for deterministic train/val/test samples in figures_gt_sanity as PNG and PDF. Automated artifact/array checks passed; interactive visual inspection was blocked by the client filesystem viewer sandbox and is explicitly not claimed.

## Reproduction

```bash
cd /datatank/giridhar.vb/repos/ws_jepa_occufly_test/experiments_wacv27/ssc/code/voxDet/vehicle_localization
PY=/datatank/giridhar.vb/repos/.codex_envs/occufly_nyu_py311/bin/python
$PY -m py_compile vehicle_localization.py
$PY -m unittest discover -s tests -v
SOURCE_MANIFEST=/datatank/giridhar.vb/repos/datasets/OccuFly_Dataset/vehicle_localization/manifests/source_manifest.csv \
INDEX_TO_GRID=/datatank/giridhar.vb/repos/datasets/OccuFly_Dataset/vehicle_localization/manifests/index_to_grid.txt \
LABEL_SPACE=raw MATERIALIZE=symlink PY=$PY bash run_pipeline.sh
```
