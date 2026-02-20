# CYP Data Engine

Code and data to reproduce the figures in the CYP Data Engine blog post.

## Prerequisites

- [Quarto](https://quarto.org/docs/get-started/) (>= 1.4)
- [R](https://www.r-project.org/) (>= 4.5) with [renv](https://rstudio.github.io/renv/)
- [Python](https://www.python.org/) (>= 3.13) with [uv](https://docs.astral.sh/uv/)

## Setup

**R packages** — restore the `renv` lockfile:

```r
renv::restore()
```

**Python packages** — create the virtual environment from the lockfile:

```bash
uv sync
```

## Rendering

```bash
quarto render cyp-blog-post.qmd
```

Output is written to `_site/index.html`.

## Data

All data is in `data/`:

| File                    | Description                                                                                                      | Rows    |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------- | ------- |
| `reactivity.csv`        | Raw Echo-MS peak areas for CYP3A4 and CYP2J2 reactivity screening (control vs treatment, per compound/replicate) | ~19,000 |
| `inhibition.csv`        | CYP3A4 pIC50 values and SMILES for ~1,300 compounds                                                              | ~1,300  |
| `willitfly.tsv`         | Ionization comparison data: 1 mM ammonium fluoride vs 5 mM ammonium formate buffers for 11,000 compounds         | ~11,000 |
| `clearance_snippet.tsv` | Example clearance assay time-course data                                                                         | ~300    |
| `tdi_drc_curves.tsv`    | Dose-response curve data for time-dependent inhibition (TDI) assay                                               | ~500    |
| `tdi_drc_params.tsv`    | Fitted DRC parameters (pIC50, Hill slope, CIs) for TDI compounds                                                 | ~12     |
| `tdi_drc_points.tsv`    | Raw DRC measurement points for TDI compounds                                                                     | ~24     |
| `tdi_pic50_shift.tsv`   | pIC50 shift estimates (±preincubation) for TDI compounds                                                         | ~6      |
| `drc-plots/`            | Dose-response curve images (1,343 PNGs, no-controls versions) used as tooltips in Figure 3                       | —       |
| `rds/`                  | Preprocessed R data objects for Figure 4 assay development panels                                                | —       |
