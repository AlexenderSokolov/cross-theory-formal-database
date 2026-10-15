/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Steinberg.Defs.PositiveRootSystem
import Steinberg.Defs.Commutator

import Steinberg.Upstream.PresentedGroup
import Steinberg.Upstream.Commutator

import Steinberg.Macro.Group
import Steinberg.Macro.Syntax


/-!

  Implementation of (ungraded) unipotent Chevalley groups.

  *NOTE:* Cleanup in this file lags behind `GradedPartialChevalleyGroup.lean`.

-/

namespace Steinberg

variable {G : Type TG} [Group G]
         {Φ : Type TΦ} [PositiveRootSystem Φ]
         {R : Type TR} [Ring R]

open PositiveRootSystem PartialChevalleySystem

namespace PartialChevalley

/-! ## Generators of (ungraded) unipotent Chevalley group -/

/--
  Generators of the (ungraded) unipotent Chevalley group corresponding to a positive root system
  over a ring.
-/
structure ChevalleyGenerator (Φ : Type TΦ) [PositiveRootSystem Φ] (R : Type TR) [Ring R] where
  mk ::
  ζ : Φ -- root
  t : R -- coefficient (ring element)

namespace ChevalleyGenerator

instance instCoeProd : Coe (Φ × R) (ChevalleyGenerator Φ R) :=
  ⟨fun p => ⟨p.1, p.2⟩⟩

/--
  Shorthand `{ζ, t}` for building free group elements from a root `ζ` and coefficient `t`.

  Note: To re-use this notation for specific groups,
  re-define it for that group and set the priority higher.
  Then implement delaboration to use the delab defined below.
-/
scoped notation (priority:=1000) "{" ζ ", " t "}" =>
  FreeGroup.of (ChevalleyGenerator.mk ζ t)

section DelabBraces

open Lean PrettyPrinter Delaborator SubExpr

/--
  Delaborates `ChevalleyGenerator.mk` to use the `{ }` notation.

  Delaboration makes it so that the infoview uses the nice notation.
-/
@[delab app.Steinberg.PartialChevalley.ChevalleyGenerator.mk]
def delab_generator_mk : Delab := do
  let e ← getExpr

  -- Only delab a full application of `.mk`
  guard $ e.isAppOfArity' ``ChevalleyGenerator.mk 6

  let ζ ← withNaryArg 4 delab
  let t ← withNaryArg 5 delab
  `({ $ζ:term, $t:term })


/--
  Delaborates `FreeGroup.of` to use the `{ }` notation.

  Delaboration makes it so that the infoview uses the nice notation.
-/
@[delab app.FreeGroup.of]
def delab_free_mk : Delab := do
  let e ← getExpr

  -- Only delab `FreeGroup.of` if its type and value are given to the app
  guard $ e.isAppOfArity' ``FreeGroup.of 2

  -- Only delab `FreeGroup.of` if the type is a Chevalley generator
  let ty := e.getAppArgs.get! 0
  guard $ ty.isAppOfArity' ``ChevalleyGenerator 4

  -- Use the delaboration of the generator
  -- Since this might be a more complicated term or calculation,
  -- we don't call `delab_generator_mk` directly
  let g ← withNaryArg 1 delab
  `($g)

end DelabBraces /- section -/

theorem eq_of_coef_eq (ζ : Φ) {t : R} (u : R) (h : t = u)
    : {ζ, t} = {ζ, u} := by
  congr

end ChevalleyGenerator

open ChevalleyGenerator

/-! ### Statements about generators which we assume and/or prove -/

section Relations

/-! #### Commutator for generators from two roots which span no additional roots -/

/- Theorem stating that commutator of generators for two roots vanishes. -/
def trivialSpanPropOfRootPair (f : FreeGroup (ChevalleyGenerator Φ R) →* G) (p : Φ × Φ) : Prop :=
  let (ζ, η) := p;
  ∀ (t u : R),
    ⁅ f {ζ, t}, f {η, u} ⁆ = 1

