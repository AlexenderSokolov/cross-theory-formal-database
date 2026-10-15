/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Steinberg.B3Large.Basic
import Steinberg.B3Large.EstabAlphaBeta2Psi

namespace Steinberg.B3Large

open Steinberg B3LargePosRoot GradedPartialChevalley GradedChevalleyGenerator GradedPartialChevalleyGroup

variable {F : Type TF} [Field F] (Fchar : (2 : F) ≠ 0)

-- TODO-B: (3/16) is there a better place/file for these theorems?
include Fchar

theorem defineThenReflect_eq_reflect_of_αβ2ψ (g : GradedChevalleyGenerator B3LargePosRoot F) (h : g.ζ = αβ2ψ) :
  (weakB3LargeGraded F).project (defineThenReflect (weakB3LargeGraded F) g) = (weakB3LargeGraded F).project (FreeGroup.of (reflect g)) := by
  rcases g with ⟨ ζ, i, hi, t ⟩
  simp only at h
  subst ζ
  simp only [defineThenReflect, MonoidHom.coe_comp, Function.comp_apply, FreeGroup.lift.of]
  rw [weakB3LargeGraded]
  simp only [weak_define, map_commutatorElement, FreeGroup.map.of, reflect]
  rw [← weakB3LargeGraded, ← def_of_αβ2ψ]
  simp only [PositiveRootSystem.height, split_4_into_1_3]
  split
  -- this resolves every goal except height 2
  all_goals (simp only [height])
  simp_arith
  repeat rw [←expr_αβ2ψ_as_comm_of_α_β2ψ]
  all_goals assumption

set_option maxHeartbeats 0

-- 8.147a
theorem hom_lift_of_interchange_of_α2β2ψ_a : forall_ijk_tuv,
    ⁅⸨αβ, i + j, t⸩, ⸨β2ψ, j + 2 * k, 2 * u * v⸩⁆ = ⁅⸨αβψ, i + j + k, t * u⸩, ⸨βψ, j + k, v⸩⁆ := by
  intro i j k hi hj hk t u v
  rcases eq_or_ne u 0 with (rfl| hu)
  · chev_simp [id_of_αβψ Fchar]
  rcases eq_or_ne v 0 with (rfl | hv)
  · chev_simp
  have aux := raw_hom_lift_of_interchange_of_α2β2ψ_a hi hj hk (t * u / v) (v / u) u
  rw [eq_of_coef_eq αβ t (by field_simp),
      eq_of_coef_eq β2ψ (2 * u * v) (by field_simp; group),
      eq_of_coef_eq αβ (t := -(t * u / v) * (v / u)) (-t) (by field_simp; group),
      div_mul_cancel₀ v hu] at aux
  grw [aux, expr_αβψ_as_ψ_αβ_ψ_αβ_ψ (add_le_add hi hj) hk]

-- 8.147b
theorem hom_lift_of_interchange_of_α2β2ψ_b : forall_ijk_tuv,
    ⁅⸨αβψ, i + j + k, t⸩, ⸨βψ, j + k, u * v⸩⁆ = ⁅⸨αβ2ψ, i + j + 2 * k, 2 * t * u⸩, ⸨β, j, v⸩⁆ := by
  intro i j k hi hj hk t u v
  rcases eq_or_ne u 0 with hu | hu
  · rw [hu, mul_zero, zero_mul, id_of_βψ, id_of_αβ2ψ Fchar]; group
  rcases eq_or_ne v 0 with hv | hv
  · rw [hv, mul_zero, id_of_βψ, id_of_β]; group
  have aux := raw_hom_lift_of_interchange_of_α2β2ψ_b hi hj hk (t / (u * v)) v u
  have : t / (u * v) * v = t / u := by field_simp; group
  rw [this] at aux
  have : -(t / (u * v)) * v = -(t / u) := by field_simp; group
  rw [this] at aux
  grw [← expr_αβψ_as_ψ_αβ_ψ_αβ_ψ (add_le_add hi hj) hk, mul_comm v u] at aux
  field_simp at aux
  rw [aux]; clear aux
  have hijk : i + j + 2 * k ≤ αβ2ψ.height := by ht
  simp_rw [commutatorElement_def]
  grw [inv_of_αβ2ψ Fchar hijk]
  have : ∀ (c : F), t / (u * v) * (c * v * u * u) = c * t * u := by
      intro c
      grw [mul_comm]
      field_simp
      group
  have h4 := expr_αβ2ψ_as_α_β2ψ_α_β2ψ Fchar (j := j + 2 * k) hi (by ht) (t / (u * v)) (2 * v * u * u)
  rw [← deg_add_assoc _ _ _ _ hijk, this] at h4
  grw [← h4]; clear h4
  have h3 := expr_αβ2ψ_as_β2ψ_α_β2ψ_α Fchar (j := j + 2 * k) hi (by ht) (t / (u * v)) (-2 * v * u * u)
  rw [← deg_add_assoc _ _ _ _ hijk, this] at h3
  chev_simp at h3
  grw [← h3]

-- 8.148
omit Fchar
theorem hom_lift_of_comm_ψ_αβ_β2ψ : forall_ijk_tuv,
    ⁅⸨ψ, k, t⸩, ⁅⸨αβ, i + j, u⸩, ⸨β2ψ, j + 2 * k, v⸩⁆⁆ = 1 := by
  intro i j k hi hj hk t u v
  rcases eq_or_ne t 0 with ht | ht
  · rw [ht, id_of_ψ]; group
  rcases eq_or_ne v 0 with hv | hv
  · rw [hv, id_of_β2ψ]; group
  have aux := raw_hom_lift_of_comm_of_ψ_αβ_β2ψ hi hj hk (u * t * t / v) (v / (t * t)) t
  have : u * t * t / v * (v / (t * t)) = u := by ring_nf; field_simp
  rw [this] at aux
  have : v / (t * t) * t ^ 2 = v := by ring_nf; field_simp
  rw [this] at aux
  exact aux

-- 8.149
theorem hom_lift_of_comm_αβ_αβ_β2ψ : forall_ijk_tu α β ψ,
    ⁅⸨αβ, i + j, t⸩, ⁅⸨αβ, i + j, t⸩, ⸨β2ψ, j + 2 * k, u⸩⁆⁆ = 1 ∧
  ⁅⸨αβ, i + j, t⸩, ⁅⸨αβ, i + j, -t⸩, ⸨β2ψ, j + 2 * k, u⸩⁆⁆ = 1 := by
  intro i j k hi hj hk t u
  rcases eq_or_ne u 0 with hu | hu
  · rw [hu, id_of_β2ψ]
    exact ⟨by group, by group⟩
  have aux₁ := raw_hom_lift_of_comm_of_αβ_αβ_β2ψ_a hi hj hk (t / u) u 1
  have aux₂ := raw_hom_lift_of_comm_of_αβ_αβ_β2ψ_b hi hj hk (t / u) u 1
  have : t / u * u = t := by field_simp
  rw [this, pow_two, one_mul, mul_one] at aux₁
  rw [this, pow_two, one_mul, mul_one] at aux₂
  have : -(t / u) * u = -t := by field_simp
  rw [this] at aux₂
  exact ⟨aux₁, aux₂⟩

-- 8.150
theorem hom_lift_of_inv_doub_of_αβ_β2ψ : forall_ijk_tu α β ψ,
  ⁅⸨αβ, i + j, t⸩, ⸨β2ψ, j + 2 * k, u⸩⁆ = ⁅⸨αβ, i + j, -t⸩, ⸨β2ψ, j + 2 * k, -u⸩⁆ ∧
  ⁅⸨αβ, i + j, t⸩, ⸨β2ψ, j + 2 * k, u⸩⁆ * ⁅⸨αβ, i + j, -t⸩, ⸨β2ψ, j + 2 * k, u⸩⁆ = 1 ∧
  ⁅⸨αβ, i + j, t⸩, ⸨β2ψ, j + 2 * k, u⸩⁆ * ⁅⸨αβ, i + j, t⸩, ⸨β2ψ, j + 2 * k, u⸩⁆ = ⁅⸨αβ, i + j, 2 * t⸩, ⸨β2ψ, j + 2 * k, u⸩⁆ := by
  intro i j k hi hj hk t u
  rcases eq_or_ne u 0 with hu | hu
  · rw [hu, neg_zero, id_of_β2ψ]
    exact ⟨by group, by group, by group⟩
  have aux₁ := raw_hom_lift_of_inv_doub_of_αβ_β2ψ_a hi hj hk (t / u) u 1
  have aux₂ := raw_hom_lift_of_inv_doub_of_αβ_β2ψ_b hi hj hk (t / u) u 1
  have aux₃ := raw_hom_lift_of_inv_doub_of_αβ_β2ψ_c hi hj hk (t / u) u 1
  have eq1 : (t / u) * u = t := by field_simp
  have eq2 : u * 1^2 = u := by rw [pow_two, mul_one, mul_one]
  have eq3 : -(t / u) * u = -t := by field_simp
  have eq4 : -u * 1^2 = -u := by rw [pow_two, mul_one, mul_one]
  have eq5 : 2 * (t / u) * u = 2 * t := by field_simp
  rw [eq1, eq2, eq3, eq4] at aux₁
  rw [eq1, eq2, eq3] at aux₂
  rw [eq1, eq2, eq5] at aux₃
  exact ⟨aux₁, aux₂, aux₃⟩

-- 8.151
include Fchar
theorem hom_lift_of_inv_doub_of_β_αβ2ψ : forall_ijk_tu α β ψ,
  ⁅⸨β, j, t⸩, ⸨αβ2ψ, i + j + 2 * k, u⸩⁆ = ⁅⸨β, j, -t⸩, ⸨αβ2ψ, i + j + 2 * k, -u⸩⁆ ∧
  ⁅⸨β, j, t⸩, ⸨αβ2ψ, i + j + 2 * k, u⸩⁆ * ⁅⸨β, j, -t⸩, ⸨αβ2ψ, i + j + 2 * k, u⸩⁆ = 1 ∧
  ⁅⸨β, j, t⸩, ⸨αβ2ψ, i + j + 2 * k, u⸩⁆ * ⁅⸨β, j, t⸩, ⸨αβ2ψ, i + j + 2 * k, u⸩⁆ = ⁅⸨β, j, 2 * t⸩, ⸨αβ2ψ, i + j + 2 * k, u⸩⁆ := by
  intro i j k hi hj hk t u
  rcases eq_or_ne t 0 with (rfl | ht)
  · chev_simp [id_of_β, commutatorElement_one_left, neg_zero, mul_one, mul_zero, and_self]
  have hijk : i + j + 2 * k ≤ αβ2ψ.height := by ht
  have hjk : j + 2 * k ≤ β2ψ.height := by ht
  have aux₁ := raw_hom_lift_of_inv_doub_of_β_αβ2ψ_a hi hj hk (u / t) t 1
  have aux₂ := raw_hom_lift_of_inv_doub_of_β_αβ2ψ_b hi hj hk (u / t) t 1
  have aux₃ := raw_hom_lift_of_inv_doub_of_β_αβ2ψ_c hi hj hk (u / t) t 1
  field_simp at aux₁ aux₂ aux₃
  rw [neg_div] at aux₁
  have h1 := @expr_αβ2ψ_as_α_β2ψ_α_β2ψ F _ Fchar i (j + 2 * k) hi hjk (-(u/t)) (t)
  have h2 := @expr_αβ2ψ_as_α_β2ψ_α_β2ψ F _ Fchar i (j + 2 * k) hi hjk (u/t) (t)
  norm_num at h1 h2; field_simp at h1 h2
  have eq1 : -u/t = -(u/t) := by field_simp
  simp only [← inv_of_β2ψ, eq1] at h1 h2
  simp only [← inv_of_α] at h2
  have : ⸨α, i, u / t⸩ = ⸨α, i, -(u / t)⸩⁻¹ := by chev_simp
  rw [this] at h1
  grw [← commutatorElement_def] at h1 h2
  rw [← deg_add_assoc _ _ _ _ hijk] at h1 h2
  grw [h2, h1, aux₂, aux₃, ← eq1, aux₁]

