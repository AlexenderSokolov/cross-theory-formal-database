/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Mathlib.GroupTheory.PresentedGroup

import Steinberg.Upstream.FreeGroup

/-- A free group element is in the normal closure of the set of relations iff its image
vanishes in the presented group. -/
theorem eq_one_iff_mem_closure {α : Type u} {rels : Set (FreeGroup α)} {x : FreeGroup α} :
  PresentedGroup.mk rels x = 1 ↔ x ∈ Subgroup.normalClosure rels := by
  nth_rewrite 2 [← one_mul x, ← inv_one]
  apply Iff.trans _ (@QuotientGroup.eq _ _ (Subgroup.normalClosure rels) 1 x)
  simp only [QuotientGroup.mk_one, PresentedGroup.mk, MonoidHom.coe_mk, OneHom.coe_mk]
  use Eq.symm, Eq.symm

/-- If a free group element is included in the set of relations, then its image
vanishes in the presented group. -/
theorem eq_one_of_mem_rels {α : Type u} {rels : Set (FreeGroup α)} {x : FreeGroup α} :
  x ∈ rels → PresentedGroup.mk rels x = 1 := by
  intro h
  apply eq_one_iff_mem_closure.mpr
  exact Subgroup.subset_normalClosure h

private theorem helper {α β : Type u} {S : Set (FreeGroup α)} {T : Set (FreeGroup β)} {f : α → FreeGroup β}
  (h : ∀ r ∈ S, (PresentedGroup.mk T) (FreeGroup.lift f r) = 1) :
    ∀ r ∈ S, (FreeGroup.lift ((PresentedGroup.mk T) ∘ f) r) = 1 := by
  intro r h_r
  rw [lift.hom, MonoidHom.coe_comp, Function.comp_apply]
  exact h r h_r

/-- Build a homomorphism between `PresentedGroup`s by specifying the image of
every generator in the source as a product of generators in the target. Requires
a well-definedness hypothesis, namely, that the image (suitably defined)
of every assumed relation in the source vanishes in the target. -/
def toPresentedGroup {α β : Type u} {S : Set (FreeGroup α)} {T : Set (FreeGroup β)} {f : α → FreeGroup β}
  (h : ∀ r ∈ S, (PresentedGroup.mk T) (FreeGroup.lift f r) = 1) : PresentedGroup S →* PresentedGroup T :=
  PresentedGroup.toGroup (helper h)

/-- Apply `toPresentedGroup` to a generator. -/
theorem toPresentedGroup.of {α β : Type u} {S : Set (FreeGroup α)} {T : Set (FreeGroup β)} {f : α → FreeGroup β}
  (h : ∀ r ∈ S, (PresentedGroup.mk T) (FreeGroup.lift f r) = 1) (x : α) :
  (toPresentedGroup h) (PresentedGroup.of x) = PresentedGroup.mk T (f x) := by
  rw [toPresentedGroup, PresentedGroup.toGroup.of]
  simp only [Function.comp_apply]

private theorem toPresentedGroup.mk' {α β : Type u} {S : Set (FreeGroup α)} {T : Set (FreeGroup β)} {f : α → FreeGroup β}
  (h : ∀ r ∈ S, (PresentedGroup.mk T) (FreeGroup.lift f r) = 1) :
  (toPresentedGroup h).comp (PresentedGroup.mk S) = (PresentedGroup.mk T).comp (FreeGroup.lift f) := by
  ext a
  simp only [MonoidHom.coe_comp, Function.comp_apply, FreeGroup.lift.of]
  rw [← PresentedGroup.of]
  exact toPresentedGroup.of h a

/-- Apply `toPresentedGroup` to the image of a free group element in a presented group. -/
theorem toPresentedGroup.mk {α β : Type u} {S : Set (FreeGroup α)} {T : Set (FreeGroup β)} {f : α → FreeGroup β}
  (h : ∀ r ∈ S, (PresentedGroup.mk T) (FreeGroup.lift f r) = 1) (a : FreeGroup α) :
  (toPresentedGroup h) (PresentedGroup.mk S a) = PresentedGroup.mk T (FreeGroup.lift f a) := by
  have aux₁ : (toPresentedGroup h).comp (PresentedGroup.mk S) a = (toPresentedGroup h) (PresentedGroup.mk S a) := by
    simp only [MonoidHom.coe_comp, Function.comp_apply]
  have aux₂ : (PresentedGroup.mk T).comp (FreeGroup.lift f) a = PresentedGroup.mk T (FreeGroup.lift f a) := by
    simp only [MonoidHom.coe_comp, Function.comp_apply]
  rw [←aux₁, ←aux₂, toPresentedGroup.mk']
