(** This file has been adapted from the Coq development of the paper

"Large Model Constructions for Second-Order ZF in Dependent Type Theory"
by Dominik Kirst and Gert Smolka, CPP 2018

See https://www.ps.uni-saarland.de/Publications/details/KirstSmolka:2017:Large-Model.html.
*)

(** Aczel's Intensional Model Construction + Extensionalisation using a choice operator*)

From SynthDom Require Export prelude.
Unset Universe Minimization ToSet.


(**  Well-Founded Trees *)
(* Following Aczel 78 and Werner 97 we construct an intensional type of sets *)
Section aczel_trees.
Set Universe Polymorphism.
Polymorphic Inductive Acz@{i} : Type :=
| Asup : ∀ A : Type@{i}, (A → Acz) → Acz.

Definition Atypeof '(Asup A f) := A.
Definition Aelements s : (Atypeof s) → Acz :=
  match s with
  Asup A f => f
  end.

Fixpoint Aeq@{i} (s t: Acz@{i}) :=
  match s, t with
  | Asup A f, Asup B g =>
  (∀ a, ∃ b, Aeq (f a) (g b)) ∧ (∀ b, ∃ a, Aeq (f a) (g b))
  end.

Lemma Aeq_ref s :
  Aeq s s.
Proof.
  induction s as [A f IH]. simpl. split.
  - intros a. exists a. by apply IH.
  - intros a. exists a. by apply IH.
Qed.


Lemma Aeq_sym s t :
  Aeq s t → Aeq t s.
Proof.
revert t. induction s as [A f IH].
intros [B g]. simpl. intros [H1 H2]. split.
- intros b. destruct (H2 b) as [a H3]. exists a. by apply IH.
- intros a. destruct (H1 a) as [b H3]. exists b. by apply IH.
Qed.

Lemma Aeq_tra s t u :
  Aeq s t → Aeq t u → Aeq s u.
Proof.
  revert t u. induction s as [A f IH].
  intros [B g] [C h]. simpl. intros [H1 H2] [H3 H4]. split.
  - intros a. destruct (H1 a) as [b H5]. destruct (H3 b) as [c H6].
  exists c. by apply IH with (t := (g b)).
  - intros c. destruct (H4 c) as [b H5]. destruct (H2 b) as [a H6].
  exists a. by apply IH with (t := (g b)).
Qed.

Hint Resolve Aeq_ref Aeq_sym Aeq_tra : core.

Global Instance aeq_equiv :
  Equivalence Aeq.
Proof.
  constructor; eauto.
Qed.

Definition Ain s '(Asup A f) := ∃ a, Aeq s (f a).
Definition ASubq s t := ∀ u, Ain u s → Ain u t.

Lemma Ain_Asup A f a : Ain (f a) (Asup A f).
Proof.
  simpl. exists a. by apply Aeq_ref.
Qed.

Lemma Ain_Alements s t : Ain s t → ∃ a : (Atypeof t), Aeq s (Aelements t a).
Proof.
  destruct t as [A f]. intros [a H]. by exists a.
Qed.

Lemma Aelements_Ain (s : Acz) (a : Atypeof s) : Ain (Aelements s a) s.
Proof.
  destruct s as [A f]; simpl in *. by exists a.
Qed.

Lemma Ain_mor s s' t t' :
  Aeq s s' → Aeq t t' → Ain s t → Ain s' t'.
Proof.
  intros H1 H2 H3.
  destruct t as [B1 g1]. simpl in H3. destruct H3 as [b1 H3].
  destruct t' as [B2 g2]. simpl. simpl in H2. destruct H2 as [H2 _].
  destruct (H2 b1) as [b2 H4]. exists b2.
  rewrite <- H4. by rewrite <- H1.
Qed.

Global Instance Ain_proper :
  Proper (Aeq ==> Aeq ==> iff) Ain.
Proof.
  intros s s' H1 t t' H2. split; intros H.
  - by eapply Ain_mor.
  - apply Aeq_sym in H1. apply Aeq_sym in H2.
    by eapply Ain_mor.
Qed.

Global Instance ASubq_proper :
Proper (Aeq ==> Aeq ==> iff) ASubq.
Proof.
intros s s' H1 t t' H2. split; intros H.
- intros u. rewrite <- H1, <- H2. apply H.
- intros u. rewrite H1 H2. apply H.
Qed.



(** Definition of Set Operations *)
Definition AEmpty :=
  Asup False (λ a,  match a with end).

Definition Aupair X Y :=
  Asup bool (λ a, if a then X else Y).

Definition Aunion '(Asup A f) :=
  Asup (sigT (λ (a : A), (Atypeof (f a)))) (λ p, let (a, b) := p in Aelements (f a) b).

Definition Apower '(Asup A f) :=
  Asup (A → Prop) (λ P, Asup (sig P) (λ p, let (a, _) := p in f a)).

Definition Asep '(Asup A f) (P : Acz → Prop) :=
  Asup (sig (λ a, P (f a))) (λ p, let (a, _) := p in f a).

Definition Arepl (F : Acz → Acz) '(Asup A f) :=
  Asup A (λ a, F (f a)).


(* Extensionality *)
Lemma Aeq_ext s t :
  ASubq s t → ASubq t s → Aeq s t.
Proof.
  destruct s as [A f], t as [B g].
  intros H1 H2. simpl. split.
  - intros a. destruct (H1 (f a) (Ain_Asup _ f a)) as [b H3]. by exists b.
  - intros b. destruct (H2 (g b) (Ain_Asup _ g b)) as [a H3]. by exists a.
Qed.

Lemma Aeq_ASubq s t :
  Aeq s t → ASubq s t.
Proof.
  destruct s as [A f], t as [B g]. intros [H _] z [a Z].
  destruct (H a) as [b I]. exists b. eauto.
Qed.

(** Proof of Intensional Axioms *)

(* Foundation *)
Lemma Aeq_acc_mor s t:
  Aeq s t → Acc Ain s → Acc Ain t.
Proof.
  revert t. induction s as [A f IH].
  intros [B g] H1 H2. constructor.
  intros u [b H3]. destruct H1 as [_ H1].
  destruct (H1 b) as [a H4]. apply (IH a).
  - by rewrite H4.
  - apply H2. apply Ain_Asup.
Qed.

Lemma Ain_wf: well_founded Ain.
Proof.
  intros s; induction s as [A f IH].
  constructor. intros t [a H].
  symmetry in H. by eapply Aeq_acc_mor, IH.
Qed.

(* Empty *)
Lemma AEmptyAx s : ¬ Ain s AEmpty.
Proof.
  by intros [t H].
Qed.

(* Unordered Pairs *)
Lemma AupairAx s t u:
  Ain u (Aupair s t) ↔ Aeq u s \/ Aeq u t.
Proof.
  split; intros H.
  - destruct H as [[] H]; auto.
  - destruct H as [H|H]; [by exists true | by exists false].
Qed.

Lemma Aupair_mor s s' t t' u :
  Aeq s s' → Aeq t t' → Ain u (Aupair s t) → Ain u (Aupair s' t').
Proof.
  intros H1 H2 H. apply AupairAx.
  rewrite <- H1, <- H2. by apply AupairAx in H.
Qed.

Global Instance Aupair_proper :
  Proper (Aeq ==> Aeq ==> Aeq) Aupair.
Proof.
  intros s s' H1 t t' H2. apply Aeq_ext; intros z H.
  - by eapply Aupair_mor.
  - symmetry in H1, H2. by eapply Aupair_mor.
Qed.

(* Union *)
Lemma AunionAx s u :
  Ain u (Aunion s) ↔ ∃ t, Ain t s /\ Ain u t.
Proof.
  split; intros H; destruct s as [A f].
  - destruct  H as [[a b] H]. exists (f a). split.
  + by exists a.
  + destruct (f a) as [C h]; simpl in *. by exists b.
  - destruct H as [[B g][[a Z1][b Z2]]].
  apply Aeq_ASubq in Z1.
  specialize (Z1 (g b) (Ain_Asup _  g b)).
  apply Ain_Alements in Z1 as [c H].
  exists (existT a c). by etransitivity.
Qed.

Lemma Aunion_mor s s' u :
  Aeq s s' → Ain u (Aunion s) → Ain u (Aunion s').