-- 8.152
theorem hom_lift_of_comm_βψ_αβ2ψ :
  ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 1) (hj : j ≤ 1) (hk : k ≤ 1) (t u : F),
  ⁅⸨βψ, j + k, t⸩, ⸨αβ2ψ, i + j + 2 * k, u⸩⁆ = 1 := by
  intro i j k hi hj hk t u
  rcases eq_or_ne t 0 with ht | ht
  · rw [ht, id_of_βψ]; group
  have aux := raw_hom_lift_of_comm_of_βψ_αβ2ψ hi hj hk (u / t) t 1
  rw [pow_two, mul_one, mul_one, mul_one] at aux
  have aux' := @expr_αβ2ψ_as_comm_of_α_β2ψ _ _ Fchar i (j + 2 * k) hi (by omega) (u / t) t
  have : ⸨αβ2ψ, i + (j + 2 * k), u / t * t⸩ = ⸨αβ2ψ, i + j + 2 * k, u⸩ := by field_simp; group
  rw [this] at aux'
  rw [aux', aux]

-- 8.153
theorem hom_lift_of_comm_of_β2ψ_αβ2ψ :
  ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 1) (hj : j ≤ 1) (hk : k ≤ 1) (t u : F),
  ⁅⸨β2ψ, j + 2 * k, t⸩, ⸨αβ2ψ, i + j + 2 * k, u⸩⁆ = 1 := by
  intro i j k hi hj hk t u
  rcases eq_or_ne t 0 with ht | ht
  · rw [ht, id_of_β2ψ]; group
  have aux := raw_hom_lift_of_comm_of_β2ψ_αβ2ψ hi hj hk (u / t) t 1
  rw [pow_two, mul_one, mul_one] at aux
  have aux' := @expr_αβ2ψ_as_comm_of_α_β2ψ _ _ Fchar i (j + 2 * k) hi (by omega) (u / t) t
  have : ⸨αβ2ψ, i + (j + 2 * k), u / t * t⸩  = ⸨αβ2ψ, i + j + 2 * k, u⸩ := by field_simp; group
  rw [this] at aux'
  rw [aux', aux]

-- 8.154
omit Fchar
theorem comm_of_βψ_αβ_β2ψ : forall_ijk_tuv βψ αβ β2ψ,
    ⁅⸨βψ, i, t⸩, ⁅⸨αβ, j, u⸩, ⸨β2ψ, k, v⸩⁆⁆ = 1 := by
  intro i j k hi hj hk t u v
  apply triv_comm_iff_commutes.2
  grw [commutatorElement_def,
    ← expr_αβ_βψ_as_βψ_αβ hj hi, expr_βψ_β2ψ_as_β2ψ_βψ hi hk,
    ← expr_αβ_βψ_as_βψ_αβ hj hi, expr_βψ_β2ψ_as_β2ψ_βψ hi hk]

@[group_reassoc]
theorem expr_βψ_comm_αβ_β2ψ_as_comm_αβ_β2ψ_βψ : forall_ijk_tuv βψ αβ β2ψ,
    ⸨βψ, i, t⸩ * ⁅⸨αβ, j, u⸩, ⸨β2ψ, k, v⸩⁆ = ⁅⸨αβ, j, u⸩, ⸨β2ψ, k, v⸩⁆ * ⸨βψ, i, t⸩ := by
  intro i j k hi hj hk t u v
  exact triv_comm_iff_commutes.1 (comm_of_βψ_αβ_β2ψ hi hj hk t u v)

-- 8.155
theorem comm_of_αβ_βψ_αβψ : forall_ijk_tuv αβ βψ αβψ,
    ⁅⸨αβ, i, t⸩, ⁅⸨βψ, j, u⸩, ⸨αβψ, k, v⸩⁆⁆ = 1 := by
  intro i j k hi hj hk t u v
  apply triv_comm_iff_commutes.2
  grw [commutatorElement_def, expr_αβ_βψ_as_βψ_αβ hi hj, expr_αβ_αβψ_as_αβψ_αβ hi hk,
  expr_αβ_βψ_as_βψ_αβ hi hj, expr_αβ_αβψ_as_αβψ_αβ hi hk]

@[group_reassoc]
theorem expr_αβ_comm_βψ_αβψ_as_comm_βψ_αβψ_αβ : forall_ijk_tuv αβ βψ αβψ,
    ⸨αβ, i, t⸩ * ⁅⸨βψ, j, u⸩, ⸨αβψ, k, v⸩⁆ = ⁅⸨βψ, j, u⸩, ⸨αβψ, k, v⸩⁆ * ⸨αβ, i, t⸩ := by
  intro i j k hi hj hk t u v
  exact triv_comm_iff_commutes.1 (comm_of_αβ_βψ_αβψ hi hj hk t u v)

-- 8.156
theorem comm_of_β_αβ_β2ψ : forall_ijk_tuv β αβ β2ψ,
    ⁅⸨β, i, t⸩, ⁅⸨αβ, j, u⸩, ⸨β2ψ, k, v⸩⁆⁆ = 1 := by
  intro i j k hi hj hk t u v
  apply triv_comm_iff_commutes.2
  grw [commutatorElement_def, expr_β_αβ_as_αβ_β hi hj, expr_β_β2ψ_as_β2ψ_β hi hk,
  expr_β_αβ_as_αβ_β hi hj, expr_β_β2ψ_as_β2ψ_β hi hk]

@[group_reassoc]
theorem expr_β_comm_αβ_β2ψ_as_comm_αβ_β2ψ_β : forall_ijk_tuv β αβ β2ψ,
    ⸨β, i, t⸩ * ⁅⸨αβ, j, u⸩, ⸨β2ψ, k, v⸩⁆ = ⁅⸨αβ, j, u⸩, ⸨β2ψ, k, v⸩⁆ * ⸨β, i, t⸩ := by
  intro i j k hi hj hk t u v
  exact triv_comm_iff_commutes.1 (comm_of_β_αβ_β2ψ hi hj hk t u v)

-- 8.157
theorem comm_of_β_αβψ_βψ : forall_ijk_tuv β αβψ βψ,
    ⁅⸨β, i, t⸩, ⁅⸨αβψ, j, u⸩, ⸨βψ, k, v⸩⁆⁆ = 1 := by
  intro i j k hi hj hk t u v
  apply triv_comm_iff_commutes.2
  grw [commutatorElement_def, expr_β_αβψ_as_αβψ_β hi hj, expr_β_βψ_as_βψ_β hi hk,
  expr_β_αβψ_as_αβψ_β hi hj, expr_β_βψ_as_βψ_β hi hk]

@[group_reassoc]
theorem expr_β_comm_αβψ_βψ_as_comm_αβψ_βψ_β : forall_ijk_tuv β αβψ βψ,
    ⸨β, i, t⸩ * ⁅⸨αβψ, j, u⸩, ⸨βψ, k, v⸩⁆ = ⁅⸨αβψ, j, u⸩, ⸨βψ, k, v⸩⁆ * ⸨β, i, t⸩ := by
  intro i j k hi hj hk t u v
  exact triv_comm_iff_commutes.1 (comm_of_β_αβψ_βψ hi hj hk t u v)

include Fchar
-- 8.158 (revised)
theorem sufficient_conditions_for_comm_of_αβψ_and_βψ :
  ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 2) (hj : j ≤ 1) (hk : k ≤ 2)
  (h35a : ∀ (t u v : F), ⁅⸨ψ, j, t⸩, ⁅⸨αβ, i, u⸩, ⸨β2ψ, j + k, v⸩⁆⁆ = 1)
  (h35b : ∀ (t u : F), ⁅⸨αβ, i, t⸩, ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u⸩⁆⁆ = 1 ∧ ⁅⸨αβ, i, t⸩, ⁅⸨αβ, i, -t⸩, ⸨β2ψ, j + k, u⸩⁆⁆ = 1)
  (h35c : ∀ (t u : F), ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u⸩⁆ = ⁅⸨αβ, i, -t⸩, ⸨β2ψ, j + k, -u⸩⁆)
  (h35d : ∀ (t u : F), ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u⸩⁆ * ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u⸩⁆ = ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, 2 * u⸩⁆),
  ∀ (t u v : F), ⁅⸨αβψ, i + j, t * u⸩, ⸨βψ, k, v⸩⁆ = ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, 2 * u * v⸩⁆ := by
  intro i j k hi hj hk h35a h35b h35c h35d t u v
  have h35a' := fun t' u' v' ↦ triv_comm_iff_commutes.1 (h35a t' u' v')
  have h35b₁ := fun t' u' ↦ triv_comm_iff_commutes.1 (h35b t' u').left
  have h35b₂ := fun t' u' ↦ triv_comm_iff_commutes.1 (h35b t' u').right
  have h35b₃ := fun t' u' ↦ triv_comm_iff_commutes.1 (h35b (-t') u').right
  norm_num at h35b₃
  have aux₀ : -(2 * (u / 2) * v) = -(u * v) := by ring_nf; field_simp
  have eq36 : ⸨β2ψ, j + k, -(u * v)⸩ * ⸨αβ, i, t⸩ = ⸨αβ, i, t⸩ * ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u * v⸩⁆ * ⸨β2ψ, j + k, -u * v⸩ := by calc
    ⸨β2ψ, j + k, -(u * v)⸩ * ⸨αβ, i, t⸩ = ⸨αβ, i, t⸩ * ⁅⸨αβ, i, -t⸩, ⸨β2ψ, j + k, -(u * v)⸩⁆ * ⸨β2ψ, j + k, -(u * v)⸩ := by
      rw [← inv_of_αβ, ← inv_of_β2ψ]; group
    _ = ⸨αβ, i, t⸩ * ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u * v⸩⁆ * ⸨β2ψ, j + k, -u * v⸩ := by grw [h35c]
  have eq37 : ⸨αβ, i, -t⸩ * ⸨β2ψ, j + k, -(u * v)⸩ = ⸨β2ψ, j + k, -(u * v)⸩ * ⸨αβ, i, -t⸩ * ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u * v⸩⁆ := by
    rw [← inv_of_αβ, ← inv_of_β2ψ]; group
  have := calc
    ⸨αβψ, i + j, t * u⸩ * ⸨βψ, k, v⸩ = ⸨ψ, j, -u/2⸩ * ⸨αβ, i, t⸩ * ⸨ψ, j, u⸩ * ⸨αβ, i, -t⸩ * ⸨ψ, j, -u/2⸩ * ⸨βψ, k, v⸩ := by rw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi hj]
    _ = ⸨βψ, k, v⸩ * ⸨ψ, j, -u/2⸩ * ⸨β2ψ, j + k, -u * v⸩ * ⸨αβ, i, t⸩ * ⸨β2ψ, j + k, 2 * u * v⸩ * ⸨ψ, j, u⸩ * ⸨αβ, i, -t⸩ * ⸨β2ψ, j + k, -u * v⸩ * ⸨ψ, j, -u/2⸩ := by
      grw [expr_ψ_βψ_as_βψ_β2ψ_ψ hj hk, aux₀, expr_αβ_βψ_as_βψ_αβ hi hk, expr_ψ_βψ_as_βψ_β2ψ_ψ hj hk, expr_αβ_βψ_as_βψ_αβ hi hk, expr_ψ_βψ_as_βψ_ψ_β2ψ hj hk, aux₀]
    _ = ⸨βψ, k, v⸩ * ⸨ψ, j, -u/2⸩ * ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u * v⸩⁆ * ⸨αβ, i, t⸩ * ⸨β2ψ, j + k, -u * v⸩ * ⸨β2ψ, j + k, 2 * u * v⸩ * ⸨ψ, j, u⸩ * ⸨β2ψ, j + k, -(u * v)⸩ * ⸨αβ, i, -t⸩ * ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u * v⸩⁆ * ⸨ψ, j, -u/2⸩ := by
      grw [eq36, eq36, eq37, h35b₁, h35b₂]
    _ = ⸨βψ, k, v⸩ * ⸨ψ, j, -u/2⸩ * ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u * v⸩⁆ * ⸨αβ, i, t⸩ * ⸨ψ, j, u⸩ * ⸨αβ, i, -t⸩ * ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u * v⸩⁆ * ⸨ψ, j, -u/2⸩ := by
      grw [expr_ψ_β2ψ_as_β2ψ_ψ hj (add_le_add hj hk)]; ring_nf
      rw [id_of_β2ψ, one_mul]
    _ = ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u * v⸩⁆ * ⸨βψ, k, v⸩ * ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u * v⸩⁆ * ⸨ψ, j, -u/2⸩ * ⸨αβ, i, t⸩ * ⸨ψ, j, u⸩ * ⸨αβ, i, -t⸩ * ⸨ψ, j, -u/2⸩ := by
      grw [h35a', expr_βψ_comm_αβ_β2ψ_as_comm_αβ_β2ψ_βψ hk hi (add_le_add hj hk), ← h35a', ← h35b₁, ← h35a', h35b₃]
    _ = ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u * v⸩⁆ * ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, u * v⸩⁆ * ⸨βψ, k, v⸩ * ⸨ψ, j, -u/2⸩ * ⸨αβ, i, t⸩ * ⸨ψ, j, u⸩ * ⸨αβ, i, -t⸩ * ⸨ψ, j, -u/2⸩ := by
      grw [expr_βψ_comm_αβ_β2ψ_as_comm_αβ_β2ψ_βψ hk hi (add_le_add hj hk)]
    _ = ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, 2 * u * v⸩⁆ * ⸨βψ, k, v⸩ * ⸨αβψ, i + j, t * u⸩ := by
      grw [h35d, expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi hj]
  exact eq_comm_of_reorder_left this

lemma interchange_of_α2β2ψ_aux :
  ∀ (t u : F), ⁅⸨αβ, 1, t⸩, ⸨β2ψ, 1, u⸩⁆ = ⁅⸨αβ, 0, t⸩, ⸨β2ψ, 2, u⸩⁆ := by
    intro t u
    have := @hom_lift_of_interchange_of_α2β2ψ_a F _ Fchar 0 1 0 (by norm_num) (by norm_num) (by norm_num)
    norm_num at this
    have this' := @hom_lift_of_interchange_of_α2β2ψ_a F _ Fchar 0 0 1 (by norm_num) (by norm_num) (by norm_num)
    norm_num at this'
    specialize this t (u/2) 1; norm_num at this; field_simp at this
    specialize this' t (u/2) 1; norm_num at this'; field_simp at this'
    exact Eq.trans this (Eq.symm this')

-- 8.159a
theorem partial_A_interchange_of_α2β2ψ_a :
  ∀ (t u v : F),
  ⁅⸨αβψ, 0, t * u⸩, ⸨βψ, 2, v⸩⁆ = ⁅⸨αβ, 0, t⸩, ⸨β2ψ, 2, 2 * u * v⸩⁆ := by
  have h1 := @hom_lift_of_comm_ψ_αβ_β2ψ F _ 0 1 0 (by ht) (by ht) (by ht)
  have h2 := @hom_lift_of_comm_αβ_αβ_β2ψ F _ 0 0 1 (by ht) (by ht) (by ht)
  have h3 := @hom_lift_of_inv_doub_of_αβ_β2ψ F _ 0 0 1 (by ht) (by ht) (by ht)
  have h4 := @hom_lift_of_interchange_of_α2β2ψ_a F _ Fchar 0 0 1 (by ht) (by ht) (by ht)
  have := @sufficient_conditions_for_comm_of_αβψ_and_βψ _ _ Fchar 0 0 2 (by ht) (by ht) (by ht)
  norm_num at this
  apply this
  · intro t u v
    have := @interchange_of_α2β2ψ_aux _ _ Fchar u v
    rw [← this]
    specialize h1 t u v; norm_num at h1; exact h1
  · exact h2
  · exact fun t u ↦ (h3 t u).left
  · intro t u
    have h4a := h4 t 1 u; norm_num at h4a
    have h4b := h4 (2*t) (1/2) u; norm_num at h4b; field_simp at h4b
    specialize h3 t u
    grw [h3.right.right, h4a, h4b]

-- 8.159b
theorem partial_A_interchange_of_α2β2ψ_b :
  ∀ (t u v : F),
  ⁅⸨αβψ, 2, t * u⸩, ⸨βψ, 0, v⸩⁆ = ⁅⸨αβ, 1, t⸩, ⸨β2ψ, 1, 2 * u * v⸩⁆ := by
  have := @sufficient_conditions_for_comm_of_αβψ_and_βψ _ _ Fchar 1 1 0 (by norm_num) (by norm_num) (by norm_num)
  have h := @interchange_of_α2β2ψ_aux _ _ Fchar
  have h1 := @hom_lift_of_comm_ψ_αβ_β2ψ F _ 0 0 1 (by norm_num) (by norm_num) (by norm_num)
  have h2 := @hom_lift_of_comm_αβ_αβ_β2ψ F _ 0 1 0 (by norm_num) (by norm_num) (by norm_num)
  have h3 := @hom_lift_of_inv_doub_of_αβ_β2ψ F _ 0 0 1 (by norm_num) (by norm_num) (by norm_num)
  have h4 := @hom_lift_of_interchange_of_α2β2ψ_a F _ Fchar 0 0 1 (by norm_num) (by norm_num) (by norm_num)
  norm_num at this
  apply this
  · intro t u v
    rw [h u v]
    specialize h1 t u v; norm_num at h1; exact h1
  · exact h2
  · intro t u
    have h1a := h t u
    have h1b := h (-t) (-u)
    grw [h1a, h1b]
    exact (h3 t u).left
  · intro t u
    specialize h3 t u; norm_num at h3
    rw [h t u]
    grw [h3.right.right]
    rw [h t (2*u)]
    have h4a := h4 t 1 u; norm_num at h4a
    have h4b := h4 (2*t) (1/2) u; norm_num at h4b; field_simp at h4b
    grw [h4a, h4b]

-- 8.160
include Fchar in
theorem more_sufficient_conditions_for_comm_of_αβψ_and_βψ :
  ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 3) (hj : j ≤ 1) (hk : k ≤ 1)
  (h38a : ∀ (t u v : F), ⁅⸨β, k, t⸩, ⁅⸨αβ2ψ, i + j, u⸩, ⸨β, k, v⸩⁆⁆ = 1)
  (h38b : ∀ (t u v : F), ⁅⸨ψ, j, t⸩, ⁅⸨αβ2ψ, i + j, u⸩, ⸨β, k, v⸩⁆⁆ = 1)
  (h38c : ∀ (t u : F), ⁅⸨β, k, u⸩, ⸨αβ2ψ, i + j, -t⸩⁆ = ⁅⸨αβ2ψ, i + j, t⸩, ⸨β, k, u⸩⁆)
  (h38d : ∀ (t u : F), ⁅⸨αβ2ψ, i + j, t⸩, ⸨β, k, u⸩⁆ * ⁅⸨αβ2ψ, i + j, t⸩, ⸨β, k, u⸩⁆ = ⁅⸨αβ2ψ, i + j, 2 * t⸩, ⸨β, k, u⸩⁆),
    ∀ (t u v : F), ⁅⸨αβψ, i, t⸩, ⸨βψ, j + k, u * v⸩⁆ = ⁅⸨αβ2ψ, i + j, 2 * t * u⸩, ⸨β, k, v⸩⁆ := by
  intro i j k hi hj hk h38a h38b h38c h38d t u v
  have hi' : i ≤ αβψ.height := by ht
  have hj' : j ≤ ψ.height := by ht
  have hk' : k ≤ β.height := by ht
  have h39 : ⸨αβ2ψ, i + j, t * u⸩ * ⸨β, k, v⸩ = ⁅⸨αβ2ψ, i + j, t * u⸩, ⸨β, k, v⸩⁆ * ⸨β, k, v⸩ * ⸨αβ2ψ, i + j, t * u⸩ := by group
  have h40 : ⸨β, k, -v⸩ * ⸨αβ2ψ, i + j, t * u⸩  = ⸨αβ2ψ, i + j, t * u⸩ * ⸨β, k, -v⸩ * ⁅⸨αβ2ψ, i + j, t * u⸩, ⸨β, k, v⸩⁆ := by
    simp [← h38c, commutatorElement_def]
    have h1 : ⸨β, k, v⸩⁻¹ = ⸨β, k, -v⸩ := by chev_simp
    have h2 : ⸨αβ2ψ, i + j, t * u⸩⁻¹ = ⸨αβ2ψ, i + j, -(t * u)⸩ := by
      rw [inv_of_αβ2ψ Fchar (by ht)]
    grw [← h1, ← h2]
  have h : i + j ≤ αβ2ψ.height := by simp [height]; omega
  apply reorder_left_iff_eq_comm.mp
  nth_rw 1 [expr_βψ_as_ψ_β_ψ_β_ψ]
  grw [expr_αβψ_ψ_as_ψ_αβ2ψ_αβψ,
        ← expr_β_αβψ_as_αβψ_β,
        expr_αβψ_ψ_as_αβ2ψ_ψ_αβψ,
        ← expr_β_αβψ_as_αβψ_β]
  grw [expr_αβψ_ψ_as_αβ2ψ_ψ_αβψ]
  field_simp [add_comm, mul_comm, ← mul_assoc]
  grw [h39, h40]
  all_goals (try assumption)
  have : ⸨ψ, j, u⸩ * ⸨αβ2ψ, i + j, t * u⸩ = ⸨αβ2ψ, i + j, t * u⸩ * ⸨ψ, j, u⸩ := by
    rw [triv_comm_iff_commutes.1]
    rw [comm_of_ψ_αβ2ψ]
    exact Fchar
  grw [this]; clear this
  have : ⸨αβ2ψ, i + j, t * u⸩ * ⸨αβ2ψ, i + j, -(t * u * 2)⸩ * ⸨αβ2ψ, i + j, t * u⸩ = 1 := by
    have : -(t * u * 2) = 2 * (-t * u) := by ring
    rw [this, ← doub_of_αβ2ψ Fchar h]
    group
    rw [← inv_of_αβ2ψ Fchar (by ht)]
    simp
  grw [this]; clear this
  grw [h38a, h38b]
  have h1 : ⸨ψ, j, -(u / 2)⸩ * ⁅⸨αβ2ψ, i + j, t * u⸩, ⸨β, k, v⸩⁆ = ⁅⸨αβ2ψ, i + j, t * u⸩, ⸨β, k, v⸩⁆ * ⸨ψ, j, -(u / 2)⸩ := by
    rw [triv_comm_iff_commutes.1]
    exact h38b (-(u / 2)) (t * u) v
  have h2 : ⸨ψ, j, u⸩ * ⁅⸨αβ2ψ, i + j, t * u⸩, ⸨β, k, v⸩⁆ = ⁅⸨αβ2ψ, i + j, t * u⸩, ⸨β, k, v⸩⁆ * ⸨ψ, j, u⸩ := by
    rw [triv_comm_iff_commutes.1]
    exact h38b u (t * u) v
  have h3 : ⸨β, k, -v⸩ * ⁅⸨αβ2ψ, i + j, t * u⸩, ⸨β, k, v⸩⁆ = ⁅⸨αβ2ψ, i + j, t * u⸩, ⸨β, k, v⸩⁆ * ⸨β, k, -v⸩ := by
    rw [triv_comm_iff_commutes.1]
    exact h38a (-v) (t * u) v
  have h4 : ⸨β, k, v⸩ * ⁅⸨αβ2ψ, i + j, t * u⸩, ⸨β, k, v⸩⁆ = ⁅⸨αβ2ψ, i + j, t * u⸩, ⸨β, k, v⸩⁆ * ⸨β, k, v⸩ := by
    rw [triv_comm_iff_commutes.1]
    exact h38a v (t * u) v
  grw [h1, h2, h3, h2, h4, h1, h38d]
  have : ⸨βψ, j + k, u * v⸩ = ⸨ψ, j, -(u / 2)⸩ * ⸨β, k, v⸩ * ⸨ψ, j, u⸩ * ⸨β, k, -v⸩ * ⸨ψ, j, -(u / 2)⸩ := by
    rw [← neg_div, ← expr_βψ_as_ψ_β_ψ_β_ψ Fchar hj hk u v, mul_comm]
  have h5 : 2 * t * u = t * u * 2 := by
    ring
  grw [h5, ← this]

-- 8.161
theorem sufficient_conditions_for_comm_of_αβ2ψ_and_β2ψ :
    ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 3) (hj : j ≤ 1) (hk : k ≤ 3)
    (hyp : ∀ (t u : F), ⁅⸨β2ψ, k, t⸩, ⸨αβ2ψ, i + j, u⸩⁆ = 1),
    ∀ (t u : F), ⁅⸨β2ψ, i, t⸩, ⸨αβ2ψ, j + k, u⸩⁆ = 1 := by
  intro i j k hi hj hk hyp t u
  have hyp' := fun t' u' ↦ triv_comm_iff_commutes.1 (hyp t' u')
  apply triv_comm_iff_commutes.2
  -- expand αβ2ψ element as a product of α and β2ψ elements
  rw [←mul_one u, expr_αβ2ψ_as_α_β2ψ_α_β2ψ Fchar hj hk]
  -- commute the β2ψ element fully to the left (working on RHS)
  grw [expr_β2ψ_β2ψ_as_β2ψ_β2ψ, expr_α_β2ψ_as_β2ψ_αβ2ψ_α (t := -u) Fchar hj hi,
  expr_β2ψ_β2ψ_as_β2ψ_β2ψ, expr_α_β2ψ_as_β2ψ_α_αβ2ψ Fchar hj hi]
  rw [eq_of_deg_eq αβ2ψ (i + j) (add_comm j i), eq_of_deg_eq αβ2ψ (i + j) (add_comm j i)]
  rw [←hyp', ← inv_of_αβ2ψ Fchar (add_le_add hi hj)]
  group

-- 8.162a
include Fchar in
theorem partial_comm_of_β2ψ_αβ2ψ_a :
  ∀ (t u : F), ⁅⸨β2ψ, 2, t⸩, ⸨αβ2ψ, 1, u⸩⁆ = 1 := by
  have := sufficient_conditions_for_comm_of_αβ2ψ_and_β2ψ (F := F) (i := 2) (j := 0) (k := 1) (by ht)
  norm_num at this
  apply this
  have := hom_lift_of_comm_of_β2ψ_αβ2ψ (i := 1) (j := 1) (k := 0) (by ht)
  norm_num at this
  exact this

-- 8.162b
include Fchar in
theorem partial_comm_of_β2ψ_αβ2ψ_b :
  ∀ (t u : F), ⁅⸨β2ψ, 0, t⸩, ⸨αβ2ψ, 2, u⸩⁆ = 1 := by
  have := @sufficient_conditions_for_comm_of_αβ2ψ_and_β2ψ F _ Fchar 0 1 1 (by ht) (by norm_num) (by norm_num)
  norm_num at this
  apply this
  have := @hom_lift_of_comm_of_β2ψ_αβ2ψ F _ Fchar 0 1 0 (by norm_num) (by norm_num) (by norm_num)
  norm_num at this
  exact this

-- 8.163
theorem sufficient_conditions_for_comm_of_ψ_and_αβ2ψ_β :
    ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 1) (hj : j ≤ 4) (hk : k ≤ 1)
    (h41a : ∀ (t u : F), ⁅⸨β2ψ, 2 * i + k, t⸩, ⸨αβ2ψ, j, u⸩⁆ = 1)
    (h41b : ∀ (t u : F), ⁅⸨βψ, i + k, t⸩, ⸨αβ2ψ, j, u⸩⁆ = 1),
    ∀ (t u v : F), ⁅⸨ψ, i, t⸩, ⁅⸨αβ2ψ, j, u⸩, ⸨β, k, v⸩⁆⁆ = 1 := by
  intro i j k hi hj hk h41a h41b t u v
  have h₁ := fun t' u' ↦ triv_comm_iff_commutes.1 (h41a t' u')
  have h₂ := fun t' u' ↦ triv_comm_iff_commutes.1 (h41b t' u')
  apply triv_comm_iff_commutes.2
  -- expand the commutator (work on LHS)
  rw [commutatorElement_def, inv_of_αβ2ψ Fchar hj, inv_of_β]
  -- move the ψ element fully to the right
  grw [expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar, expr_ψ_β_as_β_βψ_β2ψ_ψ hk hi, expr_ψ_αβ2ψ_as_αβ2ψ_ψ Fchar, expr_ψ_β_as_β2ψ_βψ_β_ψ hk hi]
  -- use assumptions to cancel stuff
  rw [eq_of_deg_eq β2ψ (2 * i + k) (by ht), mul_assoc ⸨βψ, k + i, -(v * t)⸩, h₁]
  nth_rewrite 2 [eq_of_deg_eq β2ψ (2 * i + k) (by ht)]
  grw [rfl]
  rw [eq_of_deg_eq βψ (i + k) (by ht), h₂]
  nth_rewrite 2 [eq_of_deg_eq βψ (i + k) (by ht)]
  chev_simp

-- 8.164
include Fchar
theorem partial_comm_of_ψ_αβ2ψ_β :
  ∀ (t u v : F), ⁅⸨ψ, 1, v⸩, ⁅⸨αβ2ψ, 1, t⸩, ⸨β, 0, u⸩⁆⁆ = 1 := by
  intro t u v
  have := @sufficient_conditions_for_comm_of_ψ_and_αβ2ψ_β F _ Fchar 1 1 0 (by norm_num) (by norm_num) (by norm_num)
  norm_num at this
  apply this
  exact @partial_comm_of_β2ψ_αβ2ψ_a F _ Fchar
  have := @hom_lift_of_comm_βψ_αβ2ψ F _ Fchar 0 1 0 (by norm_num) (by norm_num) (by norm_num)
  norm_num at this
  exact this

-- 8.165
theorem partial_B_interchange_of_α2β2ψ :
  ∀ (t u v : F), ⁅⸨αβψ, 0, t⸩, ⸨βψ, 1, u * v⸩⁆ = ⁅⸨αβ2ψ, 1, 2 * t * u⸩, ⸨β, 0, v⸩⁆ := by
  have h := @hom_lift_of_inv_doub_of_β_αβ2ψ F _ Fchar 1 0 0 (by norm_num) (by norm_num) (by norm_num)
  norm_num at h
  have := @more_sufficient_conditions_for_comm_of_αβψ_and_βψ F _ Fchar 0 1 0 (by norm_num) (by norm_num) (by norm_num)
  norm_num at this
  apply this
  · intro t u v
    have h1 := @hom_lift_of_interchange_of_α2β2ψ_a F _ Fchar 1 0 0 (by norm_num) (by norm_num) (by norm_num) u (1/2) v
    have h2 := @hom_lift_of_interchange_of_α2β2ψ_b F _ Fchar 1 0 0 (by norm_num) (by norm_num) (by norm_num) (u/2) 1 v
    norm_num at h1; norm_num at h2; field_simp at h1; field_simp at h2
    rw [h2] at h1
    have := @comm_of_β_αβ_β2ψ F _ 0 1 0 (by norm_num) (by norm_num) (by norm_num) t u v
    rw [h1] at this
    exact this
  · intro t u v
    have := @partial_comm_of_ψ_αβ2ψ_β F _ Fchar u v t
    exact this
  · intro t u
    nth_rw 2 [← comm_swap]
    rw [← inv_inj, inv_inv]
    apply Eq.symm
    apply eq_inv_iff_mul_eq_one.mpr
    rcases h (-u) (-t) with ⟨h1, ⟨h2, _⟩⟩
    norm_num at h1; norm_num at h2
    rw [← h1]
    exact h2
  · intro t u
    rcases h (-u) t with ⟨h1, ⟨h2, h3⟩⟩
    norm_num at h1
    apply mul_eq_one_iff_eq_inv.mp at h2
    simp only [neg_neg, commutatorElement_inv] at h2
    grw [← h2, h3]
    rcases h (-2*u) t with ⟨_, ⟨h4, _⟩⟩
    apply mul_eq_one_iff_eq_inv.mp at h4
    simp only [neg_neg, commutatorElement_inv] at h4
    norm_num at h4
    rw [h4]
    have h5 := @hom_lift_of_interchange_of_α2β2ψ_b F _ Fchar 1 0 0 (by norm_num) (by norm_num) (by norm_num)
    norm_num at h5
    have h5a := h5 t 1 u; norm_num at h5a
    have h5b := h5 (t) (1/2) (2*u); field_simp at h5b;
    rw [←h5a, ←h5b]

-- 8.166
theorem sufficient_conditions_for_comm_of_αβ_and_β2ψ :
    ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 2) (hj : j ≤ 1) (hk : k ≤ 2)
    (h42a : ∀ (t u : F), ⁅⸨αβ2ψ, i + 2 * j, t⸩, ⸨βψ, k, u⸩⁆ = 1)
    (h42b : ∀ (t u v : F), ⁅⸨ψ, j, t⸩, ⁅⸨αβψ, i + j, u⸩, ⸨βψ, k, v⸩⁆⁆ = 1),
    ∀ (t u v : F), ⁅⸨αβ, i, t⸩, ⸨β2ψ, j + k, 2 * u * v⸩⁆ = ⁅⸨αβψ, i + j, t * u⸩, ⸨βψ, k, v⸩⁆ := by
  intro i j k hi hj hk h42a h42b t u v
  have h₁ := fun t u ↦ triv_comm_iff_commutes.1 (h42a t u)
  have h₂ := fun t u v ↦ triv_comm_iff_commutes.1 (h42b t u v)
  apply eq_comm_of_reorder_left
  -- expand β2ψ element as product of βψ and ψ elements
  rw [expr_β2ψ_as_ψ_βψ_ψ_βψ hj hk]
  -- move αβ element fully to the right
  grw [expr_αβ_ψ_as_ψ_αβψ_αβ2ψ_αβ Fchar hi hj, expr_αβ_βψ_as_βψ_αβ hi hk,
  expr_αβ_ψ_as_αβ2ψ_αβψ_ψ_αβ Fchar hi hj, expr_αβ_βψ_as_βψ_αβ hi hk]
  -- by h₁, commute αβ2ψ elements together and cancel them
  grw [h₁ (-(t * u * u))]
  rw [←inv_of_αβ2ψ Fchar (by ht)]
  grw [rfl, comm_left ⸨αβψ, i + j, t * u⸩, ← inv_of_αβψ (by ht), h₂]