/-
The set of elements which must vanish according to the theorem that the commutator of generators
for two roots vanishes. (Used to construct a `PresentedGroup`.)
-/
def trivialSpanRelationsOfRootPair (R : Type TR) [Ring R] (p : Φ × Φ)
    : Set (FreeGroup (ChevalleyGenerator Φ R)) :=
  let (ζ, η) := p;
  { ⁅ {ζ, t}, {η, u} ⁆
    | (t : R) (u : R) }

/-! #### Commutator for two generators from two roots which span one additional root -/

def singleCommutatorPropOfRootPair (f : FreeGroup (ChevalleyGenerator Φ R) →* G) (p : SingleSpanRootPair Φ) : Prop :=
  let ⟨ ζ, η, θ, C, _ ⟩ := p;
  ∀ (t u : R),
    ⁅ f {ζ, t}, f {η, u} ⁆ = f {θ, ↑C * t * u}

def singleSpanRelationsOfRootPair (R : Type TR) [Ring R] (p : SingleSpanRootPair Φ) : Set (FreeGroup (ChevalleyGenerator Φ R)) :=
  let ⟨ ζ, η, θ, C, _ ⟩ := p;
  { ⁅ {ζ, t}, {η, u} ⁆ * {θ, C * t * u}⁻¹
    | (t : R) (u : R) }

/-! #### Commutator for two generators from two roots which span one additional root -/

def doubleSpanPropOfRootPair (f : FreeGroup (ChevalleyGenerator Φ R) →* G) (p : DoubleSpanRootPair Φ) : Prop :=
  let ⟨ ζ, η, θ₁, θ₂, C₁, C₂, _, _ ⟩ := p;
  ∀ (t u : R),
    ⁅ f {ζ, t}, f {η, u} ⁆ = f {θ₁, ↑C₁ * t * u} * f {θ₂, ↑C₂ * t * u * u}

def doubleSpanRelationsOfRootPair (R : Type TR) [Ring R] (p : DoubleSpanRootPair Φ) : Set (FreeGroup (ChevalleyGenerator Φ R)) :=
  let ⟨ ζ, η, θ₁, θ₂, C₁, C₂, _, _ ⟩ := p;
  { ⁅ {ζ, t}, {η, u} ⁆ *
    ({θ₁, C₁ * t * u} * {θ₂, C₂ * t * u * u})⁻¹
    | (t : R) (u : R) }

/-! #### Linearity relation for products of generators from a single root -/

/- Linearity of coefficients for products of generators of a single root (with the same degree). -/
def linearityRelationsOfRoot (R : Type TR) [Ring R] (ζ : Φ) : Set (FreeGroup (ChevalleyGenerator Φ R)) :=
  { {ζ, t} * {ζ, u} * {ζ, t + u}⁻¹
    | (t : R) (u : R) }

end Relations

/-! ### Additional properties implied by linearity and implications therein -/

section ofRoot

set_option quotPrecheck false

/--
  Linearity of group elements on a particular root.

  Equivalent to `∀ (t u), f {ζ, t} * f {ζ, i, u} = f {ζ, i, t + u}`.

  `(f : FreeGroup (ChevalleyGenerator Φ R) →* G)`
  `(ζ : Φ)`
-/
scoped notation "lin_of_root" "(" f ", " ζ ")" =>
  ∀ (t u), f {ζ, t} * f {ζ, u} = f {ζ, t + u}

/--
  Ring coefficient 0 gives an identity element.

  Equivalent to `f {ζ, i, 0} = 1`.

  `(f : FreeGroup (ChevalleyGenerator Φ R) →* G)`
  `(ζ : Φ)`
-/
scoped notation "id_of_root" "(" f ", " ζ ")" =>
  f {ζ, 0} = 1
