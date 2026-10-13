Require Import Relations List Lia PeanoNat Permutation Wellfounded.
Import ListNotations.
Require Import ssreflect ssrfun.

Arguments nth_error_split {A l n a}.
Arguments Permutation_nil_cons {A l x}.
Arguments in_split {A x}.

(* point-wise list concatenation *)
Fixpoint merge {X : Type} (Gamma : list (list X)) (Delta : list (list X)) : list (list X) :=
  match Gamma with
  | nil => Delta
  | cons u Gamma =>
    match Delta with
    | nil => cons u Gamma
    | cons v Delta => cons (u ++ v) (merge Gamma Delta)
    end
  end.

Lemma Forall2E {X Y : Type} {P : X -> Y -> Prop} l1 l2 : Forall2 P l1 l2 ->
  match l1 with
  | nil => l2 = nil
  | cons x l1 =>
      match l2 with
      | nil => False
      | cons y l2 => P x y /\ Forall2 P l1 l2
      end
  end.
Proof.
  by case.
Qed.

Lemma Forall2_trans {X Y Z : Type} (P : X -> Y -> Prop) (Q : Y -> Z -> Prop) (R : X -> Z -> Prop) l1 l2 l3 :
  (forall x y z, P x y -> Q y z -> R x z) -> Forall2 P l1 l2 -> Forall2 Q l2 l3 -> Forall2 R l1 l3.
Proof.
  move=> HPQR H. elim: H l3.
  - move=> ? /Forall2E ->. by constructor.
  - move=> > ??? [|? l3] /Forall2E; [done|].
    move=> [? ?]. constructor; by eauto.
Qed.

Lemma Forall2_map_l {X Y Z : Type} (P : X -> Y -> Prop) (f : Z -> X) l1 l2 :
  Forall2 (fun x y => P (f x) y) l1 l2 -> Forall2 P (map f l1) l2.
Proof.
  elim.
  - constructor.
  - move=> * /=. by constructor.
Qed.

Lemma Forall2_map_r {X Y Z : Type} (P : X -> Y -> Prop) (f : Z -> Y) l1 l2 :
  Forall2 (fun x y => P x (f y)) l1 l2 -> Forall2 P l1 (map f l2).
Proof.
  elim.
  - constructor.
  - move=> * /=. by constructor.
Qed.

Lemma Forall2_eq {X : Type} (P : X -> X -> Prop) l :
  Forall (fun x => P x x) l -> Forall2 P l l.
Proof. elim; by constructor. Qed.

Lemma merge_nil_r {X : Type} (Gamma : list (list X)) : merge Gamma nil = Gamma.
Proof.
  by case: Gamma.
Qed.

Lemma cons_app {X : Type} (x : X) x1s x2s : x :: x1s ++ x2s = [x] ++ x1s ++ x2s.
Proof. done. Qed.

Lemma map_neq_nil {X Y : Type} {f : X -> Y} l : map f l <> [] -> l <> [].
Proof.
  by case: l.
Qed.

Lemma nth_merge {X : Type} (Gamma1 Gamma2 : list (list X)) x :
  nth x (merge Gamma1 Gamma2) nil = nth x Gamma1 nil ++ nth x Gamma2 nil.
Proof.
  elim: x Gamma1 Gamma2.
  - by move=> [|??] [|??]; rewrite /= ?app_nil_r.
  - by move=> x IH [|??] [|??]; rewrite /= ?app_nil_r.
Qed.

Lemma In_nth_merge_l {X : Type} (Gamma2 Gamma1 : list (list X)) A x :
  In A (nth x Gamma1 nil) -> In A (nth x (merge Gamma1 Gamma2) nil).
Proof.
  move=> ?. rewrite nth_merge. apply /in_app_iff. by left.
Qed.

Lemma In_nth_merge_r {X : Type} (Gamma1 Gamma2 : list (list X)) A x :
  In A (nth x Gamma2 nil) -> In A (nth x (merge Gamma1 Gamma2) nil).
Proof.
  move=> ?. rewrite nth_merge. apply /in_app_iff. by right.