-- 8.167
include Fchar
theorem sufficient_conditions_for_comm_of_αβ2ψ_and_βψ :
  ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 4) (hj : j ≤ 1) (hk : k ≤ 1)
  (h44a : ∀ (t u v : F), ⁅⁅⸨αβ2ψ, i, t⸩, ⸨β, j, u⸩⁆, ⸨ψ, k, v⸩⁆ = 1)
  (h44b : ∀ (t u : F), ⁅⸨β, j, -u⸩, ⸨αβ2ψ, i, t⸩⁆ = ⁅⸨αβ2ψ, i, t⸩, ⸨β, j, u⸩⁆)
  (h44c : ∀ (t u : F), ⁅⸨αβ2ψ, i, t⸩, ⸨β, j, u⸩⁆ * ⁅⸨αβ2ψ, i, -t⸩, ⸨β, j, u⸩⁆ = 1),
  ∀ (t u : F), ⁅⸨αβ2ψ, i, t⸩, ⸨βψ, j + k, u⸩⁆ = 1 := by
  intro i j k hi hj hk h44a h44b h44c t u
  have := inv_of_αβ2ψ Fchar (by exact hi) (-t); rw [neg_neg] at this
  have eq45 := calc ⸨αβ2ψ, i, t⸩ * ⸨β, j, u⸩
    _ = ⸨β, j, u⸩ * ⁅⸨β, j, -u⸩, ⸨αβ2ψ, i, t⸩⁆ * ⸨αβ2ψ, i, t⸩ := by
      rw [comm_mid_rev, inv_of_β]
    _ = ⸨β, j, u⸩ * ⁅⸨αβ2ψ, i, t⸩, ⸨β, j, u⸩⁆ * ⸨αβ2ψ, i, t⸩ := by
      rw [h44b t u]
  have eq46 := calc ⸨αβ2ψ, i, t⸩ * ⸨β, j, -u⸩
    _ = ⁅⸨αβ2ψ, i, t⸩, ⸨β, j, -u⸩⁆ * ⸨β, j, -u⸩ * ⸨αβ2ψ, i, t⸩ := by
      apply comm_left
  have h44d : ∀ t u, ⁅⸨αβ2ψ, i, -t⸩, ⸨β, j, u⸩⁆ * ⁅⸨αβ2ψ, i, t⸩, ⸨β, j, u⸩⁆ = 1 := by
    intro t u
    have := h44c (-t) (u)
    norm_num at this
    exact this
  have h := expr_βψ_as_ψ_β_ψ_β_ψ Fchar (i := k) (j := j) (by ht) hj 1 u
  norm_num at h; rw [eq_of_deg_eq βψ (j + k)] at h
  have := calc ⸨αβ2ψ, i, t⸩ * ⸨βψ, j + k, u⸩
    _ = ⸨αβ2ψ, i, t⸩ * ⸨ψ, k, -1/2⸩ * ⸨β, j, u⸩ * ⸨ψ, k, 1⸩ * ⸨β, j, -u⸩ * ⸨ψ, k, -1/2⸩ := by
      grw [h]
    _ = ⸨ψ, k, -1/2⸩ * ⸨β, j, u⸩ * ⁅⸨αβ2ψ, i, t⸩, ⸨β, j, u⸩⁆ * ⸨ψ, k, 1⸩ * ⁅⸨αβ2ψ, i, -t⸩, ⸨β, j, u⸩⁆ * ⸨β, j, -u⸩ * ⸨ψ, k, -1/2⸩ * ⸨αβ2ψ, i, t⸩ := by
      have h1 : ∀ u, ⸨ψ, k, u⸩ * ⸨αβ2ψ, i, t⸩ = ⸨αβ2ψ, i, t⸩ * ⸨ψ, k, u⸩ := by
        intro u
        rw [triv_comm_iff_commutes.mp]
        apply comm_of_ψ_αβ2ψ Fchar
      have := calc ⸨αβ2ψ, i, t⸩ * ⁅⸨αβ2ψ, i, -t⸩, ⸨β, j, u⸩⁆
        _ = ⸨αβ2ψ, i, t⸩ * ⁅⸨β, j, -u⸩, ⸨αβ2ψ, i, -t⸩⁆ := by rw [(h44b (-t) (u))]
        _ = ⸨αβ2ψ, i, t⸩ * ⸨β, j, -u⸩ * ⸨αβ2ψ, i, -t⸩ * ⸨β, j, u⸩ * ⸨αβ2ψ, i, t⸩ := by
          grw [commutatorElement_def, inv_of_αβ2ψ Fchar (by ht)]
        _ = ⁅⸨αβ2ψ, i, t⸩, ⸨β, j, -u⸩⁆ * ⸨αβ2ψ, i, t⸩ := by
          grw [commutatorElement_def, inv_of_αβ2ψ Fchar (by ht)]
      grw [← h1, eq45, ← h1, eq46, ← h1]
      nth_rw 2 [← comm_swap]
      apply mul_eq_one_iff_eq_inv.mp
      have := h44b (-t) (-u)
      norm_num at this
      grw [this]
      have := h44d (-t) (-u)
      norm_num at this
      exact this
    _ = ⸨ψ, k, -1/2⸩ * ⸨β, j, u⸩ * ⸨ψ, k, 1⸩ * ⸨β, j, -u⸩ * ⸨ψ, k, -1/2⸩ * ⸨αβ2ψ, i, t⸩ := by
      have := fun t u v ↦ (triv_comm_iff_commutes.mp (h44a t u v))
      grw [this, this, h44c]
    _ = ⸨βψ, j + k, u⸩ * ⸨αβ2ψ, i, t⸩ := by
      grw [← h]
  exact triv_comm_iff_commutes.mpr this
  exact Nat.add_comm k j

