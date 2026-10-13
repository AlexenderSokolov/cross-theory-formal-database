To compile use `make`. This project has been tested using the following dependencies (packages) installed via `opam`:

# Dependencies

|Name                  |Installed                   | Synopsis|
|----------------------|----------------------------|---------|
|`rocq`                |`9.0.0`                     | The Rocq Prover with Stdlib |
|`coq-stdpp`           |`1.11.0`                    | An extended "Standard Library" for Coq|
|`ocaml`               |`5.3.0`                    | The OCaml compiler (virtual package)|

# Project layout
```
.
+-- Readme.md
+-- Makefile
+-- _CoqProject
+-- theories/prelude.v (global parameters)
+-- theories/quotient.v (quotients in Rocq)
+-- theories/stepindex.v (ordinals interface)
+-- theories/ordinals (ordinals framework)
+-- theories/existential_prop
|   +-- classical.v (Choice+FunExt+PI->EM)
|   +-- sigma.v (equality of sigma-types)
|   +-- existential_prop.v (existential property)
+-- theories/categories/
|   +-- category.v (general constructions)
|   +-- contractive.v (subclass of locally contractive functors, example)
|   +-- coprod.v (coproducts)
|   +-- domain.v (uniqueness of solution, later is locally contractive, symmetrization, )
|   +-- enriched.v (partial isomorphisms and pointwise-enriched limits)
|   +-- logic.v (logical connectives for step-indexed logic)
|   +-- ord_cat.v (presheaves over ordinals, later, next, earlier, fixpoint)
|   +-- solution.v (solver for recursive domain equations)
```

# Paper-formalization glossary
| Paper entry | Rocq qualified identifier |
| ----------- | -------------- |
| later | ```SynthDom.categories.ord_cat.later``` |
| earlier | ```SynthDom.categories.ord_cat.earlier``` |
| next | ```SynthDom.categories.ord_cat.next``` |
| def. 3 | ```SynthDom.categories.ord_cat.Contractive``` |
| lemma 4 | ```SynthDom.categories.ord_cat.{Contractive_comp_l,Contractive_comp_r}``` |
| def. 5 | ```SynthDom.categories.ord_cat.{fixpoint, fixpoint_unfold, fixpoint_unique}``` |
| theorem 7 | ```SynthDom.categories.ord_cat.{contr_fix, contr_fix_unfold, contr_fix_unique}``` |
| def. 9 | ```SynthDom.categories.category.Enriched``` |
| def. 10 | ```SynthDom.categories.category.EnrichedFunctor``` |
| def. 11 | ```SynthDom.categories.enriched.LocallyContractiveFunctor``` |
| lemma 12 | ```SynthDom.categories.enriched.{LocallyContractiveFunctor_comp_l, LocallyContractiveFunctor_comp_r}``` |
| def. 13 | ```SynthDom.categories.enriched.is_iso_at``` |
| lemma 15 | ```SynthDom.categories.enriched.is_iso_upto_total``` |
| lemma 16 | ```SynthDom.categories.enriched.is_iso_at_func``` |
| lemma 17 | ```SynthDom.categories.enriched.iso_upto_contr_func``` |
| def. 18 | ```SynthDom.categories.enriched.enr_cone``` |
| def. 19 | ```SynthDom.categories.enriched.enr_cone_hom``` |
| def. 20 | ```SynthDom.categories.enriched.enr_cone_is_limit``` |
| lemma 21 | ```SynthDom.categories.enriched.{strongly_connected_iso_at_diagram_enr_cone, limit_side_iso_at', limit_side_iso_at}``` |
| corollary 22 | ```SynthDom.categories.enriched.limit_side_iso_at_cofinal``` |
| theorem 23 | ```SynthDom.categories.domain.alg_of_solution_is_initial``` |
| def. 24 | ```SynthDom.categories.solution.partial_solution``` |
| def. 25 | ```SynthDom.categories.solution.par_sol_extension``` |
| lemma 26 | ```SynthDom.categories.solution.the_extension``` |
| def. 27 | ```SynthDom.categories.solution.is_canonical_par_sol``` |
| lemma 28 | ```SynthDom.categories.solution.canonical_eq``` |
| lemma 29 | ```SynthDom.categories.solution.tower``` |
| theorem 30 | ```SynthDom.categories.solution.solver``` |
| example 32 | ```SynthDom.categories.solution.simplified_gitree_dom``` |
| lemma 33 | ```SynthDom.categories.domain.symmetrization_sol``` |
| theorem 34 | ```SynthDom.existential_prop.existential_prop.forall_exists_swap``` |
| def. 36 | ```SynthDom.existential_prop.existential_prop.regular``` |
| theorem 37 | ```SynthDom.categories.domain.{later_enriched, later_lc}``` |
| remark 40 | ```SynthDom.categories.enriched.{isomorphism_at_id, compose_along_isomorphism_at_left, compose_along_isomorphism_at_right, compose_along_is_iso_at_left, compose_along_is_iso_at_right, compose_along_is_iso_at_left', compose_along_is_iso_at_right', is_iso_at_compose, is_iso_at_uncompose_l, is_iso_at_uncompose_r}``` |
| theorem 42 | ```SynthDom.categories.ord_cat.later_adj``` |
| theorem 43 | ```SynthDom.categories.category.{func_limit, func_cat_limits_pointwise}``` |
| theorem 44 | ```SynthDom.categories.category.alg_complete``` |

# Notation glossary
## Category theory
| Construction | Rocq notation |
| -- | ----------------- |
| Isomorphism | ```≃``` |
| Terminal object | ```1ₒ``` |
| Products | ```a ×ₒ b``` |
| Unique product morphism | ```<< f, g >>``` |
| Product of morphisms | ```f ×ₕ g``` |
| Coproduct | ```a +ₒ b``` |
| Unique coproduct morphism | ```<< f ∣ g >>``` |
| Coproduct of morphisms | ```f +ₕ g``` |
| Exponential | ```b ↑ₒ a``` |
| Functor object action | ```F ₒ a``` |
| Functor morphism action | ```F ₕ f``` |
| Natural transformation component | ```H ₙ a``` |