/--
  Negating the coefficient inverts the generator.

  Equivalent to `∀ (t : R), (f {ζ, t})⁻¹ = 1`.

  `(f : FreeGroup (ChevalleyGenerator Φ R) →* G)`
  `(ζ : Φ)`
-/
scoped notation "inv_of_root" "(" f ", " ζ ")" =>
  ∀ (t), (f {ζ, t})⁻¹ = f {ζ, -t}

/- Linearity implies identity (essentially a standard fact about group homomorphisms). -/
theorem id_of_lin_of_root {f : FreeGroup (ChevalleyGenerator Φ R) →* G} {ζ : Φ}
    : lin_of_root(f, ζ) → id_of_root(f, ζ) := by
  intro h_lin
  apply @mul_left_cancel _ _ _ (f {ζ, 0})
  rw [mul_one, h_lin, add_zero]

/- Linearity implies inverse-ness (essentially a standard fact about group homomorphisms). -/
theorem inv_of_lin_of_root {f : FreeGroup (ChevalleyGenerator Φ R) →* G} {ζ : Φ}
    : lin_of_root(f, ζ) → inv_of_root(f, ζ) := by
  intro h_lin t
  apply @mul_left_cancel _ _ _ (f {ζ, t})
  rw [mul_inv_cancel, h_lin, add_neg_cancel, id_of_lin_of_root h_lin]

end ofRoot

structure PartialChevalleyGroup (Φ : Type TΦ) [PositiveRootSystem Φ] (R : Type TR) [Ring R] where
  mk ::
  sys : PartialChevalleySystem Φ
  define : ChevalleyGenerator Φ R → FreeGroup (ChevalleyGenerator Φ R)
  h_define_of_present : ∀ {g : ChevalleyGenerator Φ R}, g.ζ ∈ sys.presentRoots → define g = FreeGroup.of g
  h_define_is_projection : ∀ {g : ChevalleyGenerator Φ R}, (FreeGroup.lift define) (define g) = define g

namespace PartialChevalleyGroup

open PartialChevalleyGroup

def fullMk (Φ : Type TΦ) [PositiveRootSystem Φ] (R : Type TR) [Ring R] (sys : PartialChevalleySystem Φ)
  : PartialChevalleyGroup Φ R :=
  PartialChevalleyGroup.mk sys FreeGroup.of (by tauto) (by tauto)

/-! ### Sets of relations -/

inductive SteinbergRelationClass
  | TrivialSpan | SingleSpan | DoubleSpan | Linearity | Definition
open SteinbergRelationClass

def definitionRelations (w : PartialChevalleyGroup Φ R) : Set (FreeGroup (ChevalleyGenerator Φ R)) :=
  ⋃ (ζ : Φ), {
      {ζ, t}⁻¹ * w.define (ChevalleyGenerator.mk ζ t) | (t : R)
  }

def allRelations (w : PartialChevalleyGroup Φ R) :=
  ⋃ (K : SteinbergRelationClass),
  (
    match K with
    | TrivialSpan =>
        ⋃ (p ∈ w.sys.trivialSpanRootPairs), trivialSpanRelationsOfRootPair R p
    | SingleSpan =>
        ⋃ (p ∈ w.sys.singleSpanRootPairs), singleSpanRelationsOfRootPair R p
    | DoubleSpan =>
        ⋃ (p ∈ w.sys.doubleCommutatorRootPairs), doubleSpanRelationsOfRootPair R p
    | Linearity =>
        ⋃ (ζ ∈ w.sys.presentRoots), linearityRelationsOfRoot R ζ
    | Definition =>
        w.definitionRelations
  )

/-! ### The group and the embedding -/

abbrev group (w : PartialChevalleyGroup Φ R) :=
  PresentedGroup (PartialChevalleyGroup.allRelations w)

def project (w : PartialChevalleyGroup Φ R) : FreeGroup (ChevalleyGenerator Φ R) →* group w :=
  PresentedGroup.mk (PartialChevalleyGroup.allRelations w)