private lemma partial_comm_of_βψ_αβ2ψ_help : ∀ t u : F,
    ⁅⸨αβ2ψ, 2, t⸩, ⸨β, 0, u⸩⁆ = ⁅⸨αβ, 1, t⸩, ⸨β2ψ, 1, u⸩⁆ := by
  intro t u
  have : t = 2 * t * (1 / 2) := by field_simp
  rw [this, ←@hom_lift_of_interchange_of_α2β2ψ_b F _ Fchar 0 0 1 (by trivial) (by trivial) (by trivial),
    ←mul_one t, ←@hom_lift_of_interchange_of_α2β2ψ_a F _ Fchar 0 1 0 (by trivial) (by trivial) (by trivial)]
  field_simp

private lemma partial_comm_of_βψ_αβ2ψ_help' : ∀ t u : F,
    ⁅⸨β, 0, u⸩, ⸨αβ2ψ, 2, t⸩⁆ = ⁅⸨β2ψ, 1, u⸩, ⸨αβ, 1, t⸩⁆ := by
  intro t u
  apply inv_inj.1
  rw [comm_swap, comm_swap]
  apply partial_comm_of_βψ_αβ2ψ_help Fchar

-- 8.168
theorem partial_comm_of_βψ_αβ2ψ :
  ∀ (t u : F), ⁅⸨αβ2ψ, 2, t⸩, ⸨βψ, 0, u⸩⁆ = 1 := by
  apply @sufficient_conditions_for_comm_of_αβ2ψ_and_βψ F _ Fchar 2 0 0 (by trivial) (by trivial) (by trivial)
  · intro t u v
    rw [partial_comm_of_βψ_αβ2ψ_help Fchar, triv_comm_symm, @hom_lift_of_comm_ψ_αβ_β2ψ F _ 0 1 0 (by trivial) (by trivial) (by trivial)]
  · intro t u
    rw [partial_comm_of_βψ_αβ2ψ_help Fchar, partial_comm_of_βψ_αβ2ψ_help' Fchar]
    apply (mul_left_inj (⁅⸨β2ψ, 1, -u⸩, ⸨αβ, 1, t⸩⁆⁻¹)).1
    rw [mul_inv_cancel, comm_swap, (@hom_lift_of_inv_doub_of_αβ_β2ψ F _ 0 1 0 (by trivial) (by trivial) (by trivial) t u).1]
    nth_rewrite 2 [←neg_neg t]
    rw [(@hom_lift_of_inv_doub_of_αβ_β2ψ F _ 0 1 0 (by trivial) (by trivial) (by trivial) (-t) (-u)).2.1]
  · intro t u
    rw [partial_comm_of_βψ_αβ2ψ_help Fchar, partial_comm_of_βψ_αβ2ψ_help Fchar,
    (@hom_lift_of_inv_doub_of_αβ_β2ψ F _ 0 1 0 (by trivial) (by trivial) (by trivial) t u).2.1]

-- 8.169a
theorem partial_C_interchange_of_α2β2ψ_a :
  ∀ (t u v : F), ⁅⸨αβ, 0, t⸩, ⸨β2ψ, 1, 2 * u * v⸩⁆ = ⁅⸨αβψ, 1, t * u⸩, ⸨βψ, 0, v⸩⁆ := by
  apply @sufficient_conditions_for_comm_of_αβ_and_β2ψ F _ Fchar 0 1 0 (by trivial) (by trivial) (by trivial)
  · exact @partial_comm_of_βψ_αβ2ψ F _ Fchar
  intro t u v
  have := @hom_lift_of_interchange_of_α2β2ψ_b F _ Fchar 1 0 0 (by trivial) (by trivial) (by trivial) u 1 v
  norm_num at this;
  grw [this, partial_comm_of_ψ_αβ2ψ_β Fchar]

-- 8.169b
theorem partial_C_interchange_of_α2β2ψ_b :
  ∀ (t u v : F), ⁅⸨αβ, 2, t⸩, ⸨β2ψ, 0, 2 * u * v⸩⁆ = ⁅⸨αβψ, 2, t * u⸩, ⸨βψ, 0, v⸩⁆ := by
  apply @sufficient_conditions_for_comm_of_αβ_and_β2ψ F _ Fchar 2 0 0 (by trivial) (by trivial) (by trivial)
  · exact @partial_comm_of_βψ_αβ2ψ F _ Fchar
  intro t u v
  rw [←one_mul u, partial_A_interchange_of_α2β2ψ_b Fchar,
  @hom_lift_of_comm_ψ_αβ_β2ψ F _ 0 1 0 (by trivial) (by trivial) (by trivial)]

-- 8.170
theorem sufficient_conditions_for_comm_of_αβ2ψ_and_β :
  ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 3) (hj : j ≤ 1) (hk : k ≤ 1)
  (h47a : ∀ (t u : F), ⁅⸨αβψ, i, t⸩, ⸨β2ψ, 2 * j + k, u⸩⁆ = 1)
  (h47b : ∀ (t u v : F), ⁅⁅⸨αβψ, i, t⸩, ⸨βψ, j + k, u⸩⁆, ⸨ψ, j, v⸩⁆ = 1)
  (h47c : ∀ (t u : F), ⁅⸨βψ, j + k, -u⸩, ⸨αβψ, i, t⸩⁆ = ⁅⸨αβψ, i, t⸩, ⸨βψ, j + k, u⸩⁆),
  ∀ (t u v : F), ⁅⸨αβ2ψ, i + j, t * u⸩, ⸨β, k, 2 * v⸩⁆ = ⁅⸨αβψ, i, t⸩, ⸨βψ, j + k, u * v⸩⁆ := by
  intro i j k hi hj hk hyp₁ hyp₂ hyp₃ t u v
  have h₁ := fun t u ↦ triv_comm_iff_commutes.1 (hyp₁ t u)
  have h₂ := fun t u v ↦ triv_comm_iff_commutes.1 (hyp₂ t u v)
  apply eq_comm_of_reorder_left
  -- expand αβ2ψ as product of αβψ and ψ elements
  rw [eq_of_coef_eq αβ2ψ (-2 * (-u/2) * t) (by ring_nf; field_simp), expr_αβ2ψ_as_ψ_αβψ_ψ_αβψ Fchar hi hj]
  -- commute β fully to the left
  grw [←expr_β_αβψ_as_αβψ_β, expr_ψ_β_as_β_β2ψ_βψ_ψ hk hj, ←expr_β_αβψ_as_αβψ_β, expr_ψ_β_as_β_ψ_βψ_β2ψ hk hj]
  -- by hyp₁, commute the β2ψ elements across αβψ and cancel them
  rw [eq_of_deg_eq β2ψ (2 * j + k) (by ht), eq_of_coef_eq βψ (-v * u) (by ring_nf; field_simp),
  eq_of_coef_eq β2ψ (v * u^2 / 2) (by ring_nf; rw [pow_two (2⁻¹), mul_assoc]; field_simp)]
  grw [←h₁ _ (v * u^2 / 2)]
  nth_rewrite 2 [eq_of_coef_eq β2ψ (-(v * u^2 / 2)) (by ring_nf; field_simp; group),
  eq_of_deg_eq β2ψ (2 * j + k) (by ht)]
  grw [rfl]
  -- commute the two βψ elements together, creating a generic commutator (using hyp₃)
  grw [comm_left (⸨βψ, k + j, -(v * u)⸩) (⸨αβψ, i, t⸩)]
  rw [eq_of_deg_eq βψ (j + k) (by ht), eq_of_coef_eq βψ (-(v * u)) (by ring_nf)]
  grw [hyp₃]
  -- commute ψ and ⁅αβψ, βψ⁆ by h₂
  grw [←h₂ t]
  -- commute β and ⁅αβψ, βψ⁆ by relation 8.157
  have := triv_comm_iff_commutes.1 (comm_of_β_αβψ_βψ (i := k) (j := i) (k := j + k)
  (t := 2 * v) (u := t) (v := u * v) (by trivial) (by trivial) (by ht))
  grw [←this, mul_comm u v]
  rw [eq_of_coef_eq βψ 0 (by ring_nf; field_simp), id_of_βψ, mul_one]

