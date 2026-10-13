(** * Set-theoretic ordinals as a step-index type using several axioms *)
(** In total, this development relies on:
    - PE
    - FE
    - Hilbert's ϵ
    - XM
    - PI (but this is already implied by PE)
  *)

Require Import Stdlib.Logic.Epsilon.
Require Import Stdlib.Logic.ProofIrrelevance.
Require Import Stdlib.Logic.Classical_Prop.
From SynthDom Require Export stepindex.
From SynthDom.ordinals Require Import set_model set_sets set_ordinals.

Set Universe Polymorphism.


(* classical preliminaries *)
(*make an or into a sum using ϵ *)
Lemma or_to_sum (P1 P2 : Prop) : P1 ∨ P2 → P1 + P2.
Proof.
  intros H. assert (exists (b : bool), if b then P1 else P2) as H1.
  { destruct H.
    - now exists true.
    - now exists false.
  }
  apply constructive_indefinite_description in H1. destruct H1 as (b & H1).
  destruct b; eauto.
Qed.

Lemma classic_dn (X : Prop) : X ↔ ¬ (¬ X).
Proof.
  split; intros H.
  - tauto.
  - destruct (classic X) as [H1 | H1]; [easy | tauto].
Qed.

Lemma classic_forall_exists_dn (X : Type) (P : X → Prop): (∀ x, P x) ↔ ¬ (∃ x, ¬ (P x)).
Proof.
  split.
  - intros H (x & H1). eauto.
  - intros H x. destruct (classic (P x)) as [ | H0]; [easy | ].  exfalso; apply H; eauto.
Qed.

Lemma classic_forall_exists (X : Type) (P : X → Prop): ¬ (∀ x, P x) ↔ (∃ x, ¬ (P x)).
Proof.
  by rewrite classic_forall_exists_dn -classic_dn.
Qed.

Lemma classic_exists_forall (X : Type) (P : X → Prop): ¬ (∃ x, (P x)) ↔ (∀ x, ¬ P x).
Proof.
  rewrite classic_forall_exists_dn; split; intros H [x ?]; eauto using classic_dn.
Qed.