Proof.
  intros H1 H2. apply AunionAx in H2 as [t H2].
  move: H2; rewrite H1 =>H2. apply AunionAx. by exists t.
Qed.

Global Instance Aunion_proper :
  Proper (Aeq ==> Aeq) Aunion.
Proof.
  intros s s' H1. apply Aeq_ext; intros z H.
  - by eapply Aunion_mor.
  - symmetry in H1. by eapply Aunion_mor.
Qed.

(* Power *)
Lemma ApowerAx s t :
  Ain t (Apower s) ↔ ASubq t s.
Proof.
  split; intros H; destruct s as [A f].
  - destruct H as [P H].
  intros u Z. apply Aeq_ASubq in H.
  destruct (H u Z) as [[a PA] I]. by exists a.
  - exists (λ a, Ain (f a) t). apply Aeq_ext; intros z Z.
  + destruct t as [B g], Z as [b H1].
    destruct (H (g b) (Ain_Asup _ g b)) as [a J].
    assert (H2: Ain (f a) (Asup B g)) by (exists b; auto).
    exists (exist _ a H2). eauto.
  + destruct Z as [[a YA] H1 % Aeq_sym].
    by eapply Ain_mor.
Qed.

Lemma Apower_mor s s' t :
  Aeq s s' → Ain t (Apower s) → Ain t (Apower s').
