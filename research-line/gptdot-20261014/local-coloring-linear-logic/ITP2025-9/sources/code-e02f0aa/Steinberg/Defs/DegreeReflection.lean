/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Steinberg.Defs.GradedPartialChevalleyGroup
import Steinberg.Upstream.PresentedGroup

import Mathlib.GroupTheory.Commutator.Basic

/-!

  File dox go here.

-/

namespace Steinberg

open PositiveRootSystem GradedPartialChevalley GradedChevalleyGenerator GradedPartialChevalleyGroup
open Set

variable {G : Type TG} [Group G]
         {Φ : Type TΦ} [PositiveRootSystem Φ]
         {R : Type TR} [Ring R]

/-- "Degree-reflection" map on `GradedGenerator` elements corresponding to replacing
degree `i` with `height ζ - i`. -/
def reflect (g : GradedChevalleyGenerator Φ R) : GradedChevalleyGenerator Φ R :=
  GradedChevalleyGenerator.mk g.ζ (height g.ζ - g.i) (by ht) g.t

/-- Reflection on generators is an involution, though we will not need this fact. -/
example (g : GradedChevalleyGenerator Φ R) : reflect (reflect g) = g := by
  let ⟨ ζ, i, hi, t ⟩ := g;
  unfold reflect
  congr
  exact Nat.sub_sub_self hi

/-- Composition of the reflection map with the definition map in a `GradedPartialChevalleyGroup`. The effect
of this map is to simply apply `reflect` to present generator and more generally to reflect the definition of all
generators. -/
def defineThenReflect (w : GradedPartialChevalleyGroup Φ R)
    : GradedChevalleyGenerator Φ R → FreeGroup (GradedChevalleyGenerator Φ R) :=
  (FreeGroup.map reflect) ∘ w.define

/- Defining-then-reflecting a present generator is the same as just reflecting the generator. -/
theorem defineThenReflect_eq_reflect_of_mem_presentRoots (w : GradedPartialChevalleyGroup Φ R)
      (g : GradedChevalleyGenerator Φ R) (h : g.ζ ∈ w.sys.presentRoots)
    : defineThenReflect w g = FreeGroup.of (reflect g) := by
  simp only [defineThenReflect, MonoidHom.coe_comp, Function.comp_apply, FreeGroup.lift.of]
  have : w.define g = FreeGroup.of g := by exact w.h_define_of_present h
  rw [this]
  simp only [FreeGroup.map.of]

/-! ### Generic reflection theorems

These theorems state that the relations which arise in a `GradedPartialChevalleyGroup` from its
`PartialChevalleySystem` are always closed under defining-then-reflecting. (Note that these
relations always only involve present roots.)
-/

/-- Defining-then-reflecting preserves the set of trivial commutator relations for any root pair. -/
private theorem defineThenReflect_eq_reflect_of_trivialSpanRelationsOfRootPair_of_mem_presentRoots (ζ η : Φ)
  (h_ζ : ζ ∈ w.sys.presentRoots) (h_η : η ∈ w.sys.presentRoots)
    : ∀ r ∈ trivialSpanRelationsOfRootPair R (ζ, η),
      (FreeGroup.lift (defineThenReflect w)) r ∈ trivialSpanRelationsOfRootPair R (ζ, η) := by
  intro r h
  simp only [trivialSpanRelationsOfRootPair, mem_setOf_eq] at h
  rcases h with ⟨ i, j, hi, hj, t, u, rfl ⟩
  simp only [map_commutatorElement, FreeGroup.lift.of]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk ζ i hi t) h_ζ]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk η j hj u) h_η]
  exists (height ζ - i), (height η - j), (by omega), (by omega), t, u