Qed.

Lemma nth_map_seq_lt {X : Type} {f : nat -> X} {i n d} : i < n -> nth i (map f (seq 0 n)) d = f i.
Proof.
  suff: (forall k, i < n -> nth i (map f (seq k n)) d = f (k + i)).
  { move=> /(_ 0). by apply. }
  elim: n i.
  - lia.
  - move=> n IH [|i] k ? /=.
    + by rewrite Nat.add_0_r.
    + rewrite IH; [lia|].
      by rewrite Nat.add_succ_r.
Qed.

Lemma nth_map_seq_ge {X : Type} {f : nat -> X} {i n d} : i >= n -> nth i (map f (seq 0 n)) d = d.
Proof.
  suff: (forall k, i >= n -> nth i (map f (seq k n)) d = d).
  { move=> /(_ 0). by apply. }
  elim: n i.
  - by case.
  - move=> n IH [|i] k ? /=.
    + lia.
    + by rewrite IH; [lia|].
Qed.

Fixpoint replace {X : Type} (xs : list X) (n : nat) (l : list (list X)) :=
  match n with
  | 0 => match l with
         | [] => [xs]
         | ys :: l => xs :: l
         end
  | S n =>
      match l with
      | [] => [] :: replace xs n l
      | ys :: l => ys :: replace xs n l
      end
  end.

Lemma nth_replace {X : Type} {xs : list X} {i l} : nth i (replace xs i l) [] = xs.
Proof.
  elim: i l.
  - by case.
  - move=> i IH [|??]; by apply: IH.
Qed.

Lemma nth_replace_neq {X : Type} {xs : list X} {i j l} : i <> j -> nth i (replace xs j l) [] = nth i l [].
Proof.
  elim: i j l.
  - by move=> [|?] [|??] /=.
  - move=> i IH [|j] [|??] /= ?.
    + by case: (i).
    + done.
    + rewrite IH; [lia|]. by case: (i).
    + apply: IH. lia.
Qed.

Lemma In_nth {X : Type} {n l} {x : X} : In x (nth n l []) ->
  exists l1 ys1 ys2 l2, l = l1 ++ (ys1 ++ x :: ys2) :: l2 /\ length l1 = n.
Proof.
  elim: n l.
  - move=> [|y l] /=; first done.
    move=> /in_split [ys1] [ys2] ->.
    by exists nil, ys1, ys2, l.
  - move=> n IH [|y l] /=; first done.
    move=> /IH [l1] [ys1] [ys2] [l2] [->] <-.
    by exists (y :: l1), ys1, ys2, l2.
Qed.

Lemma nth_middle_neq {X : Type} {n l1 l2 d} (x y : X) :
  n <> length l1 ->
  nth n (l1 ++ x :: l2) d = nth n (l1 ++ y :: l2) d.
Proof.
  elim: n l1.
  * by case.
  * move=> n IH [|??] /= ?; first done.
    apply: IH. lia.
Qed.

Fixpoint insert {X : Type} (x : X) n l :=
  match n with
  | 0 =>
    match l with
    | [] => [[x]]
    | xs :: l => (x :: xs) :: l
    end
  | S n =>
    match l with
    | [] => [] :: insert x n l
    | xs :: l => xs :: insert x n l
    end
  end.

Lemma nth_insert_neq {X : Type} {x : X} n1 n2 l : n1 <> n2 -> nth n1 (insert x n2 l) [] = nth n1 l [].
Proof.
  elim: n2 n1 l.
  - by move=> [|[|n1]] [|??] /=.
  - move=> n2 IH [|n1] [|??] /= ?; [done|done|..].
    * rewrite IH; [lia|]. by case: (n1).
    * apply: IH. lia.
Qed.

Lemma nth_insert {X : Type} {x : X} n l :
  nth n (insert x n l) [] = x :: nth n l [].
Proof.
  elim: n l.
  - by case.
  - move=> n IH [|??] /=; rewrite IH; by case: (n).
Qed.