/-- Mapping between two PartialChevalleyGroups -/
theorem injection (w₁ w₂ : PartialChevalleyGroup Φ R)
  (h_good :
  ∀ (K : SteinbergRelationClass),
    match K with
    | TrivialSpan =>
      ∀ p ∈ w₁.sys.trivialSpanRootPairs, p ∈ w₂.sys.trivialSpanRootPairs ∨
        (∀ r ∈ (trivialSpanRelationsOfRootPair R p), w₂.project r = 1)
    | SingleSpan =>
      ∀ p ∈ w₁.sys.singleSpanRootPairs, p ∈ w₂.sys.singleSpanRootPairs ∨
        (∀ r ∈ (singleSpanRelationsOfRootPair R p), w₂.project r = 1)
    | DoubleSpan =>
      ∀ p ∈ w₁.sys.doubleCommutatorRootPairs, p ∈ w₂.sys.doubleCommutatorRootPairs ∨
        (∀ r ∈ (doubleSpanRelationsOfRootPair R p), w₂.project r = 1)
    | Linearity =>
      ∀ p ∈ w₁.sys.presentRoots, p ∈ w₂.sys.presentRoots ∨
        (∀ r ∈ (linearityRelationsOfRoot R p), w₂.project r = 1)
    | Definition =>
      ∀ p ∈ w₁.definitionRelations, w₂.project p = 1
  )
  : ∀ r ∈ w₁.allRelations, w₂.project r = 1 := by
  simp only [allRelations]
  intro r h
  simp only [Set.mem_iUnion] at h
  rcases h with ⟨ K, h ⟩
  rcases h_K : K
  all_goals (
    simp only [h_K] at h
    specialize h_good K
    simp only [h_K] at h_good
  )
  any_goals (
    simp only [Set.mem_iUnion, exists_prop] at h
    rcases h with ⟨ p, h_p, h_r_p ⟩
    specialize h_good p h_p
    rcases h_good with h|h
    · apply eq_one_of_mem_rels
      simp only [allRelations, Set.mem_iUnion]
      exists K
      rw [h_K]
      simp only [Set.mem_iUnion, exists_prop]
      exists p
    · tauto
  )
  · tauto

open Lean PrettyPrinter Delaborator SubExpr in
/--
  Delaborator for `project` when it's an application.

  Note that this will obscure the widgets on the infoview, such that
  hovering over the group elements won't bring you back to `project`.
