/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Steinberg.B3Large.Basic
import Steinberg.B3Large.EstabAlpha2Beta2Psi

namespace Steinberg.B3Large

open Steinberg B3LargePosRoot GradedPartialChevalley GradedChevalleyGenerator GradedPartialChevalleyGroup

/-!

  File dox.

-/


variable {F : Type TF} [Field F] (Fchar : (2 : F) ≠ 0)
variable (F_sum_of_squares : ∀ (a : F), ∃ (x y : F), a = x^2 + y^2)

include Fchar

set_option maxHeartbeats 0

-- 8.185
theorem partial_comm_of_ψ_α2β2ψ :
    ∀ (t u : F), ⁅⸨ψ, 1, t⸩, ⸨α2β2ψ, 0, u⸩⁆ = 1 := by
  apply sufficient_conditions_for_comm_of_ψ_and_α2β2ψ Fchar (i := 1) (j := 0) (k := 0) (by trivial) (by trivial) (by trivial)
  · intro t u
    rw [triv_comm_symm, lift_hom_comm_of_β2ψ_αβψ (i := 1) (j := 0) (k := 0) (by trivial) (by trivial) (by trivial)]
  · intro t u
    rw [triv_comm_symm, partial_comm_of_β2ψ_αβ2ψ_b (by trivial)]

/- ### ψ and α + 2β + 2ψ commute -/

private lemma comm_of_ψ_α2β2ψ_00 :
    ∀ (t u : F), ⁅⸨ψ, 0, t⸩, ⸨α2β2ψ, 0, u⸩⁆ = 1 := by
  intro t u
  rw [eq_of_coef_eq α2β2ψ (-u * -1) (by ring),
  expr_α2β2ψ_as_comm_of_αβ_β2ψ (i := 0) (j := 0) Fchar (by trivial) (by trivial),
  hom_lift_of_comm_ψ_αβ_β2ψ (i := 0) (j := 0) (k := 0) (by trivial) (by trivial) (by trivial)]

private lemma comm_of_ψ_α2β2ψ_01 :
    ∀ (t u : F), ⁅⸨ψ, 0, t⸩, ⸨α2β2ψ, 1, u⸩⁆ = 1 := by
  intro t u
  rw [eq_of_coef_eq α2β2ψ (-u * -1) (by ring),
  expr_α2β2ψ_as_comm_of_αβ_β2ψ (i := 1) (j := 0) Fchar (by trivial) (by trivial),
  hom_lift_of_comm_ψ_αβ_β2ψ (i := 1) (j := 0) (k := 0) (by trivial) (by trivial) (by trivial)]

private lemma comm_of_ψ_α2β2ψ_02 :
    ∀ (t u : F), ⁅⸨ψ, 0, t⸩, ⸨α2β2ψ, 2, u⸩⁆ = 1 := by
  intro t u
  rw [eq_of_coef_eq α2β2ψ (-u * -1) (by ring),
  expr_α2β2ψ_as_comm_of_αβ_β2ψ (i := 1) (j := 1) Fchar (by trivial) (by trivial),
  hom_lift_of_comm_ψ_αβ_β2ψ (i := 0) (j := 1) (k := 0) (by trivial) (by trivial) (by trivial)]

private lemma comm_of_ψ_α2β2ψ_03 :
    ∀ (t u : F), ⁅⸨ψ, 0, t⸩, ⸨α2β2ψ, 3, u⸩⁆ = 1 := by
  intro t u
  rw [eq_of_coef_eq α2β2ψ (-u * -1) (by ring),
  expr_α2β2ψ_as_comm_of_αβ_β2ψ (i := 2) (j := 1) Fchar (by trivial) (by trivial),
  hom_lift_of_comm_ψ_αβ_β2ψ (i := 1) (j := 1) (k := 0) (by trivial) (by trivial) (by trivial)]

private lemma comm_of_ψ_α2β2ψ_10 :
    ∀ (t u : F), ⁅⸨ψ, 1, t⸩, ⸨α2β2ψ, 0, u⸩⁆ = 1 :=
  partial_comm_of_ψ_α2β2ψ Fchar

private lemma comm_of_ψ_α2β2ψ_11 :
    ∀ (t u : F), ⁅⸨ψ, 1, t⸩, ⸨α2β2ψ, 1, u⸩⁆ = 1 := by
  intro t u
  rw [eq_of_coef_eq α2β2ψ (-u * -1) (by ring),
  expr_α2β2ψ_as_comm_of_αβ2ψ_β (i := 1) (j := 0) Fchar (by trivial) (by trivial),
  partial_comm_of_ψ_αβ2ψ_β (by trivial)]

-- reflected theorems
declare_B3Large_triv_comm_reflected_thm F b3large_valid ψ α2β2ψ heights 0 4 to 1 1
declare_B3Large_triv_comm_reflected_thm F b3large_valid ψ α2β2ψ heights 0 5 to 1 0
declare_B3Large_triv_comm_reflected_thm F b3large_valid ψ α2β2ψ heights 1 2 to 0 3
declare_B3Large_triv_comm_reflected_thm F b3large_valid ψ α2β2ψ heights 1 3 to 0 2
declare_B3Large_triv_comm_reflected_thm F b3large_valid ψ α2β2ψ heights 1 4 to 0 1
declare_B3Large_triv_comm_reflected_thm F b3large_valid ψ α2β2ψ heights 1 5 to 0 0

-- 8.186
theorem comm_of_ψ_α2β2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project (ψ, α2β2ψ) := by
  intro i j hi hj
  match i, j with
  | 0, 0 => exact comm_of_ψ_α2β2ψ_00 Fchar
  | 0, 1 => exact comm_of_ψ_α2β2ψ_01 Fchar
  | 0, 2 => exact comm_of_ψ_α2β2ψ_02 Fchar
  | 0, 3 => exact comm_of_ψ_α2β2ψ_03 Fchar
  | 0, 4 => exact comm_of_ψ_α2β2ψ_04 Fchar
  | 0, 5 => exact comm_of_ψ_α2β2ψ_05 Fchar
  | 1, 0 => exact comm_of_ψ_α2β2ψ_10 Fchar
  | 1, 1 => exact comm_of_ψ_α2β2ψ_11 Fchar
  | 1, 2 => exact comm_of_ψ_α2β2ψ_12 Fchar
  | 1, 3 => exact comm_of_ψ_α2β2ψ_13 Fchar
  | 1, 4 => exact comm_of_ψ_α2β2ψ_14 Fchar
  | 1, 5 => exact comm_of_ψ_α2β2ψ_15 Fchar