Lemma nth_error_combine {X Y : Type} {n} {l1 : list X} {l2 : list Y} {x y} : nth_error (combine l1 l2) n = Some (x, y) <->
  (nth_error l1 n = Some x /\ nth_error l2 n = Some y).
Proof.
  split.
  - elim: l1 l2 n.
    + by move=> [|??] [|?] /=.
    + move=> ?? IH [|??] [|n] /= ?; [split; congruence..|].
      by apply: IH.
  - elim: l1 l2 n.
    + by move=> [|??] [|?] [] /=.
    + move=> ?? IH [|??] [|?] /= []; [congruence..|].
      move=> *. by apply: IH.
Qed.

Lemma map_nil {X Y : Type} (f : X -> Y) : map f [] = [].
Proof. done. Qed.

Lemma list_sum_cons n ns : list_sum (n :: ns) = n + list_sum ns.
Proof. done. Qed.

Lemma nth_error_length_neq {X Y : Type} (l1 : list X) (l2 : list Y) n : 
  nth_error l1 n <> None ->
  nth_error l2 n = None ->
  length l1 <> length l2.
Proof.
  move=> /nth_error_Some ? /nth_error_None ?. lia.
Qed.

Lemma Forall2_concat {X Y : Type} (P : X -> Y -> Prop) (l1s : list (list X)) (l2s : list (list Y)) :
  Forall2 (Forall2 P) l1s l2s -> Forall2 P (concat l1s) (concat l2s).
Proof.
  elim; first done.
  move=> * /=. by apply: Forall2_app.
Qed.

Lemma In_In_combine_l {X Y : Type} {x : X} l1 l2 : In x l1 -> length l1 = length l2 -> exists (y : Y), In (x, y) (combine l1 l2).
Proof.
  elim: l1 l2; first done.
  move=> ?? IH [|??] /=; first done.
  move=> [?|/IH].
  - subst=> ?. eexists. by left.
  - move=> H [/H] [??].
    eexists. right. by eassumption.
Qed.

Lemma In_In_combine_r {X Y : Type} {y : Y} l1 l2 : In y l2 -> length l1 = length l2 -> exists (x : X), In (x, y) (combine l1 l2).
Proof.
  elim: l2 l1; first done.
  move=> ?? IH [|??] /=; first done.
  move=> [?|/IH].
  - subst=> ?. eexists. by left.
  - move=> H [/H] [??].
    eexists. right. by eassumption.
Qed.

Lemma Forall2_Forall {X Y : Type} (P : X -> Y -> Prop) l1 l2 :
  (Forall (fun xy => P (fst xy) (snd xy)) (combine l1 l2) /\ length l1 = length l2) <-> Forall2 P l1 l2.
Proof.
  split.
  - elim: l1 l2.
    + by move=> [|??] [].
    + move=> ?? IH [|??] [] /=; first done.
      move=> /Forall_cons_iff [??] [?].
      constructor; first done.
      by apply: IH.
  - elim; first done.
    move=> > ?? /= [? ->]. by split; [constructor|].
Qed.

Lemma Forall2_exists_exists_Forall2 {X Y Z : Type} (P : X -> Y -> Z -> Prop) l1 l2 :
  Forall2 (fun x y => exists z, P x y z) l1 l2 ->
  exists zs, Forall2 (fun z xy => P (fst xy) (snd xy) z) zs (combine l1 l2).
Proof.
  elim.
  - by exists nil.
  - move=> > [z ?] ? [zs ?]. exists (z :: zs). by constructor.
Qed.

Lemma Permutation_Forall {A : Type} (P : A -> Prop) (l1 l2 : list A) : Permutation l1 l2 -> Forall P l1 -> Forall P l2.
Proof.
  elim.
  - done.
  - move=> > ?? /Forall_cons_iff [??]. by constructor; auto.
  - move=> > /Forall_cons_iff [? /Forall_cons_iff [??]]. by do ? constructor.
  - by auto.
Qed.

Lemma nth_skipn {A : Type} n1 n2 (a : A) l : nth n1 (skipn n2 l) a = nth (n2 + n1) l a.
Proof.
  elim: n2 l; first done.
  move=> n2 IH [|??] /=.
  - by case: (n1).
  - by apply: IH.