Proof.
  intros H1 H2. apply ApowerAx.
  rewrite <- H1. by apply ApowerAx.
Qed.

Global Instance Apower_proper :
  Proper (Aeq ==> Aeq) Apower.
Proof.
  intros s s' H1. apply Aeq_ext; intros z H.
  - by eapply Apower_mor.
  - symmetry in H1. by eapply Apower_mor.
Qed.

(* Separation *)
Definition cres {X} (equiv : X → X → Prop) (P : X → Prop) :=
  ∀ x x', equiv x x' → P x → P x'.

Lemma AsepAx (P : Acz → Prop) s t :
  cres Aeq P → Ain t (Asep s P) ↔ Ain t s /\ P t.
Proof.
  intros HP. split; intros H; destruct s as [A f].
  - destruct H as [[a PA]H].
  split; eauto. by exists a.
  - destruct H as [[a H]PY].
  assert (PA : P (f a)) by by apply (HP t).
  by exists (exist _ a PA).
Qed.

Lemma Asep_mor (P P' : Acz → Prop) s s' t :
  cres Aeq P → cres Aeq P' → (∀ s, P s ↔ P' s)
  → Aeq s s' → Ain t (Asep s P) → Ain t (Asep s' P').
Proof.
  intros H1 H2 H3 H4 H5. apply AsepAx; trivial.
  rewrite <- H3, <- H4. apply AsepAx; trivial.
Qed.

Lemma Asep_proper' (P P' : Acz → Prop) s s' :
  cres Aeq P → cres Aeq P' → (∀ s, P s ↔ P' s)
  → Aeq s s' → Aeq (Asep s P) (Asep s' P').
Proof.
  intros H1 H2 H3 H4. apply Aeq_ext; intros z Z.
  - apply (Asep_mor _ _ _ _ _ H1 H2 H3 H4); assumption.
  - apply (@Asep_mor P' P s' s); naive_solver.
Qed.

Lemma Asep_proper (P : Acz → Prop) s s' :
  cres Aeq P → Aeq s s' → Aeq (Asep s P) (Asep s' P).