declare_B3Large_trivial_span_expr_thm F ψ α2β2ψ

-- 8.187
theorem comm_of_β2ψ_α2β2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project (β2ψ, α2β2ψ) := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  rcases decompose 1 2 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  rw [eq_of_coef_eq β2ψ (2 * t * (1 / 2)) (by field_simp), expr_β2ψ_as_ψ_βψ_ψ_βψ]
  grw [expr_βψ_α2β2ψ_as_α2β2ψ_βψ Fchar hi₂, expr_ψ_α2β2ψ_as_α2β2ψ_ψ Fchar hi₁,
  expr_βψ_α2β2ψ_as_α2β2ψ_βψ Fchar hi₂, expr_ψ_α2β2ψ_as_α2β2ψ_ψ Fchar hi₁]
declare_B3Large_trivial_span_expr_thm F β2ψ α2β2ψ

-- 8.188
theorem comm_of_αβψ_α2β2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project (αβψ, α2β2ψ) := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  rcases decompose 2 1 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  rw [←mul_one t, expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi₁ hi₂]
  grw [expr_ψ_α2β2ψ_as_α2β2ψ_ψ Fchar, expr_αβ_α2β2ψ_as_α2β2ψ_αβ Fchar,
  expr_ψ_α2β2ψ_as_α2β2ψ_ψ Fchar, expr_αβ_α2β2ψ_as_α2β2ψ_αβ Fchar, expr_ψ_α2β2ψ_as_α2β2ψ_ψ Fchar]
declare_B3Large_trivial_span_expr_thm F αβψ α2β2ψ

-- 8.189
theorem comm_of_αβ2ψ_α2β2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project (αβ2ψ, α2β2ψ) := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  rcases decompose 3 1 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  rw [eq_of_coef_eq αβ2ψ (-2 * t * (-1 / 2)) (by field_simp), expr_αβ2ψ_as_αβψ_ψ_αβψ_ψ Fchar hi₁ hi₂]
  grw [expr_ψ_α2β2ψ_as_α2β2ψ_ψ Fchar, expr_αβψ_α2β2ψ_as_α2β2ψ_αβψ Fchar,
  expr_ψ_α2β2ψ_as_α2β2ψ_ψ Fchar, expr_αβψ_α2β2ψ_as_α2β2ψ_αβψ Fchar]
declare_B3Large_trivial_span_expr_thm F αβ2ψ α2β2ψ

-- 8.190
theorem comm_of_α2β2ψ :
    mixedDegreePropOfRoot (weakB3LargeGraded F).project α2β2ψ := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  rcases decompose 4 1 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  rw [eq_of_coef_eq α2β2ψ (-t * (-1)) (by ring), expr_α2β2ψ_as_comm_of_αβ2ψ_β Fchar hi₁ hi₂,
  commutatorElement_def, inv_of_β, inv_of_αβ2ψ Fchar hi₁]
  grw [expr_β_α2β2ψ_as_α2β2ψ_β Fchar, expr_αβ2ψ_α2β2ψ_as_α2β2ψ_αβ2ψ Fchar,
  expr_β_α2β2ψ_as_α2β2ψ_β Fchar, expr_αβ2ψ_α2β2ψ_as_α2β2ψ_αβ2ψ Fchar]
declare_B3Large_mixed_expr_thm F α2β2ψ

-- 8.191
theorem comm_of_αβψ_β2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project (αβψ, β2ψ) := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  -- expand αβψ into product of αβ and ψ elements (work on LHS)
  rcases decompose 2 1 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  rw [eq_of_coef_eq αβψ (-2 * (-t / 2) * 1) (by ring_nf; field_simp), expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi₁ hi₂]
  -- move β2ψ from the right to the left
  grw [expr_ψ_β2ψ_as_β2ψ_ψ, expr_αβ_β2ψ_as_β2ψ_α2β2ψ_αβ Fchar hi₁ hj, expr_ψ_β2ψ_as_β2ψ_ψ,
  expr_αβ_β2ψ_as_β2ψ_αβ_α2β2ψ Fchar hi₁ hj, expr_ψ_β2ψ_as_β2ψ_ψ]
  -- commute α2β2ψ across ψ and cancel
  grw [expr_ψ_α2β2ψ_as_α2β2ψ_ψ Fchar]
  rw [eq_of_coef_eq α2β2ψ (-(t * u)) (by ring_nf; field_simp)]
  nth_rewrite 2 [eq_of_coef_eq α2β2ψ (t * u) (by ring_nf; field_simp)]
  rw [←inv_of_α2β2ψ Fchar (add_le_add hi₁ hj), inv_mul_cancel, one_mul]
declare_B3Large_trivial_span_expr_thm F αβψ β2ψ

-- 8.192
theorem comm_of_βψ_αβ2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project (βψ, αβ2ψ) := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  -- expand βψ as a product of ψ and β elements (work on LHS)
  rcases decompose 1 1 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  rw [eq_of_coef_eq βψ (-2 * (-1 / 2) * t) (by ring_nf; field_simp), expr_βψ_as_ψ_β_ψ_β_ψ Fchar hi₁ hi₂]
  -- move αβ2ψ fully to the left
  grw [expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar, expr_β_αβ2ψ_as_αβ2ψ_α2β2ψ_β Fchar hi₂ hj,
  expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar, expr_β_αβ2ψ_as_αβ2ψ_β_α2β2ψ Fchar hi₂ hj, expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar]
  -- commute α2β2ψ across ψ and cancel
  grw [expr_ψ_α2β2ψ_as_α2β2ψ_ψ Fchar]
  rw [← inv_of_α2β2ψ Fchar (add_le_add hi₂ hj), mul_inv_cancel, one_mul]
