(*
  normalization property of simply typed terms:
  if M is simply typed, then M (I, gamma)-reduces to some term, which K-reduces to a normal form
*)

Require Import Lia List Relations PeanoNat Permutation Sorting.Heap Wellfounded.
Import ListNotations.

From NonIdempotent Require Import facts stlc stlc_facts.
Require Import ssreflect ssrbool.

#[local] Arguments Permutation_in {A l l' x}.

Lemma has_var_zero_dec M : {has_var_zero M} + {not (has_var_zero M)}.
Proof.
  have /(allfv_dec _ M) [?|?] : forall x, {is_nonzero x} + {not (is_nonzero x)}.
  { case; tauto. }
  - right=> H. by apply: H.
  - by left.
Qed.

Definition inc_depth : nat * nat -> nat * nat :=
  fun '(n, m) => (n, S m).

(* list of sizes of I, G redexes together with depth wrt. abstraction *)
Fixpoint measure (M : tm) : list (nat * nat) :=
  match M with
  | var _ => []
  | lam _ M => map inc_depth (measure M)
  | app M1 M2 =>
    match M1 with
    | var _ => []
    | app _ _ => []
    | lam t M1' =>
      if has_var_zero_dec M1' then [(size_sty t, 0)] (* top-level I-redex *)
      else
        match M1' with
        | var _ => []
        | app _ _ => []
        | lam t' _ => [(1 + size_sty t', 0)] (* top-level G-redex *)
        end
    end ++ measure M1 ++ measure M2
  end.

Arguments measure : simpl never.

Lemma measure_app_lam M N t : has_var_zero M -> measure (app (lam t M) N) = [(size_sty t, 0)] ++ map inc_depth (measure M) ++ measure N.
Proof.
  rewrite /measure -/measure /=.
  by case: (has_var_zero_dec M)=> /=.
Qed.

Lemma measure_app_lam' M N t : not (has_var_zero M) -> measure (app (lam t M) N) =
  match M with
  | var _ => []
  | app _ _ => []
  | lam t3 _ => [(1 + size_sty t3, 0)] (* G-redex *)
  end ++ map inc_depth (measure M) ++ measure N.
Proof.
  rewrite /measure -/measure /=.
  by case: (has_var_zero_dec M).
Qed.

Lemma measure_var x : measure (var x) = [].
Proof. done. Qed.

Lemma measure_lam t M : measure (lam t M) = map inc_depth (measure M).
Proof. done. Qed.

Lemma measure_app_var x M : measure (app (var x) M) = measure M.
Proof. done. Qed.

Lemma measure_app_app M1 M2 M3 : measure (app (app M1 M2) M3) = measure (app M1 M2) ++ measure M3.
Proof. done. Qed.