Proof.
  intros H1 H2. apply (@Asep_proper' P P); naive_solver.
Qed.

(* Functional Replacement *)
Definition fres {X} (equiv : X → X → Prop) (F : X → X) :=
  ∀ x x', equiv x x' → equiv (F x) (F x').

Lemma AreplAx F s u :
  fres Aeq F → Ain u (Arepl F s) ↔ ∃ t, Ain t s /\ Aeq u (F t).
Proof.
  intros HF. split; intros H; destruct s as [A f].
  - destruct H as [a H]. exists (f a).
  split; trivial. apply Ain_Asup.
  - destruct H as [z[[a H] Z]].
  exists a. apply HF in H; try by exists a.
  by rewrite Z H.
Qed.

Lemma Arepl_mor (F F' : Acz → Acz) s s' u :
  fres Aeq F → fres Aeq F' → (∀ s, Aeq (F s) (F' s))
  → Aeq s s' → Ain u (Arepl F s) → Ain u (Arepl F' s').
Proof.
  intros H1 H2 H3 H4 H5. apply AreplAx; trivial.
  apply AreplAx in H5 as [y H]; trivial.
  exists y. by rewrite <- H3, <- H4.
Qed.

Lemma Arepl_proper' (F F' : Acz → Acz) s s' :
  fres Aeq F → fres Aeq F' → (∀ s, Aeq (F s) (F' s))
  → Aeq s s' → Aeq (Arepl F s) (Arepl F' s').
Proof.
  intros H1 H2 H3 H4. apply Aeq_ext; intros z Z.
  - apply (Arepl_mor _ _ _ _ _ H1 H2 H3 H4); assumption.
  - apply (@Arepl_mor F' F s' s); auto.
Qed.

Lemma Arepl_proper (F : Acz → Acz) s s' :
  fres Aeq F → Aeq s s' → Aeq (Arepl F s) (Arepl F s').
Proof.
  intros H1 H2. by apply Arepl_proper'.
Qed.

(** Infinity *)
Fixpoint Aenc_inf n  :=
  match n with
  | O => AEmpty
  | S n' => Aunion (Aupair (Aenc_inf n') (Aupair (Aenc_inf n') (Aenc_inf n')))
  end.

Definition Aom := Asup nat Aenc_inf.

Lemma Aom_spec : ∀ x, (∃ n, Aeq x (Aenc_inf n)) ↔ Ain x Aom.
Proof.
  intros s. split; intros [n H].
  - by exists n.
  - exists n. by apply H.
Qed.

End aczel_trees.
Hint Resolve Aeq_ref Aeq_sym Aeq_tra : core.


(** * extensional model using ϵ, PE and FE *)
(** in the original development, the weaker tree description axiom below is used, but as we need ϵ to make ordinals a stepindex type anyway, we just directly use ϵ + PE + FE *)
Require Import Stdlib.Logic.Epsilon.
Require Import Stdlib.Logic.PropExtensionality.
Require Import Stdlib.Logic.FunctionalExtensionality.

Definition tdelta : (Acz → Prop) → Acz := epsilon (inhabits AEmpty).

Lemma TDesc1 : ∀ P, (∃ s, ∀ t, P t ↔ Aeq t s) → P (tdelta P).
Proof.
intros P H. unfold tdelta. apply epsilon_spec.
destruct H as (s & H). exists s. by apply H.
Qed.

Lemma TDesc2 : ∀ P P', (∀ s, P s ↔ P' s) → tdelta P = tdelta P'.
Proof.
intros P P' H. f_equal. apply functional_extensionality.
intros x. by apply propositional_extensionality.
Qed.

(* Define a normaliser yielding the quotient model *)
Definition N s := tdelta (Aeq s).

