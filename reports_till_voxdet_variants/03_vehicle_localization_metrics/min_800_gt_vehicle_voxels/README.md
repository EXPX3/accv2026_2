# Variant 5 v2 evaluation with a minimum of 800 GT vehicle voxels

This is a **frame-level conditional evaluation**. It retains official positive
test frames whose total ground-truth vehicle occupancy is at least 800 voxels.
It does not remove individual connected components and must not be compared as
an unbiased replacement for the full official test split.

- Retained frames: 1,776 / 3,224 GT-positive test frames (55.09%)
- Retained GT vehicle voxels: 5,877,197
- SC IoU: 19.48%
- SSC mIoU: 5.73%
- Vehicle IoU: 3.74%
- Instance IoU >= 0.25: TP 246, FP 16,565, FN 26,677
- Instance precision / recall / F1: 1.46% / 0.91% / 1.12%
- Matched centroid MAE: 1.407 m
- Instance IoU >= 0.50: one match

`summary_min_800_gt_vehicle_voxels.json` is the machine-readable source.
`retained_frames.csv` records the exact subset. The filtered frame/pair tables
preserve all conditional evaluation rows.

## Orientation clarification

OccuFly voxel indices are audited as camera-right, camera-down, camera-forward.
Upright 3D visualization therefore uses camera-right, camera-forward,
camera-up, where camera-up is the negative of camera-down. Native RGB is a
perspective camera image and is context only; a raw BEV/max-collapse voxel mask
cannot be overlaid on it without camera projection.
