/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Steinberg.Macro.Group
import Mathlib.Data.Finset.Defs

namespace Steinberg

/-- A typeclass representing the roots in a positive root system.

For now, we do not encode anything about the additive structure of the roots
(except for requiring that a `height` function be supplied).
-/
class PositiveRootSystem (Root : semiOutParam (Type TΦ))
  extends
    ToString Root
  where
  height : Root → Nat

attribute [height_simps] PositiveRootSystem.height

open PositiveRootSystem

/-! ## Encoding Steinberg relations -/

/-- Dependent product type, where each element encodes a Steinberg relation between two roots which span *one* additional root.

Elements of this type have the form `⟨ ζ, η, θ, C, h ⟩`. This represents the following Steinberg relation:
* `ζ` and `η` are the original pair of roots,
* `θ = ζ + η`.
* `C` is the Chevalley constant.
(`h` is a well-definedness condition on the heights of the roots).

In the ungraded case, this tuple creates relations of the form
  `⁅ {ζ, t}, {η, u} ⁆ = {θ, C * t * u}`.
In the graded case, this tuple creates relations of the form
  `⁅ {ζ, i, t}, {η, j, u} ⁆ = {θ, i + j, C * t * u}`.
 -/
abbrev SingleSpanRootPair (Φ : Type TΦ) [PositiveRootSystem Φ] :=
  (ζ : Φ) × (η : Φ) × (θ : Φ) × ℤ ×' (height θ = height ζ + height η)

/-- Dependent product type, where each element encodes a Steinberg relation between two roots which span *two* additional roots.

Elements of this type have the form `⟨ ζ, η, θ₁, θ₂, C₁, C₂, h₁, h₂ ⟩`. This represents the following Steinberg relation:
* `ζ` and `η` are the original pair of roots,
* `θ₁ = ζ + η` and `θ₂ = ζ + 2η`.
* `C₁` and `C₂` are the respectively Chevalley constants.
(`h₁` and `h₂` are well-definedness conditions on the heights of the roots).

In the ungraded case, this tuple creates relations of the form
  `⁅ {ζ, t}, {η, u} ⁆ = {θ₁, C₁ * t * u} * {θ₂, C₂ * t * u^2}`.
In the graded case, this tuple creates relations of the form
  `⁅ {ζ, i, t}, {η, j, u} ⁆ = {θ₁, i + j, C₁ * t * u} * {θ₂, i + 2 * j, C₂ * t * u^2}`.
 -/
abbrev DoubleSpanRootPair (Φ : Type TΦ) [PositiveRootSystem Φ] := (
  (ζ : Φ) × (η : Φ) × (θ₁ : Φ) × (θ₂ : Φ)
  × ℤ × ℤ ×' (height θ₁ = height ζ + height η) ×' (height θ₂ = height ζ + 2 * height η)
)

/-- A structure encoding a (possibly strict) subset of Steinberg relations for the (graded or ungraded)
unipotent Chevalley groups on `Φ`. This structure is used to build `PartialChevalleyGroup`s and
`GradedPartialChevalleyGroup`s.
-/
structure PartialChevalleySystem (Φ : Type TΦ) [PositiveRootSystem Φ] where
  mk ::
  presentRoots : Set Φ
  trivialSpanRootPairs : Set (Φ × Φ)
  singleSpanRootPairs : Set (SingleSpanRootPair Φ)
  doubleCommutatorRootPairs : Set (DoubleSpanRootPair Φ)

  -- validity hypotheses (needed for degree reflection stuff)
  h_trivial_valid : ∀ p ∈ trivialSpanRootPairs,
    p.1 ∈ presentRoots ∧ p.2 ∈ presentRoots
  h_single_valid : ∀ p ∈ singleSpanRootPairs,
    p.1 ∈ presentRoots ∧ p.2.1 ∈ presentRoots ∧ p.2.2.1 ∈ presentRoots
  h_double_valid : ∀ p ∈ doubleCommutatorRootPairs,
    p.1 ∈ presentRoots ∧ p.2.1 ∈ presentRoots ∧ p.2.2.1 ∈ presentRoots ∧ p.2.2.2.1 ∈ presentRoots

  -- TODO: hypothesis stating that if a pair appears in one of these sets, neither it nor its swap appears again

namespace PartialChevalleySystem

/-! ### 'Full' systems -/

/-- Extract the set of all ordered pairs of roots for which there exists a commutator relation,
either trivial-span, single-span, or double-span. -/
def toRootPairs (Φ : Type TΦ) [PositiveRootSystem Φ] (trivialSpanRootPairs : Set (Φ × Φ)) (singleSpanRootPairs : Set (SingleSpanRootPair Φ))
  (doubleCommutatorRootPairs : Set (DoubleSpanRootPair Φ)) : Set (Φ × Φ) :=
  (fun p => (p.1, p.2)) '' trivialSpanRootPairs ∪ (fun p => (p.1, p.2.1)) '' singleSpanRootPairs
    ∪ (fun p => (p.1, p.2.1)) '' doubleCommutatorRootPairs

/-- Proposition that every pair of (distinct) roots in `Φ` appears in `toRootPairs` (or its swap does).
Ensures that a "full" `PartialChevalleySystem` is indeed full, for sanity checking. -/
def everyRootPairInRootPairs (Φ : Type TΦ) [PositiveRootSystem Φ]
  (trivialSpanRootPairs : Set (Φ × Φ)) (singleSpanRootPairs : Set (SingleSpanRootPair Φ))
  (doubleCommutatorRootPairs : Set (DoubleSpanRootPair Φ)) : Prop :=
  ∀ (ζ η : Φ), ζ ≠ η →
   (ζ, η) ∈ toRootPairs Φ trivialSpanRootPairs singleSpanRootPairs doubleCommutatorRootPairs
    ∪ Prod.swap '' toRootPairs Φ trivialSpanRootPairs singleSpanRootPairs doubleCommutatorRootPairs

/-- Build a "full" `PartialChevalleySystem`. This allows you to omit the validity hypotheses,
instead passing a hypothesis that every root in `Φ` is contained in `presentRoots`.
For sanity checking, we also require a hypothesis that `everyRootPairInRootPairs` holds.
 -/
def mkFull (Φ : Type TΦ) [PositiveRootSystem Φ]
  (presentRoots : Set Φ) (trivialSpanRootPairs : Set (Φ × Φ)) (singleSpanRootPairs : Set (SingleSpanRootPair Φ))
  (doubleCommutatorRootPairs : Set (DoubleSpanRootPair Φ))
  (h_full : ∀ (ζ : Φ), ζ ∈ presentRoots)
  (h_full' : everyRootPairInRootPairs Φ trivialSpanRootPairs singleSpanRootPairs doubleCommutatorRootPairs)
  : PartialChevalleySystem Φ :=
  PartialChevalleySystem.mk presentRoots trivialSpanRootPairs singleSpanRootPairs doubleCommutatorRootPairs (by tauto) (by tauto) (by tauto)

end PartialChevalleySystem

end Steinberg
