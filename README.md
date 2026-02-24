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

**Blog version** (clean, no code shown):

```bash
quarto render
```

Output: `_site/index.html`

**Notebook version** (code visible with fold/expand):

```bash
quarto render --profile notebook
```

Output: `_site/notebook/index.html`

To preview either version locally without Quarto, serve the `_site/` directory:

```bash
cd _site && python -m http.server 8000
```

## Protocols

Experimental protocols used to generate the datasets in this blog post:

- [CYP Reactivity Assay](protocols/cyp_reactivity_assay.md) — CYP3A4/CYP2J2 reactivity screening via SCIEX Echo MS+ ZenoTOF 7600
- [CYP3A4 Inhibition Assay](protocols/cyp_inhibition_assay.md) — CYP3A4 inhibition (active preincubation) via fluorescence readout

## Data

All data is in `data/`:

| File | Description | Rows |
| --- | --- | --- |
| `reactivity.tsv` | Raw Echo-MS peak areas for CYP3A4 and CYP2J2 reactivity screening (control vs treatment, per compound/replicate) | 19,344 |
| `inhibition.tsv` | CYP3A4 pIC50 values, QC flags, and SMILES for inhibition screening | 1,340 |
| `inhibition_wells.tsv` | Well-level fluorescence data for CYP3A4 inhibition DRC fitting | 16,931 |
| `willitfly.tsv` | Ionization comparison: 1 mM ammonium fluoride vs 5 mM ammonium formate buffers | 11,353 |
| `clearance_snippet.tsv` | Example metabolic clearance time-course data | 292 |
| `tdi_drc_curves.tsv` | Fitted dose-response curves for time-dependent inhibition (TDI) assay | 3,012 |
| `tdi_drc_params.tsv` | Fitted DRC parameters (pIC50, Hill slope, CIs) for TDI compounds | 12 |
| `tdi_drc_points.tsv` | Raw DRC measurement points for TDI compounds | 144 |
| `tdi_pic50_shift.tsv` | pIC50 shift estimates (±preincubation) for TDI compounds | 6 |
| `inhibition_drc-plots/` | Dose-response curve images (1,343 PNGs) used as tooltips in Figure 3 | — |
