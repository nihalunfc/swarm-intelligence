# Findings so far

## 2026-11-16: first real data (schooling fish, Puy et al. 2024)

Full tables: [`results/nature/fish-tetra-2024.md`](../results/nature/fish-tetra-2024.md). Three recordings: 2 x 60 min with 39 fish, 1 x 28 min with 8 fish.

1. **The pipeline reproduces the published speed.** Median speed is 11.3 to 12.0 cm/s in the 39-fish schools. The paper set its model speed to 11 cm/s from the same data.
2. **Clear spacing rule.** Every recording shows repulsion at short range and attraction further out. The switch point is 1.6 body lengths in the 8-fish school and 3.1 to 3.8 body lengths in the 39-fish schools. Bigger schools space out more.
3. **Topological neighbours win, but only slightly.** Counting the k nearest fish (best k = 5 to 12) predicts turns better than a fixed radius (best 6 body lengths) in all three recordings. The margin is small, about 10%.
4. **Turns are mostly not explained by simple averages.** Neighbours' mean heading and centre explain only 6 to 10% of how a fish turns over the next 0.3 s. Tetras swim in bursts, and the paper itself finds they pay attention selectively (to faster neighbours). A better rule needs those terms.
5. **A fluid equation does not fit a 39-fish school.** The coarse-graining passes its check (continuity residual under 1%). But the best Toner-Tu fit explains only about 6% of the held-out acceleration field, and the kept terms change between the two recordings. With 39 fish there are only 2 to 3 animals inside each smoothing kernel, which is too few for a continuum.

**What this means for the plan:** the fluid stage needs large groups. The chimney swift data (about 1,800 birds) and starling data are the right test for it. Small groups such as the fish are better described by agent rules (stage 3).

**Not yet done:** birds (Dryad files need a manual browser download), 3D fields, comparison across species.