declare_B3Large_trivial_span_expr_thm F βψ αβ2ψ

-- 8.193
theorem comm_of_β2ψ_αβ2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project (β2ψ, αβ2ψ) := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  rcases decompose 1 2 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  rw [eq_of_coef_eq β2ψ (2 * t * (1 / 2)) (by field_simp), expr_β2ψ_as_ψ_βψ_ψ_βψ hi₁ hi₂]
  grw [expr_βψ_αβ2ψ_as_αβ2ψ_βψ Fchar, expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar,
  expr_βψ_αβ2ψ_as_αβ2ψ_βψ Fchar, expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar]
declare_B3Large_trivial_span_expr_thm F β2ψ αβ2ψ

-- 8.194
theorem comm_of_αβψ_αβ2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project (αβψ, αβ2ψ) := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  rcases decompose 1 2 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  rw [←mul_one t, expr_αβψ_as_βψ_α_βψ_α_βψ hi₁ hi₂]
  grw [expr_βψ_αβ2ψ_as_αβ2ψ_βψ Fchar, expr_α_αβ2ψ_as_αβ2ψ_α Fchar, expr_βψ_αβ2ψ_as_αβ2ψ_βψ Fchar,
  expr_α_αβ2ψ_as_αβ2ψ_α Fchar, expr_βψ_αβ2ψ_as_αβ2ψ_βψ Fchar]
declare_B3Large_trivial_span_expr_thm F αβψ αβ2ψ

-- 8.195
theorem comm_of_αβ2ψ :
    mixedDegreePropOfRoot (weakB3LargeGraded F).project αβ2ψ := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  rcases decompose 3 1 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  rw [eq_of_coef_eq αβ2ψ (-2 * t * (-1 / 2)) (by ring_nf; field_simp), expr_αβ2ψ_as_ψ_αβψ_ψ_αβψ Fchar hi₁ hi₂]
  grw [expr_αβψ_αβ2ψ_as_αβ2ψ_αβψ Fchar, expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar,
  expr_αβψ_αβ2ψ_as_αβ2ψ_αβψ Fchar, expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar]
declare_B3Large_mixed_expr_thm F αβ2ψ

-- 8.196
@[simp, chev_simps]
theorem lin_of_αβ2ψ : lin_of_root((weakB3LargeGraded F).project, αβ2ψ) := by
  intro i hi t u
  rcases decompose 1 3 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  -- expand one αβ2ψ as product of α and β2ψ elements (work on LHS)
  rw [←mul_one t, expr_αβ2ψ_as_α_β2ψ_α_β2ψ Fchar hi₁ hi₂]
  -- move the αβ2ψ to the left but not all the way
  grw [expr_β2ψ_αβ2ψ_as_αβ2ψ_β2ψ Fchar, expr_α_αβ2ψ_as_αβ2ψ_α Fchar, expr_β2ψ_αβ2ψ_as_αβ2ψ_β2ψ Fchar]
  -- expand αβ2ψ as product of α and β2ψ elements
  rw [←mul_one u, expr_αβ2ψ_as_α_β2ψ_α_β2ψ Fchar hi₁ hi₂, ←inv_of_β2ψ]
  -- collect back into an αβ2ψ term
  grw [rfl]
  rw [←mul_one (t + u), expr_αβ2ψ_as_α_β2ψ_α_β2ψ Fchar hi₁ hi₂]
  group

-- 8.197
@[simp, chev_simps]
theorem lin_of_α2β2ψ : lin_of_root((weakB3LargeGraded F).project, α2β2ψ) := by
  intro i hi t u
  rcases decompose 2 3 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  -- expand one α2β2ψ as product of αβ and β2ψ elements (work on LHS)
  rw [eq_of_coef_eq α2β2ψ (-t * -1) (by ring), expr_α2β2ψ_as_αβ_β2ψ_αβ_β2ψ Fchar hi₁ hi₂, neg_neg]
  -- move the α2β2ψ to the left but not all the way
  grw [expr_β2ψ_α2β2ψ_as_α2β2ψ_β2ψ Fchar, expr_αβ_α2β2ψ_as_α2β2ψ_αβ Fchar, expr_β2ψ_α2β2ψ_as_α2β2ψ_β2ψ Fchar]
  -- expand α2β2ψ as product of αβ and β2ψ elements
  rw [eq_of_coef_eq α2β2ψ (-u * -1) (by ring), expr_α2β2ψ_as_αβ_β2ψ_αβ_β2ψ Fchar hi₁ hi₂, neg_neg, ←inv_of_β2ψ]
  -- collect back into α2β2ψ term
  grw [rfl]
  rw [eq_of_coef_eq α2β2ψ (-(t + u) * -1) (by ring), expr_α2β2ψ_as_αβ_β2ψ_αβ_β2ψ Fchar hi₁ hi₂]
  group

