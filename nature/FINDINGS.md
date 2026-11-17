# Findings so far

## 2026-11-17: four species (fish, jackdaws, pigeons, chimney swifts)

Full tables: [`results/nature/comparison.md`](../results/nature/comparison.md), plus one file per dataset in `results/nature/`. All data are real recordings: Dryad datasets were fetched from their Zenodo mirrors.

1. **The fluid equation works for big flocks and fails for small ones.** The same sparse Toner-Tu fit explains 66% of held-out motion for chimney swifts (about 240 to 940 birds per frame) but only about 13% for the 39-fish school. Kernel width is matched in neighbour units for both. The 71% at a wider kernel shows the fit improves as the description gets coarser. This is the first real support for the "flock as a fluid" picture, and it says where it applies: hundreds of animals or more.
2. **The kept terms look like a fluid with extras.** Self-advection ((v.grad)v) dominates, with coefficient 0.6 to 1.2 depending on kernel width; an ordinary fluid would give exactly 1. Two flock-specific terms are always kept: (div v) v and grad |v|^2 (the Toner-Tu lambda2 and lambda3, both negative). A density-gradient term is kept with a positive sign, so birds move toward crowded regions, which is cohesion, the opposite of gas pressure.
3. **A new candidate term was tested and not needed.** Adding a pull toward the chimney and circling around it (extrinsic roost terms) did not improve the held-out fit (0.656 vs 0.658). The density-gradient term already carries the roost's pull. The rule is to keep a new term only if it helps, so they stay out.
4. **The predator is a clear extrinsic parameter.** In pigeon flocks, when the robotic falcon comes within 30 m, the turning rate nearly triples (27 vs 10 deg/s when it is over 100 m away) and speed drops (17.3 vs 20.8 m/s). Polarisation stays above 0.99, so the flock turns together instead of breaking up.
5. **Topological vs metric depends on the species.** Pigeons follow the k nearest (7 of 8 big flocks with a signal, median k = 7, close to the 6 to 7 reported for starlings). Jackdaws in transit lean metric (4 of 6 flocks). Fish lean topological. The margins are small and individual turns stay hard to predict (R^2 under 10%), so this is a tendency, not a law.
6. **The spacing rule is consistent within a species.** Jackdaws switch from repulsion to attraction at 2.6 to 3.0 body lengths in all 6 flocks. Body lengths for birds are approximate field-guide values, so the cross-species numbers in BL are rough.

**Next:** test the swift equation in 3D (vertical motion included), run neighbour rules on swifts (needs track matching across frames), then plug the fitted terms into the agent swarm (stage 8) on a traffic or logistics bottleneck.


## 2026-11-16: first real data (schooling fish, Puy et al. 2024)

Full tables: [`results/nature/fish-tetra-2024.md`](../results/nature/fish-tetra-2024.md). Three recordings: 2 x 60 min with 39 fish, 1 x 28 min with 8 fish.

1. **The pipeline reproduces the published speed.** Median speed is 11.3 to 12.0 cm/s in the 39-fish schools. The paper set its model speed to 11 cm/s from the same data.
2. **Clear spacing rule.** Every recording shows repulsion at short range and attraction further out. The switch point is 1.6 body lengths in the 8-fish school and 3.1 to 3.8 body lengths in the 39-fish schools. Bigger schools space out more.
3. **Topological neighbours win, but only slightly.** Counting the k nearest fish (best k = 5 to 12) predicts turns better than a fixed radius (best 6 body lengths) in all three recordings. The margin is small, about 10%.
4. **Turns are mostly not explained by simple averages.** Neighbours' mean heading and centre explain only 6 to 10% of how a fish turns over the next 0.3 s. Tetras swim in bursts, and the paper itself finds they pay attention selectively (to faster neighbours). A better rule needs those terms.
5. **A fluid equation does not fit a 39-fish school.** The coarse-graining passes its check (continuity residual under 1%). But the best Toner-Tu fit explains only about 6% of the held-out acceleration field, and the kept terms change between the two recordings. With 39 fish there are only 2 to 3 animals inside each smoothing kernel, which is too few for a continuum.

**What this means for the plan:** the fluid stage needs large groups. The chimney swift data (about 1,800 birds) and starling data are the right test for it. Small groups such as the fish are better described by agent rules (stage 3).

**Update 2026-11-17:** birds added above. Point 5 was confirmed: the large swift flock fits the fluid equation far better.
