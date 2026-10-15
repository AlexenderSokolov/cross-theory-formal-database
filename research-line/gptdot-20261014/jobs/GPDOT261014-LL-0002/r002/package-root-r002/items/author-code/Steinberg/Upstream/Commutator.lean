/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Mathlib.Algebra.Group.Aut
import Mathlib.GroupTheory.Commutator.Basic

import Mathlib.Tactic.Group

/-!

  File dox go here.

-/

-- namespace Mathlib.GroupTheory.Commutator

/-! ### Notations for theorems involving group elements -/

/-
  These notations essentially act like "inline mathematical notation,"
  in the sense that using a `def` is too strong (i.e., it obscures
  the underlying notion behind a name that we would have to `unfold`
  or `rw` or supply `simp` lemmas for). Rather, this is shorthand
  for longer expressions that would otherwise take a while to type.
-/

namespace CommutatorNotation

/-- `triv_comm(x, y)` unfolds to `⁅ x, y ⁆ = 1`.  -/
notation "triv_comm" "( " x ", " y " )" => ⁅ x, y ⁆ = 1

/-- `commutes(x, y)` unfolds to `x * y = y * x`.  -/
notation "commutes" "( " x ", " y " )" => x * y = y * x

notation "comm_unfold" "( " x ", " y " )" => x * y * x⁻¹ * y⁻¹

/-- `reorder_left(x, y, z)` unfolds to `x * y = z * y * x`.  -/
notation "reorder_left" "( " x ", " y ", " z " )" => x * y = z * y * x
notation "reorder_mid" "( " x ", " y ", " z " )" => x * y = y * z * x
notation "reorder_right" "( " x ", " y ", " z " )" => x * y = y * x * z

end CommutatorNotation

open CommutatorNotation

variable {G : Type TG} [Group G]
         {w x y z : G}

/-! ### Theorems about commutators (holding in any group) -/

theorem comm_left      (x y : G) : x * y = ⁅x, y⁆ * y * x       := by group
theorem comm_mid       (x y : G) : x * y = y * ⁅x, y⁻¹⁆⁻¹ * x   := by group
theorem comm_right     (x y : G) : x * y = y * x * ⁅x⁻¹, y⁻¹⁆   := by group
theorem comm_swap      (x y : G) : ⁅x, y⁆⁻¹ = ⁅y, x⁆            := commutatorElement_inv _ _

theorem comm_left_rev  (x y : G) : x * y = ⁅y, x⁆⁻¹ * y * x     := commutatorElement_inv y _ ▸ comm_left ..
theorem comm_mid_rev   (x y : G) : x * y = y * ⁅y⁻¹, x⁆ * x     := (commutatorElement_inv x _).symm ▸ comm_mid ..
theorem comm_right_rev (x y : G) : x * y = y * x * ⁅y⁻¹, x⁻¹⁆⁻¹ := commutatorElement_inv y⁻¹ _ ▸ comm_right ..

theorem triv_comm_iff_commutes : triv_comm(x, y) ↔ commutes(x, y) := by
  constructor
  · intro h
    rw [comm_left, h, one_mul]
  · intro h
    rw [commutatorElement_def, h, mul_inv_cancel_right, mul_inv_cancel]

theorem eq_comm_of_reorder_left : reorder_left(x, y, z) → ⁅x, y⁆ = z := by
  intro h
  simp only [commutatorElement_def, h, mul_inv_cancel_right]

theorem reorder_left_of_eq_comm : ⁅x, y⁆ = z → reorder_left(x, y, z) := by
  rw [commutatorElement_def]
  rintro rfl
  simp_rw [inv_mul_cancel_right]

@[simp]
theorem reorder_left_iff_eq_comm : reorder_left(x, y, z) ↔ ⁅x, y⁆ = z :=
  ⟨eq_comm_of_reorder_left, reorder_left_of_eq_comm⟩

