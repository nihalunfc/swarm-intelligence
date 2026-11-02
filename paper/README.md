# Paper

arXiv preprint: *When Does a Learned Swarm Beat the Rule? Residual Multi-Agent Reinforcement Learning for Grid Batteries, Wildfire Drones and Hotel Operations*. Author: Nihal.

Every table is generated from [`../results/`](../results), so re-running an experiment and rebuilding updates the paper.

```bash
sudo apt-get install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended
make -C paper          # tables from results/, then main.pdf
make -C paper arxiv    # arxiv.tar.gz to upload (tex, bbl, tables, figures)
```

CI builds the PDF on every pull request and keeps it as a downloadable artifact named `paper`.

## Before submitting

- [ ] Multi-seed results from the research-grade upgrade are in `results/` and wired into `make_tables.py`
- [ ] Every `\todo{}` is resolved, then `\drafttrue` is switched to `\draftfalse` in `main.tex` (any leftover TODO then fails the build)
- [ ] Bibliography entries checked against their arXiv pages
- [ ] Repository (or a public copy of the engine) is public and its URL is in the paper
- [ ] Endorsement for cs.MA from an existing arXiv author
- [ ] Submit: primary cs.MA, cross-list cs.LG and eess.SY; arXiv non-exclusive license; code stays MIT
