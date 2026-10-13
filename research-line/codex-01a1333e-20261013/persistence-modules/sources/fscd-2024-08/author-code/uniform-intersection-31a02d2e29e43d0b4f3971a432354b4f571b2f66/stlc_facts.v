(*
  facts about the simplty typed lambda-calculus
*)

Require Import Lia List Relations PeanoNat.
Import ListNotations.

From NonIdempotent Require Import facts stlc.
Require Import ssreflect ssrbool.

Arguments nth_error_split {A l n a}.
Arguments in_split {A x}.

Scheme nf_ind' := Induction for nf Sort Prop
  with neutral_ind' := Induction for neutral Sort Prop.

Inductive stlc_app_spec (Gamma : list sty) (M N : tm) (t : sty) : Prop :=
  | stlc_app_spec_intro s : stlc Gamma M (sarr s t) -> stlc Gamma N s -> stlc_app_spec Gamma M N t.

Inductive stlc_lam_spec (Gamma : list sty) (t' : sty) (M : tm) (t : sty) : Prop :=
  | stlc_lam_spec_intro s u : stlc (s :: Gamma) M u -> t = sarr s u -> t = t' -> stlc_lam_spec Gamma t' M t.

Lemma stlcE Gamma M t : stlc Gamma M t ->
  match M with
  | var x => nth_error Gamma x = Some t
  | app M N => stlc_app_spec Gamma M N t
  | lam t' M => stlc_lam_spec Gamma t' M t
  end.
Proof.
  intros [].
  - done.
  - by econstructor; first by eassumption.
  - by econstructor; first by eassumption.
Qed.

Lemma ren_ext M xi1 xi2 :
  (forall x, xi1 x = xi2 x) ->
  ren xi1 M = ren xi2 M.
Proof.
  elim: M xi1 xi2=> /=.
  - move=> *. by congr var.
  - move=> ? IH1 ? IH2 > ?. congr app.
    + by apply: IH1.
    + by apply: IH2.
  - move=> ?? IH > ?. congr lam.
    apply: IH. move=> [|x] /=; by [|congr S].
Qed.

Lemma subst_ext M sigma1 sigma2 :
  (forall x, sigma1 x = sigma2 x) ->
  subst sigma1 M = subst sigma2 M.
Proof.
  elim: M sigma1 sigma2=> /=.
  - move=> >. apply.
  - move=> ? IH1 ? IH2 > ?. congr app.
    + by apply: IH1.
    + by apply: IH2.
  - move=> ?? IH > Hsigma. congr lam.
    apply: IH. move=> [|x] /=; by [|congr ren].
Qed.

Lemma ren_id M : ren id M = M.
Proof.
  elim: M=> /=.
  - done.
  - by move=> ? -> ? ->.
  - move=> ?? IH. congr lam. rewrite -[RHS]IH.
    apply: ren_ext. by case.
Qed.

Lemma subst_var M : subst var M = M.
Proof.
  elim: M=> /=.
  - done.
  - by move=> ? -> ? ->.
  - move=> ?? IH. congr lam. rewrite -[RHS]IH.
    apply: subst_ext. by case.
Qed.

Lemma ren_as_subst xi M : ren xi M = subst (funcomp var xi) M.
Proof.
  elim: M xi=> /=.
  - done.
  - move=> ? IH1 ? IH2 ?. by rewrite IH1 IH2.
  - move=> ?? IH ?. congr lam. rewrite IH.
    apply: subst_ext. by case.
Qed.

Lemma ren_ren xi1 xi2 M :
  ren xi2 (ren xi1 M) = ren (funcomp xi2 xi1) M.
Proof.
  elim: M xi1 xi2=> /=.
  - done.
  - move=> ? IH1 ? IH2 ??. by rewrite IH1 IH2.
  - move=> ?? IH ??. congr lam. rewrite IH.
    rewrite !ren_as_subst. apply: subst_ext. by case.
Qed.

Lemma ren_subst xi sigma M :
  ren xi (subst sigma M) = subst (funcomp (ren xi) sigma) M.
Proof.
  elim: M xi sigma=> /=.
  - done.
  - move=> ? IH1 ? IH2 ??. by rewrite IH1 IH2.
  - move=> ?? IH ??. congr lam. rewrite IH.
    apply: subst_ext.
    move=> [|x] /=; [done|].
    rewrite !ren_ren.
    rewrite !ren_as_subst. by apply: subst_ext.
Qed.

Lemma subst_ren xi sigma M :
  subst sigma (ren xi M) = subst (funcomp sigma xi) M.
Proof.
  elim: M xi sigma=> /=.
  - done.
  - move=> ? IH1 ? IH2 ??. by rewrite IH1 IH2.
  - move=> ?? IH ??. congr lam. rewrite IH.
    apply: subst_ext. by case.
Qed.

Lemma subst_subst sigma1 sigma2 M :
  subst sigma2 (subst sigma1 M) = subst (funcomp (subst sigma2) sigma1) M.
Proof.
  elim: M sigma1 sigma2=> /=.
  - done.
  - move=> ? IH1 ? IH2 ??. by rewrite IH1 IH2.
  - move=> ?? IH ??. congr lam. rewrite IH.
    apply: subst_ext=> - [|x] /=; [done|].
    rewrite ren_subst subst_ren.
    by apply: subst_ext.
Qed.

Lemma allfv_trivial (P : nat -> Prop) t : (forall x, P x) -> allfv P t.
Proof.
  elim: t P=> /=; [by auto..|].
  move=> ?? IH *. by apply: IH => - [|?].
Qed.

Lemma allfv_impl (P Q : nat -> Prop) t : 
  (forall x, P x -> Q x) -> allfv P t -> allfv Q t.
Proof.
  elim: t P Q => /=.
  - move=> >. by apply.
  - move=> ? IH1 ? IH2 > /[dup] /IH1 {}IH1 /IH2 {}IH2. tauto.
  - move=> ? > IH > H /=. apply: IH.
    by case.
Qed.

Lemma allfv_allfv_impl (P Q : nat -> Prop) t : 
  allfv (fun x => P x -> Q x) t -> allfv P t -> allfv Q t.
Proof.
  elim: t P Q => /=.
  - move=> >. by apply.
  - move=> ? IH1 ? IH2 > [/IH1 {}IH1] /IH2 {}IH2.
    by move=> [/IH1] {}IH1 /IH2 {}IH2.
  - move=> ? > IH > H /=. apply: IH.
    apply: allfv_impl H. by case.
Qed.

Lemma allfv_dec P M : (forall x, {P x} + {not (P x)}) -> {allfv P M} + {not (allfv P M)}.
Proof.
  elim: M P=> /=.
  - done.
  - move=> s IH1 t IH2 P /[dup] /(IH1 P) {}IH1 /(IH2 P) {}IH2. tauto.
  - move=> ?? IH P H.
    case: (IH (scons True P)); [|by auto..].
    move=> [|?] /=; by auto.
Qed.

Lemma allfv_ren (P : nat -> Prop) xi t :
  allfv (funcomp P xi) t -> allfv P (ren xi t).
Proof.
  elim: t P xi.
  - done.
  - move=> ? IH1 ? IH2 > /= [??]. by auto.
  - move=> ?? IH > /= H. apply: IH.
    by apply: allfv_impl H => - [|?].
Qed.

Lemma allfv_ren' (P : nat -> Prop) xi t :
  allfv P (ren xi t) -> allfv (funcomp P xi) t.
Proof.
  elim: t P xi.
  - done.
  - move=> ? IH1 ? IH2 > /= [??]. split.
    + by apply: IH1.
    + by apply: IH2.
  - move=> ?? IH > /= /IH.
    by apply: allfv_impl => - [|?].
Qed.

Lemma allfv_subst (P : nat -> Prop) sigma t :
  allfv (fun x => allfv P (sigma x)) t -> allfv P (subst sigma t).
Proof.
  elim: t P sigma.
  - done.
  - move=> ? IH1 ? IH2 > /= [??]. by auto.
  - move=> ?? IH > /= H. apply: IH.
    apply: allfv_impl H => - [|?] /= H; [done|].
    apply /allfv_ren. by apply: allfv_impl H.
Qed.

Lemma allfv_subst' (P : nat -> Prop) sigma t :
  allfv P (subst sigma t) -> allfv (fun x => allfv P (sigma x)) t.
Proof.
  elim: t P sigma.
  - done.
  - move=> ? IH1 ? IH2 > /= [??]. by auto.
  - move=> ?? IH > /= /IH.
    apply: allfv_impl => - [|?] /=; [done|].
    move=> /allfv_ren'. by apply: allfv_impl.
Qed.

Lemma ext_allfv_subst sigma1 sigma2 t : allfv (fun x=> sigma1 x = sigma2 x) t ->
  subst sigma1 t = subst sigma2 t.
Proof.
  elim: t sigma1 sigma2.
  - by move=> > /= ?.
  - by move=> ? IH1 ? IH2 ?? /= [/IH1 -> /IH2 ->].
  - move=> ?? IH > /= Hsigma. congr lam. apply: IH.
    apply: allfv_impl Hsigma.
    by move=> [|x] /= => [|->].
Qed.

Lemma ext_allfv_ren xi1 xi2 t : allfv (fun x=> xi1 x = xi2 x) t -> ren xi1 t = ren xi2 t.
Proof.
  move=> H. rewrite !ren_as_subst. apply: ext_allfv_subst.
  by apply: allfv_impl H => ? /= ->.
Qed.

Lemma allfv_list M : exists l, forall P, allfv P M <-> Forall P l.
Proof.
  elim: M.
  - move=> x. exists [x] => P /=. split.
    + move=> ?. by constructor.
    + by move=> /Forall_cons_iff [].
  - move=> > [l1 IH1] > [l2 IH2]. exists (l1 ++ l2) => P /=. split.
    + move=> [??]. apply /Forall_app. split.
      * by apply /IH1.
      * by apply /IH2.
    + by move=> /Forall_app [/IH1 ?] /IH2.
  - move=> > [l IH]. exists (concat (map (fun x => match x with 0 => [] | S x => [x] end) l)).
    move=> P /=. split.
    + move=> /IH. elim; first done.
      move=> [|x] ? /=; first done.
      by constructor.
    + move=> H. apply /IH. elim: l {IH} H; first done.
      move=> [|x] ? IH /=.
      * move=> ?. constructor; first done.
        by apply: IH.
      * move=> /Forall_cons_iff [??].
        constructor; first done.
        by apply: IH.
Qed.

Lemma stlc_allfv_ren Gamma Delta xi M t : allfv (fun x => forall s, nth_error Gamma x = Some s -> nth_error Delta (xi x) = Some s) M ->
  stlc Gamma M t -> stlc Delta (ren xi M) t.
Proof.
  move=> + H. elim: H xi Delta.
  - move=> > ? > /= H. constructor. by apply: H.
  - move=> > ? IH1 ? IH2 > /= [] /IH1 {}IH1 /IH2 {}IH2.
    econstructor; by eassumption.
  - move=> > ? IH > /= H. constructor.
    apply: IH. by apply: allfv_impl H => - [|?] /=.
Qed.

Lemma stlc_ren Gamma Delta xi M t : (forall x s, nth_error Gamma x = Some s -> nth_error Delta (xi x) = Some s) ->
  stlc Gamma M t -> stlc Delta (ren xi M) t.
Proof.
  move=> ?. apply: stlc_allfv_ren. by apply: allfv_trivial.
Qed.

Lemma stlc_inj Gamma M t1 t2 :
  stlc Gamma M t1 ->
  stlc Gamma M t2 ->
  t1 = t2.
Proof.
  move=> H. elim: H t2.
  - move=> > ?? /stlcE. congruence.
  - by move=> > ? IH ? _ ? /stlcE [] > /IH [].
  - move=> > ? IH ? /stlcE [] > + -> [??]. by subst.
Qed.

Lemma stlc_allfv_not_None Gamma M t :
  stlc Gamma M t ->
  allfv (fun x => nth_error Gamma x <> None) M.
Proof.
  elim.
  - by move=> > /= ->.
  - by move=> > /=.
  - move=> > /= ?. by apply: allfv_impl => -[|?].
Qed.

(* typing is preserved under substitutions *)
Theorem stlc_subst {Gamma Delta M t} sigma :
  stlc Gamma M t ->
  (forall n s, nth_error Gamma n = Some s -> stlc Delta (sigma n) s) ->
  stlc Delta (subst sigma M) t.
Proof.
  move=> H. elim: H Delta sigma.
  - move=> > ??? H /=. by apply: H.
  - move=> > ? IH1 ? IH2 > H /=. econstructor.
    + by apply: IH1.
    + by apply: IH2.
  - move=> > ? IH > H /=. constructor.
    apply: IH=> - [|n] /=.
    + move=> ? [<-]. by constructor.
    + move=> ? /H ?. by apply: stlc_ren; last by eassumption.
Qed.

Theorem stepI_reduction M N Gamma t : stepI M N -> stlc Gamma M t -> stlc Gamma N t.
Proof.
  move=> H. elim: H Gamma t.
  - move=> > ? >.
    move=> /stlcE [] ? + HN.
    move=> /stlcE [] ?? HM [??] ?. subst.
    apply: stlc_subst; first by eassumption.
    move=> [|n] ? /=; first by congruence.
    move=> ?. by constructor.
  - move=> > ? IH >.
    move=> /stlcE [] *. subst.
    constructor. by apply: IH.
  - move=> > ? IH >.
    move=> /stlcE [] *. subst.
    econstructor; [|by eassumption].
    by apply: IH.
  - move=> > ? IH >.
    move=> /stlcE [] *. subst.
    econstructor; [by eassumption|].
    by apply: IH.
Qed.

Theorem stepK_reduction M N Gamma t : stepK M N -> stlc Gamma M t -> stlc Gamma N t.
Proof.
  move=> H. elim: H Gamma t.
  - move=> > _ > /stlcE [] ?.
    move=> /stlcE [] ?? + [??] ??. subst.
    move=> /(stlc_allfv_ren _ _ (Nat.pred)).
    rewrite ren_ren ren_id. apply.
    apply: allfv_ren. by apply: allfv_trivial => ? /=.
  - move=> > ? IH >.
    move=> /stlcE [] *. subst.
    constructor. by apply: IH.
  - move=> > ?? IH >.
    move=> /stlcE [] *. subst.
    by econstructor; [eassumption|apply: IH].
  - move=> > ? IH >.
    move=> /stlcE [] *. subst.
    by econstructor; [eassumption|apply: IH].
  - move=> > ? IH >.
    move=> /stlcE [] *. subst.
    by econstructor; [apply: IH|eassumption].
Qed.

Theorem stepG_reduction M N Gamma t : stepG M N -> stlc Gamma M t -> stlc Gamma N t.
Proof.
  move=> H. elim: H Gamma t.
  - move=> > /stlcE [] ?.
    move=> /stlcE [] ??.
    move=> /stlcE [] ??? -> [??] [??] [??] ?. subst.
    econstructor. econstructor.
    + econstructor. apply: stlc_ren; last by eassumption.
      move=> [|[|?] ?] /=; congruence.
    + by apply: stlc_ren; last by eassumption.
  - move=> > ? IH >.
    move=> /stlcE [] *. subst.
    constructor. by apply: IH.
  - move=> > ? IH >.
    move=> /stlcE [] *. subst.
    by econstructor; [apply: IH|eassumption].
  - move=> > ? IH >.
    move=> /stlcE [] *. subst.
    by econstructor; [eassumption|apply: IH].
Qed.

(* subject reduction wrt. stepI, stepG, stepK *)
Theorem stlc_reduction M N Gamma t : step M N -> stlc Gamma M t -> stlc Gamma N t.
Proof.
  by move=> [/stepI_reduction|[/stepG_reduction|/stepK_reduction]]; apply.
Qed.

Fixpoint size_sty (t : sty) : nat :=
  match t with
  | satom _ => 1
  | sarr s t => 1 + size_sty s + size_sty t
  end.

Fixpoint size_tm (M : tm) :=
  match M with
  | var _ => 1
  | app M N => S (size_tm M) + (size_tm N)
  | lam _ M => S (size_tm M)
  end.

Lemma size_tm_ren xi M : size_tm (ren xi M) = size_tm M.
Proof.
  elim: M xi.
  - done.
  - move=> > IH1 ? IH2 ? /=. by rewrite IH1 IH2.
  - move=> > IH ? /=. by rewrite IH.
Qed.

Lemma allfv_stepI P M N : stepI M N -> allfv P M -> allfv P N.
Proof.
  move=> H. elim: H P.
  - move=> > ?? /= [HM ?]. apply: allfv_subst.
    by apply: allfv_impl HM=> - [|x].
  - move=> > ? IH > /=. by apply: IH.
  - move=> > ? IH > /= []. by auto.
  - move=> > ? IH > /= []. by auto.
Qed.

Lemma allfv_stepI' P M N : stepI M N -> allfv P N -> allfv P M.
Proof.
  move=> H. elim: H P.
  - move=> ? {}M {}N H1M P /= /allfv_subst' /= H2M. split.
    + by apply: allfv_impl H2M=> - [|x] /=.
    + have [l Hl] := allfv_list M.
      have : In 0 l.
      { have [|H] := In_dec Nat.eq_dec 0 l; first done.
        exfalso. apply: H1M. apply /Hl.
        elim: (l) H; first done.
        move=> [|?] > IH /= /Decidable.not_or [?] /IH ?; first done.
        by constructor. }
      move=> /in_split [?] [?] ?. subst l.
      by move: H2M => /Hl /Forall_app [?] /Forall_cons_iff [] /=.
  - move=> > ? IH > /=. by apply: IH.
  - move=> > ? IH > /= []. by auto.
  - move=> > ? IH > /= []. by auto.
Qed.

Lemma allfv_stepG P M N : stepG M N -> allfv P M -> allfv P N.
Proof.
  move=> H. elim: H P.
  - move=> > /= [HM HN]. split.
    + apply: allfv_ren.
      by apply: allfv_impl HM=> - [|[|x]] /=.
    + by apply: allfv_ren.
  - move=> > ? IH > /=. by apply: IH.
  - move=> > ? IH > /= []. by auto.
  - move=> > ? IH > /= []. by auto.
Qed.

Lemma allfv_stepG' P M N : stepG M N -> allfv P N -> allfv P M.
Proof.
  move=> H. elim: H P.
  - move=> > /= [/allfv_ren' H2M1] /allfv_ren' H2M2. split.
    + by apply: allfv_impl H2M1=> - [|[|?]] /=.
    + by apply: allfv_impl H2M2=> - [|?] /=.
  - move=> > ? IH > /=. by apply: IH.
  - move=> > ? IH > /= []. by auto.
  - move=> > ? IH > /= []. by auto.
Qed.
