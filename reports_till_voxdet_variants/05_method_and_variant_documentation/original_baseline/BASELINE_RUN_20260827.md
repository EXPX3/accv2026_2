# Monocular VoxDet OccuFly baseline — 2026-08-27

## Run status

The eight-GPU run completed all 20 epochs on DGX-3. The validation-selected
checkpoint was evaluated once on the OccuFly test split before the experiment
was stopped. No training or evaluation process remains active.

Artifacts are preserved outside Git at:

`/datatank/giridhar.vb/data/checkpoints/VoxDet_original_related/monocular_voxdet_occufly_teacherdepth_full20_seed42_20260827`

- `history.csv`: epochs 0 through 19
- `last.pt`: epoch 19
- `best_val_miou.pt`: validation-selected epoch 8
- `test_metrics.json`: one test evaluation of `best_val_miou.pt`

## Validation selection

Epoch 8 produced the highest validation SSC mIoU:

- SC precision: 0.19021952
- SC recall: 0.11386563
- SC IoU: 0.07669085
- SSC mIoU: 0.00436444

## Final OccuFly test metrics

- SC precision: 0.51441991
- SC recall: 0.13008246
- SC IoU: 0.11585648
- SSC mIoU: 0.00679001

Only class 14 obtained material semantic IoU (0.12221926); most occupied
classes were zero and classes absent from the test confusion matrix were
reported as null. This is semantic collapse, not a competitive VoxDet result.

## Identified fidelity issue

This baseline used unweighted voxel cross-entropy. The reference VoxDet
occupancy head uses inverse-log class-frequency weights together with semantic
and geometric scaling losses; its camera configuration also supervises
auxiliary and final heads with different weights. Omitting those objectives
strongly favors OccuFly's dominant empty class and is consistent with the
observed collapse. Published SemanticKITTI/KITTI-360 results must therefore not
be compared directly with this baseline.

Any corrective experiment must use a new output directory and preserve these
artifacts as the immutable baseline.
