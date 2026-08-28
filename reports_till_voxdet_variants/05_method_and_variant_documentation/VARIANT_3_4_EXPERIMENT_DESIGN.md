# VoxDet Variant 3 and Variant 4: controlled OccuFly ablation design

## Status

This document fixes the experimental contract for Variant 3 and the proposed
Variant 4 run. Variant 3 is implemented under
`variant_3_film_dpt_depth_resnet_context_128ch`; Variant 4 remains a design and
is not claimed as implemented, trained or evaluated.

## Fixed depth checkpoint

Both variants must initialize their depth-FiLM-DPT branch from exactly:

```text
/datatank/giridhar.vb/data/checkpoints/my_checkpoints/01_shared_film_dpt_rgb_occufly_rerun_fullsweep/lr_8e_4__wd_1e_4/dpt_film_best.pt
```

The file was verified on the DGX filesystem on 2026-08-28. It is a 7.2 GB
checkpoint selected by validation RMSE, not by test performance. Its recorded
evaluation metadata is:

| Metric | Value |
|---|---:|
| Best validation RMSE | 2.2721700788 m |
| Test RMSE | 4.7701946796 m |
| Test MAE | 3.4571656980 m |
| Test AbsRel | 0.1313209936 |
| Test delta1 | 0.8156339114 |
| Test delta2 | 0.9695953459 |
| Test delta3 | 0.9976966545 |

The source metadata is stored beside the checkpoint in `metrics.json` and
`results-depth.csv`. Test depth metrics are reported for characterization only;
they did not select the checkpoint.

## Shared experimental contract

Variant 3 and Variant 4 must share all of the following:

- OccuFly training scenes 01--05, validation scenes 06--07 and test scenes
  08--09 at 30 m, 40 m and 50 m;
- the existing sparse raw-ID-to-contiguous-training-ID mapping, with empty class
  0 and ignore label 255;
- OccuFly `WHD = [192, 128, 128]`, with camera-right, camera-down and
  camera-forward axes and the established metric bounds;
- a low-resolution lifted volume in OccuFly WHD order with shape
  `[B, 128, 96, 64, 64]`;
- the same checkpoint-initialized depth-FiLM-DPT branch and the same depth-bin
  definition and calibrated OccuFly lifting;
- conversion of the dense metric-depth prediction into lifting probabilities
  with the existing `gaussian_dense` adapter (sigma 1 m), because the selected
  checkpoint was trained through `FeaturesToDepth` with linear normalization,
  rather than treating its 256 DPT channels as categorical-bin logits;
- the same spatially decoupled voxel encoder, task-decoupled dense predictor,
  VoxNT supervision, auxiliary occupancy head, inverse-log class weights,
  semantic-scaling loss and geometric-scaling loss;
- identical optimizer, learning-rate groups, scheduler, batch size, number of
  epochs, random seed and checkpoint-selection rule;
- checkpoint selection using validation SSC mIoU only, followed by one test
  evaluation of the selected checkpoint.

No test label, test depth map or test metric may influence optimization,
hyperparameter selection, early stopping or checkpoint selection.

## Variant 3

Recommended run tag:

```text
variant_3_film_dpt_depth_resnet_context_128ch
```

Architecture:

```text
RGB image
  -> original VoxDet ResNet-50 context encoder
  -> context projection to 128 channels

RGB image
  -> checkpoint-initialized depth-FiLM-DPT branch
  -> metric depth distribution

128-channel context + depth distribution
  -> calibrated OccuFly 2D-to-3D lifting
  -> [B, 128, 96, 64, 64] WHD feature volume
  -> auxiliary occupancy head
  -> spatially decoupled voxel encoder
  -> VoxDet TDP + VoxNT
  -> full-resolution OccuFly SSC logits
```

For a controlled comparison with Variant 2, “original ResNet-50” means the
existing `resnet50(weights=None)` initialization. Substituting ImageNet weights
would introduce an additional pretraining variable and must be assigned a
separate run tag.

Variant 2 versus Variant 3 measures the combined effect of replacing the
from-scratch 32-bin depth head with the fixed depth-FiLM-DPT initialization and
increasing the lifted representation from 32 to 128 channels.

## Variant 4

Recommended run tag:

```text
variant_4_film_dpt_depth_vjepa21_dpt_context_128ch_reference_losses_auxhead
```

Architecture:

```text
RGB image
  -> frozen V-JEPA2.1 ViT-G multi-layer features [11, 23, 37, 47]
  -> DPT context decoder/projection to 128 channels

RGB image
  -> the same checkpoint-initialized depth-FiLM-DPT branch as Variant 3
  -> metric depth distribution

128-channel V-JEPA2.1/DPT context + depth distribution
  -> calibrated OccuFly 2D-to-3D lifting
  -> [B, 128, 96, 64, 64] WHD feature volume
  -> auxiliary occupancy head
  -> spatially decoupled voxel encoder
  -> VoxDet TDP + VoxNT
  -> full-resolution OccuFly SSC logits
```

Variant 3 versus Variant 4 isolates the image-context encoder: original
randomly initialized ResNet-50 versus frozen V-JEPA2.1 multi-layer DPT context.

Variant 4 is intentionally close to FSSC-VoxDet Variant 1 at the frontend. The
scientific comparison between them isolates the reference-aligned class
weighting and auxiliary-head supervision only if their lifting implementation,
128-channel volume, decoder initialization, optimizer and training schedule are
otherwise held fixed.

## Required reporting

Each run must preserve:

- per-epoch training losses and validation SC IoU/SSC mIoU;
- the best-validation checkpoint and the final checkpoint;
- test SC precision, recall and IoU;
- test SSC mIoU excluding empty;
- raw-ID-aware per-class precision, recall, Dice/F1 and IoU;
- depth RMSE/AbsRel and depth-distribution diagnostics;
- projected-volume coverage and VoxNT offset-loss diagnostics;
- the resolved checkpoint paths, Git commit, complete command line and random
  seed.

The resulting rows should be added to
`reports/ssc_benchmark_browser/CLASSWISE_SSC_COMPARISON_LIVE.md` only after the
validation-selected checkpoint has completed the test evaluation.