/- TODO-B: For these `triv_comm` theorems, I don't like the approach of the proofs.
   So far, the proofs are essentially just unfolding the trivial commutator
   definition and applying commutativity as needed. But this sidesteps the
   potential usefulness of a `triv_comm` definition.

   While some definition-unfolding is necessary to establish an API/starting
   set of lemmas, I think things can be reworked here to use more
   "commutator theory."
-/

-- TODO-B: Perhaps we can replace this with `triv_comm()`, but I think the statement is clearer this way.
@[symm]
theorem triv_comm_symm : ⁅ x, y ⁆ = 1 ↔ ⁅ y, x ⁆ = 1 := by
  simp_rw [triv_comm_iff_commutes]
  exact eq_comm

@[simp]
theorem inv_triv_comm_iff_triv_comm : triv_comm(x⁻¹, y) ↔ triv_comm(x, y) := by
  simp_rw [triv_comm_iff_commutes]
  apply Iff.intro
  · intro h
    apply @mul_left_cancel _ _ _ x⁻¹
    rw [inv_mul_cancel_left, ← mul_assoc, h, mul_assoc, inv_mul_cancel, mul_one]
  · intro h
    apply @mul_left_cancel _ _ _ x
    rw [mul_inv_cancel_left, ← mul_assoc, h, mul_assoc, mul_inv_cancel, mul_one]

@[simp]
theorem inv_triv_comm_iff_triv_comm' : triv_comm(x, y⁻¹) ↔ triv_comm(x, y) := by
  simp_rw [@triv_comm_symm _ _ x]
  exact inv_triv_comm_iff_triv_comm

-- TODO-B: Better name? Could be `triv_comm_trans_right` or `triv_comm_trans_mul_right`
theorem triv_comm_mul_right : triv_comm(x, y) → triv_comm(x, z) → triv_comm(x, y * z) := by
  simp_rw [triv_comm_iff_commutes]
  intro hxy hxz
  rw [← mul_assoc, hxy, mul_assoc, hxz, ← mul_assoc]

-- TODO-B: Better name? Could be `triv_comm_trans_left`
theorem triv_comm_mul_left : triv_comm(x, z) → triv_comm(y, z) → triv_comm(x * y, z) := by
  simp_rw [triv_comm_iff_commutes]
  intro hxz hyz
  rw [mul_assoc, hyz, ← mul_assoc, hxz, mul_assoc]

theorem trivial_comm_mul_mul : triv_comm(x, w) → triv_comm(x, z)
    → triv_comm(y, w) → triv_comm(y, z) → triv_comm(x * y, w * z) := by
  simp_rw [triv_comm_iff_commutes]
  intro hxw hxz hyw hyz
  -- TODO-B: Ripe for automation/a macro!
  rw [← mul_assoc, mul_assoc x, hyw, ← mul_assoc, hxw,
    mul_assoc, hyz, ← mul_assoc, mul_assoc w, hxz, ← mul_assoc, mul_assoc]

/- Deduce that two elements commute if one can "embed" them in a larger, trivial commutator where all other pairs commute. -/
theorem trivial_comm_from_embedded_comm_and_pairs : triv_comm(x * y, w * z) → triv_comm(x, w)
    → triv_comm(y, w) → triv_comm(y, z) → triv_comm(x, z) := by
  simp_rw [triv_comm_iff_commutes]
  intro h_all h_xw h_yw h_yz
  -- Add `y` on the right and `w` on the left to maintain relative orders wrt `x` and `z`
  apply @mul_right_cancel _ _ _ _ y
  apply @mul_left_cancel _ _ _ w
  simp only [←mul_assoc]
  rw [← h_xw, mul_assoc, ← h_yz, ← mul_assoc, mul_assoc x, ← h_yw, ← mul_assoc,
    mul_assoc, h_all, ← mul_assoc]

open MulAut -- to access conj function

-- Commutator identities
theorem CI1 : conj x y = ⁅x, y⁆ * y := by
  rw [commutatorElement_def, conj_apply, inv_mul_cancel_right]

theorem CI2 : ⁅y, x⁆ = ⁅x, y⁆⁻¹ := by
  simp only [commutatorElement_def, mul_inv_rev, inv_inv, mul_assoc]