-- 8.171
theorem sufficient_conditions_for_comm_of_αβψ_and_β2ψ :
    ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 1) (hj : j ≤ 2) (hk : k ≤ 3)
    (hyp : ∀ (t u : F), ⁅⸨αβ2ψ, i + k, u⸩, ⸨βψ, j, t⸩⁆ = 1),
    ∀ (t u : F), ⁅⸨αβψ, i + j, t⸩, ⸨β2ψ, k, u⸩⁆ = 1 := by
  intro i j k hi hj hk hyp t u
  have hyp' := fun t u ↦ triv_comm_iff_commutes.1 (hyp t u)
  apply triv_comm_iff_commutes.2
  -- expand αβψ element as product of α and βψ elements (working on LHS)
  rw [←one_mul t, expr_αβψ_as_βψ_α_βψ_α_βψ hi hj]
  -- move β2ψ element from the right fully to the left
  grw [expr_βψ_β2ψ_as_β2ψ_βψ, expr_α_β2ψ_as_β2ψ_αβ2ψ_α Fchar hi hk, expr_βψ_β2ψ_as_β2ψ_βψ,
  expr_α_β2ψ_as_β2ψ_α_αβ2ψ Fchar hi hk, expr_βψ_β2ψ_as_β2ψ_βψ]
  -- commute αβ2ψ element across the βψ element and cancel
  rw [hyp', ←inv_of_αβ2ψ Fchar (by ht)]
  group

-- 8.172
theorem partial_comm_of_αβψ_β2ψ :
    ∀ (t u : F), ⁅⸨αβψ, 0, t⸩, ⸨β2ψ, 1, u⸩⁆ = 1 := by
  apply sufficient_conditions_for_comm_of_αβψ_and_β2ψ (i := 0) (j := 0) (k := 1) (by trivial) (by trivial) (by trivial) (by trivial)
  intro t u
  rw [eq_of_deg_eq αβ2ψ 1 rfl, ←one_mul u, expr_αβ2ψ_as_comm_of_α_β2ψ (i := 1) (j := 0) Fchar (by trivial) (by trivial)]
  apply triv_comm_symm.1
  rw [lift_hom_comm_of_βψ_α_β2ψ (i := 1) (j := 0) (k := 0) (by trivial) (by trivial) (by trivial)]

private lemma partial_D_interchange_of_α2β2ψ_help : ∀ t u : F,
    ⁅⸨αβψ, 0, t⸩, ⸨βψ, 1, u⸩⁆ = ⁅⸨αβ, 1, t⸩, ⸨β2ψ, 0, 2 * u⸩⁆ := by
  intro t u
  rw [←mul_one u, partial_B_interchange_of_α2β2ψ Fchar,
  ←hom_lift_of_interchange_of_α2β2ψ_b (i := 1) (j := 0) (k := 0) Fchar (by trivial) (by trivial) (by trivial),
  mul_one, ←mul_one t, ←hom_lift_of_interchange_of_α2β2ψ_a Fchar (by trivial) (by trivial) (by trivial)]
  simp only [add_zero, mul_zero, mul_one]

-- 8.173
theorem partial_D_interchange_of_α2β2ψ :
  ∀ (t u v : F), ⁅⸨αβψ, 0, t⸩, ⸨βψ, 1, u * v⸩⁆ = ⁅⸨αβ2ψ, 0, t * u⸩, ⸨β, 1, 2 * v⸩⁆ := by
  intro _ _ _
  apply symm
  apply @sufficient_conditions_for_comm_of_αβ2ψ_and_β F _ Fchar 0 0 1 (by trivial) (by trivial) (by trivial)
  · exact partial_comm_of_αβψ_β2ψ Fchar
  · intro t u v
    rw [partial_D_interchange_of_α2β2ψ_help Fchar, triv_comm_symm,
    hom_lift_of_comm_ψ_αβ_β2ψ (i := 1) (j := 0) (k := 0) (by trivial) (by trivial) (by trivial)]
  · intro t u
    apply (mul_right_inj (⁅⸨βψ, 0 + 1, -u⸩, ⸨αβψ, 0, t⸩⁆⁻¹)).1
    rw [inv_mul_cancel, comm_swap, partial_D_interchange_of_α2β2ψ_help Fchar,
    partial_D_interchange_of_α2β2ψ_help Fchar, eq_of_coef_eq β2ψ (-(2 * u)) (by ring),
    (hom_lift_of_inv_doub_of_αβ_β2ψ (i := 1) (j := 0) (k := 0) (by trivial) (by trivial) (by trivial) t (-(2 * u))).1,
    neg_neg]
    nth_rewrite 2 [←neg_neg t]
    rw [(hom_lift_of_inv_doub_of_αβ_β2ψ (i := 1) (j := 0) (k := 0) (by trivial) (by trivial) (by trivial) (-t) (2 * u)).2.1]


/- ### Establishing α + 2β + 2ψ -/

private lemma interchange_of_α2β2ψ_refl_u_αβ_β2ψ :
  forall_ijk_tu 1 1 1, ⁅⸨αβ, i + j, t⸩, ⸨β2ψ, j + 2 * k, 2 * u⸩⁆ = ⁅⸨αβψ, i + j + k, t⸩, ⸨βψ, j + k, u⸩⁆ := by
  intro i j k hi hj hk t u
  rw [←one_mul u, ←mul_assoc, hom_lift_of_interchange_of_α2β2ψ_a Fchar hi hj hk t, mul_one, one_mul]

private lemma interchange_of_α2β2ψ_refl_v_αβ_β2ψ :
  forall_ijk_tu 1 1 1, ⁅⸨αβ, i + j, t⸩, ⸨β2ψ, j + 2 * k, 2 * u⸩⁆ = ⁅⸨αβψ, i + j + k, t * u⸩, ⸨βψ, j + k, 1⸩⁆ := by
  intro i j k hi hj hk t u
  rw [←mul_one (2 * u), hom_lift_of_interchange_of_α2β2ψ_a Fchar hi hj hk t]

private lemma interchange_of_α2β2ψ_refl_u_αβψ_βψ :
  forall_ijk_tu 1 1 1, ⁅⸨αβψ, i + j + k, t⸩, ⸨βψ, j + k, u/2⸩⁆ = ⁅⸨αβ2ψ, i + j + 2 * k, t⸩, ⸨β, j, u⸩⁆ := by
  intro i j k hi hj hk t u
  have : u/2 = (1/2) * u := by ring
  rw [this, hom_lift_of_interchange_of_α2β2ψ_b Fchar hi hj hk]
  field_simp

private lemma interchange_of_α2β2ψ_trans_αβψ_βψ :
  forall_ijk_tu 1 1 1, ⁅⸨αβψ, i + j + k, t * u⸩, ⸨βψ, j + k, 1⸩⁆ = ⁅⸨αβψ, i + j + k, t⸩, ⸨βψ, j + k, u⸩⁆ := by
  intro i j k hi hj hk t u
  rw [←interchange_of_α2β2ψ_refl_v_αβ_β2ψ Fchar hi hj hk, ←interchange_of_α2β2ψ_refl_u_αβ_β2ψ Fchar hi hj hk]

private lemma interchange_of_α2β2ψ_trans_αβ_β2ψ :
  forall_ijk_tu 1 1 1, ⁅⸨αβ, i + j, t * u⸩, ⸨β2ψ, j + 2 * k, 1⸩⁆ = ⁅⸨αβ, i + j, t⸩, ⸨β2ψ, j + 2 * k, u⸩⁆ := by
  intro i j k hi hj hk t u
  have aux₁ := hom_lift_of_interchange_of_α2β2ψ_a Fchar hi hj hk t (u/2) 1
  have aux₂ := hom_lift_of_interchange_of_α2β2ψ_a Fchar hi hj hk (t * u) (1 / 2) 1
  field_simp at aux₁
  field_simp at aux₂
  rwa [←aux₁] at aux₂

private lemma interchange_A_of_α2β2ψ_refl_u :
  ∀ t u : F, ⁅⸨αβ, 1, t⸩, ⸨β2ψ, 1, 2 * u⸩⁆ = ⁅⸨αβψ, 2, t⸩, ⸨βψ, 0, u⸩⁆ := by
  intro t u
  rw [←one_mul u, ←mul_assoc, ←partial_A_interchange_of_α2β2ψ_b Fchar]
  simp only [mul_one, one_mul]

private lemma interchange_A_of_α2β2ψ_refl_u' :
  ∀ t u : F, ⁅⸨αβ, 0, t⸩, ⸨β2ψ, 2, 2 * u⸩⁆ = ⁅⸨αβψ, 0, t⸩, ⸨βψ, 2, u⸩⁆ := by
  intro t u
  rw [←one_mul u, ←mul_assoc, ←partial_A_interchange_of_α2β2ψ_a Fchar]
  simp only [mul_one, one_mul]

private lemma interchange_B_of_α2β2ψ_refl_u_αβψ_βψ :
  ∀ t u : F, ⁅⸨αβψ, 0, t⸩, ⸨βψ, 1, u/2⸩⁆ = ⁅⸨αβ2ψ, 1, t⸩, ⸨β, 0, u⸩⁆ := by
  intro t u
  have : u/2 = (1/2) * u := by ring
  rw [this, partial_B_interchange_of_α2β2ψ Fchar]
  field_simp

private lemma interchange_C_refl_u :
  ∀ t u : F, ⁅⸨αβ, 0, t⸩, ⸨β2ψ, 1, 2 * u⸩⁆ = ⁅⸨αβψ, 1, t⸩, ⸨βψ, 0, u⸩⁆ := by
  intro t u
  rw [←one_mul u, ←mul_assoc, partial_C_interchange_of_α2β2ψ_a Fchar]
  simp only [mul_one, one_mul]

private lemma interchange_C_refl_u' :
  ∀ t u : F, ⁅⸨αβ, 2, t⸩, ⸨β2ψ, 0, 2 * u⸩⁆ = ⁅⸨αβψ, 2, t⸩, ⸨βψ, 0, u⸩⁆ := by
  intro t u
  rw [←one_mul u, ←mul_assoc, partial_C_interchange_of_α2β2ψ_b Fchar]
  simp only [mul_one, one_mul]

private lemma interchange_C_refl_v :
  ∀ t u : F, ⁅⸨αβ, 0, t⸩, ⸨β2ψ, 1, 2 * u⸩⁆ = ⁅⸨αβψ, 1, t * u⸩, ⸨βψ, 0, 1⸩⁆ := by
  intro t u
  rw [←mul_one u, ←mul_assoc, partial_C_interchange_of_α2β2ψ_a Fchar]
  simp only [mul_one]

private lemma interchange_C_of_α2β2ψ_trans_αβψ_βψ :
  ∀ t u : F, ⁅⸨αβψ, 1, t * u⸩, ⸨βψ, 0, 1⸩⁆ = ⁅⸨αβψ, 1, t⸩, ⸨βψ, 0, u⸩⁆ := by
  intro t u
  rw [←interchange_C_refl_v Fchar, ←interchange_C_refl_u Fchar]

private lemma interchange_C_of_α2β2ψ_trans_αβ_β2ψ :
  ∀ t u : F, ⁅⸨αβ, 0, t * u⸩, ⸨β2ψ, 1, 1⸩⁆ = ⁅⸨αβ, 0, t⸩, ⸨β2ψ, 1, u⸩⁆ := by
  intro t u
  have aux₁ := partial_C_interchange_of_α2β2ψ_a Fchar t u (1 / 2)
  have aux₂ := partial_C_interchange_of_α2β2ψ_a Fchar (t * u) 1 (1 / 2)
  field_simp at aux₁
  field_simp at aux₂
  rwa [←aux₁] at aux₂

private lemma interchange_D_refl_u :
  ∀ t u : F, ⁅⸨αβψ, 0, t⸩, ⸨βψ, 1, u⸩⁆ = ⁅⸨αβ2ψ, 0, t⸩, ⸨β, 1, 2 * u⸩⁆ := by
  intro t u
  rw [←one_mul u, partial_D_interchange_of_α2β2ψ Fchar]
  simp only [mul_one, one_mul]

-- height 0
private lemma expr_α2β2ψ_as_comm_of_αβ_β2ψ_00 :
  ∀ t u : F, ⸨α2β2ψ, 0, -t * u⸩ = ⁅⸨αβ, 0, t⸩, ⸨β2ψ, 0, u⸩⁆:= by
  intro t u
  have := @def_of_α2β2ψ _ _ 0 (by trivial) (t * u)
  unfold split_5_into_2_3 at this
  simp only at this
  rw [neg_mul, ←this, @interchange_of_α2β2ψ_trans_αβ_β2ψ _ _ Fchar 0 0 0 (by trivial) (by trivial) (by trivial)]

private lemma expr_α2β2ψ_as_comm_of_αβψ_βψ_00 :
  ∀ t u : F, ⸨α2β2ψ, 0, -2 * t * u⸩ = ⁅⸨αβψ, 0, t⸩, ⸨βψ, 0, u⸩⁆ := by
  intro t u
  have : -2 * t * u = -t * (2 * u) := by ring
  rw [this, expr_α2β2ψ_as_comm_of_αβ_β2ψ_00 Fchar, @interchange_of_α2β2ψ_refl_v_αβ_β2ψ _ _ Fchar 0 0 0 (by trivial) (by trivial) (by trivial),
  interchange_of_α2β2ψ_trans_αβψ_βψ Fchar (by trivial) (by trivial) (by trivial)]

private lemma expr_α2β2ψ_as_comm_of_αβ2ψ_β_00 :
  ∀ t u : F, ⸨α2β2ψ, 0, -t * u⸩ = ⁅⸨αβ2ψ, 0, t⸩, ⸨β, 0, u⸩⁆ := by
  intro t u
  have : -t * u = -2 * t * (u/2) := by ring_nf; field_simp
  rw [this, expr_α2β2ψ_as_comm_of_αβψ_βψ_00 Fchar, @interchange_of_α2β2ψ_refl_u_αβψ_βψ _ _ Fchar 0 0 0 (by trivial) (by trivial) (by trivial)]

-- height 1
private lemma expr_α2β2ψ_as_comm_of_αβ_β2ψ_01 :
  ∀ t u : F, ⸨α2β2ψ, 1, -t * u⸩ = ⁅⸨αβ, 0, t⸩, ⸨β2ψ, 1, u⸩⁆:= by
  intro t u
  have := @def_of_α2β2ψ _ _ 1 (by trivial) (t * u)
  unfold split_5_into_2_3 at this
  rw [neg_mul, ←this, interchange_C_of_α2β2ψ_trans_αβ_β2ψ Fchar]

private lemma expr_α2β2ψ_as_comm_of_αβψ_βψ_10 :
  ∀ t u : F, ⸨α2β2ψ, 1, -2 * t * u⸩ = ⁅⸨αβψ, 1, t⸩, ⸨βψ, 0, u⸩⁆ := by
  intro t u
  have : -2 * t * u = -t * (2 * u) := by ring
  rw [this, expr_α2β2ψ_as_comm_of_αβ_β2ψ_01 Fchar, interchange_C_refl_v Fchar,
  interchange_C_of_α2β2ψ_trans_αβψ_βψ Fchar]

private lemma expr_α2β2ψ_as_comm_of_αβ_β2ψ_10 :
  ∀ t u : F, ⸨α2β2ψ, 1, -t * u⸩ = ⁅⸨αβ, 1, t⸩, ⸨β2ψ, 0, u⸩⁆:= by
  intro t u
  have : -t * u = -2 * t * (u/2) := by ring_nf; field_simp
  rw [this, expr_α2β2ψ_as_comm_of_αβψ_βψ_10 Fchar, ←@interchange_of_α2β2ψ_refl_u_αβ_β2ψ _ _ Fchar 1 0 0 (by trivial) (by trivial) (by trivial)]
  field_simp

private lemma expr_α2β2ψ_as_comm_of_αβ2ψ_β_10
    : ∀ (t u : F), ⸨α2β2ψ, 1, -t * u⸩ = ⁅⸨αβ2ψ, 1, t⸩, ⸨β, 0, u⸩⁆ := by
  intro t u
  have : -t * u = -2 * t * (u/2) := by ring_nf; field_simp
  rw [this, expr_α2β2ψ_as_comm_of_αβψ_βψ_10 Fchar, @interchange_of_α2β2ψ_refl_u_αβψ_βψ _ _ Fchar 1 0 0 (by trivial) (by trivial) (by trivial)]

-- `B` edge
private lemma expr_α2β2ψ_as_comm_of_αβψ_βψ_01
    : ∀ (t u : F), ⸨α2β2ψ, 1, -2 * t * u⸩ = ⁅⸨αβψ, 0, t⸩, ⸨βψ, 1, u⸩⁆ := by
  intro t u
  have : -2 * t * u = -t * (2 * u) := by ring
  rw [this, expr_α2β2ψ_as_comm_of_αβ2ψ_β_10 Fchar, ←interchange_B_of_α2β2ψ_refl_u_αβψ_βψ Fchar]
  field_simp

-- `D` edge
private lemma expr_α2β2ψ_as_comm_of_αβ2ψ_β_01
    : ∀ (t u : F), ⸨α2β2ψ, 1, -t * u⸩ = ⁅⸨αβ2ψ, 0, t⸩, ⸨β, 1, u⸩⁆ := by
  intro t u
  have : -t * u = -2 * t * (u/2) := by ring_nf; field_simp
  rw [this, expr_α2β2ψ_as_comm_of_αβψ_βψ_01 Fchar, interchange_D_refl_u Fchar]
  field_simp

-- height 2
private lemma expr_α2β2ψ_as_comm_of_αβ_β2ψ_11 :
  ∀ t u : F, ⸨α2β2ψ, 2, -t * u⸩ = ⁅⸨αβ, 1, t⸩, ⸨β2ψ, 1, u⸩⁆:= by
  intro t u
  have := @def_of_α2β2ψ _ _ 2 (by trivial) (t * u)
  unfold split_5_into_2_3 at this
  rw [neg_mul, ←this, @interchange_of_α2β2ψ_trans_αβ_β2ψ _ _ Fchar 0 1 0 (by trivial) (by trivial) (by trivial)]

-- `A` edge
private lemma expr_α2β2ψ_as_comm_of_αβψ_βψ_20 :
  ∀ t u : F, ⸨α2β2ψ, 2, -2 * t * u⸩ = ⁅⸨αβψ, 2, t⸩, ⸨βψ, 0, u⸩⁆ := by
  intro t u
  have : -2 * t * u = -t * (2 * u) := by ring
  rw [this, expr_α2β2ψ_as_comm_of_αβ_β2ψ_11 Fchar, interchange_A_of_α2β2ψ_refl_u Fchar]

-- `C` edge
private lemma expr_α2β2ψ_as_comm_of_αβ_β2ψ_20 :
  ∀ t u : F, ⸨α2β2ψ, 2, -t * u⸩ = ⁅⸨αβ, 2, t⸩, ⸨β2ψ, 0, u⸩⁆:= by
  intro t u
  have : -t * u = -2 * t * (u/2) := by ring_nf; field_simp
  rw [this, expr_α2β2ψ_as_comm_of_αβψ_βψ_20 Fchar, ←interchange_C_refl_u' Fchar]
  field_simp

private lemma expr_α2β2ψ_as_comm_of_αβψ_βψ_11 :
  ∀ t u : F, ⸨α2β2ψ, 2, -2 * t * u⸩ = ⁅⸨αβψ, 1, t⸩, ⸨βψ, 1, u⸩⁆ := by
  intro t u
  have : -2 * t * u = -t * (2 * u) := by ring
  rw [this, expr_α2β2ψ_as_comm_of_αβ_β2ψ_11 Fchar, @interchange_of_α2β2ψ_refl_v_αβ_β2ψ _ _ Fchar 0 1 0 (by trivial) (by trivial) (by trivial),
  interchange_of_α2β2ψ_trans_αβψ_βψ Fchar (by trivial) (by trivial) (by trivial)]

private lemma expr_α2β2ψ_as_comm_of_αβ_β2ψ_02 :
  ∀ t u : F, ⸨α2β2ψ, 2, -t * u⸩ = ⁅⸨αβ, 0, t⸩, ⸨β2ψ, 2, u⸩⁆:= by
  intro t u
  have : -t * u = -2 * t * (u/2) := by ring_nf; field_simp
  rw [this, expr_α2β2ψ_as_comm_of_αβψ_βψ_11 Fchar, ←@interchange_of_α2β2ψ_refl_u_αβ_β2ψ _ _ Fchar 0 0 1 (by trivial) (by trivial) (by trivial)]
  field_simp

-- `A` edge
private lemma expr_α2β2ψ_as_comm_of_αβψ_βψ_02 :
  ∀ t u : F, ⸨α2β2ψ, 2, -2 * t * u⸩ = ⁅⸨αβψ, 0, t⸩, ⸨βψ, 2, u⸩⁆ := by
  intro t u
  have : -2 * t * u = -t * (2 * u) := by ring
  rw [this, expr_α2β2ψ_as_comm_of_αβ_β2ψ_02 Fchar, interchange_A_of_α2β2ψ_refl_u' Fchar]

private lemma expr_α2β2ψ_as_comm_of_αβ2ψ_β_20 :
  ∀ t u : F, ⸨α2β2ψ, 2, -t * u⸩ = ⁅⸨αβ2ψ, 2, t⸩, ⸨β, 0, u⸩⁆ := by
  intro t u
  have : -t * u = -2 * t * (u/2) := by ring_nf; field_simp
  rw [this, expr_α2β2ψ_as_comm_of_αβψ_βψ_11 Fchar, ←@interchange_of_α2β2ψ_refl_u_αβψ_βψ _ _ Fchar 0 0 1 (by trivial) (by trivial) (by trivial)]

private lemma expr_α2β2ψ_as_comm_of_αβ2ψ_β_11 :
  ∀ t u : F, ⸨α2β2ψ, 2, -t * u⸩ = ⁅⸨αβ2ψ, 1, t⸩, ⸨β, 1, u⸩⁆ := by
  intro t u
  have : -t * u = -2 * t * (u/2) := by ring_nf; field_simp
  rw [this, expr_α2β2ψ_as_comm_of_αβψ_βψ_11 Fchar, ←@interchange_of_α2β2ψ_refl_u_αβψ_βψ _ _ Fchar 0 1 0 (by trivial) (by trivial) (by trivial)]

-- height 3
private lemma expr_α2β2ψ_as_comm_of_αβ_β2ψ_12 :
  ∀ t u : F, ⸨α2β2ψ, 3, -t * u⸩ = ⁅⸨αβ, 1, t⸩, ⸨β2ψ, 2, u⸩⁆:= by
  intro t u
  have := @def_of_α2β2ψ _ _ 3 (by trivial) (t * u)
  unfold split_5_into_2_3 at this
  simp only at this
  rw [neg_mul, ←this, @interchange_of_α2β2ψ_trans_αβ_β2ψ _ _ Fchar 1 0 1 (by trivial) (by trivial) (by trivial)]

-- `A` edge
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβψ βψ const neg 2 heights 3 1 2 to 2 2 0

-- `C` edge
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβ β2ψ const neg 1 heights 3 0 3 to 2 2 0

private lemma expr_α2β2ψ_as_comm_of_αβψ_βψ_21 :
  ∀ t u : F, ⸨α2β2ψ, 3, -2 * t * u⸩ = ⁅⸨αβψ, 2, t⸩, ⸨βψ, 1, u⸩⁆ := by
  intro t u
  have : -2 * t * u = -t * (2 * u) := by ring
  rw [this, expr_α2β2ψ_as_comm_of_αβ_β2ψ_12 Fchar, @interchange_of_α2β2ψ_refl_v_αβ_β2ψ _ _ Fchar 1 0 1 (by trivial) (by trivial) (by trivial),
  interchange_of_α2β2ψ_trans_αβψ_βψ Fchar (by trivial) (by trivial) (by trivial)]

declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβ β2ψ const neg 1 heights 3 2 1 to 2 0 2
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβψ βψ const neg 2 heights 3 3 0 to 2 0 2
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβ2ψ β const neg 1 heights 3 3 0 to 2 1 1
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβ2ψ β const neg 1 heights 3 2 1 to 2 2 0

-- height 4
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβ β2ψ const neg 1 heights 4 2 2 to 1 0 1
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβ β2ψ const neg 1 heights 4 1 3 to 1 1 0
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβψ βψ const neg 2 heights 4 3 1 to 1 0 1
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβψ βψ const neg 2 heights 4 2 2 to 1 1 0
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβ2ψ β const neg 1 heights 4 4 0 to 1 0 1
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβ2ψ β const neg 1 heights 4 3 1 to 1 1 0

-- height 5
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβ β2ψ const neg 1 heights 5 2 3 to 0 0 0
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβψ βψ const neg 2 heights 5 3 2 to 0 0 0
declare_B3Large_reflected_thm F b3large_valid α2β2ψ αβ2ψ β const neg 1 heights 5 4 1 to 0 0 0

-- 8.174a
theorem expr_α2β2ψ_as_comm_of_αβ_β2ψ : forall_ij_tu αβ β2ψ,
    ⸨α2β2ψ, i + j, -t * u⸩ = ⁅⸨αβ, i, t⸩, ⸨β2ψ, j, u⸩⁆ := by
  intro i j hi hj t u
  match i, j with
  | 0, 0 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_00 Fchar]
  | 1, 0 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_10 Fchar]
  | 2, 0 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_20 Fchar]
  | 0, 1 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_01 Fchar]
  | 1, 1 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_11 Fchar]
  | 2, 1 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_21 Fchar]
  | 0, 2 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_02 Fchar]
  | 1, 2 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_12 Fchar]
  | 2, 2 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_22 Fchar]
  | 0, 3 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_03 Fchar]
  | 1, 3 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_13 Fchar]
  | 2, 3 => rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ_23 Fchar]