Lemma measure_ren xi M : measure (ren xi M) = measure M.
Proof.
  elim: M xi.
  - move=> x xi /=. by rewrite !measure_var.
  - move=> [x|M1 M2|t' M] IH1 N IH2 xi /=.
    + rewrite !measure_app_var. by apply: IH2.
    + rewrite !measure_app_app IH2.
      congr List.app. by apply: IH1.
    + case: (has_var_zero_dec M).
      * move=> /[dup] H1M /measure_app_lam ->.
        have /measure_app_lam -> : has_var_zero (ren (scons 0 (fun x : nat => S (xi x))) M).
        { move=> /allfv_ren' H. apply: H1M.
          by apply: allfv_impl H=> - [|x]. }
        congr cons. rewrite IH2.
        congr List.app. by apply: IH1.
      * move=> /[dup] H1M /measure_app_lam' ->.
        have /measure_app_lam' -> : not (has_var_zero (ren (scons 0 (fun x : nat => S (xi x))) M)).
        { move=> H. apply: H1M=> H'. apply: H. apply: allfv_ren.
          by apply: allfv_impl H'=> - [|x]. }
        rewrite IH2.
        have /= := IH1 xi. rewrite !measure_lam=> ->.
        by move: (M) => [[|?]|??|??] /=.
  - move=> > IH xi /=. rewrite !measure_lam.
    congr map. by apply: IH.
Qed.

Lemma measure_app_stlc Gamma M N t :
  stlc Gamma M t ->
  exists ns,
    Permutation (measure (app M N)) (ns ++ measure M ++ measure N) /\
    Forall (fun '(n, m) => n <= size_sty t) ns.
Proof.
  move=> H. rewrite /measure -/measure. eexists. split.
  { rewrite !app_assoc. by do 2 apply: Permutation_app_tail. }
  case: H; [done..|].
  move=> {}M s'' t''. case: (has_var_zero_dec M); first by constructor.
  case: M=> /=; [done..|].
  move=> > ? /stlcE [>] *. subst.
  constructor; last done.
  case: (s'')=> /=; lia.
Qed.

Lemma measure_app_ren xi M1 M2 : measure (app (ren xi M1) M2) = measure (app M1 M2).
Proof.
  rewrite /measure -/measure. rewrite !measure_ren. congr List.app.
  case: M1=> /=; [done..|].
  move=> ? M. case: (has_var_zero_dec M).
  + move=> H.
    have : has_var_zero (ren (scons 0 (fun x : nat => S (xi x))) M).
    { move=> /allfv_ren' H'. apply: H.
      apply: allfv_impl H'. by case. }
    by case: (has_var_zero_dec _).
  + move=> H.
    have : not (has_var_zero (ren (scons 0 (fun x : nat => S (xi x))) M)).
    { move=> H'. apply: H=> H.
      apply: H'. apply: allfv_ren.
      apply: allfv_impl H. by case. }
    case: (has_var_zero_dec _); first done.
    move=> /=. by case: (M).
Qed.

(* measure decreases on innermost I-redex contraction *)
Lemma measure_decrease_stepIRed Gamma M N s t :
  stlc (s :: Gamma) M t ->
  stlc Gamma N s ->
  has_var_zero M -> measure N = [] ->
  exists ns,
    Permutation (measure (subst (scons N var) M))
      (ns ++ measure M ++ measure N) /\
    Forall (fun '(n, m) => n < size_sty (sarr s t)) ns.
Proof.
  move=> H2M H2N H1M H1N. rewrite H1N app_nil_r.
  have HNM : stlc Gamma (subst (scons N var) M) t.
  { apply: stlc_subst; first by eassumption.
    by move=> [|x] ? /=; [congruence|apply: stlc_var]. }
  have :
    match N with
    | var _ => True
    | app _ _ => True
    | lam t' _ => t' = s
    end.
  { case: (N) H2N; [done..|].
    by move=> > /stlcE []. }
  move: H1M H1N H2N. clear.
  have Hst : S (size_sty s) < size_sty s + S (size_sty t) by case: (t); cbn; lia.
  move=> _ H2N H1N H3N.
  rewrite -(ren_id N). move: (id).
  elim /(Nat.measure_induction _ size_tm): M. case.
  - move=> [|x] _ /= xi; rewrite !measure_var.
    + rewrite measure_ren H2N. exists nil. by constructor.
    + exists nil. by constructor.
  - move=> M M3 IH.
    have /IH {}IH1 : size_tm M < size_tm (app M M3) by cbn; lia.
    have /IH {}IH2 : size_tm M3 < size_tm (app M M3) by cbn; lia.
    move: M {IH} IH1=> [[|x]|M1 M2|t'' M] IH1 xi /=.
    + rewrite measure_app_var measure_app_ren.
      move: H1N=> /measure_app_stlc=> /(_ (subst (scons (ren xi N) var) M3)).
      move=> [n's] [+ H2n's].
      move: (IH2 xi)=> /= [ns] [].
      move: (subst _ _)=> M'3. move: (app N M'3)=> N'. rewrite H2N /=.
      move=> *. exists (n's ++ ns). split.
      * apply: Permutation_trans; first by eassumption.
        rewrite -app_assoc. by apply: Permutation_app_head.
      * apply /Forall_app. split; last done.
        apply: Forall_impl H2n's=> - [??]. lia.
    + rewrite !measure_app_var. apply: IH2.
    + rewrite !measure_app_app.
      move: (IH1 xi) (IH2 xi)=> /= [n1s] [H1n1s H2n1s] [n2s] [H1n2s H2n2s].
      exists (n1s ++ n2s). split.
      * apply: Permutation_trans. { apply: Permutation_app; by eassumption. }
        move: (measure (app _ _))=> ?.
        rewrite !app_assoc. apply Permutation_app_tail.
        rewrite -!app_assoc. apply Permutation_app_head.
        by apply: Permutation_app_comm.
      * apply /Forall_app. by split.
    + case: (has_var_zero_dec M).
      { move=> H.
        have : has_var_zero (subst (scons (var 0) (fun x => ren S (scons (ren xi N) var x))) M).
        { move=> /allfv_subst' H'. apply: H.
          apply: allfv_impl H'. by case. }
        move: H => /measure_app_lam -> /measure_app_lam ->.
        move: (IH2 xi) (IH1 xi)=> /=. rewrite !measure_lam.
        move=> [n1s] [+ H2n1s] [n2s] [+ H2n2s].
        move: (measure (subst _ _)) (measure (subst _ _))=> ????.
        exists (n2s ++ n1s). split.
        - apply: (Permutation_app_middle [(size_sty t'', 0)] nil _ (n2s ++ n1s) _).
          move=> /=. apply: Permutation_trans. { apply: Permutation_app; by eassumption. }
          rewrite -!app_assoc. apply: Permutation_app_head.
          rewrite !app_assoc. apply: Permutation_app_tail. by apply: Permutation_app_comm.
        - apply /Forall_app. by split. }
      move=> H. 
      have : not (has_var_zero (subst (scons (var 0) (fun x => ren S (scons (ren xi N) var x))) M)).
      { move=> H'. apply: H=> H. apply: H'. apply: allfv_subst.
        apply: allfv_impl H. case; first done.
        move=> ??. apply: allfv_ren. by apply: allfv_trivial. }
      move: H => /measure_app_lam' -> /measure_app_lam' ->.
      move: (IH2 xi) {IH1} (IH1 xi) => [n2s] [+ H2n2s] [n1s] [+ H2n1s].
      rewrite /= !measure_lam.
      { move: M => [[|[|x]]|??|??] /=.
        - move=> *. by exists n2s.
        - move=> *.
          exists (match ren S (ren xi N) with lam t3 _ => [(1 + size_sty t3, 0)] | _ => [] end ++ n1s ++ n2s).
          split.
          + apply: Permutation_trans.
            { apply: Permutation_app; [by apply: Permutation_refl|].
              apply: Permutation_app; by eassumption. }
            rewrite !app_assoc app_nil_r. by apply: Permutation_app_tail.
          + apply /Forall_app. split; [|by apply /Forall_app].
            case: H1N; [done..|].
            move=> > /= ?. by constructor; [lia|].
        - move=> *. by exists n2s.
        - move: (measure (app _ _)) (measure (app _ _))=> *.
          exists (n1s ++ n2s). split.
          + apply: Permutation_trans. { apply: Permutation_app; by eassumption. }
            rewrite -!app_assoc. apply: Permutation_app_head.
            rewrite !app_assoc. apply: Permutation_app_tail. by apply: Permutation_app_comm.
          + apply /Forall_app. by split.
        - rewrite !measure_lam. move: (measure (subst _ _)) (measure (subst _ _))=> *.
          exists (n1s ++ n2s). split.
          + apply: (Permutation_app_middle [_] nil _ (n1s ++ n2s) _).
            move=> /=. apply: Permutation_trans. { apply: Permutation_app; by eassumption. }
            rewrite -!app_assoc. apply: Permutation_app_head.
            rewrite !app_assoc. apply: Permutation_app_tail. by apply: Permutation_app_comm.
          + apply /Forall_app. by split. }
  - move=> t' M IH xi /=.
    have -> : subst (scons (var 0) (fun x : nat => ren S (scons (ren xi N) var x))) M = 
      subst (scons (ren S (ren xi N)) var) (ren swap M).
    { rewrite subst_ren. by apply: subst_ext=> - [|[|x]] /=. }
    have : size_tm (ren swap M) < size_tm (lam t M).
    { by rewrite size_tm_ren /=. }
    move=> /IH /(_ ((funcomp S xi))).
    rewrite !measure_lam measure_ren ren_ren.
    move=> [ns] [? Hns]. exists (map inc_depth ns). split.
    + rewrite -map_app. by apply: Permutation_map.
    + apply /Forall_map. apply: Forall_impl Hns. by case.
Qed.

(* rightmost lambda-I reduction *)
Inductive inner_stepI : (nat*nat) -> tm -> tm -> Prop :=
  | inner_stepIRed s t M N     : has_var_zero M -> measure N = [] ->
      inner_stepI (size_sty (sarr s t), 0) (app (lam (sarr s t) M) N) (subst (scons N var) M)
  | inner_stepILam t M M' n m    : inner_stepI (n, m) M M' -> inner_stepI (n, S m) (lam t M) (lam t M')
  | inner_stepIAppL M M' N nm : inner_stepI nm M M' -> inner_stepI nm (app M N) (app M' N)
  | inner_stepIAppR M N N' nm : inner_stepI nm N N' -> inner_stepI nm (app M N) (app M N').

Lemma inner_stepI_stepI n M N : inner_stepI n M N -> stepI M N.
Proof.
  by elim; auto using stepI.
Qed.

Lemma Forall2_le_refl (l : list (nat*nat)) : Forall2 (fun '(n1, m1) '(n2, m2) => n1 = n2 /\ m2 <= m1) l l.
Proof.
  elim: l; first done.
  move=> [??] ??. by constructor; [lia|].
Qed.

#[local] Hint Resolve Forall2_le_refl : core.

(* measure decreases on rightmost I-redex contraction *)
Lemma measure_decrease_inner_stepI Gamma n M1 M2 t :
  inner_stepI n M1 M2 ->
  stlc Gamma M1 t ->
  exists n1s, Permutation ([n] ++ n1s) (measure M1) /\
    exists n2s, Forall2 (fun '(n1, m1) '(n2, m2) => n1 = n2 /\ m2 <= m1) n1s n2s /\
      exists ns, Permutation (ns ++ n2s) (measure M2) /\ Forall (fun '(n', m') => n' < fst n \/ n' = fst n /\ m' < snd n) ns.
Proof.
  move=> H. elim: H Gamma t.
  - move=> s t {}M1 {}M2 H1M1 H2M1 Gamma t'.
    move=> /stlcE [] s' /stlcE [] s'' t'' H3M1 [??] [??] H3M2. subst.
    move: (H1M1)=> /measure_app_lam ->.
    move: H1M1 H2M1 H3M1 H3M2=> /measure_decrease_stepIRed /[apply] /[apply] /[apply].
    move=> [ns] [? Hns]. exists ((map inc_depth (measure M1)) ++ (measure M2)). split; first done.
    exists (measure M1 ++ measure M2). split.
    { apply: Forall2_app; last done.
      apply: Forall2_map_l. apply: Forall2_eq.
      apply /Forall_forall=> - [??] /=. lia. }
    exists ns. split; first by apply: Permutation_sym.
    apply: Forall_impl Hns => - [??] /=. lia.
  - move=> > ? IH > /stlcE [] ??.
    move=> /IH [n1s] [Hn1s] [n2s] [Hn1sn2s] [ns] [Hn2s Hns] ??. subst.
    rewrite !measure_lam.
    exists (map inc_depth n1s). split.
    { rewrite -/(map inc_depth [(_, _)]) -!map_app. by apply: Permutation_map. }
    exists (map inc_depth n2s). split.
    { apply: Forall2_map_l. apply: Forall2_map_r.
      apply: Forall2_impl Hn1sn2s=> - [??] [??] /=. lia. }
    exists (map inc_depth ns). split.
    { rewrite -!map_app. by apply: Permutation_map. }
    apply /Forall_map. apply: Forall_impl Hns=> - [??] /=. lia.
  - move=> {}M1 {}M2 M3 {}n Hn IH Gamma t.
    move=> /stlcE [] s' /[dup] H1M1.
    move=> /IH [n1s] [Hn1s] [n2s] [Hn1sn2s] [ns] [Hn2s Hns] ?.
    move: Hn Hn1s Hn2s H1M1 Hns Hn1sn2s. case; clear.
    + move=> s'' t'' M1 M2 H1M1 H1M2.
      rewrite !measure_app_app.
      move: (H1M1)=> /measure_app_lam ->.
      rewrite H1M2 !app_nil_r.
      move=> Hn1s Hn2s /stlcE [] s''' /stlcE [] s'''' t'''' H3M1 [??] [??] H3M2. subst.
      move=> ??. exists (n1s ++ measure M3). split.
      { rewrite !app_assoc. by apply: Permutation_app_tail. }
      exists (n2s ++ measure M3). split; first by apply: Forall2_app.
      move: M1 H1M1 H3M1 Hn1s Hn2s.
      { move=> [[|x]|t'' M'1 M'2|t'' M'1] /=.
        - move=> _ /stlcE [] /= ? Hn1s Hn2s. subst.
          move: H3M2=> /measure_app_stlc => /(_ M3) [n's].
          move: (measure (app _ _))=> ? [H1n's H2n's].
          exists (n's ++ ns). split.
          { apply: Permutation_trans; last by (apply: Permutation_sym; eassumption).
            rewrite !app_assoc. apply: Permutation_app_tail.
            rewrite -!app_assoc. by apply: Permutation_app. }
          apply /Forall_app. split; last done.
          apply: Forall_impl H2n's=> - [??] /=. lia.
        - done.
        - move=> ?. rewrite !measure_app_app.
          move: (measure (app _ _)) (measure (app _ _))=> *.
          exists ns. split; last done.
          rewrite !app_assoc. by apply: Permutation_app_tail.
        - move=> H1M'1 H2M'1. rewrite !measure_lam.
          have ? : t'' = sarr s' t.
          { by move: H2M'1 => /stlcE []. }
          subst t''.
          have : stlc Gamma (lam (sarr s' t) (subst (scons (var 0) (fun x : nat => ren S (scons M2 var x))) M'1)) (sarr s' t).
          { rewrite -/(subst _ (lam _ _)).
            apply: stlc_subst; first by eassumption.
            move=> [|?] ? /=; first by congruence.
            by move=> /stlc_var. }
          move=> /measure_app_stlc=> /(_ M3) [n's] [+ H2n's].
          rewrite !measure_lam. move: (measure (app _ _)) (measure (subst _ _))=> *.
          exists (n's ++ ns). split.
          { apply: Permutation_trans; last by (apply: Permutation_sym; eassumption).
            rewrite !app_assoc. apply: Permutation_app_tail.
            rewrite -!app_assoc. by apply: Permutation_app. }
          apply /Forall_app. split; last done.
          apply: Forall_impl H2n's=> - [??] /=. lia. }
    + move=> t' M1 M2 n m HM1M2. rewrite !measure_lam.
      case: (has_var_zero_dec M1).
      * move=> H3M1. have : has_var_zero M2.
        { move=> H3M2. apply: H3M1.
          apply: allfv_stepI'; [apply: inner_stepI_stepI|]; by eassumption. }
        move=> /measure_app_lam ->. move: H3M1=> /measure_app_lam ->.
        move=> Hn1s Hn2s /stlcE [>] ? [??] ? Hns Hn1sn2s. subst.
        eexists (n1s ++ _ ++ measure M3). split.
        { rewrite !app_assoc. apply: Permutation_app_tail.
          apply: Permutation_trans; last by apply: Permutation_app_comm.
          by apply: Permutation_app. }
        eexists (n2s ++ _ ++ measure M3). split; first by apply: Forall2_app.
        exists ns. split; last done.
        { rewrite !app_assoc. apply: Permutation_app_tail.
          apply: Permutation_trans; last by apply: Permutation_app_comm.
          by apply: Permutation_app. }
      * move=> H3M1. have : not (has_var_zero M2).
        { move=> H3M2. apply: H3M1=> H3M1. apply: H3M2.
          apply: allfv_stepI; [apply: inner_stepI_stepI|]; by eassumption. }
        move=> /measure_app_lam' ->. move: H3M1=> /measure_app_lam' ->.
        { move E: (n, m) HM1M2=> nm H. case: H E.
          - move=> s'' t'' M'1 N /[dup] /measure_app_lam -> ++ [??]. subst.
            move: M'1=> [[|x]|M'1 M'2|? M'1] /=.
            + move=> _ HN Hn1s Hn2s.
              move=> /stlcE [] ?? + [??] ?. subst.
              move=> /stlcE [] ? ++.
              move=> /stlcE [] ?? + [??] [??]. subst.
              move=> /stlcE [?]. subst.
              move: Hn1s Hn2s. rewrite HN=> H. clear HN.
              move=> ? HN *.
              exists (measure M3). split; first done.
              exists (measure M3). split; first done.
              move: N HN => [?|??|? N]; [by exists nil..|].
              move=> /stlcE [>] *. subst.
              eexists [_]. split; first done.
              constructor; last done.
              move=> /=. lia.
            + done.
            + move=> _ ?? H ???.
              exists (n1s ++ measure M3). split.
              { rewrite !cons_app !app_assoc. by apply: Permutation_app. }
              exists (n2s ++ measure M3). split; first by apply: Forall2_app.
              exists ns. split; last done.
              rewrite !app_assoc. by apply: Permutation_app.
            + rewrite !measure_lam. move: (measure (subst _ _))=> ???? H.
              move=> /stlcE [] ?? + [??] ?. subst.
              move=> /stlcE [] ? ++.
              move=> /stlcE [] ?? + [??] [??]. subst.
              move=> /stlcE [] ?? + ??. subst=> ????.
              exists (n1s ++ measure M3). split.
              { rewrite !cons_app !app_assoc. by apply: Permutation_app_tail. }
              exists (n2s ++ measure M3). split; first by apply: Forall2_app.
              eexists ([_] ++ ns). split.
              { rewrite !cons_app !app_assoc. apply: Permutation_app_tail.
                rewrite -!app_assoc. by apply: Permutation_app. }
              apply /Forall_app. split; last done.
              constructor; last done.
              move: (s'')=> [?|??] /=; lia.
          - move=> >. rewrite !measure_lam=> ? [??]. subst.
            move=> Hn1s Hn2s ? Hns ?.
            eexists (n1s ++ [_] ++ measure M3). split.
            { rewrite !app_assoc. apply: Permutation_app_tail.
              apply: Permutation_trans; last by apply: Permutation_app_comm.
              by apply: Permutation_app. }
            eexists (n2s ++ [_] ++ measure M3). split; first by apply: Forall2_app.
            exists ns. split; last done.
            rewrite !app_assoc. apply: Permutation_app_tail.
            apply: Permutation_trans; last by apply: Permutation_app_comm.
            by apply: Permutation_app.
          - move=> > ?? Hn1s Hn2s ? Hns ?. subst.
            exists (n1s ++ measure M3). split.
            { rewrite !app_assoc. by apply: Permutation_app. }
            exists (n2s ++ measure M3). split; first by apply: Forall2_app.
            exists ns. split; last done.
            rewrite !app_assoc. by apply: Permutation_app.
          - move=> > ?? Hn1s Hn2s ? Hns ?. subst.
            exists (n1s ++ measure M3). split.
            { rewrite !app_assoc. by apply: Permutation_app. }
            exists (n2s ++ measure M3). split; first by apply: Forall2_app.
            exists ns. split; last done.
            rewrite !app_assoc. by apply: Permutation_app. }
    + move=> M1 M2 N n ? Hn1s Hn2s ? Hns Hn1sn2s.
      rewrite !measure_app_app.
      exists (n1s ++ measure M3). split.
      { rewrite !app_assoc. by apply: Permutation_app. }
      exists (n2s ++ measure M3). split; first by apply: Forall2_app.
      exists ns. split; last done.
      rewrite !app_assoc. by apply: Permutation_app.
    + move=> > ? Hn1s Hn2s ? Hns Hn1sn2s. rewrite !measure_app_app.
      exists (n1s ++ measure M3). split.
      { rewrite !app_assoc. by apply: Permutation_app. }
      exists (n2s ++ measure M3). split; first by apply: Forall2_app.
      exists ns. split; last done.
      rewrite !app_assoc. by apply: Permutation_app.
  - move=> > ? IH > /stlcE [>] ?.
    move=> /IH [n1s] [Hn1s] [n2s] [Hn1sn2s] [ns] [Hn2s Hns].
    rewrite /measure -/measure. eexists (n1s ++ _). split.
    { rewrite !app_assoc. apply: Permutation_trans; first by apply: Permutation_app_comm.
      by apply: Permutation_app. }
    eexists (n2s ++ _ ++ measure _). split; first by apply: Forall2_app.
    eexists ns. split; last done.
    rewrite !app_assoc.
    apply: Permutation_trans; last by apply: Permutation_app_comm.
    rewrite !app_assoc. apply: Permutation_app; last done.
    by apply: Permutation_app.
Qed.

(* rightmost lambda-G reduction *)
Inductive inner_stepG : (nat*nat) -> tm -> tm -> Prop :=
  | inner_stepGRed s1 s2 t M N : not (has_var_zero (lam (sarr s2 t) M)) ->
    measure N = [] ->
    inner_stepG (1 + size_sty (sarr s2 t), 0)
      (app (lam (sarr s1 (sarr s2 t)) (lam (sarr s2 t) M)) N)
      (lam (sarr s2 t) (app (lam (sarr s1 t) (ren swap M)) (ren S N)))
  | inner_stepGLam t M M' n m     : inner_stepG (n, m) M M' -> inner_stepG (n, S m) (lam t M) (lam t M')
  | inner_stepGAppL M M' N nm  : inner_stepG nm M M' -> inner_stepG nm (app M N) (app M' N)
  | inner_stepGAppR M N N' nm  : inner_stepG nm N N' -> inner_stepG nm (app M N) (app M N').

Lemma inner_stepG_stepG n M N : inner_stepG n M N -> stepG M N.
Proof.
  by elim; auto using stepG.
Qed.

(* measure decreases on rightmost G-redex contraction *)
Lemma measure_decrease_inner_stepG Gamma n M1 M2 t :
  inner_stepG n M1 M2 ->
  stlc Gamma M1 t ->
  exists n1s, Permutation ([n] ++ n1s) (measure M1) /\
    exists n2s, Forall2 (fun '(n1, m1) '(n2, m2) => n1 = n2 /\ m2 <= m1) n1s n2s /\
      exists ns, Permutation (ns ++ n2s) (measure M2) /\ Forall (fun '(n', m') => n' < fst n \/ n' = fst n /\ m' < snd n) ns.
Proof.
  move=> H. elim: H Gamma t.
  - move=> s1 s2 t {}M1 {}M2 H1M1 H1M2 Gamma t'.
    move=> /stlcE [>] /stlcE [>] /stlcE [>] H2M1 ?. subst.
    move=> [??]. subst=> - [??]. subst=> - [?] H2M2. subst.
    rewrite measure_lam.
    have /measure_app_lam' -> : not (has_var_zero (ren swap M1)).
    { move=> H. apply: H1M1=> /= H1M1. apply: H.
      apply: allfv_ren. by apply: allfv_impl H1M1=> - [|[|?]] /=. }
    move: H1M1 => /measure_app_lam' ->. rewrite measure_lam !measure_ren H1M2 !app_nil_r.
    eexists. split; first done.
    rewrite map_app.
    eexists. split; first done.
    eexists. split; first done.
    apply /Forall_map.
    move: M1 H2M1=> [?|???|??] /=; [done..|].
    move=> /stlcE [>] ???. subst.
    constructor; last done.
    move=> /=. lia.
  - move=> > ? IH > /stlcE [] ?? + ?.
    move=> /IH [n1s] [Hn1s] [n2s] [Hn1sn2s] [ns] [Hn2s Hns].
    rewrite !measure_lam. exists (map inc_depth n1s). split.
    { rewrite -/(map inc_depth [(_, _)]) -map_app. by apply /Permutation_map. }
    exists (map inc_depth n2s). split.
    { apply: Forall2_map_l. apply: Forall2_map_r.
      apply: Forall2_impl Hn1sn2s=> - [??] [??] /=. lia. }
    exists (map inc_depth ns). split.
    { rewrite -map_app. by apply /Permutation_map. }
    apply /Forall_map. apply: Forall_impl Hns=> - [??] /=. lia.
  - move=> {}M1 {}M2 M3 {}n Hn IH Gamma t.
    move=> /stlcE [>] + ?.
    move=> /IH [n1s] [Hn1s] [n2s] [Hn1sn2s] [ns] [Hn2s Hns].
    case: Hn {IH} Hn1s Hn2s Hns.
    + move=> s1 s2 t' M'1 M'2 HM'1 HM'2.
      move: (HM'1) => /measure_app_lam' ->.
      rewrite !measure_app_app !measure_lam.
      have H'M'1 : ~ has_var_zero (ren swap M'1).
      { move=> H'M'1. apply: HM'1=> /= HM'1.
        apply: H'M'1. apply: allfv_ren.
        by apply: allfv_impl HM'1=> - [|[|?]]. }
      move: (H'M'1) => /measure_app_lam' ->.
      rewrite !measure_ren=> Hn1s H1ns H2ns.
      move: (HM'1) => /measure_app_lam' ->.
      rewrite !measure_lam. exists (n1s ++ measure M3). split.
      { rewrite !app_assoc. apply: Permutation_app_tail.
        by rewrite -!app_assoc. }
      exists (n2s ++ measure M3). split; first by apply: Forall2_app.
      have [H''M'1|H''M'1] := has_var_zero_dec M'1.
      { have /measure_app_lam -> : has_var_zero (app (lam (sarr s1 t') (ren swap M'1)) (ren S M'2)).
        { move=> /= [/allfv_ren' H _].
          apply: H''M'1. by apply: allfv_impl H=> - [|[|?]]. }
        move: H'M'1 => /measure_app_lam' ->.
        rewrite !measure_ren.
        exists ([(size_sty (sarr s2 t'), 0)] ++ ns). split.
        { rewrite !app_assoc. apply: Permutation_app_tail.
          rewrite -!app_assoc. by apply: Permutation_app. }
        apply /Forall_app. split; last done.
        constructor; last done.
        move=> /=. lia. }
      have /measure_app_lam' -> : not (has_var_zero (app (lam (sarr s1 t') (ren swap M'1)) (ren S M'2))).
      { move=> /= H. apply: H''M'1 => H''M'1.
        apply: H. split.
        - apply: allfv_ren. by apply: allfv_impl H''M'1=> - [|[|?]].
        - apply: allfv_ren. by apply: allfv_trivial=> - [|?]. }
      move: H'M'1 => /measure_app_lam' ->.
      rewrite !measure_ren.
      exists ns. split; last done.
      rewrite !app_assoc. apply: Permutation_app_tail.
      by rewrite -!app_assoc.
    + move=> t' M'1 M'2 {}n m.
      rewrite !measure_lam => Hn Hn1s H1ns H2ns.
      have [] := has_var_zero_dec M'1.
      { move=> HM'1.
        have : has_var_zero M'2.
        { move: Hn => /inner_stepG_stepG H HM'2.
          apply: HM'1. move: H HM'2 => /allfv_stepG'. by apply. }
        move: HM'1 => /measure_app_lam -> /measure_app_lam ->.
        exists (n1s ++ [(size_sty t', 0)] ++ measure M3). split.
        { rewrite !app_assoc. apply: Permutation_app_tail.
          apply: Permutation_trans; first by apply: Permutation_app_comm.
          by apply: Permutation_app. }
        exists (n2s ++ [(size_sty t', 0)] ++ measure M3). split; first by apply: Forall2_app.
        exists ns. split; last done.
        rewrite !app_assoc. apply: Permutation_app_tail.
        rewrite -app_assoc. apply: Permutation_trans; last by apply: Permutation_app_comm.
        rewrite !app_assoc. by apply: Permutation_app. }
      move=> HM'1.
      have : not (has_var_zero M'2).
      { move: Hn => /inner_stepG_stepG H HM'2.
        apply: HM'1=> HM'1. apply: HM'2. move: H HM'1 => /allfv_stepG. by apply. }
      move: HM'1 => /measure_app_lam' -> /measure_app_lam' ->.
      eexists (n1s ++ _ ++ measure M3). split.
      { rewrite !app_assoc. apply: Permutation_app_tail.
        apply: Permutation_trans; first by apply: Permutation_app_comm.
        by apply: Permutation_app. }
      move: (map inc_depth (measure M'2)) H1ns=> ??.
      move E: (n, m) Hn=> nm Hn.
      eexists (n2s ++ _ ++ measure M3). split; first by apply: Forall2_app.
      case: Hn E H2ns.
      * move=> ? > ?? [-> ->] ?.
        eexists ([_] ++ ns). split.
        { rewrite !app_assoc. apply: Permutation_app_tail.
          rewrite -!app_assoc app_nil_r. by apply: Permutation_app. }
        apply /Forall_app. split; last done.
        constructor; last done.
        move=> /=. lia.
      * move=> *. exists ns. split; last done.
        rewrite !app_assoc. apply: Permutation_app_tail.
        apply: Permutation_trans; last by apply: Permutation_app_comm.
        by apply: Permutation_app.
      * move=> *. exists ns. split; last done.
        rewrite !app_assoc. apply: Permutation_app_tail.
        apply: Permutation_trans; last by apply: Permutation_app_comm.
        by apply: Permutation_app.
      * move=> *. exists ns. split; last done.
        rewrite !app_assoc. apply: Permutation_app_tail.
        apply: Permutation_trans; last by apply: Permutation_app_comm.
        by apply: Permutation_app.
    + move=> > Hn Hn1s H1ns H2ns.
      exists (n1s ++ measure M3). split.
      { rewrite !measure_app_app app_assoc. by apply: Permutation_app_tail. }
      exists (n2s ++ measure M3). split; first by apply: Forall2_app.
      exists ns. split; last done.
      rewrite !measure_app_app app_assoc. by apply: Permutation_app_tail.
    + move=> > Hn Hn1s H1ns H2ns.
      exists (n1s ++ measure M3). split.
      { rewrite !measure_app_app app_assoc. by apply: Permutation_app_tail. }
      exists (n2s ++ measure M3). split; first by apply: Forall2_app.
      exists ns. split; last done.
      rewrite !measure_app_app app_assoc. by apply: Permutation_app_tail.
  - move=> > ? IH >.
    move=> /stlcE [>] ?.
    move=> /IH [n1s] [Hn1s] [n2s] [Hn1sn2s] [ns] [Hn2s Hns].
    rewrite /measure -/measure. eexists (n1s ++ _). split.
    { rewrite !app_assoc. apply: Permutation_trans; first by apply: Permutation_app_comm.
      by apply: Permutation_app. }
    eexists (n2s ++ _ ++ measure _). split; first by apply: Forall2_app.
    exists ns. split; last done.
    rewrite !app_assoc.
    apply: Permutation_trans; last by apply: Permutation_app_comm.
    rewrite !app_assoc. apply: Permutation_app; last done.
    by apply: Permutation_app.
Qed.

(* decreasing measure relation *)
Inductive measure_lt (mN mM : list (nat*nat)) : Prop :=
  | measure_lt_intro n n1s ns n2s :
    Permutation ([n] ++ n1s) mM ->
    Permutation (ns ++ n2s) mN ->
    Forall (fun '(n', m') => n' < fst n \/ n' = fst n /\ m' < snd n) ns ->
    Forall2 (fun '(n1, m1) '(n2, m2) => n1 = n2 /\ m2 <= m1) n1s n2s ->
    measure_lt mN mM.

Definition lt2 := @slexprod nat nat (Nat.lt) (Nat.lt).

Lemma lt2_spec x y : lt2 x y <-> (fst x < fst y \/ fst x = fst y /\ snd x < snd y).
Proof.
  split.
  - case=> /=; lia.
  - move: x y => [a b] [a' b'] /=.
    move=> [?|[<- ?]].
    + by apply: left_slex.
    + by apply: right_slex.
Qed.

Lemma lt2_wf : forall x, Acc lt2 x.
Proof.
  move=> [a]. elim /(Nat.measure_induction _ id) : a.
  rewrite /id=> a IHa b. elim /(Nat.measure_induction _ id) : b.
  rewrite /id=> b IHb. constructor=> - [a' b'] /lt2_spec /= [].
  - by move=> /IHa.
  - by move=> [->] /IHb.
Qed.

Lemma clos_refl_trans_list_lt_intro l l' :
  Forall2 (fun '(n1, m1) '(n2, m2) => n1 = n2 /\ m2 <= m1) l' l ->
  clos_refl_trans (list (nat * nat)) (list_lt lt2) l l'.
Proof.
  elim; first by constructor.
  move=> [a1 b1] [a2 b2] /= > [<-] *. apply: rt_trans.
  + apply: (clos_refl_trans_list_lt_app_r _ [_]). by eassumption.
  + apply: (clos_refl_trans_list_lt_app_l _ [_] [_]).
    have [<-|?] : b1 = b2 \/ b2 < b1 by lia.
    { by constructor. }
    apply: rt_step.
    rewrite -(app_nil_r [(a1, b2)]) -(app_nil_r [(a1, b1)]).
    apply: (list_lt_intro _ _ [_] nil nil).
    constructor; last done.
    apply /lt2_spec=> /=. lia.
Qed.

(* measure_lt is well-founded *)
Theorem measure_lt_wf : well_founded measure_lt.
Proof.
  apply: (wf_clos_trans_inverse_rel _ (list_lt lt2) (@Permutation (nat * nat))).
  - apply: list_lt_wf. apply: lt2_wf.
  - move=> l. by exists l.
  - move=> l1 l2 l'2 [] n n1s ns n2s Hl2 Hl1 Hns Hn12s Hl2l'2.
    move: Hl2 Hl2l'2 Hl1 => /Permutation_trans /[apply].
    have : In n ([n] ++ n1s).
    { apply /in_app_iff. left. by left. }
    move=> /Permutation_in + /[dup] => /[apply] /in_split [l'3] [l'4] ->.
    move=> /(@Permutation_app_inv (nat*nat) nil) Hn1s Hn2s.
    move: Hn12s Hn1s => /Forall2_permutation_app /[apply].
    move=> [l3] [l4] [?] [H3 H4].
    exists (l3 ++ ns ++ l4). split.
    + apply: Permutation_trans; first by (apply: Permutation_sym; eassumption).
      by apply: (Permutation_app_middle _ nil).
    + apply: (@clos_rt_t _ _ _ (l'3 ++ ns ++ l'4)).
      { apply: clos_refl_trans_list_lt_intro.
        apply Forall2_app; first done.
        apply Forall2_app; last done.
        elim: (ns); first done.
        move=> [??] ??. constructor; last done. lia. }
      apply: t_step. constructor.
      apply: Forall_impl Hns.
      move: n=> - [??] [??] /= ?. apply /lt2_spec=> /=. lia.
Qed.

Lemma measure_spec Gamma M t : measure M <> [] -> stlc Gamma M t -> exists N y, inner_stepI y M N \/ inner_stepG y M N.
Proof.
  elim /(Nat.measure_induction _ size_tm): M Gamma t.
  move=> [?|M1 M2|t M] IH.
  - done.
  - move=> ?? + /stlcE [>] ++.
    have [|] : measure M2 <> [] \/ measure M2 = [].
    { by move: (measure M2) => [|??] /=; [right|left]. }
    { move=> /IH {}IH _ _ /IH - [].
      { move=> /=. lia. }
      move=> ? [?] [|] ?.
      * do 2 eexists. left. apply: inner_stepIAppR. by eassumption.
      * do 2 eexists. right. apply: inner_stepGAppR. by eassumption. }
    have [|] : measure M1 <> [] \/ measure M1 = [].
    { by move: (measure M1) => [|??] /=; [right|left]. }
    { move=> /IH {}IH _ _ /IH - [].
      { move=> /=. lia. }
      move=> ? [?] [|] ?.
      * do 2 eexists. left. apply: inner_stepIAppL. by eassumption.
      * do 2 eexists. right. apply: inner_stepGAppL. by eassumption. }
    rewrite /measure -/measure.
    move=> /[dup] HM1 -> /[dup] HM2 ->. rewrite !app_nil_r.
    move: M1 HM1 IH=> [?|t' M'1 M'2|t' M'] IH.
    + done.
    + done.
    + case: (has_var_zero_dec M')=> /=.
      { move=> ??? /stlcE [>] ? [??] ??. subst.
        do 2 eexists. left. by apply: inner_stepIRed. }
      move: M' IH=> [?|???|??]; [done..|].
      move=> ??? _ /stlcE [>] /stlcE [>] ? ??. subst.
      move=> [??] ??. subst.
      do 2 eexists. right. by apply: inner_stepGRed.
  - move=> >. rewrite measure_lam.
    move=> /map_neq_nil /IH {}IH.
    move=> /stlcE [>] /IH - [].
    { move=> /=. lia. }
    move=> ? [[??]] [|] *; subst.
    + do 2 eexists. left. constructor. by eassumption.
    + do 2 eexists. right. constructor. by eassumption.
Qed.

(* any simply typed term (I, gamma)-reduces to a term with an empty measure *)
Lemma stepIG_normalization Gamma M t : stlc Gamma M t -> exists N, clos_refl_trans _ (fun P Q => stepI P Q \/ stepG P Q) M N /\ measure N = [] /\ stlc Gamma N t.
Proof.
  have := measure_lt_wf (measure M).
  move E: (measure M)=> n H. elim: H M E.
  move=> l _ IH M ?. subst l.
  move E: (measure M)=> [|x ?].
  { move=> ?. exists M. by split; first by apply: rt_refl. }
  have: measure M <> [] by congruence.
  move=> /measure_spec + /[dup] => /[apply] - [N] [y] [|].
  - move=> /[dup] /inner_stepI_stepI /[dup] HMN /stepI_reduction H + /[dup] + /H.
    move=> /measure_decrease_inner_stepI /[apply].
    move=> [?] [?] [?] [?] [?] [??].
    have : measure_lt (measure N) (measure M).
    { econstructor; by eassumption. }
    move=> /IH => /(_ _ eq_refl) /[apply].
    move=> [N'] [??]. exists N'. split; last done.
    apply: rt_trans; last by eassumption.
    apply: rt_step. by left.
  - move=> /[dup] /inner_stepG_stepG /[dup] HMN /stepG_reduction H + /[dup] + /H.
    move=> /measure_decrease_inner_stepG /[apply].
    move=> [?] [?] [?] [?] [?] [??].
    have : measure_lt (measure N) (measure M).
    { econstructor; by eassumption. }
    move=> /IH => /(_ _ eq_refl) /[apply].
    move=> [N'] [??]. exists N'. split; last done.
    apply: rt_trans; last by eassumption.
    apply: rt_step. by right.
Qed.

(* count the number of redexes *)
Fixpoint redex_count (M : tm) : nat :=
  match M with
  | var _ => 0
  | lam _ M => redex_count M
  | app M N =>
    match M with
    | var _ => 0
    | lam _ _ => 1 + redex_count M
    | app _ _ => redex_count M
    end + redex_count N
  end.

Lemma redex_count_zero_spec M : redex_count M = 0 -> nf M.
Proof.
  elim: M.
  - move=> *. by do 2 constructor.
  - move=> /= [?|??|??] IH1 ? IH2.
    + move=> /IH2 ?. do 2 constructor; last done.
      by constructor.
    + move=> /Nat.eq_add_0 [/IH1] {}IH1 /IH2 {}IH2.
      do 2 constructor; last done.
      by inversion IH1.
    + done.
  - move=> > /= /[apply] ?. by constructor.
Qed.

Lemma measure_app_nil M N : measure (app M N) = [] -> measure M = [] /\ measure N = [].
Proof.
  by rewrite /measure -/measure=> /app_eq_nil [] ? /app_eq_nil.
Qed.

Lemma redex_count_spec Gamma M t : measure M = [] -> redex_count M <> 0 -> stlc Gamma M t -> exists N, stepK M N.
  elim /(Nat.measure_induction _ size_tm): M Gamma t.
  move=> [x|M1 M2|t M] IH.
  - done.
  - move=> Gamma s.
    move: M1 IH=> [].
    + move=> x IH /=. rewrite measure_app_var.
      move=> /IH /[apply] {}IH.
      move=> /stlcE [>] ? /IH - [].
      { move=> /=. lia. }
      move=> *. eexists. constructor; last by eassumption.
      by constructor.
    + move=> M'1 M'2 IH. rewrite measure_app_app.
      change (redex_count (app (app M'1 M'2) M2)) with ((redex_count (app M'1 M'2)) + (redex_count M2)).
      move=> /app_eq_nil [] /IH {}IH1 /IH {}IH2 ?.
      have [|] : redex_count (app M'1 M'2) <> 0 \/ (redex_count (app M'1 M'2) = 0 /\ redex_count M2 <> 0) by lia.
      * move=> /IH1 {}IH1.
        move=> /stlcE [>] /[dup] /stlcE [>] ??.
        move=> /IH1 - [].
        { move=> /=. lia. }
        move=> *. subst. eexists. apply: stepKAAppL. by eassumption.
      * move=> [/redex_count_zero_spec] H'.
        move=> /IH2 {}IH2 /stlcE [>] _ /IH2 - [].
        { move=> /=. lia. }
        move=> *. eexists. apply: stepKNAppR; last by eassumption.
        inversion H'. subst.
        elim: H; by eauto using hf.
    + move=> t' M' IH.
      have [|HM'] := has_var_zero_dec M'.
      { by move=> /measure_app_lam ->. }
      move: IH.
      have -> : M' = ren S (ren Nat.pred M').
      { rewrite ren_ren -[LHS]ren_id.
        apply: ext_allfv_ren.
        have [] := allfv_dec (fun x : nat => id x = funcomp S Nat.pred x) M'.
        - rewrite /id. by move=> [|?] /=; [right|left].
        - done.
        - move=> H. exfalso. apply: HM'=> HM'. apply: H.
          by apply: allfv_impl HM'=> - [|?] /=. }
      move=> IH H1M2 H2M2 /stlcE [>] /stlcE [>] ? [??] ? H3M2. subst.
      have [|] : (redex_count M2 <> 0) \/ (redex_count M2 = 0) by lia.
      { move: H1M2=> /measure_app_nil [_].
        move: H3M2=> /IH /[apply] /[apply] - [].
        { move=> /=. lia. }
        move=> *. eexists. apply: stepKLAppR. by eassumption. }
      move=> /redex_count_zero_spec /stepKRed H.
      eexists. by apply: H.
  - rewrite measure_lam /=.
    move=> > /map_eq_nil /IH /[apply] {}IH.
    move=> /stlcE [>] /IH - [].
    { move=> /=. lia. }
    move=> *. eexists. constructor. by eassumption.
Qed.

Lemma redex_count_ren xi M : redex_count (ren xi M) = redex_count M.
Proof.
  elim: M xi.
  - done.
  - move=> M IH1 ? IH2 > /=.
    rewrite IH1 IH2. congr Nat.add.
    by case: (M).
  - move=> > IH >. by apply: IH.
Qed.

Lemma redex_count_stepK M N : stepK M N -> measure M = [] -> measure N = [] /\ redex_count N < redex_count M.
Proof.
  elim.
  - move=> > /= ?.
    move=> /[dup] /measure_app_nil [].
    rewrite measure_lam measure_ren redex_count_ren=> /map_eq_nil *.
    by split; [|lia].
  - move=> >. rewrite !measure_lam /=.
    by move=> ? IH /map_eq_nil /IH [-> ?].
  - move=> > ?? IH /[dup] /measure_app_nil [_] /[dup] E /IH [{}IH ?] H. split.
    + move: H. by rewrite /measure -/measure E IH !app_nil_r.
    + move=> /=. lia.
  - move=> > ? IH /[dup] /measure_app_nil [_] /[dup] E /IH [{}IH ?] H. split.
    + move: H. by rewrite /measure -/measure E IH !app_nil_r.
    + move=> /=. lia.
  - move=> M1 M2 M3 {}N H0M3 IH /[dup] /measure_app_nil [] /[dup] /IH {IH} [H1M3 H2M3] ? HN HM''.
    move E: (app M1 M2) H0M3=> M' H.
    case: H E H1M3 H2M3.
    + move=> ? M'' ?? [] ???. subst.
      move: HM''. rewrite measure_app_app measure_app_lam' ?measure_ren.
      { apply. apply: allfv_ren. by apply: allfv_trivial. }
      move=> HM'' H2M3. split; first last.
      { move: H2M3 => /=. rewrite !redex_count_ren.
        by case: (M'') HM''; [lia..|]. }
      rewrite /measure -/measure.
      move: (M'') HM''=> [] /=; last done.
      * by move=> _ /app_eq_nil [].
      * by move=> > /app_eq_nil [] /app_eq_nil [] /map_eq_nil ->.
    + done.
    + move=> > ?? [] ??. subst. rewrite !measure_app_app HN.
      move=> -> H. split; first done.
      move: H => /=. lia.
    + move=> > ? [] ??. subst. rewrite !measure_app_app HN.
      move=> -> H. split; first done.
      move: H => /=. lia.
    + move=> > ? [] ??. subst. rewrite !measure_app_app HN.
      move=> -> H. split; first done.
      move: H => /=. lia.
Qed.

(* if measure is empty, then the term K-reduces to a normal form *)
Lemma stepK_normalization Gamma M t : stlc Gamma M t -> measure M = [] ->
  exists N, clos_refl_trans _ stepK M N /\ redex_count N = 0 /\ stlc Gamma N t.
Proof.
  elim /(Nat.measure_induction _ redex_count): M.
  move=> M IH.
  move E: (redex_count M) IH=> [|?].
  { move=> _ ??. exists M. by split; first by apply: rt_refl. }
  move=> IH.
  have /redex_count_spec : redex_count M <> 0 by congruence.
  move=> H /[dup] /H.
  move=> {}H + /[dup] /H - [N HMN].
  move: (HMN)=> /stepK_reduction {}H /[dup] /H.
  move: (HMN)=> /redex_count_stepK {}H + HM /H [].
  rewrite E=> /IH /[apply] /[apply] => - [N'] [??].
  exists N'. split; last done.
  apply: rt_trans; last by eassumption.
  by apply: rt_step.
Qed.

Theorem stlc_nf M Gamma t : stlc Gamma M t -> exists N, steps M N /\ nf N.
Proof.
  move=> /stepIG_normalization [M'] [HMM'] [].
  move=> /stepK_normalization /[apply] - [N] [HM'N] [/redex_count_zero_spec ?] ?.
  exists N. split; [|done].
  apply: (rt_trans _ _ _ M').
  - elim: HMM'=> *.
    + apply: rt_step. rewrite /step. by tauto.
    + by apply: rt_refl.
    + apply: rt_trans; by eassumption.
  - elim: HM'N=> *.
    + apply: rt_step. rewrite /step. by tauto.
    + by apply: rt_refl.
    + apply: rt_trans; by eassumption.
Qed.
