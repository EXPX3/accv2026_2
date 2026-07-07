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
