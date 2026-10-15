/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Mathlib.Tactic.Group
import Steinberg.Macro.Group

namespace Steinberg

variable {G H : Type TG} [Group G] [Group H]
         {w x y z : G}

-- Star operator
def starCommutator_def (x y : G) := y⁻¹ * x * y^2 * x⁻¹ * y⁻¹
infix:68 " ⋆ " => starCommutator_def

theorem star_commutator (x y : G) : (x ⋆ y) * ⁅(x ⋆ y)⁻¹, y⁆ = ⁅x, y^2⁆ := by
  unfold starCommutator_def
  group

theorem commutator_star (x y : G) : ⁅x ⋆ y, y⁆⁻¹ * (x ⋆ y) = ⁅x, y^2⁆ := by
  unfold starCommutator_def
  group

theorem starCommutator_helper {x y z : G} (w : G) (h1 : ⁅ x, y^2 ⁆ = z * w) (h2 : ⁅ z⁻¹, y ⁆ = w) :
  z = x ⋆ y := by
  unfold starCommutator_def
  subst w
  simp only [commutatorElement_def] at h1
  group at h1
  apply @mul_left_cancel _ _ _ y
  apply @mul_right_cancel _ _ _ _ y⁻¹
  group
  rw [←h1]

theorem map_starCommutator {x y : G} (f : G →* H) : f (x ⋆ y) = (f x) ⋆ (f y) := by
  unfold starCommutator_def
  simp only [map_pow, map_inv, map_mul]

end Steinberg