-- 8.198
theorem hom_lift_of_comm_of_α_α2β2ψ_square : forall_ijk_tu α β ψ,
    ⁅⸨α, i, t⸩, ⸨α2β2ψ, i + 2 * j + 2 * k, -t * u^2⸩⁆ = 1 := by
  intro i j k hi hj hk t u
  have hi : i ≤ 1 := by ht
  have hj : j ≤ 1 := by ht
  have hk : k ≤ 1 := by ht
  have hjk : j + 2 * k ≤ β2ψ.height := by ht
  let t₁ : F := match i with
    | 1 => t
    | 0 => 0
  let t₀ : F := match i with
    | 1 => 0
    | 0 => t
  let u₁ : F := match j with
    | 1 => 1
    | 0 => 0
  let u₀ : F := match j with
    | 1 => 0
    | 0 => 1
  let v₁ : F := match k with
    | 1 => u
    | 0 => 0
  let v₀ : F := match k with
    | 1 => 0
    | 0 => u
  have hf_i : i ∈ [0,1] := by simp only [List.mem_cons, List.mem_singleton]; omega
  have hf_j : j ∈ [0,1] := by simp only [List.mem_cons, List.mem_singleton]; omega
  have hf_k : k ∈ [0,1] := by simp only [List.mem_cons, List.mem_singleton]; omega
  have aux₁ : ⸨α, i, t⸩ = ⸨α, 1, t₁⸩ * ⸨α, 0, t₀⸩ := by
    fin_cases hf_i, hf_j, hf_k
    <;> chev_simp [t₀, t₁, u₀, u₁, v₀, v₁]
  have aux₂ : ⸨αβ, i + j, t⸩ = ⸨αβ, 2, t₁ * u₁⸩ * ⸨αβ, 1, t₁ * u₀ + t₀ * u₁⸩ * ⸨αβ, 0, t₀ * u₀⸩ := by
    fin_cases hf_i, hf_j, hf_k
    <;> chev_simp [t₀, t₁, u₀, u₁, v₀, v₁]
  have aux₃ : ⸨β2ψ, j + 2 * k, u^2⸩ = ⸨β2ψ, 3, u₁ * v₁^2⸩ * ⸨β2ψ, 2, u₀ * v₁^2 + 2 * u₁ * v₀ * v₁⸩
          * ⸨β2ψ, 1, u₁ * v₀^2 + 2 * u₀ * v₀ * v₁⸩ * ⸨β2ψ, 0, u₀ * v₀^2⸩ := by
    fin_cases hf_i, hf_j, hf_k
    <;> chev_simp [pow_two, t₀, t₁, u₀, u₁, v₀, v₁]
  rw [eq_of_deg_eq α2β2ψ ((i + j) + (j + 2 * k)) (by omega),
      expr_α2β2ψ_as_comm_of_αβ_β2ψ Fchar (add_le_add hi hj) hjk,
      aux₁, aux₂, aux₃, raw_nonhom_lift_of_comm_of_α_α2β2ψ]

-- 8.199
include F_sum_of_squares

