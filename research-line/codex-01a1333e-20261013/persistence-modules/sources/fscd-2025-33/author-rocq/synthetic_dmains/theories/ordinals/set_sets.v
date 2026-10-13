(** * Formalisation of basic ZF *)
(** This file has been adapted from Dominik Kirst's Bachelor Thesis
    "Formalised Set Theory: Well-Orderings and the Axiom of Choice",
    see https://www.ps.uni-saarland.de/~kirst/bachelor.php
*)


(** This formalisation is part of Dominik Kirst's Bachelor Thesis, submitted Sep 2014.
    It was implemented at the Programming Systems Lab in Saarbrücken, headed by Prof. Gert Smolka.
    We present the development of a ZF set theory, introduce the notions of orderings,
    functions and ordinals and conclude the equivalence of Well-Ordering Theorem and Axiom of Choice.
    We do not provide excessive commentary in the source files
    and refer to the explanations given in the thesis. **)

(** import of necessary libraries **)

Require Import Stdlib.Logic.Classical_Prop.
From SynthDom.ordinals Require Export set_model.

Set Universe Polymorphism.
Unset Universe Minimization ToSet.


(** ** Basic Framework with Element- and Subset-Relation *)
Section set_theory.
  Implicit Types (A B C: set).

(* we do not want the definitions to unfold / be reduced automatically in proof scripts *)
Local Open Scope zf_scope.
Arguments union_set : simpl never.
Arguments replacement_set : simpl never.
Arguments desc_set: simpl never.
Arguments upair_set : simpl never.
Arguments specification_set : simpl never.
Arguments power_set : simpl never.

Lemma desc_set_unique P A: (exists! x, P x) → P A → A = desc_set P.
Proof.
intros I1 I2. specialize (zf_desc _ I1). intros J. destruct I1 as [x [_ I1]].
rewrite <- (I1 A I2). rewrite <- (I1 (desc_set P) J). reflexivity.
Qed.

Lemma desc_set_P P x: (exists! x, P x) → x = desc_set P → P x.
Proof.
intros I1 I2. apply zf_desc in I1.
by rewrite I2.
Qed.

(** following
  Chad Brown, "Three Forms of Replacement" at https://www.ps.uni-saarland.de/settheory.html
  we can derive a relational form of replacement_set which allows us to define non-computable things more comfortably *)
Definition total_replacement_set (X : set) (P : set → set → Prop) := (λ x, desc_set (P x)) @ X.
Lemma TotalReplacement X (P : set → set → Prop) : (∀ x, x ∈ X → exists! y, P x y) → ∀ y, y ∈ total_replacement_set X P ↔ (∃ x, x ∈ X ∧ P x y).
Proof.
  intros Htotal y. unfold total_replacement_set.
  destruct (zf_replacement (λ x, desc_set (P x)) X y) as [H1 H2]. split.
  - intros H%H1. destruct H as (x & H0 & H). exists x. split; [easy | ].
    apply desc_set_P; eauto.
  - intros (x & H3 & H4).
    apply H2. exists x. split; [easy | ].
    apply desc_set_unique; eauto.
Qed.

(** ** Some General Statements *)

Lemma subseq A: A ⊆ A.
Proof.
intros x I. assumption.
Qed.

Lemma subs_trans A B C: A ⊆ B → B ⊆ C → A ⊆ C.
Proof.
intros I I' x J. eauto.
Qed.

Lemma empty_subs A: ∅ ⊆ A.
Proof.
intros x I. apply zf_existence in I. contradiction I.
Qed.

Lemma empty_el A: A ≠ ∅ ↔ ∃ x, x ∈ A.
Proof.
split; intros I.
- destruct (classic (∃ x, x∈ A)); trivial. exfalso. apply I, zf_extensionality. split.
  + intros a Hel. exfalso; apply H; eauto.
  + intros x Hel. by apply zf_existence in Hel.
- intros H. subst A. destruct I. apply zf_existence in H. assumption.
Qed.

Lemma subs_el A B: A ⊈ B ↔ ∃ x, x ∈ A ∧ x ∉ B.
Proof.
split; intros I.
- destruct (classic (∃ x, x ∈ A ∧ x ∉ B)); eauto.
  exfalso. apply I. intros x J. destruct (classic (x ∈ B)); eauto.
  exfalso. apply H. exists x. eauto.