-/
@[delab app.DFunLike.coe]
def delab_project' : Delab := do
  withOverApp 6 do
    let e ← getExpr
    let mkApp5 (.const ``project _) _ _ _ _ _ := e.appFn!.appArg!' | failure
    let f_mk_mk ← withNaryArg 5 delab
    `($f_mk_mk)

/-! ### Helpers -/

theorem trivialSpanProp_of_mem_trivialSpanRoot_pairs {w : PartialChevalleyGroup Φ R} {p : Φ × Φ}
    (h : p ∈ w.sys.trivialSpanRootPairs)
      : trivialSpanPropOfRootPair w.project p := by
  intro t u
  apply eq_one_of_mem_rels
  simp only [allRelations, Set.mem_iUnion]
  exists TrivialSpan
  simp only [Set.mem_iUnion]
  exists p, h
  rw [trivialSpanRelationsOfRootPair]
  exists t, u

theorem singleSpanProp_of_mem_singleSpanRoot_pairs (w : PartialChevalleyGroup Φ R) (p : SingleSpanRootPair Φ)
  (h : p ∈ w.sys.singleSpanRootPairs)
    : singleCommutatorPropOfRootPair w.project p := by
  intro t u
  apply eq_of_mul_inv_eq_one
  apply eq_one_of_mem_rels
  simp only [allRelations, Set.mem_iUnion]
  exists SingleSpan
  simp only [Set.mem_iUnion]
  exists p, h
  rw [singleSpanRelationsOfRootPair]
  exists t, u

theorem doubleSpanProp_of_mem_doubleSpanRootPairs (w : PartialChevalleyGroup Φ R) (p : DoubleSpanRootPair Φ)
  (h : p ∈ w.sys.doubleCommutatorRootPairs)
    : doubleSpanPropOfRootPair w.project p := by
  intro t u
  apply eq_of_mul_inv_eq_one
  apply eq_one_of_mem_rels
  simp only [allRelations, Set.mem_iUnion]
  exists DoubleSpan
  simp only [Set.mem_iUnion]
  exists p, h
  rw [doubleSpanRelationsOfRootPair]
  exists t, u

theorem lin_of_root_of_mem_presentRoots (w : PartialChevalleyGroup Φ R) {ζ : Φ} (h : ζ ∈ w.sys.presentRoots)
    : lin_of_root(w.project, ζ) := by
  intro t u
  apply eq_of_mul_inv_eq_one
  apply eq_one_of_mem_rels
  simp only [allRelations, Set.mem_iUnion]
  exists Linearity
  simp only [Set.mem_iUnion]
  exists ζ, h
  rw [linearityRelationsOfRoot]
  exists t, u

theorem definitionProp_of_define (w : PartialChevalleyGroup Φ R)
    : ∀ (ζ : Φ) (t : R), w.project {ζ, t} = w.project (w.define (ChevalleyGenerator.mk ζ t))
      := by
  intro ζ t
  apply eq_of_inv_mul_eq_one
  apply eq_one_of_mem_rels
  simp only [allRelations, Set.mem_iUnion]
  exists Definition
  simp only [definitionRelations, Set.mem_iUnion]
  exists ζ
  simp only [Set.mem_setOf_eq]
  exists t

section declareThms

open Lean Parser.Tactic
set_option hygiene false

def makeCommands (m : MacroM Syntax) : MacroM (TSyntax `command) := do
  let cmds ← Syntax.getArgs <$> m
  return ⟨mkNullNode cmds⟩

macro "declare_ungraded_lin_id_inv_thms" w:ident R:term:arg root:term:arg : command => do
  let linOf := root.mapIdent ("lin_of_" ++ ·)
  let idOf := root.mapIdent ("id_of_" ++ ·)
  let invOf := root.mapIdent ("inv_of_" ++ ·)
  makeCommands `(section
    @[group_reassoc (attr := simp, chev_simps)]
    theorem $linOf : lin_of_root(($w $R).project, $root) :=
      ($w $R).lin_of_root_of_mem_presentRoots (by unfold $w; simp only [PartialChevalleyGroup.fullMk]; tauto)

    @[simp, chev_simps]
    theorem $idOf : id_of_root(($w $R).project, $root) :=
      id_of_lin_of_root $linOf

    @[simp, chev_simps]
    theorem $invOf : inv_of_root(($w $R).project, $root) :=
      inv_of_lin_of_root $linOf
  end)

macro "declare_ungraded_trivial_span_expr_thm" w:ident R:term:arg r₁:term:arg r₂:term:arg : command => do
  let exprAs := TSyntax.mapIdent₂ r₁ r₂
    (fun s₁ s₂ => "expr_" ++ s₁ ++ "_" ++ s₂ ++ "_as_" ++ s₂ ++ "_" ++ s₁)
  let commName := TSyntax.mapIdent₂ r₁ r₂
    (fun s₁ s₂ => "comm_of_" ++ s₁ ++ "_" ++ s₂)
  let commOf ← `(rwRule| $commName:term)
  makeCommands `(section
    @[group_reassoc] theorem $exprAs
      : ∀ (t u : $R),
        commutes(($w $R).project {$r₁:term, t},
                ($w $R).project {$r₂:term, u}) := by
      intro t u
      apply triv_comm_iff_commutes.mp
      rw [$commOf]
      <;> try assumption
  end)

macro "declare_ungraded_trivial_span_of_root_pair_thms"
    w:ident R:term:arg
    r₁:term:arg r₂:term:arg : command => do
  let commOf := TSyntax.mapIdent₂ r₁ r₂ (fun s₁ s₂ => "comm_of_" ++ s₁ ++ "_" ++ s₂)
  makeCommands `(section
    theorem $commOf : trivialSpanPropOfRootPair ($w $R).project ($r₁, $r₂) :=
      ($w $R).trivialSpanProp_of_mem_trivialSpanRoot_pairs (by unfold $w; simp only [PartialChevalleyGroup.fullMk]; tauto)
    declare_ungraded_trivial_span_expr_thm $w $R $r₁ $r₂
  end)