-- 8.200
theorem hom_lift_of_comm_of_α_α2β2ψ : forall_ijk_tu α β ψ,
    ⁅⸨α, i, t⸩, ⸨α2β2ψ, i + 2 * j + 2 * k, u⸩⁆ = 1 := by
  intro i j k hi hj hk t u
  rcases eq_or_ne t 0 with (rfl | ht)
  · chev_simp
  rcases F_sum_of_squares (-u / t) with ⟨r, s, hrs⟩
  have := (mul_left_inj' ht).2 hrs
  ring_nf at this
  field_simp at this
  have hu : u = (-t * r^2) + (-t * s^2) := by
    rw [neg_mul, neg_mul, ←neg_add]
    exact neg_eq_iff_eq_neg.1 this
  have h₁ := triv_comm_iff_commutes.1 (hom_lift_of_comm_of_α_α2β2ψ_square Fchar hi hj hk t r)
  have h₂ :=  triv_comm_iff_commutes.1 (hom_lift_of_comm_of_α_α2β2ψ_square Fchar hi hj hk t s)
  chev_simp [← mul_assoc] at h₁ h₂
  apply triv_comm_iff_commutes.2
  rw [hu, ← lin_of_α2β2ψ Fchar]
  chev_simp [← mul_assoc]
  grw [h₁, h₂]

@[group_reassoc]
theorem expr_α_α2β2ψ_as_α2β2ψ_α_parity : forall_ijk_tu α β ψ,
    ⸨α, i, t⸩ * ⸨α2β2ψ, i + 2 * j + 2 * k, u⸩ = ⸨α2β2ψ, i + 2 * j + 2 * k, u⸩ * ⸨α, i, t⸩ := by
  intro i j k hi hj hk t u
  apply triv_comm_iff_commutes.1
  exact hom_lift_of_comm_of_α_α2β2ψ Fchar F_sum_of_squares hi hj hk t u

-- 8.201
theorem nonhom_lift_of_comm_of_α_α2β2ψ : forall_ij_tu α β,
    ⁅⸨α, i, t⸩, ⸨α2β2ψ, i + 2 * j + 1, u⸩⁆ = 1 := by
  intro i j hi hj t u
  rcases eq_or_ne t 0 with ht | ht
  · rw [ht, id_of_α]; group
  have hi : i ≤ 1 := by ht
  have hj : j ≤ 1 := by ht

  -- things to plug into 8.82
  let t₁ : F := match i with
    | 1 => t
    | 0 => 0
  let t₀ : F := match i with
    | 1 => 0
    | 0 => t
  let u₁ : F := match j with
    | 1 => 1
    | 0 => 0
  let u₀ : F := match j with
    | 1 => 0
    | 0 => 1
  let v₁ : F := 1
  let v₀ : F := -u / (2 * t)
  have hf_i : i ∈ [0,1] := by simp only [List.mem_cons, List.mem_singleton]; omega
  have hf_j : j ∈ [0,1] := by simp only [List.mem_cons, List.mem_singleton]; omega
  have aux₁ : 2 * (u / (2 * t)) = u / t := by ring_nf; field_simp; group
  have aux₂ : u / (2 * t) * (u / (2 * t)) = (u * u) / (4 * (t * t)) := by
    ring_nf; simp only [inv_pow, mul_eq_mul_left_iff, inv_inj, mul_eq_zero, ne_eq,
      OfNat.ofNat_ne_zero, not_false_eq_true, pow_eq_zero_iff, inv_eq_zero];
    left
    rw [pow_two, mul_two, two_add_two_eq_four]
  have hα : ⸨α, 1, t₁⸩ * ⸨α, 0, t₀⸩ = ⸨α, i, t⸩ := by
    fin_cases hf_i, hf_j
    <;> chev_simp [t₀, t₁, u₀, u₁, v₀, v₁]
  have hαβ : ⸨αβ, 2, t₁ * u₁⸩ * ⸨αβ, 1, t₁ * u₀ + t₀ * u₁⸩ * ⸨αβ, 0, t₀ * u₀⸩ = ⸨αβ, i + j, t⸩ := by
    fin_cases hf_i, hf_j
    <;> chev_simp [t₀, t₁, u₀, u₁, v₀, v₁]
  have hβ2ψ : ⸨β2ψ, 3, u₁ * v₁^2⸩ * ⸨β2ψ, 2, u₀ * v₁^2 + 2 * u₁ * v₀ * v₁⸩
          * ⸨β2ψ, 1, u₁ * v₀^2 + 2 * u₀ * v₀ * v₁⸩ * ⸨β2ψ, 0, u₀ * v₀^2⸩
          = ⸨β2ψ, j + 2, 1⸩ * ⸨β2ψ, j + 1, -u / t⸩ * ⸨β2ψ, j, u^2 / (4 * t^2)⸩ := by
    fin_cases hf_i, hf_j
    <;> chev_simp [t₀, t₁, u₀, u₁, v₀, v₁, aux₁, aux₂, pow_two, one_mul]

  -- apply 8.82 and simplify stuff
  rw [←raw_nonhom_lift_of_comm_of_α_α2β2ψ t₁ t₀ u₁ u₀ v₁ v₀, hα, hαβ, hβ2ψ, commutatorElement_def,
  commutatorElement_def, commutatorElement_def, inv_of_α, inv_of_αβ, mul_inv_rev, mul_inv_rev, mul_inv_rev,
  mul_inv_rev, mul_inv_rev, mul_inv_rev, mul_inv_rev, mul_inv_rev, mul_inv_rev, inv_inv, inv_inv,
  inv_inv, inv_of_β2ψ, inv_of_β2ψ, inv_of_β2ψ, inv_of_αβ, inv_of_αβ, neg_neg]

  -- move pairs of β2ψ elements across αβ and cancel them
  rw [expr_β2ψ_β2ψ_as_β2ψ_β2ψ (i := j + 2) (j := j + 1) (t := 1) (u := -u / t),
  ←expr_β2ψ_β2ψ_as_β2ψ_β2ψ (i := j + 2) (j := j + 1) (t := -1) (u := -(-u / t))]
  mal
  grw [expr_αβ_β2ψ_as_β2ψ_α2β2ψ_αβ (i := i + j) (t := -t) (j := j) Fchar (by ht) (by ht),
  expr_αβ_β2ψ_as_β2ψ_α2β2ψ_αβ (i := i + j) (t := t) (j := j) Fchar (by ht) (by ht)]

  -- move the α2β2ψ together and cancel them
  grw [expr_β2ψ_α2β2ψ_as_α2β2ψ_β2ψ Fchar, expr_β2ψ_α2β2ψ_as_α2β2ψ_β2ψ Fchar]
  nth_rewrite 4 [eq_of_deg_coef_eq α2β2ψ (i + 2 * j + 2 * 0) (by omega) (u * u / (4 * t))
    (by ring_nf; simp only [inv_pow, neg_inj, mul_eq_mul_right_iff, inv_eq_zero]
        left; rw [pow_two]; field_simp
        repeat rw [← mul_assoc]; grw [mul_comm t u, mul_comm t u])]
  grw [expr_α_α2β2ψ_as_α2β2ψ_α_parity Fchar F_sum_of_squares hi hj (by trivial),
  expr_β2ψ_α2β2ψ_as_α2β2ψ_β2ψ Fchar, expr_β2ψ_α2β2ψ_as_α2β2ψ_β2ψ Fchar, expr_αβ_α2β2ψ_as_α2β2ψ_αβ Fchar]
  nth_rewrite 3 [eq_of_deg_coef_eq α2β2ψ (i + 2 * j) (by omega) (-(u * u / (4 * t)))
    (by ring_nf; simp only [inv_pow, neg_inj, mul_eq_mul_right_iff, inv_eq_zero]
        left; rw [pow_two]; field_simp
        repeat rw [← mul_assoc]; grw [mul_comm t u, mul_comm t u])]
  rw [←inv_of_α2β2ψ Fchar (by ht)]
  grw [rfl]

  -- move pairs of β2ψ elements together across αβ and cancel them
  grw [expr_αβ_β2ψ_as_β2ψ_α2β2ψ_αβ (i := i + j) (j := j + 2) (t := -t) Fchar (by ht) (by ht),
  expr_αβ_β2ψ_as_β2ψ_α2β2ψ_αβ (i := i + j) (j := j + 2) (t := t) Fchar (by ht) (by ht)]

  -- move the α2β2ψ together and cancel them
  grw [expr_β2ψ_α2β2ψ_as_α2β2ψ_β2ψ Fchar]
  nth_rewrite 4 [eq_of_deg_eq α2β2ψ (i + 2 * j + 2 * 1) (by omega)]
  grw [expr_α_α2β2ψ_as_α2β2ψ_α_parity Fchar F_sum_of_squares hi hj (by trivial),
  expr_β2ψ_α2β2ψ_as_α2β2ψ_β2ψ Fchar, expr_αβ_α2β2ψ_as_α2β2ψ_αβ Fchar]
  nth_rewrite 3 [eq_of_deg_eq α2β2ψ (i + 2 * j + 2) (by omega)]
  rw [←inv_of_α2β2ψ Fchar (by ht)]
  grw [rfl]

  -- expand the α2β2ψ elements on the LHS
  rw [eq_of_deg_coef_eq α2β2ψ ((i + j) + (j + 1)) (by omega) (-t * (-(u / t))) (by ring_nf; field_simp),
  expr_α2β2ψ_as_αβ_β2ψ_αβ_β2ψ Fchar (by ht) (by ht), neg_neg]
  grw [rfl]
  mal

-- 8.202
omit F_sum_of_squares in
theorem sufficient_conditions_for_comm_of_αβ_and_αβ2ψ :
    ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 1) (hj : j ≤ 1) (hk : k ≤ 4)
    (hyp : ∀ (t u : F), ⁅⸨α, i, t⸩, ⸨α2β2ψ, j + k, u⸩⁆ = 1),
    ∀ (t u : F), ⁅⸨αβ, i + j, t⸩, ⸨αβ2ψ, k, u⸩⁆ = 1 := by
  intro i j k hi hj hk hyp t u
  have hyp' := fun t u ↦ triv_comm_iff_commutes.1 (hyp t u)
  apply triv_comm_iff_commutes.2
  -- expand αβ into product of α and β elements (work on LHS)
  rw [←one_mul t, expr_αβ_as_α_β_α_β]
  -- move αβ2ψ to the left
  grw [expr_β_αβ2ψ_as_αβ2ψ_α2β2ψ_β Fchar hj hk, expr_α_αβ2ψ_as_αβ2ψ_α Fchar hi,
  expr_β_αβ2ψ_as_αβ2ψ_β_α2β2ψ Fchar hj hk, expr_α_αβ2ψ_as_αβ2ψ_α Fchar hi]
  -- use hyp to cancel the αβ2ψ elements
  grw [hyp' (-1)]
  rw [← inv_of_α2β2ψ Fchar (by ht), mul_inv_cancel, one_mul]

-- 8.203
theorem partial_comm_of_αβ_α2β2ψ :
    ∀ (t u : F), ⁅⸨αβ, 0, t⸩, ⸨αβ2ψ, 1, u⸩⁆ = 1 := by
  apply sufficient_conditions_for_comm_of_αβ_and_αβ2ψ (i := 0) (j := 0) (k := 1) Fchar (by trivial) (by trivial) (by trivial)
  intro t u
  rw [nonhom_lift_of_comm_of_α_α2β2ψ (i := 0) (j := 0) (by trivial) (by trivial) (by trivial) (by trivial)]

-- 8.204
omit F_sum_of_squares in
theorem sufficient_conditions_for_comm_of_α_and_α2β2ψ :
    ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 1) (hj : j ≤ 2) (hk : k ≤ 3)
    (hyp : ∀ (t u : F), ⁅⸨αβ, j, t⸩, ⸨αβ2ψ, i + k, u⸩⁆ = 1),
    ∀ (t u : F), ⁅⸨α, i, t⸩, ⸨α2β2ψ, j + k, u⸩⁆ = 1 := by
  intro i j k hi hj hk hyp t u
  have hyp' := fun t u ↦ triv_comm_iff_commutes.1 (hyp t u)
  apply triv_comm_iff_commutes.2
  -- expand α2β2ψ as product of αβ and β2ψ elements (work on LHS)
  rw [eq_of_coef_eq α2β2ψ (-u * (-1)) (by ring), expr_α2β2ψ_as_αβ_β2ψ_αβ_β2ψ Fchar hj hk, neg_neg]
  -- move the α element fully to the right
  grw [expr_α_αβ_as_αβ_α, expr_α_β2ψ_as_β2ψ_αβ2ψ_α Fchar hi hk, expr_α_αβ_as_αβ_α, expr_α_β2ψ_as_αβ2ψ_β2ψ_α Fchar hi hk]
  -- use hyp to cancel to the αβ2ψ elements
  grw [hyp' (-u)]
  rw [←inv_of_αβ2ψ Fchar (by ht), inv_mul_cancel, one_mul]


-- 8.205
theorem partial_comm_of_α_α2β2ψ :
    ∀ (t u : F), ⁅⸨α, 1, t⸩, ⸨α2β2ψ, 0, u⸩⁆ = 1 := by
  apply sufficient_conditions_for_comm_of_α_and_α2β2ψ (i := 1) (j := 0) (k := 0) Fchar (by trivial) (by trivial) (by trivial)
  exact partial_comm_of_αβ_α2β2ψ Fchar F_sum_of_squares

/- ### α and α + 2β + 2ψ commute -/

private lemma comm_of_α_α2β2ψ_00 :
    ∀ (t u : F), ⁅⸨α, 0, t⸩, ⸨α2β2ψ, 0, u⸩⁆ = 1 :=
  @hom_lift_of_comm_of_α_α2β2ψ F _ Fchar F_sum_of_squares 0 0 0 (by trivial) (by trivial) (by trivial)

private lemma comm_of_α_α2β2ψ_01 :
    ∀ (t u : F), ⁅⸨α, 0, t⸩, ⸨α2β2ψ, 1, u⸩⁆ = 1 :=
  @nonhom_lift_of_comm_of_α_α2β2ψ F _ Fchar F_sum_of_squares 0 0 (by trivial) (by trivial)

private lemma comm_of_α_α2β2ψ_02 :
    ∀ (t u : F), ⁅⸨α, 0, t⸩, ⸨α2β2ψ, 2, u⸩⁆ = 1 :=
  @hom_lift_of_comm_of_α_α2β2ψ F _ Fchar F_sum_of_squares 0 1 0 (by trivial) (by trivial) (by trivial)

private lemma comm_of_α_α2β2ψ_03 :
    ∀ (t u : F), ⁅⸨α, 0, t⸩, ⸨α2β2ψ, 3, u⸩⁆ = 1 :=
  @nonhom_lift_of_comm_of_α_α2β2ψ F _ Fchar F_sum_of_squares 0 1 (by trivial) (by trivial)

private lemma comm_of_α_α2β2ψ_04 :
    ∀ (t u : F), ⁅⸨α, 0, t⸩, ⸨α2β2ψ, 4, u⸩⁆ = 1 :=
  @hom_lift_of_comm_of_α_α2β2ψ F _ Fchar F_sum_of_squares 0 1 1 (by trivial) (by trivial) (by trivial)

private lemma comm_of_α_α2β2ψ_10 :
    ∀ (t u : F), ⁅⸨α, 1, t⸩, ⸨α2β2ψ, 0, u⸩⁆ = 1 :=
  partial_comm_of_α_α2β2ψ Fchar F_sum_of_squares

-- reflected theorems
declare_B3Large_triv_comm_reflected_thm F b3large_valid α α2β2ψ heights 0 5 to 1 0
declare_B3Large_triv_comm_reflected_thm F b3large_valid α α2β2ψ heights 1 1 to 0 4
declare_B3Large_triv_comm_reflected_thm F b3large_valid α α2β2ψ heights 1 2 to 0 3
declare_B3Large_triv_comm_reflected_thm F b3large_valid α α2β2ψ heights 1 3 to 0 2
declare_B3Large_triv_comm_reflected_thm F b3large_valid α α2β2ψ heights 1 4 to 0 1
declare_B3Large_triv_comm_reflected_thm F b3large_valid α α2β2ψ heights 1 5 to 0 0

-- 8.206
theorem comm_of_α_α2β2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project (α, α2β2ψ) := by
  intro i j hi hj
  match i, j with
  | 0, 0 => exact comm_of_α_α2β2ψ_00 Fchar F_sum_of_squares
  | 0, 1 => exact comm_of_α_α2β2ψ_01 Fchar F_sum_of_squares
  | 0, 2 => exact comm_of_α_α2β2ψ_02 Fchar F_sum_of_squares
  | 0, 3 => exact comm_of_α_α2β2ψ_03 Fchar F_sum_of_squares
  | 0, 4 => exact comm_of_α_α2β2ψ_04 Fchar F_sum_of_squares
  | 0, 5 => exact comm_of_α_α2β2ψ_05 Fchar F_sum_of_squares
  | 1, 0 => exact comm_of_α_α2β2ψ_10 Fchar F_sum_of_squares
  | 1, 1 => exact comm_of_α_α2β2ψ_11 Fchar F_sum_of_squares
  | 1, 2 => exact comm_of_α_α2β2ψ_12 Fchar F_sum_of_squares
  | 1, 3 => exact comm_of_α_α2β2ψ_13 Fchar F_sum_of_squares
  | 1, 4 => exact comm_of_α_α2β2ψ_14 Fchar F_sum_of_squares
  | 1, 5 => exact comm_of_α_α2β2ψ_15 Fchar F_sum_of_squares

-- 8.207
theorem comm_of_αβ_αβ2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project (αβ, αβ2ψ) := by
  intro i j hi hj
  rcases decompose 1 1 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  apply sufficient_conditions_for_comm_of_αβ_and_αβ2ψ Fchar (by trivial) (by trivial) (by trivial)
  intro t u
  apply comm_of_α_α2β2ψ Fchar F_sum_of_squares hi₁
declare_B3Large_trivial_span_expr_thm F αβ αβ2ψ

-- 8.208
theorem comm_of_αβψ :
    mixedDegreePropOfRoot (weakB3LargeGraded F).project αβψ := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  -- expand the left αβψ as a product of αβ and ψ elements (work on the LHS)
  rcases decompose 2 1 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  rw [←mul_one t, expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi₁ hi₂]
  -- move αβψ to the left
  grw [expr_ψ_αβψ_as_αβψ_αβ2ψ_ψ Fchar hi₂ hj, expr_αβ_αβψ_as_αβψ_αβ, expr_ψ_αβψ_as_αβψ_αβ2ψ_ψ Fchar hi₂ hj,
  expr_αβ_αβψ_as_αβψ_αβ, expr_ψ_αβψ_as_αβψ_ψ_αβ2ψ Fchar hi₂ hj]
  -- cancel the α2β2ψ terms
  grw [←expr_αβ_αβ2ψ_as_αβ2ψ_αβ Fchar F_sum_of_squares, expr_αβ_αβ2ψ_as_αβ2ψ_αβ Fchar F_sum_of_squares,
  expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar]
  rw [lin_of_αβ2ψ Fchar, lin_of_αβ2ψ Fchar]
  ring_nf; field_simp; ring_nf
  rw [id_of_αβ2ψ Fchar]
declare_B3Large_mixed_expr_thm F αβψ

-- 8.209
@[simp, chev_simps]
theorem lin_of_αβψ : lin_of_root((weakB3LargeGraded F).project, αβψ) := by
  intro i hi t u
  rcases decompose 2 1 i hi with ⟨i₁, i₂, rfl, hi₁, hi₂⟩
  -- expand one αβψ element into a product of ψ and αβ elements (work on LHS)
  rw [←mul_one t, expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi₁ hi₂]
  -- move αβψ from right to middle
  grw [expr_ψ_αβψ_as_αβψ_ψ_αβ2ψ Fchar hi₂ (add_le_add hi₁ hi₂), expr_αβ_αβψ_as_αβψ_αβ]
  -- expand the other αβψ element in the same way as before
  rw [←mul_one u, expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi₁ hi₂]
  -- simplify the product of ψ elements using linearity
  grw [rfl]
  -- commute ψ and αβ elements
  grw [expr_ψ_αβ_as_αβ_αβ2ψ_αβψ_ψ Fchar hi₁ hi₂ (t := u), expr_αβ_ψ_as_ψ_αβψ_αβ2ψ_αβ Fchar hi₁ hi₂ (t := -u)]
  -- commute αβψ across ψ and cancel
  grw [expr_ψ_αβψ_as_αβψ_αβ2ψ_ψ Fchar hi₂ (add_le_add hi₁ hi₂)]
  rw [eq_of_coef_eq αβψ (-(u / 2)) (by ring_nf; field_simp; group)]
  nth_rewrite 2 [eq_of_coef_eq αβψ (u / 2) (by ring_nf)]
  rw [←inv_of_αβψ (add_le_add hi₁ hi₂)]
  grw [expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar, expr_αβ_αβ2ψ_as_αβ2ψ_αβ Fchar F_sum_of_squares]
  nth_rewrite 2 [eq_of_deg_eq αβ2ψ (i₁ + 2 * i₂) (by ht)]
  nth_rewrite 4 [eq_of_deg_eq αβ2ψ (i₁ + 2 * i₂) (by ht)]
  grw [lin_of_αβ2ψ Fchar, expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar, lin_of_αβ2ψ Fchar, lin_of_αβ2ψ Fchar]
  rw [eq_of_coef_eq αβ2ψ 0 (by ring_nf; field_simp; ring_nf), id_of_αβ2ψ Fchar, mul_one]
  -- collect back into an αβψ term
  rw [←mul_one (t + u), expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi₁ hi₂]
  ring_nf; field_simp; ring_nf

theorem full_relations_implied_by_weak_relations :
  ∀ r ∈ (fullB3LargeGraded F).allRelations, (weakB3LargeGraded F).project r = 1 := by
  simp only [fullB3LargeGraded, fullB3Large]
  apply GradedPartialChevalleyGroup.graded_injection
  intro K
  rcases K
  all_goals simp only; intro p h
  · rcases h with h_old|h_new
    · tauto
    · right
      simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at h_new
      intro r h_r
      simp only [trivialSpanRelationsOfRootPair] at h_r
      rcases h_r with ⟨ i, j, hi, hj, t, u, rfl ⟩
      rcases h_new with h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h
      all_goals (
        subst p
        simp only
      )
      · exact comm_of_αβ_βψ hi hj t u
      · exact comm_of_α_αβψ hi hj t u
      · exact comm_of_β_αβψ hi hj t u
      · exact comm_of_αβ_αβψ hi hj t u
      · have := comm_of_αβψ_β2ψ Fchar hj hi u t
        rwa [triv_comm_symm] at this
      · exact comm_of_α_αβ2ψ Fchar hi hj t u
      · exact comm_of_ψ_αβ2ψ Fchar hi hj t u
      · exact comm_of_αβ_αβ2ψ Fchar F_sum_of_squares hi hj t u
      · exact comm_of_βψ_αβ2ψ Fchar hi hj t u
      · exact comm_of_β2ψ_αβ2ψ Fchar hi hj t u
      · exact comm_of_αβψ_αβ2ψ Fchar hi hj t u
      · exact comm_of_α_α2β2ψ Fchar F_sum_of_squares hi hj t u
      · exact comm_of_β_α2β2ψ Fchar hi hj t u
      · exact comm_of_ψ_α2β2ψ Fchar hi hj t u
      · exact comm_of_αβ_α2β2ψ Fchar hi hj t u
      · exact comm_of_βψ_α2β2ψ Fchar hi hj t u
      · exact comm_of_β2ψ_α2β2ψ Fchar hi hj t u
      · exact comm_of_αβψ_α2β2ψ Fchar hi hj t u
      · exact comm_of_αβ2ψ_α2β2ψ Fchar hi hj t u
  · rcases h with h_old|h_new
    · tauto
    · right
      simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at h_new
      intro r h_r
      simp only [singleSpanRelationsOfRootPair] at h_r
      rcases h_r with ⟨ i, j, hi, hj, t, u, rfl ⟩
      rcases h_new with h|h|h|h|h
      all_goals (
        subst p
        simp only [map_mul, map_inv, mul_inv_eq_one]
      )
      · have : ↑(1 : ℤ) * t * u = t * u := by ring_nf
        rw [this]
        exact (expr_αβ2ψ_as_comm_of_α_β2ψ Fchar hi hj t u).symm
      · have : ↑(-2 : ℤ) * t * u = -2 * u * t := by ring_nf
        rw [this]
        exact (expr_αβ2ψ_as_comm_of_αβψ_ψ Fchar hi hj u t).symm
      · have : ↑(-1 : ℤ) * t * u = -t * u := by ring_nf
        rw [this]
        exact (expr_α2β2ψ_as_comm_of_αβ_β2ψ Fchar hi hj t u).symm
      · have : ↑(-2 : ℤ) * t * u = -2 * t * u := by ring_nf
        rw [this]
        exact (expr_α2β2ψ_as_comm_of_αβψ_βψ Fchar hi hj t u).symm
      · have : ↑(-1 : ℤ) * t * u = -t * u := by ring_nf
        rw [this]
        exact (expr_α2β2ψ_as_comm_of_αβ2ψ_β Fchar hi hj t u).symm
  · rcases h with h_old|h_new
    · tauto
    · right
      simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at h_new
      intro r h_r
      simp only [doubleSpanRelationsOfRootPair] at h_r
      rcases h_r with ⟨ i, j, hi, hj, t, u, rfl ⟩
      rcases h_new with h|h
      all_goals (
        subst p
        simp only [map_mul, map_inv, mul_inv_eq_one]
      )
      · have : ↑(1 : ℤ) * t * u = t * u := by ring_nf
        rw [this]
        have : t * u * u = t * u^2 := by ring_nf
        rw [this]
        exact commutator_of_α_βψ_a Fchar hi hj t u
      · have : ↑(1 : ℤ) * t * u = t * u := by ring_nf
        rw [this]
        have : t * u * u = t * u^2 := by ring_nf
        rw [this]
        exact commutator_of_αβ_ψ_a Fchar hi hj t u
  · rcases h with h_old|h_new
    · tauto
    · right
      simp_all only [ne_eq, Set.mem_insert_iff, Set.mem_singleton_iff]
      intro r h_r
      simp only [mixedDegreeRelationsOfRoot] at h_r
      rcases h_r with ⟨ i, j, hi, hj, t, u, goal ⟩
      rcases h_new with h|h|h
      all_goals subst p r
      · exact comm_of_αβψ Fchar F_sum_of_squares hi hj t u
      · exact comm_of_αβ2ψ Fchar hi hj t u
      · exact comm_of_α2β2ψ Fchar hi hj t u
  · rcases h with h_old|h_new
    · tauto
    · right
      simp_all only [ne_eq, Set.mem_insert_iff, Set.mem_singleton_iff]
      intro r h_r
      simp only [linearityRelationsOfRoot] at h_r
      rcases h_r with ⟨ i, hi, t, u, goal ⟩
      rcases h_new with h|h|h
      all_goals (
        subst p r
        simp only [map_mul, map_inv, mul_inv_eq_one]
      )
      · exact lin_of_αβψ Fchar F_sum_of_squares hi t u
      · exact lin_of_αβ2ψ Fchar hi t u
      · exact lin_of_α2β2ψ Fchar hi t u
  · tauto
  · simp only [definitionRelations, Set.mem_iUnion, Set.mem_setOf_eq] at h
    rcases h with ⟨ζ, i, hi, t, h⟩
    subst p
    simp only [fullB3LargeGraded, fullMk, inv_mul_cancel, map_one]

end Steinberg.B3Large
