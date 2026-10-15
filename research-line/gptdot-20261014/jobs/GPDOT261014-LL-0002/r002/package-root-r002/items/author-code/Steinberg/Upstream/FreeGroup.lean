/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Mathlib.GroupTheory.FreeGroup.Basic

theorem lift.hom (α β G : Type u) [Group G] (f : α → FreeGroup β) (g : FreeGroup β →* G) :
  FreeGroup.lift (g ∘ f) = g.comp (FreeGroup.lift f) := by
  ext a
  simp only [FreeGroup.lift.of, Function.comp_apply, MonoidHom.coe_comp]
