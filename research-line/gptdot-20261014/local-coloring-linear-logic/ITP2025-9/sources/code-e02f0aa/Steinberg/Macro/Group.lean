/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

/- Tactic and metaprogramming imports -/
import Lean.Elab.Declaration
import Lean.Elab.Tactic.Rewrite
import Mathlib.Tactic.SimpRw
import Mathlib.Util.AddRelatedDecl
import Mathlib.Tactic.CategoryTheory.Reassoc

/- Mathlib mathematics imports -/
import Mathlib.Algebra.Group.Defs
import Mathlib.Algebra.Group.Basic
import Mathlib.Algebra.Ring.Defs
import Mathlib.Algebra.Group.Hom.Defs
import Mathlib.GroupTheory.FreeGroup.Basic
import Mathlib.GroupTheory.Commutator.Basic

import Steinberg.Macro.Attr

/-! Macros and other convenience keywords when doing proofs on groups.

See:
  - Associating: `mul_assoc_l`, `mal`, `mul_assoc_r`, `mar`
  - Chevalley simp automation: `chev_simp`
  - Group rewrite: `grw`

-/

namespace Steinberg

open Mathlib.Tactic
open Lean Meta Elab Term Tactic Parser.Tactic PrettyPrinter

attribute [chev_simps] neg_add_cancel add_neg_cancel
  one_mul mul_one zero_mul mul_zero
  mul_neg neg_mul neg_neg inv_inv mul_inv_rev
  div_neg neg_div
  pow_two
  zero_add add_zero neg_zero
  map_one map_zero map_mul map_add map_neg map_commutatorElement
  commutatorElement_inv commutatorElement_one_left commutatorElement_one_right
  and_true true_and and_self or_self
  Int.cast_ofNat Int.cast_one Int.cast_two Int.cast_three Int.cast_neg Int.reduceNeg
  FreeGroup.map.of FreeGroup.lift.of

/-- A macro for a common simplification when rewriting with ghost component equations. -/
syntax (name := chevSimp) "chev_simp" (simpArgs)? (location)? : tactic
macro_rules
  | `(tactic| chev_simp $[[$simpArgs,*]]? $[at $loc]?) => do
    let args := simpArgs.map (·.getElems) |>.getD #[]
    `(tactic| simp only [chev_simps, $args,*] $[at $loc]?)

syntax (name := chevSimp?) "chev_simp?" (simpArgs)? (location)? : tactic
macro_rules
  | `(tactic| chev_simp? $[[$simpArgs,*]]? $[at $loc]?) => do
    let args := simpArgs.map (·.getElems) |>.getD #[]
    `(tactic| simp? [chev_simps, $args,*] $[at $loc]?)

syntax (name := heightSimp) "height_simp" (simpArgs)? (location)? : tactic
macro_rules
  | `(tactic| height_simp $[[$simpArgs,*]]? $[at $loc]?) => do
    let args := simpArgs.map (·.getElems) |>.getD #[]
    `(tactic| simp only [height_simps, $args,*] $[at $loc]?)

/-- A simple tactic to solve `PosRootSys` height equations. Uses `omega`. -/
macro "ht" : tactic =>
  `(tactic| (
   first
    | trivial
    | assumption
    | omega
    | (try height_simp at *; omega)
  ))

namespace Macro

/-- Shorthand for `simp_rw [← mul_assoc]`, which applies the `mul_assoc` tactic to the left. -/
macro (name := mul_assoc_l) "mul_assoc_l" l:(location)? : tactic => `(tactic|
  simp_rw [← mul_assoc] $l ?
)

@[inherit_doc mul_assoc_l]
macro (name := mal) "mal" l:(location)? : tactic => `(tactic|
  mul_assoc_l $l ?
)

/-- Shorthand for `simp_rw [mul_assoc]`, which applies the `mul_assoc` tactic to the right. -/
macro (name := mul_assoc_r) "mul_assoc_r" l:(location)? : tactic => `(tactic|
  simp_rw [mul_assoc] $l ?
)

