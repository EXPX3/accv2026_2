# OccuFly Vehicle-Localization Dataset Card

Scope: Conditional vehicle localization on GT-vehicle-positive OccuFly frames.

Source frames: 20,611. Selected frames: 13,072. Six-connected semantic pseudo-instances: 103,888.

Grid: `[W,H,D]=[192,128,128]`, camera right/down/forward, 0.5 m voxels, metric bounds x `[-48,48]`, y `[-32,32]`, z `[0,64]`. Raw vehicle ID 13 maps to training ID 12; ignore is 255.

The 30/40/50 metadata values are official dataset altitude categories. They are not claimed to be above-ground altitude. Connected components are pseudo-instances, not true instance annotations. The positive-only subset is unsuitable for unbiased full-split false-positive estimates.

See `validation_summary.json`, `audit.json`, `manifests/source_audit.json`, `manifests/index_to_grid_audit.json`, and `figures_gt_sanity/`.