Qed.

Lemma concat_cons {A : Type} (l1 : list A) ls : concat (l1 :: ls) = l1 ++ concat ls.
Proof. done. Qed.

Lemma Permutation_eq {X : Type} {l1 l2 : list X} : l1 = l2 -> Permutation l1 l2.
Proof. by move=> ->. Qed.

Lemma Forall2_permutation_app {X Y : Type} (P : X -> Y -> Prop) l l' l1 l2 : Forall2 P l l' -> Permutation l (l1 ++ l2) ->
  exists l'1 l'2, Permutation l' (l'1 ++ l'2) /\ Forall2 P l1 l'1 /\ Forall2 P l2 l'2.
Proof.
  move=> H. elim: H l1 l2.
  { move=> > /Permutation_nil /app_eq_nil [-> ->]. by exists nil, nil. }
  move=> x y {}l {}l' Hxy ? IH l1 l2.
  have : In x (x :: l) by left.
  move=> /(@Permutation_in X) + /[dup] => /[apply] /in_app_iff [].
  - move=> /in_split [l3] [l4] ?. subst.
    rewrite -app_assoc /=.
    move=> /(@Permutation_app_inv X nil).
    rewrite app_assoc=> /IH [l'3] [l'4] [?].
    move=> [/Forall2_app_inv_l] [l'31] [l'32] [?] [?] *. subst.
    exists (l'31 ++ y :: l'32), l'4. split; [|split].
    + rewrite -app_assoc /=.
      apply: (Permutation_app_middle [_] nil).
      by rewrite !app_assoc.
    + apply: Forall2_app; first done.
      by constructor.
    + done.
  - move=> /in_split [l3] [l4] ?. subst.
    rewrite app_assoc /=.
    move=> /(@Permutation_app_inv X nil).
    rewrite -app_assoc=> /IH [l'3] [l'4] [?] [?].
    move=> /Forall2_app_inv_l [l'41] [l'42] [?] [?] *. subst.
    exists l'3, (l'41 ++ y :: l'42). split; [|split].
    + rewrite app_assoc /=.
      apply: (Permutation_app_middle [_] nil).
      by rewrite -!app_assoc.
    + done.
    + apply: Forall2_app; first done.
      by constructor.
Qed.

Lemma wf_clos_trans_inverse_rel {A B : Type} (Q : relation B) (R : relation A) (F : B -> A -> Prop) :
  well_founded R ->
  (forall b, exists a, F b a) ->
  (forall b1 b2 a1, Q b2 b1 -> F b1 a1 -> exists a2, F b2 a2 /\ clos_trans _ R a2 a1) ->
  well_founded Q.
Proof.
  intros HR Hintro Hstep b.
  destruct (Hintro b) as [a H].
  revert b H.
  induction (wf_clos_trans _ _ HR a) as [a _ IH].
  intros b Hba.
  constructor.
  intros b' Hb'b.
  destruct (Hstep _ _ _ Hb'b Hba) as [a' [??]].
  eapply IH; eassumption.
Qed.

(* well-founded list extension of a well-founded relation *)
Section ListLt.

Context {X : Type} (ltX : X -> X -> Prop) (ltX_wf : forall x, Acc ltX x).

Inductive list_lt : list X -> list X -> Prop :=
  | list_lt_intro x (ys : list X) l1 l2 :
      Forall (fun y => ltX y x) ys ->
      list_lt (l1 ++ ys ++ l2) (l1 ++ x :: l2).

Lemma list_lt_nil_r l : not (list_lt l nil).
Proof.
  move E: nil => l' H.
  by case: H E=> ?? [|??].
Qed.

