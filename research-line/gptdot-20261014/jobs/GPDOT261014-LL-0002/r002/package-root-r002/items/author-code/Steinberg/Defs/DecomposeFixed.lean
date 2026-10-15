/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Mathlib.Data.Nat.Notation

/-!

  Some hardcoded decompositions of small natural numbers, needed to state the "definition" relations.

-/

namespace Steinberg

def split_3_into_1_2 (i : ℕ) (hi : i ≤ 3) :=
  match i with
  | 0 => (0, 0)
  | 1 => (0, 1)
  | 2 => (1, 1)
  | 3 => (1, 2)

theorem correct_of_split_3_into_1_2 (i : ℕ) (hi : i ≤ 3) :
  (split_3_into_1_2 i hi).1 ≤ 1 ∧ (split_3_into_1_2 i hi).2 ≤ 2 ∧ (split_3_into_1_2 i hi).1 + (split_3_into_1_2 i hi).2 = i := by
  simp only [split_3_into_1_2]
  split
  all_goals trivial

theorem refl_of_split_3_into_1_2 (i : ℕ) (hi : i ≤ 3) :
  split_3_into_1_2 (3-i) (by omega) = (1-(split_3_into_1_2 i hi).1, 2-(split_3_into_1_2 i hi).2) := by
  simp only [split_3_into_1_2]
  symm
  split
  all_goals trivial

def split_4_into_1_3 (i : ℕ) (hi : i ≤ 4) :=
  match i with
  | 0 => (0, 0)
  | 1 => (0, 1)
  | 2 => (1, 1)
  | 3 => (1, 2)
  | 4 => (1, 3)

/-!
Note that it is not possible to prove a `refl_of_split_4_into_1_3` theorem.
-/

theorem correct_of_split_4_into_1_3 (i : ℕ) (hi : i ≤ 4) :
  (split_4_into_1_3 i hi).1 ≤ 1 ∧ (split_4_into_1_3 i hi).2 ≤ 3 ∧ (split_4_into_1_3 i hi).1 + (split_4_into_1_3 i hi).2 = i := by
  simp only [split_4_into_1_3]
  split
  all_goals trivial

def split_5_into_2_3 (i : ℕ) (hi : i ≤ 5) :=
  match i with
  | 0 => (0, 0)
  | 1 => (0, 1)
  | 2 => (1, 1)
  | 3 => (1, 2)
  | 4 => (2, 2)
  | 5 => (2, 3)

theorem correct_of_split_5_into_2_3 (i : ℕ) (hi : i ≤ 5) :
  (split_5_into_2_3 i hi).1 ≤ 2 ∧ (split_5_into_2_3 i hi).2 ≤ 3 ∧ (split_5_into_2_3 i hi).1 + (split_5_into_2_3 i hi).2 = i := by
  simp only [split_5_into_2_3]
  split
  all_goals trivial

theorem refl_of_split_5_into_2_3 (i : ℕ) (hi : i ≤ 5) :
  split_5_into_2_3 (5-i) (by omega) = (2-(split_5_into_2_3 i hi).1, 3-(split_5_into_2_3 i hi).2) := by
  simp only [split_5_into_2_3]
  symm
  split
  all_goals trivial