-- 8.174b
theorem expr_α2β2ψ_as_comm_of_αβψ_βψ : forall_ij_tu αβψ βψ,
    ⸨α2β2ψ, i + j, -2 * t * u⸩ = ⁅⸨αβψ, i, t⸩, ⸨βψ, j, u⸩⁆ := by
  intro i j hi hj t u
  match i, j with
  | 0, 0 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_00 Fchar]
  | 0, 1 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_01 Fchar]
  | 0, 2 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_02 Fchar]
  | 1, 0 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_10 Fchar]
  | 1, 1 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_11 Fchar]
  | 1, 2 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_12 Fchar]
  | 2, 0 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_20 Fchar]
  | 2, 1 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_21 Fchar]
  | 2, 2 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_22 Fchar]
  | 3, 0 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_30 Fchar]
  | 3, 1 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_31 Fchar]
  | 3, 2 => rw [expr_α2β2ψ_as_comm_of_αβψ_βψ_32 Fchar]

-- 8.174c
theorem expr_α2β2ψ_as_comm_of_αβ2ψ_β : forall_ij_tu αβ2ψ β,
    ⸨α2β2ψ, i + j, -t * u⸩ = ⁅⸨αβ2ψ, i, t⸩, ⸨β, j, u⸩⁆ := by
  intro i j hi hj t u
  match i, j with
  | 0, 0 => rw [expr_α2β2ψ_as_comm_of_αβ2ψ_β_00 Fchar]
  | 0, 1 => rw [expr_α2β2ψ_as_comm_of_αβ2ψ_β_01 Fchar]
  | 1, 0 => rw [expr_α2β2ψ_as_comm_of_αβ2ψ_β_10 Fchar]
  | 1, 1 => rw [expr_α2β2ψ_as_comm_of_αβ2ψ_β_11 Fchar]
  | 2, 0 => rw [expr_α2β2ψ_as_comm_of_αβ2ψ_β_20 Fchar]
  | 2, 1 => rw [expr_α2β2ψ_as_comm_of_αβ2ψ_β_21 Fchar]
  | 3, 0 => rw [expr_α2β2ψ_as_comm_of_αβ2ψ_β_30 Fchar]
  | 3, 1 => rw [expr_α2β2ψ_as_comm_of_αβ2ψ_β_31 Fchar]
  | 4, 0 => rw [expr_α2β2ψ_as_comm_of_αβ2ψ_β_40 Fchar]
  | 4, 1 => rw [expr_α2β2ψ_as_comm_of_αβ2ψ_β_41 Fchar]