Lemma list_lt_wf_app l1 l2 : Acc list_lt l1 -> Acc list_lt l2 -> Acc list_lt (l1 ++ l2).
Proof.
  move=> H. elim: H l2=> {}l1 _ IH1 l2.
  elim=> {}l2 Hl2 IH2. move E: (l1 ++ l2)=> l.
  constructor=> l' H. case: H E=> x ys l3 l4 ?.
  move=> /app_eq_app=> - [l''] [].
  - move: l''=> [|??] /=.
    + rewrite app_nil_r=> - [??]. subst.
      apply: IH2. by apply: (list_lt_intro x ys nil).
    + move=> [? [??]]. subst. rewrite !app_assoc.
      apply: IH1.
      * rewrite -!app_assoc. by constructor.
      * constructor=> ?. by apply: Hl2.
  - move=> [??]. subst. rewrite -!app_assoc.
    apply: IH2. by constructor.
Qed.

Lemma Acc_list_lt : forall l, Forall (Acc ltX) l -> Acc list_lt l.
Proof.
  elim.
  - by constructor=> ? /list_lt_nil_r.
  - move=> x l Hl.
    move=> /Forall_cons_iff [Hx /Hl {}Hl].
    apply: (list_lt_wf_app [_]); last done.
    elim: Hx {l Hl}=> {}x _ IH.
    constructor=> l'. move E: ([x])=> l H.
    case: H E=> ?? [|?[|?[|??]]] [|??]; [|done..].
    move=> + [?] /=. subst. elim.
    + by constructor=> ? /list_lt_nil_r.
    + move=> *. apply: (list_lt_wf_app [_]); last done.
      by apply: IH.
Qed.

Lemma list_lt_wf : well_founded list_lt.
Proof.
  move=> l. apply: Acc_list_lt.
  apply /Forall_forall=> *. by apply: ltX_wf.
Qed.

Lemma clos_trans_list_lt_neq_nil l : l <> [] -> clos_trans (list X) list_lt [] l.
Proof.
  elim: l; first done.
  move=> x [|y l] IH _.
  - apply: t_step. by apply: (list_lt_intro x [] nil nil).
  - apply: t_trans.
    + by apply: IH.
    + apply: t_step.
      by apply: (list_lt_intro x [] nil (_ :: _)).
Qed.

Lemma list_lt_app_l l1 l2 l : list_lt l1 l2 -> list_lt (l1 ++ l) (l2 ++ l).
Proof.
  move=> [] *. rewrite -!app_assoc. by constructor.
Qed.

Lemma list_lt_app_r l l1 l2 : list_lt l1 l2 -> list_lt (l ++ l1) (l ++ l2).
Proof.
  move=> [] ?? l' *. rewrite !(app_assoc l l'). by constructor.
Qed.

Lemma clos_trans_list_lt_app_l l1 l2 l : clos_trans (list X) list_lt l1 l2 -> clos_trans (list X) list_lt (l1 ++ l) (l2 ++ l).
Proof.
  elim.
  - move=> *. apply: t_step. by apply: list_lt_app_l.
  - move=> *. apply: t_trans; by eassumption.
Qed.

Lemma clos_trans_list_lt_app_r l l1 l2 : clos_trans (list X) list_lt l1 l2 -> clos_trans (list X) list_lt (l ++ l1) (l ++ l2).
Proof.
  elim.
  - move=> *. apply: t_step. by apply: list_lt_app_r.
  - move=> *. apply: t_trans; by eassumption.
Qed.

Lemma clos_refl_trans_list_lt_app_l l1 l2 l : clos_refl_trans (list X) list_lt l1 l2 -> clos_refl_trans (list X) list_lt (l1 ++ l) (l2 ++ l).
Proof.
  elim.
  - move=> *. apply: rt_step. by apply: list_lt_app_l.
  - by constructor.
  - move=> *. apply: rt_trans; by eassumption.
Qed.

Lemma clos_refl_trans_list_lt_app_r l l1 l2 : clos_refl_trans (list X) list_lt l1 l2 -> clos_refl_trans (list X) list_lt (l ++ l1) (l ++ l2).
Proof.
  elim.
  - move=> *. apply: rt_step. by apply: list_lt_app_r.
  - by constructor.
  - move=> *. apply: rt_trans; by eassumption.
Qed.

End ListLt.
