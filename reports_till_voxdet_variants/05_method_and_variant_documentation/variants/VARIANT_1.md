# Variant 1: FSSC lifted volume + VoxDet SDE/TDP

Variant 1 retains the complete `FSSC RGB ctx DPT, depth FiLM-DPT` frontend and
3-D lifting path through dual feature fusion. It replaces
`FoundationSSCDecoder3D` (including FoundationSSC OccHead) with the VoxDet
three-stage local encoder, spatially decoupled FPN, six-direction VoxNT offset
predictor, instance-aware voxel aggregation, and semantic dense predictor.

The experiment uses the established OccuFly protocol: scenes 01--05 train,
06--07 validation, and 08--09 held-out test, each at 30/40/50 m. Internal FSSC
labels/logits use DHW while lifted volumes use OccuFly WHD. Sampling grids
explicitly convert WHD to PyTorch `grid_sample` coordinate order.

VoxNT artifacts are written to
`/datatank/giridhar.vb/repos/datasets/OccuFly_Dataset/VoxNT_for_occufly` with
direction order `w+,w-,h+,h-,d+,d-`. Variant 1 supervises all valid classes.
This can benefit compact, instance-like categories (vehicle, person, bicycle,
tree, crane, obstacle) but same-class extents are less instance-specific for
road, grass, water, and other amorphous regions. A useful-class-only experiment
is intentionally deferred to Variant 2.

Run correctness checks, VoxNT generation, and eight-GPU training:

```bash
/datatank/giridhar.vb/repos/.codex_envs/occufly_foundationssc_py311_torch21/bin/python \
  train_variant_1.py --variant1-self-test

/datatank/giridhar.vb/repos/.codex_envs/occufly_foundationssc_py311_torch21/bin/python \
  generate_voxnt_for_occufly.py --workers 8

bash run_variant_1_8gpu.sh
```

The primary metrics are the existing OccuFly SC IoU, SSC mIoU, and per-class
IoU outputs written by the reused FSSC training/evaluation implementation.
