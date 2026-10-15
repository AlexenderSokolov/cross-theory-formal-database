/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Steinberg.B3Small.Defs

/-!

  File dox.

-/

namespace Steinberg.B3Small

open B3SmallPosRoot GradedPartialChevalley
  GradedChevalleyGenerator GradedPartialChevalleyGroup

variable {F : Type TF} [Field F]

/-! # "Given" relations for specific roots -/

declare_B3Small_lin_id_inv_thms F β
declare_B3Small_lin_id_inv_thms F ψ
declare_B3Small_lin_id_inv_thms F ω
declare_B3Small_lin_id_inv_thms F βψ
declare_B3Small_lin_id_inv_thms F ψω
declare_B3Small_lin_id_inv_thms F β2ψ

declare_B3Small_trivial_span_of_root_pair_thms F β βψ
declare_B3Small_trivial_span_of_root_pair_thms F β β2ψ
declare_B3Small_trivial_span_of_root_pair_thms F ψ β2ψ
declare_B3Small_trivial_span_of_root_pair_thms F βψ β2ψ
declare_B3Small_trivial_span_of_root_pair_thms F β ω
declare_B3Small_trivial_span_of_root_pair_thms F ψ ψω
declare_B3Small_trivial_span_of_root_pair_thms F ω ψω

declare_B3Small_single_span_of_root_pair_thms F ψ ω ψω 2
declare_B3Small_single_span_of_root_pair_thms F ψ βψ β2ψ 2

/-! ### Mixed-degree theorem for specific roots -/

declare_B3Small_mixed_degree_thms F βψ
declare_B3Small_mixed_degree_thms F ψω
declare_B3Small_mixed_degree_thms F β2ψ

declare_B3Small_defineThenReflect_thm F β
declare_B3Small_defineThenReflect_thm F ψ
declare_B3Small_defineThenReflect_thm F ω
declare_B3Small_defineThenReflect_thm F βψ
declare_B3Small_defineThenReflect_thm F ψω
declare_B3Small_defineThenReflect_thm F β2ψ

end Steinberg.B3Small
