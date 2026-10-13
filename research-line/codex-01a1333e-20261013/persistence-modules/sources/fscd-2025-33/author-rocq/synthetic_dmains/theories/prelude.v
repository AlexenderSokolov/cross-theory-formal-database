(** Coq configuration for Iris (not meant to leak to clients).
If you are a user of Iris, note that importing this file means
you are implicitly opting-in to every new option we will add here
in the future. We are *not* guaranteeing any kind of stability here.
Instead our advice is for you to have your own options file; then
you can re-export the Iris file there but if we ever add an option
you disagree with you can easily overwrite it in one central location. *)
(* Everything here should be [Export Set], which means when this
file is *imported*, the option will only apply on the import site
but not transitively. *)
From stdpp Require Export options.

#[export] Set Suggest Proof Using. (* also warns about forgotten [Proof.] *)

(* "Fake" import to whitelist this file for the check that ensures we import
this file everywhere.
From iris.prelude Require Import options.
*)

(* taken from iris *)
From Stdlib.ssr Require Export ssreflect.
From stdpp Require Export prelude.
Set Default Proof Using "Type".
Global Open Scope general_if_scope.
Global Set SsrOldRewriteGoalsOrder. (* See Coq issue #5706 *)
Ltac done := stdpp.tactics.done.

Definition castT {A B : Type} (Heq : A = B) (a : A) : B :=
  match Heq in _ = u return u with eq_refl => a end.

Definition castS {A B : Set} (Heq : A = B) (a : A) : B :=
  match Heq in _ = u return u with eq_refl => a end.

Definition castP {A B : Prop} (Heq : A = B) (a : A) : B :=
  match Heq in _ = u return u with eq_refl => a end.

Local Set Universe Polymorphism.
Unset Universe Minimization ToSet.

Inductive prod (A B : Type) : Type :=
| pair : A -> B -> prod A B
where "x * y" := (prod x y) : type_scope.
Arguments pair {A B} _ _.
Notation "( x , y , .. , z )" := (pair .. (pair x y) .. z) : core_scope.

Register prod as core.prod.type.
Register pair as core.prod.intro.
Register prod_rect as core.prod.rect.

Section projections.
  Context {A : Type} {B : Type}.

  Definition fst (p:A * B) := match p with (x, y) => x end.
  Definition snd (p:A * B) := match p with (x, y) => y end.

  Register fst as core.prod.proj1.
  Register snd as core.prod.proj2.

End projections.

#[global]
Hint Resolve pair : core.

Lemma surjective_pairing (A B:Type) (p:A * B) : p = (fst p, snd p).
Proof. destruct p; reflexivity. Qed.

Lemma injective_projections (A B:Type) (p1 p2:A * B) :
  fst p1 = fst p2 -> snd p1 = snd p2 -> p1 = p2.
Proof. destruct p1, p2; simpl; by intros -> ->. Qed.

Notation "( x ,.)" := (pair x) (only parsing) : stdpp_scope.
Notation "(., y )" := (λ x, (x,y)) (only parsing) : stdpp_scope.

Notation "p .1" := (fst p).
Notation "p .2" := (snd p).

Global Instance: Params (@pair) 2 := {}.
Global Instance: Params (@fst) 2 := {}.
Global Instance: Params (@snd) 2 := {}.
