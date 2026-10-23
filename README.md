# The Customer Is the Builder: AI Coding Agents and Software Economics

Research code, datasets, and Python notebooks for The Customer Is the Builder: How AI Coding Agents Are Rewriting the Economics of Software.

The study examines how AI coding agents could change organizations' decisions to buy software or build the functionality they need. It connects agent benchmarks, public software creation, open-source alternatives, and purchasing indicators. The central question is when an internal build becomes a credible alternative to paid software.

Authors: Ripon Chandra Malo, Zimeng Yu, and Tong Qiu, University of Utah.

## Paper and research data

- [Read the paper on arXiv: 2610.30307](https://arxiv.org/abs/2610.30307).
- [Paper DOI: 10.48550/arXiv.2610.30307](https://doi.org/10.48550/arXiv.2610.30307).
- [Download the paper PDF](https://arxiv.org/pdf/2610.30307).
- [Archived research code and data: Zenodo DOI 10.5281/zenodo.23524847](https://doi.org/10.5281/zenodo.23524847).
- [Research summary and common questions](docs/RESEARCH_SUMMARY.md).
- [Data sources and limitations](docs/DATA.md).

The paper is an empirical position paper released as a preprint. It has not undergone journal peer review. The paper DOI identifies the manuscript; the Zenodo DOI identifies the archived research materials.

## What the study examines

| Research question | Evidence |
|---|---|
| What can AI coding agents complete? | Software task horizons, coding benchmarks, general capability scores, and benchmark costs. |
| Is public software creation changing? | GitHub activity, package registries, AI-attributed commits, and Show HN projects. |
| Are alternatives to commercial software appearing? | Repository searches, product screening, and the Craft suite case study. |
| Are customers changing purchasing decisions? | Software investment, installation measures, organizational surveys, and adjacent freelance markets. |
| What could happen if measured capability trends continue? | Conditional benchmark extrapolations and observable tests of future adoption. |

We define the software substitution frontier as the functions customers could build and maintain at an acceptable standard for less than buying them. The customer is primarily an organization or professional buyer with relevant domain knowledge. The comparison concerns the required workflow and its continuing costs.

The evidence shows expanding capacity to create software alongside mixed purchasing indicators. It does not establish a broad collapse in paid software demand or a causal rate of customer substitution. Repository counts are not canceled subscriptions. Benchmark performance is not maintained-product reliability. The projections are an extrapolation, not a forecast of customer switching.

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

## Citation

For discussion of the findings, cite the paper:

Ripon Chandra Malo, Zimeng Yu, and Tong Qiu. The Customer Is the Builder: How AI Coding Agents Are Rewriting the Economics of Software. arXiv:2610.30307, 2026. https://doi.org/10.48550/arXiv.2610.30307.

```bibtex
@misc{malo2026customer,
  author = {Malo, Ripon Chandra and Yu, Zimeng and Qiu, Tong},
  title = {The Customer Is the Builder: How {AI} Coding Agents Are Rewriting the Economics of Software},
  year = {2026},
  eprint = {2610.30307},
  archivePrefix = {arXiv},
  primaryClass = {cs.SE},
  doi = {10.48550/arXiv.2610.30307},
  url = {https://arxiv.org/abs/2610.30307}
}
```

If you use the archived code or data, also cite the [Zenodo release](https://doi.org/10.5281/zenodo.23524847). Copyable entries for both records are in [CITATION.bib](CITATION.bib). GitHub's citation button uses [CITATION.cff](CITATION.cff).

## Research topics

AI coding agents; software economics; build versus buy; software substitution; agentic software development; open-source software alternatives; SaaS; developer productivity; software maintenance; reproducible research.

A concise index of the paper, data, and reproduction instructions is available in [llms.txt](llms.txt).
