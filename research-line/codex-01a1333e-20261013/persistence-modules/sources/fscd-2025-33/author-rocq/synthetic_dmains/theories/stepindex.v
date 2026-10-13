From SynthDom Require Import prelude.

Set Universe Polymorphism.
Unset Universe Minimization ToSet.

(* TODO: move into stdpp *)
Inductive rc {A} (R: A → A → Prop) (x y: A):  Prop :=
| rc_refl: x = y → rc R x y
| rc_subrel: R x y → rc R x y.
Hint Constructors rc : core.

Instance rc_reflexive {A} (R : A → A → Prop) : Reflexive (rc R).
Proof. intros ?; by apply rc_refl. Qed.
Instance rc_subrelation {A} (R : A → A → Prop): subrelation R (rc R).
Proof. intros ? ? ?; by apply rc_subrel. Qed.

Polymorphic Structure IndexMixin {A} {R: A → A → Prop} {zero: A} {succ: A → A} :=
  {
    index_mixin_lt_trans: Transitive R;
    index_mixin_lt_wf: well_founded R;
    index_mixin_lt_strict_total α β: (R α β) + (α = β) + (R β α);
    index_mixin_zero_least: nf (flip R) zero;
    index_mixin_succ_greater α: R α (succ α);
    index_mixin_succ_least α β: R α β → rc R (succ α) β;
    index_mixin_dec_limit α: {β | α = succ β} +
                           (∀ β, R β α → R (succ β) α);
    index_mixin_lt_irrel α β: ∀ Hlt Hlt' : R α β, Hlt = Hlt';
  }.
Arguments IndexMixin : clear implicits.

Polymorphic Structure indexT@{i} :=
  IndexT {
    index_car :> Type@{i};
    index_lt : relation index_car;
    index_zero : index_car;
    index_succ : index_car → index_car;
    index_mixin :> IndexMixin index_car index_lt index_zero index_succ;
  }.

Notation "(≺)" := (index_lt _).
Notation "(≻)" := (flip (index_lt _)).

Notation zero := (index_zero _).
Notation succ α := (index_succ _ α).
Notation "α ≺ β" := (index_lt _ α β) (at level 80).

Polymorphic Definition index_le (SI : indexT) : relation SI := rc (index_lt SI).
Notation "(⪯)" := (index_le _).
Notation "α ⪯ β" := (index_le _ α β) (at level 80).

Instance index_le_refl {SI : indexT} : Reflexive (@index_le SI) := _.
Instance index_lt_le_subrel {SI : indexT}: subrelation (@index_lt SI) (@index_le SI) := _.
Lemma index_le_refl_auto {SI : indexT} (α β : SI) (H : α = β): α ⪯ β.
Proof. rewrite H. apply index_le_refl. Qed.
Hint Extern 1 (?a ⪯ ?a) => apply index_le_refl : core.
Hint Extern 2 (?a ⪯ ?b) => apply index_le_refl_auto : core.
Hint Extern 1 (?a ⪯ ?b) => apply index_lt_le_subrel : core.

Lemma index_le_eq_or_lt {SI : indexT} (α β : SI) : α ⪯ β → α = β ∨ α ≺ β.
Proof. intros [H | H]; auto. Qed.

Section index_laws.
  Context {SI : indexT}.
  Global Instance index_lt_trans : Transitive (index_lt SI).
  Proof. eapply index_mixin_lt_trans, SI. Qed.
  Lemma index_lt_wf : well_founded (index_lt SI).
  Proof. eapply index_mixin_lt_wf, SI. Qed.
  Lemma index_lt_eq_lt_dec (α β : SI) : (α ≺ β) + (α = β) + (β ≺ α).
  Proof. eapply index_mixin_lt_strict_total, SI. Qed.
  Lemma index_zero_least : nf (flip (index_lt SI)) zero.
  Proof. eapply index_mixin_zero_least, SI. Qed.
  Lemma index_succ_greater (α : SI) : α ≺ succ α.
  Proof. eapply index_mixin_succ_greater, SI. Qed.
  Lemma index_succ_least (α β : SI) : α ≺ β → succ α ⪯ β.
  Proof. eapply index_mixin_succ_least, SI. Qed.
  Lemma index_dec_limit (α: SI) : { β | α = succ β } + (∀ β, β ≺ α → succ β ≺ α).
  Proof. eapply index_mixin_dec_limit, SI. Qed.
  Global Instance index_lt_irrel (α β: SI) : ProofIrrel (α ≺ β).
  Proof. intros ??; eapply index_mixin_lt_irrel, SI. Qed.
End index_laws.
Arguments index_zero_least : clear implicits.
Arguments index_lt_wf : clear implicits.

Definition index_is_limit {SI : indexT} (α : SI) := ∀ β, β ≺ α → succ β ≺ α.
(* proper limit indices that are not zero*)
Record limit_idx {SI: indexT} := mklimitidx {
  limit_index :> SI;
  limit_index_is_limit : index_is_limit limit_index;
  limit_index_not_zero : zero ≺ limit_index;
}.
Arguments limit_idx : clear implicits.
Arguments mklimitidx {_}.

