(** This file has been adapted from Dominik Kirst's Bachelor Thesis
    "Formalised Set Theory: Well-Orderings and the Axiom of Choice",
    see https://www.ps.uni-saarland.de/~kirst/bachelor.php
*)

Require Import Stdlib.Logic.Classical_Prop.
From SynthDom.ordinals Require Export set_model.
From SynthDom.ordinals Require Import set_sets set_functions.


Set Universe Polymorphism.
Set Universe Minimization ToSet.


(** * Set-theoretic ordinals as a step-index type using several axioms *)
(** In total, this development relies on:
  - PE
  - FE
  - Hilbert's ϵ
  - XM
  - PI (but this is already implied by PE)
*)
Require Import Stdlib.Logic.Epsilon.


(** ** Definition and General Statements *)
Section set_ordinals.
Local Open Scope zf_scope.
Polymorphic Universe i.
Implicit Types (a b c A B C: set@{i}).

Definition succ_set a : set := a ∪ singleton a.
Definition zero_set : set := ∅.
Definition one_set : set := succ_set zero_set.

(* we can construct omega by taking infinity and removing all elements which are not constructed by zero_set or succ_set *)
Definition omega_set := specification_set infinite_set (λ x, ∃ n, x = Nat.iter n succ_set zero_set).
Lemma omega_spec : ∀ x, x ∈ omega_set ↔ ∃ n, x = Nat.iter n succ_set zero_set.
Proof.
  intros x. split.
  - intros Hel. apply zf_specification in Hel. apply Hel.
  - intros (n & ->). apply zf_specification. split; [ | eauto].
    induction n; cbn.
    + apply Infinity.
    + apply Infinity, IHn.
Qed.
Definition stransitive (A: set@{i}) := ∀ (x: set@{i}), x ∈ A → x ⊆ A.
Definition elorder A := specification_set (product A A) (λ p, pi1 p ∈ pi2 p).
Definition ordinal (a: set@{i}) := stransitive a ∧ wordering (elorder a) a.

Lemma empty_ordinal: ordinal empty.
Proof.
split.
- intros x I. exfalso. contradiction (zf_existence x).
- cut (elorder ∅ = ∅).
+ intros J. rewrite J. apply wordering_empty.
+ apply zf_extensionality; split; eauto using empty_subs.
  intros p H. apply spec_subs in H.
  apply product_pi in H as [H _]. contradiction (zf_existence (pi1 p)).
Qed.

Lemma elorder_el a b A: a ∈ b → a ∈ A → b ∈ A → (a,b) ∈ elorder A.
Proof.
intros I J J'. apply zf_specification. split.
- apply product_opair. split; eauto.
- now rewrite pi1_cor pi2_cor.
Qed.

Lemma elorder_el' a b A: (a,b) ∈ elorder A → a ∈ A ∧ b ∈ A ∧ a ∈ b.
Proof.
intros I.
apply zf_specification in I as [I J].
apply product_opair in I as [I1 I2].
rewrite pi1_cor pi2_cor in J.
now repeat split.
Qed.

Lemma elorder_element A a b: (a,b) ∈ elorder A → a ∈ b.
Proof.
  apply elorder_el'.
Qed.


