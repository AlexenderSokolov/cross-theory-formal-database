/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Mathlib.Data.Finset.Defs
import Mathlib.Data.Finset.Sigma

import Mathlib.Tactic.Use

namespace Steinberg

/-!

  Some helpful theorems and lemmas about the images of certain linear functions on small natural numbers.

-/

/-! ## General theorems -/

/-- Decompose a number `0 ≤ i ≤ n + m` into `i₁ + i₂`, where `0 ≤ i₁ ≤ n` and `0 ≤ i₂ ≤ m`. -/
theorem decompose (n m i : ℕ) (h : i ≤ (n+m)) : ∃ (i₁ i₂ : ℕ), i = i₁ + i₂ ∧ i₁ ≤ n ∧ i₂ ≤ m := by
  by_cases i ≤ n
  · use i, 0
    omega
  · use n, i-n
    omega

/-! ## Specific decomposition theorems. -/

def booleans : Finset ℕ := {0, 1}
def boolean_square : Finset (ℕ × ℕ) := booleans ×ˢ booleans
def boolean_cube : Finset (ℕ × ℕ × ℕ) := booleans ×ˢ booleans ×ˢ booleans

@[simp]
lemma le_of_mem_booleans {i : ℕ}
    : i ∈ booleans ↔ i ≤ 1 := by
  simp only [booleans, Finset.mem_insert, Finset.mem_singleton]
  omega

@[simp]
lemma le_of_mem_boolean_square {i j : ℕ}
    : (i, j) ∈ boolean_square ↔ (i ≤ 1 ∧ j ≤ 1) := by
  simp only [boolean_square, Finset.mem_product, le_of_mem_booleans]

@[simp]
lemma le_of_mem_boolean_cube {i j k : ℕ}
    : (i, j, k) ∈ boolean_cube ↔ (i ≤ 1 ∧ j ≤ 1 ∧ k ≤ 1) := by
  simp only [boolean_cube, Finset.mem_product, le_of_mem_booleans]

private lemma decompose_3_into_booleans_1_2_helper :
  Finset.image (fun ⟨i, j⟩ => i + 2 * j) boolean_square = Finset.range 4 := by decide

/-- Over `ℕ`, every `i ≤ 3` can be written as `i = i₁ + 2 * i₂` for `i₁, i₂ ≤ 1`. -/
lemma decompose_3_into_booleans_1_2 (i : ℕ) (hi : i ≤ 3)
    : ∃ (i₁ i₂ : ℕ), i = i₁ + 2 * i₂ ∧ i₁ ≤ 1 ∧ i₂ ≤ 1 := by
  have := Finset.mem_range_succ_iff.mpr hi
  simp only [← decompose_3_into_booleans_1_2_helper, Finset.mem_image,
    Prod.exists, le_of_mem_boolean_square] at this
  tauto

private lemma decompose_5_into_booleans_1_2_2_helper :
  Finset.image (fun ⟨i, j, k⟩ => i + 2 * j + 2 * k) boolean_cube = Finset.range 6 := by decide

/-- Over `ℕ`, every `i ≤ 5` can be written as `i = i₁ + 2 * i₂ + 2 * i₃` for `i₁, i₂, i₃ ≤ 1`. -/
lemma decompose_5_into_booleans_1_2_2 (i : ℕ) (hi : i ≤ 5)
    : ∃ (i₁ i₂ i₃ : ℕ), i = i₁ + 2 * i₂ + 2 * i₃ ∧ i₁ ≤ 1 ∧ i₂ ≤ 1 ∧ i₃ ≤ 1 := by
  have := Finset.mem_range_succ_iff.mpr hi
  simp only [Nat.succ_eq_add_one, Nat.reduceAdd, ← decompose_5_into_booleans_1_2_2_helper,
    Finset.mem_image, Prod.exists, le_of_mem_boolean_cube] at this
  tauto

def f_ij_jk : ℕ × ℕ × ℕ → ℕ × ℕ := (fun ijk' : ℕ × ℕ × ℕ => let ( i', j', k' ) := ijk'; (i' + j', j' + k'))
def ij_jk_image : Finset (ℕ × ℕ) := {(0, 0), (0, 1), (1, 0), (1, 1), (1, 2), (2, 1), (2, 2)}

/-- Over `ℕ`, every `i, j ≤ 2` can be written as `(i, j) = (a + b, b + c)` for `a, b, c ≤ 1`,
except for `(i, j) = (2, 0)` and `(i, j) = (0, 2)`. -/
lemma correct_of_ij_jk_image : (Finset.image f_ij_jk boolean_cube) = ij_jk_image := by decide

end Steinberg