Section StepIndexProperties.
  Context {I: indexT}.
  Implicit Type (α β γ : I).

  Global Instance: Inhabited I.
  Proof. constructor. exact zero. Qed.

  Global Instance : ∀ SI, PreOrder (@index_le SI).
  Proof.
    split; [by constructor|].
    intros ??? [] []; subst; eauto.
    right; transitivity y; auto.
  Qed.

  Lemma index_le_total α β: {α ⪯ β} + {β ⪯ α}.
  Proof.
    destruct (index_lt_eq_lt_dec α β) as [[|]|]; eauto.
  Qed.

  Lemma index_le_lt_dec α β : {α ⪯ β} + {β ≺ α}.
  Proof.
    edestruct (index_lt_eq_lt_dec α β) as [[H | H] | H]; eauto.
  Defined.

  Lemma index_zero_minimum α: zero ⪯ α.
  Proof.
    destruct (index_le_total zero α) as [|[]]; eauto.
    exfalso; eapply (index_zero_least); eauto.
  Qed.

  Lemma index_lt_zero_is_normal α: ¬ (α ≺ zero).
  Proof.
    specialize (index_zero_least I) as H.
    intros R; apply H; unfold red, flip; eauto.
  Qed.

  Lemma index_zero_is_unique α: (∀ β, ¬ (β ≺ α)) → α = zero.
  Proof.
    intros H; destruct (index_le_total α zero) as [[]|[]]; eauto; exfalso.
    - by eapply index_lt_zero_is_normal.
    - by eapply H.
  Qed.

  Lemma index_is_zero α: {α = zero} + {zero ≺ α}.
  Proof.
    destruct (index_lt_eq_lt_dec α zero) as [[]|]; eauto.
    exfalso; by eapply index_lt_zero_is_normal.
  Qed.

  Lemma index_lt_dec_minimum α: (∀ β, ¬ (β ≺ α)) + { β | β ≺ α}.
  Proof.
    destruct (index_lt_eq_lt_dec α zero) as [[]|].
    - exfalso; by eapply index_lt_zero_is_normal.
    - subst; left; exact index_lt_zero_is_normal.
    - right; by eexists.
  Qed.

  Lemma index_lt_irrefl α: ¬ (α ≺ α).
  Proof.
    induction α using (well_founded_ind (index_lt_wf I)).
    intros H1; apply H in H1 as H2; eauto.
  Qed.

  Lemma index_lt_le_trans α β γ: α ≺ β → β ⪯ γ → α ≺ γ.
  Proof. intros ? []; subst; eauto. by transitivity β. Qed.

  Lemma index_le_lt_trans α β γ: α ⪯ β → β ≺ γ → α ≺ γ.
  Proof. intros [] ?; subst; eauto. by transitivity β. Qed.

  Lemma index_le_lt_contradict α α' : α ⪯ α' → α' ≺ α → False.
  Proof.
    intros H1 H2. enough (α ≺ α) by (by eapply index_lt_irrefl).
    by eapply index_le_lt_trans.
  Qed.

  Lemma index_lt_le_contradict α α' : α ≺ α' → α' ⪯ α → False.
  Proof.
    intros H1 H2. enough (α ≺ α) by (by eapply index_lt_irrefl).
    by eapply index_lt_le_trans.
  Qed.

  Lemma index_le_ge_eq α α' : α ⪯ α' → α' ⪯ α → α = α'.
  Proof.
    intros [-> | H1] [H2 | H2]; try by eauto.
    exfalso; eapply index_lt_irrefl. by eapply index_lt_trans.
  Qed.

  Lemma index_succ_iff α β: α ⪯ β ↔ α ≺ succ β.
  Proof.
    split; intros H.
    - destruct H; subst. 2: transitivity β.
      all: eauto; eapply index_succ_greater.
    - destruct (index_le_total α β) as [|[|H1]]; eauto.
      apply index_succ_least in H1.
      eapply index_lt_le_trans in H1; eauto.
      exfalso; eapply index_lt_irrefl; eauto.
  Qed.

  Lemma index_le_lt_eq_dec α β : α ⪯ β → {α ≺ β} + {α = β}.
  Proof.
    intros Hle. destruct (index_lt_eq_lt_dec α β) as [[H | H] | H].
    - by left.
    - by right.
    - exfalso. eapply index_lt_irrefl with (α := α). by eapply index_le_lt_trans.
  Qed.

  Lemma index_lt_succ_mono α β: α ≺ β → succ α ≺ succ β.
  Proof.
    intros. by eapply index_succ_iff, index_succ_least.
  Qed.

  Lemma index_le_succ_mono α β: α ⪯ β → succ α ⪯ succ β.
  Proof.
    intros [->|H % index_lt_succ_mono]; eauto.
  Qed.

  Lemma index_succ_greater' α β: α = succ β → β ≺ α.
  Proof. intros ->; by apply index_succ_greater. Qed.

  Lemma index_succ_neq α : α ≠ succ α.
  Proof.
    intros H%index_succ_greater'. by eapply index_lt_irrefl.
  Qed.

  Lemma index_lt_succ_inj α β: succ α ≺ succ β → α ≺ β.
  Proof.
    destruct (index_le_total α β) as [[]|H].
    - subst; intros [] % index_lt_irrefl.
    - auto.
    - intros H'. apply index_le_succ_mono in H.
      specialize (index_le_lt_trans _ _ _ H H') as [] % index_lt_irrefl.
  Qed.

  Lemma index_succ_inj α β: succ α = succ β → α = β.
  Proof.
    intros H. destruct (index_lt_eq_lt_dec α β) as [[H'|]|H']; eauto; exfalso.
    all: eapply index_lt_succ_mono in H'; rewrite H in H'; by eapply index_lt_irrefl.
  Qed.

  Lemma index_le_succ_inj α β : succ α ⪯ succ β → α ⪯ β.
  Proof.
    intros [Heq | Hlt].
    - apply index_succ_inj in Heq. by left.
    - apply index_lt_succ_inj in Hlt. by right.
  Qed.

  Lemma index_eq_dec α β: {α = β} + {α ≠ β}.
  Proof.
    destruct (index_lt_eq_lt_dec α β) as [[H|H]|H]; subst.
    - right; intros ->; by eapply index_lt_irrefl.
    - by left.
    - right; intros ->; by eapply index_lt_irrefl.
  Qed.

  Lemma index_succ_le_lt α β : succ α ⪯ β ↔ α ≺ β.
  Proof.
    split.
    - intros [<- | H1]; [eapply index_succ_greater | ].
      eapply index_lt_trans; [ eapply index_succ_greater | eauto ].
    - intros H. destruct (index_lt_eq_lt_dec (succ α) β) as [[Hlt | Heq] | Hgt].
      + by right.
      + by left.
      + exfalso. eapply index_succ_least in Hgt.
        apply index_le_succ_inj in Hgt.
        eapply index_lt_irrefl. by eapply index_lt_le_trans.
  Qed.

  Lemma index_succ_le α β : succ α ⪯ β → α ⪯ β.
  Proof.
    right. by apply index_succ_le_lt.
  Qed.

  Lemma index_lt_succ_tight α β : α ≺ β → β ≺ succ α → False.
  Proof.
    intros H1%index_succ_le_lt H2. eapply index_lt_irrefl, index_le_lt_trans; eauto.
  Qed.

  Lemma index_succ_not_zero α: succ α ≠ zero.
  Proof.
    intros H. eapply index_lt_zero_is_normal, index_succ_greater'. by symmetry.
  Qed.

  Lemma index_succ_not_limit β: ¬ (∀ α, α ≺ succ β → succ α ≺ succ β).
  Proof.
    intros H. eapply index_lt_irrefl, H. apply index_succ_greater.
  Qed.

  Lemma index_limit_not_succ (β : I) : index_is_limit β → ∀ α, β ≠ succ α.
  Proof.
    intros H α Hα. specialize (H α). rewrite Hα in H. eapply index_lt_irrefl. apply H, index_succ_greater.
  Qed.

  Definition index_min α β := if index_le_total α β then α else β.
  Lemma index_min_eq α β: index_min α β = α ∨ index_min α β = β.
  Proof.
    unfold index_min; destruct index_le_total; eauto.
  Qed.

  Lemma index_min_le_l α β : index_min α β ⪯ α.
  Proof.
    unfold index_min. destruct index_le_total; eauto.
  Qed.
  Lemma index_min_le_r α β : index_min α β ⪯ β.
  Proof.
    unfold index_min. destruct index_le_total; eauto.
  Qed.

  Lemma index_min_l α β : α ⪯ β → index_min α β = α.
  Proof.
    intros H. unfold index_min. destruct (index_le_total α β) as [_ | Hle]; [easy | ].
    by apply index_le_ge_eq.
  Qed.

  Lemma index_min_r α β : α ⪯ β → index_min β α = α.
  Proof.
    intros H. unfold index_min. destruct (index_le_total β α) as [Hle | ]; [| easy].
    by apply index_le_ge_eq.
  Qed.

  Lemma index_min_comm α β : index_min β α = index_min α β.
  Proof.
    unfold index_min.
    destruct (index_le_total β α) as [H1 | H1], (index_le_total α β) as [H2 | H2].
    - by apply index_le_ge_eq.
    - reflexivity.
    - reflexivity.
    - by apply index_le_ge_eq.
  Qed.

  Lemma index_min_mono_r γ β α: γ ⪯ β → index_min α γ ⪯ index_min α β.
  Proof.
    intros H. unfold index_min. destruct (index_le_total α γ) as [H1 | H1];
    destruct (index_le_total α β) as [H2 | H2]; try by auto.
    left. eapply index_le_ge_eq; auto. etransitivity; eauto.
  Qed.

  Global Instance index_eq_dec' : EqDecision I.
  Proof. intros ??; apply index_eq_dec. Qed.

  Global Instance index_le_proof_irrel α β : ProofIrrel (α ⪯ β).
  Proof.
    intros [->|Hlt] [Heq|Hlt'].
    - by replace Heq with (eq_refl β) by apply proof_irrel.
    - exfalso; eapply index_lt_irrefl; done.
    - destruct Heq; exfalso; eapply index_lt_irrefl; done.
    - replace Hlt with Hlt' by apply proof_irrel; done.
  Qed.

  Lemma le_zero_zero (α : I) : α ⪯ zero → α = zero.
  Proof.
    destruct (index_is_zero α) as [->|]; first done.
    intros; exfalso; eapply index_le_lt_contradict; eauto.
  Qed.
  Lemma le_succ_dec {α β : I} : α ⪯ succ β → {α ⪯ β} + {α = succ β}.
  Proof.
    intros Hle.
    destruct (index_le_lt_eq_dec α (succ β)); first done.
    - left; by apply index_succ_iff.
    - right; done.
  Qed.


End StepIndexProperties.

Hint Immediate index_zero_minimum : core.
Hint Resolve index_succ_greater : core.
Hint Resolve <- index_succ_iff : core.

Section ordinal_match.
  Context {SI : indexT}.
  Definition ord_match (P : SI → Type) : P zero → (∀ α, P (succ α)) → (∀ α : limit_idx SI, P α) → ∀ α, P α :=
    λ s f lim α,
      match index_is_zero α with
      | left EQ => eq_rect_r P s EQ
      | right NT =>
          match index_dec_limit α with
          | inl (exist _ β EQ) => eq_rect_r P (f β) EQ
          | inr Hlim => lim (mklimitidx α Hlim NT)
          end
      end.
End ordinal_match.

Section ordinal_recursor.
  Context {SI: indexT}.

  Definition index_rec (P: SI → Type): P zero → (∀ α, P α → P (succ α)) → (∀ α: limit_idx SI, (∀ β, β ≺ α → P β) → P α) → ∀ α, P α :=
    λ s f lim, Fix (index_lt_wf SI) _ (λ α IH,
        match index_is_zero α with
        | left EQ => eq_rect_r P s EQ
        | right NZ =>
          match index_dec_limit α with
          | inl (exist _ β EQ) => eq_rect_r P (f β (IH β (index_succ_greater' α β EQ))) EQ
          | inr Hlim => lim (mklimitidx α Hlim NZ) IH
          end
        end
      ).

  Lemma index_type_dec (α : SI) :
    (α = zero) + { α' | α = succ α'} + ( index_is_limit α).
  Proof.
    revert α. apply index_rec.
    - by left; left.
    - intros α _; left; right. by exists α.
    - intros α _. right. apply limit_index_is_limit.
  Defined.

  Class index_rec_lim_ext {P: SI → Type} (lim: ∀ α: limit_idx SI, (∀ β, β ≺ α → P β) → P α) := {
    index_rec_lim_ext_proofs α H1 H2 f: lim α f = lim (mklimitidx α H2 H1) f;
    index_rec_lim_ext_function α f g: (∀ β Hβ, f β Hβ = g β Hβ) → lim α f = lim α g
  }.

  Lemma index_rec_unfold P s f lim `{index_rec_lim_ext P lim} α:
    index_rec P s f lim α =
    match index_is_zero α with
    | left EQ => eq_rect_r P s EQ
    | right NZ =>
      match index_dec_limit α with
      | inl (exist _ β EQ) => eq_rect_r P (f β (index_rec P s f lim β)) EQ
      | inr Hlim => lim (mklimitidx α Hlim NZ) (λ β _, index_rec P s f lim β)
      end
    end.
  Proof.
    unfold index_rec at 1. rewrite Fix_eq.
    - reflexivity.
    - intros β g h EQ. destruct index_is_zero; eauto.
      destruct index_dec_limit as [[γ EQ']|].
      + by rewrite EQ.
      + erewrite index_rec_lim_ext_function; eauto.
  Qed.

  Lemma index_rec_zero P s f lim `{index_rec_lim_ext P lim}: index_rec P s f lim zero = s.
  Proof.
    rewrite index_rec_unfold; eauto.
    destruct index_is_zero as [EQ|NT].
    - symmetry. apply Eqdep_dec.eq_rect_eq_dec, index_eq_dec.
    - exfalso; by eapply index_lt_irrefl.
  Qed.

  Lemma index_rec_succ P s f lim `{index_rec_lim_ext P lim} α: index_rec P s f lim (succ α) = f α (index_rec P s f lim α).
  Proof.
    rewrite index_rec_unfold; eauto.
    destruct index_is_zero as [EQ|NT];[|destruct index_dec_limit as [[β EQ]|Hlim]].
    - exfalso. by eapply index_succ_not_zero.
    - eapply index_succ_inj in EQ as EQ'. subst α.
      symmetry. apply Eqdep_dec.eq_rect_eq_dec, index_eq_dec.
    - exfalso. eapply index_lt_irrefl, Hlim, index_succ_greater.
  Qed.

  Lemma index_rec_lim P s f lim `{index_rec_lim_ext P lim} (α: limit_idx SI):
    index_rec P s f lim α = lim α (λ β _, index_rec P s f lim β).
  Proof.
    rewrite index_rec_unfold; eauto.
    destruct index_is_zero as [EQ|NT];[|destruct index_dec_limit as [[β EQ]|Hlim]].
    - exfalso. specialize (limit_index_not_zero α). rewrite EQ. by apply index_lt_irrefl.
    - exfalso. specialize (limit_index_is_limit α β (index_succ_greater' _ _ EQ)).
      rewrite EQ. by apply index_lt_irrefl.
    - simpl. symmetry. apply index_rec_lim_ext_proofs.
  Qed.
End ordinal_recursor.

Record index_rect {SI : indexT} (T : SI → Type) := MkIR {
  IR_zero : T zero;
  IR_succ : ∀ α, T α → T (succ α);
  IR_lim : ∀ α : limit_idx SI, (∀ β, β ≺ α → T β) → T α;
  IR_lim_ext : index_rec_lim_ext IR_lim;
  IR_ev :> ∀ α, T α := index_rec T IR_zero IR_succ IR_lim;
  index_rect_zero : IR_ev zero = IR_zero :=
    index_rec_zero T IR_zero IR_succ IR_lim;
  index_rect_succ α : IR_ev (succ α) = IR_succ α (IR_ev α) :=
    index_rec_succ T IR_zero IR_succ IR_lim α;
  index_rect_lim (α : limit_idx SI): IR_ev α = IR_lim α (λ β _, IR_ev β) :=
    index_rec_lim T IR_zero IR_succ IR_lim α;
}.
Arguments MkIR {_ _} _ _ _ _, {_} _ _ _ _ _.
Arguments IR_zero {_ _} _.
Arguments IR_succ {_ _} _ [_] _.
Arguments IR_lim {_ _} _ [_] _.

Ltac simpl_index_rect_zero :=
  rewrite ?index_rect_zero;
  match goal with
    |- context [@IR_zero _ _ ?A] => simpl (@IR_zero _ _ A)
  end.
Ltac simpl_index_rect_succ :=
  rewrite ?index_rect_succ;
  match goal with
    |- context [@IR_succ _ _ ?A _ _] => simpl (@IR_succ _ _ A _ _)
  end.
Ltac simpl_index_rect_lim :=
  rewrite ?index_rect_lim;
  match goal with
    |- context [@IR_lim _ _ ?A _ _] => simpl (@IR_lim _ _  A _ _)
  end.

Ltac simpl_index_rect :=
  repeat first
    [simpl_index_rect_zero|
     simpl_index_rect_succ|
     simpl_index_rect_lim].

Tactic Notation "simpl_index_rect_zero" "in" hyp(H) :=
  rewrite ?index_rect_zero in H;
  match type of H with
  | context [@IR_zero _ _ ?A] => simpl (@IR_zero _ _ A) in H
  end.
Tactic Notation "simpl_index_rect_succ" "in" hyp(H) :=
  rewrite ?index_rect_succ in H;
  match type of H with
  | context [@IR_succ _ _ ?A _ _] => simpl (@IR_succ _ _ A _ _) in H
  end.
Tactic Notation "simpl_index_rect_lim" "in" hyp(H) :=
  rewrite ?index_rect_lim in H;
  match type of H with
  | context [@IR_lim _ _ ?A _ _] => simpl (@IR_lim _ _ A _ _) in H
  end.

Tactic Notation "simpl_index_rect" "in" hyp(H) :=
  repeat first
    [simpl_index_rect_zero in H|
     simpl_index_rect_succ in H|
     simpl_index_rect_lim in H].

Section ordinal_cumulative_recursor.

  Context {SI: indexT}.
  Variable (P: SI → Type) (Q: ∀ α, (∀ β, β ≺ α → P β) → Type).

  Let R α := {f: ∀ β, β ≺ α → P β & Q α f}.

  Lemma index_cumulative_rec (F: ∀ α, R α → P α):
    (∀ α G, Q α (λ β Hβ, F β (G β Hβ))) → (∀ α, R α).
  Proof.
    intros IH. apply (Fix (index_lt_wf SI)).
    intros α G. unfold R. unshelve econstructor.
    - intros β Hβ. by eapply F, G.
    - by apply IH.
  Defined.

  Lemma index_cumulative_rec_dep (F: ∀ α, R α → P α):
    (∀ α G, Q α (λ β Hβ, F β (G β Hβ))) → (∀ α (H : Acc (≺) α), R α).
  Proof.
    intros IH. apply (Fix_F).
    intros α G. unfold R. unshelve econstructor.
    - intros β Hβ. by eapply F, G.
    - by apply IH.
  Defined.

  Lemma index_cumulative_rec_dep_step F step β succs:
    index_cumulative_rec_dep F step β (Acc_intro β succs) =
    existT (λ γ Hγ, F γ (index_cumulative_rec_dep F step γ (succs γ Hγ)))
      (step β (λ γ Hγ, index_cumulative_rec_dep F step γ (succs γ Hγ))).
  Proof. reflexivity. Qed.

  Lemma index_cumulative_rec_unfold F step (M : ∀ α, R α → Prop) :
    (∀ β succs, (∀ γ (Hγ: γ ≺ β), M γ (index_cumulative_rec_dep F step γ (succs γ Hγ))) → M β (index_cumulative_rec_dep F step β (Acc_intro β succs)))
    → ∀ β, M β (index_cumulative_rec F step β).
  Proof.
    intros H β. unfold index_cumulative_rec, Fix.
    pattern β, (index_lt_wf SI β). eapply Acc_inv_dep. clear β.
    intros β succs Hβ.
    unfold index_cumulative_rec_dep in H.
    eapply H. apply Hβ.
  Qed.
  Global Opaque index_cumulative_rec_dep.
  Global Opaque index_cumulative_rec.
End ordinal_cumulative_recursor.

Polymorphic Class FiniteIndex (I: indexT) :=
  finite_index: ∀ α,  (∀ β, ¬ (β ≺ α)) + {β | β ≺ α ∧ ∀ (γ: I), γ ≺ α → γ ⪯ β}.

Polymorphic Class TransfiniteIndex (SI: indexT) :=
  { upper_limit: SI → SI;
    upper_limit_is_limit n m: Nat.iter n (index_succ SI) m ≺ upper_limit m
  }.

Section large_index_class.

  Polymorphic Universes i j.
  Polymorphic Constraint i < j.

  Polymorphic Class LargeIndex (SI: indexT@{j}) : Type :=
      can_commute_exists (X : Type@{i}) (P : X → SI → Prop) :
    (∀ x a b, a ≺ b → P x b → P x a)
    → (∀ a, ∃ x, P x a)
    → ∃ x, ∀ a, P x a.

End large_index_class.


Section finite_existential_property.
  Set Universe Polymorphism.

  (* For the finite existential property classical logic suffices *)
  Polymorphic Class FiniteExistential (SI: indexT) :=
    can_split_or (P Q: SI → Prop):
    (∀ a b, a ≺ b → P b → P a) →
    (∀ a b, a ≺ b → Q b → Q a) →
    (∀ a, P a ∨ Q a) → (∀ a, P a) ∨ (∀ a, Q a).

  (* Natural numbers satisfy a bounded version *)
  Polymorphic Class FiniteBoundedExistential (SI: indexT) :=
    can_split_bounded_or (P Q: SI → Prop) c:
    (∀ a b, a ≺ b → P b → P a) →
    (∀ a b, a ≺ b → Q b → Q a) →
    (∀ a, a ≺ c → P a ∨ Q a) → (∀ a, a ≺ c → P a) ∨ (∀ a, a ≺ c → Q a).

  (* assuming this type class or instantiaing it with classical axioms makes FiniteExistential available *)
  Polymorphic Class Classical : Prop :=
    excluded_middle : ∀ P: Prop, P ∨ ¬ P.

  Lemma classical_can_commute_or {SI: indexT} (P Q: SI → Prop):
    (∀ P: Prop, P ∨ ¬ P) →
    (∀ a b, a ≺ b → P b → P a) →
    (∀ a b, a ≺ b → Q b → Q a) →
    (∀ a, P a ∨ Q a) → (∀ a, P a) ∨ (∀ a, Q a).
  Proof.
    intros xm HdownP HdownQ Hsome. destruct (xm (∃ a, ¬ P a)) as [[a HP]|HP]; last first.
    - left. intros a. destruct (xm (P a)); auto. exfalso. apply HP. by exists a.
    - assert (Q a) by (destruct (Hsome a); naive_solver).
      right. intros b. destruct (index_lt_eq_lt_dec a b) as [[|<-]|]; eauto.
      destruct (Hsome b); auto. exfalso. apply HP; eauto.
  Qed.

  Global Instance classical_finite_existential SI `{Classical}: FiniteExistential SI.
  Proof.
    intros P Q ???. eapply classical_can_commute_or; eauto.
  Qed.

  Lemma classical_can_commute_bounded_or {SI: indexT} (P Q: SI → Prop) c:
    (∀ P: Prop, P ∨ ¬ P) →
    (∀ a b, a ≺ b → P b → P a) →
    (∀ a b, a ≺ b → Q b → Q a) →
    (∀ a, a ≺ c → P a ∨ Q a) → (∀ a, a ≺ c → P a) ∨ (∀ a, a ≺ c → Q a).
  Proof.
    intros xm HdownP HdownQ Hsome. destruct (xm (∃ a, ¬ P a ∧ a ≺ c)) as [[a [HP Ha]]|HP]; last first.
    - left. intros a Ha. destruct (xm (P a)); auto. exfalso. apply HP. by exists a.
    - assert (Q a) by (destruct (Hsome a); naive_solver).
      right. intros b Hb. destruct (index_lt_eq_lt_dec a b) as [[|<-]|]; eauto.
      destruct (Hsome b); auto. exfalso. apply HP; eauto.
  Qed.

  Global Instance classical_finite_bounded_existential SI `{Classical}: FiniteBoundedExistential SI.
  Proof.
    intros P Q ???. eapply classical_can_commute_bounded_or; eauto.
  Qed.

  Lemma can_commute_finite_exists {SI: indexT} `{FiniteExistential SI} (X : Type) (P : X → SI → Prop) (Q: X → Prop) :
    (∀ x a b, a ≺ b → P x b → P x a)
    → (∀ a, ∃ x, Q x ∧ P x a)
    → pred_finite Q
    → ∃ x, ∀ a, P x a.
  Proof.
    intros Hdown Hsome [A Hfin].
    assert (∀ a, ∃ x, x ∈ A ∧ P x a) as Hsome'.
    { intros a. destruct (Hsome a) as [x [? ?]]. exists x. split; eauto. }
    clear Hfin Hsome. induction A as [|x A IH].
    - specialize (Hsome' zero) as [x [? ?]]. exfalso. by eapply not_elem_of_nil.
    - assert ((∀ a, P x a) ∨ (∀ a : SI, ∃ x : X, x ∈ A ∧ P x a)) as [|]; eauto.
      eapply can_split_or; eauto.
      + intros a b Hab [y [HA HP]]. exists y; split; eauto.
      + intros a; destruct (Hsome' a) as [y [HA HP]].
        apply elem_of_cons in HA as [<-|?]; eauto.
  Qed.

  Lemma can_commute_finite_bounded_exists {SI: indexT} `{FiniteBoundedExistential SI} (X : Type) (P : X → SI → Prop) (Q: X → Prop) c:
    zero ≺ c
    → (∀ x a b, a ≺ b → P x b → P x a)
    → (∀ a, a ≺ c → ∃ x, Q x ∧ P x a)
    → pred_finite Q
    → ∃ x, ∀ a, a ≺ c → P x a.
  Proof.
    intros Hterm Hdown Hsome [A Hfin].
    assert (∀ a, a ≺ c → ∃ x, x ∈ A ∧ P x a) as Hsome'.
    { intros a Ha. destruct (Hsome a Ha) as [x [? ?]]. exists x. split; eauto. }
    clear Hfin Hsome. induction A as [|x A IH].
    - specialize (Hsome' zero Hterm) as [x [? ?]]. exfalso. by eapply not_elem_of_nil.
    - assert ((∀ a, a ≺ c → P x a) ∨ (∀ a : SI, a ≺ c → ∃ x : X, x ∈ A ∧ P x a)) as [|]; eauto.
      eapply can_split_bounded_or; eauto.
      + intros a b Hab [y [HA HP]]. exists y; split; eauto.
      + intros a Ha; destruct (Hsome' a Ha) as [y [HA HP]].
        apply elem_of_cons in HA as [<-|?]; eauto.
  Qed.

  Global Instance large_index_finite_existential@{i j} (SI: indexT@{j}) (LI: LargeIndex@{i j} SI): FiniteExistential@{j} SI.
  Proof.
    intros P Q H1 H2 Hor.
    enough (∃ b: bool, ∀ a, if b then P a else Q a) as [[] ?]; eauto.
    eapply can_commute_exists.
    - intros []; eauto.
    - intros a; destruct (Hor a) as [|]; [exists true|exists false]; eauto.
  Qed.

  Global Instance finite_bounded_from_finite `{FiniteIndex SI}: FiniteBoundedExistential SI.
  Proof.
    intros P Q α Pdown Qdown Hor. destruct (finite_index α) as [|[β [Hβα Hleast]]].
    - left; simpl; intros. naive_solver.
    - destruct (Hor β Hβα).
      + left. intros γ Hγ. destruct (Hleast γ Hγ) as [->|]; eauto.
      + right. intros γ Hγ. destruct (Hleast γ Hγ) as [->|]; eauto.
  Qed.
End finite_existential_property.

(* Canonical instances: natural numbers, pairs *)
Section nat_index.
  Lemma le_rc_lt x y: le x y ↔ rc lt x y.
  Proof.
    split.
    - intros [| ->] % Nat.le_lteq; [ by right| by left].
    - intros []; lia.
  Qed.

  Lemma nat_index_mixin: IndexMixin nat lt 0 S.
  Proof.
    constructor.
    - typeclasses eauto.
    - exact lt_wf.
    - intros m n. destruct (lt_eq_lt_dec m n) as [[]|]; eauto.
    - unfold flip; intros [n]; lia.
    - intros; lia.
    - intros; eapply le_rc_lt; auto.
    - intros [|n].
      + right; intros; lia.
      + left; by (exists n).
    - intros; apply proof_irrel.
  Qed.

  Canonical Structure natI : indexT := IndexT nat lt 0 S nat_index_mixin.

  Global Instance: FiniteIndex natI.
  Proof.
    intros [|n]; [left; by intros ? ? % PeanoNat.Nat.nlt_0_r|].
    right; exists n; simpl; split; [lia|]; intros. eapply le_rc_lt; lia.
  Qed.
End nat_index.


Section pair_index.
  Variable (I J: indexT).

  Definition pair_zero : I * J := (zero, zero).

  Definition pair_succ : (I * J) → I * J := λ '(n, m), (n, succ m).

  Definition pair_lt : I * J → I * J → Prop :=
    λ '(n1, m1) '(n2, m2), n1 ≺ n2 ∨ (n1 = n2 ∧ m1 ≺ m2).

  Instance pair_lt_trans: Transitive pair_lt.
  Proof.
    intros [] [] []; simpl; intros [|[]] [|[]]; subst; firstorder.
    - left; etransitivity; eauto.
    - right; split; eauto; by etransitivity.
  Qed.

  Lemma pair_lt_wf: well_founded pair_lt.
  Proof.
    intros [m n]. revert n; induction m using (well_founded_ind (index_lt_wf I)).
    intros n; induction n using (well_founded_ind (index_lt_wf J)).
    constructor. intros [m' n'] [|[->]]; eauto.
  Qed.

  Lemma pair_index_mixin: IndexMixin (I * J) pair_lt pair_zero pair_succ.
  Proof.
    constructor.
    - typeclasses eauto.
    - apply pair_lt_wf.
    - intros [m1 n1] [m2 n2]; simpl.
      destruct (index_lt_eq_lt_dec m1 m2) as [[]|];
        destruct (index_lt_eq_lt_dec n1 n2) as [[]|].
      all: subst; firstorder.
    - intros [[m n] [H1 | [_ H1]]]; eapply index_zero_least; eauto.
    - intros [m n]; simpl. right; split; eauto.
    - intros [m1 n1] [m2 n2]; simpl; intros [|[]]; subst.
      + right. by left.
      + destruct (index_succ_least n1 n2); eauto; subst.
        * by left.
        * right. right. by split.
    - intros [m n]. destruct (index_dec_limit n) as [[n' ->]|].
      + left. by (exists (m, n')).
      + right; intros [m' n']; simpl; intros []; firstorder.
    - intros [i j] [i' j'] [Hlt|[Heq Hlt]] [Hlt'|[Heq' Hlt']]; subst.
      + replace Hlt with Hlt' by apply proof_irrel; done.
      + exfalso; eapply index_lt_irrefl; done.
      + exfalso; eapply index_lt_irrefl; done.
      + replace Heq' with (eq_refl i') by apply proof_irrel.
        replace Hlt with Hlt' by apply proof_irrel; done.
  Qed.

  Canonical Structure pairI : indexT := IndexT (I * J) pair_lt pair_zero pair_succ pair_index_mixin.

  Lemma pair_rc_right n m m': (n, m) ⪯ (n, m') ↔ m  ⪯ m'.
  Proof.
    split; intros [Heq | Heq].
    - injection Heq. auto.
    - destruct Heq as [[]%index_lt_irrefl | H]. right; apply H.
    - subst; auto.
    - right. right; auto.
  Qed.


  Global Instance: TransfiniteIndex pairI.
  Proof.
    exists (λ '(m, n), (succ m, n)). intros k [m n]; simpl.
    replace (Nat.iter k pair_succ (m, n)) with (m, Nat.iter k (index_succ J) n).
    - simpl; left; eapply index_succ_greater.
    - symmetry; induction k; simpl; by rewrite ?IHk.
  Qed.
End pair_index.


(** ** Some Classical Reasoning *)
Lemma classical_dn `{Classical} (X : Prop) : X ↔ ¬ (¬ X).
Proof.
  split; intros ?.
  - tauto.
  - destruct (excluded_middle X) as [H1 | H1]; [easy | tauto].
Qed.

Lemma classical_forall_exists_dn `{Classical} (X : Type) (P : X → Prop): (∀ x, P x) ↔ ¬ (∃ x, ¬ (P x)).
Proof.
  split.
  - intros ? (x & H1). eauto.
  - intros Hx x. destruct (excluded_middle (P x)) as [ | ?]; [easy | ].  exfalso; apply Hx; eauto.
Qed.

Lemma classical_forall_exists `{Classical} (X : Type) (P : X → Prop): ¬ (∀ x, P x) ↔ (∃ x, ¬ (P x)).
Proof.
  by rewrite classical_forall_exists_dn -classical_dn.
Qed.

Lemma classical_exists_forall `{Classical} (X : Type) (P : X → Prop): ¬ (∃ x, (P x)) ↔ (∀ x, ¬ P x).
Proof.
  rewrite classical_forall_exists_dn; split; intros ? [x ?]; eauto using classical_dn.
Qed.

Lemma classical_impl `{Classical} (P Q : Prop): ¬ (P → Q) ↔ (P ∧ ¬ Q).
Proof.
  destruct (excluded_middle Q), (excluded_middle P); tauto.
Qed.

Lemma find_least `{Classical} {SI: indexT} (P: SI → Prop) α:
  (∀ α β, α ⪯ β → P β → P α) →
  P α →
  ∃ β, P β ∧ ∀ γ, γ ≺ β → ¬ P γ.
Proof.
  intros HP. induction (index_lt_wf SI α) as [α _ IH].
  intros Hα. destruct (excluded_middle (∀ γ, γ ≺ α → ¬ P γ)) as [|Hn]; eauto.
  apply ->classical_forall_exists in Hn. destruct Hn as [β Hβ].
  apply ->classical_impl in Hβ. destruct Hβ as [Hαβ Hβ].
  apply classical_dn in Hβ.
  apply (IH _ Hαβ Hβ).
Qed.

(* better support for recursion on indexes *)

Lemma index_strong_ind {SI : indexT} (P : SI → Prop) :
  P zero →
  (∀ α, (∀ β, β ⪯ α → P β) → P (succ α)) →
  (∀ α : limit_idx SI, (∀ β, β ≺ α → P β) → P α) →
  ∀ α, P α.
Proof.
  intros Pz Ps Pl α.
  induction (index_lt_wf _ α) as [α _ IHα].
  destruct (index_is_zero α) as [->| Hnz]; first done.
  destruct (index_dec_limit α) as [[β ->]|Hil].
  - apply Ps; intros ??. apply IHα.
    by eapply index_le_lt_trans; last apply index_succ_greater.
  - apply (Pl (mklimitidx α Hil Hnz)); intros; apply IHα; done.
Qed.

Lemma index_ind {SI : indexT} (P : SI → Prop) :
  P zero →
  (∀ α, P α → P (succ α)) →
  (∀ α : limit_idx SI, (∀ β, β ≺ α → P β) → P α) →
  ∀ α, P α.
Proof.
  intros Pz Ps Pl α; induction α using index_strong_ind; auto.
Qed.

Lemma index_destruct {SI : indexT} (P : SI → Prop) :
  P zero →
  (∀ α, P (succ α)) →
  (∀ α : limit_idx SI, P α) →
  ∀ α, P α.
Proof. intros; apply index_ind; done. Qed.

(** ** Automation *)

Create HintDb index.
Hint Extern 1 False => eapply index_lt_irrefl : index.
Hint Resolve -> index_succ_iff : index.
Hint Constructors rc : index.
(* TODO: maybe remove the transitivity stuff *)
Hint Extern 2 (_ ≺ _) => etransitivity : index.
Hint Resolve index_le_lt_trans : index.
Hint Resolve index_lt_le_trans : index.
Hint Resolve index_succ_greater : index.
Hint Resolve index_le_succ_inj : index.
Hint Resolve index_lt_succ_mono : index.
Hint Immediate index_zero_minimum : index.

(** subst fails in some settings with dependent typing, when that happens, we have to do stuff manually *)
Ltac subst_with H :=
  match type of H with
  | ?a = ?b =>
    tryif (match b with context[?c] => constr_eq a c end) then fail else
    (match goal with
    | H0 : _ ≺ _ |- _ => assert_fails (constr_eq H H0); rewrite H in H0
    | H0 : _ ⪯ _ |- _ => assert_fails (constr_eq H H0); rewrite H in H0
    | H0 : _ = _ |- _ => assert_fails (constr_eq H H0); progress (try rewrite H in H0)
    end;
    repeat match goal with
    | H0 : _ ≺ _ |- _ => assert_fails (constr_eq H H0); rewrite H in H0
    | H0 : _ ⪯ _ |- _ => assert_fails (constr_eq H H0); rewrite H in H0
    | H0 : _ = _ |- _ => assert_fails (constr_eq H H0); progress (try rewrite H in H0)
    end)
  end.
Ltac subst_assmpt :=
subst +
(repeat match goal with
| H : ?a = ?b |- _ => is_var a; subst_with H; clear H
| H : ?a = ?b |- _ => is_var b; let H' := fresh H in specialize (symmetry H) as H'; try clear H; subst_with H'; clear H'
end).

Ltac hypot_exists H :=
  match type of H with ?t =>
    match goal with
    | H0 : t |- _ => assert_fails (constr_eq H0 H)
    end
  end.

(* index_contra_solve: solve directly contadictory goals using assumptions on index order*)

Ltac normalise_hypot H :=
  try match type of H with
  | succ ?a ≺ succ ?b => apply index_lt_succ_inj in H
  | succ ?a = succ ?b => apply index_succ_inj in H; repeat subst_assmpt
  end.
Ltac index_contra_solve_core cont :=
  subst_assmpt;
  match goal with
  | [H : ?a ≺ ?a |- _] => specialize (index_lt_irrefl _ H) as []
  | [H : ?a ≺ zero |- _] => by apply index_lt_zero_is_normal in H
  | [H : ?a = succ ?a |- _] => apply index_succ_neq in H as []
  | [H : succ ?a = ?a |- _] => symmetry in H; cont
  | [H : ?a ⪯ zero, H1 : ?b ≺ ?a |- _] => eapply index_lt_zero_is_normal, index_lt_le_trans; [apply H1 | apply H]
  | [H1 : ?a ≺ ?b, H2 : ?b ≺ succ ?a |- _] => specialize (index_lt_succ_tight _ _ H1 H2) as []
  | [H1 : ?a ⪯ ?b, H2 : ?b ≺ ?a |- _] => eapply index_lt_irrefl, index_le_lt_trans; [apply H1 | apply H2]
  | [H : succ ?a = zero |- _] => destruct (index_succ_not_zero _ H) as []
  | [H : zero = succ ?a |- _] => symmetry in H; destruct (index_succ_not_zero _ H) as []
  | [H : succ ?a ≺ ?a |- _] =>
      let H1 := fresh "H" in
        specialize (index_lt_trans _ _ _ H (index_succ_greater a)) as H1;
        apply index_lt_irrefl in H1 as []
  | [H : succ ?a ≺ succ ?b |- _ ] => normalise_hypot H; cont
  | [H : succ ?a = succ ?b |- _ ] => normalise_hypot H; cont
  | [H : succ ?a ⪯ ?b |- _] => destruct H; cont
  end.
(* infer by transitivity -- might be very expensive when many inferences can be done or even diverge *)
Ltac index_contra_solve_infer cont :=
  match goal with
  | [H1 : ?a ≺ ?b, H2 : ?b ≺ ?c |- _] =>
      let H := fresh "H" in
        specialize (index_lt_trans _ _ _ H1 H2) as H; normalise_hypot H;
        tryif (hypot_exists H) then fail else cont
  end.
Ltac index_contra_solve :=
  exfalso;
  index_contra_solve_core index_contra_solve + index_contra_solve_infer index_contra_solve.

(* Do not do any transitivity inferences. A smarter strategy would be to give it a budget for transitivity inferences, but that would be more complicated *)
Ltac index_contra_solve_fast :=
  exfalso; index_contra_solve_core index_contra_solve_core.
