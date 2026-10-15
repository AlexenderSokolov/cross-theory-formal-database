/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Steinberg.B3Large.Basic
import Steinberg.B3Large.EstabAlphaBetaPsi
import Mathlib.Tactic.Linarith

namespace Steinberg.B3Large

open Steinberg B3LargePosRoot GradedPartialChevalley GradedChevalleyGenerator GradedPartialChevalleyGroup

variable {F : Type TF} [Field F] (Fchar : (2 : F) ≠ 0)

include Fchar

-- 8.131
theorem partial_A_interchange_of_αβ2ψ :
  ∀ (t u v : F),
  ⁅⸨αβψ, 0, t * u⸩, ⸨ψ, 1, v⸩⁆ = ⁅⸨α, 0, t⸩, ⸨β2ψ, 1, -2 * u * v⸩⁆ := by
  apply @sufficient_conditions_for_comm_of_αβψ_and_ψ _ _ Fchar 0 0 1 (by trivial) (by trivial) (by trivial)
  intro t u v
  have h₁ := @lift_hom_interchange_of_αβ2ψ _ _ 1 0 0 (by trivial) (by trivial) (by trivial) u (-v/2) 1
  have h := @lift_hom_interchange_of_αβ2ψ _ _ 0 1 0 (by trivial) (by trivial) (by trivial) u (-v/2) 1
  norm_num at h₁
  norm_num at h
  rw [h₁] at h
  have : -(2 * (-v / 2)) = v := by field_simp
  rw [this] at h
  have h₁ := @lift_hom_comm_of_βψ_α_β2ψ _ _ 1 0 0 (by trivial) (by trivial) (by trivial) t u v
  rwa [h] at h₁

theorem partial_A_interchange_of_αβ2ψ' :
  ∀ (t u v : F),
  ⁅⸨αβψ, 3, t * u⸩, ⸨ψ, 0, v⸩⁆ = ⁅⸨α, 1, t⸩, ⸨β2ψ, 2, -2 * u * v⸩⁆ := by
  apply @sufficient_conditions_for_comm_of_αβψ_and_ψ _ _ Fchar 1 2 0 (by trivial) (by trivial) (by trivial)
  intro t u v
  have h₁ := @lift_hom_interchange_of_αβ2ψ _ _ 0 1 1 (by trivial) (by trivial) (by trivial) u (-v/2) 1
  have h := @lift_hom_interchange_of_αβ2ψ _ _ 1 0 1 (by trivial) (by trivial) (by trivial) u (-v/2) 1
  norm_num at h₁
  norm_num at h
  rw [h₁] at h
  have : -(2 * (-v / 2)) = v := by field_simp
  rw [this] at h
  have h₁ := @lift_hom_comm_of_βψ_α_β2ψ _ _ 0 1 1 (by trivial) (by trivial) (by trivial) t u v
  rwa [h] at h₁

