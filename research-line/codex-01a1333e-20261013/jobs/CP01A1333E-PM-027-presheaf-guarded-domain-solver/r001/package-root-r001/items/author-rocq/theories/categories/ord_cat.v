From SynthDom Require Import prelude.
From SynthDom.categories Require Import category.
From SynthDom Require Import stepindex.

Local Set Universe Polymorphism.
Local Unset Universe Minimization ToSet.

Inductive squashed (P : Prop) : SProp :=
| squash : P → squashed P.
Arguments squash {_}.

Inductive empty : SProp := .

Lemma unsquash {P : Prop} `{!Decision P} (s : squashed P) : P.
Proof.
  destruct (decide P) as [| H]; first done.
  apply empty_ind.
  destruct s.
  exfalso.
  by apply H.
Qed.

Global Instance le_decision {SI : indexT} (α : SI) : ∀  (β : SI),
  Decision (β ⪯ α).
Proof.
  intros β.
  destruct (index_le_lt_dec β α) as [H | H].
  - by left.
  - right; intros contra.
    by eapply index_lt_le_contradict.
Qed.

Global Instance lt_decision {SI : indexT} (α : SI) : ∀  (β : SI),
  Decision (β ≺ α).
Proof.
  intros β.
  destruct (index_le_lt_dec α β) as [H | H].
  - right; intros contra.
    by eapply index_lt_le_contradict.
  - by left.
Qed.

Open Scope category_scope.

Lemma index_succ_le_lt1 : ∀ {I : indexT} (α β : I), succ α ⪯ β → α ≺ β.
Proof. intros; apply index_succ_le_lt; done. Qed.
Lemma index_succ_le_lt2 : ∀ {I : indexT} (α β : I), α ≺ β → succ α ⪯ β.
Proof. intros; apply index_succ_le_lt; done. Qed.

Global Instance index_le_equiv (SI : indexT) (α β : SI) : Equiv (α ⪯ β) := λ _ _, True.

Program Definition OrdCat (SI : indexT) : category :=
  MkCat SI (λ α β, α ⪯ β)
    (λ _, reflexivity _)
    (λ _ _ _ f g, transitivity f g)
    _ _ _.
Next Obligation.
  intros; simpl.
  apply proof_irrelevance.
Qed.
Next Obligation.
  intros; simpl.
  apply proof_irrelevance.
Qed.
Next Obligation.
  intros; simpl.
  apply proof_irrelevance.
Qed.
Fail Next Obligation.

(* successor as a functor *)

Program Definition Succ SI : functor (OrdCat SI) (OrdCat SI) :=
  MkFunc (λ α, succ α) (λ _ _ h, index_le_succ_mono _ _ h) _ _.
Next Obligation.
  intros; simpl.
  apply proof_irrelevance.
Qed.
Next Obligation.
  intros; simpl.
  apply proof_irrelevance.
Qed.

Program Definition ord_pred {SI : indexT} : index_rect (λ _ : SI, SI) :=
  MkIR zero (λ α _, α) (λ α _, α) _.
Next Obligation. done. Qed.
Fail Next Obligation.

Lemma ord_pred_le {SI : indexT} (α : SI) : ord_pred α ⪯ α.
Proof.
  destruct α using index_destruct; simpl_index_rect; [done| |done].
  apply index_lt_le_subrel, index_succ_greater.
Qed.

Lemma ord_pred_mono {SI : indexT} {α β : SI} : α ⪯ β → ord_pred α ⪯ ord_pred β.
Proof.
  intros Hαβ.
  destruct β as [|β|β]using index_destruct; simpl_index_rect.
  - etrans; first apply ord_pred_le.
    by simpl_index_rect.
  - destruct α as [|α|]using index_destruct; simpl_index_rect.
    + apply index_zero_minimum.
    + apply index_le_succ_inj; done.
    + assert (index_is_limit α) as Hil by apply α.
      pose proof (index_limit_not_succ α Hil β).
      apply index_le_eq_or_lt in Hαβ as [?|?%index_succ_iff_proj_r2l]; done.
  - destruct α as [|α|]using index_destruct; simpl_index_rect; last done.
    + apply index_zero_minimum.
    + etrans; last apply Hαβ.
      apply index_lt_le_subrel, index_succ_greater.
Qed.

Program Definition Pred SI : functor (OrdCat SI) (OrdCat SI) :=
  MkFunc (λ α, ord_pred α) (λ _ _ h, ord_pred_mono h) _ _.
Next Obligation.
  intros; simpl.
  apply proof_irrelevance.
Qed.
Next Obligation.
  intros; simpl.
  apply proof_irrelevance.
Qed.

Polymorphic Record downset_pred (SI : indexT) := MkDownSetPred {
  dsp_pred :> SI → Prop;
  dsp_pred_dec : ∀ α, Decision (dsp_pred α);
  dsp_pred_downwards : ∀ α β, α ⪯ β → dsp_pred β → dsp_pred α;
}.
Existing Instance dsp_pred_dec.

Global Arguments MkDownSetPred {_} _ _.
Global Arguments dsp_pred {_} _ _.
Global Arguments dsp_pred_dec {_} _ _.
Global Arguments dsp_pred_downwards {_} _ {_ _} _ _.

Lemma dsp_lt {SI} {dsp : downset_pred SI} {α β} : α ≺ β → dsp β → dsp α.
Proof. intros ? ?; eapply dsp_pred_downwards; [|eassumption]; apply index_lt_le_subrel; done. Qed.

Lemma dsp_unsucc {SI} {dsp : downset_pred SI} {α} : dsp (succ α) → dsp α.
Proof. intros ?; eapply dsp_lt; eauto. Qed.

Program Definition total_dsp SI : downset_pred SI := MkDownSetPred (λ _, True) _ _.
Solve All Obligations with done.
Fail Next Obligation.
Program Definition le_dsp {SI} α : downset_pred SI := MkDownSetPred (λ β, β ⪯ α ) _ _.
Next Obligation. intros ??????; simpl in *; etrans; eauto. Qed.
Fail Next Obligation.
Program Definition lt_dsp {SI} α : downset_pred SI := MkDownSetPred (λ β, β ≺ α ) _ _.
Next Obligation. intros ??????; simpl in *; eapply index_le_lt_trans; eauto. Qed.
Fail Next Obligation.

Definition dsp_included {SI} (dsp dsp' : downset_pred SI) := ∀ α, dsp α → dsp' α.

#[projections(primitive = yes)] Record downset {SI} (dsp : downset_pred SI) := MkDS {
  ds_idx :> SI;
  ds_in_dsp : squashed (dsp ds_idx);
}.
Global Arguments MkDS {_ _ _} _, {_} _ {_} _.
Global Arguments ds_idx {_ _} _.
Global Arguments ds_in_dsp {_ _} _.

Lemma downset_eq {SI} {dsp : downset_pred SI} (ds ds' : downset dsp) : ds = ds' :> SI → ds = ds'.
Proof. destruct ds; destruct ds'; simpl; intros ->; reflexivity. Qed.

Definition fun_on_empty_set {SI} (α : @downset SI (lt_dsp zero)) (T : Type) : T :=
  False_rect T (index_lt_zero_is_normal _ (unsquash (ds_in_dsp α))).

Lemma empty_dsp_included {SI} {dsp : downset_pred SI} : dsp_included (lt_dsp zero) dsp.
Proof. intros ??; simpl in *; exfalso; eapply index_lt_zero_is_normal; eauto. Qed.
Lemma lt_dsp_included {SI} {dsp : downset_pred SI} (α : downset dsp) : dsp_included (lt_dsp α) dsp.
Proof. intros ??; eapply dsp_pred_downwards; [|apply (unsquash (ds_in_dsp α))]; eauto. Qed.
Lemma le_dsp_included {SI} {dsp : downset_pred SI} (α : downset dsp) : dsp_included (le_dsp α) dsp.
Proof. intros ??; eapply dsp_pred_downwards; [|apply (unsquash (ds_in_dsp α))]; eauto. Qed.

Definition dsp_include {SI} {dsp dsp' : downset_pred SI} (incl : dsp_included dsp dsp')
  (d : downset dsp) : downset dsp' := MkDS (squash (incl _ (unsquash (ds_in_dsp d)))).

Lemma le_dsp_included_eq {SI} {dsp : downset_pred SI} (α : downset dsp) :
  α = dsp_include (le_dsp_included α) (MkDS (le_dsp α) (squash (reflexivity _))).
Proof. destruct α; rewrite /dsp_include /=; reflexivity. Qed.

Definition dsp_include_le {SI} {dsp dsp' : downset_pred SI} (incl : dsp_included dsp dsp')
  {d d' : downset dsp} (Hle : d ⪯ d') : (dsp_include incl d) ⪯ (dsp_include incl d').
Proof. done. Defined.

Definition dsp_include_le_refl {SI} {dsp dsp' : downset_pred SI} (incl : dsp_included dsp dsp')
  {d : downset dsp} : (dsp_include_le incl (reflexivity (d : SI))) = reflexivity _.
Proof. reflexivity. Qed.

Program Definition OrdDSCat {SI} (dsp : downset_pred SI) : category :=
  MkCat (downset dsp) (λ α β, α ⪯ β)
    (λ α, reflexivity (α : SI))
    (λ α β γ (f : α ⪯ β) (g : β ⪯ γ), transitivity f g)
    _ _ _.
Next Obligation.
  intros; apply proof_irrelevance.
Qed.
Next Obligation.
  intros; apply proof_irrelevance.
Qed.
Next Obligation.
  intros; apply proof_irrelevance.
Qed.
Fail Next Obligation.

Program Definition lift_func {SI} (dsp : downset_pred SI) {C} (F : functor ((OrdCat SI)ᵒᵖ) C) :
  functor ((OrdDSCat dsp)ᵒᵖ) C :=
  MkFunc (λ α, F ₒ (ds_idx α)) (λ _ _ f, F ₕ f) _ _.
Next Obligation.
Proof. intros ???? [] [] []; rewrite /=; intros ??; rewrite h_map_comp //. Qed.
Next Obligation.
Proof. intros ???? []; rewrite /= h_map_id //. Qed.
Fail Next Obligation.

Program Definition unlift_func {SI} {C} (F : functor ((OrdDSCat (total_dsp SI))ᵒᵖ) C) :
  functor ((OrdCat SI)ᵒᵖ) C :=
  MkFunc
    (λ α, F ₒ (ds_idx (@MkDS SI (total_dsp SI) α (squash I))))
    (λ α β f, F ₕ (f : (@MkDS SI (total_dsp SI) β (squash I)) ⪯ (@MkDS SI (total_dsp SI) α (squash I))))
    _ _.
Next Obligation.
Proof. repeat intros ?; rewrite /= -h_map_comp; f_equiv; done. Qed.
Next Obligation.
Proof. repeat intros ?; rewrite /= h_map_id //. Qed.
Fail Next Obligation.

Program Definition lift_natural {SI} (dsp : downset_pred SI) {C}
  {F G : functor ((OrdCat SI)ᵒᵖ) C} (η : natural F G) :
  natural (lift_func dsp F) (lift_func dsp G) :=
  MkNat (λ α, η ₙ (α : SI)) _.
Next Obligation.
Proof. repeat intros ?; rewrite /= naturality //. Qed.
Fail Next Obligation.

Program Definition unlift_natural {SI} {C} {F G : functor ((OrdCat SI)ᵒᵖ) C}
  (η : natural (lift_func (total_dsp SI) F) (lift_func (total_dsp SI) G)) :
  natural F G :=
  MkNat (λ α, η ₙ (@MkDS SI (total_dsp SI) α (squash I))) _.
Next Obligation.
Proof.
  intros ?? F G η α β Hle; rewrite /=.
  rewrite (naturality η
    (Hle : (@MkDS SI (total_dsp SI) β (squash I)) ⪯ (@MkDS SI (total_dsp SI) α (squash I)))) //.
Qed.
Fail Next Obligation.

Definition lift_in_lt_ds
  {SI : indexT} {α β : SI} (Hle : β ⪯ α) (γ : downset (lt_dsp β)) : downset (lt_dsp α) :=
  MkDS (lt_dsp α) (squash (index_lt_le_trans _ _ _ (unsquash (ds_in_dsp γ)) Hle)).

Lemma in_lt_dsp_le {SI : indexT} {α β : SI} :
  β ⪯ α → ∀ γ : downset (lt_dsp β), γ ⪯ α.
Proof.
  intros ? γ; etrans; last eassumption.
  apply index_lt_le_subrel, (unsquash (ds_in_dsp γ)).
Qed.

Lemma in_lt_dsp_succ {SI : indexT} (α : SI) : ∀ β : downset (lt_dsp (succ α)), β ⪯ α.
Proof. intros ?; apply index_succ_iff_proj_r2l, (unsquash (ds_in_dsp β)). Qed.

Lemma in_lt_dsp {SI : indexT} (α : SI) : ∀ β : downset (lt_dsp α), β ⪯ α.
Proof. intros ?; apply index_lt_le_subrel, (unsquash (ds_in_dsp β)). Qed.

Section extend_ord_ds_cat_func.
  Context {SI : indexT} {C : category} {α : SI} {F : functor ((OrdDSCat (lt_dsp α))ᵒᵖ) C}
    (cn : cone F).

  Definition extend_ord_ds_cat_func_o_map (β : downset (le_dsp α)) : obj C :=
    match index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β)) with
    | left Hlt => F ₒ (MkDS (lt_dsp α) (squash Hlt))
    | right _ => vertex cn
    end.

  Lemma extend_ord_ds_cat_func_o_map_lt {β : downset (le_dsp α)} (Hlt : β ≺ α) :
    extend_ord_ds_cat_func_o_map β = F ₒ (MkDS (lt_dsp α) (squash Hlt)).
  Proof.
    rewrite /extend_ord_ds_cat_func_o_map; destruct index_le_lt_eq_dec as [Hlt'| Heq].
    - reflexivity.
    - exfalso; eapply index_lt_le_contradict; first exact Hlt.
      rewrite Heq; done.
  Qed.

  Lemma extend_ord_ds_cat_func_o_map_at {β : downset (le_dsp α)} (Heq : β = α :> SI) :
    extend_ord_ds_cat_func_o_map β = vertex cn.
  Proof.
    rewrite /extend_ord_ds_cat_func_o_map; destruct index_le_lt_eq_dec as [Hlt| Heq'];
      last done.
    exfalso; eapply index_lt_le_contradict; first exact Hlt.
    rewrite Heq; done.
  Qed.

  Program Definition extend_ord_ds_cat_func_h_map {β γ : downset (le_dsp α)} (Hle : β ⪯ γ) :
    hom (extend_ord_ds_cat_func_o_map γ) (extend_ord_ds_cat_func_o_map β) :=
    match index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp γ))
          return hom (extend_ord_ds_cat_func_o_map γ) (extend_ord_ds_cat_func_o_map β) with
    | left Hlt =>
        match index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))
              return hom (extend_ord_ds_cat_func_o_map γ) (extend_ord_ds_cat_func_o_map β) with
        | left Hlt' =>
            (hom_trans
               (eq_sym (extend_ord_ds_cat_func_o_map_lt Hlt))
               (eq_sym (extend_ord_ds_cat_func_o_map_lt Hlt'))
               (@h_map _ _ F (MkDS (lt_dsp α) (squash Hlt)) (MkDS (lt_dsp α) (squash Hlt')) Hle))
        | right Heq =>
            False_rect _
              (index_lt_le_contradict _ _ Hlt
                 match Heq in _ = z return z ⪯ γ with eq_refl => Hle end)
        end
    | right Heq =>
        match index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))
              return hom (extend_ord_ds_cat_func_o_map γ) (extend_ord_ds_cat_func_o_map β) with
        | left Hlt' =>
            (hom_trans
               (eq_sym (extend_ord_ds_cat_func_o_map_at Heq))
               (eq_sym (extend_ord_ds_cat_func_o_map_lt Hlt'))
               (side cn (MkDS (lt_dsp α) (squash Hlt'))))
        | right Heq' =>
            (hom_trans
               (eq_sym (extend_ord_ds_cat_func_o_map_at Heq))
               (eq_sym (extend_ord_ds_cat_func_o_map_at Heq'))
               (id (vertex cn)))
        end
    end.

  Lemma extend_ord_ds_cat_func_h_map_lt_lt {β γ : downset (le_dsp α)} (Hle : β ⪯ γ)
    (Hlt : β ≺ α) (Hlt' : γ ≺ α) :
    extend_ord_ds_cat_func_h_map Hle =
      hom_trans
        (eq_sym (extend_ord_ds_cat_func_o_map_lt Hlt'))
        (eq_sym (extend_ord_ds_cat_func_o_map_lt Hlt))
        (@h_map _ _ F (MkDS (lt_dsp α) (squash Hlt')) (MkDS (lt_dsp α) (squash Hlt)) Hle).
  Proof.
    rewrite /extend_ord_ds_cat_func_h_map.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))) as [Hltβ|Heqβ];
      destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp γ))) as [Hltγ|Heqγ];
      try destruct index_lt_le_contradict.
    - replace Hltγ with Hlt' by apply proof_irrel;
        replace Hltβ with Hlt by apply proof_irrel; done.
    - exfalso; eapply index_lt_le_contradict; first by apply Hlt'.
      rewrite Heqγ; done.
    - exfalso; eapply index_lt_le_contradict; first by apply Hlt'.
      rewrite Heqγ; done.
  Qed.

  Lemma extend_ord_ds_cat_func_h_map_lt_eq {β γ : downset (le_dsp α)} (Hle : β ⪯ γ)
    (Hlt : β ≺ α) (Heq : γ = α :> SI) :
    extend_ord_ds_cat_func_h_map Hle =
      hom_trans
        (eq_sym (extend_ord_ds_cat_func_o_map_at Heq))
        (eq_sym (extend_ord_ds_cat_func_o_map_lt Hlt))
        (side cn (MkDS (lt_dsp α) (squash Hlt))).
  Proof.
    rewrite /extend_ord_ds_cat_func_h_map.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))) as [Hltβ|Heqβ];
      destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp γ))) as [Hltγ|Heqγ];
      try destruct index_lt_le_contradict.
    - exfalso; eapply index_lt_le_contradict; first by apply Hltγ.
      rewrite Heq; done.
    - replace Heqγ with Heq by apply proof_irrel;
        replace Hltβ with Hlt by apply proof_irrel; done.
    - exfalso; eapply index_lt_le_contradict; first by apply Hlt.
      rewrite Heqβ; done.
  Qed.

  Lemma extend_ord_ds_cat_func_h_map_eq_eq {β γ : downset (le_dsp α)} (Hle : β ⪯ γ)
    (Heq : β = α :> SI) (Heq' : γ = α :> SI) :
    extend_ord_ds_cat_func_h_map Hle =
      hom_trans
        (eq_sym (extend_ord_ds_cat_func_o_map_at Heq'))
        (eq_sym (extend_ord_ds_cat_func_o_map_at Heq))
        (id (vertex cn)).
  Proof.
    rewrite /extend_ord_ds_cat_func_h_map.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))) as [Hltβ|Heqβ];
      destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp γ))) as [Hltγ|Heqγ];
      try destruct index_lt_le_contradict.
    - exfalso; eapply index_lt_le_contradict; first by apply Hltγ.
      rewrite Heq'; done.
    - exfalso; eapply index_lt_le_contradict; first by apply Hltβ.
      rewrite Heq; done.
    - replace Heqγ with Heq' by apply proof_irrel;
        replace Heqβ with Heq by apply proof_irrel; done.
  Qed.

  Ltac simplify_extend_ord_ds_cat_func_h_map :=
    match goal with
    |- context [extend_ord_ds_cat_func_h_map ?Hle] =>
      match type of Hle with
      | ?A ⪯ ?B =>
          match goal with
          | HltB : B ≺ α |- _ =>
              match goal with
              | HltA : A ≺ α |- _ =>
                  rewrite (extend_ord_ds_cat_func_h_map_lt_lt _ HltA HltB)
              | HeqA : A = α |- _ =>
                  exfalso; eapply index_lt_le_contradict; [by apply HltB|by rewrite -{1}HeqA]
              end
          | HeqB : B = α |- _ =>
              match goal with
              | HltA : A ≺ α |- _ =>
                  rewrite (extend_ord_ds_cat_func_h_map_lt_eq _ HltA HeqB)
              | HeqA : A = α |- _ =>
                  rewrite (extend_ord_ds_cat_func_h_map_eq_eq _ HeqA HeqB)
              end
          end
      end
    end.

  Program Definition extend_ord_ds_cat_func : functor ((OrdDSCat (le_dsp α))ᵒᵖ) C :=
    MkFunc extend_ord_ds_cat_func_o_map (λ _ _ f, extend_ord_ds_cat_func_h_map f) _ _.
  Next Obligation.
    intros β γ δ Hγβ Hδγ; simpl in *.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))) as [Hltβ|Heqβ];
      destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp γ))) as [Hltγ|Heqγ];
      destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp δ))) as [Hltδ|Heqδ];
      repeat simplify_extend_ord_ds_cat_func_h_map.
    - rewrite (@h_map_comp _ _ F (MkDS (lt_dsp α) (squash Hltβ)) (MkDS (lt_dsp α) (squash Hltγ))).
      rewrite hom_trans_compose /=.
      rewrite !hom_trans_compose_take_in_l -!hom_trans_trans.
      rewrite !eq_trans_refl_r eq_trans_sym_inv_r //.
    - rewrite !hom_trans_compose_take_in_l -!hom_trans_trans eq_trans_sym_inv_r /=.
      rewrite !hom_trans_compose_take_in_r /= hom_trans_refl.
      rewrite -side_commutes.
      rewrite -!hom_trans_trans eq_trans_refl_r eq_trans_refl_l //.
    - rewrite !hom_trans_compose_take_in_l -!hom_trans_trans !eq_trans_sym_inv_r /=.
      rewrite right_id //.
    - rewrite !hom_trans_compose_take_in_l -!hom_trans_trans !eq_trans_sym_inv_r /=.
      rewrite right_id //.
  Qed.
  Next Obligation.
    intros β; simpl.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))) as [Hltβ|Heqβ];
      simplify_extend_ord_ds_cat_func_h_map.
    - rewrite h_map_id hom_trans_id //.
    - rewrite hom_trans_id //.
  Qed.
  Fail Next Obligation.

End extend_ord_ds_cat_func.

Ltac simplify_extend_ord_ds_cat_func_h_map :=
  match goal with
    |- context [@extend_ord_ds_cat_func_h_map _ _ ?α _ _ _ _ ?Hle] =>
      match type of Hle with
      | ?A ⪯ ?B =>
          match goal with
          | HltB : B ≺ α |- _ =>
              match goal with
              | HltA : A ≺ α |- _ =>
                  rewrite (extend_ord_ds_cat_func_h_map_lt_lt _ _ HltA HltB)
              | HeqA : A = α |- _ =>
                  exfalso; eapply index_lt_le_contradict; [by apply HltB|by rewrite -{1}HeqA]
              end
          | HeqB : B = α |- _ =>
              match goal with
              | HltA : A ≺ α |- _ =>
                  rewrite (extend_ord_ds_cat_func_h_map_lt_eq _ _ HltA HeqB)
              | HeqA : A = α |- _ =>
                  rewrite (extend_ord_ds_cat_func_h_map_eq_eq _ _ HeqA HeqB)
              end
          end
      end
  end.

Section extend_ord_ds_cat_nat.
  Context {SI : indexT} {C : category} {α : SI}
    {F : functor ((OrdDSCat (lt_dsp α))ᵒᵖ) C} {cn : cone F}
    {F' : functor ((OrdDSCat (lt_dsp α))ᵒᵖ) C} {cn' : cone F'}
    (η : natural F F') (h : hom (vertex cn) (vertex cn'))
    (Hηh : ∀ α, (η ₙ α) ∘ side cn α = side cn' α ∘ h).

  Definition extend_ord_ds_cat_nat_map β :
    hom (extend_ord_ds_cat_func_o_map cn β) (extend_ord_ds_cat_func_o_map cn' β) :=
    match index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β)) return
          hom
            (extend_ord_ds_cat_func_o_map cn β)
            (extend_ord_ds_cat_func_o_map cn' β) with
    | left Hlt =>
        hom_trans
          (eq_sym (extend_ord_ds_cat_func_o_map_lt cn Hlt))
          (eq_sym (extend_ord_ds_cat_func_o_map_lt cn' Hlt))
          (η ₙ (MkDS (lt_dsp α) (squash Hlt)))
    | right Heq =>
        hom_trans
          (eq_sym (extend_ord_ds_cat_func_o_map_at cn Heq))
          (eq_sym (extend_ord_ds_cat_func_o_map_at cn' Heq))
          h
    end.

  Lemma extend_ord_ds_cat_nat_map_lt {β : downset (le_dsp α)} (Hlt : β ≺ α) :
    extend_ord_ds_cat_nat_map β =
      hom_trans
      (eq_sym (extend_ord_ds_cat_func_o_map_lt cn Hlt))
      (eq_sym (extend_ord_ds_cat_func_o_map_lt cn' Hlt))
      (η ₙ (MkDS (lt_dsp α) (squash Hlt))).
  Proof.
    rewrite /extend_ord_ds_cat_nat_map /=.
    destruct (index_le_lt_eq_dec _ _ (unsquash _)) as [Hltβ|Heqβ];
      repeat simplify_extend_ord_ds_cat_func_h_map.
    - replace Hltβ with Hlt by apply proof_irrel; done.
    - exfalso; eapply index_lt_le_contradict; [by apply Hlt|by rewrite -{1}Heqβ].
  Qed.

  Lemma extend_ord_ds_cat_nat_map_at {β : downset (le_dsp α)} (Heq : β = α :> SI) :
    extend_ord_ds_cat_nat_map β =
      hom_trans
      (eq_sym (extend_ord_ds_cat_func_o_map_at cn Heq))
      (eq_sym (extend_ord_ds_cat_func_o_map_at cn' Heq))
      h.
  Proof.
    rewrite /extend_ord_ds_cat_nat_map /=.
    destruct (index_le_lt_eq_dec _ _ (unsquash _)) as [Hltβ|Heqβ];
      repeat simplify_extend_ord_ds_cat_func_h_map.
    - exfalso; eapply index_lt_le_contradict; [by apply Hltβ|by rewrite -{1}Heq].
    - replace Heqβ with Heq by apply proof_irrel; done.
  Qed.

  Program Definition extend_ord_ds_cat_nat :
    natural (extend_ord_ds_cat_func cn) (extend_ord_ds_cat_func cn') :=
    MkNat extend_ord_ds_cat_nat_map _.
  Next Obligation.
    intros β γ Hle; simpl in *.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))) as [Hltβ|Heqβ];
      destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp γ))) as [Hltγ|Heqγ];
      repeat simplify_extend_ord_ds_cat_func_h_map.
    - rewrite (extend_ord_ds_cat_nat_map_lt Hltβ)
        (extend_ord_ds_cat_nat_map_lt Hltγ).
      rewrite !hom_trans_compose_take_in_l.
      rewrite -!hom_trans_trans !eq_trans_sym_inv_r eq_trans_refl_r.
      rewrite !hom_trans_compose_take_in_r.
      rewrite -!hom_trans_trans !eq_trans_refl_r /= !hom_trans_refl.
      rewrite naturality //.
    - rewrite (extend_ord_ds_cat_nat_map_at Heqβ)
        (extend_ord_ds_cat_nat_map_lt Hltγ).
      rewrite !hom_trans_compose_take_in_l.
      rewrite -!hom_trans_trans !eq_trans_sym_inv_r eq_trans_refl_r.
      rewrite !hom_trans_compose_take_in_r.
      rewrite -!hom_trans_trans !eq_trans_refl_r /= !hom_trans_refl.
      rewrite Hηh //.
    - rewrite (extend_ord_ds_cat_nat_map_at Heqβ)
        (extend_ord_ds_cat_nat_map_at Heqγ).
      rewrite !hom_trans_compose_take_in_l.
      rewrite -!hom_trans_trans !eq_trans_sym_inv_r eq_trans_refl_r.
      rewrite !hom_trans_compose_take_in_r.
      rewrite -!hom_trans_trans !eq_trans_refl_r /= !hom_trans_refl.
      rewrite left_id right_id //.
  Qed.
  Fail Next Obligation.

End extend_ord_ds_cat_nat.

Section cut_ord_ds_cat_func.
  Context {SI : indexT} {dsp : downset_pred SI} (dsp' : downset_pred SI)
    (Hdsps : dsp_included dsp' dsp) {C : category} (F : functor ((OrdDSCat dsp)ᵒᵖ) C).

  Definition cut_ord_ds_cat_func_o_map (β : downset dsp') : obj C :=
    F ₒ (dsp_include Hdsps β).

  Definition cut_ord_ds_cat_func_h_map {β γ : downset dsp'} (Hle : β ⪯ γ) :
    hom (cut_ord_ds_cat_func_o_map γ) (cut_ord_ds_cat_func_o_map β) :=
    F ₕ (dsp_include_le Hdsps Hle).

  Program Definition cut_ord_ds_cat_func : functor ((OrdDSCat dsp')ᵒᵖ) C :=
    MkFunc cut_ord_ds_cat_func_o_map (λ _ _ f, cut_ord_ds_cat_func_h_map f) _ _.
  Next Obligation.
    intros ?????; rewrite /= /cut_ord_ds_cat_func_h_map -h_map_comp; f_equiv; done.
  Qed.
  Next Obligation.
    intros ?; rewrite /= /cut_ord_ds_cat_func_h_map dsp_include_le_refl h_map_id; done.
  Qed.
  Fail Next Obligation.

End cut_ord_ds_cat_func.

Section cut_ord_ds_cat_nat.
  Context {SI : indexT} {dsp : downset_pred SI} (dsp' : downset_pred SI)
    (Hdsps : dsp_included dsp' dsp) {C : category} {F F' : functor ((OrdDSCat dsp)ᵒᵖ) C}
    (η : natural F F').

  Definition cut_ord_ds_cat_nat_map β :
    hom (cut_ord_ds_cat_func_o_map dsp' Hdsps F β) (cut_ord_ds_cat_func_o_map dsp' Hdsps F' β) :=
    η ₙ (MkDS (squash (Hdsps _ (unsquash (ds_in_dsp β))))).

  Program Definition cut_ord_ds_cat_nat :
    natural (cut_ord_ds_cat_func dsp' Hdsps F) (cut_ord_ds_cat_func dsp' Hdsps F') :=
    MkNat cut_ord_ds_cat_nat_map _.
  Next Obligation.
    intros ???; rewrite /= /cut_ord_ds_cat_func_h_map naturality //.
  Qed.
  Fail Next Obligation.

End cut_ord_ds_cat_nat.

(* Section cut_ord_ds_cat_iso. *)
(*   Context {SI : indexT} {dsp : downset_pred SI} {C : category} *)
(*     (F F' : functor ((OrdDSCat dsp)ᵒᵖ) C) *)
(*     (isos : ∀ α : downset dsp, *)
(*         cut_ord_ds_cat_func _ (le_dsp_included α) F *)
(*         ≃@{FuncCat ((OrdDSCat (le_dsp α))ᵒᵖ) C} *)
(*         cut_ord_ds_cat_func _ (le_dsp_included α) F'). *)

(*   Program Definition cut_le_iso_fw {α β : SI} (Hα : dsp α) (Hβ : dsp β) (Hβα : β ⪯ α) : *)
(*     hom (F ₒ (MkDS Hβ)) (F' ₒ (MkDS Hβ)) := *)
(*     hom_trans *)
(*       _ *)
(*       _ *)
(*       (forward (isos (MkDS Hα)) ₙ (MkDS (le_dsp α) Hβα)). *)
(*   Next Obligation. *)
(*     intros. *)
(*     rewrite /cut_ord_ds_cat_func /cut_ord_ds_cat_func_o_map /dsp_include /=. *)


(*   Lemma cut_le_iso_naturality (α : downset dsp) *)
(*     (β γ : downset (le_dsp α)) (Hle : γ ⪯ β) : *)
(*     (forward (isos (dsp_include (le_dsp_included α) β)) ₙ (MkDS (le_dsp β) Hle)) ∘ *)
(*       (F ₕ (dsp_include_le (le_dsp_included α) Hle)) = *)
(*     F' ₕ (dsp_include_le (le_dsp_included α) Hle) ∘ (forward (isos α) ₙ β). *)
(*   Proof. rewrite -naturality //. Qed. *)


(*   Program Definition cut_le_iso_iso : *)
(*     F ≃@{FuncCat ((OrdDSCat dsp)ᵒᵖ) C} F' := *)
(*     MkIsoIc *)
(*       (MkNat (λ α, hom_trans *)
(*          (o_map_eq F (eq_sym (le_dsp_included_eq α))) *)
(*          (o_map_eq F' (eq_sym (le_dsp_included_eq α))) *)
(*          (forward (isos α) ₙ (MkDS (le_dsp α) (reflexivity _)))) _) *)
(*       (MkNat (λ α, hom_trans *)
(*          (o_map_eq F' (eq_sym (le_dsp_included_eq α))) *)
(*          (o_map_eq F (eq_sym (le_dsp_included_eq α))) *)
(*          (backward (isos α) ₙ (MkDS (le_dsp α) (reflexivity _)))) _) *)
(*       _. *)
(*   Next Obligation. *)
(*     intros α β Hle; simpl in *. *)
(*     rewrite hom_trans_compose_take_in_l hom_trans_compose_take_in_r. *)
(*     rewrite !o_map_eq_sym !eq_sym_involutive. *)
(*     rewrite h_map_eq_l h_map_eq_r. *)
(*     apply hom_trans_sym'. *)

(*     etrans; last apply (cut_le_iso_naturality α (MkDS (le_dsp α) (reflexivity _)) (MkDS (le_dsp α) Hle)). *)

(*     replace (@hom_trans ((OrdDSCat dsp)ᵒᵖ) _ _ _ _ (le_dsp_included_eq α) eq_refl Hle) with *)
(*       (@dsp_include_le _ _ _ (le_dsp_included α) (MkDS (le_dsp α) Hle) (MkDS (le_dsp α) (reflexivity _)) Hle) by apply proof_irrel. *)

(*     pose proof (cut_le_iso_naturality α (MkDS (le_dsp α) (reflexivity _)) (MkDS (le_dsp α) Hle)). *)


(*     pose proof (@hom_trans ((OrdDSCat dsp)ᵒᵖ) _ _ _ _ (le_dsp_included_eq α) eq_refl Hle). *)
(*     pose proof (@dsp_include_le _ _ _ (le_dsp_included α) (MkDS (le_dsp α) Hle) (MkDS (le_dsp α) (reflexivity _)) Hle). *)
(*     simpl in *. *)

(*     assert (dsp_include (le_dsp_included α) (MkDS (le_dsp α) Hle) *)
(*            ⪯ dsp_include (le_dsp_included α) (MkDS (le_dsp α) (reflexivity _))). *)
(*     { eapply . } *)


(*     pose proof (@hom_trans ((OrdDSCat dsp)ᵒᵖ) _ _ _ _ (le_dsp_included_eq α) eq_refl Hle). *)
(*     simpl in *. *)

(*     match goal with *)
(*     |- context [@h_map _ _ F' ?B ?C ?Hz ∘ (forward (isos _) ₙ ?A)] => *)
(*       pose proof (@h_map _ _ F' B C Hz); *)
(*       pose B; *)
(*       pose A; *)
(*       pose proof (@naturality _ _ _ _ (forward (isos α)) A) *)
(*     end. *)




(*   Program Definition cut_le_iso_iso *)
(*     (isos : ∀ α : downset dsp, cut_ord_ds_cat_func _ (le_dsp_included α) F *)
(*       ≃@{FuncCat ((OrdDSCat (le_dsp α))ᵒᵖ) C} *)
(*       cut_ord_ds_cat_func _ (le_dsp_included α) F') : *)
(*     F ≃@{FuncCat ((OrdDSCat dsp)ᵒᵖ) C} F' := *)
(*     MkIsoIc *)
(*       (MkNat (λ α, *)
(*            hom_trans *)
(*              (o_map_eq F (eq_sym (le_dsp_included_eq α))) *)
(*              (o_map_eq F' (eq_sym (le_dsp_included_eq α))) *)
(*              (forward (isos α) ₙ _)) _) *)
(*       (MkNat (λ α, *)
(*            hom_trans *)
(*              (o_map_eq F (eq_sym (le_dsp_included_eq α))) *)
(*              (o_map_eq F' (eq_sym (le_dsp_included_eq α))) *)
(*              (backward (isos α) ₙ (MkDS (le_dsp _) (reflexivity _)))) _) _. *)
(*   Next Obligation. *)
(*     intros. *)
(*     simpl in *. *)

(*     intros isos α β Hle; simpl in *. *)
(*     rewrite hom_trans_compose_take_in_l hom_trans_compose_take_in_r. *)
(*     rewrite !o_map_eq_sym !eq_sym_involutive. *)
(*     rewrite h_map_eq_l h_map_eq_r. *)
(*     match goal with *)
(*     |- context [@h_map _ _ F' ?B ?C ?Hz ∘ (forward (isos _) ₙ ?A)] => *)
(*       pose proof (@h_map _ _ F' B C Hz); *)
(*       pose B; *)
(*       pose A; *)
(*       pose proof (@naturality _ _ _ _ (forward (isos α)) A) *)
(*     end. *)


(*     rewrite /= /cut_ord_ds_cat_func_o_map /cut_ord_ds_cat_func_h_map /= in Hn. *)
(*     rewrite -Hn. *)

(*     pose proof (F' ₕ (@hom_trans (opposite (@OrdDSCat SI dsp)) α β *)
(*                 (@MkDS SI dsp (@ds_idx SI dsp α) *)
(*                    (@le_dsp_included SI dsp α (@ds_idx SI dsp α) *)
(*                       (@reflexivity (index_car SI) (index_le SI) *)
(*                          (@index_le_refl SI) (@ds_idx SI dsp α)))) β *)
(*                 (@le_dsp_included_eq SI dsp α) *)
(*                 (@eq_refl (obj (opposite (@OrdDSCat SI dsp))) β) Hle)). *)
(*     pose proof (@naturality _ _ _ _ (forward (isos α)) (MkDS (le_dsp _) (reflexivity _)) *)
(*                   (MkDS (le_dsp _) Hle) ) as Hn; *)
(*       rewrite /= /cut_ord_ds_cat_func_o_map /cut_ord_ds_cat_func_h_map /= in Hn. *)



(*  rewrite -Hn. *)

(*      simpl in *. *)
(*     apply hom_trans_sym'. *)
(*     rewrite -hom_trans_trans /= eq_trans_refl_l. *)
(*     rewrite hom_trans_compose_take_in_r hom_trans_refl eq_sym_involutive. *)

(*     intros Hisos [α Hα] [β Hβ] Hle; simpl in *. *)

(*     symmetry; apply hom_trans_sym'; symmetry. *)
(*     rewrite hom_trans_compose -!hom_trans_trans eq_trans_refl_l !eq_sym_involutive. *)

(*     pose (@cut_ord_ds_cat_func_h_map _ _ _ (le_dsp_included α) _ F). *)
(*     unfold cut_ord_ds_cat_func_o_map, cut_ord_ds_cat_func_h_map in h. *)



(*   Program Definition cut_ord_ds_cat_func_iso : *)
(*     cut_ord_ds_cat_func dsp' Hdsps F *)
(*     ≃@{FuncCat (OrdDSCat dsp')ᵒᵖ C} *)
(*     cut_ord_ds_cat_func dsp' Hdsps F' := *)
(*     MkIsoIc *)
(*       (cut_ord_ds_cat_nat dsp' Hdsps (forward iso)) *)
(*       (cut_ord_ds_cat_nat dsp' Hdsps (backward iso)) _. *)
(*   Next Obligation. *)
(*     split; intros ?; [apply (iso_lr (is_iso iso))|apply (iso_rl (is_iso iso))]. *)
(*   Qed. *)
(*   Fail Next Obligation. *)

(* End cut_ord_ds_cat_iso. *)


(* (* Context {SI : indexT} {dsp : downset_pred SI} (dsp' : downset_pred SI) *) *)
(* (*     (Hdsps : ∀ α, dsp' α → dsp α) {C : category} (F F' : functor ((OrdDSCat dsp)ᵒᵖ) C) *) *)
(* (*     (iso : F ≃@{FuncCat ((OrdDSCat dsp)ᵒᵖ) C} F'). *) *)

(* (*   Program Definition cut_ord_ds_cat_func_zero_iso *) *)
(* (*     {SI : indexT} {dsp : downset_pred SI} {C : category} (F F' : functor ((OrdDSCat dsp)ᵒᵖ) C) : *) *)
(* (*     cut_ord_ds_cat_func  F *) *)
(* (*     ≃@{FuncCat (OrdDSCat dsp')ᵒᵖ C} *) *)
(* (*     cut_ord_ds_cat_func dsp' Hdsps F' := *) *)
(* (*     MkIsoIc *) *)
(* (*       (cut_ord_ds_cat_nat dsp' Hdsps (forward iso)) *) *)
(* (*       (cut_ord_ds_cat_nat dsp' Hdsps (backward iso)) _. *) *)
(* (*   Next Obligation. *) *)
(* (*     split; intros ?; [apply (iso_lr (is_iso iso))|apply (iso_rl (is_iso iso))]. *) *)
(* (*   Qed. *) *)
(* (*   Fail Next Obligation. *) *)

(* Section cut_ord_ds_cat_iso. *)
(*   Context {SI : indexT} {dsp : downset_pred SI} (dsp' : downset_pred SI) *)
(*     (Hdsps : ∀ α, dsp' α → dsp α) {C : category} (F F' : functor ((OrdDSCat dsp)ᵒᵖ) C) *)
(*     (iso : F ≃@{FuncCat ((OrdDSCat dsp)ᵒᵖ) C} F'). *)

(*   Program Definition cut_ord_ds_cat_func_iso : *)
(*     cut_ord_ds_cat_func dsp' Hdsps F *)
(*     ≃@{FuncCat (OrdDSCat dsp')ᵒᵖ C} *)
(*     cut_ord_ds_cat_func dsp' Hdsps F' := *)
(*     MkIsoIc *)
(*       (cut_ord_ds_cat_nat dsp' Hdsps (forward iso)) *)
(*       (cut_ord_ds_cat_nat dsp' Hdsps (backward iso)) _. *)
(*   Next Obligation. *)
(*     split; intros ?; [apply (iso_lr (is_iso iso))|apply (iso_rl (is_iso iso))]. *)
(*   Qed. *)
(*   Fail Next Obligation. *)

(* End cut_ord_ds_cat_iso. *)

(* (* Section cut_ord_ds_cat_facts. *) *)
(* (*   Context {SI : indexT} {dsp : downset_pred SI} {C : category} *) *)
(* (*     (F F' : functor ((OrdDSCat dsp)ᵒᵖ) C). *) *)

(* (*   Program Definition cut_ord_ds_cat_eq_dsps *) *)
(* (*     (dsp1 : downset_pred SI) (Hdsps1 : ∀ α, dsp1 α → dsp α) *) *)
(* (*     (dsp2 : downset_pred SI) (Hdsps2 : ∀ α, dsp2 α → dsp α) *) *)
(* (*     (Hdspseq : ∀ α, dsp2 α → dsp1 α) *) *)
(* (*     (iso : cut_ord_ds_cat_func dsp1 Hdsps1 F *) *)
(* (*        ≃@{FuncCat (OrdDSCat dsp1)ᵒᵖ C} *) *)
(* (*        cut_ord_ds_cat_func dsp1 Hdsps1 F') : *) *)
(* (*     cut_ord_ds_cat_func dsp2 Hdsps2 F *) *)
(* (*     ≃@{FuncCat (OrdDSCat dsp2)ᵒᵖ C} *) *)
(* (*     cut_ord_ds_cat_func dsp2 Hdsps2 F' *) *)
(* (*     := *) *)
(* (*     MkIsoIc *) *)
(* (*       (forward iso) *) *)
(* (*       _ *) *)
(* (*       _. *) *)


(* (*   Definition cut_ord_ds_cat_nat_map β : *) *)
(* (*     hom (cut_ord_ds_cat_func_o_map dsp' Hdsps F β) (cut_ord_ds_cat_func_o_map dsp' Hdsps F' β) := *) *)
(* (*     η ₙ (MkDS (Hdsps _ (ds_in_dsp β))). *) *)

(* (*   Program Definition cut_ord_ds_cat_nat : *) *)
(* (*     natural (cut_ord_ds_cat_func dsp' Hdsps F) (cut_ord_ds_cat_func dsp' Hdsps F') := *) *)
(* (*     MkNat cut_ord_ds_cat_nat_map _. *) *)
(* (*   Next Obligation. *) *)
(* (*     intros ???; rewrite /= /cut_ord_ds_cat_func_h_map naturality //. *) *)
(* (*   Qed. *) *)
(* (*   Fail Next Obligation. *) *)

(* (* End cut_ord_ds_cat_nat. *) *)

Section limit_at.
  Context {SI : indexT} {C : category}.

  Variable (F : functor ((OrdCat SI)ᵒᵖ) C).

  Program Definition cone_at α dsp (Hle : ∀ β : downset dsp, β ⪯ α) : cone (lift_func dsp F) :=
    MkCone (F ₒ α) (λ β, F ₕ (Hle β)) _.
  Next Obligation.
    repeat intros ?; rewrite /= -h_map_comp; f_equiv.
    simpl.
    apply proof_irrelevance.
  Qed.
  Fail Next Obligation.
  Arguments cone_at {_} _ _, {_ _} _.

  Program Definition is_limit_at {α dsp} (Hle : ∀ β : downset dsp, β ⪯ α)
    (Hin : dsp α) : is_limit (lift_func dsp F) (F ₒ α) :=
    MkIsLimit _ (cone_is_cone (cone_at Hle))
      (MkIsTerm _ (λ cn, MkConeHom (side cn (MkDS (squash Hin))) _) _).
  Next Obligation.
    intros ????? δ; apply (@side_commutes _ _ _ cn (MkDS (squash Hin))).
  Qed.
  Next Obligation.
    intros ???? cn [f fcomm]; simpl in *.
    apply cone_hom_equiv_unpack; simpl.
    rewrite /cone_hom_eq /= fcomm.
    rewrite -{1}(left_id f) -h_map_id; repeat f_equiv; simpl.
    apply proof_irrelevance.
  Qed.
  Fail Next Obligation.

  Program Definition is_limit_at_zero {t} (Hterm : is_terminal t) :
    is_limit (lift_func (lt_dsp zero) F) t :=
    MkIsLimit _ (MkIsCone (λ β, False_rect _ (index_lt_zero_is_normal β (unsquash (ds_in_dsp β)))) _)
      (MkIsTerm _
         (λ cn, MkConeHom (bang Hterm _) _) _).
  Next Obligation.
  Proof. intros ?? β; exfalso; exact (index_lt_zero_is_normal _ (unsquash (ds_in_dsp β))). Qed.
  Next Obligation.
  Proof. intros ??? β; exfalso; exact (index_lt_zero_is_normal _ (unsquash (ds_in_dsp β))). Qed.
  Next Obligation.
  Proof.
    intros ????; simpl.
    apply cone_hom_equiv_unpack; simpl.
    rewrite /cone_hom_eq /=.
    apply bang_unique.
  Qed.
  Fail Next Obligation.

End limit_at.

Section earlier.
  Context {SI : indexT} {C : category}.

  Program Definition earlier : functor (FuncCat ((OrdCat SI)ᵒᵖ) C) (FuncCat ((OrdCat SI)ᵒᵖ) C) :=
    MkFunc (λ F, functor_compose (opposite_func (Succ _)) F)
      (λ _ _ η, hor_comp (natural_id (opposite_func (Succ _))) η) _ _.
  Next Obligation.
    repeat intros ?; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    rewrite /= !h_map_id !right_id //.
  Qed.
  Next Obligation.
    repeat intros ?; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    rewrite //= !h_map_id !right_id //.
  Qed.
  Fail Next Obligation.

  Program Definition from_earlier F : natural (earlier ₒ F) F :=
    MkNat (λ α, (F ₕ (index_lt_le_subrel _ _ (index_succ_greater α)))) _.
  Next Obligation. repeat intros ?; rewrite /= -!h_map_comp; f_equiv; simpl. apply proof_irrelevance. Qed.

End earlier.

Section later_func_gen.
  Context {SI : indexT} {C : category}.

  Variable (F : functor ((OrdCat SI)ᵒᵖ) C).

  Program Definition proj_cone {α β} (Hle : β ⪯ α) (cn : cone (lift_func (lt_dsp α) F)) :
    cone (lift_func (lt_dsp β) F) :=
    MkCone (vertex cn) (λ γ, side cn (lift_in_lt_ds Hle γ)) _.
  Next Obligation.
    intros ??? cn γ γ' f.
    exact (@side_commutes _ _ _ cn (lift_in_lt_ds Hle γ) (lift_in_lt_ds Hle γ') f).
  Qed.
  Fail Next Obligation.

  Variable (lo_map : SI → obj C).
  Hypothesis lo_map_il : ∀ α, is_limit (lift_func (lt_dsp α) F) (lo_map α).

  Lemma il_side_eq α (β : SI) Hβ1 Hβ2 :
    ic_side (il_is_cone (lo_map_il α)) (@MkDS _ _ β Hβ1) =
    ic_side (il_is_cone (lo_map_il α)) (@MkDS _ _ β Hβ2).
  Proof.
    reflexivity.
  Qed.

  Definition proj_cone_hom {α β} (Hle : β ⪯ α) :
    cone_hom
      (proj_cone Hle (cone_of_is_limit (lo_map_il α)))
      (cone_of_is_limit (lo_map_il β)) :=
    bang
      (is_limit_limiting_cone (lo_map_il β))
      (proj_cone Hle (cone_of_is_limit (lo_map_il α))).

  Program Definition later_func_gen : functor ((OrdCat SI)ᵒᵖ) C :=
    MkFunc lo_map (λ _ _ f, cone_hom_map (proj_cone_hom f)) _ _.
  Next Obligation.
  Proof.
    intros ??? Hle Hle'; rewrite /=.
    apply (hom_to_limit_unique _ _ _ (lo_map_il _)
             (cone_is_cone (proj_cone _ (cone_of_is_limit (lo_map_il _))))).
    - intros ?. rewrite_cone_hom_commutes_back; done.
    - intros.
      rewrite -comp_assoc -(cone_hom_commutes (proj_cone_hom Hle')) /=.
      rewrite_cone_hom_commutes_back; simpl.
      apply il_side_eq.
  Qed.
  Next Obligation.
  Proof.
    intros ?; rewrite /=.
    apply (hom_to_limit_unique _ _ _ (lo_map_il _)
             (cone_is_cone (proj_cone _ (cone_of_is_limit (lo_map_il _))))).
    - intros; rewrite_cone_hom_commutes_back; done.
    - intros δ; rewrite /= right_id.
      destruct δ; apply il_side_eq.
  Qed.
  Fail Next Obligation.

  Definition earlier_later_pointwise_iso α :
    (earlier ₒ later_func_gen) ₒ α ≃ (F ₒ α) :=
    cone_iso_vertex
      (is_term_unique
         (is_limit_limiting_cone (lo_map_il (succ α)))
         (is_limit_limiting_cone
            (is_limit_at F (in_lt_dsp_succ α) (index_succ_greater α)))).

  Program Definition earlier_later_iso :
    (earlier ₒ later_func_gen)
    ≃@{FuncCat ((OrdCat SI)ᵒᵖ) C}
    F :=
    MkIsoIc
      (MkNat (λ α, forward (earlier_later_pointwise_iso α)) _)
      (MkNat (λ α, backward (earlier_later_pointwise_iso α)) _)
      _.
  Next Obligation.
    intros α β Hle; simpl in *.
    rewrite_cone_hom_commutes_back; simpl.
    assert (β ≺ succ α) as Hβsα.
    { apply index_succ_iff; done. }
    pose proof (ic_side_commutes (il_is_cone (lo_map_il (succ α)))
       (Hle : MkDS (lt_dsp (succ α)) (squash Hβsα) ⪯ MkDS (lt_dsp (succ α)) (squash (index_succ_greater α))))
        as Hicc; simpl in Hicc; rewrite -Hicc; clear Hicc.
    apply il_side_eq.
  Qed.
  Next Obligation.
    intros α β Hle; simpl in *.
    apply (hom_to_limit_unique _ _ _
             (lo_map_il (succ β))
             (cone_is_cone
                (proj_cone (index_le_succ_mono _ _ Hle)
                   (cone_at F α (lt_dsp (succ α)) (in_lt_dsp_succ α))))).
    - intros γ; rewrite /= -comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite -h_map_comp.
      f_equiv; simpl.
      apply proof_irrelevance.
    - intros γ; simpl in *.
      rewrite -!comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite_cone_hom_commutes_back; done.
  Qed.
  Next Obligation.
    split; apply natural_equiv_unpack; intros α; simpl.
    - pose proof (is_iso (earlier_later_pointwise_iso α)) as [? ?]; simpl in *; done.
    - pose proof (is_iso (earlier_later_pointwise_iso α)) as [? ?]; simpl in *; done.
  Qed.
  Fail Next Obligation.

  Lemma side_of_later_gen {α} (β : downset (lt_dsp α)) :
    ic_side (il_is_cone (lo_map_il α)) β =
    (forward earlier_later_iso ₙ (β : SI)) ∘
    (later_func_gen ₕ (index_succ_le_lt2 _ _ (unsquash (ds_in_dsp β)))).
  Proof.
    assert (succ β ⪯ α) as Hsβsα.
    { apply index_succ_le_lt2, (unsquash (ds_in_dsp β)). }
    apply (hom_to_limit_unique _ _ _
      (is_limit_at F (in_lt_dsp_succ β) (index_succ_greater β))
      (cone_is_cone (proj_cone Hsβsα (cone_of_is_cone (il_is_cone (lo_map_il α)))))).
    - intros γ; simpl.
      assert (γ ≺ α) as Hγα.
      { eapply index_le_lt_trans; last apply (unsquash (ds_in_dsp β)).
        apply index_succ_iff_proj_r2l, (unsquash (ds_in_dsp γ)). }
      pose proof (ic_side_commutes (il_is_cone (lo_map_il α))
       (in_lt_dsp_succ β γ : MkDS (lt_dsp α) (squash Hγα) ⪯ MkDS (lt_dsp α) (ds_in_dsp β)))
        as Hicc.
      destruct β; simpl in *; rewrite -Hicc.
      destruct γ; simpl.
      apply il_side_eq.
    - intros γ; simpl in *.
      rewrite -comp_assoc.
      pose proof (naturality (forward earlier_later_iso)) as Hn.
      simpl in Hn; rewrite -Hn; clear Hn.
      repeat (rewrite_cone_hom_commutes_back; simpl).
      destruct γ; simpl; apply il_side_eq.
  Qed.

  Lemma side_of_later'_gen {α} (β : downset (lt_dsp α)) :
    (later_func_gen ₕ (index_succ_le_lt2 _ _ (unsquash (ds_in_dsp β)))) =
    (backward earlier_later_iso ₙ (β : SI)) ∘ ic_side (il_is_cone (lo_map_il α)) β.
  Proof.
    symmetry.
    apply (compose_along_iso_left (earlier_later_pointwise_iso (β : SI))).
    rewrite -comp_assoc (iso_rl (is_iso (earlier_later_pointwise_iso (β : SI)))) left_id.
    apply side_of_later_gen.
  Qed.

  Lemma equiv_of_into_later_gen (c : obj C) {α} (f g : hom c (later_func_gen ₒ α)) :
    (∀ β (Hlt : β ≺ α),
      (later_func_gen ₕ (index_succ_le_lt2 _ _ Hlt)) ∘ f  =
      (later_func_gen ₕ (index_succ_le_lt2 _ _ Hlt)) ∘ g) →
    f = g.
  Proof.
    intros Hfg.
    apply (hom_to_limit_unique _ _ _
             (lo_map_il α)
             (cone_is_cone (extend_cone (cone_of_is_cone (il_is_cone (lo_map_il α))) f)));
    first done.
    intros β; simpl in *.
    rewrite side_of_later_gen.
    rewrite !comp_assoc.
    f_equiv.
    rewrite Hfg; done.
  Qed.

  Program Definition cone_of_into_later_gen (c : obj C) {α}
    (f : ∀ β, β ≺ α → hom c (F ₒ β))
    (Hf : ∀ β γ (Hβ : β ≺ α) (Hγ : γ ≺ α) (Hle : β ⪯ γ),
        (F ₕ Hle) ∘ (f γ Hγ) = (f β Hβ)) :
    cone (lift_func (lt_dsp α) F) :=
    MkCone c (λ β, f _ (unsquash (ds_in_dsp β))) _.
  Next Obligation.
    intros ?? f Hf β γ Hle; simpl.
    symmetry; apply Hf.
  Qed.

  Definition into_later_gen (c : obj C) {α}
    (f : ∀ β, β ≺ α → hom c (F ₒ β))
    (Hf : ∀ β γ (Hβ : β ≺ α) (Hγ : γ ≺ α) (Hle : β ⪯ γ),
        (F ₕ Hle) ∘ (f γ Hγ) = (f β Hβ)) : hom c (later_func_gen ₒ α) :=
    cone_hom_map
      (bang (is_limit_limiting_cone (lo_map_il α)) (cone_of_into_later_gen c f Hf)).

  Lemma into_later_side_gen (c : obj C) {α}
    (f : ∀ β, β ≺ α → hom c (F ₒ β))
    (Hf : ∀ β γ (Hβ : β ≺ α) (Hγ : γ ≺ α) (Hle : β ⪯ γ),
        (F ₕ Hle) ∘ (f γ Hγ) = (f β Hβ))
    (β : downset (lt_dsp α)) :
    (ic_side (il_is_cone (lo_map_il α)) β) ∘ (into_later_gen c f Hf) = f _ (unsquash (ds_in_dsp β)).
  Proof. rewrite /into_later_gen; rewrite_cone_hom_commutes_back; simpl; done. Qed.

End later_func_gen.

Section later.
  Context {SI : indexT} {C : category} `{!HasTerm C} `{!Complete C}.

  Program Definition later_func_o_map_il (F : functor ((OrdCat SI)ᵒᵖ) C) :
    index_rect (λ α, {c : obj C & is_limit (lift_func (lt_dsp α) F) c}) :=
    MkIR
      (existT _ (is_limit_at_zero F (term_is_terminal (term_of C))))
      (λ α _, existT _ (is_limit_at F (dsp := lt_dsp (succ α)) (in_lt_dsp_succ α)
                          (index_succ_greater α)))
      (λ α _, existT _ (limiting_cone_is_limit (term_is_terminal (complete _))))
      _.
  Next Obligation. done. Qed.
  Fail Next Obligation.

  Definition later_func_o_map F α : obj C := projT1 (later_func_o_map_il F α).

  Lemma later_func_o_map_zero F : later_func_o_map F zero = (term (term_of C)).
  Proof. by rewrite /later_func_o_map; simpl_index_rect. Qed.

  Lemma later_func_o_map_succ F α : later_func_o_map F (succ α) = F ₒ α.
  Proof. by rewrite /later_func_o_map; simpl_index_rect. Qed.

  Lemma later_func_o_map_lim F (α : limit_idx SI) :
    later_func_o_map F α = vertex (term (complete (lift_func (lt_dsp α) F))).
  Proof. by rewrite /later_func_o_map; simpl_index_rect. Qed.

  Definition later_func_o_map_is_limit F α :
    is_limit (lift_func (lt_dsp α) F) (later_func_o_map F α) :=
    projT2 (later_func_o_map_il F α).

  Lemma later_func_o_map_is_limit_zero F :
    later_func_o_map_is_limit F zero =
    is_limit_trans (eq_sym (later_func_o_map_zero F))
      (is_limit_at_zero F (term_is_terminal (term_of C))).
  Proof.
    rewrite /later_func_o_map_is_limit.
    assert (later_func_o_map_il F zero =
      existT _ (is_limit_at_zero F (term_is_terminal (term_of C)))) as Heq.
    { by simpl_index_rect. }
    pose proof (projT2_eq Heq) as Heq'; simpl in *; rewrite -Heq'; clear Heq'.
    replace (projT1_eq Heq) with (later_func_o_map_zero F)
      by apply proof_irrelevance.
    destruct (later_func_o_map_zero F); simpl; done.
  Qed.

  Lemma later_func_o_map_is_limit_succ F α :
    later_func_o_map_is_limit F (succ α) =
    is_limit_trans (eq_sym (later_func_o_map_succ F α))
      (is_limit_at F (dsp := lt_dsp (succ α)) (in_lt_dsp_succ α)
         (index_succ_greater α)).
  Proof.
    assert (later_func_o_map_il F (succ α) =
      existT _ (is_limit_at F (dsp := lt_dsp (succ α)) (in_lt_dsp_succ α)
         (index_succ_greater α))) as Heq.
    { by simpl_index_rect. }
    pose proof (projT2_eq Heq) as Heq'; simpl in *; rewrite -Heq'; clear Heq'.
    replace (projT1_eq Heq) with (later_func_o_map_succ F α)
      by apply proof_irrelevance.
    destruct (later_func_o_map_succ F α); simpl; done.
  Qed.

  Lemma later_func_o_map_is_limit_lim F (α : limit_idx SI) :
    later_func_o_map_is_limit F α =
    is_limit_trans (eq_sym (later_func_o_map_lim F α))
      (limiting_cone_is_limit (term_is_terminal (complete _))).
  Proof.
    assert (later_func_o_map_il F α =
      existT _ (limiting_cone_is_limit (term_is_terminal (complete _)))) as Heq.
    { by simpl_index_rect. }
    pose proof (projT2_eq Heq) as Heq'; simpl in *; rewrite -Heq'; clear Heq'.
    replace (projT1_eq Heq) with (later_func_o_map_lim F α)
      by apply proof_irrelevance.
    destruct (later_func_o_map_lim F α); simpl; done.
  Qed.

  Program Definition later_func F : functor ((OrdCat SI)ᵒᵖ) C :=
    later_func_gen F (later_func_o_map F) (later_func_o_map_is_limit F).

  Program Definition later_h_map_cone {F G} (η : natural F G) α :
    cone (lift_func (lt_dsp α) G) :=
    MkCone (later_func_o_map F α)
      (λ δ, η ₙ (ds_idx δ) ∘ ic_side (il_is_cone (later_func_o_map_is_limit F α)) δ) _.
  Next Obligation.
    intros ???????; simpl in *. rewrite -comp_assoc -naturality /= comp_assoc.
    rewrite -(ic_side_commutes (il_is_cone (later_func_o_map_is_limit F α))); done.
  Qed.
  Fail Next Obligation.

  Program Definition later_h_map {F G} (η : natural F G) : natural (later_func F) (later_func G) :=
    MkNat
      (λ α, cone_hom_map (bang (il_is_limiting_cone _ _ (later_func_o_map_is_limit G α))
        (later_h_map_cone η α)))
      _.
  Next Obligation.
  Proof.
    intros ?? η α β f; simpl in *.
    pose (proj_cone _ f (later_h_map_cone η α)) as cn.
    apply (hom_to_limit_unique _ _ _
              (limiting_cone_is_limit (il_is_limiting_cone _ _ (later_func_o_map_is_limit _ _)))
              (cone_is_cone cn)).
    - intros ?. rewrite -comp_assoc.
      rewrite_cone_hom_commutes_back.
      rewrite /= comp_assoc.
      rewrite_cone_hom_commutes_back; done.
    - intros ?; rewrite /=.
      rewrite -comp_assoc.
      repeat (rewrite_cone_hom_commutes_back; simpl); done.
  Qed.
  Fail Next Obligation.

  Definition later_h_map_comp {F G H} (η : natural F G) (η' : natural G H) :
    later_h_map (natural_comp η η') = natural_comp (later_h_map η) (later_h_map η').
  Proof.
    apply natural_equiv_unpack; intros α; simpl.
    pose (later_h_map_cone (natural_comp η η') α) as cn.
    apply (hom_to_limit_unique _ _ _
      (limiting_cone_is_limit (il_is_limiting_cone _ _ (later_func_o_map_is_limit _ _)))
      (cone_is_cone cn)).
    - intros ?; rewrite /=. rewrite_cone_hom_commutes_back; done.
    - intros ?; rewrite /= -comp_assoc.
      rewrite_cone_hom_commutes_back.
      rewrite /= !comp_assoc.
      rewrite_cone_hom_commutes_back; done.
  Qed.

  Definition later_h_map_id F : later_h_map (natural_id F) = natural_id (later_func F).
  Proof.
    apply natural_equiv_unpack; intros α; simpl.
    pose (later_h_map_cone (natural_id F) α) as cn.
    apply (hom_to_limit_unique _ _ _
      (limiting_cone_is_limit (il_is_limiting_cone _ _ (later_func_o_map_is_limit _ _)))
      (cone_is_cone cn)).
    - intros ?; simpl.
      rewrite /= left_id.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite /= left_id //.
    - intros ?; rewrite /= left_id.
      rewrite right_id //.
  Qed.

  Program Definition later : functor (FuncCat ((OrdCat SI)ᵒᵖ) C) (FuncCat ((OrdCat SI)ᵒᵖ) C) :=
    MkFunc later_func (λ _ _ η, later_h_map η) (λ _ _ _, later_h_map_comp) later_h_map_id.
  Fail Next Obligation.

  Program Definition next : natural (id_functor (FuncCat ((OrdCat SI)ᵒᵖ) C)) later :=
    MkNat (λ F,
      MkNat (λ α,
        cone_hom_map
          (bang (il_is_limiting_cone _ _ (later_func_o_map_is_limit F α))
            (cone_at F α (lt_dsp α) (in_lt_dsp α)))) _) _.
  Next Obligation.
    intros F α β Hle; rewrite /=.
    apply (hom_to_limit_unique _ _ _
            (limiting_cone_is_limit (il_is_limiting_cone _ _ (later_func_o_map_is_limit F β)))
            (cone_is_cone (cone_at F α (lt_dsp β) (in_lt_dsp_le Hle)))).
    - intros ?; rewrite /=.
      rewrite -comp_assoc.
      rewrite_cone_hom_commutes_back.
      rewrite -h_map_comp; f_equiv.
      simpl; apply proof_irrelevance.
    - intros ?; rewrite /=.
      rewrite -comp_assoc.
      repeat (rewrite_cone_hom_commutes_back; simpl); f_equiv.
      simpl; apply proof_irrelevance.
  Qed.
  Next Obligation.
    intros F G η.
    apply natural_equiv_unpack; intros α; simpl.
    apply (hom_to_limit_unique _ _ _
             (limiting_cone_is_limit
                (il_is_limiting_cone (lift_func _ _) _ (later_func_o_map_is_limit G α)))
             (cone_is_cone
                (trans_cone_along_natural (lift_natural (lt_dsp α) η)
                   (cone_at F α (lt_dsp α) (in_lt_dsp α))))).
    - intros ?; rewrite /= -comp_assoc; rewrite_cone_hom_commutes_back.
      rewrite naturality. f_equiv; done.
    - intros ?; rewrite /= -comp_assoc; rewrite_cone_hom_commutes_back.
      rewrite comp_assoc; rewrite_cone_hom_commutes_back; f_equiv; done.
  Qed.

  Program Definition earlier_later_nat_iso :
    functor_compose later earlier
    ≃@{FuncCat (FuncCat ((OrdCat SI)ᵒᵖ) C) (FuncCat ((OrdCat SI)ᵒᵖ) C)}
    (id_functor (FuncCat ((OrdCat SI)ᵒᵖ) C)) :=
    MkIsoIc
      (MkNat (λ F,
           forward (earlier_later_iso F (later_func_o_map F) (later_func_o_map_is_limit F))) _)
      (MkNat (λ F,
           backward (earlier_later_iso F (later_func_o_map F) (later_func_o_map_is_limit F))) _)
      _.
  Next Obligation.
    intros F G η.
    apply natural_equiv_unpack; intros α; simpl.
    rewrite -comp_assoc.
    rewrite_cone_hom_commutes_back; simpl.
    rewrite comp_assoc.
    rewrite_cone_hom_commutes_back; simpl.
    f_equiv.
    apply il_side_eq.
  Qed.
  Next Obligation.
    intros F G η.
    apply natural_equiv_unpack; intros α; simpl.
    apply (hom_to_limit_unique _ _ _
             (later_func_o_map_is_limit G (succ α))
             (cone_is_cone
                (trans_cone_along_natural (lift_natural (lt_dsp (succ α)) η)
                   (cone_at F α (lt_dsp (succ α)) (in_lt_dsp_succ α))))).
    - intros γ; simpl in *.
      rewrite -comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite naturality //.
    - intros γ; simpl in *.
      rewrite -!comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite !comp_assoc; f_equiv.
      rewrite -!comp_assoc.
      repeat (rewrite_cone_hom_commutes_back; simpl).
      f_equiv; done.
  Qed.
  Next Obligation.
    split; apply natural_equiv_unpack; intros F; simpl;
      apply natural_equiv_unpack; intros α; simpl.
    - pose proof (is_iso
                    (earlier_later_iso F (later_func_o_map F) (later_func_o_map_is_limit F))) as [Hlr _].
      pose proof (natural_equiv_pack Hlr α).
      simpl in *; done.
    - pose proof (is_iso
                    (earlier_later_iso F (later_func_o_map F) (later_func_o_map_is_limit F))) as [_ Hrl].
      pose proof (natural_equiv_pack Hrl α).
      simpl in *; done.
  Qed.
  Fail Next Obligation.

  Lemma forward_earlier_later_nat_iso_next (F : functor ((OrdCat SI)ᵒᵖ) C) :
  (natural_comp
     (earlier ₕ (next ₙ F))
     (forward earlier_later_nat_iso ₙ F)) = from_earlier F.
  Proof.
    apply natural_equiv_unpack; intros α; simpl.
    rewrite /= -comp_assoc.
    rewrite_cone_hom_commutes_back; simpl.
    rewrite -h_map_comp; f_equiv; simpl; apply proof_irrelevance.
  Qed.

  Lemma side_of_later F {α} (β : downset (lt_dsp α)) :
    ic_side (il_is_cone (later_func_o_map_is_limit F α)) β =
    (forward earlier_later_nat_iso) ₙ F ₙ (β : SI) ∘
    ((later ₒ F)ₕ (index_succ_le_lt2 _ _ (unsquash (ds_in_dsp β)))).
  Proof. apply side_of_later_gen. Qed.

  Lemma side_of_later' F {α} (β : downset (lt_dsp α)) :
    ((later ₒ F)ₕ (index_succ_le_lt2 _ _ (unsquash (ds_in_dsp β)))) =
    (backward earlier_later_nat_iso) ₙ F ₙ (β : SI) ∘
    ic_side (il_is_cone (later_func_o_map_is_limit F α)) β.
  Proof. apply side_of_later'_gen. Qed.

  Lemma equiv_of_into_later F (c : obj C) {α} (f g : hom c ((later ₒ F) ₒ α)) :
    (∀ β (Hlt : β ≺ α),
      ((later ₒ F) ₕ (index_succ_le_lt2 _ _ Hlt)) ∘ f  =
      ((later ₒ F) ₕ (index_succ_le_lt2 _ _ Hlt)) ∘ g) →
    f = g.
  Proof. apply equiv_of_into_later_gen. Qed.

  Definition into_later (F : functor ((OrdCat SI)ᵒᵖ) C) (c : obj C) {α}
    (f : ∀ β, β ≺ α → hom c (F ₒ β))
    (Hf : ∀ β γ (Hβ : β ≺ α) (Hγ : γ ≺ α) (Hle : β ⪯ γ),
        (F ₕ Hle) ∘ (f γ Hγ) = (f β Hβ)) : hom c ((later ₒ F) ₒ α) :=
    into_later_gen F (later_func_o_map F) (later_func_o_map_is_limit F) c f Hf.

  Lemma into_later_side (F : functor ((OrdCat SI)ᵒᵖ) C) (c : obj C) {α}
    (f : ∀ β, β ≺ α → hom c (F ₒ β))
    (Hf : ∀ β γ (Hβ : β ≺ α) (Hγ : γ ≺ α) (Hle : β ⪯ γ),
        (F ₕ Hle) ∘ (f γ Hγ) = (f β Hβ))
    (β : downset (lt_dsp α)) :
    (ic_side (il_is_cone (later_func_o_map_is_limit F α)) β) ∘ (into_later F c f Hf) =
    f _ (unsquash (ds_in_dsp β)).
  Proof. apply into_later_side_gen. Qed.

End later.

Section Adjunction.
  Context {SI : indexT} {C : category} `{!HasTerm C} `{!Complete C}.

  Program Definition to_later_F_succ_cone (F : functor ((OrdCat SI) ᵒᵖ) C) α :
    is_cone (lift_func (lt_dsp α) (functor_compose (opposite_func (Succ SI)) F)) (F ₒ α) :=
    MkIsCone (λ β, F ₕ (index_succ_iff_proj_r2l _ _ _ (index_lt_succ_mono _ _ (unsquash (ds_in_dsp β))))) _.
  Next Obligation. repeat intros ?; rewrite /= -h_map_comp; f_equiv; simpl; apply proof_irrelevance. Qed.

  Program Definition to_later_F_succ F :
    natural F (later_func (functor_compose (opposite_func (Succ SI)) F)) :=
    MkNat (λ α,
        cone_hom_map
          (bang (is_limit_limiting_cone (later_func_o_map_is_limit _ α))
             (cone_of_is_cone (to_later_F_succ_cone F α)))) _.
  Next Obligation.
    intros ??? Hle; rewrite /=.
    apply (hom_to_limit_unique _ _ _
             (later_func_o_map_is_limit
                (functor_compose (opposite_func (Succ SI)) _) _)
             (cone_is_cone (proj_cone _ Hle (cone_of_is_cone (to_later_F_succ_cone _ _))))).
    - intros ?; rewrite /= -comp_assoc. rewrite_cone_hom_commutes_back.
      rewrite /to_later_F_succ_cone /= -h_map_comp.
      f_equiv; simpl; apply proof_irrelevance.
    - intros ?; rewrite /= -comp_assoc; repeat (rewrite_cone_hom_commutes_back; simpl); done.
  Qed.
  Fail Next Obligation.

  Program Definition cone_for_later_earlier_forward
    {F1 : functor ((OrdCat SI) ᵒᵖ) C}
    {G1 : functor ((OrdCat SI) ᵒᵖ) C}
    {F2 : functor ((OrdCat SI) ᵒᵖ) C}
    {G2 : functor ((OrdCat SI) ᵒᵖ) C}
    (η1 : natural F2 F1)
    (η2 : natural G1 G2)
    (δ : natural (functor_compose (opposite_func (Succ SI)) F1) G1)
    (α : SI)
    : cone (lift_func (lt_dsp α) G2) :=
    MkCone (F2 ₒ α)
      (λ j, (η2 ₙ (j : SI)) ∘ (δ ₙ (j : SI)) ∘ (η1 ₙ (succ j)) ∘
              (F2 ₕ (index_succ_least _ _ (unsquash (ds_in_dsp j))))) _.
  Next Obligation.
    intros ???? η1 η2 δ ????; rewrite /=.
    rewrite -!comp_assoc -!(naturality η2) !comp_assoc. f_equiv.
    rewrite -!comp_assoc -(naturality δ) /= !comp_assoc. f_equiv.
    rewrite -!comp_assoc -(naturality η1) /= !comp_assoc. f_equiv.
    rewrite -h_map_comp. f_equiv.
    simpl; apply proof_irrelevance.
  Qed.
  Fail Next Obligation.

  Program Definition later_earlier_forward :
    natural
      (in_left_of_hom (FuncCat (OrdCat SI)ᵒᵖ C) (FuncCat (OrdCat SI)ᵒᵖ C) ₒ earlier)
      (in_right_of_hom (FuncCat (OrdCat SI)ᵒᵖ C) (FuncCat (OrdCat SI)ᵒᵖ C) ₒ later) :=
    MkNat (λ FG, λ η, natural_comp (to_later_F_succ FG.1) (later ₕ η)) _.
  Next Obligation.
    intros [F1 G1] [F2 G2] [η1 η2].
    extensionality z; simpl.
    apply natural_equiv_unpack; intros α; simpl in *.
    apply (hom_to_limit_unique _ _ _
             (later_func_o_map_is_limit G2 α)
             (cone_is_cone (cone_for_later_earlier_forward η1 η2 z α))).
    - intros ?; rewrite /=.
      rewrite -!comp_assoc; rewrite_cone_hom_commutes_back.
      rewrite !comp_assoc; rewrite_cone_hom_commutes_back.
      rewrite h_map_id left_id /=; repeat f_equiv; simpl; apply proof_irrelevance.
    - intros ?; rewrite /=.
      rewrite -!comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite !comp_assoc; f_equiv.
      rewrite -!comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite !comp_assoc; f_equiv.
      rewrite -!comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite naturality; repeat f_equiv; simpl; apply proof_irrelevance.
  Qed.

  Program Definition later_earlier_backward :
    natural
      (in_right_of_hom (FuncCat (OrdCat SI)ᵒᵖ C) (FuncCat (OrdCat SI)ᵒᵖ C) ₒ later)
      (in_left_of_hom (FuncCat (OrdCat SI)ᵒᵖ C) (FuncCat (OrdCat SI)ᵒᵖ C) ₒ earlier) :=
    MkNat (λ FG, λ η,
        natural_comp
          (hor_comp (natural_id (opposite_func (Succ _))) η)
          ((forward earlier_later_nat_iso)ₙ FG.2)) _.
  Next Obligation.
    intros [F1 G1] [F2 G2] [η1 η2].
    extensionality δ; simpl.
    apply natural_equiv_unpack; intros α; simpl.
    rewrite !h_map_id !right_id.
    rewrite -!comp_assoc.
    rewrite_cone_hom_commutes_back; simpl; done.
  Qed.
  Fail Next Obligation.

  Program Definition later_adj : adjunction (@earlier SI C) later :=
    MkIsoIc later_earlier_forward later_earlier_backward _.
  Next Obligation.
    split.
    - apply natural_equiv_unpack; intros η; simpl.
      extensionality α; simpl in *.
      apply natural_equiv_unpack; intros η'; simpl.
      rewrite h_map_id right_id.
      rewrite -!comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      match goal with |- _ ∘ h_map _ ?A = _ =>
      replace A with (reflexivity (succ η')) by apply proof_irrel
      end.
      rewrite h_map_id right_id; done.
    - apply natural_equiv_unpack; intros [F G]; simpl.
      extensionality η; simpl in *.
      apply natural_equiv_unpack; intros α; simpl.
      pose (extend_cone
              (cone_of_is_cone (il_is_cone (later_func_o_map_is_limit G α)))
              (η ₙ α)) as cn.
      apply (hom_to_limit_unique _ _ _
             (later_func_o_map_is_limit G α)
             (cone_is_cone cn)); last done.
      intros γ; rewrite /= -comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite h_map_id right_id.
      rewrite !comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite (naturality η) /=.
      rewrite -!comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      f_equiv.
      destruct γ; apply il_side_eq.
  Qed.

End Adjunction.

Section basic_constructs.
  Context {SI : indexT} (F : PreSheaf (OrdCat SI)).

  Lemma equiv_of_into_later_psh {α} (x y : (later ₒ F) ₒ α) :
    (∀ β (Hlt : β ≺ α),
      ((later ₒ F) ₕ (index_succ_le_lt2 _ _ Hlt)) x  =
      ((later ₒ F) ₕ (index_succ_le_lt2 _ _ Hlt)) y) →
    x = y.
  Proof.
    intros Hxy.
    apply (λ Hxy, equal_f (equiv_of_into_later F unit (λ _, x) (λ _, y) Hxy) ()).
    intros β Hβ.
    extensionality z; simpl in *.
    done.
  Qed.

  Program Definition into_later_psh {α}
    (f : ∀ β, β ≺ α → (F ₒ β))
    (Hf : ∀ β γ (Hβ : β ≺ α) (Hγ : γ ≺ α) (Hle : β ⪯ γ),
        (F ₕ Hle) (f γ Hγ) = (f β Hβ)) : (later ₒ F) ₒ α :=
    into_later F unit (λ β Hβ, λ _, f β Hβ) _ ().
  Next Obligation.
    repeat intros ?; simpl.
    extensionality x; simpl.
    done.
  Qed.
  Fail Next Obligation.

  Lemma into_later_side_psh {α}
    (f : ∀ β, β ≺ α → F ₒ β)
    (Hf : ∀ β γ (Hβ : β ≺ α) (Hγ : γ ≺ α) (Hle : β ⪯ γ), (F ₕ Hle) (f γ Hγ) = (f β Hβ))
    (β : downset (lt_dsp α)) :
    (ic_side (il_is_cone (later_func_o_map_is_limit F α)) β) (into_later_psh f Hf) =
    f _ (unsquash (ds_in_dsp β)).
  Proof.
    apply (λ Hf, equal_f (into_later_side F unit (λ β Hβ, λ _, f β Hβ)
                   Hf β) ()).
  Qed.

End basic_constructs.

Section earlier_preserves.
  Context {SI : indexT}.

  Program Definition earlier_prod_forward
    (α1 : obj (PSh (OrdCat SI))) (α2 : obj (PSh (OrdCat SI))) :
    natural (functor_compose (opposite_func (Succ SI)) (α1 ×ₒ α2))
      (functor_compose (opposite_func (Succ SI)) α1
         ×ₒ functor_compose (opposite_func (Succ SI)) α2) :=
    (MkNat (λ α, id_fun _) _).
  Next Obligation. repeat intros ?; simpl; solve_by_eq_rewrite. Qed.

  Program Definition earlier_prod_backward
    (α1 : obj (PSh (OrdCat SI))) (α2 : obj (PSh (OrdCat SI))) :
    natural (functor_compose (opposite_func (Succ SI)) α1
               ×ₒ functor_compose (opposite_func (Succ SI)) α2)
      (functor_compose (opposite_func (Succ SI)) (α1 ×ₒ α2))
    :=
    (MkNat (λ α, id_fun _) _).
  Next Obligation. repeat intros ?; simpl; solve_by_eq_rewrite. Qed.

  Program Definition earlier_prod_nat :
    (functor_compose (prod_func _) (earlier (SI := SI)))
      ≃@{FuncCat (cat_prod (PSh (OrdCat SI)) (PSh (OrdCat SI)))
           (PSh (OrdCat SI))}
      (functor_compose (functor_prod earlier earlier) (prod_func _))
    := MkIsoIc
         (MkNat (λ α, earlier_prod_forward α.1 α.2) _)
         (MkNat (λ α, earlier_prod_backward α.1 α.2) _)
         _.
  Next Obligation.
    intros ???; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality x.
    destruct x.
    simpl.
    reflexivity.
  Qed.
  Next Obligation.
    intros ???; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality x.
    destruct x.
    simpl.
    reflexivity.
  Qed.
  Next Obligation.
    split; simpl; repeat intros ?; simpl;
      apply natural_equiv_unpack; intros ?; simpl;
      apply natural_equiv_unpack; intros ?; simpl;
      extensionality x; destruct x;
      done.
  Qed.

  Program Definition earlier_prod (F G : PreSheaf (OrdCat SI)) :
    earlier ₒ (F ×ₒ@{PSh (OrdCat SI)} G)
    ≃@{PSh (OrdCat SI)}
    (earlier ₒ F) ×ₒ (earlier ₒ G) := natural_iso_proj
                                        earlier_prod_nat
                                        (F, G).

End earlier_preserves.

Section later_preserves.
  Context {SI : indexT}.

  Local Opaque later next.

  Definition later_preserves_prods_nat :
  functor_compose (prod_func (PSh (OrdCat SI))) later
  ≃@{FuncCat (cat_prod (PSh (OrdCat SI)) (PSh (OrdCat SI))) (PSh (OrdCat SI))}
  functor_compose (functor_prod later later) (prod_func (PSh (OrdCat SI))) :=
    right_adj_preserves_prods later_adj.

  Program Definition later_prod (F G : PreSheaf (OrdCat SI)) :
    later ₒ (F ×ₒ@{PSh (OrdCat SI)} G)
    ≃@{PSh (OrdCat SI)}
    (later ₒ F) ×ₒ (later ₒ G) :=
    MkIsoIc
      (forward later_preserves_prods_nat ₙ (F, G))
      (backward later_preserves_prods_nat ₙ (F, G)) _.
  Next Obligation.
    intros F G; split.
    - pose proof (is_iso later_preserves_prods_nat) as [Hfb _].
      apply (natural_equiv_pack Hfb (F, G)).
    - pose proof (is_iso later_preserves_prods_nat) as [_ Hbf].
      apply (natural_equiv_pack Hbf (F, G)).
  Qed.

  Definition later_preserves_terminal_nat :
  functor_compose (const_functor (1ₒ)) later
  ≃@{FuncCat SingletonCat (PSh (OrdCat SI))}
  (const_functor (1ₒ)) :=
    right_adj_preserves_terminal later_adj.

  Program Definition later_term :
    later ₒ (1ₒ) ≃@{PSh (OrdCat SI)} (1ₒ) :=
    MkIsoIc
      (forward later_preserves_terminal_nat ₙ ())
      (backward later_preserves_terminal_nat ₙ ()) _.
  Next Obligation.
    split.
    - pose proof (is_iso later_preserves_terminal_nat) as [Hfb _].
      apply (natural_equiv_pack Hfb ()).
    - pose proof (is_iso later_preserves_terminal_nat) as [_ Hbf].
      apply (natural_equiv_pack Hbf ()).
  Qed.

End later_preserves.
Global Arguments later_preserves_prods_nat _ : clear implicits.
Global Arguments later_preserves_terminal_nat _ : clear implicits.

Section later_preserves.
  Context {SI : indexT}.

  Local Opaque earlier later earlier_later_nat_iso
    earlier_prod_nat iso_prod natural_iso_proj.

  Definition earlier_later_prod_nat
    : (prod_func _) ∘@{Cat} (functor_prod earlier (id (C := Cat) _))
        ≃@{FuncCat (cat_prod (PSh (OrdCat SI)) (PSh (OrdCat SI)))
             (PSh (OrdCat SI))}
        (earlier ∘@{Cat} ((prod_func _)
                            ∘@{Cat} (functor_prod (id (C := Cat) _) later)))
    := isomorphic_sym
         (isomorphic_trans (isomorphic_sym functor_compose_assoc_iso)
            (isomorphic_trans
               (functor_compose_iso_proper
                  (isomorphic_refl _)
                  earlier_prod_nat)
               (isomorphic_trans functor_compose_assoc_iso
                  (isomorphic_trans
                     (functor_compose_iso_proper functor_prod_prod_iso
                        (isomorphic_refl _))
                     (functor_compose_iso_proper
                        (functor_prod_iso_proper
                           (isomorphic_sym functor_compose_left_id_iso)
                           earlier_later_nat_iso)
                        (isomorphic_refl _)))))).

  Definition earlier_later_prod (F G : PreSheaf (OrdCat SI))
    : earlier ₒ F ×ₒ G
        ≃@{PSh (OrdCat SI)}
        earlier ₒ (F ×ₒ (later ₒ G)) :=
    natural_iso_proj earlier_later_prod_nat (F, G).


  Program Definition later_preserves_exp_nat (Y : obj (PSh (OrdCat SI))) :
    functor_compose (functor_fix_left exp_func ₒ Y) later
      ≃@{FuncCat (PSh (OrdCat SI)) (PSh (OrdCat SI))}
      functor_compose later (functor_fix_left exp_func ₒ (later ₒ Y)) :=
    fully_faithful_iso (in_right_of_hom _ _)
      (isomorphic_sym
         (isomorphic_trans
            (adj_compose_swap
               (id_functor _)
               later
               (prod_exp_adj (later ₒ Y)))
            (isomorphic_trans
               (functor_compose_iso_proper
                  (functor_prod_iso_proper
                     (isomorphic_refl _)
                     functor_compose_left_id_iso)
                  (isomorphic_refl _))
               (isomorphic_trans
                  (adj_compose_swap
                     (functor_compose (id_functor _)
                        (opposite_func
                           (functor_fix_right (prod_func _) ₒ (later ₒ Y))))
                     (id_functor _)
                     later_adj)
                  (isomorphic_sym
                     (isomorphic_trans
                        (adj_compose_swap
                           (id_functor _)
                           (functor_fix_left_o_map exp_func Y)
                           later_adj)
                        (isomorphic_trans
                           (functor_compose_iso_proper
                              (functor_prod_iso_proper
                                 (isomorphic_refl _)
                                 (functor_compose_left_id_iso))
                              (isomorphic_refl _))
                           (isomorphic_trans
                              (adj_compose_swap
                                 (functor_compose (id_functor _)
                                    (opposite_func earlier))
                                 (id_functor _)
                                 (prod_exp_adj Y))
                              (functor_compose_iso_proper
                                 (functor_prod_iso_proper
                                    (isomorphic_trans
                                       (functor_compose_iso_proper
                                          (isomorphic_sym
                                             functor_compose_left_id_iso)
                                          (isomorphic_refl _))
                                       (isomorphic_sym
                                          (isomorphic_trans
                                             (functor_compose_iso_proper
                                                (isomorphic_sym
                                                   functor_compose_left_id_iso)
                                                (isomorphic_refl _))
                                             (isomorphic_trans
                                                functor_opposite_compose
                                                (isomorphic_sym
                                                   (isomorphic_trans
                                                      functor_opposite_compose
                                                      (functor_opposite_proper
                                                         (isomorphic_trans
                                                            functor_fix_right_pre_comp
                                                            (isomorphic_sym
                                                               (isomorphic_trans
                                                                  functor_fix_right_post_comp
                                                                  (isomorphic_sym
                                                                     (isomorphic_trans
                                                                        (natural_iso_proj
                                                                           (functor_fix_right_proper_iso
                                                                              earlier_later_prod_nat) _)
                                                                        (isomorphic_sym
                                                                           (isomorphic_trans functor_fix_right_commute
                                                                              (natural_iso_proj
                                                                                 (functor_fix_right_proper_iso
                                                                                    (isomorphic_trans
                                                                                       functor_compose_assoc_iso
                                                                                       (isomorphic_refl _))) _)))))))))))))))
                                    (isomorphic_refl _))
                                 (isomorphic_refl _)))))))))).
  Next Obligation.
    intros; reflexivity.
  Defined.
  Next Obligation.
    intros; reflexivity.
  Defined.
  Next Obligation.
    intros; reflexivity.
  Defined.
  Next Obligation.
    intros; reflexivity.
  Defined.
  Fail Next Obligation.

  Definition later_preserves_exp (F G : obj (PSh (OrdCat SI)))
    : later ₒ (G ↑ₒ F)
        ≃
        ((later ₒ G) ↑ₒ (later ₒ F)) :=
    natural_iso_proj (later_preserves_exp_nat F) G.

End later_preserves.

Section earlier_later_earlier_later_prod.
  Local Transparent right_adj_preserves_prods.

  Lemma earlier_later_earlier_later_prod {SI} (F G : PreSheaf (OrdCat SI)) :
    natural_comp (earlier ₕ (backward (later_prod F G)))
      (forward (earlier_later_nat_iso (C := Typ)) ₙ (F ×ₒ G)) =
      natural_comp
      (forward (earlier_prod (later ₒ F) (later ₒ G)))
      ((forward earlier_later_nat_iso ₙ F) ×ₕ (forward earlier_later_nat_iso ₙ G)).
  Proof.
    apply natural_equiv_unpack; intros α; simpl.
    extensionality x.
    destruct x as [x y]; simpl in *.
    repeat (rewrite_cone_hom_commutes_back; simpl).
    repeat f_equiv.
  Qed.

End earlier_later_earlier_later_prod.

Class Contractive
  {SI : indexT} {F G : PreSheaf (OrdCat SI)} (η : natural F G) := MkContr {
  contr_hom : natural (later ₒ F) G;
  contr_hom_after_next : η = contr_hom ∘ (next ₙ F);
}.
Global Arguments MkContr {_ _ _ _} _ _.
Global Arguments contr_hom {_ _ _} _ {_}.
Global Arguments contr_hom_after_next {_ _ _} _ {_}.

Global Program Instance Contractive_comp_l {SI : indexT} {F G H : PreSheaf (OrdCat SI)}
  (η : natural F G) `{!Contractive η} (η' : natural G H) :
  Contractive (η' ∘@{PSh _} η) :=
  MkContr (η' ∘@{PSh _} contr_hom η) _.
Next Obligation.
  intros ???? η ? η'.
  rewrite {1}(contr_hom_after_next η) comp_assoc //.
Qed.
Fail Next Obligation.

Global Program Instance Contractive_comp_r {SI : indexT} {F G H : PreSheaf (OrdCat SI)}
  (η : natural F G) `{!Contractive η} (η' : natural H F) :
  Contractive (η ∘@{PSh _} η') :=
  MkContr (contr_hom η ∘@{PSh _} (later ₕ η')) _.
Next Obligation.
  intros ???? η ? η'.
  rewrite {1}(contr_hom_after_next η) !comp_assoc.
  rewrite -naturality //.
Qed.
Fail Next Obligation.

(* TODO: move *)
Tactic Notation "eta_expand_equation" uconstr(a) :=
  match goal with
    |- _ = _ =>
      pattern a;
      match goal with
      | |- (λ z : ?T, ?A = ?B) _ =>
          let Hf := fresh "Hf" in
          unshelve eassert ((λ z : T, A) = (λ z : T, B)) as Hf;
          last by eapply (equal_f Hf a)
      end
  end.

Tactic Notation "eta_expand_equation" uconstr(a) "of" "type" uconstr(T) :=
  match goal with
    |- _ = _ =>
      pattern a;
      match goal with
      | |- (λ z, ?A = ?B) _ =>
          let Hf := fresh "Hf" in
          unshelve eassert ((λ z : T, A) = (λ z : T, B)) as Hf;
          last by eapply (equal_f Hf a)
      end
  end.

Section fixpoint.
  Context {SI : indexT}.

  (* TODO: consider moving if useful in other places. *)
  Definition le_conv_l {α β γ : SI} (Heq : α = β) (Hle : α ⪯ γ) : β ⪯ γ :=
    match Heq in _ = z return z ⪯ γ with eq_refl => Hle end.
  Definition le_conv_r {α β γ : SI} (Heq : γ = β) (Hle : α ⪯ γ) : α ⪯ β :=
    match Heq in _ = z return α ⪯ z with eq_refl => Hle end.
  Definition psh_conv (X : PreSheaf (OrdCat SI))
    {α β : SI} (Heq : α = β) (x : X ₒ α) : X ₒ β :=
    match Heq in _ = z return X ₒ z with eq_refl => x end.
  Definition psh_conv_sym (X : PreSheaf (OrdCat SI))
    {α β : SI} (Heq : α = β) (x : X ₒ α) (y : X ₒ β) :
    psh_conv X Heq x = y ↔ x = psh_conv X (eq_sym Heq) y.
  Proof. destruct Heq; done. Qed.
  Definition psh_conv_trans (X : PreSheaf (OrdCat SI))
    {α β γ: SI} (Heq : α = β) (Heq' : β = γ) (x : X ₒ α) :
    psh_conv X (eq_trans Heq Heq') x = psh_conv X Heq' (psh_conv X Heq x).
  Proof. destruct Heq; destruct Heq'; done. Qed.
  Lemma psh_conv_hom_action (X : PreSheaf (OrdCat SI))
    {α β γ : SI} (Hle : γ ⪯ β) (Heq : α = β) (x : X ₒ α) :
    (X ₕ Hle) (psh_conv X Heq x) = (X ₕ (le_conv_r (eq_sym Heq) Hle)) x.
  Proof. destruct Heq; done. Qed.
  Lemma psh_conv_hom_action' (X : PreSheaf (OrdCat SI))
    {α β γ : SI} (Hle : α ⪯ γ) (Heq : α = β) (x : X ₒ γ) :
    psh_conv X Heq ((X ₕ Hle) x) = (X ₕ (le_conv_l Heq Hle)) x.
  Proof. destruct Heq; done. Qed.
  Lemma psh_setoid_conv {X : PreSheaf (OrdCat SI)}
    {α β : SI} (Heq : α = β) (x : X ₒ α) :
    psh_conv X Heq x = typ_conv (f_equal (X ₒ) Heq) x.
  Proof. destruct Heq; done. Qed.
  Lemma psh_exp_push_conv (X Y : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ X) Y) {β} (Hle : β ⪯ α) (x : X ₒ β)
    {γ} (Heq : β = γ) :
    psh_conv Y Heq ((η ₙ β) (Hle, x)) = (η ₙ γ) (le_conv_l Heq Hle, psh_conv X Heq x).
  Proof. destruct Heq; done. Qed.

  Lemma psh_is_lim_side_setoid_conv {J} {F : functor J Typ}
    {X} (il : is_limit F X) δ {Y : Type} (Heq : Y = X) (y : Y) :
  ic_side (il_is_cone il) δ (typ_conv Heq y) =
  ic_side (il_is_cone (is_limit_trans (C := Typ) (eq_sym Heq) il)) δ y.
  Proof. destruct Heq; done. Qed.

  Record fx_raw (X : PreSheaf (OrdCat SI)) (dsp : downset_pred SI) := Mkfxr
    { fxr_map :> ∀ α : downset dsp, X ₒ (α : SI);
      fxr_map_commutes : ∀ (β α : downset dsp) (Hβα : β ⪯ α),
        fxr_map β = (X ₕ Hβα) (fxr_map α);
    }.
  Global Arguments Mkfxr {_ _} _ _.
  Global Arguments fxr_map {_ _} _ _.
  Global Arguments fxr_map_commutes {_ _} _ [_ _] _.

  Lemma fx_raw_applied_eq {X : PreSheaf (OrdCat SI)} {dsp : downset_pred SI}
    (fx : fx_raw X dsp) (α : SI) (Hα Hα' : dsp α) :
    fx (MkDS (squash Hα)) = fx (MkDS (squash Hα')).
  Proof. replace Hα with Hα'; first done. apply proof_irrelevance. Qed.

  Program Definition fx_raw_down_le
    (X : PreSheaf (OrdCat SI)) {dsp : downset_pred SI}
    (fx : fx_raw X dsp) {α} (Hin : dsp α) : fx_raw X (le_dsp α) :=
  Mkfxr (λ β, fx (MkDS (squash (dsp_pred_downwards _ (unsquash (ds_in_dsp β)) Hin)))) _.
  Next Obligation.
    repeat intros ????? β γ ?; rewrite /=.
    rewrite -(@fxr_map_commutes _ _ fx
                (MkDS (squash (dsp_pred_downwards _ (unsquash (ds_in_dsp β)) Hin)))
                (MkDS (squash (dsp_pred_downwards _ (unsquash (ds_in_dsp γ)) Hin)))) //.
  Qed.

  Program Definition fx_raw_down_lt
    (X : PreSheaf (OrdCat SI)) {dsp : downset_pred SI}
    (fx : fx_raw X dsp) {α} (Hin : dsp α) : fx_raw X (lt_dsp α) :=
    Mkfxr (λ β, fx (MkDS (squash (dsp_pred_downwards _
      (index_lt_le_subrel _ _ (unsquash (ds_in_dsp β))) Hin)))) _.
  Next Obligation.
    repeat intros ????? β γ ?; rewrite /=.
    rewrite -(@fxr_map_commutes _ _ fx
     (MkDS (squash (dsp_pred_downwards _
              (index_lt_le_subrel _ _ (unsquash (ds_in_dsp β))) Hin)))
     (MkDS (squash (dsp_pred_downwards _
              (index_lt_le_subrel _ _ (unsquash (ds_in_dsp γ))) Hin)))) //.
  Qed.

  Definition fx_raw_zero (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ (later ₒ X)) X) : X ₒ zero :=
    (η ₙ zero)
      (index_zero_minimum _,
       typ_conv (eq_sym (later_func_o_map_zero X)) ()).

  Lemma fx_raw_zero_ext X
    {α} (η : natural (yoneda ₒ α ×ₒ (later ₒ X)) X)
    {α'} (η' : natural (yoneda ₒ α' ×ₒ (later ₒ X)) X) :
    (∀ Hle Hle' x, (η ₙ zero) (Hle, x) = (η' ₙ zero) (Hle', x)) →
    fx_raw_zero X η = fx_raw_zero X η'.
  Proof.
    rewrite /fx_raw_zero; intros H.
    erewrite ->H.
    done.
  Qed.

  Lemma fx_raw_zero_ext' X {α} (η η' : natural (yoneda ₒ α ×ₒ (later ₒ X)) X) :
    (η ₙ zero = η' ₙ zero) →
    fx_raw_zero X η = fx_raw_zero X η'.
  Proof.
    intros Heq; apply fx_raw_zero_ext; intros ???; rewrite Heq; f_equiv.
    f_equiv.
    simpl; apply proof_irrelevance.
  Qed.

  Program Definition fx_raw_succ (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ (later ₒ X)) X)
    {β} (Hβ : succ β ⪯ α) (x : X ₒ β) : X ₒ (succ β) :=
    (η ₙ (succ β))
      (Hβ, typ_conv (eq_sym (later_func_o_map_succ X β)) x).

  Lemma fx_raw_succ_ext X
    {α} (η : natural (yoneda ₒ α ×ₒ (later ₒ X)) X)
    {α'} (η' : natural (yoneda ₒ α' ×ₒ (later ₒ X)) X)
    {β} (Hβ : succ β ⪯ α) (Hβ' : succ β ⪯ α') x y :
    (∀ Hle Hle' x, (η ₙ (succ β)) (Hle, x) = (η' ₙ (succ β)) (Hle', x)) →
    x = y → fx_raw_succ X η Hβ x = fx_raw_succ X η' Hβ' y.
  Proof.
    rewrite /fx_raw_succ.
    intros H1 ->.
    erewrite ->H1.
    f_equiv; split; done.
  Qed.

  Lemma fx_raw_succ_ext' X {α} (η η' : natural (yoneda ₒ α ×ₒ (later ₒ X)) X)
    {β} (Hβ Hβ' : succ β ⪯ α) x y :
    (η ₙ (succ β) = η' ₙ (succ β)) →
    x = y → fx_raw_succ X η Hβ x = fx_raw_succ X η' Hβ' y.
  Proof.
    intros Heq; apply fx_raw_succ_ext; intros ???; rewrite Heq.
    do 2 f_equiv.
    simpl; apply proof_irrelevance.
  Qed.

  Program Definition fx_raw_cone (X : PreSheaf (OrdCat SI)) α
    (fx : fx_raw X (lt_dsp α)) : cone (lift_func (lt_dsp α) X) :=
    MkCone (1ₒ) (λ j, λ _, fx j) _.
  Next Obligation.
    repeat intros ?.
    extensionality x.
    apply fxr_map_commutes.
  Qed.
  Fail Next Obligation.

  Definition fx_raw_lim (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X)
    {β : limit_idx SI} (Hβ : β ⪯ α) (fx : fx_raw X (lt_dsp β)) : X ₒ (β : SI) :=
    (η ₙ (β : SI))
      (Hβ,
       typ_conv
         (eq_sym (later_func_o_map_lim X β))
         (cone_hom_map
            (bang
               (term_is_terminal (complete (lift_func (lt_dsp β) X)))
               (fx_raw_cone X β fx))
            ())).

  Lemma fx_raw_lim_ext (X : PreSheaf (OrdCat SI)) {α} (η : natural (yoneda ₒ α ×ₒ (later ₒ X)) X)
    {α'} (η' : natural (yoneda ₒ α' ×ₒ (later ₒ X)) X)
    {β : limit_idx SI} (Hβ : β ⪯ α) (Hβ' : β ⪯ α') (fx fx' : fx_raw X (lt_dsp β)) :
    (∀ Hle Hle' x, (η ₙ (β : SI)) (Hle, x) = (η' ₙ (β : SI)) (Hle', x)) →
    (∀ γ (Hγ : γ ≺ β), fx (MkDS (lt_dsp β) (squash Hγ)) = fx' (MkDS (lt_dsp β) (squash Hγ))) →
    fx_raw_lim X η Hβ fx = fx_raw_lim X η' Hβ' fx'.
  Proof.
    rewrite /fx_raw_lim; intros Heq Hfxfx'.
    rewrite (Heq Hβ Hβ').
    repeat f_equiv.
    erewrite (hom_to_limit_unique _ _ _
             (limiting_cone_is_limit
                (term_is_terminal (complete (lift_func (lt_dsp β) X))))
             (cone_is_cone (fx_raw_cone X β fx))).
    - simpl.
      reflexivity.
    - intros [j Hpr].
      extensionality t; simpl.
      rewrite /= (Hfxfx' _ (unsquash Hpr)) //.
    - intros; simpl.
      extensionality t; simpl.
      rewrite Hfxfx'.
      + apply (unsquash (ds_in_dsp j)).
      + intros; simpl.
        f_equal.
  Qed.

  Lemma fx_raw_lim_ext' (X : PreSheaf (OrdCat SI)) {α}
    (η η': natural (yoneda ₒ α ×ₒ later_func X) X)
    {β : limit_idx SI} (Hβ Hβ' : β ⪯ α) (fx fx' : fx_raw X (lt_dsp β)) :
    (η ₙ (β : SI) = η' ₙ (β : SI)) →
    (∀ γ (Hγ : γ ≺ β), fx (MkDS (lt_dsp β) (squash Hγ)) = fx' (MkDS (lt_dsp β) (squash Hγ))) →
    fx_raw_lim X η Hβ fx = fx_raw_lim X η' Hβ' fx'.
  Proof.
    intros Heq; apply fx_raw_lim_ext; intros ???; rewrite Heq.
    do 2 f_equiv.
    simpl; apply proof_irrelevance.
  Qed.

  Definition fx_raw_compat_zero (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X)
    {dsp} (fx : fx_raw X dsp) (Hz : dsp zero) : Prop :=
    fx (MkDS (squash Hz)) = fx_raw_zero X η.

  Definition fx_raw_compat_succ (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X)
    {dsp} (fx : fx_raw X dsp) {β}
    (Hsβ : dsp (succ β)) (Hβα : succ β ⪯ α) : Prop :=
    fx (MkDS (squash Hsβ)) =
        fx_raw_succ X η Hβα
         (fx (MkDS (squash (dsp_pred_downwards _
           (index_lt_le_subrel _ _ (index_succ_greater β)) Hsβ)))).

  Definition fx_raw_compat_lim (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X)
    {dsp} (fx : fx_raw X dsp) {β : limit_idx SI}
    (Hβ : dsp β) (Hβα : β ⪯ α) : Prop :=
    fx (MkDS (squash Hβ)) = fx_raw_lim X η Hβα (fx_raw_down_lt X fx Hβ).

  Program Definition fx_raw_compat (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X)
    {dsp} (fx : fx_raw X dsp) :
    index_rect (λ β, dsp β → β ⪯ α → Prop) :=
    MkIR
      (λ Hz _, fx (MkDS (squash Hz)) = fx_raw_zero X η)
      (λ β _ Hsβ Hsβ',
        fx (MkDS (squash Hsβ)) =
        fx_raw_succ X η Hsβ'
         (fx (MkDS (squash (dsp_pred_downwards _
           (index_lt_le_subrel _ _ (index_succ_greater β)) Hsβ)))))
      (λ β _ Hβ Hsβ',
        fx (MkDS (squash Hβ)) = fx_raw_lim X η Hsβ' (fx_raw_down_lt X fx Hβ))
      _.
  Next Obligation.
    split; last reflexivity.
    intros β Hβ1 Hβ2 ?; simpl.
    destruct β as [β Hβ2' Hβ1']; simpl in *.
    replace Hβ1 with Hβ1' by apply proof_irrelevance.
    replace Hβ2 with Hβ2' by apply proof_irrelevance.
      reflexivity.
  Qed.

  Lemma fx_raw_compat_equiv (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X)
    {dsp} (fx : fx_raw X dsp) {dsp'} (fx' : fx_raw X dsp')
    {β} (Hβid : dsp β) (Hβid' : dsp' β) (Hβle : β ⪯ α) :
    (∀ γ (Hγ : dsp γ) (Hγ' : dsp' γ), fx (MkDS (squash Hγ)) = fx' (MkDS (squash Hγ'))) →
    fx_raw_compat X η fx β Hβid Hβle ↔ fx_raw_compat X η fx' β Hβid' Hβle.
  Proof.
    intros Hfxfx'.
    destruct β as [|β|β] using index_destruct; simpl_index_rect.
    - rewrite /fx_raw_compat_zero Hfxfx' //.
    - rewrite /fx_raw_compat_succ !Hfxfx' //.
      eapply dsp_lt; last apply Hβid'.
      done.
    - rewrite /fx_raw_compat_lim Hfxfx'.
      f_equiv.
      erewrite ->fx_raw_lim_ext'; [done|done|].
      intros ??; rewrite /fx_raw_down_lt /= Hfxfx' //.
      eapply dsp_lt; last apply Hβid'.
      done.
  Qed.

  Record fx_data (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X) (dsp : downset_pred SI) := Mkfxd
    { fxd_fx :> fx_raw X dsp;
      fxd_compat : ∀ β Hβid Hβle, fx_raw_compat X η fxd_fx β Hβid Hβle;
    }.
  Global Arguments Mkfxd {_ _ _ _} _ _.
  Global Arguments fxd_fx {_ _ _ _} _.
  Global Arguments fxd_compat {_ _ _ _} _ [_] _ _.

  Local Opaque typ_complete typ_lim_side.

  Lemma fx_data_succ_back (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ (later ₒ X)) X) {dsp : downset_pred SI}
    (fxd : fx_data X η dsp) :
    ∀ (β : downset dsp) (Hsβ : succ β ⪯ α),
      (X ₕ (index_lt_le_subrel _ _ (index_succ_greater β)))
        (fx_raw_succ X η Hsβ (fxd β)) = fxd β.
  Proof.
    intros [β Hβid] Hsβ; simpl in *.
    pose proof (fxd_compat fxd) as Hcmp.
    induction β as [|β IHβ|β IHβ] using index_ind;
      specialize (Hcmp _ (unsquash Hβid));
      simpl_index_rect in Hcmp; simpl in Hcmp.
    - rewrite Hcmp; last by auto.
      rewrite /fx_raw_zero /fx_raw_succ /= -(psh_naturality η).
      f_equiv; simpl.
      unfold hom_prod.
      simpl.
      f_equiv; first (simpl; apply proof_irrelevance).
      apply typ_conv_sym.
      apply unit_pi.
    - assert (succ β ⪯ α) as Hβα.
      { apply index_succ_le; done. }
      rewrite (Hcmp Hβα).
      rewrite /fx_raw_succ -(psh_naturality η) /=.
      unfold hom_prod; simpl.
      f_equiv; simpl.
      f_equiv; first (simpl; apply proof_irrelevance).
      rewrite -{2}(IHβ _ Hβα).
      rewrite /fx_raw_succ /=.
      match goal with
      |- context ctx [(η ₙ succ β) ?B] =>
        remember ((η ₙ succ β) B) as s; clear Heqs
      end.
      eta_expand_equation s.
      apply (hom_to_limit_unique _ _ _
               (later_func_o_map_is_limit X (succ β))
               (cone_is_cone (cone_at X (succ β) (lt_dsp (succ β))
                                (in_lt_dsp_le (reflexivity (succ β)))))).
      + intros ?.
        extensionality x; simpl.
        rewrite_cone_hom_commutes_back; simpl.
        rewrite later_func_o_map_is_limit_succ.
        rewrite trans_side_of_is_limit_trans /=.
        rewrite hom_trans_typ_conv' /=.
        rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
        do 2 f_equal.
        unfold OrdCat.
        simpl.
        apply proof_irrelevance.
      + intros ?.
        extensionality x; simpl.
        rewrite later_func_o_map_is_limit_succ.
        rewrite trans_side_of_is_limit_trans /=.
        rewrite hom_trans_typ_conv' /=.
        rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
        rewrite -psh_h_map_comp.
        do 2 f_equal.
        apply proof_irrel.
    - assert (β ⪯ α) as Hβα.
      { eapply index_lt_le_subrel, index_lt_le_trans;
          [apply index_succ_greater|done]. }
      rewrite (Hcmp Hβα).
      rewrite /fx_raw_lim -(psh_naturality η) /=.
      f_equiv.
      unfold hom_prod.
      simpl.
      f_equiv; first (simpl; apply proof_irrelevance).
      eta_expand_equation () of type unit.
      apply (hom_to_limit_unique _ _ _
               (later_func_o_map_is_limit X β)
               (cone_is_cone (fx_raw_cone X β (fx_raw_down_lt X fxd (unsquash Hβid))))).
      + intros δ.
        extensionality x; simpl in *.
        rewrite_cone_hom_commutes_back; simpl.
        rewrite later_func_o_map_is_limit_succ.
        rewrite trans_side_of_is_limit_trans.
        rewrite hom_trans_typ_conv' /=.
        rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
        assert (succ δ ⪯ β) as Hsδ.
        { apply index_lt_le_subrel, limit_index_is_limit, (unsquash (ds_in_dsp δ)). }
        assert (succ δ ⪯ α) as Hsδα.
        { etrans; [done|apply Hβα]. }
        match goal with
          |- context ctx [X ₕ ?B] =>
            replace B with
            (transitivity (index_lt_le_subrel _ _ (index_succ_greater _)) Hsδ)
            by apply proof_irrel
        end.
        rewrite h_map_comp /=.
        rewrite -(IHβ _ (unsquash (ds_in_dsp δ)) _ Hsδα).
        f_equiv.
        rewrite -(psh_naturality η) /=.
        rewrite /(fx_raw_succ X η Hsδα).
        f_equal; simpl.
        unfold hom_prod.
        simpl.
        f_equiv; first (simpl; apply proof_irrelevance).
        rewrite /proj_cone_hom /=.
        rewrite later_func_o_map_is_limit_succ.
        rewrite bang_of_is_limit_trans.
        rewrite hom_trans_typ_conv' /=.
        f_equiv.
        rewrite later_func_o_map_is_limit_lim /=.
        rewrite trans_side_of_is_limit_trans /=.
        rewrite hom_trans_typ_conv' /=.
        rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
        rewrite ic_side_limiting_cone_is_limit.
        rewrite_cone_hom_commutes_back; simpl.
        apply fx_raw_applied_eq.
      + intros δ.
        extensionality x; simpl in *.
        rewrite psh_is_lim_side_setoid_conv eq_sym_involutive /=.
        match goal with
        | |- context [(ic_side _ ?j)
                       ((cone_hom_map ?c) ?d)] =>
            pose proof (typ_cone_hom_commutes c j d) as Hcheq;
            simpl in Hcheq; rewrite Hcheq; clear Hcheq
        end.
        rewrite trans_side_of_is_limit_trans.
        rewrite later_func_o_map_is_limit_lim /=.
        rewrite trans_side_of_is_limit_trans /=.
        rewrite -hom_trans_trans eq_trans_sym_inv_l /= hom_trans_refl //=.
  Qed.

  Lemma fx_data_lim_back (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ (later ₒ X)) X)
    {β : limit_idx SI} (Hβ : β ⪯ α)
    (fxd : fx_data X η (lt_dsp β))
    {γ} (Hγβ : γ ≺ β) :
      (X ₕ (index_lt_le_subrel _ _ Hγβ))
        (fx_raw_lim X η Hβ fxd) = fxd (MkDS (lt_dsp _) (squash Hγβ)).
  Proof.
    pose proof (fxd_compat fxd) as Hcmp.
    induction γ as [|γ IHγ|γ IHγ] using index_strong_ind;
      specialize (Hcmp _ Hγβ);
      simpl_index_rect in Hcmp; simpl in Hcmp.
    - rewrite Hcmp; last by auto.
      rewrite /fx_raw_zero /fx_raw_succ /= -(psh_naturality η).
      f_equiv; simpl.
      unfold hom_prod.
      simpl.
      f_equiv; first (simpl; apply proof_irrelevance).
      apply typ_conv_sym.
      apply unit_pi.
    - assert (succ γ ⪯ α) as Hsγα.
      { eapply index_lt_le_subrel, index_lt_le_trans; eassumption. }
      rewrite (Hcmp Hsγα) /fx_raw_succ.
      rewrite -IHγ // -!(psh_naturality η) /=.
      f_equiv; simpl.
      unfold hom_prod.
      simpl.
      f_equiv; first (simpl; apply proof_irrelevance).
      eta_expand_equation () of type unit.
      apply (hom_to_limit_unique _ _ _
               (later_func_o_map_is_limit X (succ γ))
               (cone_is_cone (fx_raw_cone X (succ γ) (fx_raw_down_lt X fxd Hγβ)))).
      + intros ?; extensionality x; simpl.
        rewrite_cone_hom_commutes_back; simpl.
        rewrite later_func_o_map_is_limit_lim.
        rewrite trans_side_of_is_limit_trans /=.
        rewrite hom_trans_typ_conv' /=.
        rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
        rewrite ic_side_limiting_cone_is_limit.
        rewrite_cone_hom_commutes_back; simpl.
        reflexivity.
      + intros δ'; rewrite /=.
        extensionality x.
        destruct x; simpl.
        rewrite later_func_o_map_is_limit_succ.
        rewrite trans_side_of_is_limit_trans /=.
        rewrite hom_trans_typ_conv' /=.
        rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
        rewrite -IHγ; last first.
        { by apply index_succ_iff_proj_r2l, (unsquash (ds_in_dsp δ')). }
        rewrite /fx_raw_lim -!(psh_naturality η) /=.
        f_equal.
        unfold hom_prod; simpl; f_equiv; first apply proof_irrel.
        eta_expand_equation () of type unit.
        apply (hom_to_limit_unique _ _ _
                 (later_func_o_map_is_limit X δ')
                 (cone_is_cone (fx_raw_cone X δ'
                   (fx_raw_down_lt X fxd (transitivity (unsquash (ds_in_dsp δ')) Hγβ))))).
        * intros δ''; rewrite /=.
          extensionality x.
          destruct x; simpl.
          rewrite_cone_hom_commutes_back; simpl.
          rewrite later_func_o_map_is_limit_lim.
          rewrite trans_side_of_is_limit_trans /=.
          rewrite hom_trans_typ_conv' /=.
          rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
          rewrite ic_side_limiting_cone_is_limit.
          rewrite_cone_hom_commutes_back; simpl.
          reflexivity.
        * intros δ''; rewrite /=.
          extensionality x; destruct x; simpl.
          repeat (rewrite_cone_hom_commutes_back; simpl).
          rewrite later_func_o_map_is_limit_lim.
          rewrite trans_side_of_is_limit_trans /=.
          rewrite hom_trans_typ_conv' /=.
          rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
          rewrite ic_side_limiting_cone_is_limit.
          rewrite_cone_hom_commutes_back; simpl.
          reflexivity.
    - assert (γ ⪯ α) as Hγα.
      { eapply index_lt_le_subrel, index_lt_le_trans; done. }
      rewrite (Hcmp Hγα).
      rewrite /fx_raw_lim /fx_raw_succ -(psh_naturality η) /=.
      f_equal.
      unfold hom_prod; simpl; f_equiv; first apply proof_irrel.
      eta_expand_equation () of type unit.
      apply (hom_to_limit_unique _ _ _
               (later_func_o_map_is_limit X γ)
               (cone_is_cone (fx_raw_cone X γ (fx_raw_down_lt X fxd Hγβ)))).
      + intros δ; simpl in *.
        extensionality x; destruct x; simpl.
        rewrite_cone_hom_commutes_back; simpl.
        rewrite later_func_o_map_is_limit_lim.
        rewrite trans_side_of_is_limit_trans.
        rewrite hom_trans_typ_conv' /=.
        rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
        rewrite ic_side_limiting_cone_is_limit.
        rewrite_cone_hom_commutes_back; simpl.
        reflexivity.
      + intros δ; simpl in *.
        rewrite later_func_o_map_is_limit_lim.
        rewrite trans_side_of_is_limit_trans.
        extensionality x; destruct x; simpl.
        rewrite hom_trans_typ_conv' /=.
        rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
        rewrite ic_side_limiting_cone_is_limit.
        rewrite_cone_hom_commutes_back; done.
  Qed.

  Lemma fx_data_agree (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X) (dsp dsp' : downset_pred SI)
    (fx : fx_data X η dsp) (fx' : fx_data X η dsp') {β}
    (Hle : β ⪯ α) (Hβ : dsp β) (Hβ' : dsp' β) :
    fx (MkDS (squash Hβ)) = fx' (MkDS (squash Hβ')).
  Proof.
    induction β as [|β IHβ|β IHβ]using index_ind;
      pose proof (fxd_compat fx Hβ) as Hcmp;
      pose proof (fxd_compat fx' Hβ') as Hcmp';
      simpl_index_rect in Hcmp; simpl_index_rect in Hcmp'.
    - rewrite Hcmp // Hcmp' //.
    - rewrite (Hcmp Hle) (Hcmp' Hle).
      erewrite IHβ; first reflexivity.
      by etrans; first apply index_lt_le_subrel, index_succ_greater.
    - rewrite (Hcmp Hle) (Hcmp' Hle).
      erewrite fx_raw_lim_ext'; [done|done|].
      intros ??; rewrite /fx_raw_down_lt /=.
      apply IHβ; first done.
      by etrans; first apply index_lt_le_subrel.
  Qed.

  Program Definition fx_data_zero (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X) :
    fx_data X η (le_dsp zero) :=
    Mkfxd (Mkfxr
      (λ δ, psh_conv X (eq_sym (le_zero_zero _ (unsquash (ds_in_dsp δ))))
        (fx_raw_zero X η)) _) _.
  Next Obligation.
    intros ?? η ???; simpl.
    rewrite !psh_setoid_conv.
    apply typ_conv_sym.
    rewrite -!eq_sym_map_distr.
    rewrite -hom_trans_typ_conv'.
    rewrite hom_trans_typ_conv.
    rewrite !eq_sym_map_distr.
    rewrite -psh_setoid_conv hom_trans_typ_conv'.
    rewrite /fx_raw_zero.
    rewrite psh_exp_push_conv /=.
    rewrite -(psh_naturality η).
    rewrite -psh_setoid_conv.
    rewrite psh_exp_push_conv /=.
    f_equiv; simpl.
    f_equiv; first (simpl; apply proof_irrelevance).
    rewrite /= !psh_setoid_conv.
    apply typ_conv_sym.
    apply unit_pi.
  Qed.
  Next Obligation.
    intros ???? Hβid ?; simpl.
    pose proof (le_zero_zero _ Hβid); subst.
    simpl_index_rect; simpl.
    rewrite /fx_raw_zero psh_exp_push_conv.
    f_equiv; simpl.
    f_equiv; first (simpl; apply proof_irrelevance).
    apply typ_conv_sym.
    apply unit_pi.
  Qed.
  Fail Next Obligation.

  Program Definition fx_data_succ (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X) {β} (Hsβ : succ β ⪯ α)
    (fxd : fx_data X η (le_dsp β)) : fx_data X η (le_dsp (succ β)) :=
    Mkfxd (Mkfxr
      (λ δ, match le_succ_dec (unsquash (ds_in_dsp δ)) return X ₒ (δ : SI) with
            | left Hle => fxd (MkDS (le_dsp β) (squash Hle))
            | right Heq =>
                psh_conv X (eq_sym Heq)
                  (fx_raw_succ X η Hsβ
                     (fxd (MkDS (le_dsp β) (squash (reflexivity _)))))
            end) _) _.
  Next Obligation.
    intros ????? fxd γ γ' Hγγ'; simpl in *.
    destruct le_succ_dec as [Hle|Heq];
      destruct le_succ_dec as [Hle'|Heq'].
    - rewrite -(@fxr_map_commutes _ _ (fxd_fx fxd)
        (MkDS (le_dsp β) (squash Hle)) (MkDS (le_dsp β) (squash Hle'))); done.
    - rewrite psh_conv_hom_action.
      replace (le_conv_r (eq_sym (eq_sym Heq')) Hγγ') with
        (transitivity Hle
           (index_lt_le_subrel _ _ (index_succ_greater _)));
        last (simpl; apply proof_irrelevance).
      rewrite h_map_comp /=.
      etrans; first apply (@fxr_map_commutes _ _ fxd (MkDS (le_dsp β) (squash Hle)) (MkDS (le_dsp β)
        (squash (reflexivity _))) Hle).
      f_equiv.
      rewrite (fx_data_succ_back X η fxd (MkDS (squash (reflexivity _)))) //.
    - exfalso.
      apply (index_le_lt_contradict γ γ'); first done.
      eapply index_le_lt_trans; last by rewrite Heq; apply index_succ_greater.
      done.
    - assert (γ = γ') as -> by by apply downset_eq; rewrite Heq Heq' //.
      replace Hγγ' with (reflexivity _ : γ' ⪯ γ'); last (simpl; apply proof_irrelevance).
      rewrite h_map_id /=.
      apply psh_conv_sym.
      rewrite -psh_conv_trans.
      replace Heq' with Heq by apply proof_irrel.
      rewrite eq_trans_sym_inv_r //=.
  Qed.
  Next Obligation.
    intros ??? γ Hγ fxd β Hsβ Hβα; simpl.
    destruct (le_succ_dec Hsβ) as [Hle| ->].
    { pose proof (fxd_compat fxd Hle Hβα) as Hcmp.
      rewrite (@fx_raw_compat_equiv X α η _ fxd (le_dsp (succ γ)) _ β Hle Hsβ) in Hcmp; first exact Hcmp.
      intros γ' Hγ'id Hsγγ'; rewrite /=; destruct le_succ_dec as [|Heq];
        first reflexivity.
      exfalso.
      apply (index_le_lt_contradict γ' γ); first done.
      rewrite Heq; apply index_succ_greater.
    }
    simpl_index_rect; rewrite /fx_raw_compat_succ /=.
    assert (¬ (succ γ ⪯ γ)).
    { intros Hle; apply index_succ_le_lt in Hle; eapply index_lt_irrefl; done. }
    destruct (le_succ_dec (unsquash _)) as [|Heq]; first done.
    destruct le_succ_dec as [|Heq'].
    - replace Heq with (eq_refl (succ γ)) by apply proof_irrel.
      simpl; f_equiv; first (apply proof_irrelevance).
      reflexivity.
    - exfalso.
      eapply (index_lt_irrefl γ), index_succ_le_lt; rewrite {2}Heq'; done.
  Qed.
  Fail Next Obligation.

  Program Definition fx_data_glue (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X) {β}
    (Hle : β ⪯ α)
    (fxds : ∀ γ, γ ≺ β → fx_data X η (le_dsp γ)) : fx_data X η (lt_dsp β) :=
    Mkfxd (Mkfxr (λ γ, fxds _ (unsquash (ds_in_dsp γ)) (MkDS (squash (reflexivity _)))) _) _.
  Next Obligation.
    intros ??? β Hβ ?; revert Hβ; simpl in *.
    intros Hβα γ' γ Hγ'γ.
    rewrite -(@fxr_map_commutes _ _ (fxds γ (unsquash (ds_in_dsp γ)))
      (MkDS (le_dsp γ) (squash Hγ'γ)) (MkDS (squash (reflexivity _))) Hγ'γ).
    apply fx_data_agree.
    etrans; first done.
    etrans; first apply index_lt_le_subrel, (unsquash (ds_in_dsp γ)); done.
  Qed.
  Next Obligation.
    intros ??? β Hβ fxds γ Hγid Hγle.
    rewrite -(fx_raw_compat_equiv X η (fxds γ Hγid) _ (reflexivity _)).
    { apply (fxd_compat (fxds γ Hγid) (β := γ) (reflexivity _) Hγle). }
    simpl; intros γ' Hγ'1 Hγ'2; apply fx_data_agree.
    etrans; done.
  Qed.
  Fail Next Obligation.

  Program Definition fx_data_lim' (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X) {β : limit_idx SI} (Hβ : β ⪯ α)
    (fxd : fx_data X η (lt_dsp β)) : fx_data X η (le_dsp β) :=
    Mkfxd (Mkfxr
      (λ δ, match index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp δ)) return X ₒ (δ : SI) with
            | left Hlt => fxd (MkDS (lt_dsp β) (squash Hlt))
            | right Heq => psh_conv X (eq_sym Heq) (fx_raw_lim X η Hβ fxd)
            end) _) _.
  Next Obligation.
    intros ??? β ?? γ γ' Hγγ'; simpl.
    destruct (index_le_lt_eq_dec γ) as [Hltγ|Heqγ];
      destruct (index_le_lt_eq_dec γ') as [Hltγ'|Heqγ'].
    - rewrite -(@fxr_map_commutes _ _ fxd
        (MkDS (lt_dsp _) (squash Hltγ)) (MkDS (lt_dsp _) (squash Hltγ'))) //.
    - rewrite psh_conv_hom_action.
      replace (le_conv_r (eq_sym (eq_sym Heqγ')) Hγγ') with
        (index_lt_le_subrel _ _ Hltγ) by apply proof_irrel.
      rewrite fx_data_lim_back //.
    - exfalso.
      apply (index_le_lt_contradict γ γ'); [done|rewrite Heqγ //].
    - rewrite psh_conv_hom_action psh_conv_sym.
      rewrite psh_conv_hom_action'.
      match goal with
        |- context [_ ₕ ?A] =>
          replace A with (reflexivity (β : SI)) by apply proof_irrel
      end.
      rewrite h_map_id //.
  Qed.
  Next Obligation.
    intros ??? β ?? γ Hγid Hγα; simpl.
    destruct (index_le_lt_eq_dec _ _ Hγid) as [Hlt|Heq].
    - pose proof (fxd_compat fxd Hlt Hγα) as Hcmp.
      rewrite (fx_raw_compat_equiv X η fxd _ Hlt Hγid Hγα) in Hcmp; first exact Hcmp.
      intros γ' Hγ'id Hsγγ'; rewrite /=; destruct index_le_lt_eq_dec as [|Heq];
        first reflexivity.
      exfalso; apply (index_lt_irrefl γ'); rewrite {2}Heq //.
    - subst.
      simpl_index_rect; rewrite /fx_raw_compat_lim /=.
      destruct index_le_lt_eq_dec as [|Heq].
      { exfalso; eapply index_lt_irrefl; eassumption. }
      replace Heq with (eq_refl (β : SI)) by apply proof_irrel.
      simpl.
      apply fx_raw_lim_ext'; first done.
      intros ??; simpl.
      destruct index_le_lt_eq_dec as [|Heq']; first reflexivity.
      exfalso; eapply (index_lt_irrefl γ); rewrite {2}Heq' //.
  Qed.
  Fail Next Obligation.

  Definition fx_data_lim (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X) {β : limit_idx SI} (Hβ : β ⪯ α)
    (fxds : ∀ γ, γ ≺ β → γ ⪯ α → fx_data X η (le_dsp γ)) : fx_data X η (le_dsp β) :=
    fx_data_lim' X η Hβ
      (fx_data_glue X η Hβ
         (λ γ Hγ, fxds γ Hγ (transitivity (index_lt_le_subrel _ _ Hγ) Hβ))).

  Program Definition make_fx_data (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X) :
    index_rect (λ β, β ⪯ α → fx_data X η (le_dsp β)) :=
    MkIR
      (λ _, fx_data_zero X η)
      (λ _ f Hle, fx_data_succ X η Hle (f (index_succ_le _ _ Hle)))
      (λ _ f Hle, fx_data_lim X η Hle f)
      _.
  Next Obligation.
    split.
    - intros β Hβ1 Hβ2 ?; simpl.
      destruct β as [β Hβ2' Hβ1']; simpl in *.
      replace Hβ1 with Hβ1' by apply proof_irrel.
      replace Hβ2 with Hβ2' by apply proof_irrelevance.
      reflexivity.
    - intros β f g Hfg; simpl.
      destruct β as [β Hβ2' Hβ1']; simpl in *.
      extensionality Hle.
      rewrite /fx_data_lim /=.
      repeat f_equal.
      extensionality γ; extensionality Hγ; rewrite Hfg //.
  Qed.

  Lemma make_fx_data_ext (X : PreSheaf (OrdCat SI))
    {α} (η : natural (yoneda ₒ α ×ₒ (later ₒ X)) X)
    {α'} (η' : natural (yoneda ₒ α' ×ₒ (later ₒ X)) X)
    β Hβα Hβα' γ :
    (∀ δ, δ ⪯ β → ∀ Hle Hle' x, (η ₙ δ) (Hle, x) = (η' ₙ δ) (Hle', x)) →
    make_fx_data X η β Hβα γ = make_fx_data X η' β Hβα' γ.
  Proof.
    revert Hβα Hβα' γ.
    induction β as [|β IHβ|β IHβ] using index_ind;
      intros Hβα Hβα' γ Hηη'.
    - simpl_index_rect; rewrite /fx_data_zero /=.
      f_equiv.
      erewrite fx_raw_zero_ext; first done.
      apply Hηη'; done.
    - simpl_index_rect; rewrite /fx_data_succ /=.
      destruct le_succ_dec.
      + erewrite IHβ; first done.
        intros; apply Hηη'.
        apply index_lt_le_subrel, index_succ_iff; done.
      + f_equiv.
        erewrite fx_raw_succ_ext; [done|apply Hηη'; done|].
        erewrite IHβ; first done.
        intros; apply Hηη'.
        apply index_lt_le_subrel, index_succ_iff; done.
    - simpl_index_rect; rewrite /fx_data_lim /=.
      destruct index_le_lt_eq_dec.
      + erewrite IHβ; [done|done|].
        intros; apply Hηη';
          by etrans; last by apply index_lt_le_subrel.
      + f_equiv.
        apply fx_raw_lim_ext; simpl; first by apply Hηη'.
        repeat intros ?; erewrite IHβ; [done|done|].
        intros; apply Hηη';
          by etrans; last by apply index_lt_le_subrel.
  Qed.

  Lemma make_fx_data_ext' (X : PreSheaf (OrdCat SI)) {α}
    (η η' : natural (yoneda ₒ α ×ₒ later_func X) X) β Hle γ :
    (∀ δ, δ ⪯ β → η ₙ δ = η' ₙ δ) →
    make_fx_data X η β Hle γ = make_fx_data X η' β Hle γ.
  Proof.
    intros Heq; apply make_fx_data_ext;
      intros ?????; erewrite Heq; [f_equiv|]; last done.
    f_equiv; simpl; apply proof_irrelevance.
  Qed.

  Lemma make_fx_data_stable (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X) β Hle β' Hle' {γ} (Hγ : γ ⪯ β) (Hγ' : γ ⪯ β')
    (Hβ'β : β' ⪯ β) :
    make_fx_data X η β Hle (MkDS (le_dsp _) (squash Hγ)) = make_fx_data X η β' Hle' (MkDS (le_dsp _) (squash Hγ')).
  Proof.
    revert Hle β' Hβ'β Hle' γ Hγ Hγ'.
    induction (index_lt_wf _ β) as [β _ IHβ].
    specialize (λ z β' Hlt Hle , IHβ z Hlt Hle β').
    intros Hle β' Hβ'β Hle' γ Hγ Hγ'.
    destruct (index_le_lt_eq_dec _ _ Hβ'β) as [Hβ'ltβ| ->]; last first.
    { replace Hγ with Hγ' by apply proof_irrel.
      replace Hle with Hle' by apply proof_irrel.
      apply make_fx_data_ext'; done. }
    destruct (index_is_zero β) as [->| Hnz].
    { exfalso; eapply index_lt_zero_is_normal; done. }
    destruct (index_dec_limit β) as [[δ ->]|Hil].
    - simpl_index_rect; rewrite /fx_data_succ /=.
      destruct le_succ_dec as [Hγ'2| ->]; simpl.
      + rewrite (IHβ δ β'); [done|by apply index_succ_greater|].
        by apply index_succ_iff_proj_r2l.
      + by exfalso; eapply (index_lt_le_contradict β' (succ δ)).
    - change β with (mklimitidx β Hil Hnz : SI).
      simpl_index_rect; rewrite /fx_data_lim /=.
      destruct index_le_lt_eq_dec as [| ->].
      + erewrite (IHβ β' γ); done.
      + by exfalso; apply (index_lt_le_contradict β' β).
  Qed.

  Lemma make_fx_data_stable' (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X) β Hle (γ : downset (le_dsp β)):
    make_fx_data X η β Hle γ =
    make_fx_data X η γ (transitivity (unsquash (ds_in_dsp γ)) Hle) (MkDS (le_dsp _) (squash (reflexivity _))).
  Proof.
    destruct γ as [γ Hγ].
    rewrite -(make_fx_data_stable _ _ β _ γ _ (unsquash Hγ)) /=; first reflexivity. apply (unsquash Hγ).
  Qed.

  Lemma make_fx_data_natural (X : PreSheaf (OrdCat SI)) {α}
    (η : natural (yoneda ₒ α ×ₒ later_func X) X) β (Hβα : β ⪯ α) γ (Hγβ : γ ⪯ β) δ (Hδγ : δ ⪯ γ) :
    make_fx_data X η β Hβα (MkDS (le_dsp _) (squash (transitivity Hδγ Hγβ))) =
    (X ₕ Hδγ) (make_fx_data X η β Hβα (MkDS (le_dsp _) (squash Hγβ))).
  Proof.
    revert γ Hγβ δ Hδγ.
    induction (index_lt_wf _ β) as [β _ IHβ].
    specialize (λ z γ δ Hlt Hzα Hγz, IHβ z Hlt Hzα γ Hγz δ).
    intros γ Hγβ δ Hδγ.
    destruct (index_le_lt_eq_dec _ _ Hγβ) as [Hβ'ltβ| ->].
    { rewrite !(make_fx_data_stable' _ _ β) /=.
      rewrite -IHβ; last done.
      rewrite (make_fx_data_stable' _ _ γ) /=.
      erewrite make_fx_data_ext; first done.
      intros; f_equiv.
      f_equiv; simpl; apply proof_irrelevance.
    }
    destruct (index_is_zero β) as [->| Hnz].
    { assert (δ = zero) as -> by by apply le_zero_zero.
      replace Hδγ with (reflexivity (zero : SI))
        by by apply proof_irrel.
      rewrite h_map_id /=. reflexivity. }
    destruct (index_dec_limit β) as [[γ ->]|Hil].
    - simpl_index_rect; rewrite /fx_data_succ /=.
      destruct le_succ_dec as [Hγ'2| ->]; simpl.
      + destruct le_succ_dec.
        { exfalso; eapply index_le_lt_contradict;
            [done|by apply index_succ_greater]. }
        rewrite psh_conv_hom_action.
        replace (le_conv_r (eq_sym (eq_sym e)) Hδγ) with
          (transitivity Hγ'2 (index_lt_le_subrel _ _ (index_succ_greater γ)))
          by by apply proof_irrel.
        rewrite h_map_comp /=.
        rewrite (fx_data_succ_back _ _ _ (MkDS (squash (reflexivity γ)))).
        rewrite -IHβ; last apply index_succ_greater.
        reflexivity.
      + destruct le_succ_dec as [|Heq].
        { exfalso; eapply index_le_lt_contradict;
            [done|by apply index_succ_greater]. }
        replace Hδγ with (reflexivity (succ γ))
          by by apply proof_irrel.
        rewrite h_map_id /=.
        replace Heq with (eq_refl (succ γ))
          by apply proof_irrel.
        done.
    - change β with (mklimitidx β Hil Hnz : SI).
      simpl_index_rect; simpl.
      destruct index_le_lt_eq_dec as [Hlt| ->].
      + destruct index_le_lt_eq_dec as [|Heq].
        { exfalso; eapply index_lt_irrefl; done. }
        replace Heq with (eq_refl β) by apply proof_irrel.
        replace Hδγ with (index_lt_le_subrel _ _ Hlt)
          by by apply proof_irrel.
        rewrite (fx_data_lim_back X η
          (β := mklimitidx β Hil Hnz) Hβα (fx_data_glue X η Hβα
               (λ (γ : SI) (Hγ : γ ≺ β),
                 make_fx_data X η γ
                   (transitivity (index_lt_le_subrel γ β Hγ) Hβα))) Hlt).
        done.
      + destruct index_le_lt_eq_dec as [|Heq].
        { exfalso; eapply index_lt_irrefl; done. }
        replace Heq with (eq_refl β) by apply proof_irrel.
        simpl.
        replace Hδγ with (reflexivity β) by by apply proof_irrel.
        rewrite h_map_id; done.
        Qed.

  Program Definition fixpoint_combinator (X : PreSheaf (OrdCat SI)) : natural (X ↑ₒ (later ₒ X)) X :=
    MkNat (λ α, λ η, make_fx_data X η α (reflexivity α) (MkDS (squash (reflexivity α)))) _.
  Next Obligation.
    intros ? β γ Hγβ.
    extensionality η; simpl in *.
    rewrite -make_fx_data_natural.
    rewrite (make_fx_data_stable X η β (reflexivity _) γ Hγβ); last done; first done.
    erewrite make_fx_data_ext; first done.
    repeat intros ?; simpl; do 2 f_equiv; simpl; apply proof_irrelevance.
  Qed.

  Definition fixpoint {X Y : PreSheaf (OrdCat SI)} (η : natural ((later ₒ X) ×ₒ Y) X) : natural Y X :=
    (fixpoint_combinator X ∘ (transpose η)).

  Definition fixpoint_seed (X : PreSheaf (OrdCat SI)) : (later ₒ X) ₒ zero :=
    typ_conv (eq_sym (later_func_o_map_zero X)) ().

  Lemma fixpoint_zero {X Y : PreSheaf (OrdCat SI)} (η : natural ((later ₒ X) ×ₒ Y) X)
    (y : Y ₒ zero) :
    (fixpoint η ₙ zero) y = (η ₙ zero) (fixpoint_seed X, y).
  Proof.
    simpl; simpl_index_rect; simpl.
    rewrite /fx_data_zero /fx_raw_zero /=.
    replace (le_zero_zero zero (unsquash (squash (reflexivity zero)))) with (eq_refl (zero : SI))
        by apply proof_irrel.
    rewrite /=.
    do 2 f_equiv; first done.
    simpl.
    { replace (index_zero_minimum zero) with (reflexivity (zero: SI))
          by apply proof_irrel.
      rewrite h_map_id //. }
  Qed.

  Lemma fixpoint_succ {X Y : PreSheaf (OrdCat SI)} (η : natural ((later ₒ X) ×ₒ Y) X) α y :
    ((fixpoint η) ₙ (succ α)) y =
      (η ₙ (succ α))
       (typ_conv (eq_sym (later_func_o_map_succ X α))
          ((fixpoint η ₙ α) ((Y ₕ (index_lt_le_subrel _ _ (index_succ_greater α))) y)), y).
  Proof.
    simpl; simpl_index_rect; simpl.
    rewrite /fx_data_succ /fx_raw_succ /=.
    destruct le_succ_dec as [Hle| Heq].
    { exfalso; eapply index_lt_le_contradict; [apply index_succ_greater|apply Hle]. }
    replace Heq with (eq_refl (succ α)) by apply proof_irrel.
    rewrite /=.
    f_equiv; simpl.
    f_equiv; last by rewrite h_map_id.
    f_equiv.
    erewrite make_fx_data_ext; first done.
    intros ? Hle Hle' Hle'' ?; simpl in *.
    replace Hle' with (transitivity Hle'' (index_lt_le_subrel α (succ α) (index_succ_greater α)))
      by apply proof_irrel.
    rewrite h_map_comp; done.
  Qed.

  Program Definition fixpoint_lim_cone {X Y : PreSheaf (OrdCat SI)} (η : natural ((later ₒ X) ×ₒ Y) X)
    {α : SI} (y : Y ₒ (α : SI)) : cone (lift_func (lt_dsp α) X) :=
    MkCone unit
      (λ j, λ _, (fixpoint η ₙ (j : SI)) ((Y ₕ (index_lt_le_subrel _ _ (unsquash (ds_in_dsp j)))) y))
      _.
  Next Obligation.
    intros ??????? h.
    extensionality x; destruct x; simpl in *.
    rewrite -make_fx_data_natural.
    rewrite (make_fx_data_stable _ _ _ _ _ h _ (reflexivity _) h).
    erewrite make_fx_data_ext; first done.
    intros ?????; simpl.
    repeat f_equiv; rewrite -!psh_h_map_comp; repeat f_equiv.
    simpl; apply proof_irrelevance.
  Qed.

  Lemma fixpoint_lim {X Y : PreSheaf (OrdCat SI)} (η : natural ((later ₒ X) ×ₒ Y) X)
    (α : limit_idx SI) (y : Y ₒ (α : SI)) :
    ((fixpoint η) ₙ (α : SI)) y =
      (η ₙ (α : SI))
      (typ_conv (eq_sym (later_func_o_map_lim X α))
        (cone_hom_map
           (bang (term_is_terminal (complete (lift_func (lt_dsp α) X)))
              (fixpoint_lim_cone η y)) ()), y).
  Proof.
    simpl; simpl_index_rect; simpl.
    rewrite /fx_data_lim /= /fx_raw_lim /=.
    destruct index_le_lt_eq_dec as [Hlt| Heq].
    { exfalso; eapply index_lt_irrefl; done. }
    replace Heq with (eq_refl (α : SI)) by apply proof_irrel.
    rewrite /=.
    do 2 f_equiv; last by rewrite h_map_id.
    f_equiv.
    eta_expand_equation () of type unit.
    apply (hom_to_limit_unique _ _ _
                   (limiting_cone_is_limit
                      (term_is_terminal (complete (lift_func (lt_dsp α) X))))
                   (cone_is_cone (fixpoint_lim_cone η y))).
    - intros ?; simpl.
      extensionality x; destruct x; simpl.
      rewrite ic_side_limiting_cone_is_limit.
      rewrite_cone_hom_commutes_back; simpl.
      erewrite make_fx_data_ext; first done.
      repeat intros ?; simpl; repeat f_equiv.
      rewrite -psh_h_map_comp; repeat f_equiv; apply proof_irrel.
    - intros ?.
      extensionality x; simpl.
      rewrite ic_side_limiting_cone_is_limit.
      rewrite_cone_hom_commutes_back; simpl.
      reflexivity.
  Qed.

  Global Opaque fixpoint.

  Lemma fixpoint_unfold {X Y : PreSheaf (OrdCat SI)} (η : natural ((later ₒ X) ×ₒ Y) X) :
    fixpoint η = η ∘ << next ₙ X ∘@{PSh (OrdCat SI)} fixpoint η, @id (PSh (OrdCat SI)) Y>>.
  Proof.
    apply natural_equiv_unpack; intros α.
    extensionality y.
    induction α as [|α IHα|α IHα] using index_ind.
    - rewrite /= fixpoint_zero.
      do 2 f_equiv.
      simpl.
      unfold fixpoint_seed.
      simpl.
      apply typ_conv_sym.
      apply unit_pi.
    - rewrite /= !fixpoint_succ.
      do 2 f_equiv.
      rewrite later_func_o_map_is_limit_succ.
      rewrite bang_of_is_limit_trans.
      rewrite hom_trans_typ_conv' /=.
      f_equiv.
      rewrite -(psh_naturality η) /=.
      rewrite {1}IHα /=.
      f_equiv.
      unfold hom_prod; simpl; f_equiv;
        last (f_equiv; simpl; apply proof_irrelevance).
      eta_expand_equation ((fixpoint η ₙ α)
                             ((Y ₕ index_lt_le_subrel _ _ (index_succ_greater α)) y)).
      apply (hom_to_limit_unique _ _ _
               (later_func_o_map_is_limit X α)
               (cone_is_cone (extend_cone
                 (cone_of_is_cone (il_is_cone (later_func_o_map_is_limit X α)))
                 ((next ₙ X) ₙ α)))).
      + intros ?; done.
      + intros ?; rewrite /=.
        extensionality x.
        repeat (rewrite_cone_hom_commutes_back; simpl).
        rewrite later_func_o_map_is_limit_succ.
        rewrite trans_side_of_is_limit_trans.
        rewrite hom_trans_typ_conv' /=.
        rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
        repeat f_equiv; apply proof_irrel.
    - rewrite /=.
      rewrite ->fixpoint_lim at 1.
      do 2 f_equal.
      rewrite later_func_o_map_is_limit_lim.
      rewrite bang_of_is_limit_trans.
      rewrite hom_trans_typ_conv' /=.
      f_equal.
      eta_expand_equation () of type unit.
      apply (hom_to_limit_unique _ _ _
               (limiting_cone_is_limit
                  (term_is_terminal (complete (lift_func (lt_dsp α) X))))
               (cone_is_cone (@fixpoint_lim_cone _ _ η α y))).
      + intros ?; done.
      + intros β; rewrite /=.
        extensionality x.
        rewrite_cone_hom_commutes_back; simpl.
        rewrite -psh_naturality.
        repeat f_equal; apply proof_irrel.
  Qed.

  Lemma fixpoint_unique' {X Y : PreSheaf (OrdCat SI)} (η : natural ((later ₒ X) ×ₒ Y) X)
    (FX : natural Y X) :
    FX = η ∘ << next ₙ X ∘@{PSh (OrdCat SI)} FX, @id (PSh (OrdCat SI)) Y>> →
    FX = fixpoint η.
  Proof.
    intros HFX.
    apply natural_equiv_unpack; intros α.
    extensionality y.
    induction α as [|α IHα|α IHα] using index_ind.
    - rewrite /= fixpoint_zero HFX /=.
      rewrite /fixpoint_seed.
      f_equal; simpl.
      f_equal; simpl.
      apply typ_conv_sym.
      apply proof_irrel.
    - rewrite /= fixpoint_succ HFX /= -IHα.
      do 2 f_equal.
      rewrite psh_naturality.
      eta_expand_equation ((FX ₙ (succ α)) y).
      apply (hom_to_limit_unique _ _ _
               (later_func_o_map_is_limit X (succ α))
               (cone_is_cone
                  (cone_at X (succ α) (lt_dsp (succ α))
                     (in_lt_dsp_le (reflexivity (succ α)))))).
      + intros ?.
        extensionality x; simpl.
        rewrite_cone_hom_commutes_back; simpl.
        repeat f_equiv; apply proof_irrel.
      + intros ?.
        extensionality x; simpl.
        rewrite later_func_o_map_is_limit_succ.
        rewrite trans_side_of_is_limit_trans.
        rewrite hom_trans_typ_conv' /=.
        rewrite -typ_conv_trans eq_trans_sym_inv_r /=.
        rewrite -psh_h_map_comp /=.
        repeat f_equiv; apply proof_irrel.
    - rewrite fixpoint_lim HFX /=.
      do 2 f_equal.
      rewrite later_func_o_map_is_limit_lim.
      rewrite bang_of_is_limit_trans.
      rewrite hom_trans_typ_conv' /=.
      f_equal.
      eta_expand_equation () of type unit.
      apply (hom_to_limit_unique _ _ _
               (limiting_cone_is_limit
                  (term_is_terminal (complete (lift_func (lt_dsp α) X))))
               (cone_is_cone (@fixpoint_lim_cone _ _ η _ y))).
      + intros β; simpl.
        rewrite_cone_hom_commutes_back; simpl.
        rewrite -psh_naturality.
        rewrite IHα; last apply (unsquash (ds_in_dsp β)).
        extensionality x; simpl.
        repeat f_equal; apply proof_irrel.
      + intros β; rewrite /=.
        extensionality x.
        rewrite ic_side_limiting_cone_is_limit.
        rewrite_cone_hom_commutes_back; simpl; done.
  Qed.

  Lemma fixpoint_unique {X Y : PreSheaf (OrdCat SI)} (η : natural ((later ₒ X) ×ₒ Y) X)
    (FX FX' : natural Y X) :
    FX = η ∘ << next ₙ X ∘@{PSh (OrdCat SI)} FX, @id (PSh (OrdCat SI)) Y>> →
    FX' = η ∘ << next ₙ X ∘@{PSh (OrdCat SI)} FX', @id (PSh (OrdCat SI)) Y>> →
    FX = FX'.
  Proof.
    intros ? ?; erewrite (fixpoint_unique' _ FX); last done.
    erewrite (fixpoint_unique' _ FX'); last done.
    reflexivity.
  Qed.

  Definition contr_fix {X : PreSheaf (OrdCat SI)} (η : natural X X) `{!Contractive η} :
    natural (1ₒ) X := fixpoint (contr_hom η ∘ prj1 (product_of (later ₒ X) (1ₒ))).

  Lemma contr_fix_unfold {X : PreSheaf (OrdCat SI)} (η : natural X X) `{!Contractive η} :
    η ∘@{PSh _} contr_fix η = contr_fix η.
  Proof.
    rewrite {2}(contr_hom_after_next η) /contr_fix.
    remember (contr_hom η ∘ prj1 (product_of (later ₒ X) (1ₒ))) as f.
    rewrite {2}fixpoint_unfold.
    rewrite {3}Heqf !comp_assoc hom_to_prod_prj1 //.
  Qed.

  Lemma contr_fix_unique {X : PreSheaf (OrdCat SI)} (η : natural X X) `{!Contractive η}
    (f1 f2 : natural (1ₒ) X) :
    η ∘@{PSh _} f1 = f1 →
    η ∘@{PSh _} f2 = f2 →
    f1 = f2.
  Proof.
    intros ??.
    eapply (fixpoint_unique (contr_hom η ∘ prj1 (product_of (later ₒ X) (1ₒ)))).
    - rewrite comp_assoc hom_to_prod_prj1 -comp_assoc -(contr_hom_after_next η) //.
    - rewrite comp_assoc hom_to_prod_prj1 -comp_assoc -(contr_hom_after_next η) //.
  Qed.

End fixpoint.