Lemma elorder_res a b: a ⊆ b → (elorder b)|> a = elorder a.
Proof.
intros I. apply zf_extensionality; split; intros p J.
- apply zf_specification in J as [J1 J2].
  apply zf_specification in J1 as [J1 J1'].
  apply zf_specification. now split.
- apply zf_specification in J as [J1 J2].
  apply zf_specification. split; auto.
  apply zf_specification. split; eauto.
  now apply (product_subs b a I p).
Qed.

Lemma succ_set_subs A B: A ⊆ B → A ⊆ succ_set B.
Proof.
intros I x J. apply bunionI1. exact (I x J).
Qed.

Lemma succ_set_el A: A ∈ succ_set A.
Proof.
apply bunionI2. now apply single_el.
Qed.

Lemma succ_set_subset A: A ⊆ succ_set A.
Proof.
intros x I. now apply bunionI1.
Qed.

Lemma el_succ_set b a: ordinal a → b ∈ a → succ_set b ⊆ succ_set a.
Proof.
intros AO I. intros x X.
apply bunionE in X as [X|X].
- apply bunionI1. apply AO with (x:=b); assumption.
- apply single_el in X. subst x.
  apply bunionI1. assumption.
Qed.

Lemma el_succ_set_subs b a: ordinal a → b ∈ a → succ_set b ⊆ a.
Proof.
intros AO I. intros x X.
apply bunionE in X as [X|X].
- apply AO with (x:=b); assumption.
- apply single_el in X. now subst x.
Qed.

Lemma zero_set_succ_set_disjoint a : zero_set <> succ_set a.
Proof.
  intros H. enough (a ∈ zero_set) as H0 by now apply zf_existence in H0.
  rewrite H. apply succ_set_el.
Qed.

Lemma in_succ_set_iff a : ∀ x, x ∈ succ_set a ↔ x = a ∨ x ∈ a.
Proof.
  intros x. unfold succ_set. split; intros Hel.
  - apply bunionE in Hel as [Hel | Hel]; [eauto | ]. apply single_el in Hel. eauto.
  - destruct Hel as [-> | Hel].
    + apply bunionI2, single_el; easy.
    + now apply bunionI1.
Qed.

Lemma succ_set_injective a b : succ_set a = succ_set b → a = b.
Proof.
  revert a b.
  enough (∀ a b, succ_set a = succ_set b → a ⊆ b).
  { intros a b H1. apply zf_extensionality. split; now apply H. }
  intros a b Heq.
  intros x Hel.
  enough (x ∈  succ_set b).
  { apply in_succ_set_iff in H as [-> | H]; [ | easy].
    apply zf_extensionality in Heq as [H1 H2].
    enough (a ∈ succ_set b).
    { apply in_succ_set_iff in H as [-> | H]; [now apply one_cycles in Hel | exfalso; eapply two_cycles; eauto]. }
    eapply H1. apply in_succ_set_iff. now left.
  }
  rewrite <- Heq. apply in_succ_set_iff. now right.
Qed.

Lemma succ_set_fun f A B: function f A (succ_set B) → B ∉ ran f → function f A B.
Proof.
intros I I'. specialize (fun_ran_subs f A (succ_set B) I). intros J.
apply fun_ran in I. apply fun_expand with (B:=ran f); trivial.
intros y Y. specialize (J y Y). apply bunionE in J as [J|J]; trivial.
exfalso. apply single_el in J. subst y. now apply I'.
Qed.

Lemma succ_set_trans A x: x ∈ A → x ∈ succ_set A.
Proof.
apply succ_set_subset.
Qed.

Lemma elorder_subs A A' a b: A' ⊆ A → (a,b) ∈ elorder A' → (a,b) ∈ elorder A.
Proof.
intros I I'. apply zf_specification in I' as [I' I'']. apply zf_specification. split; eauto.
apply (product_subs1 A A' A') in  I'; eauto. apply (product_subs2 A A' A) in I'; eauto.
Qed.

Lemma elorder_succ_set A a b: (a,b) ∈ elorder A → (a,b) ∈ elorder (succ_set A).
Proof.
intros I. apply (elorder_subs (succ_set A) A); eauto using succ_set_subset.
Qed.

Lemma el_su A A' a b: (a,b) ∈ elorder A → a ∈ A' → b ∈ A' → (a,b) ∈ elorder A'.
Proof.
intros I J J'. apply elorder_el; eauto. apply zf_specification in I as [I I'].
now rewrite pi1_cor pi2_cor in I'.
Qed.

Lemma elorder_trans a x y z: transitive (elorder a) → x ∈ a → y ∈ a → z ∈ a →
  x ∈ y → y ∈ z → x ∈ z.
Proof.
intros I X Y Z J1 J2. specialize (I x y z).
apply zf_specification in I as [_ I]; eauto using elorder_el.
now rewrite pi1_cor pi2_cor in I.
Qed.