/-- Defining-then-reflecting preserves the set of single commutator relations for any root pair. -/
-- TODO: maybe we can replace with passing the generator directly, it'll be shorter
private theorem defineThenReflect_eq_reflect_of_singleSpanRelationsOfRootPair_of_mem_presentRoots
  (ζ η θ : Φ) (C : ℤ) (h_height : height θ = height ζ + height η)
  (h_ζ : ζ ∈ w.sys.presentRoots) (h_η : η ∈ w.sys.presentRoots) (h_θ : θ ∈ w.sys.presentRoots)
    : ∀ r ∈ singleSpanRelationsOfRootPair R ⟨ ζ, η, θ, C, h_height ⟩,
      (FreeGroup.lift (defineThenReflect w)) r ∈ singleSpanRelationsOfRootPair R ⟨ ζ, η, θ, C, h_height ⟩ := by
  intro r h
  simp only [singleSpanRelationsOfRootPair, mem_setOf_eq] at h
  rcases h with ⟨ i, j, hi, hj, t, u, rfl ⟩
  simp only [map_mul, map_commutatorElement, FreeGroup.lift.of, map_inv]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk ζ i hi t) h_ζ]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk η j hj u) h_η]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk θ (i + j) (by omega) (C * t * u)) h_θ]
  exists (height ζ - i), (height η - j), (by omega), (by omega), t, u
  congr
  simp only
  omega

/-- Defining-then-reflecting preserves the set of trivial commutator relations for any root pair. -/
private theorem defineThenReflect_eq_reflect_of_doubleSpanRelationsOfRootPair_of_mem_presentRoots
  (ζ η θ₁ θ₂ : Φ) (C₁ C₂ : ℤ) (h_height₁ : height θ₁ = height ζ + height η) (h_height₂ : height θ₂ = height ζ + 2 * height η)
  (h_ζ : ζ ∈ w.sys.presentRoots) (h_η : η ∈ w.sys.presentRoots) (h_θ₁ : θ₁ ∈ w.sys.presentRoots) (h_θ₂ : θ₂ ∈ w.sys.presentRoots)
    : ∀ r ∈ doubleSpanRelationsOfRootPair R ⟨ ζ, η, θ₁, θ₂, C₁, C₂, h_height₁, h_height₂ ⟩,
      (FreeGroup.lift (defineThenReflect w)) r ∈ doubleSpanRelationsOfRootPair R ⟨ ζ, η, θ₁, θ₂, C₁, C₂, h_height₁, h_height₂ ⟩ := by
  intro r h
  simp only [doubleSpanRelationsOfRootPair, mem_setOf_eq] at h
  rcases h with ⟨ i, j, hi, hj, t, u, rfl ⟩
  simp only [mul_inv_rev, map_mul, map_commutatorElement, FreeGroup.lift.of, map_inv]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk ζ i hi t) h_ζ]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk η j hj u) h_η]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk θ₁ (i + j) (by omega) (C₁ * t * u)) h_θ₁]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk θ₂ (i + 2 * j) (by omega) (C₂ * t * u * u)) h_θ₂]
  exists (height ζ - i), (height η - j), (by omega), (by omega), t, u
  simp only [mul_inv_rev]
  congr
  all_goals (ht)

/-- Defining-then-reflecting preserves the set of mixed-degree commutator relations for any root. -/
private theorem defineThenReflect_eq_reflect_of_mixedDegRelationsOfRoot_of_mem_presentRoots (ζ : Φ) (h_ζ : ζ ∈ w.sys.presentRoots) :
  ∀ r ∈ mixedDegreeRelationsOfRoot R ζ,
    (FreeGroup.lift (defineThenReflect w)) r ∈ mixedDegreeRelationsOfRoot R ζ := by
  intro r h
  simp only [mixedDegreeRelationsOfRoot, mem_setOf_eq] at h
  rcases h with ⟨ i, j, hi, hj, t, u, rfl ⟩
  simp only [map_commutatorElement, FreeGroup.lift.of]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk ζ i hi t) h_ζ]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk ζ j hj u) h_ζ]
  exists (height ζ - i), (height ζ - j), (by omega), (by omega), t, u