Lemma PI_N: ∀ s (H H' : N s = s), H = H'.
Proof.
  intros s. apply proof_irrelevance.
Qed.

Fact N_Aeq: ∀ s, Aeq s (N s).
Proof.
  intros s. pattern (N s). apply TDesc1. by exists s.
Qed.

Lemma N_Aeq_mor: ∀ s t, Aeq s t → N s = N t.
Proof.
  intros s t H. apply TDesc2.
  intros u. rewrite H. tauto.
Qed.

Lemma N_idem s: N (N s) = N s.
Proof.
  apply N_Aeq_mor. symmetry. apply N_Aeq.
Qed.

Lemma N_eq_Aeq s t: N s = N t → Aeq s t.
Proof.
  intros H. rewrite (N_Aeq s) (N_Aeq t). by rewrite H.
Qed.

Instance N_proper : Proper (Aeq ==> Aeq) N.
Proof.
  intros s t H. by rewrite -(N_Aeq s) -(N_Aeq t).
Qed.


(* sigma type for sets based on aczel trees *)
Polymorphic Record set@{i} := mkset {
  set_tree :> Acz@{i};
  set_tree_is_normal: N set_tree = set_tree
}.

Definition NS s : set := mkset (N s) (N_idem s).
Definition IN (X Y : set) := Ain X Y.
Instance in_elem_of: ElemOf set set := IN.
Lemma IN_unfold (X Y: set): X ∈ Y = Ain X Y.
Proof. reflexivity. Qed.


Definition Subq (X Y : set) := ∀ Z, Z ∈ X → Z ∈ Y.
Instance Subq_subseteq: SubsetEq set := Subq.
Lemma Subq_unfold (X Y: set): X ⊆ Y = Subq X Y.
Proof. reflexivity. Qed.

(* lemmas for interfacing with the normalizer *)
Section set_lemmas.
  Implicit Types s t u : Acz.
  Implicit Types X Y Z: set.


  (* equality *)
  Lemma mkset_pi s t (H1 : N s = s) (H2 : N t = t) :
    s = t → mkset s H1 = mkset t H2.
  Proof.
    intros XY. subst t. f_equal. apply PI_N.
  Qed.

  Lemma NS_id X : NS X = X.
  Proof.
    destruct X. simpl. by apply mkset_pi.
  Qed.

  Lemma Aeq_NS s: Aeq (NS s) s.
  Proof. symmetry. exact (N_Aeq s). Qed.


  Lemma Aeq_eq_NS s t :
    Aeq s t → NS s = NS t.
  Proof.
    intros H % N_Aeq_mor. by apply mkset_pi.
  Qed.

  Lemma Aeq_eq X Y:
    Aeq X Y → X = Y.
  Proof.
    intros H % Aeq_eq_NS; move: H; by rewrite !NS_id.
  Qed.


  (* elements *)
  Lemma Ain_IN X Y : Ain X Y ↔ X ∈ Y.
  Proof. by rewrite IN_unfold. Qed.

  Lemma Ain_IN_NS s t : Ain s t ↔ NS s ∈ NS t.
  Proof.
    by rewrite -Ain_IN !Aeq_NS.
  Qed.

  Lemma ASubq_Subq X Y :
    ASubq X Y ↔ Subq X Y.
  Proof.
    split; intros H s H1.
    - by apply Ain_IN, H.
    - rewrite Ain_IN_NS NS_id. eapply H.
      by rewrite IN_unfold Aeq_NS.
  Qed.

End set_lemmas.


(* shorthands hiding the normalizer and the aczel trees *)
Definition setof {X: Type} (f: X → set): set := NS (Asup X (λ x, set_tree (f x))).
Notation "{{ f | x : X }}" := (@setof X (λ x, f)) (x pattern, at level 60).

Definition typeof (s: set) : Type := Atypeof s.
Definition elements (s: set): typeof s → set := λ x, NS (Aelements s x).

Lemma in_inv {Y} x (f: Y → set): x ∈ setof f → ∃ y, x = f y.
Proof.
  rewrite IN_unfold Aeq_NS; intros [y Heq] % Ain_Alements; simpl in *.
  exists y; by apply Aeq_eq.
Qed.

Lemma in_intro {Y} x y (f: Y → set): x = f y → x ∈ setof f.
Proof.
  intros ->. rewrite IN_unfold Aeq_NS; simpl.
  by exists y.
Qed.

Lemma setof_ext {Y} (f g: Y → set): (∀ y, f y = g y) → setof f = setof g.
Proof.
  intros Heq. unfold setof. eapply Aeq_eq_NS; simpl; split.
  all: intros a; exists a; rewrite Heq; reflexivity.
Qed.

Lemma setof_eta (s: set): {{ elements s x | x: typeof s }} = s.
Proof.
  apply Aeq_eq; rewrite Aeq_NS; destruct s as [[X f]]; simpl.
  split; intros a; exists a; symmetry; by rewrite -N_Aeq.
Qed.

Lemma elements_in s x: elements s x ∈ s.
Proof.
  replace s with ({{ elements s x | x: typeof s }}) at 2 by apply setof_eta.
  by eapply in_intro.
Qed.

Lemma in_inv_elements s t: s ∈ t → ∃ x: typeof t, s = elements t x.
Proof.
  replace t with ({{ elements t x | x: typeof t }}) at 1 by apply setof_eta.
  intros [x ->] % in_inv. by exists x.
Qed.


(* ZF constructions *)
Declare Scope zf_scope.
Delimit Scope zf_scope with zf.

Definition empty_set := NS AEmpty.
Instance empty_set_notation: Empty set := empty_set.
Lemma empty_set_unfold: ∅ = empty_set.
Proof. reflexivity. Qed.

Definition upair_set (X Y : set) := NS (Aupair X Y).
Definition union_set (X : set) := NS (Aunion X).
Notation "⋃ S" := (union_set S) (at level 20) : zf_scope.

Definition singleton_set A := upair_set A A.
Instance singleton_Singleton: Singleton set set := singleton_set.

Definition bunion_set A B := union_set (upair_set A B).
Instance bunion_Union : Union set := bunion_set.


Definition power_set (X : set) := NS (Apower X).

Definition empred (P : set → Prop) := λ s, P (NS s).
Definition specification_set (X : set) (P : set → Prop) := NS (Asep X (empred P)).

Definition inter_set S := specification_set (⋃ S)%zf (λ x, ∀ A, A ∈ S → x ∈ A).
Notation "⋂ S" := (inter_set S) (at level 50) : zf_scope.
Definition binter_set A B := inter_set (upair_set A B).
Instance binter_notation : Intersection set := binter_set.

Definition comp_set (A B: set) := specification_set A (λ a, ¬ a ∈ B).
Infix "\" := comp_set (at level 55) : zf_scope.

Definition emfun (F : set → set) := λ s, F (NS s): Acz.

(* We have functional replacement, which is weaker than the usual relational replacement.*)
(* (this difference in power between relational replacement and functional replacement is only present when formalising set theory in Coq, as functions need to be computable while relations don't) *)
Definition replacement_set (X : set) (F : set → set) := NS (Arepl (emfun F) X).
Notation "R @ A" := (replacement_set A R) (at level 56) : zf_scope.


(* We prove the extensional axioms of ZF for the quotient type *)
Section zf_axioms.
Implicit Types X Y Z: set.
(* Extensionality *)
Lemma zf_extensionality X Y : X ⊆ Y ∧ Y ⊆ X ↔ X = Y.
Proof.
  rewrite !Subq_unfold; split; intros H.
  - destruct H as [H1 H2]. apply Aeq_eq, Aeq_ext; by apply ASubq_Subq.
  - by rewrite H /Subq.
Qed.

(* Foundation *)
Lemma IN_wf : well_founded IN.
Proof.
  intros X. destruct X as [s NX].
  induction (Ain_wf s) as [s _ IH].
  constructor. intros [t NY] YX.
  by apply IH.
Qed.

(* Existence *)
Lemma zf_existence X : ¬ X ∈ (∅: set).
Proof.
  rewrite empty_set_unfold.
  intros H % Ain_IN. move: H; rewrite Aeq_NS. by apply AEmptyAx.
Qed.

(* Unordered Pairs *)
Lemma zf_pair X Y Z : Z ∈ (upair_set X Y) ↔ Z = X ∨ Z = Y.
Proof.
  split; rewrite -Ain_IN Aeq_NS AupairAx.
  - intros [H|H].
    + left. by apply Aeq_eq.
    + right. by apply Aeq_eq.
  - intros [-> | ->]; auto.
Qed.

(* Union *)
Lemma zf_union X Z : Z ∈ (union_set X) ↔ ∃ Y, Z ∈ Y ∧ Y ∈ X.
Proof.
split; rewrite -Ain_IN Aeq_NS AunionAx.
- intros [y[Y1 Y2]].
  exists (NS y). by rewrite -!Ain_IN Aeq_NS.
- intros [Y[Y1 Y2]].
  exists Y. move: Y1 Y2; by rewrite -!Ain_IN.
Qed.

(* Power *)
Lemma zf_power X Y : Y ∈ (power_set X) ↔ Y ⊆ X.
Proof.
  split; by rewrite -Ain_IN Aeq_NS ApowerAx Subq_unfold ASubq_Subq.
Qed.

(* Specification *)
Lemma empred_Aeq P : cres Aeq (empred P).
Proof.
  intros s s' H % Aeq_eq_NS. unfold empred. by rewrite H.
Qed.

Lemma zf_specification X P Y : Y ∈ (specification_set X P) ↔ Y ∈ X ∧ P Y.
Proof.
  split; rewrite -!Ain_IN Aeq_NS AsepAx; auto using empred_Aeq.
  all: intros [H1 H2]; split; auto.
  - by rewrite -[Y]NS_id.
  - by rewrite /empred NS_id.
Qed.

(* Functional Replacement *)
Lemma emfun_Aeq F: fres Aeq (emfun F).
Proof.
  intros s s' H % Aeq_eq_NS. by rewrite /emfun H.
Qed.

Lemma zf_replacement F X Y :
  Y ∈ (replacement_set X F) ↔ ∃ Z, Z ∈ X ∧ Y = F Z.
Proof.
  split; rewrite -!Ain_IN Aeq_NS AreplAx; auto using emfun_Aeq.
  - intros [z[Z1 Z2]]; exists (NS z); rewrite -Ain_IN Aeq_NS; split; auto.
    by apply Aeq_eq.
  - intros [Z [Z1 ->]]. exists Z.
    by rewrite Ain_IN /emfun NS_id.
Qed.


Fixpoint inf_set_at n : set :=
  match n with
  | O => ∅
  | S n' => (inf_set_at n') ∪ (singleton (inf_set_at n'))
  end.

Lemma NS_enc_inf n : Aeq (inf_set_at n) (Aenc_inf n).
Proof.
  induction n; cbn [inf_set_at Aenc_inf].
  - cbn. by rewrite -N_Aeq.
  - cbn -[Aunion]. by rewrite IHn -!N_Aeq.
Qed.

Fact SETZS_Inf :
  ∀ x, (∃ n, x = inf_set_at n) ↔ x ∈ (NS Aom).
Proof.
  intros x. rewrite -Ain_IN Aeq_NS -Aom_spec; split.
  - intros [n ->]. exists n. apply NS_enc_inf.
  - intros [n Heq]. exists n. revert Heq; rewrite -NS_enc_inf; apply Aeq_eq.
Qed.

Definition infinite_set := NS Aom.
Lemma Infinity : (∅: set) ∈ infinite_set ∧ (∀ x: set, x ∈ infinite_set → x ∪ (singleton x) ∈ infinite_set).
Proof.
split.
- rewrite -SETZS_Inf. by exists 0.
- intros x. rewrite -!SETZS_Inf. intros [n ->]; by exists (S n).
Qed.


(* As we only require functional replacement, we use the following description axiom to make up for the lack of relational replacement *)
(* The quotient model inherits the description operator *)
Definition desc_set (P : set → Prop) := NS (tdelta (λ s, empred P s)).

Lemma zf_desc : ∀ P, (exists! x, P x) → P (desc_set P).
Proof.
  intros P [X [H1 H2]].
  enough (empred P (tdelta (empred P))) by assumption.
  apply TDesc1. exists X.
  intros t. split; intros H.
  - by rewrite (H2 _ H) Aeq_NS.
  - symmetry in H. apply (empred_Aeq _ _ _ H).
    by rewrite /empred NS_id.
Qed.

(* epsilon induction is equivalent to regularity in ZF*)
(*Axiom Regularity : ∀ A, A <> empty → exists B, B ∈ A /\ (∀ x, x ∈ B → x ∉ A). *)
Lemma eps_ind : ∀ (P:set → Prop), (∀ X, (∀ x, x ∈ X → P x) → P X) → ∀ X, P X.
Proof.
  intros P H X. specialize (IN_wf X). induction 1; auto.
Qed.
End zf_axioms.

(* universe polymorphism test --  we can create a set of sets (not really, since the sets contained in the set live in a different universe, so a better description might be that this is the class of sets?) *)
Definition set_of_sets: set := {{ (∅: set) | s : set (* <- set in a smaller universe *) }}.
(* Definition set_of_all_sets: set := {{ s | s : set <- set in a smaller universe }}. *)
