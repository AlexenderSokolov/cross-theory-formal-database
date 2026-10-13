From SynthDom Require Import prelude.
From SynthDom Require Import stepindex.
From SynthDom.categories Require Import category coprod
  ord_cat enriched domain solution.

Set Universe Polymorphism.
Unset Universe Minimization ToSet.

Declare Scope contractive_scope.
Delimit Scope contractive_scope with contractive.

Local Open Scope contractive_scope.

Section functor_diag.
  Context {SI : indexT}.
  Context {C : category}.
  Context `{!Enriched C (PSh (OrdCat SI))}.
  Local Instance : Enriched (cat_prod C C) (PSh (OrdCat SI)) := prod_enriched_def.

  Program Definition functor_diag_enr_def (a b : obj C)
    : natural (enr_hom a b) (enr_hom (functor_diag ₒ a) (functor_diag ₒ b))
    := MkNat (λ x, λ f, (f, f)) _.
  Next Obligation.
    repeat intros ?; solve_by_eq_rewrite.
  Qed.
  Fail Next Obligation.

  Local Program Instance functor_diag_enr : EnrichedFunctor (@functor_diag C)
    := MkEnrFunc (λ a b, functor_diag_enr_def a b) _ _ _.
  Next Obligation.
    intros; simpl.
    rewrite enr_project_embed.
    apply natural_equiv_unpack.
    intros ?; simpl.
    extensionality x; simpl.
    solve_by_eq_rewrite.
  Qed.
  Next Obligation.
    intros; simpl.
    apply natural_equiv_unpack.
    intros ?.
    extensionality x; destruct x; simpl.
    reflexivity.
  Qed.
  Next Obligation.
    intros; simpl.
    apply natural_equiv_unpack.
    intros ?.
    extensionality x; simpl.
    reflexivity.
  Qed.
  Fail Next Obligation.
End functor_diag.

Section functor_prod.
  Context {SI : indexT}.
  Context {C C' D D' : category}.
  Context `{!Enriched C (PSh (OrdCat SI))} `{!Enriched D (PSh (OrdCat SI))}
    `{!Enriched C' (PSh (OrdCat SI))} `{!Enriched D' (PSh (OrdCat SI))}.
  Local Instance : Enriched (cat_prod C D) (PSh (OrdCat SI)) := prod_enriched_def.
  Local Instance : Enriched (cat_prod C' D') (PSh (OrdCat SI)) := prod_enriched_def.
  Context (f : functor C C').
  Context (g : functor D D').
  Context `{!LocallyContractiveFunctor f}.
  Context `{!LocallyContractiveFunctor g}.

  Local Opaque next later.

  Program Definition functor_prod_enr_def (a b : obj (cat_prod C D))
    : natural (enr_hom a b) (enr_hom (f ₒ a.1, g ₒ a.2) (f ₒ b.1, g ₒ b.2))
    := MkNat (λ x, λ h, (((enr_func_h_map f a.1 b.1 ₙ x) h.1),
                             ((enr_func_h_map g a.2 b.2 ₙ x) h.2)))
         _.
  Next Obligation.
    intros ?????.
    extensionality x.
    rewrite /= !psh_naturality //.
  Qed.
  Fail Next Obligation.

  Local Program Instance functor_prod_enr : EnrichedFunctor (functor_prod f g)
    := MkEnrFunc (λ a b, functor_prod_enr_def a b) _ _ _.
  Next Obligation.
    intros; simpl.
    apply natural_equiv_unpack.
    intros ?; simpl.
    rewrite !enr_func_h_map_is_h_map /=.
    reflexivity.
  Qed.
  Next Obligation.
    intros a b c; simpl.
    apply natural_equiv_unpack.
    intros d.
    extensionality y; simpl.

    pose proof (equal_f (natural_equiv_pack (enr_func_h_map_comp f a.1 b.1 c.1) d)
                  (y.1.1, y.2.1)) as H.
    simpl in H.
    rewrite H; clear H.
    pose proof (equal_f (natural_equiv_pack (enr_func_h_map_comp g a.2 b.2 c.2) d)
                  (y.1.2, y.2.2)) as H.
    simpl in H.
    rewrite H; clear H.
    reflexivity.
  Qed.
  Next Obligation.
    intros a; simpl.
    apply natural_equiv_unpack.
    intros b.
    extensionality y; simpl.
    pose proof (equal_f (natural_equiv_pack (enr_func_h_map_id f a.1) b) y) as H.
    simpl in H.
    rewrite H; clear H.
    pose proof (equal_f (natural_equiv_pack (enr_func_h_map_id g a.2) b) y) as H.
    simpl in H.
    rewrite H; clear H.
    reflexivity.
  Qed.
  Fail Next Obligation.

  Program Definition func_prod_lc_def
    (a b : obj (cat_prod C D))
    : natural (later_func (enr_hom a.1 b.1 ×ₒ@{PSh (OrdCat SI)} enr_hom a.2 b.2))
        (enr_hom (f ₒ a.1) (f ₒ b.1) ×ₒ enr_hom (g ₒ a.2) (g ₒ b.2))
    := MkNat (λ x,
           λ h,
           ((((contr_func_h_map f a.1 b.1) ₙ x)
               ((forward (later_prod (enr_hom a.1 b.1) (enr_hom a.2 b.2)) ₙ x) h).1)
             , (((contr_func_h_map g a.2 b.2) ₙ x)
                  ((forward (later_prod (enr_hom a.1 b.1) (enr_hom a.2 b.2)) ₙ x) h).2))) _.
  Next Obligation.
    intros ???? j; simpl.
    extensionality y; simpl.
    pose proof (psh_naturality (contr_func_h_map f a.1 b.1) _ _ j) as H.
    simpl in H.
    unfold hom_prod; simpl.
    rewrite -H; clear H.
    pose proof (psh_naturality (contr_func_h_map g a.2 b.2) _ _ j) as H.
    simpl in H.
    rewrite -H; clear H.
    f_equiv.
    - f_equiv.
      pose proof (equal_f (@naturality _ _ _ _
                    (forward (later_preserves_prods_nat SI)ₙ
                       (enr_hom a.1 b.1, enr_hom a.2 b.2)) _ _ j) y) as Hn.
      simpl in Hn.
      rewrite Hn; clear Hn.
      reflexivity.
    - f_equiv.
      pose proof (equal_f (@naturality _ _ _ _
                    (forward (later_preserves_prods_nat SI)ₙ
                       (enr_hom a.1 b.1, enr_hom a.2 b.2)) _ _ j)
                    y) as Hn.
      simpl in Hn.
      rewrite Hn; clear Hn.
      reflexivity.
  Qed.
  Fail Next Obligation.

  Local Program Instance func_prod_lc
    : LocallyContractiveFunctor (functor_prod f g)
  := MkLocContrFunc (λ a b, func_prod_lc_def a b) _ _ _.
  Next Obligation.
    intros a b.
    apply natural_equiv_unpack.
    intros c.
    extensionality y; simpl.
    f_equiv.
    - rewrite (equal_f (natural_equiv_pack (contr_func_h_map_is_h_map f a.1 b.1) c) y.1) /=.
      f_equiv.
      rewrite {1}/later_preserves_prods_nat
        right_adj_preserves_prods_forward /=.
      symmetry.
      destruct y as [y1 y2]; simpl.
      match goal with
      | |- context G [next ₙ ?a]
        => set (T := a)
      end.
      match goal with
      | |- context G [later ₕ ?a]
        => set (T' := a)
      end.
      epose proof (equal_f (natural_equiv_pack (@naturality
                     (PSh (OrdCat SI))
                     (PSh (OrdCat SI))
                     (id_functor _)
                     (later)
                     next
                     T _ T') c) (y1, y2)) as H.
      simpl in H.
      rewrite -H; clear H.
      reflexivity.
    - rewrite (equal_f (natural_equiv_pack (contr_func_h_map_is_h_map g a.2 b.2) c) y.2)/=.
      f_equiv.
      rewrite {1}/later_preserves_prods_nat
        right_adj_preserves_prods_forward /=.
      symmetry.
      destruct y as [y1 y2]; simpl.
      match goal with
      | |- context G [next ₙ ?a]
        => set (T := a)
      end.
      match goal with
      | |- context G [later ₕ ?a]
        => set (T' := a)
      end.
      epose proof (equal_f (natural_equiv_pack (@naturality
                     (PSh (OrdCat SI))
                     (PSh (OrdCat SI))
                     (id_functor _)
                     (later)
                     next
                     T _ T') c)
                     (y1, y2)) as H.
      simpl in H.
      rewrite -H; clear H.
      reflexivity.
  Qed.
  Next Obligation.
    intros a b c.
    apply natural_equiv_unpack.
    intros d.
    extensionality e'.
    simpl.
    f_equiv.
    - destruct e' as [e1 e2]; simpl.
      match goal with
      | |- context G [backward ?a ₙ ?b]
        => set (T := a)
      end.
      simpl in *.
      pose proof (equal_f (natural_equiv_pack (contr_func_h_map_comp f a.1 b.1 c.1) d)
                    (((((forward T ₙ (enr_hom a.1 b.1, enr_hom a.2 b.2))ₙ d) e1).1),
                      ((((forward T ₙ (enr_hom b.1 c.1, enr_hom b.2 c.2))ₙ d) e2).1))) as H.
      simpl in H.
      rewrite -H; clear H.
      f_equiv.
      rewrite {1}/later_preserves_prods_nat
        right_adj_preserves_prods_forward /=.
      match goal with
      | |- context G [later ₕ ?a]
        => set (T' := a)
      end.
      match goal with
      | |- context G [((later ₕ T')ₙ d)
                       (((later ₕ ?a ₙ _)) _)]
        => set (T'' := a)
      end.
      simpl in *.
      pose proof (equal_f (natural_equiv_pack (h_map_comp _ _ later _ _ _ T'' T') d)
                    (((backward T ₙ (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2,
                           enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2))ₙ d) (
                         e1, e2))) as H.
      simpl in H.
      rewrite -H; clear H.
      subst T'' T'.
      match goal with
      | |- context G [<< ?a, ?b >>]
        => set (Q1 := a); set (Q2 := b)
      end.
      pose proof (hom_to_prod_prj1 Q1 Q2) as H.
      simpl in H.
      rewrite H; clear H.
      subst Q1.
      clear Q2.
      subst T; simpl.
      rewrite /later_preserves_prods_nat.
      match goal with
      | |- context G [backward ?a]
        => set (T' := a)
      end.
      rewrite h_map_comp /=.
      f_equiv.
      epose proof (equal_f
                     (natural_equiv_pack
                        (@naturality _ _ _ _ (backward T')
                           (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2,
                             enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2)
                           (enr_hom a.1 b.1, enr_hom b.1 c.1)
                           (_, _)
                           )
                        d)
                     (e1, e2)) as Hn.
      simpl in Hn; rewrite ->Hn; clear Hn.
      done.
    - destruct e' as [e1 e2]; simpl.
      match goal with
      | |- context G [backward ?a ₙ ?b]
        => set (T := a)
      end.
      simpl in *.
      pose proof (equal_f (natural_equiv_pack (contr_func_h_map_comp g a.2 b.2 c.2) d)
                    (((((forward T ₙ (enr_hom a.1 b.1, enr_hom a.2 b.2))ₙ d) e1).2),
                      ((((forward T ₙ (enr_hom b.1 c.1, enr_hom b.2 c.2))ₙ d) e2).2))) as H.
      simpl in H.
      rewrite -H; clear H.
      f_equiv.
      rewrite {1}/later_preserves_prods_nat
        right_adj_preserves_prods_forward /=.
      match goal with
      | |- context G [later ₕ ?a]
        => set (T' := a)
      end.
      match goal with
      | |- context G [((later ₕ T')ₙ d)
                       (((later ₕ ?a ₙ _)) _)]
        => set (T'' := a)
      end.
      simpl in *.
      pose proof (equal_f (natural_equiv_pack (h_map_comp _ _ later _ _ _ T'' T') d)
                    (((backward T ₙ (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2,
                           enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2))ₙ d) (
                         e1, e2))) as H.
      simpl in H.
      rewrite -H; clear H.
      subst T'' T'.
      match goal with
      | |- context G [<< ?a, ?b >>]
        => set (Q1 := a); set (Q2 := b)
      end.
      pose proof (hom_to_prod_prj2 Q1 Q2) as H.
      simpl in H.
      rewrite H; clear H.
      subst Q2.
      clear Q1.
      subst T; simpl.
      rewrite /later_preserves_prods_nat.
      match goal with
      | |- context G [backward ?a]
        => set (T' := a)
      end.
      rewrite h_map_comp /=.
      f_equiv.
      epose proof (equal_f
                     (natural_equiv_pack
                        (@naturality _ _ _ _
                           (backward T')
                           (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2,
                             enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2)
                           (enr_hom a.2 b.2, enr_hom b.2 c.2)
                           (_, _)) d)
                     (e1, e2)) as Hn.
      simpl in Hn.
      rewrite <-Hn.
      done.
  Qed.
  Next Obligation.
    intros a.
    apply natural_equiv_unpack.
    intros c.
    extensionality e'.
    simpl.
    f_equiv.
    - rewrite -(equal_f (natural_equiv_pack (contr_func_h_map_id f a.1) c) e').
      simpl.
      f_equiv.
      rewrite {1}/later_preserves_prods_nat
        right_adj_preserves_prods_forward /=.
      set (T := func_prj1 _ _).
      set (T' := << _, _ >>).
      pose proof (equal_f
                     (natural_equiv_pack (h_map_comp _ _ later _ _ _ T' T) c)
                     (((next ₙ 1ₒ)ₙ c) e')) as H.
      simpl in H.
      rewrite -H; clear H.
      f_equal.
      subst T T'.
      pose proof (hom_to_prod_prj1 ⌜ id a.1 ⌝ ⌜ id a.2 ⌝) as H.
      simpl in H.
      rewrite H; clear H.
      reflexivity.
    - rewrite -(equal_f (natural_equiv_pack (contr_func_h_map_id g a.2) c) e').
      simpl.
      f_equiv.
      rewrite {1}/later_preserves_prods_nat
        right_adj_preserves_prods_forward /=.
      set (T := func_prj2 _ _).
      set (T' := << _, _ >>).
      pose proof (equal_f (natural_equiv_pack (h_map_comp _ _ later _ _ _ T' T) c) (((next ₙ 1ₒ)ₙ c) e'))
                    as H.
      simpl in H.
      rewrite -H; clear H.
      f_equal.
      subst T T'.
      pose proof (hom_to_prod_prj2 ⌜ id a.1 ⌝ ⌜ id a.2 ⌝) as H.
      simpl in H.
      rewrite H; clear H.
      reflexivity.
  Qed.
  Fail Next Obligation.

End functor_prod.

Section prod_func.
  Context {SI : indexT}.
  Local Instance : Enriched (PSh (OrdCat SI)) (PSh (OrdCat SI)) := @self_enriched _ _.
  Local Instance : Enriched (cat_prod (PSh (OrdCat SI)) (PSh (OrdCat SI)))
                     (PSh (OrdCat SI)) := prod_enriched_def.

  Program Definition prod_func_enr_def
    (a b : obj (cat_prod (PSh (OrdCat SI)) (PSh (OrdCat SI))))
    : natural (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2) (enr_hom (a.1 ×ₒ a.2) (b.1 ×ₒ b.2))
    := MkNat (λ x,
           λ f,
           MkNat (λ c,
               λ g,
               (((f.1 ₙ c) (g.1, g.2.1)), ((f.2 ₙ c) (g.1, g.2.2)))) _) _.
  Next Obligation.
    intros ??? M ?? F.
    extensionality y.
    simpl; unfold hom_prod; simpl.
    rewrite -(psh_naturality M.2 _ _ F) /=; f_equiv; last done.
    rewrite -(psh_naturality M.1 _ _ F) /=; f_equiv; done.
  Qed.
  Next Obligation.
    intros ?????.
    extensionality x; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality y; simpl.
    reflexivity.
  Qed.
  Fail Next Obligation.

  Local Program Instance prod_func_enr : EnrichedFunctor (prod_func _)
    := MkEnrFunc (λ a b, prod_func_enr_def a b) _ _ _.
  Next Obligation.
    intros a b f; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality x; destruct x; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality y; simpl.
    pose proof (equal_f (naturality f y.1) ()) as H.
    simpl in H.
    unfold hom_prod in H; simpl in H.
    rewrite H.
    apply injective_projections;
      simpl; do 2 f_equiv; apply proof_irrel.
  Qed.
  Next Obligation.
    intros a b c; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality x; destruct x; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality y; simpl.
    apply injective_projections;
      simpl; do 2 f_equiv; apply proof_irrel.
  Qed.
  Next Obligation.
    repeat intros ?; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality x; destruct x; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality y; simpl.
    destruct y as [? y]; simpl.
    destruct y; simpl.
    reflexivity.
  Qed.
  Fail Next Obligation.
End prod_func.

Section coprod_func.
  Context {SI : indexT}.
  Local Instance : Enriched (PSh (OrdCat SI)) (PSh (OrdCat SI)) := @self_enriched _ _.
  Local Instance : Enriched (cat_prod (PSh (OrdCat SI)) (PSh (OrdCat SI)))
                     (PSh (OrdCat SI)) := prod_enriched_def.

  Program Definition coprod_func_enr_def
    (a b : obj (cat_prod (PSh (OrdCat SI)) (PSh (OrdCat SI))))
    : natural (b.1 ↑ₒ a.1 ×ₒ (b.2 ↑ₒ a.2)) (b.1 +ₒ b.2 ↑ₒ (a.1 +ₒ a.2))
    := MkNat (λ x,
           λ f,
           MkNat (λ c,
               λ g,
               (sum_rect
                  (λ _, (b.1 ₒ c) +ₒ (b.2 ₒ c))
                  (λ g', inl ((f.1 ₙ c) (g.1, g')))
                  (λ g', inr ((f.2 ₙ c) (g.1, g'))) g.2)) _) _.
  Next Obligation.
    intros ??? M ?? F.
    extensionality y; simpl.
    unfold hom_coprod; simpl.
    destruct y as [o [g | g]]; simpl.
    - rewrite -(psh_naturality M.1 _ _ F (o, g)) /=.
      by do 2 f_equiv.
    - rewrite -(psh_naturality M.2 _ _ F (o, g)) /=.
      by do 2 f_equiv.
  Qed.
  Next Obligation.
    intros ?????.
    extensionality x; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality t; simpl.
    destruct t as [? [t | t]]; simpl.
    - by do 2 f_equiv.
    - by do 2 f_equiv.
  Qed.
  Fail Next Obligation.

  Local Program Instance coprod_func_enr : EnrichedFunctor (coprod_func _)
    := MkEnrFunc (λ a b, coprod_func_enr_def a b) _ _ _.
  Next Obligation.
    intros a b f; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality a'; destruct a'; simpl.
    apply natural_equiv_unpack; intros ?; simpl.
    extensionality y; simpl.
    destruct y as [y1 [t | t]]; simpl.
    - f_equiv.
      pose proof (equal_f (naturality f y1) ()) as H.
      simpl in H.
      rewrite H; clear H.
      unfold hom_prod; simpl.
      do 2 f_equiv.
      apply proof_irrel.
    - f_equiv.
      pose proof (equal_f (naturality f y1) ()) as H.
      simpl in H.
      rewrite H; clear H.
      unfold hom_prod; simpl.
      do 2 f_equiv.
      apply proof_irrel.
  Qed.
  Next Obligation.
    intros a b c; simpl.
    apply natural_equiv_unpack; intros d.
    extensionality y.
    apply natural_equiv_unpack; intros ?.
    extensionality y'; simpl.
    destruct y' as [? [y' | y']]; simpl; by f_equiv.
  Qed.
  Next Obligation.
    intros ?.
    apply natural_equiv_unpack; intros ?.
    extensionality x.
    apply natural_equiv_unpack; intros ?.
    extensionality t.
    simpl.
    destruct t as [? [t | t]]; simpl; by f_equiv.
  Qed.
  Fail Next Obligation.
End coprod_func.

Definition cod_func_prod {C D} `{!HasProducts D} (f g : functor C D)
  : functor C D
  := functor_compose
       functor_diag
       (functor_compose
          (functor_prod f g)
          (prod_func _)).

Infix "×ᵨ" := cod_func_prod (at level 40, left associativity)
    : contractive_scope.

Definition cod_func_sum {C D} `{!HasCoproducts D} (f g : functor C D)
  : functor C D
  := functor_compose
       functor_diag
       (functor_compose
          (functor_prod f g)
          (coprod_func _)).

Infix "+ᵨ" := cod_func_sum (at level 40, left associativity)
    : contractive_scope.

Definition func_lift {C D E} (f : functor D E)
  : functor (cat_prod C D) E
  := functor_compose (cat_proj2 _ _) f.

Notation "'↑ᵨ'" := func_lift (at level 40, no associativity)
    : contractive_scope.

Section cat_proj.
  Context {SI : indexT}.
  Context {C D : category}.
  Context `{!Enriched C (PSh (OrdCat SI))} `{!Enriched D (PSh (OrdCat SI))}.
  Local Instance : Enriched (cat_prod C D) (PSh (OrdCat SI)) := prod_enriched_def.

  Program Definition cat_proj2_enr_def (a b : obj (cat_prod C D))
    : natural (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2) (enr_hom a.2 b.2)
    := MkNat (λ x, λ f, f.2) _.
  Next Obligation.
    repeat intros ?; solve_by_eq_rewrite.
  Qed.
  Fail Next Obligation.

  Local Program Instance cat_proj2_enr : EnrichedFunctor (cat_proj2 C D)
    := MkEnrFunc (λ a b, cat_proj2_enr_def a b) _ _ _.
  Next Obligation.
    intros; simpl.
    rewrite enr_project_embed.
    apply natural_equiv_unpack; intros ?.
    extensionality x.
    simpl.
    solve_by_eq_rewrite.
  Qed.
  Next Obligation.
    intros; simpl.
    apply natural_equiv_unpack; intros ?.
    extensionality x.
    simpl.
    reflexivity.
  Qed.
  Next Obligation.
    intros; simpl.
    apply natural_equiv_unpack; intros ?.
    extensionality x.
    simpl.
    reflexivity.
  Qed.
  Fail Next Obligation.
End cat_proj.

Section func_lift.
  Context {SI : indexT}.
  Context {C D F : category}.
  Context `{!Enriched C (PSh (OrdCat SI))} `{!Enriched D (PSh (OrdCat SI))}
    `{!Enriched F (PSh (OrdCat SI))}.
  Local Instance : Enriched (cat_prod C D) (PSh (OrdCat SI)) := prod_enriched_def.
  Context (f : functor D F).
  Context `{!LocallyContractiveFunctor f}.

  Local Program Instance func_lift_enr : EnrichedFunctor (func_lift f)
    := @EnrichedFunctor_comp _ _ _ _ _ _ _ _ _
         (cat_proj2 _ _) f cat_proj2_enr contr_enriched.

  Local Program Instance func_lift_lc : LocallyContractiveFunctor (func_lift f)
    := (@LocallyContractiveFunctor_comp_r SI _ _ _ _ _ _
          f (cat_proj2 C D) _ cat_proj2_enr).
End func_lift.

Definition func_const {SI} {C} (c : obj (PSh (OrdCat SI)))
  : functor (cat_prod C (PSh (OrdCat SI))) (PSh (OrdCat SI))
  := ((const_functor c : hom (C := Cat) _ _)
        ∘ (!ₕ ((cat_prod C (PSh (OrdCat SI))) : obj Cat))).

Notation "'Δᵨ'" := func_const (at level 40, no associativity)
    : contractive_scope.

Section func_const.
  Context {SI : indexT}.
  Context {C : category} (c : obj (PSh (OrdCat SI))).
  Context `{!Enriched C (PSh (OrdCat SI))}.
  Local Instance : Enriched (PSh (OrdCat SI)) (PSh (OrdCat SI)) :=
    self_enriched (PSh (OrdCat SI)).
  Local Instance : Enriched (cat_prod C (PSh (OrdCat SI)))
                     (PSh (OrdCat SI)) := prod_enriched_def.

  Local Program Instance func_const_enr : EnrichedFunctor (func_const c)
    := MkEnrFunc (λ a b, (enr_embed (id _) ∘ !ₕ _)) _ _ _.
  Next Obligation.
    intros a b f.
    rewrite -{1}(right_id (⌜ id c ⌝)).
    rewrite comp_assoc.
    f_equiv; last done.
    rewrite (bang_unique (term_is_terminal _) (id (1ₒ))).
    rewrite (bang_unique (term_is_terminal _) ((!ₕ) (enr_hom a b) ∘ f)).
    reflexivity.
  Qed.
  Next Obligation.
    intros a b d.
    rewrite hom_prod_comp.
    unfold hom_prod.
    apply natural_equiv_unpack; intros ?.
    extensionality x.
    simpl.
    apply natural_equiv_unpack; intros ?.
    extensionality y.
    simpl.
    reflexivity.
  Qed.
  Next Obligation.
    intros a.
    cbn beta.
    rewrite comp_assoc.
    apply natural_equiv_unpack; intros ?.
    extensionality x.
    simpl.
    apply natural_equiv_unpack; intros ?.
    extensionality y.
    simpl.
    reflexivity.
  Qed.
  Fail Next Obligation.

  Program Definition func_const_lc_def (a b : obj (cat_prod C (PSh (OrdCat SI))))
    : natural (later_func (enr_hom a.1 b.1 ×ₒ (b.2 ↑ₒ a.2))) (c ↑ₒ c)
    := MkNat (λ x, λ f, MkNat (λ d, λ g, g.2) _) _.
  Next Obligation.
    repeat intros ?.
    solve_by_eq_rewrite.
  Qed.
  Next Obligation.
    repeat intros ?; simpl.
    extensionality x.
    apply natural_equiv_unpack; intros ?.
    extensionality y.
    simpl.
    reflexivity.
  Qed.
  Fail Next Obligation.

  Local Program Instance func_const_lc : LocallyContractiveFunctor (func_const c)
    := MkLocContrFunc (λ a b, func_const_lc_def a b) _ _ _.
  Next Obligation.
    repeat intros ?; simpl.
    apply natural_equiv_unpack; intros ?.
    extensionality x.
    simpl.
    apply natural_equiv_unpack; intros ?.
    extensionality y.
    simpl.
    reflexivity.
  Qed.
  Next Obligation.
    repeat intros ?; simpl.
    apply natural_equiv_unpack; intros ?.
    extensionality x.
    simpl.
    apply natural_equiv_unpack; intros ?.
    extensionality y.
    simpl.
    reflexivity.
  Qed.
  Next Obligation.
    repeat intros ?; simpl.
    apply natural_equiv_unpack; intros ?.
    extensionality x.
    simpl.
    apply natural_equiv_unpack; intros ?.
    extensionality y.
    simpl.
    reflexivity.
  Qed.
  Fail Next Obligation.
End func_const.

Section exp_func.
  Context {SI : indexT}.
  Local Instance : Enriched (PSh (OrdCat SI)) (PSh (OrdCat SI))
    := (@self_enriched (PSh (OrdCat SI)) _).
  Local Instance : Enriched ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI))
    := op_enriched_def.
  Local Instance : Enriched (cat_prod ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI)))
                     (PSh (OrdCat SI))
    := prod_enriched_def.

  Local Opaque later next.

  Program Definition exp_psh_enr_def
    (a b : functor (OrdCat SI)ᵒᵖ Typ * functor (OrdCat SI)ᵒᵖ Typ)
    : natural (a.1 ↑ₒ b.1 ×ₒ (b.2 ↑ₒ a.2)) (b.2 ↑ₒ b.1 ↑ₒ (a.2 ↑ₒ a.1))
    := MkNat (λ x,
           λ f,
           MkNat (λ c,
               λ g,
               MkNat (λ d,
                   λ h,
                   ((f.2 ₙ d)
                      (g.1 ∘ h.1,
                        ((g.2 ₙ d) (h.1,
                             ((f.1 ₙ d) (g.1 ∘ h.1, h.2))))))) _) _) _.
  Next Obligation.
    intros ??? N ? M ?? F.
    cbn beta.
    extensionality t1.
    simpl.
    rewrite -(psh_naturality N.2 _ _ F) /=; f_equiv.
    unfold hom_prod; simpl.
    f_equiv; first apply proof_irrel.
    rewrite -(psh_naturality M.2 _ _ F) /=; f_equiv.
    unfold hom_prod; simpl.
    f_equiv.
    rewrite -(psh_naturality N.1 _ _ F) /=; f_equiv.
    unfold hom_prod; simpl.
    f_equiv.
    apply proof_irrel.
  Qed.
  Next Obligation.
    intros ???????.
    extensionality t1.
    apply natural_equiv_unpack; intros ?.
    extensionality t2.
    simpl.
    do 2 f_equiv; first apply proof_irrel.
    do 4 f_equiv. apply proof_irrel.
  Qed.
  Next Obligation.
    intros ?????.
    extensionality t1.
    apply natural_equiv_unpack; intros ?.
    extensionality t2.
    apply natural_equiv_unpack; intros ?.
    extensionality t3.
    simpl.
    do 2 f_equiv; first apply proof_irrel.
    do 4 f_equiv.
    apply proof_irrel.
  Qed.
  Fail Next Obligation.

  Global Program Instance exp_psh_enr : EnrichedFunctor exp_func
    := MkEnrFunc (λ a b, exp_psh_enr_def a b) _ _ _.
  Next Obligation.
    intros a b f; simpl.
    apply natural_equiv_unpack; intros ?.
    extensionality x; destruct x.
    apply natural_equiv_unpack; intros ?.
    extensionality y.
    apply natural_equiv_unpack; intros d.
    extensionality y'; simpl.
    epose proof (equal_f (naturality f y'.1) ()) as H.
    simpl in H.
    rewrite H /hom_prod /=; clear H.
    epose proof (equal_f (naturality f y.1) ()) as H.
    simpl in H.
    rewrite H /hom_prod /=; clear H.
    do 3 f_equiv; first apply proof_irrel.
    f_equiv; first apply proof_irrel.
    do 2 f_equiv; apply proof_irrel.
  Qed.
  Next Obligation.
    intros a b c; simpl.
    apply natural_equiv_unpack; intros d.
    extensionality y.
    apply natural_equiv_unpack; intros ?.
    extensionality y'.
    apply natural_equiv_unpack; intros ?.
    extensionality y''.
    simpl.
    do 2 f_equiv; first apply proof_irrel.
    do 2 f_equiv; first apply proof_irrel.
    do 4 f_equiv; first apply proof_irrel.
    do 2 f_equiv; apply proof_irrel.
  Qed.
  Next Obligation.
    intros a.
    apply natural_equiv_unpack; intros c.
    extensionality y.
    apply natural_equiv_unpack; intros d.
    extensionality y'.
    apply natural_equiv_unpack; intros e.
    extensionality y''.
    simpl.
    f_equiv.
    by destruct y''.
  Qed.
  Fail Next Obligation.
End exp_func.

Section interface.
  Context {SI : indexT}.
  Local Instance : Enriched (PSh (OrdCat SI)) (PSh (OrdCat SI))
    := (@self_enriched (PSh (OrdCat SI)) _).
  Local Instance : Enriched ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI))
    := op_enriched_def.
  Local Instance : Enriched (cat_prod ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI)))
                     (PSh (OrdCat SI))
    := prod_enriched_def.
  Local Instance : Enriched (cat_prod
                               (cat_prod ((PSh (OrdCat SI)) ᵒᵖ)
                                  (PSh (OrdCat SI)))
                               (cat_prod ((PSh (OrdCat SI)) ᵒᵖ)
                                  (PSh (OrdCat SI))))
                     (PSh (OrdCat SI))
    := prod_enriched_def.

  Lemma i_cod_func_prod_lc
    (f g : functor (cat_prod ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI)))
             (PSh (OrdCat SI)))
    {Hf : LocallyContractiveFunctor f}
    {Hg : LocallyContractiveFunctor g}
    : LocallyContractiveFunctor (cod_func_prod f g).
  Proof.
    unfold cod_func_prod.
    apply (@LocallyContractiveFunctor_comp_r SI
                   (cat_prod ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI)))
                   (cat_prod (cat_prod ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI)))
                      (cat_prod ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI))))
                   (PSh (OrdCat SI)) _ _ _
                   (functor_compose (functor_prod f g)
                      (prod_func (PSh (OrdCat SI))))
                   functor_diag);
      last apply functor_diag_enr.
    unshelve eapply LocallyContractiveFunctor_comp_l.
    - apply prod_enriched_def.
    - by apply func_prod_lc.
    - apply prod_func_enr.
  Qed.

  Lemma i_cod_func_sum_lc
    (f g : functor (cat_prod ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI)))
             (PSh (OrdCat SI)))
    {Hf : LocallyContractiveFunctor f}
    {Hg : LocallyContractiveFunctor g}
    : LocallyContractiveFunctor (cod_func_sum f g).
  Proof.
    unfold cod_func_sum.
    set (T1 := functor_diag).
    set (T2 := (functor_prod f g)).
    set (T3 := (coprod_func (PSh (OrdCat SI)))).
    apply (@LocallyContractiveFunctor_comp_r SI
             (cat_prod (PSh (OrdCat SI))ᵒᵖ (PSh (OrdCat SI)))
             (cat_prod (cat_prod (PSh (OrdCat SI))ᵒᵖ (PSh (OrdCat SI)))
                (cat_prod (PSh (OrdCat SI))ᵒᵖ (PSh (OrdCat SI))))
             (PSh (OrdCat SI))
             _ _ _ (functor_compose T2 T3) T1);
      last apply functor_diag_enr.
    unshelve eapply LocallyContractiveFunctor_comp_l.
    - apply prod_enriched_def.
    - by apply func_prod_lc.
    - apply coprod_func_enr.
  Qed.

  Lemma i_lift_func_lc
    (f : functor (PSh (OrdCat SI)) (PSh (OrdCat SI)))
    {Hf : LocallyContractiveFunctor f}
    : LocallyContractiveFunctor (func_lift f).
  Proof.
    by apply func_lift_lc.
  Qed.

  Lemma i_const_func_lc
    (c : obj (PSh (OrdCat SI)))
    : LocallyContractiveFunctor (func_const c).
  Proof.
    apply func_const_lc.
  Qed.
End interface.

Section complete_prod.
  Context {C D : category}.
  Context {HC : Complete C} {HD : Complete D}.

  Program Definition cat_prod_limit_cone (J : category)
    (F : functor J (cat_prod C D)) : cone F
    := MkCone ((vertex (term (HC J (functor_compose F (cat_proj1 _ _)))))
           , (vertex (term (HD J (functor_compose F (cat_proj2 _ _))))))
         (λ j, ((side (term (HC J (functor_compose F (cat_proj1 _ _)))) j)
                 , (side (term (HD J (functor_compose F (cat_proj2 _ _)))) j))) _.
  Next Obligation.
    intros; simpl.
    rewrite -!side_commutes //.
  Qed.

  Program Definition cone_proj1 (J : category)
    (F : functor J (cat_prod C D)) (cn : cone F)
    : cone (functor_compose F (cat_proj1 C D))
    := MkCone (vertex cn).1 (λ j, (side cn j).1) _.
  Next Obligation.
    intros; simpl.
    rewrite (side_commutes cn f).
    reflexivity.
  Qed.

  Program Definition cone_proj2 (J : category)
    (F : functor J (cat_prod C D)) (cn : cone F)
    : cone (functor_compose F (cat_proj2 C D))
    := MkCone (vertex cn).2 (λ j, (side cn j).2) _.
  Next Obligation.
    intros; simpl.
    rewrite (side_commutes cn f).
    reflexivity.
  Qed.

  Program Definition cat_prod_limit_is_term (J : category)
    (F : functor J (cat_prod C D))
    : is_terminal (C := ConeCat F) (cat_prod_limit_cone J F)
    := MkIsTerm _ (λ d,
           MkConeHom ((cone_hom_map
                         (bang
                            (term_is_terminal
                               (HC J (functor_compose F (cat_proj1 _ _))))
                            (cone_proj1 J F d))),
               (cone_hom_map
                  (bang
                     (term_is_terminal
                        (HD J (functor_compose F (cat_proj2 _ _))))
                     (cone_proj2 J F d)))) _) _.
  Next Obligation.
    intros; simpl.
    rewrite -(cone_hom_commutes
                (bang (term_is_terminal (HC J (functor_compose F (cat_proj1 C D))))
                   (cone_proj1 J F d)) j).
    rewrite -(cone_hom_commutes
                (bang (term_is_terminal (HD J (functor_compose F (cat_proj2 C D))))
                   (cone_proj2 J F d)) j).
    simpl.
    destruct (side d j).
    reflexivity.
  Qed.
  Next Obligation.
    intros; simpl.
    destruct f as [[f1 f2] fc]; simpl.
    unshelve eset (f1' := (MkConeHom (F := (functor_compose F (cat_proj1 C D))) _ _)
           : hom (C := ConeCat (functor_compose F (cat_proj1 C D)))
               (cone_proj1 J F c)
               (term (HC J (functor_compose F (cat_proj1 C D))))).
    {
      simpl.
      apply f1.
    }
    {
      intros; simpl.
      epose proof (fc j) as H.
      simpl in H.
      rewrite H.
      reflexivity.
    }
    unshelve eset (f2' := (MkConeHom (F := (functor_compose F (cat_proj2 C D))) _ _)
           : hom (C := ConeCat (functor_compose F (cat_proj2 C D)))
               (cone_proj2 J F c)
               (term (HD J (functor_compose F (cat_proj2 C D))))).
    {
      simpl.
      apply f2.
    }
    {
      intros; simpl.
      epose proof (fc j) as H.
      simpl in H.
      rewrite H.
      reflexivity.
    }
    rewrite /equiv /cone_hom_eq /=.
    apply cone_hom_equiv_unpack.
    unfold cone_hom_eq; simpl.
    f_equiv.
    - epose proof (@bang_unique _ _
                     (term_is_terminal
                        (HC J (functor_compose F (cat_proj1 C D))))
                     (cone_proj1 J F c) f1') as H.
      subst f1'.
      simpl in H.
      rewrite -H.
      reflexivity.
    - epose proof (@bang_unique _ _
                     (term_is_terminal
                        (HD J (functor_compose F (cat_proj2 C D))))
                     (cone_proj2 J F c) f2') as H.
      subst f2'.
      simpl in H.
      rewrite -H.
      reflexivity.
  Qed.

  Program Definition cat_prod_limit_term (J : category)
    (F : functor J (cat_prod C D)) : terminal (ConeCat F)
    := MkTerm (cat_prod_limit_cone J F) (cat_prod_limit_is_term J F).

  Program Definition cat_prod_complete : Complete (cat_prod C D)
    := λ J F, cat_prod_limit_term J F.
End complete_prod.

Section example.
  Context {SI : indexT}.
  Local Instance : Enriched (PSh (OrdCat SI)) (PSh (OrdCat SI))
    := (@self_enriched (PSh (OrdCat SI)) _).
  Local Instance : Enriched ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI))
    := op_enriched_def.
  Local Instance : Enriched (cat_prod ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI)))
                     (PSh (OrdCat SI))
    := prod_enriched_def.

  Example simplified_gitree_dom
    : functor (cat_prod ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI))) (PSh (OrdCat SI))
    := (functor_compose exp_func later)
       +ᵨ (Δᵨ (discr_psh nat))
       +ᵨ (↑ᵨ later).
  Lemma simplified_gitree_dom_lc
    : LocallyContractiveFunctor simplified_gitree_dom.
  Proof.
    apply i_cod_func_sum_lc.
    - apply i_cod_func_sum_lc.
      + eapply LocallyContractiveFunctor_comp_r.
        * apply later_lc.
        * apply exp_psh_enr.
      + apply i_const_func_lc.
    - apply i_lift_func_lc.
      apply later_lc.
  Qed.

  Lemma simplified_gitree_dom_sol : @bifunc_solution _ simplified_gitree_dom.
  Proof.
    unshelve eapply (@symmetrization_sol SI
                       (PSh (OrdCat SI)) _ _ simplified_gitree_dom simplified_gitree_dom_lc _).
    intros F ?.
    unshelve eapply solver; last done.
    unshelve eapply cat_prod_complete.
    apply func_cat_cocomplete.
  Qed.
End example.
