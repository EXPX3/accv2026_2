# VoxDet reports through Variant 5 v2

This directory is a portable archive of the corrected VoxDet evaluation,
per-variant metrics, vehicle-localization analysis, and requested voxel/instance
visualizations generated through 2026-08-28. Model checkpoints, raw prediction
volumes, caches, and training logs are intentionally excluded.

## View locally after pulling

From the `confxxx_checkbranch` repository root:

```bash
git switch wacv27-support
git pull
python3 reports_till_voxdet_variants/serve_reports.py --open
```

The command prints and optionally opens a URL such as
`http://127.0.0.1:8770/`. It uses only the Python standard library. If port
8770 is occupied, choose another one:

```bash
python3 reports_till_voxdet_variants/serve_reports.py --port 8870 --open
```

You can also open `reports_till_voxdet_variants/index.html` directly, although
the local server is more reliable for large self-contained visualization files.

## Structure

- `01_corrected_cross_variant_evaluation`: corrected SC/SSC metrics, classwise
  reports, rankings, checkpoint provenance, and static HTML browsers.
- `02_training_and_test_metrics`: training histories and available final test
  metrics grouped by variant.
- `03_vehicle_localization_metrics`: Stage A dataset audit and Stage B raw
  localization tables, including IoU/Hungarian matching results.
- `04_visualizations`: portable browser reports and all requested GT, SSC,
  instance, threshold, semantic, and 3D voxel views.
- `05_method_and_variant_documentation`: baseline, variant, method, dataset,
  evaluation-audit, and reproducibility documentation.

Start at [index.html](index.html) for links to every browser visualization.
