/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Steinberg.B3Large.Basic

import Mathlib.Tactic.Group
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.FieldSimp

import Steinberg.Defs.Lattice
import Steinberg.Defs.Commutator
import Steinberg.Defs.DegreeReflection

import Steinberg.Upstream.FreeGroup


namespace Steinberg.B3Large

open Steinberg B3LargePosRoot GradedPartialChevalley GradedChevalleyGenerator GradedPartialChevalleyGroup

variable {F : Type TF} [Field F] (Fchar : (2 : F) ≠ 0)
variable (F_sum_of_squares : ∀ (a : F), ∃ (x y : F), a = x^2 + y^2)

theorem def_of_αβψ : forall_i_t αβψ,
  ⸨βψ, (split_3_into_1_2 i hi).2, -1/2⸩'(correct_of_split_3_into_1_2 i hi).2.1 *
  ⸨α, (split_3_into_1_2 i hi).1, t⸩'(correct_of_split_3_into_1_2 i hi).1 *
  ⸨βψ, (split_3_into_1_2 i hi).2, 1⸩'(correct_of_split_3_into_1_2 i hi).2.1 *
  ⸨α, (split_3_into_1_2 i hi).1, -t⸩'(correct_of_split_3_into_1_2 i hi).1 *
  ⸨βψ, (split_3_into_1_2 i hi).2, -1/2⸩'(correct_of_split_3_into_1_2 i hi).2.1
    = ⸨αβψ, i, t⸩ := by
  intro i hi t
  symm
  apply (weakB3LargeGraded F).definitionProp_of_define

