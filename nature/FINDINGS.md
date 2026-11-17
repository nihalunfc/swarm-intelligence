# Findings so far

## 2026-11-17 (later): swifts in 3D, and two real human bottlenecks

Tables: [`results/nature/swift-2017-3d.md`](../results/nature/swift-2017-3d.md), [`results/nature/bottlenecks.md`](../results/nature/bottlenecks.md).

1. **In 3D the swift flock is almost one term.** On a 3D grid with vertical motion included, the fit explains 83% of held-out acceleration (85% with all terms). The sparse fit keeps only self-advection, (v.grad)v, with coefficient 0.93. In plain words, each bird's acceleration is mostly the bend of a smooth, nearly steady flow that circles the roost. Pressure-like and viscosity-like forces are small at this scale. A constant vertical pull (gravity or the descent into the chimney) was tested and not needed. **Caveat:** a high R^2 from (v.grad)v says the flow is smooth and steady. It is not yet a force law that predicts how the flock reacts to something new.
2. **Flock rules help describe drivers at a lane drop.** At a real highway merge (four lanes to three, about 5,000 vehicles), a standard car-following rule explains 32.3% of the next-second speed change in congestion. Adding the two bird rules (match the 6 nearest vehicles' speed, move toward their centre) raises it to 35.5%. In free flow it goes from 7.2% to 10.1%. Drivers react to the group, not only to the car ahead, and most of the gain comes from cohesion. Densities match the dataset's own figures (108 vs 123 and 37 vs 41 veh/km, depending on how the periods are split).
3. **A crowd at an exit is not a fluid at 150 to 220 people.** Flow rises with exit width (1.6 to 2.8 people/s; 1.6 to 2.3 per metre of width). People keep a very steady personal space: the push-to-pull switch is 0.57 to 0.61 m at every width. Neighbour rules explain about 20% of turns, more than in any animal group, but the fluid fit explains only 1 to 10%, like the fish. Crowd order before the exit does not predict flow just after (r between -0.17 and 0.39), so "more aligned means more flow" is not supported here.

**What this means for nihal's bottleneck goal:** the evidence so far points to group-aware rules (cohesion with the k nearest) as the useful ingredient for vehicles. It does not point to a fluid equation, which only clearly fits the large, smoothly circling swift flock. The next test is a control experiment: give a share of the vehicles a cohesion rule in a model calibrated on DRaT, and measure throughput at the merge.


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
