/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Steinberg.Defs.PartialChevalleyGroup
import Steinberg.Defs.GradedPartialChevalleyGroup
import Steinberg.Defs.DegreeReflection
import Steinberg.Defs.DecomposeFixed

import Mathlib.Tactic.DeriveFintype

/-!

  File dox.

-/

namespace Steinberg.B3Small

open Steinberg PartialChevalley GradedPartialChevalley GradedChevalleyGenerator
  PartialChevalleySystem

/-! # The B3-small positive root system -/

inductive B3SmallPosRoot
  | β | ψ | ω | βψ | ψω | β2ψ | βψω
deriving Fintype, DecidableEq, Inhabited

namespace B3SmallPosRoot

@[reducible, height_simps]
def height : B3SmallPosRoot → Nat
  | β | ψ | ω => 1
  | βψ | ψω => 2
  | βψω | β2ψ => 3

def toString : B3SmallPosRoot → String
  | β => "β"
  | ψ => "ψ"
  | ω => "ω"
  | βψ => "β+ψ"
  | ψω => "ψ+ω"
  | βψω => "β+ψ+ω"
  | β2ψ => "β+2ψ"

instance : PositiveRootSystem B3SmallPosRoot where
  height := height
  toString := toString

instance instCoeNat : Coe B3SmallPosRoot Nat where
  coe r := height r

end B3SmallPosRoot

open B3SmallPosRoot

variable {F : Type TR} [Field F]

/-! # Definition of the 'weak' B3-small graded group -/

/-! ## Defining the 'weak' positive root system -/

abbrev weakPresentRoots : Set (B3SmallPosRoot) := {β, ψ, ω, βψ, ψω, β2ψ}

abbrev weakTrivialSpanPairs : Set (B3SmallPosRoot × B3SmallPosRoot) :=
  {(β, βψ), (β, β2ψ), (ψ, β2ψ), (βψ, β2ψ), (β, ω), (ψ, ψω), (ω, ψω)}

abbrev weakSingleSpanRootPairs : Set (SingleSpanRootPair B3SmallPosRoot)
   := {⟨ ψ, βψ, β2ψ, 2, (by ht)⟩, ⟨ψ, ω, ψω, 2, (by ht)⟩}

abbrev weakDoubleSpanRootPairs : Set (DoubleSpanRootPair B3SmallPosRoot) :=
    {⟨β, ψ, βψ, β2ψ, 1, 1, (by exact rfl), (by exact rfl)⟩}

abbrev weakB3SmallSystem := PartialChevalleySystem.mk
  weakPresentRoots
  weakTrivialSpanPairs
  weakSingleSpanRootPairs
  weakDoubleSpanRootPairs
  (by simp only [Set.mem_insert_iff, Set.mem_singleton_iff, forall_eq_or_imp, reduceCtorEq, or_self,
    or_false, or_true, and_self, forall_eq])
  (by simp only [Set.mem_insert_iff, Set.mem_singleton_iff, forall_eq_or_imp, reduceCtorEq, or_self,
    or_false, or_true, and_self, forall_eq])
  (by simp only [Set.mem_singleton_iff, Set.mem_insert_iff, forall_eq, reduceCtorEq, or_self,
    or_false, or_true, and_self])

/-! ## Lifted relations -/

/-
The specific relation arises from "nonhomogeneously lifting" the commutator of βψ and ψω elements. (There is no analogue
of this relation for other root-pairs, since all other present pairs lie in a common two-dimensional subspace.)
-/
def rels_of_nonhom_lift_of_comm_of_βψ_ψω :=
   { ⁅ {βψ, 2, t₁ * u₁} * {βψ, 1, t₁ * u₀ + t₀ * u₁} * {βψ, 0, t₀ * u₀},
       {ψω, 2, u₁ * v₁} * {ψω, 1, u₁ * v₀ + u₀ * v₁} * {ψω, 0, u₀ * v₀} ⁆
     | (t₁ : F) (t₀ : F) (u₁ : F) (u₀ : F) (v₁ : F) (v₀ : F) }

-- lifted commutator of βψ and ψω
def lifted_sets (F : Type TR) [Field F] : Set (Set (FreeGroup (GradedChevalleyGenerator B3SmallPosRoot F))) := {
  rels_of_nonhom_lift_of_comm_of_βψ_ψω
}

/-! ## Definition for missing root (βψω) -/