theorem def_of_αβ2ψ : forall_i_t αβ2ψ,
    ⁅ (⸨α, (split_4_into_1_3 i hi).1, t⸩'(correct_of_split_4_into_1_3 i hi).1),
      (⸨β2ψ, (split_4_into_1_3 i hi).2, 1⸩'(correct_of_split_4_into_1_3 i hi).2.1)
    ⁆ = ⸨αβ2ψ, i, t⸩ := by
  intro i hi t
  symm
  apply (weakB3LargeGraded F).definitionProp_of_define

theorem def_of_α2β2ψ : forall_i_t α2β2ψ,
    ⁅ (⸨αβ, (split_5_into_2_3 i hi).1, t⸩'(correct_of_split_5_into_2_3 i hi).1),
      (⸨β2ψ, (split_5_into_2_3 i hi).2, 1⸩'(correct_of_split_5_into_2_3 i hi).2.1)
    ⁆ = ⸨α2β2ψ, i, -t⸩ := by
  intro i hi t
  symm
  nth_rewrite 2 [←neg_neg t]
  apply (weakB3LargeGraded F).definitionProp_of_define

/-! ### Nonhomogeneous lift -/

-- 8.81
theorem raw_nonhom_lift_of_comm_of_αβ_βψ : ∀ (t₁ t₀ u₁ u₀ v₁ v₀ : F),
    ⁅ ⸨αβ, 2, t₁ * u₁⸩ * ⸨αβ, 1, t₁ * u₀ + t₀ * u₁⸩ * ⸨αβ, 0, t₀ * u₀⸩
    , ⸨βψ, 2, u₁ * v₁⸩ * ⸨βψ, 1, u₁ * v₀ + u₀ * v₁⸩ * ⸨βψ, 0, u₀ * v₀⸩ ⁆
    = 1 := by
  nonhom_tac rels_of_nonhom_lift_of_comm_of_αβ_βψ [t₁, t₀, u₁, u₀, v₁, v₀]

-- 8.82
theorem raw_nonhom_lift_of_comm_of_α_α2β2ψ : ∀ (t₁ t₀ u₁ u₀ v₁ v₀ : F),
    ⁅ ⸨α, 1, t₁⸩ * ⸨α, 0, t₀⸩,
      ⁅ ⸨αβ, 2, t₁ * u₁⸩ * ⸨αβ, 1, t₁ * u₀ + t₀ * u₁⸩ * ⸨αβ, 0, t₀ * u₀⸩,
        ⸨β2ψ, 3, u₁ * v₁^2⸩ * ⸨β2ψ, 2, u₀ * v₁^2 + 2 * u₁ * v₀ * v₁⸩
          * ⸨β2ψ, 1, u₁ * v₀^2 + 2 * u₀ * v₀ * v₁⸩ * ⸨β2ψ, 0, u₀ * v₀^2⸩ ⁆⁆ = 1 := by
  nonhom_tac rels_of_nonhom_lift_of_comm_of_α_α2β2ψ [t₁, t₀, u₁, u₀, v₁, v₀]

/-! ### Homogeneous lift -/

-- 8.83
theorem raw_hom_lift_of_interchange_of_αβψ : forall_ijk_tuv,
    ⸨ψ, k, -v / 2⸩ * ⸨αβ, i + j, t * u⸩ * ⸨ψ, k, v⸩ * ⸨αβ, i + j, -t * u⸩ * ⸨ψ, k, -v / 2⸩ =
    ⸨βψ, j + k, -u * v / 2⸩ * ⸨α, i, t⸩ * ⸨βψ, j + k, u * v⸩ * ⸨α, i, -t⸩ * ⸨βψ, j + k, -u * v / 2⸩ := by
  hom_tac base_rel_of_hom_lift_of_interchange_of_αβψ [i, j, k, hi, hj, hk, t, u, v]


-- 8.84
theorem raw_hom_lift_of_doub_of_αβψ' : forall_ijk_tuv,
    ⸨ψ, k, -v / 2⸩ * ⸨αβ, i + j, t * u⸩ * ⸨ψ, k, v⸩ * ⸨αβ, i + j, -t * u⸩ * ⸨ψ, k, -v / 2⸩ *
    ⸨ψ, k, -v / 2⸩ * ⸨αβ, i + j, t * u⸩ * ⸨ψ, k, v⸩ * ⸨αβ, i + j, -t * u⸩ * ⸨ψ, k, -v / 2⸩ =
    ⸨ψ, k, -v⸩ * ⸨αβ, i + j, t * u⸩ * ⸨ψ, k, 2 * v⸩ * ⸨αβ, i + j, -t * u⸩ * ⸨ψ, k, -v⸩ := by
  hom_tac base_rel_of_hom_lift_of_doub_of_αβψ [i, j, k, hi, hj, hk, t, u, v]

-- this is slightly annoying b/c we want to switch the index on i to (0,1,2)
theorem raw_hom_lift_of_doub_of_αβψ : forall_ik_tuv αβ ψ,
    ⸨ψ, k, -v / 2⸩ * ⸨αβ, i, t * u⸩ * ⸨ψ, k, v⸩ * ⸨αβ, i, -t * u⸩ * ⸨ψ, k, -v / 2⸩ *
    ⸨ψ, k, -v / 2⸩ * ⸨αβ, i, t * u⸩ * ⸨ψ, k, v⸩ * ⸨αβ, i, -t * u⸩ * ⸨ψ, k, -v / 2⸩ =
    ⸨ψ, k, -v⸩ * ⸨αβ, i, t * u⸩ * ⸨ψ, k, 2 * v⸩ * ⸨αβ, i, -t * u⸩ * ⸨ψ, k, -v⸩ := by
  intro i k hi hk
  have : ∃ i₁ i₂ : ℕ, i = i₁ + i₂ ∧ i₁ ≤ 1 ∧ i₂ ≤ 1 := decompose 1 1 i (by tauto)
  rcases this with ⟨ i₁, i₂,h,  hi₁, hi₂ ⟩
  simp only [h]
  exact raw_hom_lift_of_doub_of_αβψ' hi₁ hi₂ hk

-- 8.85
theorem raw_hom_lift_of_interchange_of_αβ2ψ : forall_ijk_tuv,
    ⁅ ⸨ψ, k, -v / 2⸩ * ⸨αβ, i + j, t * u⸩ * ⸨ψ, k, v⸩ * ⸨αβ, i + j, -t * u⸩ * ⸨ψ, k, -v / 2⸩,
      ⸨ψ, k, v⸩ ⁆
      = ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, -2 * u * v^2⸩ ⁆ := by
  hom_tac base_rel_of_hom_lift_of_interchange_of_αβ2ψ [i, j, k, hi, hj, hk, t, u, v]

-- 8.86
theorem raw_hom_lift_of_comm_of_βψ_α_β2ψ : forall_ijk_tuv,
    ⁅ ⸨βψ, j + k, u * v⸩, ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆ = 1 := by
  hom_tac base_rel_of_hom_lift_of_comm_of_βψ_α_β2ψ [i, j, k, hi, hj, hk, t, u, v]

-- 8.87a
theorem raw_hom_lift_of_inv_doub_of_α_β2ψ_a : forall_ijk_tuv,
    ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ = ⁅ ⸨α, i, -t⸩, ⸨β2ψ, j + 2 * k, -u * v^2⸩ ⁆ := by
  hom_tac base_rel_of_hom_lift_of_inv_doub_of_α_β2ψ_a [i, j, k, hi, hj, hk, t, u, v]

-- 8.87b
theorem raw_hom_lift_of_inv_doub_of_α_β2ψ_b : forall_ijk_tuv,
    ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ * ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, -u * v^2⸩ ⁆ = 1 := by
  hom_tac base_rel_of_hom_lift_of_inv_doub_of_α_β2ψ_b [i, j, k, hi, hj, hk, t, u, v]

-- 8.87c
theorem raw_hom_lift_of_inv_doub_of_α_β2ψ_c : forall_ijk_tuv,
    ⁅ ⸨α, i, t⸩ , ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆
    * ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆
      = ⁅⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, 2 * u * v^2⸩ ⁆ := by
  hom_tac base_rel_of_hom_lift_of_inv_doub_of_α_β2ψ_c [i, j, k, hi, hj, hk, t, u, v]

-- 8.88
theorem raw_hom_lift_of_comm_of_β2ψ_αβψ : forall_ijk_tuv,
    ⁅ ⸨β2ψ, j + 2 * k, u * v^2⸩,
      ⸨ψ, k, -v / 2⸩ * ⸨αβ, i + j, t * u⸩ * ⸨ψ, k, v⸩ * ⸨αβ, i + j, -t * u⸩ * ⸨ψ, k, -v / 2⸩ ⁆ = 1 := by
  hom_tac base_rel_of_hom_lift_of_comm_of_β2ψ_αβψ [i, j, k, hi, hj, hk, t, u, v]

-- 8.89a
theorem raw_hom_lift_of_interchange_of_α2β2ψ_a : forall_ijk_tuv,
    ⁅ ⸨αβ, i + j, t * u⸩, ⸨β2ψ, j + 2 * k, 2 * u * v^2⸩ ⁆
      = ⁅ ⸨ψ, k, -v / 2⸩ * ⸨αβ, i + j, t * u⸩ * ⸨ψ, k, v⸩ * ⸨αβ, i + j, -t * u⸩ * ⸨ψ, k, -v / 2⸩,
          ⸨βψ, j + k, u * v⸩ ⁆ := by
  hom_tac base_rel_of_hom_lift_of_interchange_of_α2β2ψ_a [i, j, k, hi, hj, hk, t, u, v]

-- 8.89b
theorem raw_hom_lift_of_interchange_of_α2β2ψ_b : forall_ijk_tuv,
    ⁅ ⸨ψ, k, -v / 2⸩ * ⸨αβ, i + j, t * u⸩ * ⸨ψ, k, v⸩ * ⸨αβ, i + j, -t * u⸩ * ⸨ψ, k, -v / 2⸩,
      ⸨βψ, j + k, u * v⸩ ⁆
      = ⁅ ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, 2 * u * v^2⸩ ⁆, ⸨β, j, u⸩ ⁆ := by
  hom_tac base_rel_of_hom_lift_of_interchange_of_α2β2ψ_b [i, j, k, hi, hj, hk, t, u, v]

-- 8.90
theorem raw_hom_lift_of_comm_of_ψ_αβ_β2ψ : forall_ijk_tuv,
    ⁅ ⸨ψ, k, v⸩, ⁅ ⸨αβ, i + j, t * u⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆ = 1 := by
  hom_tac base_rel_of_hom_lift_of_comm_of_ψ_αβ_β2ψ [i, j, k, hi, hj, hk, t, u, v]

-- 8.91a
theorem raw_hom_lift_of_comm_of_αβ_αβ_β2ψ_a : forall_ijk_tuv,
    ⁅ ⸨αβ, i + j, t * u⸩, ⁅ ⸨αβ, i + j, t * u⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆ = 1 := by
  hom_tac base_rel_of_hom_lift_of_comm_of_αβ_αβ_β2ψ_a [i, j, k, hi, hj, hk, t, u, v]

-- 8.91b
theorem raw_hom_lift_of_comm_of_αβ_αβ_β2ψ_b : forall_ijk_tuv,
    ⁅ ⸨αβ, i + j, t * u⸩, ⁅ ⸨αβ, i + j, -t * u⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆ = 1 := by
  hom_tac base_rel_of_hom_lift_of_comm_of_αβ_αβ_β2ψ_b [i, j, k, hi, hj, hk, t, u, v]

-- 8.92a
theorem raw_hom_lift_of_inv_doub_of_αβ_β2ψ_a : forall_ijk_tuv,
    ⁅ ⸨αβ, i + j, t * u⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆
      = ⁅ ⸨αβ, i + j, -t * u⸩, ⸨β2ψ, j + 2 * k, -u * v^2⸩ ⁆ := by
  hom_tac base_rel_of_hom_lift_of_inv_doub_of_αβ_β2ψ_a [i, j, k, hi, hj, hk, t, u, v]

-- 8.92b
theorem raw_hom_lift_of_inv_doub_of_αβ_β2ψ_b : forall_ijk_tuv,
    ⁅ ⸨αβ, i + j, t * u⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆
    * ⁅ ⸨αβ, i + j, -t * u⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ = 1 := by
  hom_tac base_rel_of_hom_lift_of_inv_doub_of_αβ_β2ψ_b [i, j, k, hi, hj, hk, t, u, v]

-- 8.92c
theorem raw_hom_lift_of_inv_doub_of_αβ_β2ψ_c : forall_ijk_tuv,
    ⁅ ⸨αβ, i + j, t * u⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆
    * ⁅ ⸨αβ, i + j, t * u⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆
      = ⁅ ⸨αβ, i + j, 2 * t * u⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ := by
  hom_tac base_rel_of_hom_lift_of_inv_doub_of_αβ_β2ψ_c [i, j, k, hi, hj, hk, t, u, v]

-- 8.93a
theorem raw_hom_lift_of_inv_doub_of_β_αβ2ψ_a : forall_ijk_tuv,
    ⁅ ⸨β, j, u⸩,
      ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆
      = ⁅ ⸨β, j, -u⸩, ⁅ ⸨α, i, -t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆ := by
  hom_tac base_rel_of_hom_lift_of_inv_doub_of_β_αβ2ψ_a [i, j, k, hi, hj, hk, t, u, v]

-- 8.93b
theorem raw_hom_lift_of_inv_doub_of_β_αβ2ψ_b : forall_ijk_tuv,
    ⁅ ⸨β, j, u⸩, ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆
    * ⁅ ⸨β, j, -u⸩, ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆ = 1 := by
  hom_tac base_rel_of_hom_lift_of_inv_doub_of_β_αβ2ψ_b [i, j, k, hi, hj, hk, t, u, v]

-- 8.93c
theorem raw_hom_lift_of_inv_doub_of_β_αβ2ψ_c : forall_ijk_tuv,
    ⁅ ⸨β, j, u⸩, ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆
    * ⁅ ⸨β, j, u⸩, ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆
      = ⁅ ⸨β, j, 2 * u⸩, ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆ := by
  hom_tac base_rel_of_hom_lift_of_inv_doub_of_β_αβ2ψ_c [i, j, k, hi, hj, hk, t, u, v]

-- 8.94
theorem raw_hom_lift_of_comm_of_βψ_αβ2ψ : forall_ijk_tuv,
    ⁅ ⸨βψ, j + k, u * v⸩, ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆ = 1 := by
  hom_tac base_rel_of_hom_lift_of_comm_of_βψ_αβ2ψ [i, j, k, hi, hj, hk, t, u, v]

-- 8.95
theorem raw_hom_lift_of_comm_of_β2ψ_αβ2ψ : forall_ijk_tuv,
    ⁅ ⸨β2ψ, j + 2 * k, u * v^2⸩, ⁅ ⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, u * v^2⸩ ⁆ ⁆ = 1 := by
  hom_tac base_rel_of_hom_lift_of_comm_of_β2ψ_αβ2ψ [i, j, k, hi, hj, hk, t, u, v]

/-- Reflecting the lift of a generator is the same as taking the opposite lift. -/
theorem reflect_of_hom (g : PartialChevalley.ChevalleyGenerator B3LargePosRoot F)
  (i j k : ℕ) (hi : i ≤ α.height) (hj : j ≤ β.height) (hk : k ≤ ψ.height)
  (t u v : F) :
    reflect (hom_lift i j k hi hj hk t u v g) = hom_lift (1-i) (1-j) (1-k) (by ht) (by ht) (by ht) t u v g := by
    rcases g with ⟨ ζ, t ⟩
    simp only [reflect, hom_lift]
    split
    all_goals simp only [PositiveRootSystem.height, B3LargePosRoot.height]
    all_goals congr; ht

/-- Extends previous theorem to arbitrary relations. -/
-- TODO: simplify?
theorem reflect_of_hom' (r : FreeGroup (PartialChevalley.ChevalleyGenerator B3LargePosRoot F))
  (i j k : ℕ) (hi : i ≤ α.height) (hj : j ≤ β.height) (hk : k ≤ ψ.height)
  (t u v : F) :
    (FreeGroup.map reflect) (FreeGroup.map (hom_lift i j k hi hj hk t u v) r)
      = FreeGroup.map (hom_lift (1-i) (1-j) (1-k) (by ht) (by ht) (by ht) t u v) r := by
    suffices (FreeGroup.map reflect).comp (FreeGroup.map (hom_lift i j k hi hj hk t u v))
      = FreeGroup.map (hom_lift (1-i) (1-j) (1-k) (by ht) (by ht) (by ht) t u v) by
      have : (FreeGroup.map reflect).comp (FreeGroup.map (hom_lift i j k hi hj hk t u v)) r
        = FreeGroup.map (hom_lift (1-i) (1-j) (1-k) (by ht) (by ht) (by ht) t u v) r := by
          congr
      rw [←this]
      simp only [MonoidHom.coe_comp, Function.comp_apply]
    ext g
    simp only [MonoidHom.coe_comp, Function.comp_apply, FreeGroup.map.of]
    congr
    exact reflect_of_hom g i j k hi hj hk t u v

theorem map_reflect_of_hom (r : FreeGroup (PartialChevalley.ChevalleyGenerator B3LargePosRoot F)) :
  (FreeGroup.map reflect) '' (hom_lift_set r) = hom_lift_set r := by
  simp only [hom_lift_set]
  ext r'
  simp only [Set.mem_image, Set.mem_setOf]
  constructor
  · intro h
    rcases h with ⟨ x, h, _ ⟩
    subst r'
    rcases h with ⟨ i, j, k, hi, hj, hk, t, u, v, h ⟩
    subst x
    use (1-i), (1-j), (1-k), (by ht), (by ht), (by ht), t, u, v
    exact (reflect_of_hom' r i j k hi hj hk t u v).symm
  · intro h
    rcases h with ⟨ i, j, k, hi, hj, hk, t, u, v, h ⟩
    use (FreeGroup.map (hom_lift (1-i) (1-j) (1-k) (by ht) (by ht) (by ht) t u v)) r
    constructor
    · use (1-i), (1-j), (1-k), (by ht), (by ht), (by ht), t, u, v
    · subst r'
      rw [reflect_of_hom' r (1-i) (1-j) (1-k) (by ht) (by ht) (by ht) t u v]
      congr
      apply eq_of_hom_lift_eq
      all_goals ht

private theorem help1 (r : FreeGroup (GradedChevalleyGenerator B3LargePosRoot F))
  (h : ∀ r' ∈ hom_lift_set b, (FreeGroup.lift (defineThenReflect (weakB3LargeGraded F))) r' = (FreeGroup.map reflect) r') :
  (∃ x ∈ hom_lift_set b, (FreeGroup.lift (defineThenReflect (weakB3LargeGraded F))) x = r) ↔ ∃ x ∈ hom_lift_set b, (FreeGroup.map reflect) x = r := by
  constructor
  · intro h
    rcases h with ⟨ r', h_r', h ⟩
    subst r
    use r'
    constructor
    · exact h_r'
    · exact (h r' h_r').symm
  · intro h
    rcases h with ⟨ r', h_r', h ⟩
    subst r
    use r'
    constructor
    · exact h_r'
    · exact (h r' h_r')

set_option maxHeartbeats 0

theorem b3large_valid :
  reflectValidProp (weakB3LargeGraded F) := by
  simp only [reflectValidProp]
  intro S h_S
  simp only [weakB3LargeGraded, lifted_sets, Set.mem_union] at h_S
  rcases h_S with h_nonhom|h_hom
  · simp only [nonhom_lifted_sets, Set.mem_insert_iff,
    Set.mem_singleton_iff] at h_nonhom
    rcases h_nonhom with h | h
    · subst h
      intro r hr
      simp only [rels_of_nonhom_lift_of_comm_of_αβ_βψ] at hr
      rcases hr with ⟨ t₁, t₀, u₁, u₀, v₁, v₀, rfl ⟩
      simp only [map_commutatorElement, map_mul, FreeGroup.lift.of]
      repeat rw [defineThenReflect_eq_reflect_of_mem_presentRoots _ _ (by tauto)]
      simp only [reflect, PositiveRootSystem.height, height]
      simp_arith
      rw [add_comm, add_comm (u₁ * v₀)]
      grw [expr_αβ_αβ_as_αβ_αβ (i := 1), expr_αβ_αβ_as_αβ_αβ, expr_αβ_αβ_as_αβ_αβ (i := 0)]
      grw [expr_βψ_βψ_as_βψ_βψ (i := 1), expr_βψ_βψ_as_βψ_βψ, expr_βψ_βψ_as_βψ_βψ (i := 0)]
      exact raw_nonhom_lift_of_comm_of_αβ_βψ t₀ t₁ u₀ u₁ v₀ v₁
    · subst h
      intro r hr
      simp only [rels_of_nonhom_lift_of_comm_of_α_α2β2ψ] at hr
      rcases hr with ⟨ t₁, t₀, u₁, u₀, v₁, v₀, rfl ⟩
      simp only [map_commutatorElement, map_mul, FreeGroup.lift.of]
      repeat rw [defineThenReflect_eq_reflect_of_mem_presentRoots _ _ (by tauto)]
      simp only [reflect, PositiveRootSystem.height, height]
      simp_arith
      rw [add_comm]
      have := raw_nonhom_lift_of_comm_of_α_α2β2ψ t₀ t₁ u₀ u₁ v₀ v₁
      norm_num at this
      grw [expr_α_α_as_α_α, expr_αβ_αβ_as_αβ_αβ (i := 1), expr_αβ_αβ_as_αβ_αβ (i := 0),
          expr_αβ_αβ_as_αβ_αβ (i := 0), expr_β2ψ_β2ψ_as_β2ψ_β2ψ (i := 2),
          expr_β2ψ_β2ψ_as_β2ψ_β2ψ (i := 1), expr_β2ψ_β2ψ_as_β2ψ_β2ψ (i := 0), expr_β2ψ_β2ψ_as_β2ψ_β2ψ (i := 1),
          expr_β2ψ_β2ψ_as_β2ψ_β2ψ (i := 0), expr_β2ψ_β2ψ_as_β2ψ_β2ψ (i := 0)]
      rw [← this]
      grw [pow_two, mul_comm v₁ v₀, mul_comm v₁ v₀]
  · suffices (FreeGroup.lift (defineThenReflect (weakB3LargeGraded F))) '' S = S by
      intro r h_r
      apply eq_one_of_mem_rels
      have : (FreeGroup.lift (defineThenReflect (weakB3LargeGraded F))) r ∈ S := by
        rw [←this]
        simp only [Set.mem_image]
        use r
      simp only [allRelations, lifted_sets, Set.mem_iUnion]
      use GradedSteinbergRelationClass.Lifted
      use S
      constructor
      · simp only [weakB3LargeGraded, liftedRelationsSets, lifted_sets, Set.mem_union]
        right
        exact h_hom
      · exact this
    simp only [hom_lifted_sets, hom_lift_base_set, Set.mem_image] at h_hom
    rcases h_hom with ⟨ b, h, h_hom ⟩
    subst S
    nth_rewrite 2 [←map_reflect_of_hom]
    ext r
    simp only [Set.mem_image]
    apply help1
    intro r' h_r'
    simp only [hom_lift_set, Set.mem_setOf] at h_r'
    rcases h_r' with ⟨ i, j, k, hi, hj, hk, t, u, v, h_r' ⟩
    subst r'
    rcases h with h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h
    -- TODO: abstract out a property that says "all the base_rels are present"
    all_goals (
      subst b
      simp only [
        base_rel_of_hom_lift_of_interchange_of_αβψ,
        base_rel_of_hom_lift_of_doub_of_αβψ,
        base_rel_of_hom_lift_of_interchange_of_αβ2ψ,
        base_rel_of_hom_lift_of_comm_of_βψ_α_β2ψ,
        base_rel_of_hom_lift_of_inv_doub_of_α_β2ψ_a,
        base_rel_of_hom_lift_of_inv_doub_of_α_β2ψ_b,
        base_rel_of_hom_lift_of_inv_doub_of_α_β2ψ_c,
        base_rel_of_hom_lift_of_comm_of_β2ψ_αβψ,
        base_rel_of_hom_lift_of_interchange_of_α2β2ψ_a,
        base_rel_of_hom_lift_of_interchange_of_α2β2ψ_b,
        base_rel_of_hom_lift_of_comm_of_ψ_αβ_β2ψ,
        base_rel_of_hom_lift_of_comm_of_αβ_αβ_β2ψ_a,
        base_rel_of_hom_lift_of_comm_of_αβ_αβ_β2ψ_b,
        base_rel_of_hom_lift_of_inv_doub_of_αβ_β2ψ_a,
        base_rel_of_hom_lift_of_inv_doub_of_αβ_β2ψ_b,
        base_rel_of_hom_lift_of_inv_doub_of_αβ_β2ψ_c,
        base_rel_of_hom_lift_of_inv_doub_of_β_αβ2ψ_a,
        base_rel_of_hom_lift_of_inv_doub_of_β_αβ2ψ_b,
        base_rel_of_hom_lift_of_inv_doub_of_β_αβ2ψ_c,
        base_rel_of_hom_lift_of_comm_of_βψ_αβ2ψ,
        base_rel_of_hom_lift_of_comm_of_β2ψ_αβ2ψ]
      simp only [one_mul, neg_mul, map_mul, map_inv, map_commutatorElement, FreeGroup.map.of, FreeGroup.lift.of, hom_lift]
      repeat rw [defineThenReflect_eq_reflect_of_mem_presentRoots (weakB3LargeGraded F)]
      all_goals tauto
    )

include Fchar
theorem Fchar4 : (4 : F) ≠ 0 := by
  have : (4 : F) = 2 * 2 := by ring_nf
  rw [this]
  exact mul_ne_zero Fchar Fchar

-- 8.108
-- TODO: abstract?
theorem expr_βψ_as_ψ_β_ψ_β_ψ :
  forall_ij_tu 1 1,
    ⸨βψ, i + j, t * u⸩ = ⸨ψ, i, -t/2⸩ * ⸨β, j, u⸩ * ⸨ψ, i, t⸩ * ⸨β, j, -u⸩ * ⸨ψ, i, -t/2⸩ := by
  intro i j hi hj t u
  have : ⸨ψ, i, -t/2⸩ * ⸨β, j, u⸩ * ⸨ψ, i, t⸩ * ⸨β, j, -u⸩ * ⸨ψ, i, -t/2⸩ = ⸨β, j, u⸩ ⋆ ⸨ψ, i, t/2⸩ := by
    unfold starCommutator_def
    simp only [inv_of_ψ, inv_of_β, pow_two, lin_of_ψ, neg_div]
    congr
    field_simp
    ring
  rw [this]
  apply starCommutator_helper ⸨β2ψ, 2 * i + j, t^2 * u⸩
  · rw [pow_two, lin_of_ψ, comm_of_β_ψ]
    simp_rw [←add_comm i j, ←add_comm (2*i) j]
    have := Fchar4 Fchar
    field_simp
    ring_nf
    field_simp
  · rw [inv_of_βψ, CI2, comm_of_ψ_βψ, inv_of_β2ψ]
    field_simp
    ring_nf

omit Fchar

-- 8.111
@[group_reassoc]
theorem expr_β_α_as_αβ_α_β : forall_ij_tu α β,
    ⸨β, j, u⸩ * ⸨α, i, t⸩ = ⸨αβ, i + j, -t * u⸩ * ⸨α, i, t⸩ * ⸨β, j, u⸩ := by
  intro i j hi hj t u
  rw [neg_mul, ← inv_of_αβ]
  have : t * u = ↑(1 : ℤ) * t * u := by chev_simp
  rw [this]
  rw [← comm_of_α_β hi hj]
  exact comm_left _ _

-- 8.112a
@[group_reassoc]
theorem expr_ψ_β_as_β_ψ_βψ_β2ψ : forall_ij_tu β ψ,
    ⸨ψ, j, u⸩ * ⸨β, i, t⸩ = ⸨β, i, t⸩ * ⸨ψ, j, u⸩ * ⸨βψ, i + j, -t * u⸩ * ⸨β2ψ, i + 2 * j, t * u^2⸩ := by
  intro i j hi hj t u
  have hij : i + j ≤ βψ.height := by ht
  have hi2j : i + (2 * j) ≤ β2ψ.height := by ht
  rw [comm_right_rev, inv_of_β, inv_of_ψ]
  grw [comm_of_β_ψ, mul_inv_rev, expr_βψ_β2ψ_as_β2ψ_βψ hij hi2j, pow_two]

-- 8.112b
@[group_reassoc]
theorem expr_ψ_β_as_β2ψ_βψ_β_ψ : forall_ij_tu β ψ,
    ⸨ψ, j, u⸩ * ⸨β, i, t⸩ = ⸨β2ψ, i + 2 * j, -t * u^2⸩ * ⸨βψ, i + j, -t * u⸩ * ⸨β, i, t⸩ * ⸨ψ, j, u⸩ := by
  intro i j hi hj t u
  have hij : i + j ≤ βψ.height := by ht
  have hi2j : i + (2 * j) ≤ β2ψ.height := by ht
  rw [comm_left_rev]
  grw [comm_of_β_ψ, mul_inv_rev, pow_two]

-- 8.112c
omit Fchar
@[group_reassoc]
theorem expr_ψ_β_as_β_β2ψ_βψ_ψ : forall_ij_tu β ψ,
    ⸨ψ, j, u⸩ * ⸨β, i, t⸩ = ⸨β, i, t⸩ * ⸨β2ψ, i + 2 * j, -t * u^2⸩ * ⸨βψ, i + j, -t * u⸩ * ⸨ψ, j, u⸩ := by
  intro i j hi hj t u
  have hij : i + j ≤ βψ.height := by ht
  have hi2j : i + (2 * j) ≤ β2ψ.height := by ht
  rw [comm_mid_rev, inv_of_β]
  grw [comm_of_β_ψ, expr_βψ_β2ψ_as_β2ψ_βψ hij hi2j, pow_two]

-- 8.112d
@[group_reassoc]
theorem expr_ψ_β_as_β_βψ_β2ψ_ψ : forall_ij_tu β ψ,
    ⸨ψ, j, u⸩ * ⸨β, i, t⸩ = ⸨β, i, t⸩ * ⸨βψ, i + j, -t * u⸩ * ⸨β2ψ, i + 2 * j, -t * u^2⸩ * ⸨ψ, j, u⸩ := by
  intro i j hi hj t u
  have hij : i + j ≤ βψ.height := by ht
  have hi2j : i + (2 * j) ≤ β2ψ.height := by ht
  rw [expr_ψ_β_as_β_β2ψ_βψ_ψ hi hj t u,
        greassoc_of% expr_βψ_β2ψ_as_β2ψ_βψ hij hi2j (-t * u) (-t * u^2)]

-- 8.113a
@[group_reassoc]
theorem expr_ψ_βψ_as_βψ_β2ψ_ψ : forall_ij_tu ψ βψ,
    ⸨ψ, i, t⸩ * ⸨βψ, j, u⸩ = ⸨βψ, j, u⸩ * ⸨β2ψ, i + j, 2 * t * u⸩ * ⸨ψ, i, t⸩ := by
  intro i j hi hj t u
  rw [comm_mid, inv_of_βψ]
  grw [comm_of_ψ_βψ hi hj]

-- 8.113b
@[group_reassoc]
theorem expr_ψ_βψ_as_βψ_ψ_β2ψ :
  forall_ij_tu ψ βψ,
    ⸨ψ, i, t⸩ * ⸨βψ, j, u⸩ = ⸨βψ, j, u⸩ * ⸨ψ, i, t⸩ * ⸨β2ψ, i + j, 2 * t * u⸩ := by
  intro i j hi hj t u
  have hij : i + j ≤ β2ψ.height := by ht
  grw [expr_ψ_β2ψ_as_β2ψ_ψ hi hij, expr_ψ_βψ_as_βψ_β2ψ_ψ hi hj]

-- 8.114a
@[group_reassoc]
theorem expr_βψ_ψ_as_ψ_β2ψ_βψ :
  forall_ij_tu ψ βψ,
    ⸨βψ, j, u⸩ * ⸨ψ, i, t⸩ = ⸨ψ, i, t⸩ * ⸨β2ψ, i + j, -2 * t * u⸩ * ⸨βψ, j, u⸩ := by
  intro i j hi hj t u
  have hij : j + i ≤ β2ψ.height := by ht
  rw [deg_add_comm β2ψ i j, ← greassoc_of% expr_βψ_β2ψ_as_β2ψ_βψ hj hij, deg_add_comm β2ψ j i]
  grw [expr_ψ_βψ_as_βψ_ψ_β2ψ hi hj]

-- 8.114b
@[group_reassoc]
theorem expr_βψ_ψ_as_ψ_βψ_β2ψ : forall_ij_tu ψ βψ,
    ⸨βψ, j, u⸩ * ⸨ψ, i, t⸩ = ⸨ψ, i, t⸩ * ⸨βψ, j, u⸩ * ⸨β2ψ, i + j, -2 * t * u⸩ := by
  intro i j hi hj t u
  have hij : i + j ≤ β2ψ.height := by ht
  rw [expr_βψ_ψ_as_ψ_β2ψ_βψ hi hj, greassoc_of% expr_βψ_β2ψ_as_β2ψ_βψ hj hij]

/- Commutator relation in the case (i,j) is not (0,2) or (2,0) (via the previous theorem). -/
private lemma hom_lift_of_comm_of_αβ_βψ (i j k : ℕ) (hi : i ≤ 1) (hj : j ≤ 1) (hk : k ≤ 1) :
  ∀ (t u : F), ⁅ ⸨ αβ, i + j, t⸩, ⸨βψ, j + k, u⸩ ⁆ = 1 := by
    intro t u
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
    have id₁ : ⸨αβ, i + j, t⸩ = ⸨αβ, 2, t₁ * u₁⸩ * ⸨αβ, 1, t₁ * u₀ + t₀ * u₁⸩ * ⸨αβ, 0, t₀ * u₀⸩ := by (
      fin_cases hf_i, hf_j, hf_k
      <;> chev_simp [t₀, t₁, u₀, u₁, v₀, v₁]
    )
    have id₂ : ⸨βψ, j + k, u⸩ = ⸨βψ, 2, u₁ * v₁⸩ * ⸨βψ, 1, u₁ * v₀ + u₀ * v₁⸩ * ⸨βψ, 0, u₀ * v₀⸩ := by (
      fin_cases hf_i, hf_j, hf_k
      <;> chev_simp [t₀, t₁, u₀, u₁, v₀, v₁]
    )
    rw [id₁, id₂, raw_nonhom_lift_of_comm_of_αβ_βψ]

private lemma image_of_hom_lift_of_comm_of_αβ_βψ {i j : ℕ} (hi : i ≤ αβ.height) (hj : j ≤ βψ.height)
    : ((i, j) ∈ ij_jk_image) → ∀ (t u : F), ⁅ ⸨αβ, i, t⸩, ⸨βψ, j, u⸩ ⁆ = 1 := by
  intro h_in_image t u
  have : ∃ ijk' : ℕ × ℕ × ℕ, ijk' ∈ boolean_cube ∧ f_ij_jk ijk' = (i, j) := by
    rw [← Finset.mem_image, correct_of_ij_jk_image]; exact h_in_image
  simp [f_ij_jk] at this
  rcases this with ⟨ i', j', k', ⟨ hi', hj', hk' ⟩, rfl, rfl ⟩
  rw [← hom_lift_of_comm_of_αβ_βψ i' j' k' hi' hj' hk' t u]

private lemma comm_of_αβ_βψ_20 : ∀ (t u : F), ⁅ ⸨αβ, 2, t⸩, ⸨βψ, 0, u⸩ ⁆ = 1 := by
  intro t u
  apply @trivial_comm_from_embedded_comm_and_pairs _ _ ⸨βψ, 1, u⸩ _ ⸨αβ, 1, t⸩
  grw [← raw_nonhom_lift_of_comm_of_αβ_βψ t 0 1 1 0 u]
  rw [← hom_lift_of_comm_of_αβ_βψ 1 1 0 (by trivial) (by trivial) (by trivial) t u]
  rw [← hom_lift_of_comm_of_αβ_βψ 0 1 0 (by trivial) (by trivial) (by trivial) t u]
  rw [← hom_lift_of_comm_of_αβ_βψ 1 0 0 (by trivial) (by trivial) (by trivial) t u]

private lemma comm_of_αβ_βψ_02 : ∀ (t u : F), ⁅ ⸨αβ, 0, t⸩, ⸨βψ, 2, u⸩⁆ = 1 := by
  intro t u
  apply triv_comm_symm.1
  apply @trivial_comm_from_embedded_comm_and_pairs _ _ ⸨αβ, 1, t⸩ _ (⸨βψ, 1, u + 1⸩ * ⸨βψ, 0, 1⸩)
  · mul_assoc_l
    rw [←triv_comm_symm.1 (raw_nonhom_lift_of_comm_of_αβ_βψ 0 t 1 1 u 1)]
    simp only [one_mul, mul_one, mul_zero, add_zero, zero_add]
    rw [add_comm u 1, id_of_αβ, one_mul]
  · rw [←triv_comm_symm.1 (hom_lift_of_comm_of_αβ_βψ 0 1 1 (by trivial) (by trivial) (by trivial) t u)]
  · apply triv_comm_mul_left
    rw [←triv_comm_symm.1 (hom_lift_of_comm_of_αβ_βψ 0 1 0 (by trivial) (by trivial) (by trivial) t (u + 1))]
    rw [←triv_comm_symm.1 (hom_lift_of_comm_of_αβ_βψ 1 0 0 (by trivial) (by trivial) (by trivial) t 1)]
  apply triv_comm_mul_left
  rw [←triv_comm_symm.1 (hom_lift_of_comm_of_αβ_βψ 0 0 1 (by trivial) (by trivial) (by trivial) t (u + 1))]
  rw [←triv_comm_symm.1 (hom_lift_of_comm_of_αβ_βψ 0 0 0 (by trivial) (by trivial) (by trivial) t 1)]

-- 8.115
theorem comm_of_αβ_βψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project ⟨αβ, βψ⟩ := by
  intro i j hi hj t u
  by_cases hij : (i, j) ∈ ij_jk_image
  · apply image_of_hom_lift_of_comm_of_αβ_βψ hi hj hij
  · have : (i = 0 ∧ j = 2) ∨ (i = 2 ∧ j = 0) := by
      simp [ij_jk_image] at hij
      ht
    rcases this with ( ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ )
    · rw [← comm_of_αβ_βψ_02 t u]
    · rw [← comm_of_αβ_βψ_20 t u]
declare_B3Large_trivial_span_expr_thm F αβ βψ

omit Fchar in
theorem defineThenReflect_eq_reflect_of_αβψ (g : GradedChevalleyGenerator B3LargePosRoot F)
  (h : g.ζ = αβψ) :
  (weakB3LargeGraded F).project (defineThenReflect (weakB3LargeGraded F) g)
    = (weakB3LargeGraded F).project (FreeGroup.of (reflect g)) := by
  rcases g with ⟨ ζ, i, hi, t ⟩
  simp only at h
  subst ζ
  simp only [defineThenReflect, MonoidHom.coe_comp, Function.comp_apply,
    FreeGroup.lift.of, reflect, ←def_of_αβψ]
  rw [weakB3LargeGraded]
  simp only
  rw [weak_define]
  simp only [map_mul, map_inv, FreeGroup.map.of, reflect, PositiveRootSystem.height, height]
  congr
  all_goals rw [refl_of_split_3_into_1_2]

omit Fchar in
theorem defineThenReflect_eq_reflect_of_α2β2ψ (g : GradedChevalleyGenerator B3LargePosRoot F)
  (h : g.ζ = α2β2ψ) :
  (weakB3LargeGraded F).project (defineThenReflect (weakB3LargeGraded F) g)
    = (weakB3LargeGraded F).project (FreeGroup.of (reflect g)) := by
  rcases g with ⟨ ζ, i, hi, t ⟩
  simp only at h
  subst ζ
  nth_rewrite 2 [←neg_neg t]
  simp only [defineThenReflect, MonoidHom.coe_comp, Function.comp_apply,
    FreeGroup.lift.of, reflect, ←def_of_α2β2ψ]
  rw [weakB3LargeGraded]
  simp only
  rw [weak_define]
  simp only [map_commutatorElement, FreeGroup.map.of, reflect, PositiveRootSystem.height, height]
  congr
  all_goals rw [refl_of_split_5_into_2_3]