/-- Defining-then-reflecting preserves the set of linearity relations for any root. -/
private theorem defineThenReflect_eq_reflect_of_linearityRelationsOfRoot_of_mem_presentRoots (ζ : Φ) (h_ζ : ζ ∈ w.sys.presentRoots) :
  ∀ r ∈ linearityRelationsOfRoot R ζ,
    (FreeGroup.lift (defineThenReflect w)) r ∈ linearityRelationsOfRoot R ζ := by
  intro r h
  simp only [linearityRelationsOfRoot, mem_setOf_eq] at h
  rcases h with ⟨ i, hi, t, u, rfl ⟩
  simp only [map_mul, FreeGroup.lift.of, map_inv]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk ζ i hi t) h_ζ]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk ζ i hi u) h_ζ]
  rw [defineThenReflect_eq_reflect_of_mem_presentRoots w (GradedChevalleyGenerator.mk ζ i hi (t + u)) h_ζ]
  exists (height ζ - i), (by omega), t, u

/-! ### Establishing the reflection map -/

/-- The following proposition supposes that the reflected definitions of lifted relations vanish.
It is used as a hypothesis to define the reflection map. -/
def reflectValidProp (w : GradedPartialChevalleyGroup Φ R) :=
  (∀ S ∈ w.liftedRelationsSets, ∀ r ∈ S, w.project ((FreeGroup.lift (defineThenReflect w)) r) = 1)

private theorem lift_of_refl_eq_comp (w : GradedPartialChevalleyGroup Φ R) : FreeGroup.lift (defineThenReflect w) = (FreeGroup.map reflect).comp (FreeGroup.lift w.define)
  := by
  ext a : 1
  simp_all only [FreeGroup.lift.of, MonoidHom.coe_comp, Function.comp_apply]
  rfl