Section ord_definition.
  Local Open Scope zf_scope.
  Implicit Types s t u: set.

  (* definition of the ordinal type *)
  Record Ord@{i}:= ord {
    ord_set :> set@{i};
    ord_set_is_ordinal : ordinal ord_set
  }.
  Hint Extern 0 (ordinal _) => by apply ord_set_is_ordinal : core.
  Implicit Types α β γ δ : Ord.

  (* NOTE: This proof uses proof_irrelevance.  *)
  Lemma ord_extensional α β: ord_set α = ord_set β → α = β.
  Proof.
    intros Heq. destruct α as [s Hs], β as [t Ht]; simpl in *.
    subst s. f_equal. apply proof_irrelevance.
  Qed.

  Program Definition ordinals (α: Ord) (x: typeof α): Ord :=
    {| ord_set := elements α x |}.
  Next Obligation.
    intros α x. eapply ordinal_el; eauto using elements_in.
  Qed.

  Definition zero : Ord := {| ord_set := empty; ord_set_is_ordinal := empty_ordinal |}.
  Definition succ α : Ord := {| ord_set := succ_set α; ord_set_is_ordinal := succ_set_ordinal α (ord_set_is_ordinal α) |}.
  Program Definition limit {X} (f: X → Ord) := {| ord_set := ⋃ {{ f x | x : X}} |}.
  Next Obligation.
    intros X f. apply ordinal_union. by intros a [x ->] % in_inv.
  Qed.

  Definition ord_lt (α β : Ord) := (α: set) ∈ (β: set).
  Infix "≺" := ord_lt (at level 80).
  Infix "⪯" := (rc ord_lt) (at level 80).
  Hint Constructors rc : core.

  Lemma ord_leq_unfold α β: α ⪯ β ↔ (α: set) ⊆ (β: set).
  Proof.
    split.
    - intros [->|H]; first by intros ?.
      apply el_succ_set_subs in H; auto.
      eapply subs_trans; last apply H.
      eauto using bunion_subs1, subseq.
    - destruct (ordinal_linear α β) as [H|[H % ord_extensional|Hβα]]; auto.
      intros Hαβ. exfalso. eapply one_cycles, Hαβ, Hβα.
  Qed.

  (** Step-Index Instance *)
  (* Transitivity *)
  Instance ord_lt_trans : Transitive ord_lt.
  Proof.
    intros ???; simpl. destruct z as [z [Ht ?]].
    intros ??. eapply Ht; eauto.
  Qed.

  (* ordinal induction and well-foundedness *)
  Lemma ord_ind (P: Ord → Prop): (∀ α, (∀ β, β ≺ α → P β) → P α) → ∀ α, P α.
  Proof.
    specialize (eps_ind) as Htrans.
    specialize (ordinal_el) as Hordel.
    intros H [a Ha].
    pose (P' := fun a => forall (Ha : ordinal a), P (ord a Ha)).
    enough (P' a) as H'.
    { subst P'. simpl in H'. now apply H'. }
    apply (Htrans P'); auto. clear a Ha.
    intros a IH. intros Ha'. apply H.
    intros [b Hb] Hlt. now apply (IH b Hlt).
  Qed.

  Lemma wf_ord_lt: well_founded ord_lt.
  Proof.
    intros α. induction α using ord_ind.
    by constructor.
  Qed.

  (* strong linearity *)
  Lemma ord_linear_strong α β: (α ≺ β) + (α = β) + (β ≺ α).
  Proof.
    destruct (or_to_sum _ _ (ordinal_linear α β (ord_set_is_ordinal α) (ord_set_is_ordinal β))) as [|H]; auto.
    destruct (or_to_sum _ _ H); auto using ord_extensional.
  Qed.

  (* zero *)
  Lemma zero_least α: α ≺ zero → False.
  Proof.
     apply zf_existence.
  Qed.

  Corollary no_smaller_than_zero: ¬ (∃ α, α ≺ zero).
  Proof. by intros [α H % zero_least]. Qed.

  (* successor *)
  Lemma succ_greater α: α ≺ succ α.
  Proof.
    eapply in_succ_set_iff. by left.
  Qed.

  Lemma succ_least_greater α β: α ≺ β → succ α ⪯ β.
  Proof.
    intros H. apply ord_leq_unfold.
    intros s Hs. eapply in_succ_set_iff in Hs as [->|Hs]; auto.
    eapply ordinal_trans with (y := (α: set)); eauto using ordinal_el.
  Qed.

  Lemma succ_or_limit α: {β : Ord | α = succ β} + (∀ β : Ord, β ≺ α → succ β ≺ α).
  Proof.
    destruct (or_to_sum _ _ (ord_types α (ord_set_is_ordinal α))) as [H|[H|H] % or_to_sum].
    - right. replace α with zero by (apply ord_extensional, symmetry, H).
      intros ? [] % zero_least.
    - left. apply constructive_indefinite_description in H as [s [Ho Heq]].
      exists (ord s Ho); by apply ord_extensional.
    - right. intros β Hβα. by apply limit_ord_el_succ_set in Hβα.
  Qed.

  Lemma ord_index_mixin : IndexMixin Ord ord_lt zero succ.
  Proof.
    constructor.
    - apply _.
    - apply wf_ord_lt.
    - apply ord_linear_strong.
    - apply no_smaller_than_zero.
    - apply succ_greater.
    - apply succ_least_greater.
    - apply succ_or_limit.
    - intros; apply proof_irrelevance.
    Qed.

    Canonical Structure ordI@{i j} : indexT@{j} := IndexT (Ord@{i}) ord_lt zero succ ord_index_mixin.

    (** we define the jump operation to the next limit ordinal by taking the union over all ordinals reachable via succ *)
    Definition jump_limit α := limit (λ n: nat, Nat.iter n succ α).

    Global Instance: TransfiniteIndex ordI.
    Proof.
      exists jump_limit. intros n α.
      apply zf_union. exists (Nat.iter (S n) succ α); split.
      - apply succ_greater.
      - by eapply in_intro.
    Qed.

End ord_definition.
Hint Extern 0 (ordinal _) => by apply ord_set_is_ordinal : core.


Section set_ordinal_lemmas.
  Implicit Types α β γ δ : Ord.

  Lemma ord_lt_unfold α β: α ≺ β ↔ (α: set) ∈ (β: set).
  Proof. reflexivity. Qed.

  Lemma ordinals_lt α x: ordinals α x ≺ α.
  Proof.
    apply ord_lt_unfold, elements_in.
  Qed.
  Hint Immediate ordinals_lt : core.

  Lemma ord_subset α β: (∀ γ, γ ≺ α → γ ≺ β) → (α: set) ⊆ (β: set).
  Proof.
    intros Ha s [x ->] % in_inv_elements.
    apply (Ha _ (ordinals_lt α x)).
  Qed.

  Lemma ord_lt_inv_ordinals β α: β ≺ α → ∃ x: typeof α, β = ordinals α x.
  Proof.
    intros [x Hx] % in_inv_elements. exists x. apply ord_extensional, Hx.
  Qed.

  (* limit operation *)
  Lemma limit_upper_bound_strong (X : Type) (f : X → Ord) (α: Ord):
    (∀ β, β ≺ α → ∃ x, β ≺ f x) → α ⪯ limit f.
  Proof.
    intros H. apply ord_leq_unfold, ord_subset. intros s [a ->] % ord_lt_inv_ordinals.
    destruct (H (ordinals α a) (ordinals_lt α a)) as [x Hleq].
    apply zf_union. exists (f x); eauto using in_intro.
  Qed.

  Lemma limit_upper_bound {X} (f: X → Ord) x: f x ⪯ limit f.
  Proof.
    eapply limit_upper_bound_strong; eauto.
  Qed.

  Lemma limit_least_upper_bound {X} (f: X → Ord) y: (∀ x, f x ⪯ y) → limit f ⪯ y.
  Proof.
    intros Hle. apply ord_leq_unfold.
    intros s [t [Hst Hf]] % zf_union. apply in_inv in Hf as [x ->].
    eapply ord_leq_unfold; [ | apply Hst]. destruct (index_le_eq_or_lt _ _ (Hle x)); eauto.
  Qed.

  Lemma limit_ext {Y} (f g: Y → Ord):
    (∀ x, f x = g x) → limit f = limit g.
  Proof.
    intros Heq. apply ord_extensional; simpl.
    f_equal. apply setof_ext. intros x. by destruct (Heq x).
  Qed.

  Lemma limit_mono_strong {A B} (F: A → Ord) (G: B → Ord): (∀ a, ∃ b, F a ⪯ G b) → limit F ⪯ limit G.
  Proof.
    intros H.
    apply limit_least_upper_bound. intros x. destruct (H x) as [b Hle].
    transitivity (G b); eauto using limit_upper_bound.
  Qed.

  Lemma limit_mono {A} (F: A → Ord) (G: A → Ord): (∀ a, F a ⪯ G a) → limit F ⪯ limit G.
  Proof.
    intros H; eapply limit_mono_strong; intros a; by exists a.
  Qed.

  (* derived limit constructor for limits of ordinals *)
  Definition limitO α (f: ∀ β, β ≺ α → Ord) := limit (λ x : typeof α, f (ordinals α x) (ordinals_lt α x)).

  Lemma limitO_ext α (f g: ∀ β, β ≺ α → Ord): (∀ β Hβ, f β Hβ = g β Hβ) → limitO α f = limitO α g.
  Proof.
    intros H; apply limit_ext; auto.
  Qed.
End set_ordinal_lemmas.


Section existential_property.

  (** proof that once can "pull out" existentials when using ordinals as the stepindex type *)
  Lemma constructive_upper_bound_ordinal A (φ: A → Ord → Prop):
    (∀ a α β, α ⪯ β → φ a α → φ a β) →
    (∀ a : A, { α : Ord | φ a α }) →
    ({ α: Ord | ∀ a: A, φ a α}).
  Proof.
  intros Hge X. exists (limit (λ a : A, proj1_sig (X a))).
  intros a. destruct (X a) as [α Hφ] eqn: H.
  eapply Hge, Hφ. transitivity (proj1_sig (X a)); last apply (limit_upper_bound (λ a : A, proj1_sig (X a))).
  by rewrite H.
  Qed.

  Lemma upper_bound_ordinal (A: Type) (φ: A → Ord → Prop):
    (∀ a α β, α ⪯ β → φ a α → φ a β) →
    (∀ a : A, ∃ α : Ord, φ a α) →
    (∃ α: Ord, ∀ a: A, φ a α).
  Proof.
  intros Hge Ha. edestruct (constructive_upper_bound_ordinal _ _ Hge) as [α Hα].
  - intros a. by apply constructive_indefinite_description.
  - by exists α.
  Qed.

  (* classical proof of the existential property *)
  Lemma commute_exists (J : Type) (P : J → Ord → Prop) :
    (∀ j α β, α ≺ β → P j β → P j α)
    → (∀ α, ∃ j, P j α)
    → ∃ j, ∀ α, P j α.
  Proof.
    intros Hdown H. destruct (classic (∃ j : J, ∀ α : Ord, P j α)) as [|H1]; auto.
    destruct (upper_bound_ordinal _ (λ j α, ¬ P j α)) as [α Hbound].
    - intros a α β Hle Hα Hβ. apply Hα. destruct Hle; subst; eauto.
    - intros a. revert H1. rewrite classic_exists_forall -classic_forall_exists; eauto.
    - exfalso. destruct (H α); by eapply Hbound.
  Qed.
End existential_property.

Section large_index_class.
  Polymorphic Universes i j.
  Polymorphic Constraint i < j.

  Global Instance set_model_large_index: LargeIndex (ordI@{i j}).
  Proof.
    intros X P H He. eapply commute_exists; eauto.
  Qed.
End large_index_class.
