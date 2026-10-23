# AI Coding Agents and Software Economics: Research Summary

The Customer Is the Builder: How AI Coding Agents Are Rewriting the Economics of Software is a preprint by Ripon Chandra Malo, Zimeng Yu, and Tong Qiu at the University of Utah.

[Read the paper](https://arxiv.org/abs/2610.30307). [Paper DOI](https://doi.org/10.48550/arXiv.2610.30307). [Archived code and data](https://doi.org/10.5281/zenodo.23524847).

## What is the research question?

Could AI coding agents make it economical for organizations to build and maintain software functionality they previously bought? The study compares growing capacity to build with indicators of changes in purchasing. It reports evidence that supports the proposed mechanism and evidence that challenges it.

## What is the software substitution frontier?

The software substitution frontier is the set of functions customers could build and maintain at an acceptable standard for less than buying them. The comparison includes verification, integration, hosting, security, and maintenance. It concerns the customer's required workflow rather than necessarily reproducing an entire commercial product.

## Who is the customer?

The main focus is organizations and professional buyers whose domain knowledge helps them specify and evaluate tools. These include firms, institutions, teams, scientists, and engineers. Public developer populations do not represent all such buyers, particularly those with limited technical support.

## What evidence does the repository contain?

The research combines software task-horizon benchmarks and benchmark costs with GitHub activity, package creation, open-source alternative discovery, installation measures, software investment, surveys, and case studies. Each source measures a separate part of the proposed mechanism. See the [data documentation](DATA.md) and [notebooks](../notebooks/).

## Does the paper show that AI is replacing paid software?

The evidence does not establish a broad shift from buying to building. Public creation measures expanded, while purchasing indicators remained mixed. Survey respondents reported some decisions to forgo purchases, but those reports do not verify the spending displaced or the sustained reliability of internal tools. Repositories and downloads do not identify canceled subscriptions.

## Do the projections predict when software vendors will lose customers?

No. The capability projections extend measured benchmark trends under stated assumptions. They are an extrapolation, not a forecast of customer switching. A benchmark task horizon is expressed in human task duration; it is not the same as continuous autonomous agent labor or a maintained product.

## What are the implications for SaaS and software vendors?

A credible internal build option could affect purchasing negotiations before aggregate spending changes. Narrow workflows may become economical to build while buyers continue paying for shared infrastructure, integrations, reliable operation, support, and accountability. The research does not measure how much these services protect vendor prices or renewals.

## How can the results be reproduced?

Install the dependencies in `requirements.txt`, then run `python tools/build_figures.py` from the repository root. This workflow uses included processed tables without making network requests. Open `notebooks/00_overview.ipynb` for the module index. Live collection is separate and may encounter API quotas or return different observations.

## How should this work be cited?

Cite the [arXiv paper](https://arxiv.org/abs/2610.30307) for the framework, findings, and interpretation. Cite the [Zenodo archive](https://doi.org/10.5281/zenodo.23524847) when using the archived research materials. [CITATION.cff](../CITATION.cff) provides structured metadata and [CITATION.bib](../CITATION.bib) provides BibTeX entries. The preprint has not undergone journal peer review.