-- TODO: can we handle the first five cases uniformly?
private theorem eq_one_of_defineThenReflect_lift_allRelations_of_reflectValidProp
  {w : GradedPartialChevalleyGroup Φ R} (h' : reflectValidProp w) :
    ∀ r ∈ w.allRelations, w.project (FreeGroup.lift (defineThenReflect w) r) = 1 := by
  nth_rewrite 1 [allRelations]
  intro r h_r
  simp only [mem_iUnion] at h_r
  rcases h_r with ⟨ K, h_r ⟩
  rcases K
  all_goals simp only at h_r
  · apply eq_one_of_mem_rels
    simp only [mem_iUnion, exists_prop, Prod.exists] at h_r
    rcases h_r with ⟨ ζ, η, h_in_pairs, h_t_in_rels ⟩
    simp only [allRelations, mem_iUnion]
    use GradedSteinbergRelationClass.TrivialSpan
    simp only [mem_iUnion, exists_prop, Prod.exists]
    use ζ, η, h_in_pairs
    exact defineThenReflect_eq_reflect_of_trivialSpanRelationsOfRootPair_of_mem_presentRoots
      ζ η (w.sys.h_trivial_valid (ζ, η) h_in_pairs).1 (w.sys.h_trivial_valid (ζ, η) h_in_pairs).2 r h_t_in_rels
  · apply eq_one_of_mem_rels
    simp only [mem_iUnion, exists_prop, Sigma.exists, PProd.exists] at h_r
    rcases h_r with ⟨ ζ, η, θ, C, h_height, h_in_pairs, h_t_in_rels ⟩
    simp only [allRelations, mem_iUnion]
    use GradedSteinbergRelationClass.SingleSpan
    simp only [mem_iUnion, exists_prop, Prod.exists]
    use ⟨ ζ, η, θ, C, h_height ⟩, h_in_pairs
    exact defineThenReflect_eq_reflect_of_singleSpanRelationsOfRootPair_of_mem_presentRoots
      ζ η θ C h_height
      (w.sys.h_single_valid ⟨ ζ, η, θ, C, h_height ⟩ h_in_pairs).1 (w.sys.h_single_valid ⟨ ζ, η, θ, C, h_height ⟩ h_in_pairs).2.1
      (w.sys.h_single_valid ⟨ ζ, η, θ, C, h_height ⟩ h_in_pairs).2.2
      r h_t_in_rels
  · apply eq_one_of_mem_rels
    simp only [mem_iUnion, exists_prop, Sigma.exists, PProd.exists] at h_r
    rcases h_r with ⟨ ζ, η, θ₁, θ₂, ⟨ C₁, C₂, h_height₁, h_height₂ ⟩ , h_in_pairs, h_t_in_rels ⟩
    simp only [allRelations, mem_iUnion]
    use GradedSteinbergRelationClass.DoubleSpan
    simp only [mem_iUnion, exists_prop, Prod.exists]
    use ⟨ ζ, η, θ₁, θ₂, C₁, C₂, h_height₁, h_height₂ ⟩, h_in_pairs
    exact defineThenReflect_eq_reflect_of_doubleSpanRelationsOfRootPair_of_mem_presentRoots ζ η θ₁ θ₂ C₁ C₂ h_height₁ h_height₂
      (w.sys.h_double_valid ⟨ ζ, η, θ₁, θ₂, C₁, C₂, h_height₁, h_height₂ ⟩ h_in_pairs).1
      (w.sys.h_double_valid ⟨ ζ, η, θ₁, θ₂, C₁, C₂, h_height₁, h_height₂ ⟩ h_in_pairs).2.1
      (w.sys.h_double_valid ⟨ ζ, η, θ₁, θ₂, C₁, C₂, h_height₁, h_height₂ ⟩ h_in_pairs).2.2.1
      (w.sys.h_double_valid ⟨ ζ, η, θ₁, θ₂, C₁, C₂, h_height₁, h_height₂ ⟩ h_in_pairs).2.2.2
      r h_t_in_rels
  · apply eq_one_of_mem_rels
    simp only [mem_iUnion, exists_prop, Prod.exists] at h_r
    rcases h_r with ⟨ ζ, h_in_present, h_t_in_rels ⟩
    simp only [allRelations, mem_iUnion]
    use GradedSteinbergRelationClass.MixedDegree
    simp only [mem_iUnion, exists_prop, Prod.exists]
    use ζ, h_in_present
    exact defineThenReflect_eq_reflect_of_mixedDegRelationsOfRoot_of_mem_presentRoots ζ h_in_present r h_t_in_rels
  · apply eq_one_of_mem_rels
    simp only [mem_iUnion, exists_prop, Prod.exists] at h_r
    rcases h_r with ⟨ ζ, h_in_present, h_t_in_rels ⟩
    simp only [allRelations, mem_iUnion]
    use GradedSteinbergRelationClass.Linearity
    simp only [mem_iUnion, exists_prop, Prod.exists]
    use ζ, h_in_present
    exact defineThenReflect_eq_reflect_of_linearityRelationsOfRoot_of_mem_presentRoots ζ h_in_present r h_t_in_rels
  · rcases h_r with ⟨ T, ⟨ h_T, h_t_T ⟩ ⟩
    exact h' T h_T r h_t_T
  · simp only [definitionRelations, mem_setOf_eq] at h_r
    rcases h_r with ⟨ S, h_S, h_r ⟩
    simp only [mem_range, SetLike.mem_coe] at h_S
    rcases h_S with ⟨ ζ, h_ζ ⟩
    subst S
    simp only [mem_setOf_eq] at h_r
    rcases h_r with ⟨ i, hi, t, h ⟩
    subst r
    simp only [lift_of_refl_eq_comp, map_mul, map_inv, MonoidHom.coe_comp, Function.comp_apply,
      FreeGroup.lift.of, w.h_define_is_projection, inv_mul_cancel]
    rfl

/-- A homomorphism from a `GradedPartialChevalleyGroup` to itself, assuming `reflectValidProp` holds. -/
def defineThenReflectOfPresentedGroup {w : GradedPartialChevalleyGroup Φ R} (h : reflectValidProp w) : group w →* group w :=
  toPresentedGroup (eq_one_of_defineThenReflect_lift_allRelations_of_reflectValidProp h)

/-- Defining-then-reflecting commutes with projection. -/
theorem defineThenReflectOfPresentedGroup_of_project {w : GradedPartialChevalleyGroup Φ R} {h : reflectValidProp w}
  {g : FreeGroup (GradedChevalleyGenerator Φ R)} :
    defineThenReflectOfPresentedGroup h (w.project g) = w.project (FreeGroup.lift (defineThenReflect w) g) := by
  simp only [defineThenReflectOfPresentedGroup, project, toPresentedGroup.mk]

end Steinberg