-- 8.175
theorem comm_of_β_α2β2ψ :
  trivialSpanPropOfRootPair (weakB3LargeGraded F).project ⟨β, α2β2ψ⟩ := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  rcases decompose 2 3 j hj with ⟨ j₁, j₂, rfl, hj₁, hj₂ ⟩
  rw [←one_mul u, ←neg_neg 1, expr_α2β2ψ_as_comm_of_αβ_β2ψ Fchar hj₁ hj₂,
        expr_β_comm_αβ_β2ψ_as_comm_αβ_β2ψ_β hi hj₁ hj₂]
declare_B3Large_trivial_span_expr_thm F β α2β2ψ

omit Fchar in
theorem expr_αβ_comm_αβψ_βψ_as_comm_αβψ_βψ_αβ : forall_ijk_tuv αβ αβψ βψ,
    ⸨αβ, i, t⸩ * ⁅⸨αβψ, j, u⸩, ⸨βψ, k, v⸩⁆ = ⁅⸨αβψ, j, u⸩, ⸨βψ, k, v⸩⁆ * ⸨αβ, i, t⸩ := by
  intro i j k hi hj hk t u v
  grw [commutatorElement_def, inv_of_βψ,
    expr_αβ_αβψ_as_αβψ_αβ, expr_αβ_βψ_as_βψ_αβ hi hk,
    expr_αβ_αβψ_as_αβψ_αβ, expr_αβ_βψ_as_βψ_αβ hi hk]

-- 8.176
theorem comm_of_αβ_α2β2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project ⟨αβ, α2β2ψ⟩ := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  rcases decompose 3 2 j hj with ⟨ j₁, j₂, rfl, hj₁, hj₂ ⟩
  have : u = -2 * (-1/2) * u := by field_simp
  rw [this, expr_α2β2ψ_as_comm_of_αβψ_βψ Fchar hj₁ hj₂,
        expr_αβ_comm_αβψ_βψ_as_comm_αβψ_βψ_αβ hi hj₁ hj₂]
declare_B3Large_trivial_span_expr_thm F αβ α2β2ψ

