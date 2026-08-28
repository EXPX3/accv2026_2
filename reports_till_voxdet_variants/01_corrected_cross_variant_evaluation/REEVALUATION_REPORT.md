# Canonical OccuFly SSC re-evaluation report

Generated from repository commit `4bc18cd868839c2bb37b65863efce62467febbd5` on dgx-3 with Python `3.11.15`.

## Protocol

All corrected rows use the same ordered 3,842-sample test manifest with SHA-256 `9f87fcd0c4f4f236e4b7d9b56e7624965bbb0f595d36fcc83870e77add782cb6`, ignore target 255, and one int64 22×22 confusion matrix. OccuFly has 22 valid classes including empty. Historical FSSC heads use an explicit raw-indexed 37→22 channel adapter; CGFormer DAV2 and Variants 2–5 use 22 contiguous channels directly. The primary semantic score excludes empty and averages only GT-present semantic classes.

## Corrected ranking by primary SSC mIoU

| Rank | Model | SSC mIoU GT-present (%) | SC IoU (%) |
|---:|---|---:|---:|
| 1 | FSSC-VoxDet V1 — FSSC RGB-context/DPT + FiLM-DPT depth + spatial encoder + VoxDet TDP/VoxNT | 3.8292 | 39.4726 |
| 2 | FSSC-VoxDet V5 — corrected VoxNT/evaluation | 3.8155 | 39.5436 |
| 3 | FSSC RGB context DPT, depth FiLM-DPT | 3.4849 | 34.4203 |
| 4 | FSSC-VoxDet V4 — FiLM-DPT depth + V-JEPA 2.1 DPT context, 128-channel volume | 3.4747 | 38.8690 |
| 5 | FSSC-VoxDet V3 — FiLM-DPT depth + ResNet context, 128-channel volume | 2.8502 | 38.8508 |
| 6 | Monocular VoxDet V2 — reference losses and auxiliary head | 1.8729 | 27.0889 |
| 7 | CGFormer DAV2 prior | 1.3736 | 9.9257 |

## Unavailable or deferred models

- **CGFormer Vjepa2_1ML_FiLM_DPT:** checkpoint retained, but its recorded V-JEPA depth-prior dependency tree is missing; no substitution permitted. Older reported values are retained as historical evidence and are not presented as canonical re-evaluations.
- **FSSC RGB context FiLM-DPT, depth FiLM-DPT:** checkpoint unavailable. Older reported values are retained as historical evidence and are not presented as canonical re-evaluations.
- **FSSC video context DTA-DPT, depth DTA-MVS:** checkpoint unavailable. Older reported values are retained as historical evidence and are not presented as canonical re-evaluations.
- **FSSC video context DTA-DPT, depth DTA-FiLM-MVS:** checkpoint unavailable. Older reported values are retained as historical evidence and are not presented as canonical re-evaluations.
- **FSSC-VoxDet V5 v2 — long-tail/depth-gradient/full-resolution VoxNT/cosine:** training active on DGX-4; deliberately excluded from this audit snapshot. Older reported values are retained as historical evidence and are not presented as canonical re-evaluations.

## Interpretation

Differences between historical and corrected numbers are evaluator/reporting effects, not model improvements. The FSSC discrepancy arose from displaying a 37-channel raw-ID-indexed vector as if it were a contiguous semantic vector: raw channel 0 (empty) appeared under road, while raw channel 16 (building) appeared under cable_tower. Canonical inference corrects that mapping before accumulating the confusion matrix. Exact rank-strided evaluation also eliminates padding duplicates; all completed models share the same manifest and sample count.

The camera-only OccuFly scores are dataset-domain results. For context, official VoxDet reports 47.81% SC IoU / 18.67% SSC mIoU on SemanticKITTI camera and 48.59% / 21.40% on KITTI-360 camera. These are contextual cross-dataset references, not directly comparable measurements. The 63.0% LiDAR SC result is intentionally excluded from camera-to-camera ranking because its modality differs.

See `../METRIC_DISCREPANCY_AUDIT.md` for the traced historical indexing failure and `historical_vs_corrected.csv` for metric-level deltas. Original inference logs are preserved under `/datatank/giridhar.vb/data/checkpoints/corrected_evaluation_v1/<model>/`; they are not copied or altered by this report builder.
