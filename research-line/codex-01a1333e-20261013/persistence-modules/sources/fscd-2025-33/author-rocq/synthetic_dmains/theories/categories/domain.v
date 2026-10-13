From SynthDom Require Import prelude.
From SynthDom Require Import stepindex.
From SynthDom.categories Require Import category ord_cat enriched.

Set Universe Polymorphism.
Unset Universe Minimization ToSet.

Opaque later next.

Lemma transpose_compose_right {C} `{!HasTerm C, !HasProducts C
    , !HasExponentials C}
  {a b c d : obj C} (f : hom (b ×ₒ a) c) (g : hom d a) :
  transpose f ∘ g = transpose (f ∘ (id _ ×ₕ g)).
Proof.
  unfold transpose.
  apply exp_hom_unique.
  rewrite -{2} (left_id (id b)).
  rewrite hom_prod_comp.
  rewrite -comp_assoc.
  by rewrite -(exp_hom_commutes (exponential_of b c)).
Qed.

Section solution_unique.
  Context {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
    (F : functor C C) `{!LocallyContractiveFunctor F}.

  Record solution := MkSolution { sol_obj : obj C; sol_iso : (F ₒ sol_obj) ≃ sol_obj}.

  Definition alg_of_solution (S : solution) : algebra F :=
    MkAlg (sol_obj S) (forward (sol_iso S)).

  Definition solution_to_alg (S : solution) (A : algebra F) :
    natural (enr_hom (sol_obj S) (car A)) (enr_hom (sol_obj S) (car A)) :=
    enr_comp_r (backward (sol_iso S)) ∘
    (enr_comp_l (cons A) ∘
    enr_func_h_map F (sol_obj S) (car A)).

  Program Definition fix_of_solution_to_alg_alg_hom (S : solution) (A : algebra F)
    (fx : natural (1ₒ) (enr_hom (sol_obj S) (car A)))
    (fx_fix : (solution_to_alg S A) ∘@{PSh _} fx = fx) :
    alg_hom (alg_of_solution S) A :=
    MkAlgHom ⌞fx⌟ _.
  Next Obligation.
    intros S A fx fx_fix.
    rewrite -{1}fx_fix /solution_to_alg.
    rewrite comp_assoc enr_comp_r_comp -enr_comp_comp !enr_embed_project.
    rewrite comp_assoc enr_comp_l_comp -enr_comp_comp !enr_embed_project.
    rewrite -enr_func_h_map_is_h_map !enr_embed_project.
    rewrite !comp_assoc /alg_of_solution /=.
    pose proof (is_iso (sol_iso S)) as [-> _].
    rewrite right_id //.
  Qed.
  Fail Next Obligation.

  Lemma alg_hom_from_solution_is_fix (S : solution) (A : algebra F)
    (h : alg_hom (alg_of_solution S) A) :
    (solution_to_alg S A) ∘@{PSh _} ⌜alg_hom_map h⌝ = ⌜alg_hom_map h⌝.
  Proof.
    rewrite /solution_to_alg.
    rewrite (comp_assoc _ _ (enr_comp_r _))
      (comp_assoc _ _ (enr_comp_l _)).
    rewrite -enr_func_h_map_is_h_map !enr_embed_project.
    rewrite enr_comp_l_comp -enr_comp_comp !enr_embed_project.
    rewrite enr_comp_r_comp -enr_comp_comp !enr_embed_project.
    rewrite -(alg_hom_commutes h).
    rewrite !comp_assoc /alg_of_solution /=.
    pose proof (is_iso (sol_iso S)) as [_ ->].
    rewrite right_id //.
  Qed.

  Program Definition alg_of_solution_is_initial S :
    @is_initial (Alg F) (alg_of_solution S) :=
    MkIsInit _
      (λ A, fix_of_solution_to_alg_alg_hom S A
              (contr_fix (solution_to_alg S A))
              (contr_fix_unfold (solution_to_alg S A)))
      _.
  Next Obligation.
    intros S A h; simpl.
    match goal with
      |- ?A = ?B =>
        apply alg_hom_map_eq;
        rewrite -(enr_embed_project (alg_hom_map A))
        -(enr_embed_project (alg_hom_map B))
    end.
    f_equiv.
    apply (contr_fix_unique (solution_to_alg S A)).
    - apply alg_hom_from_solution_is_fix.
    - apply alg_hom_from_solution_is_fix.
  Qed.
  Fail Next Obligation.

  Definition solution_unique (S S' : solution) : sol_obj S ≃ sol_obj S' :=
    alg_iso
      (@is_initial_unique (Alg F) _ _
         (alg_of_solution_is_initial S)
         (alg_of_solution_is_initial S')).

End solution_unique.

Section later.
  Context {SI : indexT}.
  Local Instance : Enriched (PSh (OrdCat SI)) (PSh (OrdCat SI)) :=
    (@self_enriched (PSh (OrdCat SI)) _).

  Program Definition later_hom_action (F G : obj (PSh (OrdCat SI)))
  : hom (later ₒ (G ↑ₒ F)) ((later ₒ G) ↑ₒ (later ₒ F))
  := (transpose ((later ₕ eval _) ∘ (backward (later_prod _ _)))).

  Opaque comp.
  Opaque eval.
  Opaque id.
  Opaque prj1.
  Opaque prj2.

  Lemma later_hom_action_project_embed
    (F G : obj (PSh (OrdCat SI))) (f : hom (1ₒ) (G ↑ₒ F))
    : later_hom_action F G ∘ (next ₙ (G ↑ₒ F)) ∘ f
        = transpose' (later ₕ untranspose' f).
  Proof.
    intros; simpl.
    unfold later_hom_action.
    rewrite comp_assoc.
    rewrite (naturality next f).
    rewrite -comp_assoc.
    rewrite transpose_compose_right.
    rewrite -h_map_id.
    rewrite comp_assoc.
    rewrite (@naturality _ _ _ _ (backward (later_preserves_prods_nat SI))
               (F, (1ₒ)) (F, (G ↑ₒ F)) (id F, f)).
    simpl.
    rewrite -comp_assoc.
    rewrite -h_map_comp.
    rewrite -{1} (transpose'_untranspose' f).
    unfold transpose' at 1.
    unfold transpose at 2.
    pose proof (exp_hom_commutes (exponential_of F G)
                  (untranspose' f ∘ term_times_proj F ∘ commutator F (1ₒ)))
      as HEQ.
    rewrite -HEQ; clear HEQ.
    rewrite comp_assoc.
    rewrite commute_term_times_proj.
    rewrite h_map_comp.
    rewrite transpose_compose_right.
    rewrite comp_assoc.
    rewrite comp_assoc.
    assert ((later ₕ prj1 (product_of F (1ₒ))
        ∘ (backward (later_preserves_prods_nat SI)ₙ (F, term_func (OrdCat SI)ᵒᵖ Typ)
             ∘ (id (later ₒ F) ×ₕ (next ₙ term_func (OrdCat SI)ᵒᵖ Typ))))
              = prj1 _) as HEQ.
    {
      unfold later_preserves_prods_nat.
      rewrite <-comp_assoc.
      rewrite (right_adj_preserves_prods_backward_prj1
                 later_adj _ _ _ _
                 (id (later ₒ F))
                 (next ₙ term_func (OrdCat SI)ᵒᵖ Typ)).
      rewrite left_id.
      reflexivity.
    }
    simpl in HEQ.
    rewrite HEQ; clear HEQ.
    unfold transpose'.
    rewrite comp_assoc.
    rewrite commute_term_times_proj.
    reflexivity.
  Qed.

  Lemma later_hom_action_contr_assoc
    (F G H : obj (PSh (OrdCat SI)))
    : (enr_comp _ _ _
         ∘ (later_hom_action F G ×ₕ (later_hom_action G H)))
        = (later_hom_action F H ∘ (later ₕ enr_comp _ _ _) ∘ (backward (later_prod _ _))).
  Proof.
    simpl.
    rewrite transpose_compose_right.
    rewrite !comp_assoc.
    rewrite associator'_twist2.
    rewrite -(comp_assoc (associator' (later ₒ F) (later ₒ (G ↑ₒ F)) (later ₒ (H ↑ₒ G)))).
    rewrite -hom_prod_comp.
    rewrite left_id.
    unfold later_hom_action at 1.
    pose proof (eval_transpose
                  (later ₕ eval (exponential_of F G) ∘ backward (later_prod F (exp (exponential_of F G))))
                  (id (later ₒ F))) as HEQ.
    rewrite HEQ; clear HEQ.
    rewrite hom_prod_id.
    rewrite right_id.
    unfold later_hom_action at 1.
    rewrite <-comp_assoc.
    pose proof (eval_transpose
                  (later ₕ eval (exponential_of G H) ∘ backward (later_prod G (exp (exponential_of G H))))
                  (later ₕ eval (exponential_of F G) ∘ backward (later_prod F (exp (exponential_of F G))))) as HEQ.
    rewrite HEQ; clear HEQ.
    rewrite hom_prod_comp_right_id.
    simpl.
    rewrite <-h_map_id at 2.
    rewrite (comp_assoc _ (backward (later_preserves_prods_nat SI)ₙ (G, psh_exp G H))).
    rewrite -(comp_assoc _ _ (backward (later_preserves_prods_nat SI)ₙ (G, psh_exp G H))).
    epose proof (@naturality _ _ _ _
                   (backward (later_preserves_prods_nat SI))
                   ((F ×ₒ psh_exp F G), (psh_exp G H))
                   (G, (psh_exp G H))
                   ((eval (exponential_of F G)), id _)) as Hn.
    simpl in Hn; rewrite Hn; clear Hn.
    rewrite <-!comp_assoc.
    pose proof (h_map_comp _ _ later _ _ _ (eval (exponential_of F G) ×ₕ id (H ↑ₒ G))
                  (eval (exponential_of G H))) as HEQ.
    rewrite -HEQ; clear HEQ.
    rewrite ->!comp_assoc.
    assert ((backward (later_preserves_prods_nat SI)ₙ (F ×ₒ psh_exp F G, psh_exp G H)
               ∘ (backward (later_preserves_prods_nat SI)ₙ (F, psh_exp F G) ×ₕ id (later ₒ psh_exp G H)
                    ∘ associator' (later ₒ F) (later ₒ (G ↑ₒ F)) (later ₒ (H ↑ₒ G))))
               = ((later ₕ (associator' F (G ↑ₒ F) (H ↑ₒ G)))
                    ∘ (backward (later_preserves_prods_nat SI)ₙ (F, (G ↑ₒ F ×ₒ (H ↑ₒ G)))))
               ∘ (id _ ×ₕ (backward (later_preserves_prods_nat SI)ₙ ((G ↑ₒ F), H ↑ₒ G)))) as HEQ.
    {
      rewrite -right_adj_preserves_prods_backward_assoc.
      simpl.
      unfold later_preserves_prods_nat.
      simpl.
      rewrite ->!comp_assoc.
      f_equiv.
      reflexivity.
    }
    simpl in HEQ; rewrite HEQ; clear HEQ.
    rewrite <-!comp_assoc.
    rewrite -transpose_compose_right.
    epose proof (h_map_comp _ _ later _ _ _
                   (associator' F (G ↑ₒ F) (H ↑ₒ G))
                   (eval (exponential_of G H) ∘ (eval (exponential_of F G) ×ₕ id (H ↑ₒ G)))) as HEQ.
    rewrite -HEQ; clear HEQ.
    f_equiv.
    unfold later_hom_action.
    simpl.
    unfold inner_comp.
    simpl.
    rewrite transpose_compose_right.
    f_equiv.
    rewrite -h_map_id.
    epose proof (comp_assoc _ _ (later ₕ eval (exponential_of F H))) as HEQ.
    rewrite ->HEQ; clear HEQ.
    epose proof (@naturality _ _ _ _
                   (backward (later_preserves_prods_nat SI))
                   (F, (psh_exp F G ×ₒ psh_exp G H))
                   (F, (H ↑ₒ F))
                   (id F, (transpose
                             (eval (exponential_of G H) ∘ (eval (exponential_of F G) ×ₕ id (H ↑ₒ G))
                                ∘ associator' F (psh_exp F G) (psh_exp G H))))) as Hn.
    simpl in Hn.
    rewrite Hn; clear Hn.
    rewrite <-!comp_assoc.
    f_equiv.
    rewrite -h_map_comp.
    pose proof (eval_transpose2 ((eval (exponential_of G H) ∘ (eval (exponential_of F G) ×ₕ id (H ↑ₒ G))
                                     ∘ associator' F (psh_exp F G) (psh_exp G H)))) as HEQ.
    rewrite HEQ; clear HEQ.
    reflexivity.
  Qed.

  Lemma later_hom_action_enr_assoc
    (F G H : obj (PSh (OrdCat SI)))
    : enr_comp _ _ _
        ∘ (later_hom_action F G ∘ (next ₙ (G ↑ₒ F)) ×ₕ (later_hom_action G H ∘ (next ₙ (H ↑ₒ G))))
        = later_hom_action F H ∘ (next ₙ (H ↑ₒ F)) ∘ enr_comp _ _ _.
  Proof.
    intros; simpl.
    rewrite hom_prod_comp.
    rewrite -!comp_assoc.
    rewrite later_hom_action_contr_assoc.
    rewrite ->!comp_assoc.
    f_equiv; last done.
    simpl.
    pose proof (naturality next (inner_comp F G H))
      as Hn'.
    simpl in Hn'; rewrite Hn'; clear Hn'.
    f_equiv; last done.
    rewrite <-(left_id (next ₙ (G ↑ₒ F ×ₒ (H ↑ₒ G)))).
    epose proof (iso_lr (is_iso (natural_iso_proj (later_preserves_prods_nat SI) (G ↑ₒ F, H ↑ₒ G)))) as HEQ.
    simpl in HEQ.
    rewrite -HEQ; clear HEQ.
    rewrite ->!comp_assoc.
    f_equiv; last done.
    unfold later_preserves_prods_nat.
    rewrite (right_adj_preserves_prods_forward later_adj).
    simpl.
    rewrite hom_to_prod_comp_r.
    pose proof (naturality next (prj1 (product_of (G ↑ₒ F) (H ↑ₒ G)))) as HEQ.
    rewrite -HEQ; clear HEQ.
    pose proof (naturality next (prj2 (product_of (G ↑ₒ F) (H ↑ₒ G)))) as HEQ.
    rewrite -HEQ; clear HEQ.
    simpl.
    rewrite hom_to_prod_comp.
    rewrite <-(right_id (prj1 (product_of (G ↑ₒ F) (H ↑ₒ G)))).
    rewrite <-(right_id (prj2 (product_of (G ↑ₒ F) (H ↑ₒ G)))).
    rewrite hom_to_prod_of_prjs.
    rewrite right_id.
    reflexivity.
  Qed.

  Lemma later_hom_action_contr_id
    (F : obj (PSh (OrdCat SI)))
    : later_hom_action F _ ∘ (later ₕ (transpose' (id _))) ∘ (next ₙ (1ₒ))
        = transpose' (id (later ₒ F)).
  Proof.
    unfold later_hom_action.
    rewrite transpose_compose_right.
    rewrite <-h_map_id.
    simpl.
    rewrite comp_assoc.
    epose proof (@naturality _ _ _ _
                   (backward (later_preserves_prods_nat SI))
                   (F, (1ₒ))
                   (F, psh_exp F F)
                   (id F, transpose' (id F)))
      as Hn.
    simpl in Hn; rewrite Hn; clear Hn.
    rewrite <-comp_assoc.
    rewrite <-h_map_comp.
    unfold transpose'.
    epose proof (eval_transpose
                   (id F ∘ term_times_proj F ∘ commutator F (1ₒ))
                   (id F))
      as HEQ.
    rewrite HEQ; clear HEQ.
    rewrite hom_prod_id.
    rewrite left_id right_id.
    rewrite h_map_id left_id.
    rewrite !commute_term_times_proj.
    rewrite transpose_compose_right.
    unfold later_preserves_prods_nat.
    rewrite right_adj_preserves_prods_backward_prj1.
    rewrite left_id.
    reflexivity.
  Qed.

  Lemma later_hom_action_enr_id
    (F : obj (PSh (OrdCat SI)))
    : later_hom_action F F ∘ (next ₙ _) ∘ (transpose' (id _))
        = transpose' (id (later ₒ F)).
  Proof.
    intros; simpl.
    rewrite -later_hom_action_contr_id.
    rewrite ->!comp_assoc.
    f_equiv; last done.
    rewrite -naturality.
    f_equiv.
    reflexivity.
  Qed.

  Global Program Instance later_enriched
    : EnrichedFunctor (C := (PSh (OrdCat SI)))
        (D := (PSh (OrdCat SI)))
        (E := (PSh (OrdCat SI))) later
    := MkEnrFunc
         (λ a b, (later_hom_action _ _ ∘ (next ₙ _)))
         _
         _
         _.
  Next Obligation.
    intros; simpl.
    by rewrite later_hom_action_project_embed.
  Qed.
  Next Obligation.
    intros; simpl.
    by rewrite later_hom_action_enr_assoc.
  Qed.
  Next Obligation.
    intros; simpl.
    by rewrite later_hom_action_enr_id.
  Qed.

  Global Program Instance later_lc
    : @LocallyContractiveFunctor SI (PSh (OrdCat SI)) (PSh (OrdCat SI)) _ _ later
    := MkLocContrFunc
         (λ a b, later_hom_action a b)
         _
         _
         _.
  Next Obligation.
    intros; simpl.
    reflexivity.
  Qed.
  Next Obligation.
    intros; simpl.
    by rewrite later_hom_action_contr_assoc.
  Qed.
  Next Obligation.
    intros; simpl.
    by rewrite later_hom_action_contr_id.
  Qed.

  Transparent comp.
  Transparent eval.
  Transparent id.
  Transparent prj1.
  Transparent prj2.
End later.

Section op_enriched.
  Context `{!HasTerm E} `{!HasProducts E} `{!Enriched C E}.

  Program Definition op_enriched_def
    : Enriched (C ᵒᵖ) E :=
    MkEnr
      (λ x y, enr_hom (y : obj C) (x : obj C))
      (λ x y f, enr_embed (C := C) f)
      (λ x y f, enr_project (C := C) f)
      (λ x y z, enr_comp (C := C) z y x ∘ commutator _ _)
      _ _ _ _ _ _.
  Next Obligation.
    intros; simpl in *.
    apply enr_embed_project.
  Qed.
  Next Obligation.
    intros; simpl in *.
    apply enr_project_embed.
  Qed.
  Next Obligation.
    intros; simpl in *.
    rewrite comp_assoc commute_hom_to_prod.
    apply enr_comp_comp.
  Qed.
  Next Obligation.
    intros; simpl in *.

    rewrite !comp_assoc.
    rewrite hom_prod_comp_right_id.
    rewrite -(comp_assoc _ (enr_comp c b a ×ₕ id (enr_hom d c))).
    rewrite -commute_hom_prod.
    rewrite (comp_assoc
               (commutator (enr_hom b a) (enr_hom c b) ×ₕ id (enr_hom d c))).
    rewrite -!comp_assoc.
    rewrite enr_comp_assoc'.
    rewrite !comp_assoc.

    f_equiv.
    rewrite -commute_hom_prod.
    rewrite hom_prod_comp_left_id.
    rewrite -!comp_assoc.
    rewrite -commute_hom_prod.
    rewrite !comp_assoc.
    f_equiv.

    rewrite commute_hom_prod.
    rewrite hom_to_prod_comp_r.
    rewrite -!comp_assoc.
    rewrite hom_to_prod_prj1.
    rewrite left_id.
    rewrite hom_to_prod_prj2.
    rewrite prj1_associator.
    rewrite !comp_assoc.
    rewrite prj2_associator.
    rewrite commute_hom_to_prod.


    rewrite /associator' /commutator.
    rewrite commute_hom_to_prod.
    rewrite left_id.
    rewrite ->3 hom_to_prod_comp_r.
    rewrite !comp_assoc.
    rewrite hom_to_prod_prj2 hom_to_prod_prj2.
    rewrite hom_to_prod_prj1 hom_to_prod_prj1.
    reflexivity.
  Qed.
  Next Obligation.
    intros; simpl in *.
    by rewrite !comp_assoc -commute_hom_prod
                              -!comp_assoc
                              enr_right_id
                              commute_term_times_proj.
  Qed.
  Next Obligation.
    intros; simpl in *.
    by rewrite !comp_assoc -commute_hom_prod
                              -!comp_assoc
                              enr_left_id
                              /commutator hom_to_prod_prj1
    .
  Qed.
  Fail Next Obligation.

End op_enriched.

Section prod_enriched.
  Context `{!HasTerm E} `{!HasProducts E} `{!Enriched C E} `{!Enriched D E}.

  Program Definition prod_enriched_def
    : Enriched (cat_prod C D) E :=
    MkEnr
      (λ x y, enr_hom (x.1 : obj C) (y.1 : obj C)
                ×ₒ enr_hom (x.2 : obj D) (y.2 : obj D))
      (λ x y f, << enr_embed (C := C) f.1, enr_embed (C := D) f.2 >>)
      (λ x y f, (enr_project (C := C) ((prj1 _) ∘ f)
                  , (enr_project (C := D) ((prj2 _) ∘ f))))
      (λ x y z, << enr_comp _ _ _
                  ∘ (prj1 _ ×ₕ prj1 _)
        , enr_comp _ _ _
            ∘ (prj2 _ ×ₕ prj2 _)>>)
      _ _ _ _ _ _.
  Next Obligation.
    intros; simpl in *.
    rewrite hom_to_prod_prj1 hom_to_prod_prj2 !enr_embed_project.
    by destruct f.
  Qed.
  Next Obligation.
    intros; simpl in *.
    by rewrite !enr_project_embed hom_to_prod_of_prjs.
  Qed.
  Next Obligation.
    intros; simpl in *.
    rewrite !enr_comp_comp.
    rewrite hom_to_prod_comp_r.
    f_equiv;
      (rewrite comp_assoc;
       rewrite hom_to_prod_comp;
       reflexivity).
  Qed.
  Next Obligation.
    intros; simpl in *.
    rewrite !comp_assoc.
    rewrite hom_to_prod_comp_r.
    rewrite (comp_assoc _ _ (enr_comp a.1 b.1 d.1)).
    rewrite (comp_assoc _ _ (enr_comp a.2 b.2 d.2)).
    rewrite -(comp_assoc _ _
                (prj1 (product_of (enr_hom a.1 b.1) (enr_hom a.2 b.2))
                   ×ₕ prj1 (product_of (enr_hom b.1 d.1) (enr_hom b.2 d.2)))).
    rewrite -(comp_assoc _ _
                (prj2 (product_of (enr_hom a.1 b.1) (enr_hom a.2 b.2))
                   ×ₕ prj2 (product_of (enr_hom b.1 d.1) (enr_hom b.2 d.2)))).
    rewrite -!hom_prod_comp.
    rewrite !right_id.
    rewrite hom_to_prod_prj1.
    rewrite hom_to_prod_prj2.
    assert (∀ (a b c d : obj C * obj D),
              (prj1 (product_of (enr_hom a.1 b.1) (enr_hom a.2 b.2))
                 ×ₕ (enr_comp b.1 c.1 d.1
                       ∘ (prj1 (product_of (enr_hom b.1 c.1) (enr_hom b.2 c.2))
                            ×ₕ prj1 (product_of (enr_hom c.1 d.1)
                                       (enr_hom c.2 d.2))))
                 ∘ associator (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2)
                 (enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2)
                 (enr_hom c.1 d.1 ×ₒ enr_hom c.2 d.2))
                =
                (id (enr_hom a.1 b.1) ×ₕ enr_comp b.1 c.1 d.1)
                ∘ associator (enr_hom a.1 b.1) (enr_hom b.1 c.1) (enr_hom c.1 d.1)
                ∘ ((prj1 _ ×ₕ prj1 _) ×ₕ prj1 _)) as ->.
    {
      clear.
      intros.
      rewrite -associator'_twist1.
      rewrite -!comp_assoc.
      rewrite (comp_assoc (associator' (enr_hom a.1 b.1) (enr_hom b.1 c.1)
                             (enr_hom c.1 d.1))).
      rewrite associator_associator'.
      f_equiv.
      rewrite right_id.
      rewrite -hom_prod_comp.
      rewrite left_id.
      reflexivity.
    }
    assert (∀ (a b c d : obj C * obj D),
              (prj2 (product_of (enr_hom a.1 b.1)
                       (enr_hom a.2 b.2))
                 ×ₕ (enr_comp b.2 c.2 d.2
                       ∘ (prj2 (product_of (enr_hom b.1 c.1) (enr_hom b.2 c.2))
                            ×ₕ prj2
                            (product_of (enr_hom c.1 d.1) (enr_hom c.2 d.2))))
                 ∘ associator (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2)
                 (enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2)
                 (enr_hom c.1 d.1 ×ₒ enr_hom c.2 d.2))
                =
                (id (enr_hom a.2 b.2) ×ₕ enr_comp b.2 c.2 d.2)
                ∘ associator (enr_hom a.2 b.2) (enr_hom b.2 c.2)
                (enr_hom c.2 d.2)
                ∘ ((prj2 _ ×ₕ prj2 _) ×ₕ prj2 _)) as ->.
    {
      clear.
      intros.
      rewrite -associator'_twist1.
      rewrite -!comp_assoc.
      rewrite (comp_assoc (associator' (enr_hom a.2 b.2) (enr_hom b.2 c.2)
                             (enr_hom c.2 d.2))).
      rewrite associator_associator'.
      f_equiv.
      rewrite right_id.
      rewrite -hom_prod_comp.
      rewrite left_id.
      reflexivity.
    }
    rewrite -!comp_assoc.
    rewrite !enr_comp_assoc.
    rewrite hom_to_prod_comp_r.
    f_equiv.
    - rewrite !comp_assoc.
      f_equiv.
      rewrite -!hom_prod_comp.
      rewrite hom_to_prod_prj1.
      f_equiv; first reflexivity.
      by rewrite right_id left_id.
    - rewrite !comp_assoc.
      f_equiv.
      rewrite -!hom_prod_comp.
      rewrite hom_to_prod_prj2.
      f_equiv; first reflexivity.
      by rewrite right_id left_id.
  Qed.
  Next Obligation.
    intros; simpl in *.
    rewrite hom_to_prod_comp_r.
    rewrite !comp_assoc.
    rewrite -!hom_prod_comp.
    rewrite !right_id.
    rewrite hom_to_prod_prj1 hom_to_prod_prj2.
    rewrite hom_prod_split.
    rewrite -comp_assoc.
    rewrite enr_left_id.
    rewrite (hom_prod_split (prj2 (product_of
                                     (enr_hom a.1 b.1) (enr_hom a.2 b.2)))).
    rewrite -comp_assoc.
    rewrite enr_left_id.
    rewrite !hom_prod_prj1.
    rewrite hom_to_prod_of_prjs.
    reflexivity.
  Qed.
  Next Obligation.
    intros; simpl in *.
    rewrite hom_to_prod_comp_r.
    rewrite !comp_assoc.
    rewrite -!hom_prod_comp.
    rewrite !right_id.
    rewrite hom_to_prod_prj1 hom_to_prod_prj2.
    rewrite -(left_id (prj1 (product_of (enr_hom a.1 b.1) (enr_hom a.2 b.2)))).
    rewrite -(right_id (⌜ id a.1 ⌝)).
    rewrite hom_prod_comp.
    rewrite -comp_assoc.
    rewrite enr_right_id.
    rewrite -(left_id (prj2 (product_of (enr_hom a.1 b.1) (enr_hom a.2 b.2)))).
    rewrite -(right_id (⌜ id a.2 ⌝)).
    rewrite hom_prod_comp.
    rewrite -comp_assoc.
    rewrite enr_right_id.
    rewrite !hom_prod_prj2.
    rewrite hom_to_prod_of_prjs.
    reflexivity.
  Qed.
  Fail Next Obligation.

End prod_enriched.

Section psh_op_limits_enriched.
  Context {SI : indexT} {J} {F : functor J ((PSh (OrdCat SI)) ᵒᵖ)}
    {L : PreSheaf (OrdCat SI)} (il : is_limit F L).

  Local Instance : Enriched ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI))
    := @op_enriched_def _ _ _ _ (self_enriched _).

  Opaque func_cat_colimits_pointwise.

  Program Definition psh_colimits_enriched_enr_cocone_to_pointwise_cocone
    {α} (cn : enr_cone F α) : cone (pointwise_func_colim F α) :=
    MkCone (enr_vertex cn ₒ α)
      (λ j, λ x, (enr_side cn j ₙ α) (id _, x)) _.
  Next Obligation.
    intros ?? j j' f.
    extensionality x; simpl in *.
    rewrite (λ z, equal_f (natural_equiv_pack (enr_side_commutes cn f) α)
                    ((reflexivity _), z)) /=.
    repeat f_equiv; apply proof_irrel.
  Qed.
  Fail Next Obligation.

  Program Definition enr_cocone_coherent_partial_cocone {α} (cn : enr_cone F α) :
    coherent_partial_cocone _ α :=
    MkCohParCocone _ _
      (psh_colimits_enriched_enr_cocone_to_pointwise_cocone cn)
      (λ _ f, (psh_colimits_enriched_enr_cocone_to_pointwise_cocone
                 (enr_cone_natural cn f)))
      (λ _ f, (enr_vertex cn ₕ f))
      _
      .
  Next Obligation.
    intros α cn β f j; extensionality x; simpl in *.
    epose proof (equal_f
                   (naturality (enr_side cn j) f) (_, _)) as Hn;
      simpl in Hn; rewrite <-Hn; simpl; clear Hn.
    repeat f_equiv; simpl.
    unfold hom_prod; simpl.
    f_equiv; last done.
    apply proof_irrel.
  Qed.

  Program Definition psh_colimits_enriched_enr_cocone_hom_back {α}
    (cn : enr_cone F α) :
    enr_cone_hom cn (cone_to_enr_cone (cone_of_is_cone (il_is_cone il)) α) :=
    MkEnrConeHom
      (MkNat (λ c, λ f,
           (cone_hom_map
              (bang (il_is_limiting_cone _ _
                       (func_cat_colimits_pointwise F il c))
                 (psh_colimits_enriched_enr_cocone_to_pointwise_cocone
                    (enr_cone_natural cn f.1))) f.2)) _)
      _.
  Next Obligation.
    intros α cn β γ f.
    extensionality H; destruct H as [le x]; simpl in *.
    replace (transitivity le (reflexivity α)) with le by apply proof_irrel.
    epose proof (equal_f
                   (func_cat_colimits_pointwise_natural F il
                      (enr_cocone_coherent_partial_cocone (enr_cone_natural cn le))
                      f) x) as Hpln.
    simpl in Hpln; rewrite Hpln /=; clear Hpln.
    eta_expand_equation ((L ₕ f) x).
    apply (hom_to_limit_unique
             _ _ _ (func_cat_colimits_pointwise F il γ)
             (cone_is_cone
                (psh_colimits_enriched_enr_cocone_to_pointwise_cocone
                   (enr_cone_natural (enr_cone_natural cn le) f)))).
    - intros ?; simpl in *.
      extensionality y; simpl.
      pose proof (equal_f (cone_hom_commutes
                    (bang (il_is_limiting_cone
                             (pointwise_func_colim F γ) (L ₒ γ)
                             (func_cat_colimits_pointwise F il γ))
                       (psh_colimits_enriched_enr_cocone_to_pointwise_cocone
                          (enr_cone_natural cn (transitivity f le)))) j) y) as HEQ.
      simpl in HEQ; rewrite -HEQ; clear HEQ.
      do 2 f_equiv.
      apply proof_irrel.
    - intros ?; extensionality y; simpl in *.
      pose proof (equal_f (cone_hom_commutes
                    (bang (il_is_limiting_cone
                             (pointwise_func_colim F γ) (L ₒ γ)
                             (func_cat_colimits_pointwise F il γ))
                       (psh_colimits_enriched_enr_cocone_to_pointwise_cocone
                          (enr_cone_natural (enr_cone_natural cn le) f))) j) y) as HEQ.
      simpl in HEQ; rewrite -HEQ; clear HEQ; last done.
  Qed.
  Next Obligation.
    intros α cn j.
    apply natural_equiv_unpack; intros β.
    extensionality t.
    destruct t as [le x]; simpl in *.
    epose proof (equal_f (cone_hom_commutes (bang
            (il_is_limiting_cone (pointwise_func_colim F β)
               (L ₒ β) (func_cat_colimits_pointwise F il β))
            (psh_colimits_enriched_enr_cocone_to_pointwise_cocone
               (enr_cone_natural cn (transitivity (reflexivity β) le)))) j)) as Hn;
      simpl in Hn; rewrite -Hn; simpl; clear Hn.
    repeat f_equiv. apply proof_irrel.
  Qed.
  Fail Next Obligation.

  Program Definition psh_colimits_enr_cocone_hom_to_cocone_hom {α cn β}
    (le : β ⪯ α)
    (h : enr_cone_hom cn
           (cone_to_enr_cone (cone_of_is_cone (il_is_cone il)) α)) :
      cone_hom
        (psh_colimits_enriched_enr_cocone_to_pointwise_cocone
           (enr_cone_natural cn le))
        (cone_of_is_cone (il_is_cone (func_cat_colimits_pointwise F il β))) :=
  MkConeHom (λ x, (enr_cone_hom_map h ₙ β) (le, x)) _.
  Next Obligation.
    intros ???? h ?; extensionality x; simpl in *.
    epose proof (natural_equiv_pack (enr_cone_hom_commutes h _) _) as Hsc;
    simpl in Hsc; rewrite ->Hsc; clear.
    repeat f_equiv; first apply proof_irrel.
    reflexivity.
  Qed.
  Fail Next Obligation.

  Program Definition psh_op_limits_enriched : enr_limit il :=
    λ α, MkEnrConeIsLimit (λ cn, psh_colimits_enriched_enr_cocone_hom_back cn) _.
  Next Obligation.
    intros α cn h h'.
    apply natural_equiv_unpack; intros β.
    extensionality t; destruct t as [le x]; simpl in *.
    epose proof (equal_f (cone_hom_equiv_pack _ (@bang_unique _ _
                   (il_is_limiting_cone _ _
                      (func_cat_colimits_pointwise F il β))
                   (psh_colimits_enriched_enr_cocone_to_pointwise_cocone
                      (enr_cone_natural cn le))
                   (psh_colimits_enr_cocone_hom_to_cocone_hom le h))) x) as Hbu.
    simpl in Hbu; rewrite Hbu; clear Hbu.
    epose proof (equal_f (cone_hom_equiv_pack _ (@bang_unique _ _
                   (il_is_limiting_cone _ _
                      (func_cat_colimits_pointwise F il β))
                   (psh_colimits_enriched_enr_cocone_to_pointwise_cocone
                      (enr_cone_natural cn le))
                   (psh_colimits_enr_cocone_hom_to_cocone_hom le h'))) x) as Hbu;
      simpl in Hbu; rewrite Hbu; clear Hbu.
    done.
  Qed.

End psh_op_limits_enriched.

Section psh_op_limits_enriched.
  Context {SI : indexT}.

  Local Instance : Enriched ((PSh (OrdCat SI)) ᵒᵖ) (PSh (OrdCat SI))
    := @op_enriched_def _ _ _ _ (self_enriched _).

  Global Instance op_limits_enriched : LimitsEnriched ((PSh (OrdCat SI)) ᵒᵖ)
    := λ J F c il, psh_op_limits_enriched il.

End psh_op_limits_enriched.

Section proj_limits.
  Context {C D : category}.

  Context {J} {F : functor J (cat_prod C D)}
    {L : obj (cat_prod C D)} (il : is_limit F L).

  Local Program Definition cone_from_limit_left
    (c : cone (functor_compose F (cat_proj1 C D)))
    : cone F := MkCone
                  (vertex c, L.2)
                  (λ j, ((side c j), (ic_side (il_is_cone il) j).2))
                  (λ j j' f,
                    _).
  Next Obligation.
    intros; simpl.
    f_equal.
    - apply (side_commutes c f).
    - by rewrite (ic_side_commutes (il_is_cone il) f).
  Qed.

  Local Definition cone_from_limit_left_proj
    (c : cone (functor_compose F (cat_proj1 C D)))
    : cone_hom (cone_from_limit_left c) (cone_of_is_cone (il_is_cone il)) :=
    (bang (il_is_limiting_cone _ _ il) (cone_from_limit_left c)).

  Local Program Definition cone_proj1
    : is_cone (functor_compose F (cat_proj1 C D)) L.1 :=
    MkIsCone
      L.1
      (λ j, (ic_side (il_is_cone il) j).1)
      (λ j j' f, _).
  Next Obligation.
    intros; simpl.
    by rewrite (ic_side_commutes (il_is_cone il) f).
  Qed.

  Local Program Definition extend_cone_proj1
    (c : cone (functor_compose F (cat_proj1 C D)))
    (f : cone_hom c (cone_of_is_cone cone_proj1))
    : cone_hom (cone_from_limit_left c) (cone_of_is_cone (il_is_cone il))
    := MkConeHom (cone_hom_map f, id _)
         (λ j, _).
  Next Obligation.
    intros; simpl.
    by rewrite (cone_hom_commutes f j) right_id.
  Qed.

  Program Definition limit_proj1
    : is_limit (functor_compose F (cat_proj1 C D)) L.1
    := MkIsLimit
         cone_proj1
         (MkIsTerm
            _
            (λ c, MkConeHom
                    (cone_hom_map (cone_from_limit_left_proj c)).1
                    (λ j, _))
            (λ c f, _)).
  Next Obligation.
    intros.
    simpl.
    pose proof (cone_hom_commutes (cone_from_limit_left_proj c) j) as H.
    by inversion H.
  Qed.
  Next Obligation.
    intros; simpl.
    apply cone_hom_equiv_unpack.
    unfold cone_hom_eq; simpl.
    pose proof (cone_hom_equiv_pack _ (bang_unique (il_is_limiting_cone _ _ il)
                                         (extend_cone_proj1 c f))).
    unfold cone_hom_eq in H; simpl in H.
    rewrite -H.
    done.
  Qed.

  Local Program Definition cone_from_limit_right
    (c : cone (functor_compose F (cat_proj2 C D)))
    : cone F := MkCone
                  (L.1, vertex c)
                  (λ j, ((ic_side (il_is_cone il) j).1, (side c j)))
                  (λ j j' f, _).
  Next Obligation.
    intros; simpl.
    rewrite (ic_side_commutes (il_is_cone il) f).
    rewrite (side_commutes c f).
    done.
  Qed.

  Local Definition cone_from_limit_right_proj
    (c : cone (functor_compose F (cat_proj2 C D)))
    : cone_hom (cone_from_limit_right c) (cone_of_is_cone (il_is_cone il)) :=
    (bang (il_is_limiting_cone _ _ il) (cone_from_limit_right c)).

  Local Program Definition cone_proj2
    : is_cone (functor_compose F (cat_proj2 C D)) L.2 :=
    MkIsCone
      L.2
      (λ j, (ic_side (il_is_cone il) j).2)
      (λ j j' f, _).
  Next Obligation.
    intros; simpl.
    rewrite (ic_side_commutes (il_is_cone il) f).
    done.
  Qed.

  Local Program Definition extend_cone_proj2
    (c : cone (functor_compose F (cat_proj2 C D)))
    (f : cone_hom c (cone_of_is_cone cone_proj2))
    : cone_hom (cone_from_limit_right c) (cone_of_is_cone (il_is_cone il))
    := MkConeHom (id _, cone_hom_map f)
         (λ j, _).
  Next Obligation.
    intros; simpl.
    by rewrite (cone_hom_commutes f j) right_id.
  Qed.

  Program Definition limit_proj2
    : is_limit (functor_compose F (cat_proj2 C D)) L.2
    := MkIsLimit
         cone_proj2
         (MkIsTerm
            _
            (λ c, MkConeHom
                    (cone_hom_map (cone_from_limit_right_proj c)).2
                    (λ j, _))
            (λ c f, _)).
  Next Obligation.
    intros; simpl.
    pose proof (cone_hom_commutes (cone_from_limit_right_proj c) j) as H.
    simpl in *.
    by inversion H.
  Qed.
  Next Obligation.
    intros; simpl.
    apply cone_hom_equiv_unpack.
    unfold cone_hom_eq; simpl.
    pose proof (cone_hom_equiv_pack _  (bang_unique (il_is_limiting_cone _ _ il) (extend_cone_proj2 c f))) as H.
    unfold cone_hom_eq in H; simpl in H.
    rewrite -H.
    done.
  Qed.

End proj_limits.

Section prod_limits_enriched.
  Context {SI : indexT}
    `{!Enriched C (PSh (OrdCat SI)), !Enriched D (PSh (OrdCat SI))}.

  Local Instance : Enriched (cat_prod C D) (PSh (OrdCat SI))
    := @prod_enriched_def (PSh (OrdCat SI)) _ _ _ _ _ _.

  Context `{HLE1 : !LimitsEnriched C, HLE2 : !LimitsEnriched D}.

  Context {J} {F : functor J (cat_prod C D)}
    {L : obj (cat_prod C D)} (il : is_limit F L).

  Local Program Definition restrict_enr_cone_left {α} (cn : enr_cone F α)
    : enr_cone (functor_compose F (cat_proj1 C D)) α
    := MkEnrCone
         (enr_vertex cn).1
         (λ j, (enr_side cn j).1)
         (λ j j' f, _).
  Next Obligation.
    intros; simpl.
    rewrite (enr_side_commutes cn f).
    done.
  Qed.

  Local Program Definition restrict_enr_cone_right {α} (cn : enr_cone F α)
    : enr_cone (functor_compose F (cat_proj2 C D)) α
    := MkEnrCone
         (enr_vertex cn).2
         (λ j, (enr_side cn j).2)
         (λ j j' f, _).
  Next Obligation.
    intros; simpl.
    rewrite (enr_side_commutes cn f).
    done.
  Qed.

  Local Program Definition restrict_enr_hom_left {α}
    (cn' : enr_cone F α)
    (h : enr_cone_hom cn'
           (cone_to_enr_cone (cone_of_is_cone (il_is_cone il)) α))
    : enr_cone_hom (restrict_enr_cone_left cn')
        (cone_to_enr_cone (cone_of_is_cone (il_is_cone (limit_proj1 il))) α)
    := MkEnrConeHom (enr_cone_hom_map h).1
         (λ j, _).
  Next Obligation.
    intros; simpl.
    rewrite (enr_cone_hom_commutes h j).
    simpl.
    do 2 f_equiv.
  Qed.

  Local Program Definition restrict_enr_hom_right {α}
    (cn' : enr_cone F α)
    (h : enr_cone_hom cn'
           (cone_to_enr_cone (cone_of_is_cone (il_is_cone il)) α))
    : enr_cone_hom (restrict_enr_cone_right cn')
        (cone_to_enr_cone (cone_of_is_cone (il_is_cone (limit_proj2 il))) α)
    := MkEnrConeHom (enr_cone_hom_map h).2
         (λ j, _).
  Next Obligation.
    intros; simpl.
    rewrite (enr_cone_hom_commutes h j).
    simpl.
    do 2 f_equiv.
    reflexivity.
  Qed.

  Local Program Definition prod_limits_enriched_enr_cone_hom_back {α}
    (cn : enr_cone F α) :
    enr_cone_hom cn (cone_to_enr_cone (cone_of_is_cone (il_is_cone il)) α) :=
    MkEnrConeHom
      ((enr_cone_hom_map (enr_limit_hom
                            (HLE1 J (functor_compose F (cat_proj1 _ _)) L.1
                               (limit_proj1 il) α)
                            (restrict_enr_cone_left cn))),
        (enr_cone_hom_map (enr_limit_hom
                             (HLE2 J (functor_compose F (cat_proj2 _ _)) L.2
                                (limit_proj2 il) α)
                             (restrict_enr_cone_right cn))))
      (λ j, _).
  Next Obligation.
    intros; simpl.
    pose proof (enr_cone_hom_commutes (enr_limit_hom
                                        (HLE1 J (functor_compose F
                                                   (cat_proj1 _ _)) L.1
                                           (limit_proj1 il) α)
                                        (restrict_enr_cone_left cn)) j) as H.
    simpl in H; rewrite -H; clear H.
    pose proof (enr_cone_hom_commutes (enr_limit_hom
                                        (HLE2 J (functor_compose F
                                                   (cat_proj2 _ _)) L.2
                                           (limit_proj2 il) α)
                                        (restrict_enr_cone_right cn)) j) as H.
    simpl in H; rewrite -H; clear H.
    by destruct (enr_side cn j).
  Qed.

  Program Definition prod_limits_enriched_lim : enr_limit il :=
    λ α, MkEnrConeIsLimit (λ cn, prod_limits_enriched_enr_cone_hom_back cn) _.
  Next Obligation.
    intros; simpl.
    apply injective_projections.
    - apply (@enr_limit_hom_unique _ _ _ _ _ _ _
               (HLE1 J (functor_compose F (cat_proj1 _ _)) L.1
                  (limit_proj1 _) α)
               (restrict_enr_cone_left cn')
               (restrict_enr_hom_left cn' h)
               (restrict_enr_hom_left cn' h')).
    - apply (@enr_limit_hom_unique _ _ _ _ _ _ _
               (HLE2 J (functor_compose F (cat_proj2 _ _)) L.2
                  (limit_proj2 _) α)
               (restrict_enr_cone_right cn')
               (restrict_enr_hom_right cn' h)
               (restrict_enr_hom_right cn' h')).
  Qed.

End prod_limits_enriched.

Section prod_limits_enriched.
  Context {SI : indexT}
    `{!Enriched C (PSh (OrdCat SI)), !Enriched D (PSh (OrdCat SI))}.

  Local Instance : Enriched (cat_prod C D) (PSh (OrdCat SI))
    := @prod_enriched_def (PSh (OrdCat SI)) _ _ _ _ _ _.

  Context `{!LimitsEnriched C, !LimitsEnriched D}.

  Global Instance prod_limits_enriched : LimitsEnriched (cat_prod C D)
    := λ J F c il, prod_limits_enriched_lim il.

End prod_limits_enriched.

Section enr_func_to_prod.
  Context {C D E Z}
    `{!HasTerm Z, !HasProducts Z}
    `{!Enriched C Z, !Enriched D Z, !Enriched E Z}
    {F : functor C D} {G : functor C E}
    `{!EnrichedFunctor F, !EnrichedFunctor G}.

  Local Instance : Enriched (cat_prod D E) Z := prod_enriched_def.

  Program Definition functor_to_prod_enr_def :
    EnrichedFunctor (functor_to_prod F G)
    := MkEnrFunc (λ a b, <<enr_func_h_map F a b, enr_func_h_map G a b>>)
         _ _ _.
  Next Obligation.
    intros; simpl.
    rewrite hom_to_prod_comp_r.
    f_equiv; apply enr_func_h_map_is_h_map.
  Qed.
  Next Obligation.
    intros; simpl.
    rewrite !hom_to_prod_comp_r.
    f_equiv.
    - rewrite enr_func_h_map_comp comp_assoc.
      f_equiv.
      by rewrite -hom_prod_comp !hom_to_prod_prj1.
    - rewrite enr_func_h_map_comp comp_assoc.
      f_equiv.
      by rewrite -hom_prod_comp !hom_to_prod_prj2.
  Qed.
  Next Obligation.
    intros; simpl.
    rewrite hom_to_prod_comp_r.
    by rewrite !enr_func_h_map_id.
  Qed.

End enr_func_to_prod.

Section lc_func_to_prod.
  Context {SI} {C D E}
    `{!Enriched C (PSh (OrdCat SI))
      , !Enriched D (PSh (OrdCat SI))
      , !Enriched E (PSh (OrdCat SI))}
    {F : functor C D} {G : functor C E}.

  Local Instance : Enriched (cat_prod D E) (PSh (OrdCat SI)) :=
    prod_enriched_def.

  Context `{!LocallyContractiveFunctor F, !LocallyContractiveFunctor G}.

  Local Instance : EnrichedFunctor (functor_to_prod F G) :=
    functor_to_prod_enr_def.

  Opaque comp.
  Opaque prj1.
  Opaque prj2.

  Program Definition functor_to_prod_lc_def
    : LocallyContractiveFunctor (functor_to_prod F G)
    := MkLocContrFunc
         (λ a b, <<contr_func_h_map F a b, contr_func_h_map G a b>>)
         _ _ _.
  Next Obligation.
    intros; simpl.
    rewrite hom_to_prod_comp_r.
    f_equiv; apply contr_func_h_map_is_h_map.
  Qed.
  Next Obligation.
    intros; simpl.
    rewrite !hom_to_prod_comp_r.
    f_equiv; rewrite contr_func_h_map_comp.
    - rewrite comp_assoc.
      f_equiv; last done.
      rewrite -hom_to_prod_comp.
      rewrite -!comp_assoc.
      rewrite !hom_to_prod_prj1.
      rewrite hom_to_prod_comp.
      rewrite -(right_id (prj1 (product_of (later ₒ enr_hom a b)
                                  (later ₒ enr_hom b c)))).
      rewrite -(right_id (prj2 (product_of (later ₒ enr_hom a b)
                                  (later ₒ enr_hom b c)))).
      rewrite hom_to_prod_of_prjs.
      rewrite right_id.
      reflexivity.
    - rewrite comp_assoc.
      f_equiv; last done.
      rewrite -hom_to_prod_comp.
      rewrite -!comp_assoc.
      rewrite !hom_to_prod_prj2.
      rewrite hom_to_prod_comp.
      rewrite -(right_id (prj1 (product_of (later ₒ enr_hom a b)
                                  (later ₒ enr_hom b c)))).
      rewrite -(right_id (prj2 (product_of (later ₒ enr_hom a b)
                                  (later ₒ enr_hom b c)))).
      rewrite hom_to_prod_of_prjs.
      rewrite right_id.
      reflexivity.
  Qed.
  Next Obligation.
    intros; simpl.
    rewrite !hom_to_prod_comp_r.
    f_equiv; apply contr_func_h_map_id.
  Qed.

  Transparent comp.
  Transparent prj1.
  Transparent prj2.

End lc_func_to_prod.

Program Definition flip_bifunc {C : category}
  (F : functor (cat_prod (C ᵒᵖ) C) C)
  : functor (cat_prod (C ᵒᵖ) C) (C ᵒᵖ) :=
  MkFunc (λ x, F ₒ (x.2, x.1))
    (λ a b f, @h_map (cat_prod (C ᵒᵖ) C) C F (b.2, b.1) (a.2, a.1) (f.2, f.1))
    _ _.
Next Obligation.
  intros; simpl.
  by rewrite -h_map_comp.
Qed.
Next Obligation.
  intros; simpl.
  by rewrite h_map_id.
Qed.

Section enr_func_flip_bifunc.
  Context {C E : category}
    `{!HasTerm E, !HasProducts E, !Enriched C E}.

  Local Instance : Enriched (C ᵒᵖ) E := op_enriched_def.
  Local Instance : Enriched (cat_prod (C ᵒᵖ) C) E := prod_enriched_def.

  Program Definition flip_bifunc_enr_def
    (F : functor (cat_prod (C ᵒᵖ) C) C)
    `{!EnrichedFunctor F} :
    EnrichedFunctor (E := E) (D := C ᵒᵖ) (flip_bifunc F)
    := MkEnrFunc (λ a b,
           enr_func_h_map F (b.2, b.1) (a.2, a.1) ∘ commutator _ _)
         _ _ _.
  Next Obligation.
    intros; simpl.
    rewrite comp_assoc.
    pose proof (@enr_func_h_map_is_h_map _ _ _ _ _ _ _ F _
                  (b.2, b.1) (a.2, a.1) (commutator _ _ ∘ f)) as Heq.
    simpl in Heq; rewrite -Heq; clear Heq.
    rewrite -!comp_assoc hom_to_prod_prj1 hom_to_prod_prj2.
    reflexivity.
  Qed.
  Next Obligation.
    intros; simpl.
    rewrite !comp_assoc.
    rewrite -!commute_hom_prod.
    rewrite hom_prod_comp.
    rewrite -!comp_assoc.
    pose proof (enr_func_h_map_comp F (c.2, c.1) (b.2, b.1) (a.2, a.1)) as HEQ.
    rewrite -HEQ //=; clear HEQ.
    rewrite !comp_assoc.
    f_equiv.
    rewrite ->1 hom_to_prod_comp_r.
    rewrite commute_hom_to_prod.
    f_equiv.
    - rewrite comp_assoc.
      f_equiv.
      rewrite comp_assoc.
      epose proof (comp_assoc _ _ (prj1 (product_of (enr_hom b.2 c.2)
                                           (enr_hom b.1 c.1))
                                     ×ₕ prj1 (product_of (enr_hom a.2 b.2)
                                                (enr_hom a.1 b.1 )))) as HEQ.
      rewrite <-HEQ; clear HEQ.
      rewrite -hom_prod_comp.
      rewrite !hom_to_prod_prj1.
      rewrite commute_hom_prod.
      rewrite -comp_assoc.
      rewrite commutator_involutive.
      rewrite left_id.
      reflexivity.
    - rewrite comp_assoc.
      f_equiv.
      rewrite -comp_assoc.
      rewrite -hom_prod_comp.
      rewrite !hom_to_prod_prj2.
      reflexivity.
  Qed.
  Next Obligation.
    intros; simpl.
    rewrite comp_assoc.
    rewrite commute_hom_to_prod.
    rewrite -(enr_func_h_map_id F (a.2, a.1)).
    by f_equiv.
  Qed.

End enr_func_flip_bifunc.

Section lc_func_flip_bifunc.
  Context {SI} {C}
    `{!Enriched C (PSh (OrdCat SI))}
    {F : functor (cat_prod (C ᵒᵖ) C) C}.

  Local Instance : Enriched (C ᵒᵖ) (PSh (OrdCat SI)) := op_enriched_def.
  Local Instance : Enriched (cat_prod (C ᵒᵖ) C) (PSh (OrdCat SI)) :=
    prod_enriched_def.

  Context `{!LocallyContractiveFunctor F}.

  Local Instance : EnrichedFunctor (flip_bifunc F) := flip_bifunc_enr_def F.

  Opaque comp.
  Opaque prj1.
  Opaque prj2.
  Opaque later_preserves_prods_nat.

  Program Definition flip_bifunc_lc_def
    : LocallyContractiveFunctor (flip_bifunc F)
    := MkLocContrFunc
         (λ a b, contr_func_h_map F (b.2, b.1) (a.2, a.1)
                   ∘ (later ₕ (commutator _ _)))
         _ _ _.
  Next Obligation.
    intros; simpl.
    reflexivity.
  Defined.
  Next Obligation.
    intros; simpl.
    rewrite comp_assoc.
    pose proof (naturality next
                  (commutator (enr_hom a.1 b.1) (enr_hom a.2 b.2))) as Heq.
    simpl in Heq; rewrite -Heq; clear Heq.
    rewrite -comp_assoc.
    pose proof (contr_func_h_map_is_h_map F (b.2, b.1) (a.2, a.1)) as Heq.
    simpl in Heq; rewrite -Heq; clear Heq.
    f_equiv.
    reflexivity.
  Qed.
  Next Obligation.
    intros; simpl.
    rewrite !comp_assoc.
    rewrite -!commute_hom_prod.
    rewrite hom_prod_comp.
    rewrite <-!comp_assoc.
    epose proof (contr_func_h_map_comp F (c.2, c.1) (b.2, b.1) (a.2, a.1)) as HEQ.
    rewrite -HEQ; clear HEQ.
    unfold later_prod.
    simpl.
    rewrite ->!comp_assoc.
    f_equiv; last done.
    rewrite <-!comp_assoc.
    rewrite -h_map_comp.
    rewrite commute_hom_to_prod.
    rewrite ->!comp_assoc.
    epose proof (comp_assoc _ _ (backward (later_preserves_prods_nat SI) ₙ
                                   (enr_hom b.2 c.2 ×ₒ enr_hom b.1 c.1, enr_hom a.2 b.2 ×ₒ enr_hom a.1 b.1))) as HEQ.
    simpl in HEQ.
    rewrite <-HEQ; clear HEQ.
    epose proof (@naturality _ _ _ _ (backward (later_preserves_prods_nat SI))
                   ((enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2), (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2))
                   ((enr_hom b.2 c.2 ×ₒ enr_hom b.1 c.1), (enr_hom a.2 b.2 ×ₒ enr_hom a.1 b.1))
                   (commutator (enr_hom b.1 c.1) (enr_hom b.2 c.2), commutator (enr_hom a.1 b.1) (enr_hom a.2 b.2))) as HEQ.
    simpl in HEQ.
    rewrite HEQ; clear HEQ.
    rewrite <-!comp_assoc.
    rewrite -h_map_comp.
    rewrite ->! comp_assoc.
    assert ((backward (later_preserves_prods_nat SI)ₙ
               (enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2, enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2))
              ∘ commutator
              (later ₒ (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2))
              (later ₒ (enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2))
              =
              later ₕ (commutator ((enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2)) ((enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2)))
              ∘ (backward (later_preserves_prods_nat SI)ₙ
                   (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2, enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2))) as HEQ.
    {
      rewrite right_adj_preserves_prods_backward_comm.
      reflexivity.
    }
    simpl in HEQ; rewrite HEQ; clear HEQ.
    rewrite <-! comp_assoc.
    f_equiv.
    rewrite -h_map_comp.
    rewrite !hom_to_prod_comp_r.
    do 2 f_equiv.
    - rewrite ->!comp_assoc.
      epose proof (comp_assoc (commutator (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2) (enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2))) as HEQ.
      simpl in HEQ; rewrite <-HEQ; clear HEQ.
      rewrite -hom_prod_comp.
      rewrite !hom_to_prod_prj1.
      rewrite commute_hom_prod.
      rewrite -!comp_assoc.
      rewrite (comp_assoc _ _ (enr_comp a.2 b.2 c.2)).
      rewrite commutator_involutive.
      rewrite right_id.
      reflexivity.
    - rewrite ->!comp_assoc.
      f_equiv.
      epose proof (comp_assoc (commutator (enr_hom a.1 b.1 ×ₒ enr_hom a.2 b.2) (enr_hom b.1 c.1 ×ₒ enr_hom b.2 c.2))) as HEQ.
      simpl in HEQ; rewrite <-HEQ; clear HEQ.
      rewrite -hom_prod_comp.
      rewrite !hom_to_prod_prj2.
      rewrite commute_hom_prod.
      reflexivity.
  Qed.
  Next Obligation.
    intros; simpl.
    rewrite !comp_assoc.
    epose proof (comp_assoc (next ₙ term_func (OrdCat SI)ᵒᵖ Typ)
                  (later ₕ << ⌜ id a.1 ⌝, ⌜ id a.2 ⌝ >>)) as Heq.
    rewrite <-Heq; clear Heq.
    rewrite <-h_map_comp.
    rewrite commute_hom_to_prod.
    rewrite -(contr_func_h_map_id F (a.2, a.1)).
    rewrite comp_assoc.
    f_equiv; done.
  Qed.

  Transparent comp.
  Transparent prj1.
  Transparent prj2.
  Transparent later_preserves_prods_nat.

End lc_func_flip_bifunc.

Program Definition iso_cat_prod_left {C D} {a c : obj C} {b d : obj D}
  (HISO : (a, b) ≃@{cat_prod C D} (c, d)) : a ≃ c
  := MkIsoIc (forward HISO).1 (backward HISO).1 _.
Next Obligation.
  intros; split.
  - pose proof (iso_lr (is_iso HISO)).
    simpl.
    destruct (backward HISO).
    destruct (forward HISO).
    simpl in *.
    by inversion H.
  - pose proof (iso_rl (is_iso HISO)).
    simpl.
    destruct (backward HISO).
    destruct (forward HISO).
    simpl in *.
    by inversion H.
Qed.

Program Definition iso_cat_prod_right {C D} {a c : obj C} {b d : obj D}
  (HISO : (a, b) ≃@{cat_prod C D} (c, d)) : b ≃ d
  := MkIsoIc (forward HISO).2 (backward HISO).2 _.
Next Obligation.
  intros; split.
  - pose proof (iso_lr (is_iso HISO)).
    simpl.
    destruct (backward HISO).
    destruct (forward HISO).
    simpl in *.
    by inversion H.
  - pose proof (iso_rl (is_iso HISO)).
    simpl.
    destruct (backward HISO).
    destruct (forward HISO).
    simpl in *.
    by inversion H.
Qed.

Section symmetrization.
  Context {SI : indexT} {C : category}
    `{!Enriched C (PSh (OrdCat SI))}
    `{!LimitsEnriched C}.

  Local Instance : Enriched (C ᵒᵖ) (PSh (OrdCat SI)) := op_enriched_def.
  Local Instance : Enriched (cat_prod (C ᵒᵖ) C) (PSh (OrdCat SI)) :=
    prod_enriched_def.

  Context {sol : ∀ (F : functor
                          (cat_prod (C ᵒᵖ) C)
                          (cat_prod (C ᵒᵖ) C))
                   `{!LocallyContractiveFunctor F},
             solution F}.

  Context {F : functor (cat_prod (C ᵒᵖ) C) C}
    `{LC : !LocallyContractiveFunctor F}.

  Record bifunc_solution :=
    MkBifuncSolution
      {
        bifunc_sol_obj :> obj C;
        bifunc_sol_iso : (F ₒ (bifunc_sol_obj, bifunc_sol_obj))
                           ≃ bifunc_sol_obj;
      }.

  Program Definition symmetrization
    : functor (cat_prod (C ᵒᵖ) C) (cat_prod (C ᵒᵖ) C)
    := functor_to_prod (flip_bifunc F) F.

  Local Program Instance symmetrization_enriched_func
    : EnrichedFunctor symmetrization := _.
  Next Obligation.
    unshelve eapply functor_to_prod_enr_def.
    apply flip_bifunc_enr_def; apply _.
  Qed.

  Local Program Instance symmetrization_locally_contractive
    : LocallyContractiveFunctor symmetrization := _.
  Next Obligation.
    unshelve eapply functor_to_prod_lc_def.
    apply flip_bifunc_lc_def.
  Qed.

  Lemma bifunc_solution_eq (s : obj (C ᵒᵖ)) (s' : obj C)
    (H : (symmetrization ₒ (s, s')) ≃ (s, s')) :
    (symmetrization ₒ (s', s)) ≃@{cat_prod (C ᵒᵖ) C} (s', s).
  Proof.
    assert (H1 : F ₒ (s, s') ≃@{C} s').
    {
      apply (iso_cat_prod_right H).
    }
    assert (H2 : F ₒ (s', s) ≃@{C ᵒᵖ} s).
    {
      apply (iso_cat_prod_left H).
    }
    rewrite /symmetrization //=.
    apply (MkIsoIc
             (((backward H1), (backward H2))
               : hom (C := cat_prod (C ᵒᵖ) C)
                   (F ₒ (s, s'), F ₒ (s', s)) (s', s))
             ((forward H1), (forward H2))).
    apply MkIso.
    - apply injective_projections; simpl.
      + apply (iso_lr (is_iso H1)).
      + apply (iso_lr (is_iso H2)).
    - apply injective_projections; simpl.
      + apply (iso_rl (is_iso H1)).
      + apply (iso_rl (is_iso H2)).
  Qed.

  Lemma bifunc_solution_flip (s : obj (C ᵒᵖ)) (s' : obj C)
    (H : (symmetrization ₒ (s, s')) ≃ (s, s')) :
    (s, s') ≃@{cat_prod (C ᵒᵖ) C} (s', s).
  Proof using LC SI.
    set (MkSolution symmetrization (s, s') H) as X.
    set (MkSolution symmetrization (s', s) (bifunc_solution_eq _ _ H)) as Y.
    apply (solution_unique (SI := SI) symmetrization X Y).
  Qed.

  Lemma bifunc_solution_symmetry (s : obj (C ᵒᵖ)) (s' : obj C)
    (H : (symmetrization ₒ (s, s')) ≃ (s, s')) :
    (symmetrization ₒ (s', s)) ≃@{cat_prod (C ᵒᵖ) C} (symmetrization ₒ (s, s')).
  Proof using LC SI.
    apply @isomorphic_trans with (s', s);
      first apply (bifunc_solution_eq _ _ H).
    apply isomorphic_sym.
    apply @isomorphic_trans with (s, s'); first apply H.
    by apply bifunc_solution_flip.
  Qed.

  Lemma symmetrization_sol `{!LimitsEnriched (cat_prod (C ᵒᵖ) C)}
    : bifunc_solution.
  Proof using LC SI sol.
    set (X := (sol symmetrization _)).
    set (s := sol_obj _ X).
    set (s1 := cat_proj1 _ _ ₒ s).
    set (s2 := cat_proj2 _ _ ₒ s).
    assert (s = (s1, s2)) as HEQ.
    { subst s; destruct (sol_obj symmetrization X); reflexivity. }
    assert (s1 ≃@{C} s2) as HISO.
    {
      assert ((s2, s1) ≃@{cat_prod (C ᵒᵖ) C} (s1, s2)) as HISO.
      {
        apply bifunc_solution_flip.
        apply bifunc_solution_eq.
        rewrite <-HEQ.
        apply (sol_iso _ X).
      }
      apply (iso_cat_prod_right HISO).
    }
    refine {| bifunc_sol_obj := s1 |}.
    {
      assert ((F ₒ (s1, s1), F ₒ (s1, s1)) ≃@{cat_prod (C ᵒᵖ) C} (s1, s1)) as G.
      {
        apply @isomorphic_trans with (F ₒ (s2, s1), F ₒ (s1, s2)).
        - apply (@prod_of_isos (C ᵒᵖ) C).
          + apply iso_op.
            apply (@functor_preserves_iso (cat_prod (C ᵒᵖ) C) C F).
            apply (@prod_of_isos (C ᵒᵖ) C); last apply isomorphic_refl.
            apply iso_op, HISO.
          + apply functor_preserves_iso.
            apply (@prod_of_isos (C ᵒᵖ) C); first apply isomorphic_refl.
            apply HISO.
        - apply @isomorphic_trans with (s1, s2).
          + rewrite <-HEQ.
            apply (sol_iso _ X).
          + apply (@prod_of_isos (C ᵒᵖ) C); first apply isomorphic_refl.
            apply isomorphic_sym.
            apply HISO.
      }
      apply (iso_cat_prod_right G).
    }
  Defined.

  Program Definition bifunc_sol_unary_sol (bs : bifunc_solution)
    : solution symmetrization :=
    MkSolution _ (bifunc_sol_obj bs, bifunc_sol_obj bs) _.
  Next Obligation.
    intros; simpl.
    apply (@prod_of_isos (C ᵒᵖ) C).
    - apply iso_op.
      apply bifunc_sol_iso.
    - apply bifunc_sol_iso.
  Defined.

  Lemma bifunc_sol_unique `{!LimitsEnriched (cat_prod (C ᵒᵖ) C)}
    : ∀ X, F ₒ (X, X) ≃ X → X ≃ bifunc_sol_obj symmetrization_sol.
  Proof.
    intros X HEQ.
    pose proof (solution_unique symmetrization
                  (bifunc_sol_unary_sol (MkBifuncSolution X HEQ))
                  (bifunc_sol_unary_sol
                     (MkBifuncSolution symmetrization_sol
                        (bifunc_sol_iso symmetrization_sol)))) as HI.
    apply (iso_cat_prod_left HI).
  Qed.

End symmetrization.
