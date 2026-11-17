# Chimney swifts: fluid equation in 3D

Same method as the horizontal fit, on a 3D grid (38 x 36 x 21 cells of 2.4 m, kernel 4.9 m). Includes vertical motion. 'z-hat' is a candidate new term: a constant vertical pull (gravity, or the descent into the chimney).

| Library | Samples | Held-out R^2 (all terms) | Held-out R^2 (sparse) | Kept terms |
| --- | --- | --- | --- | --- |
| without z-hat | 2027556 | 0.853 | 0.829 | `(v.grad)v` 0.926 |
| with z-hat | 2027556 | 0.853 | 0.829 | `(v.grad)v` 0.926 |