@[inherit_doc mul_assoc_r]
macro (name := mar) "mar" l:(location)? : tactic => `(tactic|
  mul_assoc_r $l ?
)

/- TODO-B: Use these two theorems to generate an automatic new theorem from a commutative theorem. -/

private theorem mul_assoc_left {G : Type u} [Semigroup G] {b c d : G} (h : b * c = d) (a : G)
    : a * b * c = a * d := by
  rw [mul_assoc, h]

private theorem mul_assoc_right {G : Type u} [Semigroup G] {b c d : G} (h : b * c = d) (a : G)
    : b * (c * a) = d * a := by
  rw [← mul_assoc, h]

private theorem add_assoc_left {G : Type u} [AddSemigroup G] {b c d : G} (h : b + c = d) (a : G)
    : a + b + c = a + d := by
  rw [add_assoc, h]

private theorem add_assoc_right {G : Type u} [AddSemigroup G] {b c d : G} (h : b + c = d) (a : G)
    : b + (c + a) = d + a := by
  rw [← add_assoc, h]

private theorem mul_assoc_symm {G : Type u} [Semigroup G] (a b c : G)
    : a * (b * c) = a * b * c := by
  exact Eq.symm (mul_assoc _ _ _)

private theorem mul_left_inj_assoc {G : Type u} [Semigroup G] [IsRightCancelMul G] (a : G) {b c d e : G}
    : d * (b * a) = e * (c * a) ↔ d * b = e * c := by
  mal; rw [mul_left_inj]

private theorem mul_left_inj_assoc_l {G : Type u} [Semigroup G] [IsRightCancelMul G] (a : G) {b c d : G}
    : d * (b * a) = c * a ↔ d * b = c := by
  mal; rw [mul_left_inj]

private theorem mul_left_inj_assoc_r {G : Type u} [Semigroup G] [IsRightCancelMul G] (a : G) {b c e : G}
    : b * a = e * (c * a) ↔ b = e * c := by
  mal; rw [mul_left_inj]

private theorem mul_right_inj_assoc {G : Type u} [Semigroup G] [IsLeftCancelMul G] (a : G) {b c d e : G}
    : (a * b) * d = (a * c) * e ↔ b * d = c * e := by
  mar; rw [mul_right_inj]

private theorem mul_right_inj_assoc_l {G : Type u} [Semigroup G] [IsLeftCancelMul G] (a : G) {b c d : G}
    : (a * b) * d = a * c ↔ b * d = c := by
  mar; rw [mul_right_inj]

private theorem mul_right_inj_assoc_r {G : Type u} [Semigroup G] [IsLeftCancelMul G] (a : G) {b c e : G}
    : a * b = (a * c) * e ↔ b = c * e := by
  mar; rw [mul_right_inj]

/--
  Apply `mul_left_inj` and `mul_right_inj` after reassociating.
  End with the term reassociated to the left (i.e., `(a * b) * c`).
-/
macro (name := mul_inj) "mul_inj" l:(location)? : tactic => `(tactic| (
  (try simp only [mul_assoc, mul_right_inj,
    mul_inv_cancel, inv_mul_cancel, one_mul, mul_one] $l ?);
  (try simp only [← mul_assoc, mul_left_inj,
    mul_inv_cancel, inv_mul_cancel, one_mul, mul_one] $l ?)
))

/--
  An empty list of `simp` lemmas and terms.

  TODO-B: See `Mathlib.Tactic.CategoryTheory.Reassoc` for a list of potential
      relevant lemmas, but for category theory. The problem of using a lot
      of standard group theory lemmas is that they will simplify away
      `a * 1`, which we often don't want to do in our proofs. If we find
      that we *do* need some lemmas, add them here.
-/
def groupSimp_left (e : Expr) : MetaM Simp.Result :=
  simpOnlyNames [``mul_assoc_symm] e

def groupSimp_right (e : Expr) : MetaM Simp.Result :=
  simpOnlyNames [``mul_assoc] e

/--
  An attribute to automatically generate a new theorem of the same name,
  plus a suffix of `_assoc`.

  Note: This is a copy of `reassocExpr` in `Mathlib.Tactic.CategoryTheory.Reassoc`.

  Essentially, theorems with this attribute automatically generate a proof
  of that same theorem, modulo associativity. See the `private theorems` above.

  Only theorems of the form `∀ ..., a * b = c` are allowed,
  where `*` is the group-theoretic binary operation.
