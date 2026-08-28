# Conference Paper Scaffold

This repository is the reusable conference-paper scaffold for the
`ws_jepa_occufly_test` workspace. The `main` branch is intentionally minimal and
should remain a clean starting point for future conference papers.

Conference-specific paper state belongs on support branches:

```text
main              reusable paper scaffold
accv26-support    preserved ACCV26 paper state
wacv27-support    fresh WACV27 starting branch
```

## VoxDet reports and browser visualizations

The `wacv27-support` branch contains a portable archive of the corrected
VoxDet variant evaluations through Variant 5 v2. It includes SC/SSC and
classwise metrics—including the verified Variant 5 v2 result (45.7703% SC IoU, 4.6203% primary SSC mIoU, and 3.9603% fixed-21 SSC mIoU)—training histories, vehicle-localization results, GT versus
SSC instance comparisons, Hungarian matching at several 3D-IoU thresholds,
and semantic 3D voxel-grid views. All representative vehicle visualizations apply the frame-level minimum of 800 ground-truth vehicle voxels; groups without a qualifying frame are explicitly marked and never replaced by a below-threshold example.

**[Open the VoxDet browser-visualization index](reports_till_voxdet_variants/index.html)**

For reliable viewing after pulling the branch, start the included local server
from the repository root:

```bash
git switch wacv27-support
git pull
python3 reports_till_voxdet_variants/serve_reports.py --open
```

Then open [http://127.0.0.1:8770/](http://127.0.0.1:8770/) in the local-host
browser. The server uses only the Python standard library and binds to the
local machine by default.

## Structure

```text
main.tex                 paper entry point
content/chapters/        section files included by main.tex
content/images/          paper figures
content/tables/          paper tables
content/references.bib   bibliography database
docs/                    organizer/LNCS reference documentation
accv.sty                 organizer style file
accvabbrv.sty            organizer abbreviation helpers
llncs.cls                LNCS class file
splncs04.bst             LNCS bibliography style
```

Keep organizer-provided template files, class files, and bibliography styles in
the repository. Conference organizers are strict about formatting, margins,
fonts, and bibliography behavior; do not replace these files with generic
LaTeX scaffolding unless the target venue provides an official update.

## Compile

With Tectonic:

```bash
tectonic -X compile main.tex
```

With pdfLaTeX/BibTeX:

```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

Generated PDFs and auxiliary files should not be committed on `main`.
