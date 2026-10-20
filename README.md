# The Customer Is the Builder

Code and data for *The Customer Is the Builder: How AI Coding Agents Are Rewriting the Economics of Software*.

Authors: Ripon Chandra Malo, Zimeng Yu, and Tong Qiu, University of Utah.

## Setup

The analysis is tested with Python 3.12.

```bash
python -m venv .venv
```

Activate the environment with `.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on macOS and Linux. Then install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Reproduce figures

```bash
python tools/build_figures.py
```

The default workflow reads the included processed data and makes no network requests. Figures are written to `output/figures/` as PDF and PNG files. To reproduce one figure:

```bash
python plots/f02_ig_languages.py
```

## Notebooks

Open `notebooks/00_overview.ipynb` for the module index. Each analysis notebook loads the included tables and displays the corresponding figures. Notebook outputs are cleared in the repository.

```bash
jupyter lab
```

The capability and projection notebooks also include local calculations using the saved observations. To rerun the package break-date sensitivity analysis:

```bash
python tools/package_break_sensitivity.py
```

## Layout

```text
src/collect/       Collection and processing modules
src/               Paths, HTTP helpers, and figure styling
plots/             One script per figure
notebooks/         Analysis and inspection notebooks
data/raw/          Source snapshots and tabular inputs
data/processed/    Tables used by the analyses and figures
data/sample/       Product sample and case-study inputs
docs/DATA.md       Source links, definitions, and limitations
tools/             Figure and sensitivity-analysis commands
```

## Refreshing data

Collection functions in `src/collect/` can request new data from upstream services. Run them separately from the snapshot notebooks. Live collection can take substantial time, encounter API quotas, or return different observations. GitHub collection can use `GITHUB_TOKEN` or an authenticated GitHub CLI session. Optional service credentials are listed in `.env.example`; do not commit a filled environment file.

## Interpretation

Public activity, installations, reported purchasing decisions, and benchmark scores measure different outcomes. They do not identify a causal effect of coding agents or a verified customer substitution rate. Capability projections are conditional extrapolations. Broad alternative counts require independent workflow validation.

Observation dates and source URLs are retained. Retrieval timestamps are omitted from the distributed metadata. Raw source documents may contain their own publication dates and references to the technologies studied.

## Data reuse

Third-party data and source documents remain subject to their original licenses and terms. Source attribution is provided in `docs/DATA.md` and the data files.
