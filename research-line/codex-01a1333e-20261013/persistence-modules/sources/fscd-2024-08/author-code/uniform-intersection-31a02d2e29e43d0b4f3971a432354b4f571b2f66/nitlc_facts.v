(*
  facts about the non-idempotently typed lambda-calculus
*)

Require Import PeanoNat Lia List Relations Permutation.
Import ListNotations.

From NonIdempotent Require Import facts stlc stlc_facts nitlc.
Require Import ssreflect ssrbool ssrfun.

#[local] Arguments nth_error_split {A l n a}.
#[local] Arguments Permutation_in {A l l' x}.
#[local] Arguments Permutation_nil_cons {A l x}.
#[local] Arguments in_split {A x l}.


Lemma nitlcE Gamma M A : nitlc Gamma M A ->
  match M with
  | var x => (exists t, ssim t A) /\ In A (nth x Gamma nil)
  | app M N => exists Gamma' Deltas u,
      sty_permutation [Gamma] (Gamma' :: Deltas) /\
      nitlc Gamma' M (niarr u A) /\
      Forall2 (fun B Delta => nitlc Delta N B) u Deltas
  | lam t M => exists u B,
      A = niarr u B /\
      ssim t (niarr u B) /\
      nitlc (cons u Gamma) M B
  end.
Proof.
  case; by eauto 10.
Qed.

Notation env_ssim Gamma Delta :=
  (forall x, match nth_error Gamma x with Some s => Forall (ssim s) (nth x Delta []) | None => True end).

Lemma ssimE t A : ssim t A ->
  match t with
  | satom x => A = niatom x
  | sarr s t => exists C u B, A = niarr (cons C u) B /\ Forall (ssim s) (cons C u) /\ ssim t B
  end.
Proof.
  case.
  + done.
  + move=> *.
    do 5 econstructor; eassumption.
Qed.

Lemma nitlc_ssim Gamma M A : nitlc Gamma M A -> exists t, ssim t A.
Proof.
  elim.
  - move=> *. eexists. by eassumption.
  - move=> > ?? [t] /ssimE.
    case: t => [?|??]; first done.
    move=> [?] [?] [?] [[]] ? -> [??] ?.
    eexists. by eassumption.
  - move=> *. eexists. by eassumption.
Qed.

(* intermediate induction principle, not including additional constraints *)
Lemma nitlc_ind' (P : environment -> tm -> nity -> Prop) :
  (forall Gamma t x A,
    ssim t A ->
    In A (nth x Gamma nil) -> 
    P Gamma (var x) A) ->
  (forall Gamma Deltas Gamma' t M N u A,
    Deltas <> [] ->
    ssim t A ->
    sty_permutation [Gamma] (Gamma' :: Deltas) ->
    nitlc Gamma' M (niarr u A) ->
    P Gamma' M (niarr u A) ->
    Forall2 (fun (B : nity) (Delta : environment) => nitlc Delta N B) u Deltas ->
    Forall2 (fun (B : nity) (Delta : environment) => P Delta N B) u Deltas ->
    P Gamma (app M N) A) ->
  (forall Gamma t M u B,
    ssim t (niarr u B) ->
    nitlc (u :: Gamma) M B ->
    P (u :: Gamma) M B ->
    P Gamma (lam t M) (niarr u B)) ->
  forall Gamma M A, nitlc Gamma M A -> P Gamma M A.
Proof.
  move=> IH1 IH2 IH3 + M. elim: M.
  - move=> > /nitlcE [] [?]. by apply: IH1.
  - move=> M IHM N IHN Gamma A.
    move=> /[dup] /nitlc_ssim [t ?].
    move=> /nitlcE [Gamma'] [Deltas] [u] [?] [HM HN].
    apply: IH2; try eassumption.
    + move: HM HN => /nitlc_ssim [?] H. inversion H. subst.
      move=> /Forall2_length. by case: (Deltas).
    + by apply: IHM.
    + apply: Forall2_impl HN => *. by apply: IHN.
  - move=> t M IHM Gamma A /nitlcE.
    move=> [?] [?] [?] [??]. subst A.
    apply: IH3; [assumption..|].
    by apply: IHM.
Qed.

Lemma sty_permutation_mergeL Gamma' Gamma Delta Gammas Deltas :
  sty_permutation (Gamma :: Gammas) (Delta :: Deltas) ->
  sty_permutation ((merge Gamma' Gamma) :: Gammas) ((merge Gamma' Delta) :: Deltas).
Proof.
  move=> H x.
  rewrite /= !nth_merge -!app_assoc.
  by apply: Permutation_app; [|apply: H].
Qed.

Theorem weakening Gamma' Gamma M A :
  nitlc Gamma M A -> nitlc (merge Gamma' Gamma) M A.
Proof.
  move=> H. elim /nitlc_ind': H Gamma'.
  - move=> *. apply: nitlc_var; [by eassumption|]. by apply: In_nth_merge_r.
  - move=> {}Gamma Deltas Gamma' t {}M N u {}A.
    move=> _ Hta HGamma IHM IH'M IHN IH'N Gamma''.
    apply: (nitlc_app _ (merge Gamma'' Gamma') Deltas).
    + by apply (sty_permutation_mergeL _ _ _ nil Deltas).
    + apply: IH'M.
    + by apply: Forall2_impl IH'N => > /(_ nil).
  - move=> {}Gamma t {}M u B ? IH'M IHM Gamma'.
    constructor; [assumption|].
    by apply: (IHM ([] :: Gamma')).
Qed.

Lemma sty_permutation_trans Gammas1 Gammas2 Gammas3 :
  sty_permutation Gammas1 Gammas2 ->
  sty_permutation Gammas2 Gammas3 ->
  sty_permutation Gammas1 Gammas3.
Proof.
  move=> H1 H2 x. move: (H1 x) (H2 x). apply: Permutation_trans.
Qed.

Lemma sty_permutation_sym Gammas1 Gammas2 :
  sty_permutation Gammas1 Gammas2 ->
  sty_permutation Gammas2 Gammas1.
Proof.
  move=> H x. by apply: Permutation_sym.
Qed.

Lemma sty_permutation_app Gammas1 Gammas2 Deltas1 Deltas2 :
  sty_permutation Gammas1 Deltas1 ->
  sty_permutation Gammas2 Deltas2 ->
  sty_permutation (Gammas1 ++ Gammas2) (Deltas1 ++ Deltas2).
Proof.
  move=> H1 H2 x. rewrite !map_app !concat_app. by apply: Permutation_app.
Qed.

Lemma sty_permutation_app_comm Gammas1 Gammas2 :
  sty_permutation (Gammas1 ++ Gammas2) (Gammas2 ++ Gammas1).
Proof.
  move=> x. rewrite !map_app !concat_app. by apply: Permutation_app_comm.
Qed.

(* actually can be a special case of weakening with <= instead of permutation *)
Theorem permutation Gamma1 Gamma2 M A : sty_permutation [Gamma1] [Gamma2] -> nitlc Gamma1 M A -> nitlc Gamma2 M A.
Proof.
  move=> + H. elim /nitlc_ind': H Gamma2.
  - move=> {}Gamma1 t x {}A ?? Gamma2 H. econstructor; [by eassumption|].
    move: H=> /(_ x) /Permutation_in=> /(_ A) /=.
    rewrite !app_nil_r. by apply.
  - move=> {}Gamma1 Deltas Gamma' t {}M N u {}A ??? IH1M IH2M IH1N IH2N.
    move=> Gamma2 /sty_permutation_sym ?.
    econstructor; [ |by eassumption..].
    apply: sty_permutation_trans; by eassumption.
  - move=> {}Gamma t {}M u B ?? IH Gamma2 H.
    constructor; [done|].
    by apply: IH=> - [|x] /=; [|apply: H].
Qed.

Lemma sty_permutation_skipn n Gamma Deltas :
  sty_permutation [Gamma] Deltas ->
  sty_permutation [skipn n Gamma] (map (skipn n) Deltas).
Proof.
  move=> H x. move: (H (n + x))=> /=.
  rewrite nth_skipn map_map.
  congr Permutation. congr concat.
  apply: map_ext=> ?. by rewrite nth_skipn.
Qed.

Lemma ssim_inj A s t : ssim s A -> ssim t A -> s = t.
Proof.
  elim: s t A.
  - move=> ? [?|??] ?.
    + by move=> /ssimE -> /ssimE [->].
    + by move=> /ssimE -> /ssimE [?] [?] [?] [].
  - move=> s1 IH1 s2 IH2 [?|t1 t2] ?.
    + by move=> /ssimE [?] [?] [?] [->] ? /ssimE.
    + move=> /ssimE [?] [?] [?] [->] [/Forall_cons_iff [Hs1 ?] Hs2].
      move=> /ssimE [?] [?] [?] [[]] ??? [/Forall_cons_iff [Ht1 ?] Ht2]. subst.
      congr sarr.
      * apply: IH1; by eassumption.
      * apply: IH2; by eassumption.
Qed.

Fixpoint lift_sty (s : sty) : nity :=
  match s with
  | satom x => niatom x
  | sarr s t => niarr (cons (lift_sty s) nil) (lift_sty t)
  end.

Lemma ssim_lift_sty {t} : ssim t (lift_sty t).
Proof.
  elim: t.
  - constructor.
  - move=> s IHs t IHt /=. constructor.
    + by constructor.
    + done.
Qed.

Lemma Forall2_merge Gamma Gamma1 Gamma2 :
  Forall2 (fun s u => Forall (ssim s) u) Gamma Gamma1 ->
  Forall2 (fun s u => Forall (ssim s) u) Gamma Gamma2 ->
  Forall2 (fun s u => Forall (ssim s) u) Gamma (merge Gamma1 Gamma2).
Proof.
  move=> H. elim: H Gamma2.
  - move=> [|??].
    + constructor.
    + by move=> /Forall2E.
  - move=> s u1 {}Gamma {}Gamma1.
    move=> ?? IH [|u2 Gamma2].
    + by move=> /Forall2E.
    + move=> /Forall2E [??] /=.
      constructor.
      * apply /Forall_app.
        by constructor.
      * by apply: IH.
Qed.

Lemma sty_permutation_fold_right_merge Gamma Deltas : sty_permutation [fold_right merge Gamma Deltas] (Gamma :: Deltas).
Proof.
  elim: Deltas Gamma.
  - done.
  - move=> Delta Deltas IH Gamma x.
    rewrite /= !app_nil_r nth_merge.
    apply: (Permutation_app_middle _ []).
    have /= := IH Gamma x.
    by rewrite app_nil_r.
Qed.

(* a simply-typed normal form is typable in the uniform non-itempotent type system *)
Theorem stlc_nitlc_nf {Gamma M t} :
  nf M -> stlc Gamma M t ->
  exists Gamma' A', nitlc Gamma' M A' /\ Forall2 (fun s u => Forall (ssim s) u) Gamma Gamma' /\ ssim t A'.
Proof.
  move=> HM.
  move: M HM Gamma t.
  (* a neutral term can be assigned any suitable type *)
  apply: (nf_ind' _ (fun M _ => forall Gamma t, stlc Gamma M t -> forall A', ssim t A' -> exists Gamma', nitlc Gamma' M A' /\ Forall2 (fun s u => Forall (ssim s) u) Gamma Gamma')).
  - move=> s M HM IH Gamma t /stlcE [] s' t' /IH + ??. subst.
    move=> [Gamma'] [A'] [H'M] [/Forall2E].
    move: Gamma' H'M => [|u Gamma']; [done|].
    move: u => [|C u] H'M [Hu HGamma] Ht'.
    + exists Gamma', (niarr [lift_sty s'] A').
      do ? apply: conj.
      * constructor; [(do ? constructor); [by apply: ssim_lift_sty|done]|].
        by apply: (weakening [[lift_sty s']]) H'M.
      * done.
      * do ? constructor; [|done].
        by apply: ssim_lift_sty.
    + exists Gamma', (niarr (C :: u) A').
      constructor; [|constructor].
      * constructor; [by constructor|done].
      * done.
      * by constructor.
  - move=> M HM IH Gamma t /IH /(_ (lift_sty t) ssim_lift_sty).
    move=> [Gamma'] [? ?].
    exists Gamma', (lift_sty t).
    constructor; [|constructor].
    + done.
    + done.
    + apply: ssim_lift_sty.
  - move=> x Gamma t /stlcE Hx A' Ht.
    move: Hx => /nth_error_split [Gamma1] [Gamma2] [-> <-].
    exists ((repeat nil (length Gamma1)) ++ (cons A' nil) :: (repeat nil (length Gamma2))).
    constructor.
    + apply: (nitlc_var); [by eassumption|].
      rewrite app_nth2 repeat_length; [lia|].
      rewrite Nat.sub_diag. by left.
    + elim: Gamma1.
      * constructor; [by constructor|].
        elim: (Gamma2); by constructor.
      * move=> ??? /=.
        constructor; [by constructor|done].
  - move=> M N HM IHM HN IHN Gamma t /stlcE [].
    move=> s /IHM {}IHM + A'3.
    move=> /IHN [Gamma'2] [A'2] [H'N] [H2Gamma HA'2].
    move=> Ht.
    move: (IHM (niarr [A'2] A'3)) => [].
    { by do ? constructor. }
    move=> Gamma'1 [H'M] H1Gamma.
    exists (fold_right merge Gamma'1 [Gamma'2]).
    constructor.
    + apply: (nitlc_app _ Gamma'1 [Gamma'2]); [ |by eassumption|by constructor].
      by apply: sty_permutation_fold_right_merge.
    + by apply: Forall2_merge.
Qed.

Lemma sty_permutation_In_nth Gamma Delta Deltas x A :
  sty_permutation [Gamma] Deltas ->
  In A (nth x Delta []) ->
  In Delta Deltas ->
  In A (nth x Gamma []).
Proof.
  move=> /(_ x) /=. rewrite app_nil_r.
  move=> /Permutation_sym /Permutation_in H ??.
  apply: H. apply /in_concat.
  do ? econstructor; [|by eassumption].
  apply /in_map_iff.
  by do ? econstructor.
Qed.

Lemma sty_permutation_ssim_nth Gamma Deltas x t :
  sty_permutation [Gamma] Deltas ->
  Forall (ssim t) (nth x Gamma []) -> Forall (fun Delta => Forall (ssim t) (nth x Delta [])) Deltas.
Proof.
  move=> /(_ x) /=. rewrite app_nil_r.
  by move=> /Permutation_Forall /[apply] /Forall_concat /Forall_map.
Qed.

Lemma Permutation_remove_elt {X : Type} {x : X} {Delta1 xs Delta2 Gamma xi} f:
  (forall x1 x2, xi x1 = xi x2 -> x1 = x2) ->
  (forall y, Permutation (nth y (Delta1 ++ (x :: xs) :: Delta2) [] ++ f y) (nth (xi y) Gamma [])) ->
  exists Gamma1 : list (list X),
    length Gamma1 = xi (length Delta1) /\
    (exists (ys1 ys2 : list X) (Gamma2 : list (list X)),
      Gamma = Gamma1 ++ (ys1 ++ x :: ys2) :: Gamma2 /\
      (forall y,
        Permutation
          (nth y (Delta1 ++ xs :: Delta2) [] ++ f y)
          (nth (xi y) (Gamma1 ++ (ys1 ++ ys2) :: Gamma2) []))).
Proof.
  move=> Hxi H.
  have : In x (nth (xi (length Delta1)) Gamma []).
  { have := H (length Delta1). rewrite nth_middle /=.
    move=> /(@Permutation_in _ _ _ x). apply. by left. }
  move=> /In_nth [Gamma1] [ys1] [ys2] [Gamma2] [?] HG1.
  subst Gamma. exists Gamma1. split; first done.
  exists ys1, ys2, Gamma2. split; first done.
  move=> y. have /= := H y.
  have [->|Hy] : (y = length Delta1) \/ (y <> length Delta1) by lia.
  - rewrite -HG1 !nth_middle. by apply: (@Permutation_app_inv _ nil).
  - congr Permutation.
    + congr List.app. by apply: nth_middle_neq.
    + apply: nth_middle_neq. move=> ?. apply: Hy. apply: Hxi. lia.
Qed.

Lemma Permutation_concat_split {X : Type} xi (Deltas : list (list (list X))) Gamma :
  (forall x1 x2, xi x1 = xi x2 -> x1 = x2) ->
  (forall x, Permutation (concat (map ((nth x)^~ []) Deltas)) (nth (xi x) Gamma [])) ->
  exists Delta' Deltas',
    (forall x, Permutation (nth x Gamma []) (concat (map ((nth x)^~ []) (Delta' :: Deltas')))) /\
    Forall2 (fun Delta Delta' => forall x, nth x Delta [] = nth (xi x) Delta' []) Deltas Deltas'.
Proof.
  move=> Hxi.
  elim /(Nat.measure_induction _ (fun Deltas => list_sum (map (fun Delta => 1 + list_sum (map (@length X) Delta)) Deltas))) : Deltas Gamma.
  move=> [|Delta Deltas].
  { move=> _ Gamma HG. exists Gamma, nil. split.
    + move=> x /=. by rewrite app_nil_r.
    + done. }
  move=> IH Gamma.
  have [|[Delta1 [x [xs [Delta2 Hx]]]]] : (forall x, nth x Delta [] = []) \/
    exists Delta1 x xs Delta2, Delta = Delta1 ++ (x :: xs) :: Delta2.
  { elim: (Delta).
    - left. by case.
    - move=> [|??] ? [?|].
      + by left=> - [|?] /=.
      + move=> [?] [?] [?] [?] ->.
        right. by eexists (nil :: _), _, _, _.
      + right. by eexists nil, _, _, _.
      + move=> [?] [?] [?] [?] ->.
        right. by eexists ((_ :: _) :: _), _, _, _. }
  - move=> HD /= HDDs.
    have := IH Deltas _ Gamma. case.
    + move=> /=. lia.
    + move=> x. apply: Permutation_trans; [|by apply: HDDs x].
      by rewrite HD.
    + move=> Delta' [Deltas'] [IH1 IH2].
      exists Delta', ([] :: Deltas'). split=> /=.
      * move=> [|x]; by apply: IH1.
      * constructor; [|done].
        move=> x. by move: (xi x) => [|?]; rewrite HD.
  - subst Delta. move=> /= Hx.
    have [Gamma1 [HD1 [ys1 [ys2 [Gamma2 [? HG]]]]]] := Permutation_remove_elt _ Hxi Hx.
    subst Gamma.
    have := IH ((Delta1 ++ xs :: Delta2) :: Deltas) _ (Gamma1 ++ (ys1 ++ ys2) :: Gamma2). case.
    + rewrite /= !map_app !list_sum_app /=. lia.
    + done.
    + move=> Delta'' [[|Delta' Deltas']] [IH1 /Forall2E]; [done|].
      move=> [IH2 ?].
      exists Delta'', ((insert x (xi (length Delta1)) Delta') :: Deltas'). split.
      * move=> y. have /= := IH1 y.
        have [->|Hy] : (y = length Gamma1) \/ (y <> length Gamma1) by lia.
        ** rewrite !nth_middle HD1 nth_insert. by apply: Permutation_elt.
        ** have : y <> xi (length Delta1) by lia.
           move=> /nth_insert_neq ->.
           apply: Permutation_trans.
           by rewrite (nth_middle_neq _ (ys1 ++ ys2)).
      * constructor; [|done].
        move=> y. have := IH2 y.
        have [->|Hy] : (y = length Delta1) \/ (y <> length Delta1) by lia.
        ** rewrite !nth_middle nth_insert. by move=> ->.
        ** have : xi y <> xi (length Delta1).
           { move=> ?. apply: Hy. by apply: Hxi. }
           move=> /nth_insert_neq -> <-.
           by apply: nth_middle_neq.
Qed.

Lemma nitlc_ren Gamma Delta xi A M :
  (forall x1 x2, xi x1 = xi x2 -> x1 = x2) ->
  (forall x, nth x Gamma nil = nth (xi x) Delta nil) ->
  nitlc Gamma M A ->
  nitlc Delta (ren xi M) A.
Proof.
  move=> Hxi H H'. elim /nitlc_ind': H' xi Delta H Hxi.
  - move=> > /= ? ? > H ?. econstructor; [|rewrite -H]; by eassumption.
  - move=> {}Gamma Deltas Gamma' t {}M N u ? ?? HG ? IHM ? IHN xi Gamma'' HMN Hxi.
    have : forall x, Permutation (concat (map ((nth x)^~ []) (Gamma' :: Deltas))) (nth (xi x) Gamma'' []).
    { move=> x. rewrite -HMN. apply /Permutation_sym.
      have := HG x.
      by rewrite /= app_nil_r. }
    move: (Hxi) => /Permutation_concat_split /[apply].
    move=> [G0] [[|Gamma''' Deltas']].
    { by move=> [?] /Forall2_length. }
    move=> [HG''] /= /Forall2E [HG' HD].
    apply: (nitlc_app _ (merge G0 Gamma''') Deltas' _ _ u).
    + move=> x /=.
      by rewrite app_nil_r nth_merge -app_assoc.
    + apply: weakening. by apply: IHM.
    + apply: Forall2_trans; [|by eassumption..].
      move=> > H' /= /H'. by apply.
  - move=> > ?? IH > /= HM Hxi. constructor; first done.
    apply: IH; [by case|].
    move=> [|x1] [|x2] /=; [done..|].
    by move=> [/Hxi <-].
Qed.

Lemma allfv_make_injective M (xi : nat -> nat) : allfv (fun x1 => allfv (fun x2 => xi x1 = xi x2 -> x1 = x2) M) M ->
  exists xi', allfv (fun x => xi x = xi' x) M /\ (forall x1 x2, xi' x1 = xi' x2 -> x1 = x2).
Proof.
  move=> H.
  have [l Hl] := allfv_list M.
  have H' : Forall (fun x1 => Forall (fun x2 => xi x1 = xi x2 -> x1 = x2) l) l.
  { apply /Hl. by apply: allfv_impl H => ? /Hl. }
  suff: exists xi' : nat -> nat,
    Forall (fun x => xi x = xi' x) l /\ (forall x1 x2 : nat, xi' x1 = xi' x2 -> x1 = x2).
  { move=> [xi'] [??]. exists xi'. by split; [apply /Hl|]. }
  clear H Hl.
  have D := In_dec Nat.eq_dec.
  pose k := S (list_sum (map xi l)).
  exists (fun i => if D i l then xi i else k + i). split.
  - apply /Forall_forall => i ?. by case: (D i l).
  - move=> x1 x2. move: (D x1 l) (D x2 l) => [Hx1|Hx1] [Hx2|Hx2] /=.
    + by move: H' Hx1 Hx2 => /Forall_forall /[apply] /Forall_forall /[apply].
    + move: Hx1 => /in_split [?] [?] ->.
      rewrite map_app /= list_sum_app /=. lia.
    + move: Hx2 => /in_split [?] [?] ->.
      rewrite map_app /= list_sum_app /=. lia.
    + lia.
Qed.

Lemma Permutation_allfv_split M (Delta : environment) Deltas Gamma' :
  allfv (fun x => Permutation (concat (map ((nth x)^~ []) (Delta :: Deltas))) (nth x Gamma' [])) M ->
  exists Delta' Deltas',
    (forall x, Permutation (nth x Gamma' []) (concat (map ((nth x)^~ []) (Delta' :: Deltas')))) /\
    (allfv (fun x => nth x Delta [] = nth x Delta' []) M) /\
    Forall2 (fun Delta Delta' => allfv (fun x => nth x Delta [] = nth x Delta' []) M) Deltas Deltas'.
Proof.
  have [l Hl] := allfv_list M.
  have D := In_dec Nat.eq_dec.
  move=> /Hl /Forall_forall HM.
  exists (map (fun i => nth i (if D i l then Delta else Gamma') []) (seq 0 (length Gamma'))).
  exists (map (fun Delta => map (fun i => nth i (if D i l then Delta else []) []) (seq 0 (length Delta))) Deltas).
  do ? split.
  - move=> i /=.
    have [|] : i < length Gamma' \/ i >= length Gamma' by lia.
    + move=> /nth_map_seq_lt ->.
      case: (D i l).
      * move=> Hi /=.
        have /Permutation_sym /Permutation_trans /= := HM _ Hi. apply.
        apply: Permutation_eq. congr List.app. congr concat.
        rewrite !map_map. apply: map_ext => Delta'.
        have [|] : i < length Delta' \/ i >= length Delta' by lia.
        ** move=> /nth_map_seq_lt ->. by case: (D i l).
        ** move=> /[dup] ? /nth_map_seq_ge ->.
           by rewrite (nth_overflow Delta').
      * move=> Hi /=. apply: Permutation_eq. apply: eq_trans.
        { apply: eq_sym. by apply: app_nil_r. }
        congr List.app. elim: (Deltas); first done.
        move=> Delta' Deltas' IH /=.
        rewrite -IH app_nil_r.
        have [|] : i < length Delta' \/ i >= length Delta' by lia.
        ** move=> /nth_map_seq_lt ->. by move: (i) (D i l) Hi => [|?] [|] /=.
        ** by move=> /nth_map_seq_ge ->.
    + move=> /[dup] ? /nth_map_seq_ge ->.
      rewrite (nth_overflow Gamma') /=; first done.
      apply: Permutation_eq. case: (D i l) => Hi.
      * have := HM _ Hi.
        rewrite (nth_overflow Gamma') /=; first done.
        move=> H.
        have : Forall (fun Delta' => nth i Delta' [] = []) Deltas.
        { apply /Forall_forall => Delta' HDelta'.
          move: HDelta' H => /in_split [?] [?] ->.
          rewrite map_app concat_app /=.
          case: (nth i Delta' []); first done.
          move=> s ? /=.
          move=> /(Permutation_in) => /(_ s) H. exfalso.
          apply: H. do 2 (apply /in_app_iff; right). by left. }
        elim; first done.
        move=> Delta' Deltas' IH ? /= <-.
        rewrite app_nil_r.
        have [|] : i < length Delta' \/ i >= length Delta' by lia.
        ** move=> /nth_map_seq_lt ->. case: (D i l); last done.
           by rewrite /= IH.
        ** by move=> /nth_map_seq_ge ->.
      * elim: (Deltas); first done.
        move=> Delta' Deltas' /= <-. rewrite app_nil_r.
        have [|] : i < length Delta' \/ i >= length Delta' by lia.
        ** move=> /nth_map_seq_lt ->. by move: (i) (D i l) Hi => [|?] [|] /=.
        ** by move=> /nth_map_seq_ge ->.
  - apply /Hl. apply /Forall_forall => i Hi.
    have [|] : i < length Gamma' \/ i >= length Gamma' by lia.
    + move=> /nth_map_seq_lt ->. by case: (D i l).
    + move=> /[dup] ? /nth_map_seq_ge ->.
      have := HM _ Hi. rewrite (nth_overflow Gamma') /=; first done.
      case: (nth i Delta []); first done.
      by move=> > /Permutation_sym /Permutation_nil_cons.
  - apply: Forall2_map_r. elim: (Deltas); first done.
    move=> Delta' Deltas' IH. constructor; last done.
    apply /Hl. apply /Forall_forall => i Hi.
    have [|] : i < length Delta' \/ i >= length Delta' by lia.
    + move=> /nth_map_seq_lt ->. by case: (D i l).
    + move=> /[dup] ? /nth_map_seq_ge ->.
      by rewrite (nth_overflow Delta').
Qed.

Lemma nitlc_allfv Gamma Delta A M :
  allfv (fun x => nth x Gamma nil = nth x Delta nil) M ->
  nitlc Gamma M A ->
  nitlc Delta M A.
Proof.
  move=> H H'. elim /nitlc_ind': H' Delta H.
  - move=> > /= ? ? > H. econstructor; [|rewrite -H]; by eassumption.
  - move=> {}Gamma Deltas Gamma' t {}M N u ? ?? HG ? IHM ? IHN Gamma'' HMN.
    have : allfv (fun x => Permutation (concat (map ((nth x)^~ []) (Gamma' :: Deltas))) (nth x Gamma'' [])) (app M N).
    { apply: allfv_impl HMN => x H.
      have /Permutation_sym := HG x.
      by rewrite /= H app_nil_r. }
    move=> /Permutation_allfv_split.
    move=> [Gamma'''] [Deltas'].
    move=> [HG''] /= [[HM HN]] ?.
    apply: (nitlc_app _ Gamma''' Deltas' _ _ u).
    + move=> x /=.
      by rewrite app_nil_r.
    + apply: IHM. by apply: allfv_impl HM.
    + apply: Forall2_trans; [|by eassumption..].
      by move=> > H' /= [_ /H'].
  - move=> > ?? IH > /= HM. constructor; first done.
    apply: IH. apply: allfv_impl HM. by case.
Qed.

Lemma nitlc_allfv_ren xi Gamma Delta A M :
  allfv (fun x1 => allfv (fun x2 => xi x1 = xi x2 -> x1 = x2) M) M ->
  allfv (fun x => nth x Gamma nil = nth (xi x) Delta nil) M ->
  nitlc Gamma M A ->
  nitlc Delta (ren xi M) A.
Proof.
  move=> /allfv_make_injective [xi'] [H1xi' H2xi'] H.
  have -> : ren xi M = ren xi' M by apply: ext_allfv_ren.
  have {}H : allfv (fun x => nth x Gamma [] = nth (xi' x) Delta []) M.
  { apply: allfv_allfv_impl H. apply: allfv_impl H1xi'.
    by move=> ? ->. }
  clear xi H1xi'.
  have : exists Gamma' Delta',
    allfv (fun x => nth x Gamma nil = nth x Gamma' nil) M /\
    allfv (fun x => nth x Delta' nil = nth x Delta nil) (ren xi' M) /\
    (forall x, nth x Gamma' nil = nth (xi' x) Delta' nil).
  { have [l Hl] := allfv_list M.
    suff: exists (Gamma' Delta' : environment),
      Forall (fun x => 
        (nth x Gamma [] = nth x Gamma' []) /\
        (nth (xi' x) Delta' [] = nth (xi' x) Delta [])) l /\
      (forall x , nth x Gamma' [] = nth (xi' x) Delta' []).
    { move=> [Gamma'] [Delta'] [/Hl HM] ?.
      exists Gamma', Delta'. do ? split.
      - apply: allfv_impl HM. tauto.
      - apply: allfv_ren. apply: allfv_impl HM. tauto.
      - done. }
    move: H => /Hl. clear -H2xi'.
    elim: l Gamma Delta.
    - move=> *. exists nil, nil. split; first done.
      move=> x. by move: x (xi' x) => [|?] [|?].
    - move=> i l IH Gamma Delta.
      move=> /Forall_cons_iff [?] /IH.
      move=> [Gamma'] [Delta'] [H'l ?].
      exists (replace (nth i Gamma []) i Gamma').
      exists (replace (nth (xi' i) Delta []) (xi' i) Delta'). do ? split.
      + constructor.
        * by rewrite !nth_replace.
        * apply: Forall_impl H'l => j [?] ?. split.
          ** case: (Nat.eq_dec j i) => /=.
             *** move=> <-. by rewrite nth_replace.
             *** by move=> /nth_replace_neq ->.
          ** case: (Nat.eq_dec (xi' j) (xi' i)) => /=.
             *** move=> <-. by rewrite nth_replace.
             *** by move=> /nth_replace_neq ->.
      + move=> j. case: (Nat.eq_dec j i) => /=.
        * move=> ->. by rewrite !nth_replace.
        * move=> /[dup] Hji /nth_replace_neq ->.
          have : xi' j <>  xi' i.
          { move=> ?. apply: Hji. by apply: H2xi'. }
          by move=> /nth_replace_neq ->. }
  move=> [Gamma'] [Delta'] [HG'] [HD'] ?.
  move: HG' => /nitlc_allfv /[apply].
  move: (H2xi') => /nitlc_ren /[apply] H'.
  move: HD' => /nitlc_allfv. apply.
  by apply: H'.
Qed.