macro "declare_ungraded_single_span_expr_thms"
    w:ident R:term:arg
    r₁:term:arg r₂:term:arg r₃:term:arg isNeg:num n:num : command => do
  let innerTerm ←
    match isNeg.getNat, n.getNat with
    | 0, 1 => `(t * u)
    | 1, 1 => `(-(t * u))
    | 1, _ => `(-($n * t * u))
    | _, _ => `($n * t * u)

  let commOf := TSyntax.mapIdent₂ r₁ r₂ (fun s₁ s₂ => "comm_of_" ++ s₁ ++ "_" ++ s₂)
  let exprAs := TSyntax.mapIdent₃ r₁ r₂ r₃
    (fun s₁ s₂ s₃ => "expr_" ++ s₃ ++ "_as_" ++ s₁ ++ "_" ++ s₂ ++ "_" ++ s₁ ++ "_" ++ s₂)
  let exprAsRev := TSyntax.mapIdent₃ r₁ r₂ r₃
    (fun s₁ s₂ s₃ => "expr_" ++ s₁ ++ "_" ++ s₂ ++ "_as_" ++ s₃ ++ "_" ++ s₂ ++ "_" ++ s₁)
  makeCommands `(section
    theorem $exprAs : ∀ (t u : $R),
        (($w $R).project {$r₃:term, $innerTerm})
          = ($w $R).project {$r₁:term, t}
            * ($w $R).project {$r₂:term, u}
            * ($w $R).project {$r₁:term, -t}
            * ($w $R).project {$r₂:term, -u} := by
      intro t u
      have := $commOf t u
      chev_simp [commutatorElement_def, one_mul, mul_one] at this
      symm at this
      exact this

    @[group_reassoc]
    theorem $exprAsRev : ∀ (t u : $R),
        reorder_left(
          ($w $R).project {$r₁:term, t},
          ($w $R).project {$r₂:term, u},
          (($w $R).project {$r₃:term, $innerTerm})
        ) := by
      intro t u
      have := $commOf t u
      chev_simp [commutatorElement_def, one_mul, mul_one] at this
      grw [← this]
  end)

macro "declare_ungraded_single_span_of_root_pair_thms"
    w:ident R:term:arg
    r₁:term:arg r₂:term:arg r₃:term:arg isNeg:num n:num : command => do
  let innerTerm ←
    match isNeg.getNat with
    | 1 => `(-($n))
    | _ => `($n)

  let commOf := TSyntax.mapIdent₂ r₁ r₂ (fun s₁ s₂ => "comm_of_" ++ s₁ ++ "_" ++ s₂)
  makeCommands `(section
    theorem $commOf : singleCommutatorPropOfRootPair ($w $R).project ⟨$r₁, $r₂, $r₃, $innerTerm, rfl⟩ :=
      ($w $R).singleSpanProp_of_mem_singleSpanRoot_pairs ⟨$r₁, $r₂, $r₃, $innerTerm, rfl⟩ (
        by unfold $w; simp only [PartialChevalleyGroup.fullMk]; tauto)
    declare_ungraded_single_span_expr_thms $w $R $r₁ $r₂ $r₃ $isNeg $n
  end)

end declareThms /- section -/

end PartialChevalleyGroup