theorem CI3 : ⁅x, y * z⁆ = ⁅x, y⁆ * conj y ⁅x, z⁆ := by
  simp only [conj_apply, commutatorElement_def, mul_inv_rev, ← mul_assoc,
    inv_mul_cancel_right]

theorem CI4 : ⁅x * y, z⁆ = conj x ⁅y, z⁆ * ⁅x, z⁆ := by
  simp only [conj_apply, commutatorElement_def, mul_inv_rev, ← mul_assoc,
    inv_mul_cancel_right]

theorem CI5 : conj x ⁅x⁻¹, y⁆ = ⁅y, x⁆ := by
  simp only [conj_apply, commutatorElement_def, mul_inv_rev, ← mul_assoc,
    inv_inv, mul_inv_cancel, one_mul]

theorem CI6 : ⁅y, z⁆ * ⁅x, z⁆ = ⁅x, ⁅y, z⁆⁆⁻¹ * ⁅x * y, z⁆ := by
  simp only [conj_apply, commutatorElement_def, mul_inv_rev, ← mul_assoc,
    inv_inv, mul_inv_cancel_right, inv_mul_cancel_right, CI2]

theorem CI7 : ⁅x, z⁆ = 1 → ⁅x, ⁅y, z⁆⁆ = ⁅⁅x, y⁆, conj y z⁆ := by
  intro h
  have hc : Commute x z := by
    apply (commute_iff_eq x z).mpr
    exact triv_comm_iff_commutes.mp h
  have h1 : Commute x⁻¹ z := Commute.inv_left hc
  rw [commute_iff_eq] at h1
  simp [commutatorElement_def, ← mul_assoc, conj_apply]
  simp [mul_assoc, h1]

theorem CI8 : ⁅y, z⁆ = 1 → ⁅⁅x, y⁆, z⁆ = conj (x * y) ⁅x⁻¹, z⁆ * ⁅x, z⁆ := by
  intro h
  have hc : Commute y z := by
    apply (commute_iff_eq y z).mpr
    exact triv_comm_iff_commutes.mp h
  have h1 : Commute y⁻¹ z := Commute.inv_left hc
  rw [commute_iff_eq] at h1
  simp [commutatorElement_def, ← mul_assoc, conj_apply]
  simp [mul_assoc, h1]

theorem CI9 : ⁅x, z⁆ = 1 → ⁅⁅x, y⁆, z⁆ = conj x (conj (y * x⁻¹) ⁅y⁻¹, z⁆ * ⁅y, z⁆) := by
  intro h
  have hc : Commute x z := by
    apply (commute_iff_eq x z).mpr
    exact triv_comm_iff_commutes.mp h
  have h1 : Commute x⁻¹ z := Commute.inv_left hc
  have h2: Commute x⁻¹ z⁻¹ := Commute.inv_inv_iff.mpr hc
  rw [commute_iff_eq] at h1 h2 hc
  simp [commutatorElement_def, ← mul_assoc, conj_apply]
  simp [mul_assoc, h1, h2, hc]

-- Hall Witt identities
theorem HW1 : ⁅⁅y, x⁆, conj x z⁆ * ⁅⁅x, z⁆, conj z y⁆ * ⁅⁅z, y⁆, conj y x⁆ = 1 := by
  simp only [commutatorElement_def, conj_apply, ← mul_assoc, inv_mul_cancel_right,
    mul_inv_rev, inv_inv, mul_inv_cancel_right, mul_inv_cancel]

theorem HW2 : (conj y ⁅⁅y⁻¹, x⁆, z⁆) * (conj z ⁅⁅z⁻¹, y⁆, x⁆) * (conj x ⁅⁅x⁻¹, z⁆, y⁆) = 1 := by
  simp only [commutatorElement_def, conj_apply, ← mul_assoc, inv_mul_cancel_right,
    mul_inv_rev, inv_inv, mul_inv_cancel_right, mul_inv_cancel, one_mul]

theorem commutatorElement_def' : ⁅ x, y ⁆ = (x * y) * (x⁻¹ * y⁻¹) := by group
