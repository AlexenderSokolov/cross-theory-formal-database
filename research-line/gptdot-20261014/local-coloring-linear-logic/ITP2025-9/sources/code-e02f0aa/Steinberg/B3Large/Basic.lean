/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Steinberg.B3Large.Defs

/-!

  File dox.

-/

namespace Steinberg.B3Large

open B3LargePosRoot GradedPartialChevalley GradedChevalleyGenerator GradedPartialChevalleyGroup

variable {F : Type TF} [Field F]

/-! # "Given" relations for specific roots -/

declare_B3Large_lin_id_inv_thms F α
declare_B3Large_lin_id_inv_thms F β
declare_B3Large_lin_id_inv_thms F ψ
declare_B3Large_lin_id_inv_thms F αβ
declare_B3Large_lin_id_inv_thms F βψ
declare_B3Large_lin_id_inv_thms F β2ψ

declare_B3Large_trivial_span_of_root_pair_thms F α αβ
declare_B3Large_trivial_span_of_root_pair_thms F β αβ
declare_B3Large_trivial_span_of_root_pair_thms F α ψ
declare_B3Large_trivial_span_of_root_pair_thms F β βψ
declare_B3Large_trivial_span_of_root_pair_thms F β β2ψ
declare_B3Large_trivial_span_of_root_pair_thms F ψ β2ψ
declare_B3Large_trivial_span_of_root_pair_thms F βψ β2ψ

declare_B3Large_single_span_of_root_pair_thms F α β αβ 1
declare_B3Large_single_span_of_root_pair_thms F ψ βψ β2ψ 2

-- Double: {(β, ψ)}
theorem comm_of_β_ψ : doubleSpanPropOfRootPair (weakB3LargeGraded F).project ⟨β, ψ, βψ, β2ψ, 1, 1, by rfl, by rfl⟩ :=
  (weakB3LargeGraded F).doubleSpanProp_of_mem_doubleSpanRootPairs ⟨β, ψ, βψ, β2ψ, 1, 1, by rfl, by rfl⟩
    (by unfold weakB3LargeGraded; simp)

/-! ### Mixed-degree theorem for specific roots -/

declare_B3Large_mixed_degree_thms F α
declare_B3Large_mixed_degree_thms F β
declare_B3Large_mixed_degree_thms F ψ
declare_B3Large_mixed_degree_thms F αβ
declare_B3Large_mixed_degree_thms F βψ
declare_B3Large_mixed_degree_thms F β2ψ

/- ### Reflected theorems for present roots -/

declare_B3Large_defineThenReflect_thm F α
declare_B3Large_defineThenReflect_thm F β
declare_B3Large_defineThenReflect_thm F ψ
declare_B3Large_defineThenReflect_thm F αβ
declare_B3Large_defineThenReflect_thm F βψ
declare_B3Large_defineThenReflect_thm F β2ψ

end Steinberg.B3Large
