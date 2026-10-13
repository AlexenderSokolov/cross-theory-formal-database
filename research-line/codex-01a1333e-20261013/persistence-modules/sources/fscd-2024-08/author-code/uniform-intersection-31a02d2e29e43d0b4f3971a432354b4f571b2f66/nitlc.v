(*
  definitions for the non-idempotently typed lambda-calculus
  "nitlc Gamma M A" means that in the type environment Gamma the term M is assigned the type A
*)

Require Import List Permutation.
Import ListNotations.
From NonIdempotent Require Import stlc.

(* non-itempotent intersection types *)
Inductive nity : Type :=
  | niatom (x : nat) : nity
  | niarr (u : list nity) (A : nity) : nity.

(* type environment *)
Notation environment := (list (list nity)).

(* ssim s A means non-idempotent type A collapses to simple type s *)
Inductive ssim : sty -> nity -> Prop :=
  | ssim_atom x : ssim (satom x) (niatom x)
  | ssim_arr s t A u B : Forall (ssim s) (cons A u) -> ssim t B -> ssim (sarr s t) (niarr (cons A u) B).

(* ssim lifted to type environments *)
Notation env_ssim Gamma Delta :=
  (forall x, match nth_error Gamma x with Some s => Forall (ssim s) (nth x Delta []) | None => True end).

(* environment permutation *)
Notation sty_permutation Gammas Deltas :=
  (forall x, @Permutation nity
    (concat (map (fun Gamma => nth x Gamma nil) Gammas))
    (concat (map (fun Delta => nth x Delta nil) Deltas))).

(* non-idempotently typed lambda-calculus *)
(* nitlc Gamma M A means that in the type environment Gamma the term M is assigned the type A *)
Inductive nitlc (Gamma : environment) : tm -> nity -> Prop :=
  | nitlc_var t x A :
      ssim t A ->
      In A (nth x Gamma nil) ->
      nitlc Gamma (var x) A
  | nitlc_app Gamma' Deltas M N u A :
      sty_permutation [Gamma] (Gamma' :: Deltas) ->
      nitlc Gamma' M (niarr u A) ->
      Forall2 (fun B Delta => nitlc Delta N B) u Deltas ->
      nitlc Gamma (app M N) A
  | nitlc_lam t M u A :
      ssim t (niarr u A) ->
      nitlc (cons u Gamma) M A ->
      nitlc Gamma (lam t M) (niarr u A).
