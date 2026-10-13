(*
  main result: theorem "nitlc_type_inference" states that
  if a term M is assigned the simple type s in the simple type environemnt Gamma0,
  then there is a uniform non-idempotent type environment Gamma (collapsing to Gamma0)
  and a uniform non-idempotent type A (collapsing to s) such that
  M is assigned the type A in the type environment Gamma

  supplementary result: theorem "nitlc_stlc" states that
  if a term M is assigned the uniform non-idempotent type A in the uniform non-idempotent type environemnt Gamma
  such that Gamma collapses to a simple type environment Gamma0,
  then A collapses to a simple type t such that
  the term M is assigned the type t in the environemnt Gamma0.
*)

Require Import PeanoNat Lia List Relations Permutation.
Import ListNotations.

From NonIdempotent Require Import facts stlc stlc_facts stlc_nf nitlc nitlc_facts.
Require Import ssreflect ssrfun.

Arguments nth_error_split {A l n a}.
Arguments in_split {A x}.
Arguments in_combine_r {A B l l' x y}.
Arguments In_nth_error {A l x}.
Arguments map_nth_error {A B f n l d}.

#[local] Notation environment := (list (list nity)).

(* a term is simply typable, if it is typable in the uniform non-itempotent type system *)
Theorem nitlc_stlc Gamma0 M Gamma A : nitlc Gamma M A ->
  env_ssim Gamma0 Gamma ->
  allfv (fun x => nth_error Gamma0 x <> None) M ->
  exists t, stlc Gamma0 M t /\ ssim t A.
Proof.
  move=> H. elim /nitlc_ind': H Gamma0.
  - move=> Gamma' t x A' Ht Hx Gamma0 H' H''.
    exists t. constructor; [|done].
    constructor. move: (H' x) H'' => /=.
    move E: (nth_error Gamma0 x) => [?|]; last done.
    move=> /Forall_forall => /(_ _ Hx) ? _.
    congr Some. apply: ssim_inj; by eassumption.
  - move=> {}Gamma' [|Delta Deltas]; first done.
    move=> Gamma'' t' {}M N [|B' u'] {}A' _.
    { by move=> _ _ _ _ /Forall2_length. }
    move=> H HGamma' ? IHM ? /Forall2E [] IH1N IH2N Gamma0 /= H' [H'M H'N].
    exists t'. split; [|done].
    have : env_ssim Gamma0 Gamma''.
    { move=> x. have := H' x. move E: (nth_error _ _) => [?|]; last done.
      by move: HGamma' => /sty_permutation_ssim_nth /[apply] /Forall_cons_iff []. }
    move: H'M => /IHM /[apply].
    move=> [] [?|??] [] H''M /ssimE; first done.
    move=> [?] [?] [?] [[]] ??? [/Forall_cons_iff [??] ?].
    have : env_ssim Gamma0 Delta.
    { move=> x. have := H' x. move E: (nth_error _ _) => [?|]; last done.
      by move: HGamma' => /sty_permutation_ssim_nth /[apply] /Forall_cons_iff [?] /Forall_cons_iff []. }
    move: (H'N) => /IH1N /[apply].
    move=> [] ? [] H''N ?. subst.
    econstructor; [|by eassumption].
    move: H''M. congr stlc. congr sarr; apply: ssim_inj; by eassumption.
  - move=> {}Gamma' [?|s t] {}M u' {}A' /ssimE; first done.
    move=> [?] [?] [?] [[]] ?? []. subst.
    move=> ??? IH Gamma0 /= H' H'M.
    exists (sarr s t). split; [|by constructor].
    constructor. case: (IH (s :: Gamma0)).
    + by move=> [|x]; [|apply: H'].
    + by apply: allfv_impl H'M => - [|?] /=.
    + move=> ? [+] ?. congr stlc. apply: ssim_inj; by eassumption.
Qed.

Lemma ssim_arr_transport' s t u A t' A' : ssim (sarr s t) (niarr u A) -> ssim t' A' -> ssim (sarr s t') (niarr u A').
Proof.
  move=> /ssimE [?] [?] [?] [[-> ?]] [??] ?. by constructor.
Qed.

Lemma stlc_nitlc_ssim Gamma Gamma' M t A :
  stlc Gamma M t -> nitlc Gamma' M A -> env_ssim Gamma Gamma' -> ssim t A.
Proof.
  move=> /[dup] /stlc_allfv_not_None /nitlc_stlc + /stlc_inj HM.
  by move=> /[apply] /[apply] - [?] [/HM <-].
Qed.

Lemma nitlc_allfv_not_nil Gamma M A :
  nitlc Gamma M A ->
  allfv (fun x => nth x Gamma nil <> nil) M.
Proof.
  elim /nitlc_ind'.
  - move=> {}Gamma t x {}A ? /=. by case: (nth x Gamma []).
  - move=> {}Gamma [|Delta ?]; first done.
    move=> Gamma' ??? [|??] > _ ? H ? HM ? /=.
    + by move=> /Forall2_length.
    + move=> /Forall2E [] HN ?. split.
      * apply: allfv_impl HM => x.
        move: H => /sty_permutation_In_nth => /(_ Gamma' x).
        case: (nth x Gamma []); last done.
        move: (nth x Gamma' []) => [|B ?]; first done.
        move=> H _ _. apply: (H B); by left.
      * apply: allfv_impl HN => x.
        move: H => /sty_permutation_In_nth => /(_ Delta x).
        case: (nth x Gamma []); last done.
        move: (nth x Delta []) => [|B ?]; first done.
        move=> H _ _. apply: (H B); [by left|].
        right. by left.
  - move=> > ?? /=. by apply: allfv_impl=> - [|?] /=.
Qed.

Lemma env_ssim_merge Gamma Delta1 Delta2 :
  env_ssim Gamma Delta1 ->
  env_ssim Gamma Delta2 ->
  env_ssim Gamma (merge Delta1 Delta2).
Proof.
  move=> H1 H2 x. move: (H1 x) (H2 x).
  case: (nth_error Gamma x); last done.
  move=> *. rewrite nth_merge. by apply /Forall_app.
Qed.

Lemma env_ssim_fold_right_merge Gamma Gamma' Deltas :
  env_ssim Gamma Gamma' ->
  Forall (fun Delta => env_ssim Gamma Delta) Deltas ->
  env_ssim Gamma (fold_right merge Gamma' Deltas).
Proof.
  move=> H. elim; first done.
  move=> *. by apply: env_ssim_merge.
Qed.

Lemma env_ssim_sty_permutation_In Gamma0 Gamma Delta Deltas :
  env_ssim Gamma0 Gamma ->
  sty_permutation [Gamma] Deltas ->
  In Delta Deltas ->
  env_ssim Gamma0 Delta.
Proof.
  move=> HG0G /sty_permutation_In_nth /[apply] HDDs x.
  have := HG0G x.
  case: (nth_error Gamma0 x); last done.
  move=> s /Forall_forall H.
  apply /Forall_forall => A /HDDs. by apply: H.
Qed.

Lemma nitlc_change_K u v Gamma M A :
  nitlc (u :: Gamma) (ren S M) A ->
  nitlc (v :: Gamma) (ren S M) A.
Proof.
  apply: nitlc_allfv. apply: allfv_ren. by apply: allfv_trivial.
Qed.

Lemma ssim_arr_transport u u' A s t :
  ssim (sarr s t) (niarr u A) ->
  length u' = length u ->
  Forall (ssim s) u' ->
  ssim (sarr s t) (niarr u' A).
Proof.
  move=> /ssimE [?] [?] [?] [[??]] [??]. subst.
  case: u'; first done.
  move=> > ??. by constructor.
Qed.

Lemma hf_change_ty A B M Gamma0 Gamma :
  hf M ->
  env_ssim Gamma0 Gamma ->
  nitlc Gamma M A ->
  (forall s, ssim s A -> ssim s B) ->
  exists Gamma', env_ssim Gamma0 Gamma' /\ nitlc Gamma' M B.
Proof.
  move=> H HG0G. elim: H A B Gamma HG0G.
  - move=> x A B Gamma HG0G /nitlcE [[t']] H Hx HAB.
    exists (merge ((repeat [] x) ++ [[B]]) Gamma). split.
    + apply: env_ssim_merge; last done.
      move=> y.
      have [<-|] := Nat.eq_dec x y.
      * have := HG0G x. move: (nth x Gamma []) Hx.
        move=> ? /in_split [?] [?] ->.
        move: (nth_error Gamma0 x) => [t|]; last done.
        move=> /Forall_app [_] /Forall_cons_iff [+ _].
        move=> /HAB ?.
        rewrite app_nth2 repeat_length; first done.
        rewrite Nat.sub_diag. by constructor.
      * move: (nth_error Gamma0 y) => [?|]; last done.
        elim: (x) y; first by move=> [|[|y]].
        move=> z IH [|y]; first done.
        move=> ?. apply: IH. lia.
    + apply: nitlc_var.
      * apply: HAB. by eassumption.
      * apply: In_nth_merge_l.
        rewrite app_nth2 repeat_length; first done.
        rewrite Nat.sub_diag. by left.
  - move=> {}M N ? IH A B Gamma HG0G.
    move=> /nitlcE [Gamma'] [Deltas] [u] [HG].
    move=> [/IH {}IH] HDs HAB.
    have /IH {}IH : env_ssim Gamma0 Gamma'.
    { move: HG => /env_ssim_sty_permutation_In. by apply; [|left]. }
    have /IH [Gamma'' [??]] : forall s, ssim s (niarr u A) -> ssim s (niarr u B).
    { move=> [?|??] /ssimE; first done.
      move=> [?] [?] [?] [[??]] [??]. subst.
      constructor; first done.
      by apply: HAB. }
    exists (fold_right merge Gamma'' Deltas). split.
    + apply: env_ssim_fold_right_merge; first done.
      apply /Forall_forall => Delta ?.
      move: HG => /env_ssim_sty_permutation_In. by apply; [|right].
    + econstructor.
      * by apply: sty_permutation_fold_right_merge.
      * by eassumption.
      * done.
Qed.

(* subject expansion for specialized K-reduction *)
Theorem stepK_expansion M N Gamma0 t0 Gamma A : stepK M N -> stlc Gamma0 M t0 -> nitlc Gamma N A ->
  (* strengthen this to all variables, but not length-fixed? *)
  env_ssim Gamma0 Gamma ->
  exists Gamma',
    env_ssim Gamma0 Gamma' /\
    match M with
    | var _ =>  nitlc Gamma' M A
    | app _ _ => nitlc Gamma' M A
    | lam _ _ => exists A', nitlc Gamma' M A'
    end.
Proof.
  have Hty : forall Gamma M A,
    match M with
    | var _ => nitlc Gamma M A
    | app _ _ => nitlc Gamma M A
    | lam _ _ => exists A', nitlc Gamma M A'
    end -> exists A', nitlc Gamma M A'.
  { move=> ? [] > ? => [| |[? ?]]; eexists; by eassumption. }
  move=> H. elim: H Gamma0 t0 Gamma A.
  - (* stepKRed ... stepK (app (lam (sarr s t) (ren S M)) N) M *)
    move=> t {}M {}N /stlc_nitlc_nf H1N Gamma0 t0 Gamma A.
    move=> /stlcE [] s0 + /H1N {H1N} [GammaN] [A'] [?] [HG0N ?] H'1M.
    move=> /stlcE [] s1 t1 H1M [??] ?.
    subst=> /= HG0.
    exists (merge Gamma GammaN).
    split.
    { apply: env_ssim_merge; first done.
      elim: HG0N; first by case.
      by move=> > ?? H [|?] /=; [|apply: H]. }
    have ? : ssim t1 A.
    { move: (H1M) => /stlc_nitlc_ssim. apply.
      - by apply: (nitlc_ren _ ([A']:: Gamma)) H'1M; [lia|].
      - by move=> [|?] /=; [constructor|apply: HG0]. }
    apply: (nitlc_app _ Gamma [GammaN] _ _ [A']).
    + have := (sty_permutation_mergeL Gamma GammaN nil nil [GammaN]).
      rewrite merge_nil_r. by apply=> - [|x].
    + constructor; [by do ? constructor|].
      by apply: nitlc_ren; [lia| |eassumption].
    + by constructor.
  - (* stepKLam ... stepK (lam t M) (lam t M') *)
    move=> ? {}M M' ? IH Gamma0 t0 Gamma [] > + /nitlcE.
    { by move=> _ [?] [?] []. }
    move=> /stlcE [] s' t' + ??. subst.
    move=> /[dup] H0M /IH {}IH.
    move=> [?] [?] [[??]] [/ssimE] [?] [?] [?] [[??] [??]]. subst.
    move=> /[dup] ? /IH{IH} + /= H.
    evar (T : Type). evar (H' : T). subst T. move=> /(_ H').
    [H']: { by move=> [|x] /=; [|apply: H]. }
    move=> [Gamma'] [H4M] /Hty [?] H5M.
    exists (skipn 1 Gamma'). split.
    { move=> x. have /= := (H4M (S x)).
      case: (nth_error Gamma0 x); last done.
      by move: (x) (Gamma')=> [|?] [|??]. }
    eexists (niarr (lift_sty s' :: nth 0 Gamma' []) _). constructor.
    + constructor.
      * constructor; [|by apply: (H4M 0)].
        by apply: ssim_lift_sty.
      * apply: stlc_nitlc_ssim; by eassumption.
    + have -> : (lift_sty s' :: nth 0 Gamma' []) :: skipn 1 Gamma' = merge [[lift_sty s']] Gamma'.
      { by case: (Gamma'). }
      by apply: weakening.
  - (* stepKNAppR ... stepK (app M N) (app M N') *)
    move=> {}M {}N N' ?? IH Gamma0 t0 Gamma A.
    move=> /stlcE [] s H1M H1N.
    move=> /nitlcE [Gamma'] [Deltas] [u] [HG] [H2M] H2N HG0G.
    move: (H1N) (H2N) => /IH {}IH.
    have /Forall_cons_iff [HG0G' HG0Ds]: Forall (fun Delta => env_ssim Gamma0 Delta) (Gamma' :: Deltas).
    { apply /Forall_forall => Delta /sty_permutation_In_nth H.
      move: HG => /H {}H x.
      have := HG0G x.
      move: (nth_error Gamma0 x) => [?|]; last done.
      move=> /Forall_forall H'.
      apply /Forall_forall => ? /H.
      by apply: H'. }
    have: exists u' Deltas', length u' = length u /\
      Forall2 (fun B' Delta' => env_ssim Gamma0 Delta' /\ nitlc Delta' N B') u' Deltas'.
    { elim: H2N HG0Ds; first by exists nil, nil.
      move=> B Delta u' Deltas' /IH {}IH.
      move=> ? IH' /Forall_cons_iff [/IH].
      move=> [Delta'] [? /Hty [B' ?]] /IH' [u''] [Deltas''] [??].
      exists (B' :: u''), (Delta' :: Deltas'') => /=.
      split; [by lia|by constructor]. }
    move => [u'] [Deltas'] [Hu'u HDs'].
    have [Gamma'' [??]]: exists Gamma'', env_ssim Gamma0 Gamma'' /\ nitlc Gamma'' M (niarr u' A).
    { have H' : ssim (sarr s t0) (niarr u A).
      { apply: stlc_nitlc_ssim; by eassumption. }
      have ? : ssim (sarr s t0) (niarr u' A).
      { apply: ssim_arr_transport; [by eassumption..|].
        elim: HDs'; first done.
        move=> > [HG0D ?] ??. constructor; last done.
        apply: stlc_nitlc_ssim; by eassumption. }
      apply: (hf_change_ty); [by eassumption..|].
      move=> ?. by move: H' => /ssim_inj /[apply] <-. }
    exists (fold_right merge Gamma'' Deltas').
    split.
    { apply: env_ssim_fold_right_merge; first done.
      elim: HDs'; first done.
      move=> > [??] *. by constructor. }
    apply: (nitlc_app _ Gamma'' Deltas' _ _ u').
    + by apply: sty_permutation_fold_right_merge.
    + done.
    + elim: HDs'; first done.
      move=> > [] *. by constructor.
  - (* stepKLAppR ... stepK (app (lam (sarr s t) (ren S M)) N) (app (lam (sarr s t) (ren S M)) N') *)
    move=> t {}M {}N N' ? IH Gamma0 t0 Gamma A.
    move=> /stlcE [] ? /stlcE [] ?? H1M [??] ? H1N. subst.
    move=> + HG0G.
    move=> /nitlcE [Gamma'] [Deltas] [u'] [HG].
    move=> [/nitlcE] [u] [?] [[??]] [?] H3M H3N. subst.
    move: (H1N) => /IH {}IH.
    have /Forall_cons_iff [HG0G' HG0Ds]: Forall (fun Delta => env_ssim Gamma0 Delta) (Gamma' :: Deltas).
    { apply /Forall_forall => Delta /sty_permutation_In_nth H.
      move: HG => /H {}H x.
      have := HG0G x.
      move: (nth_error Gamma0 x) => [?|]; last done.
      move=> /Forall_forall H'.
      apply /Forall_forall => ? /H.
      by apply: H'. }
    have: exists u' Deltas', length u' = length u /\
      Forall2 (fun B' Delta' => env_ssim Gamma0 Delta' /\ nitlc Delta' N B') u' Deltas'.
    { elim: H3N HG0Ds; first by exists nil, nil.
      move=> B Delta u' Deltas' /IH {}IH.
      move=> ? IH' /Forall_cons_iff [/IH].
      move=> [Delta'] [? /Hty [B' ?]] /IH' [u''] [Deltas''] [??].
      exists (B' :: u''), (Delta' :: Deltas'') => /=.
      split; [by lia|by constructor]. }
    move => [u'] [Deltas'] [Hu'u HDs']. exists (fold_right merge Gamma' Deltas').
    split.
    { apply: env_ssim_fold_right_merge; first done.
      elim: HDs'; first done.
      move=> > [??] *. by constructor. }
    apply: (nitlc_app _ Gamma' Deltas' _ _ u').
    + by apply: sty_permutation_fold_right_merge.
    + econstructor.
      * apply: ssim_arr_transport; [by eassumption..|].
        elim: HDs'; first done.
        move=> B Delta u'' Deltas'' [HG0D ?] ? ?. constructor; last done.
        apply: stlc_nitlc_ssim; by eassumption.
      * apply: nitlc_change_K. by eassumption.
    + elim: HDs'; first done.
      move=> > [] *. by constructor.
  - (* stepKAAppL ... stepK (app (app M1 M2) N) (app M' N) *)
    move=> > ? IH Gamma0 t0 Gamma A.
    move=> /stlcE [] ? H1M H1N.
    move=> /nitlcE [Gamma'] [Deltas] [?] [HGamma] [H2M H2N] HG0G. subst.
    move: (H1M) (H2M) => /IH /[apply].
    case.
    { move=> x. have := HG0G x.
      move E: (nth_error Gamma0 x) => [?|]; last done.
      move: HGamma => /sty_permutation_In_nth H /Forall_forall H'.
      apply /Forall_forall => ? /H {}H.
      apply: H'. apply: H. by left. }
    move=> Gamma'' [H4M ?].
    exists (fold_right merge Gamma'' Deltas).
    have H'Gamma : sty_permutation [Gamma] [fold_right merge Gamma' Deltas].
    { apply: sty_permutation_trans; [by eassumption|].
      apply: sty_permutation_sym. by apply: sty_permutation_fold_right_merge. }
    split.
    { apply: env_ssim_fold_right_merge; first done.
      apply /Forall_forall => Delta ?.
      move: HGamma => /sty_permutation_In_nth => /(_ Delta) H x.
      have := HG0G x.
      move E: (nth_error Gamma0 x) => [?|]; last done.
      move=> /Forall_forall H'.
      apply /Forall_forall => ? /H {}H.
      apply: H'. apply: H. by right. }
    econstructor; [by apply: sty_permutation_fold_right_merge| |]; by eassumption.
Qed.

Lemma nitlc_ren_swap u0 u1 Gamma M A :
  nitlc (u1 :: u0 :: Gamma) (ren swap M) A ->
  nitlc (u0 :: u1 :: Gamma) M A.
Proof.
  move=> /(@nitlc_ren _ _ swap).
  rewrite ren_ren.
  have -> : ren (funcomp swap swap) M = M.
  { rewrite -[RHS]ren_id. by apply: ren_ext=> - [|[|?]]. }
  apply.
  - move=> [|[|?]] [|[|?]] /=; lia.
  - by move=> [|[|?]] /=.
Qed.

Lemma stepGRed_expansion (s1 s2 t : sty) (M N : tm) (Gamma : environment) (A : nity) :
  nitlc Gamma (lam (sarr s2 t) (app (lam (sarr s1 t) (ren swap M)) (ren S N))) A ->
  nitlc Gamma (app (lam (sarr s1 (sarr s2 t)) (lam (sarr s2 t) M)) N) A.
Proof.
  move=> /nitlcE [u2] [B] [->] [?].
  move=> /nitlcE [Gamma'] [Deltas] [u1] [HG] [].
  move=> /nitlcE [u1'] [A'] [[??]] [?] HM HN. subst u1' A'.
  have ? : ssim (sarr s1 (sarr s2 t)) (niarr u1 (niarr u2 B)).
  { by apply: ssim_arr_transport'; [by eassumption|]. }
  apply: (nitlc_app _ (skipn 1 Gamma') (map (skipn 1) Deltas) _ _ u1).
  + move: HG => /(sty_permutation_skipn 1). by apply.
  + econstructor; first done.
    econstructor; first done.
    apply: nitlc_ren_swap.
    have : exists u2', sty_permutation [merge ([[]; u2']) (u1 :: Gamma')] [u1 :: u2 :: skipn 1 Gamma'].
    { move: Gamma' HG {HM} => [|u Gamma'] HG.
      { by exists u2. }
      suff : exists u' : list nity, sty_permutation [[u' ++ u]] [[u2]].
      { move=> [u2'] H. by exists u2'=> - [|[|x]]; [|apply: (H 0)|]. }
      exists (concat (concat (map (firstn 1) Deltas))).
      move=> [|x]; last done.
      have /= /Permutation_sym := HG 0.
      apply: Permutation_trans.
      rewrite app_nil_r. apply: Permutation_trans; [by apply: Permutation_app_comm|].
      apply: Permutation_app; first done.
      apply: Permutation_eq.
      elim: (Deltas); first done.
      by move=> [|? Delta'] Deltas' /= <-. }
    move=> [?] /permutation. apply.
    by apply: weakening.
  + elim: HN; first done.
    move=> ? Delta > HN *. constructor; last done.
    move: HN.
    move=> /(nitlc_allfv_ren Nat.pred). rewrite ren_ren ren_id. apply.
    * apply: allfv_ren. apply: allfv_trivial => ? /=.
      apply: allfv_ren. by apply: allfv_trivial => ? /= ->.
    * apply: allfv_ren. apply: allfv_trivial => x /=.
      by move: (x) (Delta) => [|?] [|??].
Qed.

(* subject expansion for gamma-reduction *)
Theorem stepG_expansion M N Gamma A : stepG M N -> nitlc Gamma N A -> nitlc Gamma M A.
Proof.
  move=> H. elim: H Gamma A.
  - move=> >. by apply: stepGRed_expansion.
  - move=> > ? IH > /nitlcE [?] [?] [?] [? /IH ?]. subst.
    by econstructor.
  - move=> > ? IH > /nitlcE [?] [?] [?] [?] [/IH ?] ?.
    econstructor; by eassumption.
  - move=> > ? IH > /nitlcE [?] [?] [?] [?] [?] HN'.
    econstructor; [by eassumption..|].
    apply: Forall2_impl HN' => >. by apply: IH.
Qed.

Lemma sty_permutation_app_concat Deltas Gammas Gammas's :
  length Gammas = length Gammas's ->
  Forall2 (fun Delta '(Gamma, Gammas') => sty_permutation [Delta] (Gamma :: Gammas')) Deltas (combine Gammas Gammas's) ->
  sty_permutation Deltas (Gammas ++ concat Gammas's).
Proof.
  move=> H H' x.
  elim: Deltas Gammas Gammas's H H'.
  - by move=> [|??] [|??] /= ? /Forall2_length /=.
  - move=> ?? IH [|??] [|??] /= ? /[dup] /Forall2_length /= ?; [lia..|].
    move=> /Forall2E [] /(_ x) /= H /IH ->; [lia|].
    rewrite app_nil_r in H.
    apply: Permutation_trans; [by apply: Permutation_app; [eassumption|]|].
    rewrite !map_app !concat_app !app_assoc. apply: Permutation_app_tail.
    rewrite -!app_assoc. apply: Permutation_app_head.
    by apply: Permutation_app_comm.
Qed.

#[local] Arguments list_sum : simpl never.
#[local] Arguments map : simpl never.
#[local] Arguments concat : simpl never.

Lemma stepIRed_expansion (s t : sty) (M N : tm) :
  has_var_zero M ->
  forall Gamma0 (Gamma : environment) (A : nity),
  stlc Gamma0 (app (lam (sarr s t) M) N) t ->
  env_ssim Gamma0 Gamma ->
  nitlc Gamma (subst (scons N var) M) A ->
  nitlc Gamma (app (lam (sarr s t) M) N) A.
Proof.
  move=> H0M Gamma0 Gamma A /stlcE [] ?.
  move=> /stlcE [] ? t' H1M [??] [] ? H1N HG0G HNM. subst.
  suff: exists Gamma' u Deltas,
    sty_permutation [Gamma] (Gamma' :: Deltas) /\
    nitlc (u :: Gamma') M A /\
    ssim (sarr s t') (niarr u A) /\
    Forall2 (fun B Delta => nitlc Delta N B) u Deltas.
  { move=> [?] [?] [?] [?] [?] [H ?].
    move: (H) => /ssimE [?] [?] [?] [[??]] [??]. subst.
    econstructor; [|econstructor|]; by eassumption. }
  rename t' into t.
  have [Gamma' [u [Deltas]]] : exists (Gamma' : environment) (u : list nity) (Deltas : list environment),
    sty_permutation [Gamma] (Gamma' :: Deltas) /\
    nitlc (u :: Gamma') M A /\
    Forall (ssim s) u /\
    Forall2 (fun (B : nity) (Delta : environment) => nitlc Delta N B) u Deltas.
  { move: H1N H1M HG0G HNM. clear.
    elim /(Nat.measure_induction _ size_tm): M N t A Gamma0 Gamma. case.
    - move=> [|x] _ N t A Gamma0 Gamma /=.
      + move=> HN ? HG0G ?.
        have ? : ssim s A.
        { apply: (stlc_nitlc_ssim Gamma0 Gamma); by eassumption. }
        exists nil, [A], [Gamma]. do ? split.
        * by case.
        * by econstructor; [eassumption|left].
        * by constructor.
        * by constructor.
      + move=> H1N H1M HG0G /nitlcE [[?]] ??.
        exists Gamma, nil, []. do ? split; [done| |done..].
        econstructor; by eassumption.
    - move=> M1 M2 IH N t0 A Gamma0 Gamma H1N.
      have /IH IH1 : size_tm M1 < size_tm (app M1 M2).
      { move=> /=. lia. }
      have /IH IH2 : size_tm M2 < size_tm (app M1 M2).
      { move=> /=. lia. }
      clear IH.
      move=> /stlcE [] ? H1M1 H1M2 HG0G /=.
      move=> /nitlcE [Gamma'] [Deltas] [u] [HGDs] [H2M1] H2M2.
      have : env_ssim Gamma0 Gamma'.
      { by apply: env_ssim_sty_permutation_In; [eassumption..|left]. }
      move: (H2M1) (H1M1) (H1N) => /IH1 /[apply] /[apply] /[apply].
      move=> [Gamma''] [u''] [Deltas''].
      move=> [?] [?] [??].
      move: (H1M2) (H1N) => /IH2 /[apply] {}IH2.
      have HDs : Forall (fun Delta => env_ssim Gamma0 Delta) Deltas.
      { apply /Forall_forall => Delta ?.
        apply: env_ssim_sty_permutation_In; [by eassumption..|by right]. }
      have : Forall2 (fun B Delta => exists Gamma'' u'' Deltas'',
        sty_permutation [Delta] (Gamma'' :: Deltas'') /\
        nitlc (u'' :: Gamma'') M2 B /\
        Forall (ssim s) u'' /\
        Forall2 (fun B' Delta' => nitlc Delta' N B') u'' Deltas'') u Deltas.
      { elim: H2M2 HDs; first done.
        move=> > /IH2 {}IH2 ? IH' /Forall_cons_iff [/IH2 ?] /IH' ?.
        by constructor. }
      move=> /[dup] /Forall2_length ?.
      move=> /Forall2_exists_exists_Forall2 [Gamma's].
      move=> /[dup] /Forall2_length. rewrite combine_length=> ?.
      move=> /Forall2_exists_exists_Forall2 [us].
      move=> /[dup] /Forall2_length. rewrite !combine_length=> ?.
      move=> /Forall2_exists_exists_Forall2 [Deltass].
      move=> /Forall2_Forall [/Forall_forall H].
      rewrite !combine_length=> ?.
      exists (fold_right merge Gamma'' Gamma's).
      exists (u'' ++ concat us).
      exists (Deltas'' ++ concat Deltass). do ? split.
      + apply: sty_permutation_trans; first by eassumption.
        have : sty_permutation ([Gamma'] ++ Deltas) ((Gamma'' :: Deltas'') ++ Deltas).
        { by apply: sty_permutation_app. }
        move=> /sty_permutation_trans. apply.
        apply: (sty_permutation_trans _ (([Gamma''] ++ Deltas'' ++ Gamma's) ++ concat Deltass)).
        * rewrite -!app_assoc /=.
          apply: (sty_permutation_app (_ :: _) _ (_ :: _) _); first done.
          apply: sty_permutation_app_concat; first by lia.
          apply /Forall2_Forall. split; last by (rewrite combine_length; lia).
          apply /Forall_forall => - [Delta''' [Gamma'''' Deltas''']] H''' /=.
          have [? [?]] : exists u''' A''', In (Deltas''', (u''', (Gamma'''', (A''', Delta''')))) (combine Deltass (combine us (combine Gamma's (combine u Deltas)))).
          { move: H''' => /In_nth_error [n].
            move=> /nth_error_combine [?].
            move=> /nth_error_combine [??].
            case E1: (nth_error us n)=> [u'''|]; first last.
            { exfalso. apply: (nth_error_length_neq Deltas us n); [congruence..|lia]. }
            case E2: (nth_error u n)=> [A'''|]; first last.
            { exfalso. apply: (nth_error_length_neq Deltas u n); [congruence..|lia]. }
            exists u''', A'''.
            apply: (nth_error_In _ n).
            by do 4 (apply /nth_error_combine; split; first done). }
          move=> /H /=. tauto.
        * apply: (sty_permutation_app _ _ (_ :: _) _); last done.
          rewrite app_assoc.
          apply: sty_permutation_trans; first by apply: sty_permutation_app_comm.
          rewrite app_assoc. apply: (sty_permutation_app _ _ [_] _); last done.
          apply: sty_permutation_sym. apply: sty_permutation_trans; first by apply: sty_permutation_fold_right_merge.
          by apply: sty_permutation_trans; last by apply: sty_permutation_app_comm.
      + apply: (nitlc_app _ (u'' :: Gamma'') (map (fun '(u, Gamma') => cons u Gamma') (combine us Gamma's)));
          [|by eassumption|].
        * have : length us = length Gamma's by lia.
          elim: (us) (Gamma's).
          { move=> [|??] /= ?; last done.
            by rewrite app_nil_r=> - [|?]. }
          move=> u''' ? IH [|Gamma''' ?] /=; first done.
          move=> [/IH] {}IH [|y].
          { have := IH 0.
            rewrite !map_cons !concat_cons /= map_nil concat_nil !app_nil_r=> {}IH.
            by apply: Permutation_app_middle. }
          have := IH (S y).
          rewrite !map_cons !concat_cons /= nth_merge map_nil concat_nil !app_nil_r=> {}IH.
          by apply: (Permutation_app_middle _ []).
        * apply /Forall2_Forall. split.
          ** apply /Forall_forall=> - [] /= C ? H'''.
             move: (H''') => /in_combine_r /in_map_iff [[u''' Gamma''']] [?] ?. subst.
             have [? [?]] : exists Delta''' Deltas''', 
               In (Deltas''', (u''', (Gamma''', (C, Delta''')))) (combine Deltass (combine us (combine Gamma's (combine u Deltas)))).
             { move: H''' => /In_In_combine_l => /(_ _ Deltass). case.
               { rewrite combine_length map_length combine_length. lia. }
               move=> Deltas'''.
               move=> /In_In_combine_l => /(_ _ Deltas). case.
               { rewrite !combine_length map_length combine_length. lia. }
               move=> Delta''' H'''. exists Delta''', Deltas'''.
               move: H''' => /In_nth_error [n].
               move=> /nth_error_combine [+ ?].
               move=> /nth_error_combine [+ ?].
               move=> /nth_error_combine [?].
               rewrite nth_error_map.
               move E: (nth_error _ n)=> [[??]|]; last done.
               move: E=> /nth_error_combine [??] [??]. subst.
               apply: (nth_error_In _ n).
               by do 4 (apply /nth_error_combine; split; first done). }
             move=> /H /=. tauto.
          ** rewrite map_length combine_length. lia.
      + apply /Forall_app. split; first done.
        apply /Forall_concat.
        apply /Forall_forall => u''' .
        have : length us = length (combine Gamma's (combine u Deltas)).
        { rewrite !combine_length. lia. }
        move=> /In_In_combine_l /[apply] - [?].
        have : length Deltass = length (combine us (combine Gamma's (combine u Deltas))).
        { rewrite !combine_length. lia. }
        move=> /In_In_combine_r /[apply] - [?] /H /=. tauto.
      + apply: Forall2_app; first done.
        apply: Forall2_concat.
        apply /Forall2_Forall. split; [|lia].
        apply /Forall_forall=> - [] u''' Deltas''' H'''.
        suff [? /H /=] : exists T, In (Deltas''', (u''', T)) (combine Deltass (combine us (combine Gamma's (combine u Deltas)))) by tauto.
        move: H''' => /In_nth_error [n].
        move=> /nth_error_combine [Husn ?].
        move E: (nth_error (combine Gamma's (combine u Deltas)) n) => [T|].
        * exists T.
          apply: (nth_error_In _ n).
          by do 2 (apply /nth_error_combine; split; first done).
        * exfalso. move: E => /nth_error_None.
          rewrite !combine_length.
          have : nth_error us n <> None by congruence.
          move=> /nth_error_Some. lia.
    - move=> t M IH N t0 A Gamma0 Gamma H1N.
      move=> /stlcE [] s' t' H1M ?? HG0G /=. subst.
      move=> /nitlcE [u'] [B'] [?] [Hssim]. subst.
      have -> : subst (scons (var 0) (fun x : nat => ren S (scons N var x))) M = 
        subst (scons (ren S N) var) (ren swap M).
      { rewrite subst_ren. by apply: subst_ext=> - [|[|x]] /=. }
      pose P n := match n with 0 => False | S _ => True end.
      have : (forall x, {P x} + {~ P x}) by (subst P; case; tauto).
      have /[apply] := allfv_dec P (ren swap M). case=> H'M.
      { have /nitlc_ren /[apply] : forall x1 x2, S x1 = S x2 -> x1 = x2 by lia.
        have -> : ren S (subst (scons (ren S N) var) (ren swap M)) = ren swap M.
        { rewrite -[RHS]subst_var ren_subst.
          apply: ext_allfv_subst. apply: allfv_impl H'M.
          by subst P=> - [|x] /=. }
        move=> H2M. exists Gamma, nil, nil. do ? constructor; [done..|].
        apply: nitlc_ren_swap. by apply: H2M. }
      have /IH {}IH : size_tm (ren swap M) < size_tm (lam (sarr s' t') M).
      { move=> /=. by rewrite size_tm_ren. }
      have : stlc (s :: s' :: Gamma0) (ren swap M) t'.
      { by apply: stlc_ren H1M=> - [|[|?]] /=. }
      have : stlc (s' :: Gamma0) (ren S N) s.
      { by apply: stlc_ren; last by eassumption. }
      have ? : Forall (ssim s') u'.
      { move: Hssim => /ssimE [?] [?] [?] [[??]] []. by subst. }
      have : env_ssim (s' :: Gamma0) (u' :: Gamma).
      { by move=> [|?] /=; [|apply: HG0G]. }
      move=> /IH /[apply] /[apply] /[apply].
      move=> [Gamma'] [u] [Deltas] [HG'Ds] [H2M] [? HuDs].
      exists (skipn 1 Gamma'), u, (map (skipn 1) Deltas). do ? split.
      + by move: HG'Ds => /(sty_permutation_skipn 1).
      + econstructor; first done.
        move: (Gamma') H2M HG'Ds => [|u0 ?].
        { move=> /(weakening [[]; u']) /=.
          by move=> /nitlc_ren_swap. }
        move=> /nitlc_ren_swap /= + /(_ 0) HG'Ds.
        have [u''' Hu'''] : exists u''', sty_permutation [[u''' ++ u0]] [[u']].
        { exists (concat (map ((nth 0)^~ []) Deltas)).
          move=> [|x]; last done.
          move: HG'Ds.
          rewrite !map_cons /= !concat_cons !map_nil !concat_nil !app_nil_r.
          move=> /Permutation_sym. apply: Permutation_trans.
          by apply: Permutation_app_comm. }
        move=> /(weakening [u''']) /=.
        apply: permutation=> - [|x] /=; last done.
        by apply: (Hu''' 0).
      + done.
      + apply: Forall2_map_r.
        apply: Forall2_impl HuDs=> ? Delta.
        move=> /(nitlc_allfv_ren Nat.pred _ (skipn 1 Delta)).
        rewrite ren_ren ren_id. apply.
        * apply: allfv_ren. apply: allfv_trivial=> ? /=.
          apply: allfv_ren. by apply: allfv_trivial=> ? /= <-.
        * apply: allfv_ren. apply: allfv_trivial.
          by move: (Delta) => [|??] [|?] /=. }
  move=> [?] [HM] [Hu ?].
  exists Gamma', u, Deltas. do ? split; [done|done| |done].
  move: HM => /nitlc_allfv_not_nil.
  move: (u) Hu => [|??].
  - move=> _ H. exfalso. apply: H0M.
    apply: allfv_impl H. by case.
  - move=> ??. constructor; first done.
    apply: stlc_nitlc_ssim; [|eassumption..].
    apply: stlc_subst; [eassumption|].
    by move=> [|?] ? => [[<-]|]; [|constructor].
Qed.

(* subject expansion for I-reduction *)
Theorem stepI_expansion M N Gamma0 t0 Gamma A : stepI M N -> stlc Gamma0 M t0 ->
  env_ssim Gamma0 Gamma -> nitlc Gamma N A -> nitlc Gamma M A.
Proof.
  move=> H. elim: H Gamma0 t0 Gamma A.
  - move=> [?|s t] > ? ? t0 Gamma A H *.
    + by move: H => /stlcE [] > /stlcE [].
    + have ? : t0 = t.
      { by move: H => /stlcE [] > /stlcE [] > ?? []. }
      subst t0. apply: stepIRed_expansion; by eassumption.
  - move=> > ? IH >.
    move=> /stlcE [] ????? HG0G. subst.
    move=> /nitlcE [?] [?] [?] [H /IH {}IH]. subst.
    econstructor; first done.
    apply: IH; first by eassumption.
    move=> [|y] /=; last by apply HG0G.
    move: H => /ssimE [?] [?] [?] [[??]] [?]. by subst.
  - move=> > ? IH >.
    move=> /stlcE [] ??? HG0G. subst.
    move=> /nitlcE [?] [?] [?] [?] [/IH {}IH] ?.
    econstructor.
    + by eassumption.
    + apply: IH.
      * by eassumption.
      * apply: env_ssim_sty_permutation_In; [by eassumption..|by left].
    + done.
  - move=> > ? IH >.
    move=> /stlcE [] ??? HG0G. subst.
    move=> /nitlcE [?] [Deltas] [?] [H] [?] HN'.
    econstructor; [by eassumption..|].
    move: H (HG0G) => /env_ssim_sty_permutation_In /[apply].
    elim: HN'; first done.
    move=> ?? Delta ? /IH {}IH ? IH' H'. constructor.
    + apply: IH; first by eassumption.
      apply: H'. right. by left.
    + by apply: IH' => ? /= [<-|?]; apply: H'; [left|do 2 right].
Qed.

Theorem nitlc_expansion M N Gamma0 t Gamma A :
  stlc Gamma0 M t -> step M N -> nitlc Gamma N A -> env_ssim Gamma0 Gamma -> ssim t A ->
  exists (Gamma' : environment) (A' : nity),
    nitlc Gamma' M A' /\ env_ssim Gamma0 Gamma' /\ ssim t A'.
Proof.
  move=> + H + /[dup] ?. move: H => [|[|]].
  - move=> /stepI_expansion /[apply] /[apply] /[apply] *.
    do ? econstructor; by eassumption.
  - move=> /stepG_expansion + ? => /[apply] *.
    do ? econstructor; by eassumption.
  - move=> + /[dup] HM.
    move=> /stepK_expansion /[apply] /[apply] /[apply].
    move=> [Gamma'] [HG0G']. case: M HM=> [>?|>?|> HM [A']] *; [by eauto..|].
    exists Gamma', A'.
    split; [done|split;[done|]].
    apply: stlc_nitlc_ssim; by eassumption.
Qed.

Theorem nitlc_steps_type_inference M N Gamma0 t : stlc Gamma0 M t -> steps M N -> nf N ->
  exists Gamma A, nitlc Gamma M A /\ env_ssim Gamma0 Gamma /\ ssim t A.
Proof.
  move=> + /clos_rt_rt1n_iff H.
  elim: H.
  - move=> {}N /stlc_nitlc_nf /[apply] - [Gamma] [A] [?] [H ?].
    exists Gamma, A. do ? split; [done| |done].
    elim: H; first by case.
    move=> > ?? H [|?] /=; first done.
    by apply: H.
  - move=> > + _ IH.
    move=> /[dup] H + /[dup] H'.
    move=> /stlc_reduction /[apply] /IH /[apply].
    move=> [?] [?] [?] [??].
    apply: nitlc_expansion; by eassumption.
Qed.

Theorem nitlc_type_inference M Gamma0 t : stlc Gamma0 M t ->
  exists Gamma A,
    nitlc Gamma M A /\
    Forall2 (fun s u => u <> [] /\ Forall (ssim s) u) Gamma0 Gamma /\
    ssim t A.
Proof.
  move=> /[dup] HM /[dup] /nitlc_steps_type_inference H /stepIG_normalization [N] [HMN] [].
  move=> /stepK_normalization /[apply] - [N'] [HNN'] [/redex_count_zero_spec] /H {}H _.
  suff : steps M N'.
  { move=> /H [Gamma] [A] [H'M] [HG0G HtA].
    suff: exists Gamma', nitlc Gamma' M A /\ Forall2 (fun s u => Forall (ssim s) u) Gamma0 Gamma'.
    { move=> [Gamma'] [? H'].
      exists (merge (map (fun s => [lift_sty s]) Gamma0) Gamma'), A.
      do ? split; [by apply: weakening| |done].
      elim: H'; first done.
      move=> *. by do ? constructor; auto using ssim_lift_sty. }
    exists (merge (repeat (@nil nity) (length Gamma0)) (firstn (length Gamma0) Gamma)). split.
    - apply: weakening.
      apply: nitlc_allfv H'M.
      move: HM => /stlc_allfv_not_None. apply: allfv_impl.
      clear. elim: Gamma0 Gamma.
      + by move=> ? [|?].
      + move=> ?? IH [|??]; first done.
        move=> [|?]; first done.
        move=> /IH. by apply.
    - elim: Gamma0 Gamma HG0G {H'M HM H}.
      + by move=> [|??] /=.
      + move=> ? Gamma0 IH [|??] /=.
        * move=> ?. constructor; first done.
          clear. elim: Gamma0; first done.
          move=> *. by constructor.
        * move=> HG0G. constructor; first by apply: (HG0G 0).
          apply: IH=> x. by apply: (HG0G (S x)). }
  move: HMN HNN'=> /clos_rt_rt1n_iff. elim.
  - move=> ? /clos_rt_rt1n_iff. elim.
    + move=> ?. apply: rt_refl.
    + move=> > *. apply: rt_trans; [|by eassumption].
      apply: rt_step. right. by right.
  - move=> M1 M2 M3 H' /clos_rt_rt1n_iff HM2M3 _ HM3N'.
    apply: (@rt_trans _ _ _ M2).
    + apply: rt_step. rewrite /step. tauto.
    + apply: (@rt_trans _ _ _ M3).
      * rewrite /step. elim: HM2M3; [|by eauto using clos_refl_trans..].
        move=> *. apply: rt_step. tauto.
      * rewrite /step. elim: HM3N'; [|by eauto using clos_refl_trans..].
        move=> *. apply: rt_step. tauto.
Qed.

Check nitlc_type_inference.

Print Assumptions nitlc_type_inference.