- destruct I as [x[I1 I2]]. intros J. apply I2. by apply J.
Qed.

Lemma extenE A B: A = B → A ⊆ B ∧ B ⊆ A.
Proof.
intros I. rewrite I. split; apply subseq.
Qed.

Lemma upair1 A B: A ∈ upair_set A B.
Proof.
apply zf_pair. left. reflexivity.
Qed.

Lemma upair2 A B: B ∈ upair_set A B.
Proof.
apply zf_pair. right. reflexivity.
Qed.

Lemma spec_subs A P: specification_set A P ⊆ A.
Proof.
intros x. intros I. apply zf_specification in I as [I J]. assumption.
Qed.

Lemma spec_equal A P: specification_set A P = A ↔ (∀ x, x ∈ A → P x).
Proof.
split; intros I.
- rewrite <- I. intros x H. by apply zf_specification in H as [].
- apply zf_extensionality; split; first by eauto using spec_subs.
  intros x J. apply zf_specification. eauto.
Qed.

Lemma spec_empty P: specification_set ∅ P = ∅.
Proof.
apply zf_extensionality; split; eauto using empty_subs. intros x I.
apply zf_specification in I as [I _]. assumption.
Qed.

Lemma el_union_subs A B : A ∈ B → A ⊆ ⋃ B.
Proof.
  intros H c Hel. apply zf_union. eauto.
Qed.

Lemma power_set_trans A B C: A ⊆ B → B ∈ power_set C → A ∈ power_set C.
Proof.
intros I J. apply zf_power.
apply (@subs_trans A B C); auto.
by apply zf_power in J.
Qed.

Lemma one_cycles A: A ∉ A.
Proof.
  revert A. apply eps_ind.
  intros X H H1. by apply (H X).
Qed.

Lemma all_set: ¬ ∃ A, ∀ B, B ∈ A.
Proof.
intros [A I]. by apply (@one_cycles A).
Qed.

Lemma russell: ¬ ∃ A, ∀ B, B ∈ A ↔ B ∉ B.
Proof.
  intros [A I]. specialize (I A). tauto.
Qed.

Lemma two_cycles A B : not (A ∈ B ∧ B ∈ A).
Proof.
  revert B. enough (∀ B, B ∈ A → not (A ∈  B)).
  { intros B [H1 H2]. eapply H; eauto. }
  apply eps_ind with (X := A); clear A.
  intros A IH B Hel1 Hel2.
  specialize (IH B Hel1 A Hel2). tauto.
Qed.

(** ** Binary Union, Intersection and Complement Sets *)


Lemma bunionI1 A B x: x ∈ A → x ∈ A ∪ B.
Proof.
intros I. apply zf_union. exists A. split.
- assumption.
- apply zf_pair. left. reflexivity.
Qed.

Lemma bunionI2 A B x: x ∈ B → x ∈ A ∪ B.
Proof.
intros I. apply zf_union. exists B. split.
- assumption.
- apply zf_pair. right. reflexivity.
Qed.

Lemma bunionE A B x: x ∈ A ∪ B → x ∈ A ∨ x ∈ B.
Proof.
intros I. apply zf_union in I as [C I]. destruct I as [I J]. apply zf_pair in J as [J|J].
- left. subst C. assumption.
- right. subst C. assumption.
Qed.

Lemma interI S x: (∀ A, A ∈ S → x ∈ A) → S ≠ ∅ → x ∈ (⋂ S).
Proof.
intros I J. apply zf_specification. split.
- apply zf_union. apply empty_el in J as [A H]. exists A. split; first exact (I A H). assumption.
- assumption.
Qed.

Lemma interE S x: x ∈ (⋂ S) → (∀ A, A ∈ S → x ∈ A) ∧ S ≠ ∅.
Proof.
intros I. apply zf_specification in I as [I J]. split.
- assumption.
- apply zf_union in I as [A [I1 I2]]. intros H. subst S. apply zf_existence in I2. assumption.
Qed.

Lemma binterI A B x: x ∈ A → x ∈ B → x ∈ (A ∩ B).
Proof.
intros I J. apply interI.
- intros C H. apply zf_pair in H as [H|H]; subst C; assumption.
- apply empty_el. exists A. apply zf_pair. left. reflexivity.
Qed.