def weak_define (F : Type TR) [Field F] (g : GradedChevalleyGenerator B3SmallPosRoot F) : FreeGroup (GradedChevalleyGenerator B3SmallPosRoot F) :=
  let ⟨ ζ, i, hi, t ⟩ := g;
  match ζ with
  | βψω => ⁅ {β,(split_3_into_1_2 i (by ht)).1, g.t}'(correct_of_split_3_into_1_2 i (by ht)).1,
    {ψω, (split_3_into_1_2 i (by ht)).2, 1}'(correct_of_split_3_into_1_2 i (by ht)).2.1 ⁆
  | ζ => FreeGroup.of g

theorem weak_define_of_present (F : Type TR) [Field F] :
  ∀ {g : GradedChevalleyGenerator B3SmallPosRoot F}, g.ζ ∈ weakB3SmallSystem.presentRoots → weak_define F g = FreeGroup.of g := by
  intro g h_g_in_present
  rcases g with ⟨ ζ, i, hi, t ⟩
  cases ζ
  all_goals simp only [weak_define] -- this will close all present roots
  all_goals ( -- this will close the remaining (nonpresent) roots
    simp only [weakPresentRoots] at h_g_in_present
    contradiction
  )

theorem weak_define_is_projection (F : Type TR) [Field F] :
  ∀ {g : GradedChevalleyGenerator B3SmallPosRoot F}, (FreeGroup.lift (weak_define F)) (weak_define F g) = weak_define F g := by
  intro g
  rcases g with ⟨ ζ, i, hi, t ⟩
  cases ζ
  all_goals simp only [weak_define, FreeGroup.lift.of, map_commutatorElement]

def weakB3SmallGraded (F : Type TR) [Field F] := GradedPartialChevalleyGroup.mk
  weakB3SmallSystem
  (lifted_sets F)
  (weak_define F)
  (weak_define_of_present F)
  (weak_define_is_projection F)

/-! # Definition of the 'full' A3 ungraded and graded groups -/

abbrev fullPresentRoots : Set (B3SmallPosRoot) :=
  weakPresentRoots ∪ {βψω}

abbrev fullTrivialSpanPairs : Set (B3SmallPosRoot × B3SmallPosRoot) :=
  weakTrivialSpanPairs ∪ {(βψ, ψω), (βψω, β), (βψω, ψ), (βψω, ω), (βψω, βψ), (βψω, β2ψ), (βψω, ψω), (ω, β2ψ), (ψω, β2ψ)}

abbrev fullSingleSpanRootPairs : Set (SingleSpanRootPair B3SmallPosRoot) :=
  weakSingleSpanRootPairs ∪ {⟨ β, ψω, βψω, 1, (by ht)⟩, ⟨βψ, ω, βψω, 2, (by ht)⟩}

abbrev fullDoubleSpanRootPairs : Set (DoubleSpanRootPair B3SmallPosRoot) :=
  weakDoubleSpanRootPairs

-- TODO: this should really be via 'decide', but we had issues with declaring PartialChevalleySystem as a Finset
theorem all_root_pairs_have_relation : everyRootPairInRootPairs B3SmallPosRoot fullTrivialSpanPairs fullSingleSpanRootPairs fullDoubleSpanRootPairs := by
  intro ζ η h_ne
  unfold toRootPairs fullTrivialSpanPairs weakTrivialSpanPairs fullSingleSpanRootPairs
    weakSingleSpanRootPairs fullDoubleSpanRootPairs weakDoubleSpanRootPairs
  simp only [Set.image_insert_eq, Set.image_singleton, Set.union_insert, Set.union_singleton, Prod.swap,
    Set.mem_insert_iff, Set.mem_singleton_iff]
  cases ζ
  all_goals (
    simp only [Prod.mk.injEq, reduceCtorEq, false_and, true_and, or_self, or_false, false_or]
    cases η
    all_goals trivial
  )

abbrev fullB3SmallSystem := PartialChevalleySystem.mkFull B3SmallPosRoot
  fullPresentRoots
  fullTrivialSpanPairs
  fullSingleSpanRootPairs
  fullDoubleSpanRootPairs
  (by decide)
  all_root_pairs_have_relation

def fullB3Small (R : Type TR) [Ring R] := PartialChevalleyGroup.fullMk B3SmallPosRoot R fullB3SmallSystem
def fullB3SmallGraded (R : Type TR) [Ring R] := GradedPartialChevalleyGroup.fullMk B3SmallPosRoot R fullB3SmallSystem

/-! # Notation and macros -/

/- Instantiate the `declare_thms` macros from `PartialChevalley.lean`. -/

-- TODO-B: TODO: Make this a macro to declare all at once for A3.
--     Something like: `declare_thms A3 weakB3SmallGraded F`