-- 8.177
theorem comm_of_βψ_α2β2ψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project ⟨βψ, α2β2ψ⟩ := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.2
  rcases decompose 2 3 j hj with ⟨ j₁, j₂, rfl, hj₁, hj₂ ⟩
  rw [←one_mul u, ←neg_neg 1, expr_α2β2ψ_as_comm_of_αβ_β2ψ Fchar hj₁ hj₂,
        expr_βψ_comm_αβ_β2ψ_as_comm_αβ_β2ψ_βψ hi hj₁ hj₂]
declare_B3Large_trivial_span_expr_thm F βψ α2β2ψ

-- 8.178a
@[simp, chev_simps]
theorem inv_of_α2β2ψ : forall_i_t α2β2ψ,
    ⸨α2β2ψ, i, t⸩⁻¹ = ⸨α2β2ψ, i, -t⸩  := by
  intro i hi t
  rcases decompose_5_into_booleans_1_2_2 i hi with ⟨i₁, i₂, i₃, rfl, hi₁, hi₂, hi₃⟩
  rw [eq_of_deg_coef_eq α2β2ψ ((i₁ + i₂) + (i₂ + 2 * i₃)) (by ht) (-t * (-1)) (by ring),
  eq_of_deg_coef_eq α2β2ψ (i := i₁ + 2 * i₂ + 2 * i₃) ((i₁ + i₂) + (i₂ + 2 * i₃)) (by ht) (-t * 1) (by ring),
  expr_α2β2ψ_as_comm_of_αβ_β2ψ Fchar (by ht) (by ht), expr_α2β2ψ_as_comm_of_αβ_β2ψ Fchar (by ht) (by ht),
  (hom_lift_of_inv_doub_of_αβ_β2ψ hi₁ hi₂ hi₃ _ _).1, neg_neg]
  apply (mul_right_inj ⁅⸨αβ, i₁ + i₂, -t⸩, ⸨β2ψ, i₂ + 2 * i₃, 1⸩⁆).1
  rw [mul_inv_cancel]
  nth_rewrite 2 [←neg_neg t]
  rw [(hom_lift_of_inv_doub_of_αβ_β2ψ hi₁ hi₂ hi₃ (-t) _).2.1]

-- 8.178b
@[group_reassoc]
theorem inv_doub_of_α2β2ψ_b : forall_i_t α2β2ψ,
    ⸨α2β2ψ, i, t⸩ * ⸨α2β2ψ, i, t⸩ = ⸨α2β2ψ, i, 2 * t⸩ := by
  intro i hi t
  rcases decompose_5_into_booleans_1_2_2 i hi with ⟨i₁, i₂, i₃, rfl, hi₁, hi₂, hi₃⟩
  rw [eq_of_deg_coef_eq α2β2ψ ((i₁ + i₂) + (i₂ + 2 * i₃)) (by ht) (-t * (-1)) (by ring),
  eq_of_deg_coef_eq α2β2ψ (i := i₁ + 2 * i₂ + 2 * i₃) ((i₁ + i₂) + (i₂ + 2 * i₃)) (by ht) (-(2 * t) * (-1)) (by ring),
  expr_α2β2ψ_as_comm_of_αβ_β2ψ Fchar (by ht) (by ht), expr_α2β2ψ_as_comm_of_αβ_β2ψ Fchar (by ht) (by ht),
  (hom_lift_of_inv_doub_of_αβ_β2ψ hi₁ hi₂ hi₃ _ _).2.2]

-- 8.179a
theorem expr_α2β2ψ_as_αβ_β2ψ_αβ_β2ψ : forall_ij_tu αβ β2ψ,
    ⸨α2β2ψ, i + j, -t * u⸩ = ⸨αβ, i, t⸩ * ⸨β2ψ, j, u⸩ * ⸨αβ, i, -t⸩ * ⸨β2ψ, j, -u⸩ := by
  intro i j hi hj t u
  rw [expr_α2β2ψ_as_comm_of_αβ_β2ψ Fchar hi hj, ←inv_of_αβ, ←inv_of_β2ψ, commutatorElement_def]

-- 8.179b
theorem expr_α2β2ψ_as_β2ψ_αβ_β2ψ_αβ : forall_ij_tu αβ β2ψ,
    ⸨α2β2ψ, i + j, -t * u⸩ = ⸨β2ψ, j, -u⸩ * ⸨αβ, i, t⸩ * ⸨β2ψ, j, u⸩ * ⸨αβ, i, -t⸩ := by
  intro i j hi hj t u
  apply inv_inj.1
  rw [inv_of_α2β2ψ Fchar (by ht)]
  simp only [neg_mul, neg_neg, mul_inv_rev, inv_of_αβ, inv_of_β2ψ]
  rw [eq_of_coef_eq α2β2ψ (-t * (-u)) (by ring), expr_α2β2ψ_as_comm_of_αβ_β2ψ Fchar hi hj,
  ←inv_of_αβ, ←inv_of_β2ψ]
  group

-- 8.180a
@[group_reassoc]
theorem expr_αβ_β2ψ_as_β2ψ_α2β2ψ_αβ : forall_ij_tu αβ β2ψ,
    ⸨αβ, i, t⸩ * ⸨β2ψ, j, u⸩ = ⸨β2ψ, j, u⸩ * ⸨α2β2ψ, i + j, -t * u⸩ * ⸨αβ, i, t⸩ := by
  intro i j hi hj t u
  rw [expr_α2β2ψ_as_β2ψ_αβ_β2ψ_αβ Fchar hi hj, ←inv_of_β2ψ, ←inv_of_αβ]
  group

-- 8.180b
@[group_reassoc]
theorem expr_αβ_β2ψ_as_β2ψ_αβ_α2β2ψ : forall_ij_tu αβ β2ψ,
    ⸨αβ, i, t⸩ * ⸨β2ψ, j, u⸩ = ⸨β2ψ, j, u⸩ * ⸨αβ, i, t⸩ * ⸨α2β2ψ, i + j, -t * u⸩ := by
  intro i j hi hj t u
  rw [eq_of_coef_eq α2β2ψ (- -t * -u) (by ring), expr_α2β2ψ_as_αβ_β2ψ_αβ_β2ψ Fchar hi hj,
  ←inv_of_αβ, neg_neg, neg_neg, ←inv_of_β2ψ]
  group

-- 8.181a
@[group_reassoc]
theorem expr_β_αβ2ψ_as_αβ2ψ_α2β2ψ_β : forall_ij_tu β αβ2ψ,
    ⸨β, i, t⸩ * ⸨αβ2ψ, j, u⸩ = ⸨αβ2ψ, j, u⸩ * ⸨α2β2ψ, i + j, t * u⸩ * ⸨β, i, t⸩ := by
  intro i j hi hj t u
  rw [eq_of_deg_coef_eq α2β2ψ (j + i) (by ht) (-(-u) * t) (by ring), expr_α2β2ψ_as_comm_of_αβ2ψ_β Fchar hj hi,
  ←inv_of_αβ2ψ Fchar hj]
  group

-- 8.181b
@[group_reassoc]
theorem expr_β_αβ2ψ_as_αβ2ψ_β_α2β2ψ : forall_ij_tu β αβ2ψ,
    ⸨β, i, t⸩ * ⸨αβ2ψ, j, u⸩ = ⸨αβ2ψ, j, u⸩ * ⸨β, i, t⸩ * ⸨α2β2ψ, i + j, t * u⸩ := by
  intro i j hi hj t u
  rw [←neg_neg (t * u), ←inv_of_α2β2ψ Fchar (by ht), eq_of_deg_coef_eq α2β2ψ (j + i) (by ht) (-(-u) * (-t)) (by ring),
  expr_α2β2ψ_as_comm_of_αβ2ψ_β Fchar hj hi, comm_swap, ←inv_of_β, ←inv_of_αβ2ψ Fchar hj]
  group

-- 8.182a
@[group_reassoc]
theorem expr_βψ_αβψ_as_αβψ_α2β2ψ_βψ : forall_ij_tu βψ αβψ,
    ⸨βψ, i, t⸩ * ⸨αβψ, j, u⸩ = ⸨αβψ, j, u⸩ * ⸨α2β2ψ, i + j, 2 * t * u⸩ * ⸨βψ, i, t⸩ := by
  intro i j hi hj t u
  rw [eq_of_deg_coef_eq α2β2ψ (j + i) (by ht) (-2 * (-u) *(t)) (by ring),
  expr_α2β2ψ_as_comm_of_αβψ_βψ Fchar hj hi, ←inv_of_αβψ hj]
  group

-- 8.182b
@[group_reassoc]
theorem expr_βψ_αβψ_as_αβψ_βψ_α2β2ψ : forall_ij_tu βψ αβψ,
    ⸨βψ, i, t⸩ * ⸨αβψ, j, u⸩ = ⸨αβψ, j, u⸩ * ⸨βψ, i, t⸩ * ⸨α2β2ψ, i + j, 2 * t * u⸩ := by
  intro i j hi hj t u
  rw [←neg_neg (2 * t * u), ←inv_of_α2β2ψ Fchar (by ht), eq_of_deg_coef_eq α2β2ψ (j + i) (by ht) (-2 * (-u) * (-t)) (by ring),
  expr_α2β2ψ_as_comm_of_αβψ_βψ Fchar hj hi, comm_swap, ←inv_of_βψ, ←inv_of_αβψ hj]
  group

-- 8.183a
theorem commutator_of_α_βψ_a : forall_ij_tu α βψ,
    ⁅⸨α, i, t⸩, ⸨βψ, j, u⸩⁆ = ⸨αβψ, i + j, t * u⸩ * ⸨α2β2ψ, i + 2 * j, t * u^2⸩ := by
  intro i j hi hj t u
  rw [(generic_comm_of_α_βψ Fchar hi hj _ _).1, eq_of_deg_coef_eq α2β2ψ ((i + j) + j) (by ht) (-2 * (-t * u) * (u / 2)) (by ring_nf; field_simp),
  expr_α2β2ψ_as_comm_of_αβψ_βψ Fchar (by ht) hj]

-- 8.183b
theorem commutator_of_α_βψ_b : forall_ij_tu α βψ,
    ⁅⸨α, i, t⸩, ⸨βψ, j, u⸩⁆ = ⸨α2β2ψ, i + 2 * j, t * u^2⸩ * ⸨αβψ, i + j, t * u⸩ := by
  intro i j hi hj t u
  rw [(generic_comm_of_α_βψ Fchar hi hj _ _).2, ←neg_neg (t * u^2), ←inv_of_α2β2ψ Fchar (by ht),
  eq_of_deg_coef_eq α2β2ψ ((i + j) + j) (by ht) (-2 * (t * u) * (u / 2)) (by ring_nf; field_simp),
  expr_α2β2ψ_as_comm_of_αβψ_βψ Fchar (by ht) hj, comm_swap]

-- 8.184
theorem sufficient_conditions_for_comm_of_ψ_and_α2β2ψ :
    ∀ ⦃i j k : ℕ⦄ (hi : i ≤ 1) (hj : j ≤ 2) (hk : k ≤ 3)
    (h50a : ∀ (t u : F), ⁅⸨αβψ, i + j, t⸩, ⸨β2ψ, k, u⸩⁆ = 1)
    (h50b : ∀ (t u : F), ⁅⸨αβ2ψ, 2 * i + j, t⸩, ⸨β2ψ, k, u⸩⁆ = 1),
    ∀ (t u : F), ⁅⸨ψ, i, t⸩, ⸨α2β2ψ, j + k, u⸩⁆ = 1 := by
  intro i j k hi hj hk h50a h50b t u
  have h₁ := fun t u ↦ triv_comm_iff_commutes.1 (h50a t u)
  have h₂ := fun t u ↦ triv_comm_iff_commutes.1 (h50b t u)
  apply triv_comm_iff_commutes.2
  -- expand α2β2ψ into a product of αβ and β2ψ (work on RHS)
  rw [eq_of_coef_eq α2β2ψ (-u * -1) (by ring), expr_α2β2ψ_as_αβ_β2ψ_αβ_β2ψ Fchar hj hk, neg_neg]
  -- move ψ fully to the left
  grw [←expr_ψ_β2ψ_as_β2ψ_ψ, expr_αβ_ψ_as_ψ_αβ2ψ_αβψ_αβ Fchar hj hi, ←expr_ψ_β2ψ_as_β2ψ_ψ, expr_αβ_ψ_as_ψ_αβ_αβψ_αβ2ψ Fchar hj hi]
  -- use h₂ to cancel the αβ2ψ elements
  grw [eq_of_deg_eq αβ2ψ (2 * i + j) (by ht), h₂ (-(u * t * t))]
  nth_rewrite 2 [eq_of_deg_eq αβ2ψ (2 * i + j) (by ht)]
  rw [← inv_of_αβ2ψ Fchar (by ht)]
  grw [rfl]
  -- use h₁ to cancel the αβψ elements
  grw [eq_of_deg_eq αβψ (i + j) (by ht), h₁]
  rw [← inv_of_αβψ (by ht)]
  nth_rewrite 2 [eq_of_deg_eq αβψ (i + j) (by ht)]
  grw [rfl]