Lemma binterE A B x: x ∈ (A ∩ B) → x ∈ A ∧ x ∈ B.
Proof.
intros I. apply interE in I as [I J]. split; apply I; apply zf_pair.
- left. reflexivity.
- right. reflexivity.
Qed.

Lemma union_set_empty: ⋃ ∅ = ∅.
Proof.
apply zf_extensionality; split; intros x I.
- apply zf_union in I as [A [I I']]. destruct (zf_existence A I').
- destruct (zf_existence x I).
Qed.

Lemma inter_empty: ⋂ ∅ = ∅.
Proof.
apply zf_extensionality; split; intros x I.
- apply interE in I as [I I']. exfalso. by apply I'.
- destruct (zf_existence x I).
Qed.

Lemma repl_empty R: R @ ∅ = ∅.
Proof.
apply zf_extensionality; split; intros x I.
- apply zf_replacement in I as [A [I I']]. destruct (zf_existence A I).
- destruct (zf_existence x I).
Qed.

Lemma binter_subs1 A B: A ∩ B ⊆ A.
Proof.
intros x I. by apply binterE in I as [I _].
Qed.

Lemma binter_subs2 A B: A ∩ B ⊆ B.
Proof.
intros x I. by apply binterE in I as [_ I].
Qed.

Lemma binter_eq1 A B: A ∩ B = A → A ⊆ B.
Proof.
intros I. rewrite <- I. apply binter_subs2.
Qed.

Lemma binter_eq2 A B: A ∩ B = B → B ⊆ A.
Proof.
intros I. rewrite <- I. apply binter_subs1.
Qed.

Lemma comp_empty A B: A\B = ∅ ↔ A ⊆ B.
Proof.
split.
- intros I. intros x J. destruct (classic (x ∈ B)); eauto.
  exfalso. apply (zf_existence x). rewrite <- I. apply zf_specification. split; eauto.
- intros I. apply zf_extensionality; split; eauto using empty_subs.
  intros x J. apply zf_specification in J as [J J'].
  exfalso. apply J'. by apply (I x).
Qed.

Lemma comp_nempty A B: A ≠ B → A ⊆ B → B\A ≠ ∅.
Proof.
intros J1 J2. destruct (classic (B\A = ∅)); eauto.
exfalso. apply J1. apply zf_extensionality; split; eauto.
intros a I. destruct (classic (a ∈ A)); eauto. exfalso. apply (zf_existence a).
rewrite <- H. apply zf_specification; eauto.
Qed.

Lemma subs_comp A B: A ⊈ B → ∃ x, x ∈ A \ B.
Proof.
intros I. destruct (classic (∃ x, x ∈ A\B)); eauto. exfalso.
apply I. intros x. intros J. destruct (classic (x ∈ B)); eauto. exfalso.
apply H. exists x. apply zf_specification. split; eauto.
Qed.

Lemma bunion_subs1 A B C: C ⊆ A → C ⊆ A ∪ B.
Proof.
intros I x J. apply bunionI1. eauto.
Qed.

Lemma bunion_subs2 A B C: C ⊆ B → C ⊆ A ∪ B.
Proof.
intros I x J. apply bunionI2. eauto.
Qed.



(** ** Singletons and Ordered Pairs, Projection and Cartesian Product *)

Definition opair A B := upair_set (singleton A) (upair_set A B).
Notation "( x , y )" := (opair x y) (at level 0) : zf_scope.

Definition pi1 p := ⋃ (⋂ p).
Definition pi2 p := ⋃ (specification_set (⋃ p) (λ x, x ∈ ⋂ p → ⋃ p = ⋂ p)).
Definition product A B := ⋃ ((λ a, (λ b, (a, b)) @ B) @ A).
Notation "A × B" := (product A B) (at level 53) : zf_scope.


Lemma single_el A B: A = B ↔ A ∈ (singleton B: set).
Proof.
split; intros I.
- rewrite I. apply zf_pair. left. reflexivity.
- apply zf_pair in I as [I|I]; apply I.
Qed.

Lemma single_union_set A: ⋃ (singleton A) = A.
Proof.
apply zf_extensionality; split; intros x I.
- apply zf_union in I as [a [I J]]. apply single_el in J. rewrite <- J. apply I.
- apply zf_union. exists A. split; first apply I. apply single_el. reflexivity.
Qed.

Lemma single_inter A: ⋂ (singleton A) = A.
Proof.
apply zf_extensionality; split; intros x I.
- apply interE in I as [I I']. apply (I A). by apply single_el.
- apply zf_specification.
  split.
  { apply zf_union; exists A. split; first apply I. apply single_el. eauto. }
  intros a J. apply single_el in J. rewrite J. assumption.
Qed.

Lemma opair_single A: (A,A) = singleton(singleton A).
Proof.
reflexivity.
Qed.

Lemma single_opair A B: singleton A ∈ (A,B).
Proof.
apply upair1.
Qed.

Lemma opair_intuni A B: ⋃ (A,B) = ⋂ (A,B) ↔ A = B.
Proof.
split; intros I.
- apply extenE in I as [I I']. symmetry. apply single_el. cut (B ∈ union_set (A,B)).
+ intros J. specialize (I B J). apply interE in I as [I H].
  specialize (I (singleton A)). apply I. apply upair1.
+ apply zf_union. exists (upair_set A B). split; apply upair2.
- rewrite I. rewrite opair_single. by rewrite single_union_set single_inter.
Qed.

Lemma opair_nempty A B: (A,B) ≠ ∅.
Proof.
apply empty_el. exists (singleton A). apply upair1.
Qed.

Lemma pi1_subs1 A B: pi1 (A,B) ⊆ A.
Proof.
intros x I. apply zf_union in I as [a [I J]]. apply interE in J as [J J'].
specialize (J (singleton A) (single_opair A B)). apply single_el in J. by rewrite <- J.
Qed.

Lemma pi1_subs2 A B: A ⊆ pi1 (A,B).
Proof.
intros x I. apply zf_union.
exists A. split; first apply I. apply interI.
- intros a J. apply zf_pair in J as [J|J].
+ rewrite J. by apply single_el.
+ rewrite J. apply upair1.
- apply empty_el. exists (singleton A). apply upair1.
Qed.

Lemma pi1_cor A B: pi1 (A,B) = A.
Proof.
apply zf_extensionality. split.
- apply pi1_subs1.
- apply pi1_subs2.
Qed.

Lemma pi2_subs1 A B: pi2 (A,B) ⊆ B.
Proof.
intros x I.
apply zf_union in I as [a [I J]]. apply zf_specification in J as [J J'].
apply zf_union in J as [b [J H]]. apply zf_pair in H as [H|H].
- subst b. apply single_el in J. subst a. cut (A=B); first by intros H; subst A.
  apply opair_intuni. apply J'. apply interI.
+ intros a H. apply zf_pair in H as [H|H]; subst a; first by apply single_el.
  apply zf_pair. eauto.
+ apply empty_el. exists (singleton A). apply upair1.
- subst b. apply zf_pair in J as [J|J].
+ subst a. cut (A=B); try congruence.
  apply opair_intuni. apply J'. apply interI; eauto using opair_nempty.
  intros a H. apply zf_pair in H as [H|H]; subst a; try by apply single_el. apply upair1.
+ subst a. assumption.
Qed.

Lemma pi2_subs2 A B: B ⊆ pi2 (A,B).
Proof.
intros x I. apply zf_union. exists B. split; trivial. apply zf_specification. split.
- apply zf_union. exists (upair_set A B). split; apply upair2.
- intros J. cut (A=B).
+ intros H. apply opair_intuni. assumption.
+ apply interE in J as [J J']. specialize (J (singleton A) (single_opair A B)).
  apply single_el in J. by rewrite J.
Qed.

Lemma pi2_cor A B: pi2 (A,B) = B.
Proof.
apply zf_extensionality. split.
- apply pi2_subs1.
- apply pi2_subs2.
Qed.

Lemma opair_eq A A' B B': (A,B) = (A',B') ↔ A = A' ∧ B = B'.
Proof.
split; intros I.
- split; first by rewrite <- (pi1_cor A B), <- (pi1_cor A' B'); rewrite I.
  rewrite <- (pi2_cor A B), <- (pi2_cor A' B'). by rewrite I.
- destruct I as [I J]. by rewrite I J.
Qed.

Lemma product_empty1 B: ∅ × B = ∅.
Proof.
unfold product. rewrite repl_empty. by rewrite union_set_empty.
Qed.

Lemma product_empty2 A: A × ∅ = ∅.
Proof.
destruct (classic (A = ∅)); first by rewrite H; apply product_empty1.
apply empty_el in H as [a H].
cut (replacement_set A (λ A : set, replacement_set ∅ (λ B : set, (A,B))) = singleton ∅).
- intros I. unfold product. rewrite I. apply single_union_set.
- apply zf_extensionality; split; intros x I.
+ apply single_el. apply zf_replacement in I as [y [I I']]. rewrite I'. apply repl_empty.
+ apply single_el in I. apply zf_replacement. exists a. split; first assumption.
  by rewrite -> repl_empty.
Qed.

Lemma product_el A B p: p ∈ A × B ↔ ∃ a b, a ∈ A ∧ b ∈ B ∧ p = (a,b).
Proof.
split; intros I.
- apply zf_union in I as [C [I I']]. apply zf_replacement in I' as [a [a' J]]. subst C.
  apply zf_replacement in I as [b [B' I]]. exists a, b. eauto.
- destruct I as [a [b [A' [B' P]]]]. apply zf_union.
  exists (replacement_set B (λ c : set, (a,c))). split.
+ apply zf_replacement. exists b. split; first by apply B'. assumption.
+ apply zf_replacement. exists a. split; first by apply A'. reflexivity.
Qed.

Lemma opair_pi A B a b p: p ∈ A × B → a = pi1 p → b = pi2 p → p = (a,b).
Proof.
intros I PI1 PI2. apply product_el in I as [a' [b' [H [H' J]]]].
subst p. apply opair_eq. split.
- rewrite PI1. by rewrite pi1_cor.
- rewrite PI2. by rewrite pi2_cor.
Qed.

Lemma product_opair x y A B: x ∈ A ∧ y ∈ B ↔ (x,y) ∈ A × B.
Proof.
split; intros I.
- apply product_el. exists x, y. destruct I as [I I']. eauto.
- apply product_el in I as [a [b [I [I' J]]]]. apply opair_eq in J as [J J']. subst x y. eauto.
Qed.

Lemma product_pi1 A B p: p ∈ A × B → pi1 p ∈ A.
Proof.
intros I. apply product_el in I as [a [b [I [I' J]]]].
rewrite J. rewrite pi1_cor. assumption.
Qed.

Lemma product_pi2 A B p: p ∈ A × B → pi2 p ∈ B.
Proof.
intros I. apply product_el in I as [a [b [I [I' J]]]].
rewrite J. rewrite pi2_cor. assumption.
Qed.

Lemma product_pi A B p: p ∈ A × B → pi1 p ∈ A ∧ pi2 p ∈ B.
Proof.
intros I. split; first by eauto using product_pi1. eauto using product_pi2.
Qed.

Lemma product_p A B p: p ∈ A × B → p = (pi1 p, pi2 p).
Proof.
intros I. by apply (opair_pi A B).
Qed.

Lemma product_subs1 A A' B: A' ⊆ A → A' × B ⊆ A × B.
Proof.
intros I p H.
specialize (product_el A' B p). intros [J _]. specialize (J H). destruct J as [a [b [X [Y Z]]]].
apply product_el. exists a, b. repeat split; eauto.
Qed.

Lemma product_subs2 A B B': B ⊆ B' → A ×B ⊆ A × B'.
Proof.
intros I p H.
specialize (product_el A B p). intros [J _]. specialize (J H). destruct J as [a [b [X [Y Z]]]].
apply product_el. exists a, b. repeat split; eauto.
Qed.

Lemma product_subs A A': A' ⊆ A → A' × A' ⊆ A × A.
Proof.
intros I. specialize (product_subs1 A A' A I).
intros J. specialize (product_subs2 A' A' A I).
intros H. by apply (subs_trans (product A' A') (product A' A)).
Qed.

Lemma product_monotone A B C D: A ⊆ C → B ⊆ D → A × B ⊆ C × D.
Proof.
intros I1 I2 p P.
generalize (product_pi A B p P). intros [P1 P2].
generalize (product_p A B p P). intros P3.
apply product_el. exists (pi1 p), (pi2 p).
repeat split; auto.
Qed.

End set_theory.
Notation "( x , y )" := (opair x y) (at level 0) : zf_scope.
Notation "A × B" := (product A B) (at level 53) : zf_scope.