macro "declare_B3Small_trivial_span_expr_thm" F:term:arg r₁:term:arg r₂:term:arg : command =>
  `(command| declare_trivial_span_expr_thm weakB3SmallGraded $F $r₁ $r₂)

macro "declare_B3Small_trivial_span_of_root_pair_thms" F:term:arg r₁:term:arg r₂:term:arg : command =>
  `(command| declare_trivial_span_of_root_pair_thms weakB3SmallGraded $F $r₁ $r₂)

macro "declare_B3Small_single_span_expr_thms" F:term:arg r₁:term:arg r₂:term:arg r₃:term:arg n:num : command =>
  `(command| declare_single_span_expr_thms weakB3SmallGraded $F $r₁ $r₂ $r₃ $n)

macro "declare_B3Small_single_span_of_root_pair_thms" F:term:arg r₁:term:arg r₂:term:arg r₃:term:arg n:num : command =>
  `(command| declare_single_span_of_root_pair_thms weakB3SmallGraded $F $r₁ $r₂ $r₃ $n)

macro "declare_B3Small_lin_id_inv_thms" F:term:arg root:term:arg : command =>
  `(command| declare_lin_id_inv_thms weakB3SmallGraded $F $root)

macro "declare_B3Small_mixed_expr_thm" F:term:arg r:term:arg : command =>
  `(command| declare_mixed_degree_expr_thm weakB3SmallGraded $F $r)

macro "declare_B3Small_mixed_degree_thms" F:term:arg r:term:arg : command =>
  `(command| declare_mixed_degree_thms weakB3SmallGraded $F $r)

macro "declare_B3Small_defineThenReflect_thm" F:term:arg r:term:arg : command =>
  `(command| declare_defineThenReflect_thm weakB3SmallGraded $F B3SmallPosRoot $r)

-- r₁ is the larger root, as opposed to the above macros
macro "declare_B3Small_reflected_thm"
    F:term:arg v:term:arg r₁:term:arg r₂:term:arg r₃:term:arg
    "const" C:num
    "heights" n₁:num n₂:num n₃:num
    "to" n₄:num n₅:num n₆:num : command =>
  `(command| declare_reflected_thm weakB3SmallGraded $F $v $r₁ $r₂ $r₃ 0 $C $n₁ $n₂ $n₃ $n₄ $n₅ $n₆)

macro "declare_B3Small_triv_comm_reflected_thm"
    F:term:arg v:term:arg r₁:term:arg r₂:term:arg
    "heights" n₁:num n₂:num
    "to" n₃:num n₄:num : command =>
  `(command| declare_triv_comm_reflected_thm weakB3SmallGraded $F $v $r₁ $r₂ $n₁ $n₂ $n₃ $n₄)

set_option hygiene false in
/-- Shorthand for building free group elements from a root, degree, and ring element. -/
scoped notation (priority:=high) "⸨" ζ ", " i ", " t "⸩" =>
  (weakB3SmallGraded F).project {ζ, i, t}

set_option hygiene false in
/-- Shorthand for building free group elements from a root, degree, and ring element. -/
scoped notation (priority:=high) "⸨" ζ ", " i ", " t "⸩'" h:max =>
  (weakB3SmallGraded F).project ({ζ, i, t}'h)

section forallNotation

set_option hygiene false

scoped notation "forall_i_t" h:max "," e =>
  ∀ ⦃i : ℕ⦄ (hi : i ≤ h) (t : F), e

scoped notation "forall_ij_tu" h₁:max h₂:max "," e =>
  ∀ ⦃i j : ℕ⦄ (hi : i ≤ h₁) (hk : j ≤ h₂) (t u : F), e

scoped notation "forall_ik_tuv" h₁:max h₂:max "," e =>
  ∀ ⦃i k : ℕ⦄ (hi : i ≤ h₁) (hk : k ≤ h₂) (t u v : F), e

scoped notation "forall_ijk_tu" h₁:max h₂:max h₃:max "," e =>
  ∀ ⦃i j k : ℕ⦄ (hi : i ≤ h₁) (hj : j ≤ h₂) (hk : k ≤ h₃) (t u : F), e

scoped notation "forall_ijk_tuv" h₁:max h₂:max h₃:max "," e =>
  ∀ ⦃i j k : ℕ⦄ (hi : i ≤ h₁) (hj : j ≤ h₂) (hk : k ≤ h₃) (t u v : F), e

end forallNotation

macro "hom_tac " rel:ident " [" intros:ident,* "]" : tactic => `(tactic|
  ( intros $intros*;
    apply GradedPartialChevalleyGroup.helper;
    apply (weakB3SmallGraded _).liftedProp_of_mem_lifted $rel;
    simp only [weakB3SmallGraded, lifted_sets, Set.mem_insert_iff,
      Set.mem_singleton_iff, true_or, or_true];
    exists $intros,* ))

end Steinberg.B3Small