-/
def reassocExpr_left (e : Expr) : MetaM Expr := do
  mapForallTelescope (fun e => do simpType groupSimp_left (← mkAppM ``mul_assoc_left #[e])) e

/--
  An attribute to automatically generate a new theorem of the same name,
  plus a suffix of `_assoc'`.

  Note: This is a copy of `reassocExpr` in `Mathlib.Tactic.CategoryTheory.Reassoc`.

  Essentially, theorems with this attribute automatically generate a proof
  of that same theorem, modulo associativity. See the `private theorems` above.

  Only theorems of the form `∀ ..., a * b = c` are allowed,
  where `*` is the group-theoretic binary operation.
-/
def reassocExpr_right (e : Expr) : MetaM Expr := do
  mapForallTelescope (fun e => do simpType groupSimp_right (← mkAppM ``mul_assoc_right #[e])) e

syntax (name := group_reassoc) "group_reassoc" (" (" &"attr" ":=" Parser.Term.attrInstance,* ")")? : attr

initialize registerBuiltinAttribute {
  name := `group_reassoc
  descr := "Attribute for generating reassociated versions of commutator lemmas"
  applicationTime := .afterCompilation
  add := fun src ref kind => match ref with
  | `(attr| group_reassoc $[(attr := $stx?,*)]?) => MetaM.run' do
    if (kind != AttributeKind.global) then
      throwError "`reassoc` can only be used as a global attribute"
    addRelatedDecl src "_assoc_left" ref stx? fun type value levels => do
      pure (← reassocExpr_left (← mkExpectedTypeHint value type), levels)
    -- TODO-B: (3/18) Removing this still allows `B3Large/Thm.lean` to compile.
    -- TODO-B: I've removed this to speed up compilation.
    -- addRelatedDecl src "_assoc_right" ref stx? fun type value levels => do
    --  pure (← reassocExpr_right (← mkExpectedTypeHint value type), levels)
  | _ => throwUnsupportedSyntax
}

open Term in
/--
  A term elaborator `greassoc_of% t`, where `t` is
  an equation `f = g` on `Semigroup`s (possibly under a `∀` binder),
  used to reassociate the group equation with a fresh third term to the right.

  To use, place before a proof term or hypothesis name to create a new term
  that has been reassociated in the other way. For example,

  `rw [greassoc_of% h]` will rewrite with `h` after being reassociated.

  Note that the elaborator creates only one term. Using this with `rw` will
  NOT
-/
elab "greassoc_of% " t:term : term => do
  reassocExpr_left (← elabTerm t none)

open Term in
/--
  A term elaborator `greassoc_of% t`, where `t` is
  an equation `f = g` on `Semigroup`s (possibly under a `∀` binder),
  used to reassociate the group equation with a fresh third term to the right.

  To use, place before a proof term or hypothesis name to create a new term
  that has been reassociated in the other way. For example,

  `rw [greassoc_of% h]` will rewrite with `h` after being reassociated.

  Note that the elaborator creates only one term. Using this with `rw` will
  NOT
-/
elab "greassoc_of_r% " t:term : term => do
  reassocExpr_right (← elabTerm t none)

/-
  TODO-B: It's very, very hard to get `(rwRule| )` to type check, since it expects
      a `term`, while most outputs of this function are `Term.app`, which for
      whatever reason is not a `term`. So we have to open the `.Compat`
      environment to extract coercions between the `TSyntax` kinds.
      Ideally, we wouldn't need to do this.
-/
open TSyntax.Compat in
/--
  Peers into a `Syntax` object and tries to add `_assoc` to the base theorem
  used in the term.

  For example, if the term is `add_comm h₁ h₂ a b`, then this function
  returns `add_comm_assoc h₁ h₂ a b`.
-/
partial def replaceWithAssocName (stx : Syntax) : Option (TSyntax `term × TSyntax `term) :=
  let k := stx.getKind
  if k == ``Lean.Parser.Term.app then
    let ⟨assocName_left, assocName_right⟩ :=
      match stx[0].getId with
      | Name.str n s =>
        let str_left := s ++ "_assoc_left"
        let str_right := s ++ "_assoc_right"
        let s_left := Name.mkStr n <| str_left
        let s_right := Name.mkStr n <| str_right
        Prod.mk s_left s_right
      | x => Prod.mk x x
    let appNode_left := mkNode ``Lean.Parser.Term.app #[mkIdent assocName_left, stx[1]]
    let appNode_right := mkNode ``Lean.Parser.Term.app #[mkIdent assocName_right, stx[1]]
    some (appNode_left, appNode_right)
  else if k == ``Lean.Parser.Term.proj then
    replaceWithAssocName stx[0]
  else if k == ``Lean.Parser.Term.paren then
    replaceWithAssocName stx[1]
  else
    none

/--
  A special group `rw` tactic that works well with the `group_reassoc`
  attribute for theorems.

  Like `rw`, `grw` takes a list of rewrite terms and applies them in order.
  If the rewrite fails, it reassociates the identified goal/expression
  to the left and tries again. If *that* fails, it tries to extract the
  base theorem name of the rewrite rule and add `_assoc` to it.

  Basically, if a rewrite rule has the form `a * b = c`, but the identified
  goal/expression has the form `(d * a) * b`, then `grw` will use the
  `group_reassoc`-generated theorem to replace `a * b` with `c` by using
  the assoc version of the theorem instead.

  TODO-B: This tactic is a hack. There's no guarantee that the rewrite rule
      has the right form, nor that there exists a reassoc theorem. Another
      attempt of the tactic tried to extract the sub-expression to reassociate
      instead, but constructing the right `mul_assoc` proof term was hard.
-/
elab s:"grw " cfg:optConfig rws:rwRuleSeq l:(location)? : tactic => Elab.Tactic.focus do
  /-
    For each `rwRule` in the `rwRuleSeq`, let `rewrite` process the
    rewrite term to give us a term's `Syntax`. On that syntax,
    examine its type to get out the right expression.
  -/
  withRWRulesSeq s rws fun symm term => do
    match term with
    | `(term| $e:term) => do
      let cont : TacticM Unit := (do
        match replaceWithAssocName e with
        | none => evalTactic <| ← `(tactic| skip)
        | some ⟨assoc_l, _⟩ =>
          let rule_l := ← do if symm then `(rwRule| ← $assoc_l:term) else `(rwRule| $assoc_l:term)
          -- let rule_r := ← do if symm then `(rwRule| ← $assoc_r:term) else `(rwRule| $assoc_r:term)
          evalTactic <| ← `(tactic|
            (rw $cfg [$rule_l] $l ?)
            --first
            -- | (rw $cfg [$rule_l] $l ?)
            -- | (rw $cfg [$rule_r] $l ?)
          )
      )

      let rwTerm ← do if symm then `(rwRule| ← $e:term) else `(rwRule| $e:term)

      -- Now try to reassociate the term `e`
      -- This might fail, but it's an okay transformation to make here
      -- because all we're extracting at this point is syntax
      let reassocTerm_l ← do
        if symm then `(rwRule | ← greassoc_of% $e:term) else `(rwRule | greassoc_of% $e:term)

      let reassocTerm_r ← do
        if symm then `(rwRule | ← greassoc_of_r% $e:term) else `(rwRule | greassoc_o_rf% $e:term)

      ((evalTactic <| ← `(tactic|
        first
        | rw $cfg [$rwTerm] $l ?
        | (mal $l ?; rw $cfg [$rwTerm] $l ?)
        | rw $cfg [$reassocTerm_l] $l ?
        | rw $cfg [$reassocTerm_r] $l ?
      ))
      <|>
      cont);
      (evalTactic <| ← `(tactic| mul_inj $l ?));
      (evalTactic <| ← `(tactic| try chev_simp [] $l ?))

/-- `rwa` is short-hand for `rw; assumption`. -/
macro "rwa " rws:rwRuleSeq loc:(location)? : tactic =>
  `(tactic| (rw $rws:rwRuleSeq $[$loc:location]?; assumption))

macro "grwa " rws:rwRuleSeq l:(location)? : tactic =>
  `(tactic| (grw $rws:rwRuleSeq $[$l:location]?; assumption))

end Macro

end Steinberg