Lemma elorder_worder M M': M' ⊆ M → wordering (elorder M) M → wordering (elorder M') M'.
Proof.
intros I J. generalize (elorder_res M' M I). intros H.
rewrite <- H. now apply worder_subs with (A:=M).
Qed.

Lemma ordinal_el a a': ordinal a → a' ∈ a → ordinal a'.
Proof.
intros [str [[reo [ass [tra lin]]] ex]]. intros I. split.
- intros v V u U. assert (J: v ∈ a) by by epose proof (str a' I v); eauto.
  assert (H: u ∈ a) by by epose proof (str v J u); eauto. eauto using elorder_trans.
- apply (elorder_worder a); eauto. repeat split; eauto.
Qed.

Lemma ordinal_eltrans a x: ordinal a → x ∈ a → stransitive x.
Proof.
intros I J. now apply (ordinal_el a x I) in J as [J _].
Qed.

Lemma ordinal_subs x y: ordinal x → ordinal y → x <> y → x ⊆ y → x ∈ y.
Proof.
intros I1 I2 J1 J2. assert (YWF: wfounded (elorder y) y) by now destruct I2 as [_[_ wf]].
destruct (YWF (y\x)) as [l [H1 H2]]; eauto using spec_subs.
- now apply (comp_nempty x y).
- cut (x = l); try (intros I; rewrite I; now apply spec_subs in H1).
  apply zf_specification in H1 as [H1 H1'].
  assert (LO: ordinal l) by eauto using ordinal_el. apply zf_extensionality; split.
+ intros d I. destruct (classic (d ∈ l)); eauto. exfalso.
  destruct I1 as [I1 _]. destruct I2 as [_[[_[_[_ lin]]]_]].
  destruct (lin d l) as [J|[J|J]]; eauto.
* apply elorder_element in J. now apply H.
* apply elorder_element in J. apply H1'. by epose proof (I1 d I); eauto.
* subst d. now apply H.
+ destruct (classic (l ⊆ x)); eauto. exfalso. apply subs_comp in H as [d H].
  destruct I2 as [str [[_ [ass _]] _]].
  assert (irr: irreflexive (elorder y)) by now apply asym_irref.
  apply zf_specification in H as [H H']. destruct (H2 d) as [I|I].
* apply zf_specification. split; eauto. now apply (str l H1).
* apply (ass l d I). apply elorder_el; eauto. now apply (str l H1).
* subst d. apply (irr l). apply elorder_el; eauto.
Qed.



(** ** Ordering Properties *)

Lemma ordinal_nel a: ordinal a → a ∉ a.
Proof.
intros [str [[reo [ass [tra lin]]] wf]]. intros I.
assert (IRR: irreflexive (elorder a)) by now apply asym_irref.
apply (IRR a). now apply elorder_el.
Qed.

Lemma ordinal_trans x y z: ordinal x → ordinal y → ordinal z → x ∈ y → y ∈ z → x ∈ z.
Proof.
intros I1 I2 I3 J1 J2. destruct I3 as [T _]. exact (T y J2 x J1).
Qed.

Lemma ordinal_anti x y: ordinal x → ordinal y → x ∈ y → y ∉ x.
Proof.
intros I1 I2 J1 J2. assert (T: stransitive x).
- now destruct I1.
- specialize (T y J2 x J1). now apply (ordinal_nel x).
Qed.

Lemma ordinal_inter x y: ordinal x → ordinal y → ordinal (x ∩ y).
Proof.
intros I1 I2. split.
- intros a I. apply binterE in I as [J1 J2]. destruct I1 as [I1 _]. destruct I2 as [I2 _].
  specialize (I1 a J1). specialize (I2 a J2). intros x' I. apply binterI; eauto.
- apply (elorder_worder x).
+ apply binter_subs1.
+ destruct I1 as [_ I1]. assumption.
Qed.

Lemma ordinal_linear x y: ordinal x → ordinal y → x ∈ y ∨ x = y ∨ y ∈ x.
Proof.
intros I1 I2. pose (int := binter_set x y).
assert (J1: int ⊆ x) by eauto using binter_subs1.
assert (J2: int ⊆ y) by eauto using binter_subs2.
assert (IO: ordinal int) by eauto using ordinal_inter.
destruct (classic (int = x)) as [I|I], (classic (int = y)) as [J|J].
- right. left. rewrite <- I. rewrite J. reflexivity.
- apply binter_eq1 in I. destruct (classic (x=y)); eauto. left.
  apply ordinal_subs; eauto.
- apply binter_eq2 in J. destruct (classic (x=y)); eauto. right. right.
  apply ordinal_subs; eauto.
- exfalso. apply (ordinal_nel int); eauto.
  assert (H1: int ∈ x) by eauto using ordinal_subs.
  assert (H2: int ∈ y) by eauto using ordinal_subs.
  now apply binterI.
Qed.

Lemma elorder_linear M: (∀ a, a ∈ M → ordinal a) → linear (elorder M) M.
Proof.
intros I x y X Y. destruct (ordinal_linear x y) as [J|[J|J]]; eauto.
- left. now apply elorder_el.
- right. left. now apply elorder_el.
Qed.

Lemma ordinal_wfounded (M: set): (∀ a, a ∈ M → ordinal a) → M ≠ ∅ →
  ∃ a, a ∈ M ∧ ∀ b, b ∈ M → a ∈ b ∨ a = b.
Proof.
intros I J. apply empty_el in J as [a A].
destruct (classic (binter_set a M = empty)).
- exists a. split; trivial. intros b B.
  destruct (ordinal_linear a b (I a A) (I b B)) as [J|[J|J]].
+ now left.
+ now right.
+ exfalso. apply (empty_el (binter_set a M)); eauto. exists b. now apply binterI.
- assert (OA: ordinal a) by eauto.
  assert (J: wfounded (elorder a) a); first by destruct OA as [_[]].
  specialize (J (binter_set a M) (binter_subs1 a M) H). destruct J as [x [H1 H2]].
  exists x. split; first by apply binterE in H1 as []. apply binterE in H1 as [H1 H1'].
  intros b B. destruct (elorder_linear M I x b H1' B) as [J|[J|J]].
+ apply elorder_element in J. now left.
+ apply zf_specification in J as [J J']. rewrite pi1_cor pi2_cor in J'.
  destruct OA as [TA _]. specialize (TA x H1 b J'). destruct (H2 b); eauto using binterI.
  left. apply zf_specification in H0 as [_ H0]. now rewrite pi1_cor pi2_cor in H0.
+ now right.
Qed.



(** ** Sets of Ordinals are Wellordered *)

Lemma ordinal_set_asym M: (∀ a, a ∈ M → ordinal a) → asymmetric (elorder M).
Proof.
intros I x y. intros J H.
apply elorder_el' in J as [J1[J2 J3]].
apply elorder_el' in H as [H1[H2 H3]].
apply (ordinal_anti x y); eauto.
Qed.

Lemma ordinal_set_trans M: (∀ a, a ∈ M → ordinal a) → transitive (elorder M).
Proof.
intros I x y z J H.
apply elorder_el' in J as [J1[J2 J3]].
apply elorder_el' in H as [H1[H2 H3]].
apply elorder_el; eauto.
apply (ordinal_trans x y); eauto.
Qed.

Lemma ordinal_set_wf M: (∀ a, a ∈ M → ordinal a) → wfounded (elorder M) M.
Proof.
intros I N J1 J2. destruct (ordinal_wfounded N) as [min [N1 N2]]; trivial.
- intros a A. apply I. now apply J1.
- exists min. split; trivial. intros a A. destruct (N2 a A) as [H|H].
+ left. apply elorder_el; auto.
+ now right.
Qed.

Theorem ordinal_set M: (∀ a, a ∈ M → ordinal a) → wordering (elorder M) M.
Proof.
intros I. repeat split.
- apply spec_subs.
- now apply ordinal_set_asym.
- now apply ordinal_set_trans.
- now apply elorder_linear.
- now apply ordinal_set_wf.
Qed.

Corollary succ_set_ordinal a: ordinal a → ordinal (succ_set a).
Proof.
intros I. split.
- destruct I as [str _]. intros x I. apply bunionE in I as [I|I].
+ eauto using succ_set_subs.
+ apply single_el in I. subst x. apply succ_set_subset.
- apply ordinal_set. intros x J. apply bunionE in J as [J|J].
+ apply (ordinal_el a); eauto.
+ apply single_el in J. now subst x.
Qed.

Lemma el_succ_set_eq_el b a : ordinal a → b ∈ a → succ_set b = a ∨ succ_set b ∈ a.
Proof.
  intros Hord Hel. specialize (ordinal_el _ _ Hord Hel) as Hordb.
  specialize (succ_set_ordinal _ Hordb) as Hordb'.
  destruct (ordinal_linear _ _ Hord Hordb') as [H1 | [H1 | H1]];[ | eauto | eauto].
  exfalso. apply bunionE in H1. destruct H1 as [H1 | H1].
  - eapply two_cycles; eauto.
  - apply single_el in H1. rewrite H1 in Hel. now apply one_cycles in Hel.
Qed.

Corollary ordinal_union (M: set): (∀ a, a ∈ M → ordinal a) → ordinal (union_set M).
Proof.
intros I. split.
- intros a A c C. apply zf_union in A as [b [B1 B2]].
  specialize (I b B2). apply zf_union. exists b. split; trivial.
  assert (AB: a ⊆ b) by now apply I. now apply AB.
- apply ordinal_set. intros a A. apply zf_union in A as [b [B1 B2]].
  specialize (I b B2). now apply ordinal_el with (a:=b).
Qed.

(*we can obtain an ordinal bounding every ordinal of a set S *)
Lemma ordinal_union_el_succ_set S : (∀ a, a ∈ S → ordinal a) → ∀ a, a ∈ S → a ∈ succ_set (union_set S).
Proof.
  intros H a Hel.
  (* either a is the largest ordinal of S or there exists a larger ordinal *)
  destruct (classic (∃ b, b ∈ S ∧ a ∈ b)) as [Hlarger | Hmax].
  - apply bunionI1. apply zf_union. destruct Hlarger as (b & H1 & H2); eauto.
  - apply bunionI2. apply single_el.
    apply zf_extensionality. split.
    + intros x H1. apply zf_union. exists a. eauto.
    + intros x H1. apply zf_union in H1 as (c & H2 & H3).
      specialize (H c H3) as Hordc.
      specialize (H a Hel) as Horda.
      destruct (ordinal_linear a c Horda Hordc) as [H0 | [H0 | H0]].
      * exfalso; apply Hmax. eauto.
      * rewrite H0. apply H2.
      * eapply ordinal_trans; [ | apply Hordc | apply Horda | apply H2 | apply H0].
        eapply ordinal_el; [apply Hordc | apply H2].
Qed.

Corollary ordinal_bunion a b: ordinal a → ordinal b → ordinal (a ∪ b).
Proof.
intros AO BO. apply ordinal_union. intros x X.
apply zf_pair in X as [X|X]; now subst x.
Qed.

Corollary ordinal_noset: ¬ ∃ O: set, ∀ a, (ordinal a → a ∈ O) ∧ (a ∈ O → ordinal a).
Proof.
intros [O I].
assert (OO: ordinal O).
- split.
+ intros a A b B. apply I. apply ordinal_el with (a:=a); trivial. now apply I.
+ apply ordinal_set. intros a A. now apply I.
- apply (ordinal_nel O); trivial. now apply I.
Qed.

Corollary ordinals_nosubset: ¬ ∃ O: set, ∀ a, ordinal a → a ∈ O.
Proof.
intros [S I]. pose (O:=specification_set S (λ a, ordinal a)).
apply ordinal_noset. exists O. intros a. split; intros J.
- apply zf_specification. split; trivial. now apply I.
- apply zf_specification in J as [_ J]. assumption.
Qed.

Definition is_limit_ordinal a := a = ⋃ a ∧ ∀ a', a' ∈ a → ordinal a'.
Definition is_succ_set_ordinal a := ∃ b, ordinal b ∧ a = succ_set b.

Hint Unfold is_limit_ordinal is_succ_set_ordinal : core.

Lemma succ_set_not_el a : not (succ_set a ∈  a).
Proof.
  intros H. eapply two_cycles. split; first by apply H. apply succ_set_el.
Qed.

Lemma ord_types a : ordinal a → a = ∅ ∨ is_succ_set_ordinal a ∨ is_limit_ordinal a.
Proof.
  intros Hord.
  destruct (classic (a = ∅)) as [H1 | Hne]; [now left | right ].
  destruct (classic (is_succ_set_ordinal a)) as [H1 | Hns]; [now left | right].
  split. 2: { intros a' Hel. eapply ordinal_el; eauto. }
  pose (b := ⋃ a). assert (ordinal b ∧ (a = b ∨ b ∈ a)) as [H1 H2].
  - assert (ordinal b) as Hordb.
    { eapply ordinal_union. intros a' Hel. eapply ordinal_el; eauto. }
    split; [easy | ].
    destruct (ordinal_linear _ _ Hord Hordb) as [H | [H | H]]; [ | eauto | eauto ].
    exfalso. subst b. apply zf_union in H. destruct H as (A & H1 & H2).
    eapply two_cycles; eauto.
  - destruct H2 as [H | H]; [easy | ].
    specialize (el_succ_set_eq_el _ _ Hord H) as [H2 | H2].
    + exfalso; apply Hns. eauto.
    + (* b is the largest ordinal < a *)
      assert (∀ c, c ∈ a → c = b ∨ c ∈ b) as Hgreatest.
      {
        intros c Hel. assert (Hordc : ordinal c). { eapply ordinal_el; first by apply Hord. eauto. }
        apply el_union_subs in Hel.
        destruct (classic (c = b)) as [Heq | Hneq]; [now left | ].
        right. apply ordinal_subs; eauto.
      }
      apply Hgreatest in H2 as [H2 | H2].
      { unfold succ_set in H2. enough (b ∈ b) by (exfalso; eapply one_cycles; eauto).
        rewrite <- H2 at 2. apply bunionI2, single_el. reflexivity.
      }
      now apply succ_set_not_el in H2.
Qed.

Lemma succ_set_smallest a b: b ∈ a → a ∈ succ_set b → False.
Proof.
  intros H H1. apply bunionE in H1 as [H1 | H1].
  - eapply two_cycles; eauto.
  - apply single_el in H1. rewrite H1 in H. now apply one_cycles in H.
Qed.

Lemma limit_not_succ_set a : is_limit_ordinal a → not (is_succ_set_ordinal a).
Proof.
  intros [Heq H] [b [H1 H2]].
  rewrite H2 in Heq. clear H2. enough (b ∈ succ_set b ∧ not (b ∈ ⋃ (succ_set b))) as H0.
  { rewrite {1}Heq in H0. destruct H0. by apply H2. }
  split.
  - apply succ_set_el.
  - intros H2. unfold succ_set in H2. apply zf_union in H2 as (B & H2 & H3).
    apply bunionE in H3 as [H3 | H3].
    + eapply two_cycles; eauto.
    + apply single_el in H3. rewrite H3 in H2. now apply one_cycles in H2.
Qed.

Lemma limit_ord_el_succ_set a : is_limit_ordinal a → ∀ b, b ∈ a → succ_set b ∈ a.
Proof.
  intros [Heq H] b Hel.
  destruct (ordinal_linear (succ_set b) a) as [Hl | [Hl | Hl]].
  - apply succ_set_ordinal. apply H, Hel.
  - rewrite Heq. apply ordinal_union, H.
  - easy.
  - exfalso. eapply limit_not_succ_set.
    + eauto.
    + exists b. split; [ | eauto]. apply H, Hel.
  - exfalso. eapply succ_set_smallest; first by apply Hel. now apply Hl.
Qed.

End set_ordinals.
