(*
  definitions for the simply typed lambda-calculus
  "stlc Gamma M s" means that in the type environment Gamma the term M is assigned the type s
*)

Require Import List Relations.

(* function composition *)
Definition funcomp {X Y Z} (g : Y -> Z) (f : X -> Y) :=
  fun x => g (f x).

Arguments funcomp {X Y Z} (g f) /.

(* stream cons *)
Definition scons {X: Type} (x : X) (xi : nat -> X) :=
  fun n => match n with | 0 => x | S n => xi n end.

(* simple types *)
Inductive sty : Type :=
  | satom (x : nat)   (* type variable *)
  | sarr (s t : sty). (* function type *)

(* type-annotated lambda-terms *)
Inductive tm : Type :=
  | var (n : nat)           (* term variable *)
  | app (M N : tm)          (* application *)
  | lam (t : sty) (M : tm). (* type-annotated abstraction *)

(* parallel term renaming *)
Fixpoint ren (xi : nat -> nat) (t : tm) : tm  :=
  match t with
  | var x => var (xi x)
  | app M N => app (ren xi M) (ren xi N)
  | lam t M => lam t (ren (scons 0 (funcomp S xi)) M)
  end.

(* parallel term substitution *)
Fixpoint subst (sigma: nat -> tm) (s: tm) : tm :=
  match s with
  | var n => sigma n
  | app M N => app (subst sigma M) (subst sigma N)
  | lam t M => lam t (subst (scons (var 0) (funcomp (ren S) sigma)) M)
  end.

Fixpoint allfv (P : nat -> Prop) (M: tm) : Prop :=
  match M with
  | var n => P n
  | app M N => allfv P M /\ allfv P N
  | lam _ M =>  allfv (scons True P) M
  end.

(* simply typed lambda-calculus *)
(* stlc Gamma M s means that in the type environment Gamma the term M is assigned the type s *)
Inductive stlc (Gamma : list sty) : tm -> sty -> Prop :=
  | stlc_var x t : nth_error Gamma x = Some t -> stlc Gamma (var x) t
  | stlc_app M N s t : stlc Gamma M (sarr s t) -> stlc Gamma N s -> stlc Gamma (app M N) t
  | stlc_lam M s t : stlc (cons s Gamma) M t -> stlc Gamma (lam (sarr s t) M) (sarr s t).

(* normal form property *)
Inductive nf : tm -> Prop :=
  | nf_lam t M : nf M -> nf (lam t M)
  | nf_neutral M : neutral M -> nf M
with neutral : tm -> Prop :=
  | neutral_var x : neutral (var x)
  | neutral_app M N : neutral M -> nf N -> neutral (app M N).

(* head form property: x M1 .. Mn *)
Inductive hf : tm -> Prop :=
  | hf_var x : hf (var x)
  | hf_app M N : hf M -> hf (app M N).

Notation is_nonzero := (fun n : nat => match n with 0 => False | S _ => True end).

(* has_var_zero M means that ((lam M) N) is a lambda-I redex *)
Notation has_var_zero M := (not (allfv is_nonzero M)).

(* traditional I reduction *)
Inductive stepI : tm -> tm -> Prop :=
  | stepIRed t M N   : has_var_zero M -> stepI (app (lam t M) N) (subst (scons N var) M)
  | stepILam t M M'  : stepI M M' -> stepI (lam t M) (lam t M')
  | stepIAppL M M' N : stepI M M' -> stepI (app M N) (app M' N)
  | stepIAppR M N N' : stepI N N' -> stepI (app M N) (app M N').

(* specific K reduction *)
Inductive stepK : tm -> tm -> Prop :=
  (* lambda-K redex contraction *)
  | stepKRed t M N          : nf N -> stepK (app (lam t (ren S M)) N) M
  | stepKLam t M M'         : stepK M M' -> stepK (lam t M) (lam t M')
  | stepKNAppR M N N'       : hf M -> stepK N N' -> stepK (app M N) (app M N')
  | stepKLAppR t M N N'     : stepK N N' -> stepK (app (lam t (ren S M)) N) (app (lam t (ren S M)) N')
  | stepKAAppL M1 M2 M' N   : stepK (app M1 M2) M' -> stepK (app (app M1 M2) N) (app M' N).

Definition swap (x : nat) :=
  match x with
  | 0 => 1
  | 1 => 0
  | _ => x
  end.

(* gamma reduction [1] *)
(* [1] Kfoury, A. J., and J. B. Wells.
       New notions of reduction and non-semantic proofs of β-strong normalization in typed λ-calculi.
       Boston University Computer Science Department, 1994. *)
Inductive stepG : tm -> tm -> Prop :=
  | stepGRed s1 s2 t M N : 
      stepG
        (app (lam (sarr s1 (sarr s2 t)) (lam (sarr s2 t) M)) N)
        (lam (sarr s2 t) (app (lam (sarr s1 t) (ren swap M)) (ren S N)))
  | stepGLam t M M'      : stepG M M' -> stepG (lam t M) (lam t M')
  | stepGAppL M M' N   : stepG M M' -> stepG (app M N) (app M' N)
  | stepGAppR M N N'   : stepG N N' -> stepG (app M N) (app M N').

(* union of stepI, stepG, stepK *)
Definition step M N := stepI M N \/ stepG M N \/ stepK M N.

(* reflexive, transitive closure of step *)
Notation steps := (clos_refl_trans tm step).