-- Proposition 8.132
theorem sufficient_conditions_for_comm_of_βψ_and_α_β2ψ :
  ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 2) (hj : j ≤ 1) (hk : k ≤ 3) (hyp : ∀ (t u : F), ⁅⸨αβψ, i + j, t⸩, ⸨β2ψ, k, u⸩⁆ = 1),
  ∀ (t u v : F), ⁅⸨βψ, i, t⸩, ⁅⸨α, j, u⸩, ⸨β2ψ, k, v⸩⁆⁆ = 1 := by
  intro i j k hi hj hk hyp t u v
  apply triv_comm_iff_commutes.2
  have hyp' := fun t' u' ↦ triv_comm_iff_commutes.1 (hyp t' u')
  have aux₁ : ∀ (u' : F), ⸨βψ, i, t⸩ * ⸨α, j, u'⸩ = ⸨α, j, u'⸩ * ⁅⸨α, j, -u'⸩, ⸨βψ, i, t⸩⁆ * ⸨βψ, i, t⸩ := by
    intro u'; rw [← inv_of_α]; group
  have aux₂ : ∀ (u' : F), ⸨βψ, i, t⸩ * ⸨α, j, u'⸩ = ⁅⸨α, j, u'⸩, ⸨βψ, i, t⸩⁆⁻¹ * ⸨α, j, u'⸩ * ⸨βψ, i, t⸩ := by
    intro u'; group
  grw [commutatorElement_def, ←inv_of_α, ←inv_of_β2ψ, aux₁ u, expr_βψ_β2ψ_as_β2ψ_βψ hi hk, aux₂ (-u), expr_βψ_β2ψ_as_β2ψ_βψ hi hk]
  suffices h : ⁅⸨α, j, -u⸩, ⸨βψ, i, t⸩⁆ * ⸨β2ψ, k, v⸩ * ⁅⸨α, j, -u⸩, ⸨βψ, i, t⸩⁆⁻¹ = ⸨β2ψ, k, v⸩ by
    have : ⁅⸨βψ, i, t⸩, ⸨α, j, -u⸩⁆ = ⁅⸨α, j, -u⸩, ⸨βψ, i, t⸩⁆⁻¹ := by rw [←inv_of_α]; group
    rw [this]; exact h
  apply mul_inv_eq_iff_eq_mul.2
  have := (generic_comm_of_α_βψ Fchar hj hi (-u) t).1
  field_simp at this
  have := calc
    ⁅⸨α, j, -u⸩, ⸨βψ, i, t⸩⁆ = ⸨αβψ, j + i, -(u * t)⸩ * ⁅⸨αβψ, j + i, u * t⸩, ⸨βψ, i, t / 2⸩⁆ := this
    _ = ⸨αβψ, i + j, -t * u⸩ * ⁅⸨αβψ, i + j, t * u⸩, ⸨βψ, i, t / 2⸩⁆ := by group
  grw [this, commutatorElement_def, expr_βψ_β2ψ_as_β2ψ_βψ hi hk, inv_of_αβψ, ←hyp', ←hyp']
  rw [mul_assoc, hyp']
  grw [expr_βψ_β2ψ_as_β2ψ_βψ]

-- 8.133
theorem partial_comm_of_βψ_α_β2ψ :
  ∀ (t u v : F),
  ⁅⸨βψ, 2, t⸩, ⁅⸨α, 0, u⸩, ⸨β2ψ, 2, v⸩⁆⁆ = 1 := by
  apply @sufficient_conditions_for_comm_of_βψ_and_α_β2ψ _ _ Fchar 2 0 2 (by trivial) (by trivial) Nat.AtLeastTwo.prop
  intro t u
  have := triv_comm_iff_commutes.mp (@lift_hom_comm_of_β2ψ_αβψ _ _ 1 0 1 (by trivial) (by trivial) (by trivial) u t)
  apply triv_comm_iff_commutes.mpr
  rw [←this]

-- 8.134
theorem partial_B_interchange_of_αβ2ψ :
  ∀ (t u v : F),
  ⁅⸨αβψ, 2, t * u⸩, ⸨ψ, 0, v⸩⁆ = ⁅⸨α, 0, t⸩, ⸨β2ψ, 2, -2 * u * v⸩⁆ :=
  @sufficient_conditions_for_comm_of_αβψ_and_ψ _ _ Fchar 0 2 0 (by trivial) (by ht) (by trivial) (@partial_comm_of_βψ_α_β2ψ _ _ Fchar)

/- ### Establishing α + β + 2ψ -/

private lemma interchange_of_αβ2ψ_trans_α_β2ψ : forall_ijk_tu α β ψ,
    ⁅⸨α, i, t * u⸩, ⸨β2ψ, j + 2 * k, 1⸩⁆ = ⁅⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u⸩⁆ := by
  intro i j k hi hj hk t u
  have aux₁ := lift_hom_interchange_of_αβ2ψ hi hj hk (t * u) 1 (-1/2)
  have aux₂ := lift_hom_interchange_of_αβ2ψ hi hj hk t u (-1/2)
  field_simp at aux₁
  field_simp at aux₂
  rwa [aux₁] at aux₂

omit Fchar
private lemma interchange_of_αβ2ψ_refl_u : forall_ijk_tu α β ψ,
    ⁅⸨αβψ, i + j + k, t⸩, ⸨ψ, k, u⸩⁆ = ⁅⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, -2 * u⸩⁆ := by
  intro i j k hi hj hk t u
  rw [← mul_one t]
  grw [lift_hom_interchange_of_αβ2ψ hi hj hk]

private lemma interchange_of_αβ2ψ_refl_v : forall_ijk_tu α β ψ,
    ⁅⸨αβψ, i + j + k, t * u⸩, ⸨ψ, k, 1⸩⁆ = ⁅⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, -2 * u⸩⁆ := by
  intro i j k hi hj hk t u
  grw [lift_hom_interchange_of_αβ2ψ hi hj hk]

private lemma interchange_of_αβ2ψ_trans_αβψ_ψ : forall_ijk_tu α β ψ,
    ⁅⸨αβψ, i + j + k, t * u⸩, ⸨ψ, k, 1⸩⁆ = ⁅⸨αβψ, i + j + k, t⸩, ⸨ψ, k, u⸩⁆ := by
  intro i j k hi hj hk t u
  rw [interchange_of_αβ2ψ_refl_v hi hj hk, interchange_of_αβ2ψ_refl_u hi hj hk]

include Fchar
private lemma interchange_A_of_αβ2ψ_refl_u :
  ∀ t u : F, ⁅⸨αβψ, 0, t⸩, ⸨ψ, 1, u⸩⁆ = ⁅⸨α, 0, t⸩, ⸨β2ψ, 1, -2 * u⸩⁆ := by
  intro t u
  rw [←mul_one t, partial_A_interchange_of_αβ2ψ Fchar]
  simp only [mul_one, neg_mul]

private lemma interchange_A_of_αβ2ψ_refl_u' :
  ∀ t u : F, ⁅⸨αβψ, 3, t⸩, ⸨ψ, 0, u⸩⁆ = ⁅⸨α, 1, t⸩, ⸨β2ψ, 2, -2 * u⸩⁆ := by
  intro t u
  rw [←mul_one t, partial_A_interchange_of_αβ2ψ' Fchar]
  simp only [mul_one, neg_mul]

private lemma interchange_A_of_αβ2ψ_refl_v :
  ∀ t u : F, ⁅⸨αβψ, 0, t * u⸩, ⸨ψ, 1, 1⸩⁆ = ⁅⸨α, 0, t⸩, ⸨β2ψ, 1, -2 * u⸩⁆ := by
  intro t u
  rw [partial_A_interchange_of_αβ2ψ Fchar]
  simp only [neg_mul, mul_one]

private lemma interchange_A_of_αβ2ψ_refl_v' :
  ∀ t u : F, ⁅⸨αβψ, 3, t * u⸩, ⸨ψ, 0, 1⸩⁆ = ⁅⸨α, 1, t⸩, ⸨β2ψ, 2, -2 * u⸩⁆ := by
  intro t u
  rw [partial_A_interchange_of_αβ2ψ' Fchar]
  simp only [neg_mul, mul_one]

private lemma interchange_A_of_αβ2ψ_trans_αβψ_ψ :
  ∀ t u : F, ⁅⸨αβψ, 0, t * u⸩, ⸨ψ, 1, 1⸩⁆ = ⁅⸨αβψ, 0, t⸩, ⸨ψ, 1, u⸩⁆ := by
  intro t u
  rw [interchange_A_of_αβ2ψ_refl_v Fchar, interchange_A_of_αβ2ψ_refl_u Fchar]

private lemma interchange_A_of_αβ2ψ_trans_αβψ_ψ' :
  ∀ t u : F, ⁅⸨αβψ, 3, t * u⸩, ⸨ψ, 0, 1⸩⁆ = ⁅⸨αβψ, 3, t⸩, ⸨ψ, 0, u⸩⁆ := by
  intro t u
  rw [interchange_A_of_αβ2ψ_refl_v' Fchar, interchange_A_of_αβ2ψ_refl_u' Fchar]

private lemma interchange_B_of_αβ2ψ_refl_u :
  ∀ t u : F, ⁅⸨αβψ, 2, t⸩, ⸨ψ, 0, u⸩⁆ = ⁅⸨α, 0, t⸩, ⸨β2ψ, 2, -2 * u⸩⁆ := by
  intro t u
  rw [←mul_one t, partial_B_interchange_of_αβ2ψ Fchar]
  simp only [mul_one, neg_mul]

private lemma interchange_B_of_αβ2ψ_refl_v :
  ∀ t u : F, ⁅⸨αβψ, 2, t * u⸩, ⸨ψ, 0, 1⸩⁆ = ⁅⸨α, 0, t⸩, ⸨β2ψ, 2, -2 * u⸩⁆ := by
  intro t u
  rw [partial_B_interchange_of_αβ2ψ Fchar]
  simp only [neg_mul, mul_one]

private lemma interchange_B_of_αβ2ψ_trans_αβψ_ψ :
  ∀ t u : F, ⁅⸨αβψ, 2, t * u⸩, ⸨ψ, 0, 1⸩⁆ = ⁅⸨αβψ, 2, t⸩, ⸨ψ, 0, u⸩⁆ := by
  intro t u
  rw [interchange_B_of_αβ2ψ_refl_v Fchar, interchange_B_of_αβ2ψ_refl_u Fchar]

-- height 0
private lemma expr_αβ2ψ_as_comm_of_α_β2ψ_00 :
  ∀ t u : F, ⸨αβ2ψ, 0, t * u⸩ = ⁅⸨α, 0, t⸩, ⸨β2ψ, 0, u⸩⁆ := by
  intro t u
  have := @def_of_αβ2ψ _ _ 0 (by trivial) (t * u)
  unfold split_4_into_1_3 at this
  rw [←this, @interchange_of_αβ2ψ_trans_α_β2ψ _ _ Fchar 0 0 0 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβ2ψ_as_comm_of_αβψ_ψ_00 :
  ∀ t u : F, ⸨αβ2ψ, 0, -2 * t * u⸩ = ⁅⸨αβψ, 0, u⸩, ⸨ψ, 0, t⸩⁆ := by
  intro t u
  have : -2 * t * u = t * (-2 * u) := by group
  rw [this, expr_αβ2ψ_as_comm_of_α_β2ψ_00 Fchar, ←@interchange_of_αβ2ψ_refl_v _ _ 0 0 0 (by trivial) (by trivial) (by trivial),
  mul_comm t u, interchange_of_αβ2ψ_trans_αβψ_ψ (by trivial) (by trivial) (by trivial)]

-- height 1
private lemma expr_αβ2ψ_as_comm_of_α_β2ψ_01 :
  ∀ t u : F, ⸨αβ2ψ, 1, t * u⸩ = ⁅⸨α, 0, t⸩, ⸨β2ψ, 1, u⸩⁆ := by
  intro t u
  have := @def_of_αβ2ψ _ _ 1 (by trivial) (t * u)
  unfold split_4_into_1_3 at this
  rw [←this, @interchange_of_αβ2ψ_trans_α_β2ψ _ _ Fchar 0 1 0 (by trivial) (by trivial) (by trivial)]

-- `A` edge
private lemma expr_αβ2ψ_as_comm_of_αβψ_ψ_01 :
  ∀ t u : F, ⸨αβ2ψ, 1, -2 * t * u⸩ = ⁅⸨αβψ, 0, u⸩, ⸨ψ, 1, t⸩⁆ := by
  intro t u
  have : -2 * t * u = t * (-2 * u) := by group
  rw [this, expr_αβ2ψ_as_comm_of_α_β2ψ_01 Fchar, ←interchange_A_of_αβ2ψ_refl_v Fchar,
  mul_comm t u, interchange_A_of_αβ2ψ_trans_αβψ_ψ Fchar]

private lemma expr_αβ2ψ_as_comm_of_αβψ_ψ_10 :
  ∀ t u : F, ⸨αβ2ψ, 1, -2 * t * u⸩ = ⁅⸨αβψ, 1, u⸩, ⸨ψ, 0, t⸩⁆ := by
  intro t u
  have : -2 * t * u = t * (-2 * u) := by group
  rw [this, expr_αβ2ψ_as_comm_of_α_β2ψ_01 Fchar, ←@interchange_of_αβ2ψ_refl_v _ _ 0 1 0 (by trivial) (by trivial) (by trivial),
  mul_comm t u, @interchange_of_αβ2ψ_trans_αβψ_ψ _ _ 0 1 0 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβ2ψ_as_comm_of_α_β2ψ_10 :
  ∀ t u : F, ⸨αβ2ψ, 1, t * u⸩ = ⁅⸨α, 1, t⸩, ⸨β2ψ, 0, u⸩⁆ := by
  intro t u
  have : t * u = -2 * (-u / 2) * t := by ring_nf; field_simp
  rw [this, expr_αβ2ψ_as_comm_of_αβψ_ψ_10 Fchar, @interchange_of_αβ2ψ_refl_u _ _ 1 0 0 (by trivial) (by trivial) (by trivial)]
  field_simp

-- height 2
private lemma expr_αβ2ψ_as_comm_of_α_β2ψ_11 :
  ∀ t u : F, ⸨αβ2ψ, 2, t * u⸩ = ⁅⸨α, 1, t⸩, ⸨β2ψ, 1, u⸩⁆ := by
  intro t u
  have := @def_of_αβ2ψ _ _ 2 (by trivial) (t * u)
  unfold split_4_into_1_3 at this
  rw [←this, @interchange_of_αβ2ψ_trans_α_β2ψ _ _ Fchar 1 1 0 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβ2ψ_as_comm_of_αβψ_ψ_20 :
  ∀ t u : F, ⸨αβ2ψ, 2, -2 * t * u⸩ = ⁅⸨αβψ, 2, u⸩, ⸨ψ, 0, t⸩⁆ := by
  intro t u
  have : -2 * t * u = t * (-2 * u) := by group
  rw [this, expr_αβ2ψ_as_comm_of_α_β2ψ_11 Fchar, ←@interchange_of_αβ2ψ_refl_v _ _ 1 1 0 (by trivial) (by trivial) (by trivial),
  mul_comm t u, @interchange_of_αβ2ψ_trans_αβψ_ψ _ _ 1 1 0 (by trivial) (by trivial) (by trivial)]

-- `B` edge
private lemma expr_αβ2ψ_as_comm_of_α_β2ψ_02 :
  ∀ t u : F, ⸨αβ2ψ, 2, t * u⸩ = ⁅⸨α, 0, t⸩, ⸨β2ψ, 2, u⸩⁆ := by
  intro t u
  have : t * u = -2 * (-u / 2) * t := by ring_nf; field_simp
  rw [this, expr_αβ2ψ_as_comm_of_αβψ_ψ_20 Fchar, interchange_B_of_αβ2ψ_refl_u Fchar]
  field_simp

private lemma expr_αβ2ψ_as_comm_of_αβψ_ψ_11 :
  ∀ t u : F, ⸨αβ2ψ, 2, -2 * t * u⸩ = ⁅⸨αβψ, 1, u⸩, ⸨ψ, 1, t⸩⁆ := by
  intro t u
  have : -2 * t * u = t * (-2 * u) := by group
  rw [this, expr_αβ2ψ_as_comm_of_α_β2ψ_02 Fchar, ←@interchange_of_αβ2ψ_refl_v _ _ 0 0 1 (by trivial) (by trivial) (by trivial),
  mul_comm t u, interchange_of_αβ2ψ_trans_αβψ_ψ (by trivial) (by trivial) (by trivial)]

-- height 3
private lemma expr_αβ2ψ_as_comm_of_α_β2ψ_12 :
  ∀ t u : F, ⸨αβ2ψ, 3, t * u⸩ = ⁅⸨α, 1, t⸩, ⸨β2ψ, 2, u⸩⁆ := by
  intro t u
  have := @def_of_αβ2ψ _ _ 3 (by trivial) (t * u)
  unfold split_4_into_1_3 at this
  rw [←this, @interchange_of_αβ2ψ_trans_α_β2ψ _ _ Fchar 1 0 1 (by trivial) (by trivial) (by trivial)]

-- `A` edge
private lemma expr_αβ2ψ_as_comm_of_αβψ_ψ_30 :
  ∀ t u : F, ⸨αβ2ψ, 3, -2 * t * u⸩ = ⁅⸨αβψ, 3, u⸩, ⸨ψ, 0, t⸩⁆ := by
  intro t u
  have : -2 * t * u = t * (-2 * u) := by group
  rw [this, expr_αβ2ψ_as_comm_of_α_β2ψ_12 Fchar, ←interchange_A_of_αβ2ψ_refl_v' Fchar,
  mul_comm t u, interchange_A_of_αβ2ψ_trans_αβψ_ψ' Fchar]

private lemma expr_αβ2ψ_as_comm_of_αβψ_ψ_21 :
  ∀ t u : F, ⸨αβ2ψ, 3, -2 * t * u⸩ = ⁅⸨αβψ, 2, u⸩, ⸨ψ, 1, t⸩⁆ := by
  intro t u
  have : -2 * t * u = u * (-2 * t) := by group
  rw [this, expr_αβ2ψ_as_comm_of_α_β2ψ_12 Fchar, ←@interchange_of_αβ2ψ_refl_v _ _ 1 0 1 (by trivial) (by trivial) (by trivial),
  @interchange_of_αβ2ψ_trans_αβψ_ψ _ _ 1 0 1 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβ2ψ_as_comm_of_α_β2ψ_03 :
  ∀ t u : F, ⸨αβ2ψ, 3, t * u⸩ = ⁅⸨α, 0, t⸩, ⸨β2ψ, 3, u⸩⁆ := by
  intro t u
  have : t * u = -2 * (-u / 2) * t := by ring_nf; field_simp
  rw [this, expr_αβ2ψ_as_comm_of_αβψ_ψ_21 Fchar, @interchange_of_αβ2ψ_refl_u _ _ 0 1 1 (by trivial) (by trivial) (by trivial)]
  field_simp

-- height 4
private lemma expr_αβ2ψ_as_comm_of_α_β2ψ_13 :
  ∀ t u : F, ⸨αβ2ψ, 4, t * u⸩ = ⁅⸨α, 1, t⸩, ⸨β2ψ, 3, u⸩⁆ := by
  intro t u
  have := @def_of_αβ2ψ _ _ 4 (by trivial) (t * u)
  unfold split_4_into_1_3 at this
  rw [←this, @interchange_of_αβ2ψ_trans_α_β2ψ _ _ Fchar 1 1 1 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβ2ψ_as_comm_of_αβψ_ψ_31 :
  ∀ t u : F, ⸨αβ2ψ, 4, -2 * t * u⸩ = ⁅⸨αβψ, 3, u⸩, ⸨ψ, 1, t⸩⁆ := by
  intro t u
  have : -2 * t * u = u * (-2 * t) := by group
  rw [this, expr_αβ2ψ_as_comm_of_α_β2ψ_13 Fchar, ←@interchange_of_αβ2ψ_refl_v _ _ 1 1 1 (by trivial) (by trivial) (by trivial),
  @interchange_of_αβ2ψ_trans_αβψ_ψ _ _ 1 1 1 (by trivial) (by trivial) (by trivial)]

-- 8.135a
theorem expr_αβ2ψ_as_comm_of_α_β2ψ :
  forall_ij_tu 1 3,
    ⸨αβ2ψ, i + j, t * u⸩ = ⁅⸨α, i, t⸩, ⸨β2ψ, j, u⸩⁆ := by
  intro i j hi hj t u
  match i, j with
  | 0, 0 => rw [expr_αβ2ψ_as_comm_of_α_β2ψ_00 Fchar]
  | 0, 1 => rw [expr_αβ2ψ_as_comm_of_α_β2ψ_01 Fchar]
  | 1, 0 => rw [expr_αβ2ψ_as_comm_of_α_β2ψ_10 Fchar]
  | 0, 2 => rw [expr_αβ2ψ_as_comm_of_α_β2ψ_02 Fchar]
  | 1, 1 => rw [expr_αβ2ψ_as_comm_of_α_β2ψ_11 Fchar]
  | 0, 3 => rw [expr_αβ2ψ_as_comm_of_α_β2ψ_03 Fchar]
  | 1, 2 => rw [expr_αβ2ψ_as_comm_of_α_β2ψ_12 Fchar]
  | 1, 3 => rw [expr_αβ2ψ_as_comm_of_α_β2ψ_13 Fchar]

-- 8.135b
theorem expr_αβ2ψ_as_comm_of_αβψ_ψ :
  forall_ij_tu 3 1,
    ⸨αβ2ψ, i + j, -2 * t * u⸩ = ⁅⸨αβψ, i, u⸩, ⸨ψ, j, t⸩⁆ := by
  intro i j hi hj t u
  match i, j with
  | 0, 0 => rw [expr_αβ2ψ_as_comm_of_αβψ_ψ_00 Fchar]
  | 1, 0 => rw [expr_αβ2ψ_as_comm_of_αβψ_ψ_10 Fchar]
  | 0, 1 => rw [expr_αβ2ψ_as_comm_of_αβψ_ψ_01 Fchar]
  | 1, 1 => rw [expr_αβ2ψ_as_comm_of_αβψ_ψ_11 Fchar]
  | 2, 0 => rw [expr_αβ2ψ_as_comm_of_αβψ_ψ_20 Fchar]
  | 2, 1 => rw [expr_αβ2ψ_as_comm_of_αβψ_ψ_21 Fchar]
  | 3, 0 => rw [expr_αβ2ψ_as_comm_of_αβψ_ψ_30 Fchar]
  | 3, 1 => rw [expr_αβ2ψ_as_comm_of_αβψ_ψ_31 Fchar]

-- 8.136
theorem comm_of_α_αβ2ψ :
  trivialSpanPropOfRootPair (weakB3LargeGraded F).project ⟨α, αβ2ψ⟩ := by
  intro i j hi hj t u
  rcases decompose 3 1 j hj with ⟨ j₁, j₂, ⟨ rfl, hj₁, hj₂ ⟩ ⟩
  have expr_αβ2ψ := @expr_αβ2ψ_as_comm_of_αβψ_ψ _ _ Fchar j₁ j₂ hj₁ hj₂ (-1/2) u
  field_simp at expr_αβ2ψ
  have := @comm_of_α_αβψ_ψ _ _ i j₁ j₂ hi hj₁ hj₂ t u (-1/2)
  rwa [←expr_αβ2ψ] at this
declare_B3Large_trivial_span_expr_thm F α αβ2ψ

-- 8.137
theorem comm_of_ψ_αβ2ψ :
  trivialSpanPropOfRootPair (weakB3LargeGraded F).project ⟨ψ, αβ2ψ⟩ := by
  intro i j hi hj t u
  rcases decompose 3 1 j hj with ⟨ j₂, j₁, ⟨ rfl, hj₂, hj₁ ⟩ ⟩
  have expr_αβ2ψ := @expr_αβ2ψ_as_comm_of_α_β2ψ _ _ Fchar j₁ j₂ hj₁ hj₂ 1 u
  have := @comm_of_ψ_α_β2ψ _ _ i j₁ j₂ hi hj₁ hj₂ t 1 u
  rw [←expr_αβ2ψ] at this
  rw [←this]
  group
declare_B3Large_trivial_span_expr_thm F ψ αβ2ψ

-- 8.138a
@[simp, chev_simps]
private lemma inv_doub_of_αβ2ψ_a :
  forall_i_t αβ2ψ,
    ⸨αβ2ψ, i, t⸩ * ⸨αβ2ψ, i, -t⸩ = 1 := by
  intro i hi t
  rcases decompose 3 1 i hi with ⟨ i₂, i₁, ⟨ rfl, hi₂, hi₁ ⟩ ⟩
  have := @expr_αβ2ψ_as_comm_of_α_β2ψ _ _ Fchar i₁ i₂ hi₁ hi₂
  calc
    ⸨αβ2ψ, i₂ + i₁, t⸩ * ⸨αβ2ψ, i₂ + i₁, -t⸩ = ⸨αβ2ψ, i₁ + i₂, t * 1⸩ * ⸨αβ2ψ, i₁ + i₂, t * (-1)⸩ := by group
    _ = ⁅⸨α, i₁, t⸩, ⸨β2ψ, i₂, 1⸩⁆ * ⁅⸨α, i₁, t⸩, ⸨β2ψ, i₂, -1⸩⁆ := by rw [this t 1, this t (-1)]
    _ = 1 := by rw [lift_hom_inv_doub_of_α_β2ψ_b hi₁ hi₂]

@[simp, chev_simps]
theorem inv_of_αβ2ψ :
  forall_i_t αβ2ψ,
    ⸨αβ2ψ, i, t⸩⁻¹ = ⸨αβ2ψ, i, -t⸩ := by
  intro i hi t
  have := @inv_doub_of_αβ2ψ_a _ _ Fchar i hi t
  rw [eq_inv_of_mul_eq_one_left this, inv_inv]

-- 8.138b
theorem doub_of_αβ2ψ :
  forall_i_t αβ2ψ.height,
    ⸨αβ2ψ, i, t⸩ * ⸨αβ2ψ, i, t⸩ = ⸨αβ2ψ, i, 2 * t⸩ := by
  intro i hi t
  rcases decompose 3 1 i hi with ⟨ i₂, i₁, ⟨ rfl, hi₂, hi₁ ⟩ ⟩
  have := @expr_αβ2ψ_as_comm_of_α_β2ψ _ _ Fchar i₁ i₂ hi₁ hi₂
  calc
    ⸨αβ2ψ, i₂ + i₁, t⸩ * ⸨αβ2ψ, i₂ + i₁, t⸩ = ⸨αβ2ψ, i₁ + i₂, 1 * t⸩ * ⸨αβ2ψ, i₁ + i₂, 1 * t⸩ := by group
    _ = ⁅⸨α, i₁, (1 : F)⸩, ⸨β2ψ, i₂, t⸩⁆ * ⁅⸨α, i₁, (1 : F)⸩, ⸨β2ψ, i₂, t⸩⁆ := by rw [this]
    _ = ⁅⸨α, i₁, (1 : F)⸩, ⸨β2ψ, i₂, 2 * t⸩⁆ := by rw [lift_hom_inv_doub_of_α_β2ψ_c hi₁ hi₂]
    _ = ⸨αβ2ψ, i₂ + i₁, 2 * t⸩ := by rw [←this]; group

-- 8.139a
theorem commutator_of_αβ_ψ_a :
  forall_ij_tu 2 1,
    ⁅⸨αβ, i, t⸩, ⸨ψ, j, u⸩⁆ = ⸨αβψ, i + j, t * u⸩ * ⸨αβ2ψ, i + 2 * j, t * u^2⸩ := by
  intro i j hi hj t u
  have aux := expr_αβ2ψ_as_comm_of_αβψ_ψ Fchar (add_le_add hi hj) hj (u / 2) (-t * u)
  have : ⸨αβ2ψ, i + j + j, -2 * (u / 2) * (-t * u)⸩ = ⸨αβ2ψ, i + 2 * j, t * u^2⸩ := by ring_nf; field_simp
  rw [this] at aux
  rw [(generic_comm_of_αβ_ψ Fchar hi hj t u).1, aux]

-- 8.139b
theorem commutator_of_αβ_ψ_b :
  forall_ij_tu 2 1,
    ⁅⸨αβ, i, t⸩, ⸨ψ, j, u⸩⁆ = ⸨αβ2ψ, i + 2 * j, t * u^2⸩ * ⸨αβψ, i + j, t * u⸩ := by
  intro i j hi hj t u
  have aux := expr_αβ2ψ_as_comm_of_αβψ_ψ Fchar (add_le_add hi hj) hj (u / 2) (t * u)
  rw [(generic_comm_of_αβ_ψ Fchar hi hj t u).2, ←aux, inv_of_αβ2ψ Fchar (by ht)]
  ring_nf; field_simp

-- 8.140a
theorem expr_αβ2ψ_as_α_β2ψ_α_β2ψ :
  forall_ij_tu α β2ψ,
    ⸨αβ2ψ, i + j, t * u⸩ = ⸨α, i, t⸩ * ⸨β2ψ, j, u⸩ * ⸨α, i, -t⸩ * ⸨β2ψ, j, -u⸩ := by
  intro i j hi hj t u
  rw [expr_αβ2ψ_as_comm_of_α_β2ψ Fchar hi hj, ← inv_of_α, ← inv_of_β2ψ, commutatorElement_def]

-- 8.140b
theorem expr_αβ2ψ_as_β2ψ_α_β2ψ_α :
  forall_ij_tu α β2ψ,
    ⸨αβ2ψ, i + j, t * u⸩ = ⸨β2ψ, j, -u⸩ * ⸨α, i, t⸩ * ⸨β2ψ, j, u⸩ * ⸨α, i, -t⸩ := by
  intro i j hi hj t u
  calc
    ⸨αβ2ψ, i + j, t * u⸩ = ⸨αβ2ψ, i + j, t * (-u)⸩⁻¹ := by rw [inv_of_αβ2ψ Fchar (add_le_add hi hj)]; group
    _ = ⁅⸨α, i, t⸩, ⸨β2ψ, j, -u⸩⁆⁻¹ := by rw [expr_αβ2ψ_as_comm_of_α_β2ψ Fchar hi hj]
    _ = ⁅⸨α, i, t⸩, ⸨β2ψ, j, u⸩⁻¹⁆⁻¹ := by rw [inv_of_β2ψ]
    _ = ⸨β2ψ, j, -u⸩ * ⸨α, i, t⸩ * ⸨β2ψ, j, u⸩ * ⸨α, i, -t⸩ := by rw [← inv_of_β2ψ, ← inv_of_α]; group

-- 8.141a
theorem expr_αβ2ψ_as_αβψ_ψ_αβψ_ψ :
  forall_ij_tu αβψ ψ,
    ⸨αβ2ψ, i + j, -2 * t * u⸩ = ⸨αβψ, i, u⸩ * ⸨ψ, j, t⸩ * ⸨αβψ, i, -u⸩ * ⸨ψ, j, -t⸩ := by
  intro i j hi hj t u
  rw [expr_αβ2ψ_as_comm_of_αβψ_ψ Fchar hi hj, ← inv_of_αβψ hi, ← inv_of_ψ hj, commutatorElement_def];

-- 8.141b
theorem expr_αβ2ψ_as_ψ_αβψ_ψ_αβψ :
  forall_ij_tu αβψ ψ,
    ⸨αβ2ψ, i + j, -2 * t * u⸩ = ⸨ψ, j, -t⸩ * ⸨αβψ, i, u⸩ * ⸨ψ, j, t⸩ * ⸨αβψ, i, -u⸩ := by
  intro i j hi hj t u
  calc
    ⸨αβ2ψ, i + j, -2 * t * u⸩ = ⸨αβ2ψ, i + j, -2 * (-t) * u⸩⁻¹ := by rw [inv_of_αβ2ψ Fchar (add_le_add hi hj)]; group
    _ = ⁅⸨αβψ, i, u⸩, ⸨ψ, j, -t⸩⁆⁻¹ := by rw [expr_αβ2ψ_as_comm_of_αβψ_ψ Fchar hi hj]
    _ = ⁅⸨αβψ, i, u⸩, ⸨ψ, j, t⸩⁻¹⁆⁻¹ := by rw [inv_of_ψ]
    _ = ⸨ψ, j, -t⸩ * ⸨αβψ, i, u⸩ * ⸨ψ, j, t⸩ * ⸨αβψ, i, -u⸩ := by rw [← inv_of_ψ hj, ← inv_of_αβψ hi]; group

-- 8.142a
@[group_reassoc]
theorem expr_α_β2ψ_as_αβ2ψ_β2ψ_α :
  forall_ij_tu α β2ψ,
    ⸨α, i, t⸩ * ⸨β2ψ, j, u⸩ = ⸨αβ2ψ, i + j, t * u⸩ * ⸨β2ψ, j, u⸩ * ⸨α, i, t⸩ := by
  intro i j hi hj t u
  rw [expr_αβ2ψ_as_comm_of_α_β2ψ Fchar hi hj]
  group

-- 8.142b
@[group_reassoc]
theorem expr_α_β2ψ_as_β2ψ_αβ2ψ_α :
  forall_ij_tu α β2ψ,
    ⸨α, i, t⸩ * ⸨β2ψ, j, u⸩ = ⸨β2ψ, j, u⸩ * ⸨αβ2ψ, i + j, t * u⸩ * ⸨α, i, t⸩ := by
  intro i j hi hj t u
  have := calc
    ⸨αβ2ψ, i + j, t * u⸩ = ⸨αβ2ψ, i + j, t * (-u)⸩⁻¹ := by rw [inv_of_αβ2ψ Fchar (add_le_add hi hj)]; group
    _ = ⁅⸨α, i, t⸩, ⸨β2ψ, j, -u⸩⁆⁻¹ := by rw [expr_αβ2ψ_as_comm_of_α_β2ψ Fchar hi hj]
    _ = ⁅⸨α, i, t⸩, ⸨β2ψ, j, u⸩⁻¹⁆⁻¹ := by rw [inv_of_β2ψ]
  rw [this]
  group

-- 8.142c
@[group_reassoc]
theorem expr_α_β2ψ_as_β2ψ_α_αβ2ψ :
  forall_ij_tu α β2ψ,
    ⸨α, i, t⸩ * ⸨β2ψ, j, u⸩ = ⸨β2ψ, j, u⸩ * ⸨α, i, t⸩ * ⸨αβ2ψ, i + j, t * u⸩ := by
  intro i j hi hj t u
  have := calc
    ⸨αβ2ψ, i + j, t * u⸩ = ⸨αβ2ψ, i + j, (-t) * (-u)⸩ := by group
    _ = ⁅⸨α, i, -t⸩, ⸨β2ψ, j, -u⸩⁆ := by rw [expr_αβ2ψ_as_comm_of_α_β2ψ Fchar hi hj]
    _ = ⁅⸨α, i, t⸩⁻¹, ⸨β2ψ, j, u⸩⁻¹⁆ := by rw [inv_of_β2ψ, inv_of_α]
  rw [this]
  group

-- 8.143a
@[group_reassoc]
theorem expr_ψ_αβψ_as_αβψ_αβ2ψ_ψ :
  forall_ij_tu ψ αβψ,
    ⸨ψ, i, t⸩ * ⸨αβψ, j, u⸩ = ⸨αβψ, j, u⸩ * ⸨αβ2ψ, i + j, 2 * t * u⸩ * ⸨ψ, i, t⸩ := by
  intro i j hi hj t u
  have := calc
    ⸨αβ2ψ, i + j, 2 * t * u⸩ = ⸨αβ2ψ, j + i, -2 * t * (-u)⸩ := by group
    _ = ⁅⸨αβψ, j, u⸩⁻¹, ⸨ψ, i, t⸩⁆ := by rw [expr_αβ2ψ_as_comm_of_αβψ_ψ Fchar hj hi, inv_of_αβψ hj]
  rw [this]
  group

-- 8.143b
@[group_reassoc]
theorem expr_ψ_αβψ_as_αβψ_ψ_αβ2ψ :
  forall_ij_tu ψ αβψ,
    ⸨ψ, i, t⸩ * ⸨αβψ, j, u⸩ = ⸨αβψ, j, u⸩ * ⸨ψ, i, t⸩ * ⸨αβ2ψ, i + j, 2 * t * u⸩ := by
  intro i j hi hj t u
  have := calc
    ⸨αβ2ψ, i + j, 2 * t * u⸩ = ⸨αβ2ψ, j + i, -2 * (-t) * (-u)⸩⁻¹ := by rw [inv_of_αβ2ψ Fchar (by ht)]; group
    _ = ⁅⸨αβψ, j, u⸩⁻¹, ⸨ψ, i, t⸩⁻¹⁆⁻¹ := by rw [expr_αβ2ψ_as_comm_of_αβψ_ψ Fchar hj hi, inv_of_αβψ hj, inv_of_ψ]
  rw [this]
  group

-- 8.144a
@[group_reassoc]
theorem expr_αβψ_ψ_as_αβ2ψ_ψ_αβψ :
  forall_ij_tu ψ αβψ,
    ⸨αβψ, j, u⸩ * ⸨ψ, i, t⸩ = ⸨αβ2ψ, i + j, -2 * t * u⸩ * ⸨ψ, i, t⸩ * ⸨αβψ, j, u⸩ := by
  intro i j hi hj t u
  have := calc
    ⸨αβ2ψ, i + j, -2 * t * u⸩ = ⸨αβ2ψ, j + i, -2 * t * u⸩ := by group
    _ = ⁅⸨αβψ, j, u⸩, ⸨ψ, i, t⸩⁆ := by rw [expr_αβ2ψ_as_comm_of_αβψ_ψ Fchar hj hi]
  rw [this]
  group

-- 8.144b
@[group_reassoc]
theorem expr_αβψ_ψ_as_ψ_αβ2ψ_αβψ :
  forall_ij_tu ψ αβψ,
    ⸨αβψ, j, u⸩ * ⸨ψ, i, t⸩ = ⸨ψ, i, t⸩ * ⸨αβ2ψ, i + j, -2 * t * u⸩ * ⸨αβψ, j, u⸩ := by
  intro i j hi hj t u
  have := calc
    ⸨αβ2ψ, i + j, -2 * t * u⸩ = ⸨αβ2ψ, j + i, -2 * (-t) * u⸩⁻¹ := by rw [inv_of_αβ2ψ Fchar (by ht)]; group
    _ = ⁅⸨αβψ, j, u⸩, ⸨ψ, i, t⸩⁻¹⁆⁻¹ := by rw [expr_αβ2ψ_as_comm_of_αβψ_ψ Fchar hj hi, inv_of_ψ]
  rw [this]
  group

-- 8.145a
@[group_reassoc]
theorem expr_αβ_ψ_as_ψ_αβ_αβψ_αβ2ψ :
  forall_ij_tu 2 1,
    ⸨αβ, i, t⸩ * ⸨ψ, j, u⸩ = ⸨ψ, j, u⸩ * ⸨αβ, i, t⸩ * ⸨αβψ, i + j, t * u⸩ * ⸨αβ2ψ, i + 2 * j, -t * u^2⸩ := by
  intro i j hi hj t u
  have aux := calc
    ⸨αβψ, i + j, t * u⸩ * ⸨αβ2ψ, i + 2 * j, -t * u^2⸩ = ⸨αβψ, i + j, (-t) * (-u)⸩ * ⸨αβ2ψ, i + 2 * j, -t * (-u)^2⸩ := by ring_nf
    _ = ⁅⸨αβ, i, -t⸩, ⸨ψ, j, -u⸩⁆ := by rw [commutator_of_αβ_ψ_a Fchar hi hj]
  have := calc
    ⸨ψ, j, u⸩ * ⸨αβ, i, t⸩ * ⸨αβψ, i + j, t * u⸩ * ⸨αβ2ψ, i + 2 * j, -t * u ^ 2⸩
    = ⸨ψ, j, u⸩ * ⸨αβ, i, t⸩ * (⸨αβψ, i + j, t * u⸩ * ⸨αβ2ψ, i + 2 * j, -t * u^2⸩) := rfl
    _ = ⸨ψ, j, u⸩ * ⸨αβ, i, t⸩ * ⁅⸨αβ, i, -t⸩, ⸨ψ, j, -u⸩⁆ := by rw [aux]
    _ = ⸨ψ, j, u⸩ * ⸨αβ, i, t⸩ * ⁅⸨αβ, i, t⸩⁻¹, ⸨ψ, j, u⸩⁻¹⁆ := by rw [inv_of_αβ, inv_of_ψ]
    _ = ⸨αβ, i, t⸩ * ⸨ψ, j, u⸩ := by group
  exact this.symm

-- 8.145b
@[group_reassoc]
theorem expr_αβ_ψ_as_ψ_αβψ_αβ2ψ_αβ :
  forall_ij_tu 2 1,
    ⸨αβ, i, t⸩ * ⸨ψ, j, u⸩ = ⸨ψ, j, u⸩ * ⸨αβψ, i + j, t * u⸩ * ⸨αβ2ψ, i + 2 * j, -t * u^2⸩ * ⸨αβ, i, t⸩ := by
  intro i j hi hj t u
  have aux : ⸨ψ, j, u⸩ * ⸨αβψ, i + j, t * u⸩ * ⸨αβ2ψ, i + 2 * j, -t * u^2⸩ * ⸨αβ, i, t⸩ = ⸨ψ, j, u⸩ * (⸨αβψ, i + j, t * u⸩ * ⸨αβ2ψ, i + 2 * j, -t * u^2⸩) * ⸨αβ, i, t⸩ := rfl
  have := calc
    ⸨αβψ, i + j, t * u⸩ * ⸨αβ2ψ, i + 2 * j, -t * u^2⸩ = ⸨αβψ, i + j, t * (-u)⸩⁻¹ * ⸨αβ2ψ, i + 2 * j, t * u^2⸩⁻¹ := by
      rw [inv_of_αβ2ψ Fchar (by ht), inv_of_αβψ (by ht)]; field_simp
    _ = (⸨αβ2ψ, i + 2 * j, t * (-u)^2⸩ * ⸨αβψ, i + j, t * (-u)⸩)⁻¹ := by ring_nf; group
    _ = ⁅⸨αβ, i, t⸩, ⸨ψ, j, -u⸩⁆⁻¹ := by rw [commutator_of_αβ_ψ_b Fchar hi hj]
    _ = ⁅⸨αβ, i, t⸩, ⸨ψ, j, u⸩⁻¹⁆⁻¹ := by rw [inv_of_ψ]
  rw [aux, this]
  group

-- 8.145c
@[group_reassoc]
theorem expr_αβ_ψ_as_ψ_αβ2ψ_αβψ_αβ :
  ∀ ⦃i j : ℕ⦄ (hi : i ≤ 2) (hj : j ≤ 1) (t u : F),
  ⸨αβ, i, t⸩ * ⸨ψ, j, u⸩ = ⸨ψ, j, u⸩ * ⸨αβ2ψ, i + 2 * j, -t * u^2⸩ * ⸨αβψ, i + j, t * u⸩ * ⸨αβ, i, t⸩ := by
  intro i j hi hj t u
  have aux : ⸨ψ, j, u⸩ * ⸨αβ2ψ, i + 2 * j, -t * u^2⸩ * ⸨αβψ, i + j, t * u⸩ * ⸨αβ, i, t⸩ = ⸨ψ, j, u⸩ * (⸨αβ2ψ, i + 2 * j, -t * u^2⸩ * ⸨αβψ, i + j, t * u⸩) * ⸨αβ, i, t⸩ := rfl
  have := calc
    ⸨αβ2ψ, i + 2 * j, -t * u^2⸩ * ⸨αβψ, i + j, t * u⸩ = ⸨αβ2ψ, i + 2 * j, t * (-u)^2⸩⁻¹ * ⸨αβψ, i + j, t * (-u)⸩⁻¹ := by rw [inv_of_αβ2ψ Fchar (by ht), inv_of_αβψ (by ht)]; field_simp
    _ = (⸨αβψ, i + j, t * (-u)⸩ * ⸨αβ2ψ, i + 2 * j, t * (-u)^2⸩)⁻¹ := by group
    _ = ⁅⸨αβ, i, t⸩, ⸨ψ, j, -u⸩⁆⁻¹ := by rw [commutator_of_αβ_ψ_a Fchar hi hj]
    _ = ⁅⸨αβ, i, t⸩, ⸨ψ, j, u⸩⁻¹⁆⁻¹ := by rw [inv_of_ψ]
  rw [aux, this]
  group

-- 8.145d
@[group_reassoc]
theorem expr_αβ_ψ_as_αβ2ψ_αβψ_ψ_αβ :
  forall_ij_tu 2 1,
    ⸨αβ, i, t⸩ * ⸨ψ, j, u⸩ = ⸨αβ2ψ, i + 2 * j, t * u^2⸩ * ⸨αβψ, i + j, t * u⸩ * ⸨ψ, j, u⸩ * ⸨αβ, i, t⸩ := by
  intro i j hi hj t u
  rw [←commutator_of_αβ_ψ_b Fchar hi hj]
  group

-- 8.146
@[group_reassoc]
theorem expr_ψ_αβ_as_αβ_αβ2ψ_αβψ_ψ :
  forall_ij_tu αβ ψ,
    ⸨ψ, j, u⸩ * ⸨αβ, i, t⸩ = ⸨αβ, i, t⸩ * ⸨αβ2ψ, i + 2 * j, -t * u^2⸩ * ⸨αβψ, i + j, -t * u⸩ * ⸨ψ, j, u⸩ := by
  intro i j hi hj t u
  have := calc
    ⸨αβ2ψ, i + 2 * j, -t * u^2⸩ * ⸨αβψ, i + j, -t * u⸩ = ⁅⸨αβ, i, -t⸩, ⸨ψ, j, u⸩⁆ := by rw [commutator_of_αβ_ψ_b Fchar hi hj]
    _ = ⁅⸨αβ, i, t⸩⁻¹, ⸨ψ, j, u⸩⁆ := by rw [inv_of_αβ]
  grw [this]
  rw [←inv_of_αβ]
  group

@[simp, chev_simps]
theorem id_of_αβψ : id_of_root((weakB3LargeGraded F).project, αβψ) := by
  intro i hi
  have := doub_of_αβψ Fchar hi 0
  rw [mul_zero] at this
  exact mul_right_eq_self.1 this

@[simp, chev_simps]
theorem id_of_αβ2ψ : id_of_root((weakB3LargeGraded F).project, αβ2ψ) := by
  intro i hi
  have := doub_of_αβ2ψ Fchar hi 0
  rw [mul_zero] at this
  exact mul_right_eq_self.1 this

theorem defineThenReflect_of_αβ2ψ (g : GradedChevalleyGenerator B3LargePosRoot F)
  (h : g.ζ = αβ2ψ) :
  (weakB3LargeGraded F).project (defineThenReflect (weakB3LargeGraded F) g)
    = (weakB3LargeGraded F).project (FreeGroup.of (reflect g)) := by
  rcases g with ⟨ ζ, i, hi, t ⟩
  simp only at h
  subst ζ
  simp only [defineThenReflect, MonoidHom.coe_comp, Function.comp_apply, FreeGroup.lift.of]
  rw [weakB3LargeGraded]
  simp only
  rw [weak_define]
  simp only [map_commutatorElement, map_mul, map_inv, FreeGroup.map.of, reflect, PositiveRootSystem.height]
  rw [←weakB3LargeGraded, ←expr_αβ2ψ_as_comm_of_α_β2ψ Fchar (by ht) (by ht), mul_one,
    eq_of_deg_eq αβ2ψ (αβ2ψ.height - i)]
  simp only [height]
  nth_rewrite 3 [←(correct_of_split_4_into_1_3 i hi).2.2]
  have := (correct_of_split_4_into_1_3 i hi).1
  have := (correct_of_split_4_into_1_3 i hi).2.1
  omega
