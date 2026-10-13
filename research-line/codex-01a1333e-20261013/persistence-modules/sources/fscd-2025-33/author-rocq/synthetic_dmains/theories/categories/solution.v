From SynthDom Require Import prelude.
From SynthDom Require Import stepindex.
From SynthDom.categories Require Import category ord_cat enriched domain.

Set Universe Polymorphism.
Unset Universe Minimization ToSet.

Lemma func_eq_o_map_refl {E D : category} {G : functor E D}
  {Equiv : functor_equiv G G} : ∀ a, func_eq_o_map Equiv a = eq_refl.
Proof.
  intros.
  apply UIP_refl.
Qed.

Lemma func_eq_o_map_sym {E D : category} {G G' : functor E D}
  {Equiv : functor_equiv G G'}
  : ∀ a, eq_sym (func_eq_o_map Equiv a) = func_eq_o_map (symmetry Equiv) a.
Proof.
  intros.
  destruct (functor_equiv_unpack Equiv).
  rewrite func_eq_o_map_refl.
  assert ((symmetry Equiv) = Equiv) as ->.
  { apply proof_irrelevance. }
  rewrite func_eq_o_map_refl.
  apply UIP_refl.
Qed.

Lemma func_eq_o_map_trans {E D : category} {G G' G'' : functor E D}
  {Equiv : functor_equiv G G'} {Equiv' : functor_equiv G' G''}
  : ∀ a, eq_trans (func_eq_o_map Equiv a) (func_eq_o_map Equiv' a)
         = func_eq_o_map (transitivity Equiv Equiv') a.
Proof.
  intros.
  destruct (functor_equiv_unpack Equiv).
  destruct (functor_equiv_unpack Equiv').
  assert (Equiv = Equiv') as ->.
  { apply proof_irrelevance. }
  rewrite func_eq_o_map_refl.
  assert ((transitivity Equiv' Equiv') = Equiv') as ->.
  { apply proof_irrelevance. }
  rewrite func_eq_o_map_refl.
  apply UIP_refl.
Qed.

Lemma car_eq_eq_trans {E : category} {G : functor E E} {a b c : algebra G}
  : ∀ (H : a = b) (G : b = c), car_eq (eq_trans H G) = eq_trans (car_eq H) (car_eq G).
Proof. by intros [] []. Qed.

Lemma car_eq_eq_symm {E : category} {G : functor E E} {a b : algebra G}
  : ∀ (H : a = b), car_eq (eq_sym H) = eq_sym (car_eq H).
Proof. by intros []. Qed.

Lemma func_equiv_compose {E D H : category}
  {G1 G2 : functor E D}
  {J1 J2 : functor D H}
  (Equiv1 : functor_equiv G1 G2)
  (Equiv2 : functor_equiv J1 J2)
  : functor_equiv (functor_compose G1 J1) (functor_compose G2 J2).
Proof.
  destruct (functor_equiv_unpack Equiv1).
  destruct (functor_equiv_unpack Equiv2).
  reflexivity.
Qed.

Record cones_equiv {J C} {F F' : functor J C}
  (Fequiv : functor_equiv F F') (cn : cone F) (cn' : cone F') :=
  MkConesEq {
      cones_eq_vertexes : vertex cn = vertex cn';
      cones_eq_sides :
      ∀ j, side cn' j
           = hom_trans cones_eq_vertexes (func_eq_o_map Fequiv j) (side cn j);
    }.
Arguments MkConesEq {_ _ _ _ _ _ _} _ _.
Arguments cones_eq_vertexes {_ _ _ _ _ _ _} _.
Arguments cones_eq_sides {_ _ _ _ _ _ _} _ _.

Definition cone_trans {J C} {F F' : functor J C}
  (heq : F = F') (cn : cone F) : cone F' :=
  match heq in _ = F' return cone F' with
      eq_refl => cn
  end.

Definition cones_eq {J C} {F F' : functor J C}
  (Fequiv : F = F') (cn : cone F) (cn' : cone F') :=
  cn' = cone_trans Fequiv cn.

Lemma cones_equiv_eq {J C} {F F' : functor J C}
  (Fequiv : functor_equiv F F') (Fequiv' : F = F') (cn : cone F) (cn' : cone F')
  : cones_equiv Fequiv cn cn'
    = (cones_eq Fequiv' cn cn').
Proof.
  apply propositional_extensionality.
  split.
  - intros H.
    destruct Fequiv'.
    rewrite /cones_eq /=.
    destruct cn as [v s p].
    destruct cn' as [v' s' p'].
    assert (v = v') as ->.
    { apply (cones_eq_vertexes H). }
    assert (s = s') as ->.
    {
      apply functional_extensionality_dep.
      intros x.
      pose proof (cones_eq_sides H x) as G.
      simpl in G.
      rewrite G.
      clear.
      assert (func_eq_o_map Fequiv x = eq_refl) as -> by apply proof_irrelevance.
      assert (cones_eq_vertexes H = eq_refl) as -> by apply proof_irrelevance.
      by rewrite hom_trans_refl.
    }
    assert (p = p') as -> by apply proof_irrelevance.
    reflexivity.
  - intros ->.
    destruct Fequiv'.
    apply (MkConesEq eq_refl).
    intros j; simpl.
    assert ((func_eq_o_map Fequiv j) = eq_refl) as -> by apply proof_irrelevance.
    by rewrite hom_trans_refl.
Qed.

Record packed_cones_equiv {J C} {F F' : functor J C} (cn : cone F) (cn' : cone F') :=
  MkPackedConesEquiv {
      packed_cones_equiv_f : functor_equiv F F';
      packed_cones_equiv_c : cones_equiv packed_cones_equiv_f cn cn';
    }.
Arguments MkPackedConesEquiv {_ _ _ _ _ _}.
Arguments packed_cones_equiv_f {_ _ _ _ _ _}.
Arguments packed_cones_equiv_c {_ _ _ _ _ _}.

Lemma cones_equiv_unpack {J C} {F F' : functor J C}
  (Fequiv : functor_equiv F F')
  (cn : cone F) (cn' : cone F') : packed_cones_equiv cn cn' → cones_equiv Fequiv cn cn'.
Proof.
  intros H.
  destruct (functor_equiv_unpack Fequiv).
  rewrite (proof_irrelevance _
             Fequiv (packed_cones_equiv_f H)).
  apply (packed_cones_equiv_c H).
Qed.

Lemma cones_equiv_pack {J C} {F F' : functor J C}
  (Fequiv : functor_equiv F F')
  (cn : cone F) (cn' : cone F') : cones_equiv Fequiv cn cn' → packed_cones_equiv cn cn'.
Proof.
  intros H.
  apply (MkPackedConesEquiv Fequiv).
  apply H.
Qed.

Program Definition packed_cones_equiv_refl {J C} {F : functor J C} (cn : cone F) :
  packed_cones_equiv cn cn :=
  MkPackedConesEquiv (reflexivity _) _.
Next Obligation.
  intros.
  apply (MkConesEq eq_refl).
  intros; by rewrite func_eq_o_map_refl hom_trans_refl.
Qed.

Program Definition packed_cones_equiv_sym {J C} {F F' : functor J C}
  (cn : cone F) (cn' : cone F') (H : packed_cones_equiv cn cn')
  : packed_cones_equiv cn' cn :=
  MkPackedConesEquiv (symmetry (packed_cones_equiv_f H)) _.
Next Obligation.
  intros.
  set (H2 := packed_cones_equiv_f H).
  pose proof (packed_cones_equiv_c H) as H1.
  clearbody H2.
  assert (H2 = packed_cones_equiv_f H) as Hf.
  { apply proof_irrelevance. }
  destruct Hf.
  clear H.
  destruct (functor_equiv_unpack H2).
  rewrite (proof_irrelevance _
             (symmetry H2) H2).
  apply (MkConesEq (eq_sym (cones_eq_vertexes H1))).
  intros j.
  rewrite (cones_eq_sides H1 j).
  rewrite -hom_trans_trans.
  rewrite eq_trans_sym_inv_r.
  rewrite func_eq_o_map_trans.
  rewrite func_eq_o_map_refl.
  rewrite hom_trans_refl.
  reflexivity.
Qed.

Program Definition packed_cones_equiv_trans {J C} {F F' F'' : functor J C}
  (cn : cone F) (cn' : cone F') (cn'' : cone F'')
  (H : packed_cones_equiv cn cn')
  (H' : packed_cones_equiv cn' cn'')
  : packed_cones_equiv cn cn'' :=
  MkPackedConesEquiv
    (transitivity (packed_cones_equiv_f H) (packed_cones_equiv_f H')) _.
Next Obligation.
  intros.
  set (H2 := packed_cones_equiv_f H).
  pose proof (packed_cones_equiv_c H) as H1.
  clearbody H2.
  assert (H2 = packed_cones_equiv_f H) as Hf.
  { apply proof_irrelevance. }
  destruct Hf.
  clear H.
  set (H4 := packed_cones_equiv_f H').
  pose proof (packed_cones_equiv_c H') as H3.
  clearbody H4.
  assert (H4 = packed_cones_equiv_f H') as Hf.
  { apply proof_irrelevance. }
  destruct Hf.
  clear H'.
  destruct (functor_equiv_unpack H2).
  destruct (functor_equiv_unpack H4).
  rewrite (proof_irrelevance _
             (transitivity _ _) (reflexivity _)).
  apply (MkConesEq (eq_trans (cones_eq_vertexes H1) (cones_eq_vertexes H3))).
  intros j.
  rewrite (cones_eq_sides H3 j).
  rewrite !func_eq_o_map_refl.
  rewrite (cones_eq_sides H1 j).
  rewrite !func_eq_o_map_refl.
  rewrite -hom_trans_trans.
  f_equal.
Qed.

Lemma alg_hom_map_prop_eq {C : category} {T : functor C C} {A B : algebra T} (f g : alg_hom A B) :
  alg_hom_map f = alg_hom_map g → f = g.
Proof.
  intros H.
  by apply alg_hom_map_eq.
Qed.

Lemma alg_hom_map_prop_eq' {C : category} {T : functor C C} {A B : algebra T} (f g : alg_hom A B) :
  f = g → alg_hom_map f = alg_hom_map g.
Proof.
  intros H.
  destruct H.
  reflexivity.
Qed.

Program Definition iso_alg_hom_map {D} (G : functor D D)
  (a b : obj (Alg G)) (i : hom a b) (j : hom b a)
  (H : isomorphism i j) : isomorphism (alg_hom_map i) (alg_hom_map j)
  := MkIso
       _
       _.
Next Obligation.
  intros; simpl.
  by rewrite -alg_hom_map_comp (iso_lr H).
Qed.
Next Obligation.
  intros; simpl.
  by rewrite -alg_hom_map_comp (iso_rl H).
Qed.

Program Definition alg_func_on_alg_iso_cong {D} (G : functor D D)
  (a b : algebra G) (i : a ≃@{Alg G} b)
  : alg_func_on_alg a ≃@{Alg G} alg_func_on_alg b
  := MkIsoIc
       (MkAlgHom (G ₕ (alg_hom_map (forward i))) _)
       (MkAlgHom (G ₕ (alg_hom_map (backward i))) _)
       (MkIso _ _).
Next Obligation.
  intros; simpl.
  by rewrite -!h_map_comp alg_hom_commutes.
Qed.
Next Obligation.
  intros; simpl.
  by rewrite -!h_map_comp alg_hom_commutes.
Qed.
Next Obligation.
  intros; simpl.
  apply alg_hom_map_eq; simpl.
  rewrite -h_map_comp.
  rewrite iso_lr; first by rewrite h_map_id.
  apply iso_alg_hom_map, i.
Qed.
Next Obligation.
  intros; simpl.
  apply alg_hom_map_eq; simpl.
  rewrite -h_map_comp.
  rewrite iso_rl; first by rewrite h_map_id.
  apply iso_alg_hom_map, i.
Qed.

Program Definition alg_lim_alg_iso_cong {D} `{Complete D} {T : functor D D}
  {J : category}
  (I I' : functor J (Alg T)) (i : I ≃@{FuncCat _ _} I')
  : alg_lim_alg I ≃@{Alg _} alg_lim_alg I'
  := eq_cones_vertexes (limit_of_isos_equiv_cones i (alg_lim _) (alg_lim _)).

Lemma functor_equiv_lim {J D} `{!Complete D} {I I' : functor J D}
  (eq : functor_equiv I I')
  : cones_equiv eq
      (term (complete I))
      (term (complete I')).
Proof.
  epose proof (functor_equiv_unpack eq).
  destruct H.
  apply (MkConesEq eq_refl).
  intros H; simpl.
  rewrite (UIP_refl _ _ (func_eq_o_map eq H)).
  reflexivity.
Qed.

Lemma alg_lim_alg_equiv_cong {D} `{Complete D} {T : functor D D}
  {J : category}
  {I I' : functor J (Alg T)} (i : functor_equiv I I')
  : (alg_lim_alg I) = (alg_lim_alg I').
Proof.
  destruct (functor_equiv_unpack i).
  reflexivity.
Qed.

Opaque later next.

Section solution.
  Context {SI : indexT} {C : category} `{!Complete C}
    `{!Enriched C (PSh (OrdCat SI))} `{!LimitsEnriched C}
    (F : functor C C) `{!LocallyContractiveFunctor F}.

  Definition dsp_included_refl {dsp : downset_pred SI} : dsp_included dsp dsp
    := λ _ P, P.

  Definition dsp_included_lt_le {α : SI} : dsp_included (lt_dsp α) (le_dsp α)
    := λ β P, index_lt_le_subrel _ _ P.

  Program Definition dsp_included_trans {dsp dsp' dsp'' : downset_pred SI} :
    dsp_included dsp dsp' → dsp_included dsp' dsp'' → dsp_included dsp dsp''
    := λ H G β P, (G _ (H _ P)).

  Definition dsp_le_top (α : SI) : downset (le_dsp α)
    := MkDS (le_dsp α) (squash (reflexivity _)).

  (* An F-algebra whose constructor map is α-iso for all α is the solution. *)
  Definition alg_cons_is_iso_upto_total_solution {A : algebra F}
    (iso : is_iso_upto (cons A) (total_dsp SI)) : (solution F) :=
    MkSolution _ (car A) (is_iso_upto_total (cons A) iso).

  (* Now, we will construct such an algebra. *)

  Record partial_solution (dsp: downset_pred SI) := MkParSol {
    parsol_func :> functor ((OrdDSCat dsp)ᵒᵖ) (Alg F);
    parsol_edge_iso : ∀ (α β : downset dsp) (Hle : β ⪯ α),
      is_iso_at (alg_hom_map (parsol_func ₕ Hle)) β;
    parsol_cons_iso : ∀ (α : downset dsp), is_iso_at (cons (parsol_func ₒ α)) α;
  }.
  Arguments MkParSol {_} _ _ _.
  Arguments parsol_func {_} _.
  Arguments parsol_edge_iso {_} _ [_ _] _.
  Arguments parsol_cons_iso {_} _ _.

  Record par_sol_extension {dsp} (ps : partial_solution dsp) := MkParSolExt {
    parsolext_cone :> cone ps;
    parsolext_side_iso : ∀ (α : downset dsp),
      is_iso_at (alg_hom_map (side parsolext_cone α)) α;
    parsolext_cons_iso : ∀ (α : SI),
      (∀ β, β ≺ α → dsp β) → is_iso_at (cons (vertex parsolext_cone)) α;
  }.
  Arguments MkParSolExt {_ _} _ _.
  Arguments parsolext_cone {_ _} _.
  Arguments parsolext_side_iso {_ _} _ _.
  Arguments parsolext_cons_iso {_ _} _ _.

  Program Definition apply_par_sol_extension {α} {ps : partial_solution (lt_dsp α)}
    (pse : par_sol_extension ps) : partial_solution (le_dsp α) :=
    MkParSol (extend_ord_ds_cat_func pse) _ _.
  Next Obligation.
    intros α ps pse β γ Hle; simpl.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))) as [Hltβ|Heqβ];
      destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp γ))) as [Hltγ|Heqγ];
      simplify_extend_ord_ds_cat_func_h_map.
    - eapply is_iso_at_proper; last by rewrite hom_trans_alg_hom_map.
      apply iso_at_hom_trans, (parsol_edge_iso ps).
    - eapply is_iso_at_proper; last by rewrite hom_trans_alg_hom_map.
      apply iso_at_hom_trans, (parsolext_side_iso pse).
    - eapply is_iso_at_proper; last by rewrite hom_trans_alg_hom_map.
      apply iso_at_hom_trans, is_iso_at_id.
  Qed.
  Next Obligation.
    intros α ps pse β; simpl.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))) as [Hltβ|Heqβ].
    - rewrite extend_ord_ds_cat_func_o_map_lt.
      apply (parsol_cons_iso ps).
    - rewrite extend_ord_ds_cat_func_o_map_at // Heqβ.
      apply parsolext_cons_iso; done.
  Qed.
  Fail Next Obligation.

  Program Definition extend_partial_solution_iso {α} {ps ps' : partial_solution (lt_dsp α)}
    (psiso : ps ≃@{FuncCat ((OrdDSCat (lt_dsp α))ᵒᵖ) (Alg F)} ps')
    {pse : par_sol_extension ps} {pse' : par_sol_extension ps'}
    (pseseq : equiv_cones psiso pse pse') :
    apply_par_sol_extension pse ≃@{FuncCat ((OrdDSCat (le_dsp α))ᵒᵖ) (Alg F)}
    apply_par_sol_extension pse' :=
    MkIsoIc
      (extend_ord_ds_cat_nat (forward psiso) (forward (eq_cones_vertexes pseseq))
         (eq_cones_sides pseseq))
      (extend_ord_ds_cat_nat (backward psiso) (backward (eq_cones_vertexes pseseq))
         (eq_cones_sides' pseseq))
      _.
  Next Obligation.
  intros α ps ps' psiso pse pse' pseseq; split; simpl in *.
  - apply natural_equiv_unpack.
    intros β; simpl.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))) as [Hltβ|Heqβ].
    + rewrite !(extend_ord_ds_cat_nat_map_lt _ _ Hltβ) /=.
      apply alg_hom_map_eq; simpl.
      rewrite !hom_trans_alg_hom_map.
      rewrite hom_trans_compose_take_in_l /= -hom_trans_trans.
      rewrite !eq_trans_sym_inv_r !eq_trans_refl_r.
      rewrite hom_trans_compose_take_in_r /= -hom_trans_trans.
      rewrite !eq_trans_refl_l !eq_trans_refl_r !hom_trans_refl /=.
      pose proof (natural_equiv_pack (iso_lr (is_iso psiso)) (MkDS (lt_dsp α) (squash Hltβ))) as Hlr;
        apply alg_hom_map_eq' in Hlr; simpl in Hlr; rewrite Hlr; clear Hlr.
      rewrite hom_trans_id //.
    + rewrite !(extend_ord_ds_cat_nat_map_at _ _ Heqβ) /=.
      apply alg_hom_map_eq; simpl.
      rewrite !hom_trans_alg_hom_map.
      rewrite hom_trans_compose_take_in_l /= -hom_trans_trans.
      rewrite !eq_trans_sym_inv_r !eq_trans_refl_r.
      rewrite hom_trans_compose_take_in_r /= -hom_trans_trans.
      rewrite !eq_trans_refl_l !eq_trans_refl_r !hom_trans_refl /=.
      pose proof iso_lr (is_iso (eq_cones_vertexes pseseq)) as Hlr;
        apply alg_hom_map_eq' in Hlr; simpl in Hlr; rewrite Hlr; clear Hlr.
      rewrite hom_trans_id //.
  - apply natural_equiv_unpack.
    intros β; simpl.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp β))) as [Hltβ|Heqβ].
    + rewrite !(extend_ord_ds_cat_nat_map_lt _ _ Hltβ) /=.
      apply alg_hom_map_eq; simpl.
      rewrite !hom_trans_alg_hom_map.
      rewrite hom_trans_compose_take_in_l /= -hom_trans_trans.
      rewrite !eq_trans_sym_inv_r !eq_trans_refl_r.
      rewrite hom_trans_compose_take_in_r /= -hom_trans_trans.
      rewrite !eq_trans_refl_l !eq_trans_refl_r !hom_trans_refl /=.
      pose proof (natural_equiv_pack (iso_rl (is_iso psiso)) (MkDS (lt_dsp α) (squash Hltβ))) as Hlr;
        apply alg_hom_map_eq' in Hlr; simpl in Hlr; rewrite Hlr; clear Hlr.
      rewrite hom_trans_id //.
    + rewrite !(extend_ord_ds_cat_nat_map_at _ _ Heqβ) /=.
      apply alg_hom_map_eq; simpl.
      rewrite !hom_trans_alg_hom_map.
      rewrite hom_trans_compose_take_in_l /= -hom_trans_trans.
      rewrite !eq_trans_sym_inv_r !eq_trans_refl_r.
      rewrite hom_trans_compose_take_in_r /= -hom_trans_trans.
      rewrite !eq_trans_refl_l !eq_trans_refl_r !hom_trans_refl /=.
      pose proof (iso_rl (is_iso (eq_cones_vertexes pseseq))) as Hlr;
        apply alg_hom_map_eq' in Hlr; simpl in Hlr; rewrite Hlr; clear Hlr.
      rewrite hom_trans_id //.
  Qed.
  Fail Next Obligation.

  Program Definition the_extension {dsp} (ps : partial_solution dsp) : par_sol_extension ps :=
    MkParSolExt (alg_func_on_cone (term (complete ps))) _ _.
  Next Obligation.
    intros ? ps α; rewrite /=.
    apply is_iso_at_compose; last apply parsol_cons_iso.
    apply (is_iso_at_func F).
    rewrite -(ic_side_limiting_cone_is_limit _ _
      (term_is_terminal (complete (functor_compose ps (forgetful F))))).
    apply (limit_side_iso_at_cofinal
             (limiting_cone_is_limit
                (term_is_terminal (complete (functor_compose ps (forgetful F)))))
             α (unsquash (ds_in_dsp α))); last done.
    intros; simpl.
    eapply is_iso_at_downwards; last by apply parsol_edge_iso.
    done.
  Qed.
  Next Obligation.
    intros ? ps α Hdsp; simpl.
    eapply (iso_upto_contr_func F); last by apply Hdsp.
    intros β.
    assert (is_iso_at (side (term (complete (functor_compose ps (forgetful F)))) β) β) as Hiso.
    { rewrite -(ic_side_limiting_cone_is_limit _ _
        (term_is_terminal (complete (functor_compose ps (forgetful F))))).
      apply (limit_side_iso_at_cofinal
             (limiting_cone_is_limit
                (term_is_terminal (complete (functor_compose ps (forgetful F)))))
             β (unsquash (ds_in_dsp β))); last done.
      intros; simpl.
      eapply is_iso_at_downwards; last by apply parsol_edge_iso.
      done. }
    eapply is_iso_at_uncompose_r; first apply Hiso.
    eapply is_iso_at_proper; last by rewrite_cone_hom_commutes_back; reflexivity.
    simpl.
    apply is_iso_at_compose; last apply parsol_cons_iso.
    apply (is_iso_at_func F).
    done.
  Qed.
  Fail Next Obligation.

  Program Definition total_partial_sol_sol
    (ps : partial_solution (total_dsp SI))
    : solution F :=
    MkSolution F
      (car (vertex (the_extension ps)))
      (is_iso_upto_total (cons (vertex (the_extension ps)))
         (λ α, (parsolext_cons_iso (the_extension ps) α (λ _ _, I)))).

  Definition the_extension_eq_cones {α} {ps ps' : partial_solution (lt_dsp α)}
    (psiso : ps ≃@{FuncCat ((OrdDSCat (lt_dsp α))ᵒᵖ) (Alg F)} ps') :
    equiv_cones psiso (the_extension ps) (the_extension ps') :=
    alg_func_on_eq_cones (limit_of_isos_equiv_cones psiso (complete ps) (complete ps')).

  Definition extend_par_sol_lt_le {α} (ps : partial_solution (lt_dsp α)) :
    partial_solution (le_dsp α) :=
    apply_par_sol_extension (the_extension ps).

  Definition extend_par_sol_lt_le_iso {α} {ps ps' : partial_solution (lt_dsp α)}
    (psiso : ps ≃@{FuncCat ((OrdDSCat (lt_dsp α))ᵒᵖ) (Alg F)} ps') :
    extend_par_sol_lt_le ps ≃@{FuncCat ((OrdDSCat (le_dsp α))ᵒᵖ) (Alg F)}
    extend_par_sol_lt_le ps' :=
    extend_partial_solution_iso psiso (the_extension_eq_cones psiso).

  Definition cut_ord_ds_cat_func_trivial {dsp : downset_pred SI}
    (P : partial_solution dsp)
    : ∀ a : downset dsp,
    P ₒ a
    = P ₒ dsp_include (le_dsp_included a) (dsp_le_top a)
  := λ _, eq_refl.

  Lemma cut_ord_ds_cat_func_trivial_refl {dsp : downset_pred SI}
    {P : partial_solution dsp} : ∀ a, (cut_ord_ds_cat_func_trivial P a = eq_refl).
  Proof. intros; reflexivity. Qed.

  Program Definition cut_par_sol {dsp} (ps : partial_solution dsp)
    {dsp' : downset_pred SI}
    (Hdsps : dsp_included dsp' dsp) : partial_solution dsp' :=
    MkParSol (cut_ord_ds_cat_func dsp' Hdsps ps) _ _.
  Next Obligation.
    intros ? ps ?????.
    rewrite /cut_ord_ds_cat_func /= /cut_ord_ds_cat_func_h_map.
    apply (parsol_edge_iso ps).
  Qed.
  Next Obligation.
    intros ? ps ???.
    rewrite /cut_ord_ds_cat_func /= /cut_ord_ds_cat_func_h_map.
    apply (parsol_cons_iso ps).
  Qed.
  Fail Next Obligation.

  Program Definition par_sol_extensional {dsp : downset_pred SI}
    (P Q : partial_solution dsp)
    (eqs : ∀ α : downset dsp,
       functor_equiv
         (cut_ord_ds_cat_func _ (le_dsp_included α) P)
         (cut_ord_ds_cat_func _ (le_dsp_included α) Q))
    : functor_equiv P Q
    := MkFuncEq
         (λ a, eq_trans
                 (eq_trans
                    (cut_ord_ds_cat_func_trivial P a)
                    (func_eq_o_map (eqs a) (dsp_le_top a)))
                 (eq_sym (cut_ord_ds_cat_func_trivial Q a)))
         _.
  Next Obligation.
    intros dsp P Q eqs α β f; simpl.
    rewrite !hom_trans_trans.
    symmetry.
    rewrite !cut_ord_ds_cat_func_trivial_refl.
    rewrite hom_trans_refl.
    epose proof (λ δ γ g, func_eq_h_map (eqs α) (a := δ) (b := γ) g) as HEQ.
    rewrite /= /cut_ord_ds_cat_func_h_map /= in HEQ.
    match goal with
    | |- context G [_ ₕ ?a = _] =>
        set (f' := a)
    end.
    simpl in f'.
    assert (f' = f) as ->.
    { apply proof_irrel. }
    simpl in f.
    rewrite -(HEQ
                (dsp_le_top α)
                  (MkDS (le_dsp α) (squash f))
                  f).
    f_equiv; last done.
    apply ProofIrrelevance.proof_irrelevance.
  Qed.

  Record compat_iso_fam {dsp : downset_pred SI}
    (P Q : partial_solution dsp)
    := MkCompatIsoFam {
           iso_fam : ∀ a : downset dsp,
             isomorphic (C := FuncCat _ _)
               (cut_ord_ds_cat_func _ (le_dsp_included a) P)
               (cut_ord_ds_cat_func _ (le_dsp_included a) Q);
           iso_fam_compat_forward : ∀ (a b : downset dsp) (f : le_dsp b a),
             forward (iso_fam a) ₙ (dsp_le_top a)
               = forward (iso_fam b) ₙ (MkDS (le_dsp b)
                                          (squash f));
           iso_fam_compat_backward : ∀ (a b : downset dsp) (f : le_dsp b a),
             backward (iso_fam a) ₙ (dsp_le_top a)
               = backward (iso_fam b) ₙ (MkDS (le_dsp b)
                                           (squash f));
         }.

  Program Definition par_sol_extensional_iso {dsp : downset_pred SI}
    (P Q : partial_solution dsp)
    (eqs : compat_iso_fam P Q)
    : isomorphic (C := FuncCat _ _) P Q
    := MkIsoIc
         (MkNat (λ β, (forward (iso_fam _ _ eqs β) ₙ
                         (dsp_le_top β))) _)
         (MkNat (λ β, (backward (iso_fam _ _ eqs β) ₙ
                         (dsp_le_top β))) _)
         _.
  Next Obligation.
    intros; simpl.
    simpl in f.
    epose proof (@naturality _ _ _ _ (forward (iso_fam _ _ eqs a))
                   (dsp_le_top a)
                   (MkDS (le_dsp a) (squash f)) f) as H.
    simpl in H.
    rewrite -H; clear H.
    f_equiv.
    match goal with
    | |- context G [MkDS ?a ?b] =>
        set (T := MkDS a b)
    end.
    apply (iso_fam_compat_forward _ _ eqs b).
  Qed.
  Next Obligation.
    intros; simpl.
    simpl in f.
    epose proof (@naturality _ _ _ _ (backward (iso_fam _ _ eqs a))
                   (dsp_le_top a)
                   (MkDS (le_dsp a) (squash f)) f) as H.
    simpl in H.
    rewrite -H; clear H.
    f_equiv.
    apply (iso_fam_compat_backward _ _ eqs b).
  Qed.
  Next Obligation.
    intros; simpl.
    split.
    - apply natural_equiv_unpack.
      intros ?; simpl.
      pose proof (natural_equiv_pack (iso_lr (is_iso (iso_fam _ _ eqs a)))
                    (dsp_le_top a)) as H.
      simpl in H.
      rewrite H; clear H.
      reflexivity.
    - apply natural_equiv_unpack.
      intros ?; simpl.
      pose proof (natural_equiv_pack (iso_rl (is_iso (iso_fam _ _ eqs a)))
                    (dsp_le_top a)) as H.
      simpl in H.
      rewrite H; clear H.
      reflexivity.
  Qed.

  Opaque comp id.
  Program Definition extend_par_sol_lt_le_iso_lt {α}
    (ps : partial_solution (lt_dsp α))
    (H : dsp_included (lt_dsp α) (le_dsp α))
    : isomorphic (C := FuncCat _ _)
        (cut_par_sol (extend_par_sol_lt_le ps) H)
        ps
    := MkIsoIc
         (MkNat (λ c,
            (hom_trans
               eq_refl
               (extend_ord_ds_cat_func_o_map_lt
                  (β := (dsp_include H c))
                  (alg_func_on_cone (alg_lim_cone ps)) (unsquash (ds_in_dsp c)))
               (id _))) _)
         (MkNat (λ c,
            (hom_trans
               (extend_ord_ds_cat_func_o_map_lt
                  (β := (dsp_include H c))
                  (alg_func_on_cone (alg_lim_cone ps)) (unsquash (ds_in_dsp c)))
               eq_refl
               (id _))) _)
         _.
  Next Obligation.
    intros α ps H.
    intros β γ Hle; simpl in *.
    rewrite !hom_trans_compose_take_in_l.
    rewrite right_id.
    rewrite hom_trans_refl.
    rewrite !hom_trans_compose_take_in_r.
    rewrite left_id.
    rewrite -!hom_trans_trans eq_trans_refl_r eq_trans_refl_l.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp (dsp_include H β)))) as [Hltβ|Heqβ];
      destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp (dsp_include H γ)))) as [Hltγ|Heqγ];
      repeat simplify_extend_ord_ds_cat_func_h_map.
    - rewrite -!hom_trans_trans eq_trans_refl_r.
      f_equiv; last reflexivity.
      + apply proof_irrelevance.
      + apply proof_irrelevance.
    - exfalso.
      eapply index_lt_le_contradict; first apply (unsquash (ds_in_dsp β)).
      rewrite Heqβ; reflexivity.
    - exfalso.
      eapply index_lt_le_contradict; first apply (unsquash (ds_in_dsp β)).
      rewrite Heqβ; reflexivity.
  Qed.
  Next Obligation.
    intros α ps H.
    intros β γ Hle; simpl in *.
    rewrite !hom_trans_compose_take_in_l.
    rewrite right_id.
    rewrite hom_trans_refl.
    rewrite !hom_trans_compose_take_in_r.
    rewrite left_id.
    rewrite -!hom_trans_trans eq_trans_refl_l eq_trans_refl_r.
    destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp (dsp_include H β)))) as [Hltβ|Heqβ];
      destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp (dsp_include H γ)))) as [Hltγ|Heqγ];
      repeat simplify_extend_ord_ds_cat_func_h_map.
    - rewrite -!hom_trans_trans eq_trans_refl_r.
      f_equiv; last reflexivity.
      + apply proof_irrelevance.
      + apply proof_irrelevance.
    - exfalso.
      eapply index_lt_le_contradict; first apply (unsquash (ds_in_dsp β)).
      rewrite Heqβ; reflexivity.
    - exfalso.
      eapply index_lt_le_contradict; first apply (unsquash (ds_in_dsp β)).
      rewrite Heqβ; reflexivity.
  Qed.
  Transparent comp id.
  Next Obligation.
    intros; simpl; split.
    - apply natural_equiv_unpack.
      intros ?; simpl.
      apply alg_hom_map_eq; simpl.
      rewrite !hom_trans_alg_hom_map /=.
      rewrite !hom_trans_compose_take_in_l.
      rewrite -!hom_trans_trans !eq_trans_sym_inv_r.
      rewrite !hom_trans_refl.
      rewrite left_id.
      reflexivity.
    - apply natural_equiv_unpack.
      intros ?; simpl.
      apply alg_hom_map_eq; simpl.
      rewrite !hom_trans_alg_hom_map /=.
      rewrite !hom_trans_compose_take_in_l.
      rewrite -!hom_trans_trans !eq_trans_sym_inv_r eq_trans_refl_r.
      rewrite !hom_trans_compose_take_in_r.
      rewrite -!hom_trans_trans !eq_trans_refl_r /= !hom_trans_refl.
      rewrite eq_trans_refl_l.
      rewrite left_id.
      rewrite hom_trans_id.
      reflexivity.
  Qed.

  Program Definition cut_partial_solution_equiv
    {dsp dsp'} {ps ps' : partial_solution dsp}
    (H : dsp_included dsp' dsp)
    (psequiv : functor_equiv ps ps')
    : functor_equiv
        (cut_par_sol ps H)
        (cut_par_sol ps' H)
    := MkFuncEq
         (λ a, func_eq_o_map psequiv (dsp_include H a))
         _.
  Next Obligation.
    intros; simpl.
    unfold cut_ord_ds_cat_func_h_map.
    rewrite func_eq_h_map.
    reflexivity.
  Qed.

  Program Definition extend_par_sol_lt_le_equiv_lt {α}
    (ps : partial_solution (lt_dsp α))
    (H : dsp_included (lt_dsp α) (le_dsp α))
    : functor_equiv
        (cut_par_sol (extend_par_sol_lt_le ps) H)
        ps :=
    MkFuncEq (λ a, (extend_ord_ds_cat_func_o_map_lt (alg_func_on_cone (alg_lim_cone ps))
                      (β := dsp_include H a) (unsquash (ds_in_dsp a)))) _.
  Next Obligation.
    intros; simpl.
    rewrite (extend_ord_ds_cat_func_h_map_lt_lt (alg_func_on_cone (alg_lim_cone ps))).
    { apply (unsquash (ds_in_dsp a)). }
    { apply (unsquash (ds_in_dsp b)). }
    intros J1 J2.
    rewrite -!hom_trans_trans.
    assert (J1 = unsquash (ds_in_dsp a)) as -> by apply proof_irrelevance.
    assert (J2 = unsquash (ds_in_dsp b)) as -> by apply proof_irrelevance.
    rewrite !eq_trans_sym_inv_l.
    rewrite hom_trans_refl.
    reflexivity.
  Qed.

  Program Definition extend_partial_solution_equiv
    {α : SI} {ps ps' : partial_solution (lt_dsp α)}
    (H : dsp_included (lt_dsp α) (le_dsp α))
    (psequiv : functor_equiv ps ps')
    : functor_equiv
        (cut_par_sol (extend_par_sol_lt_le ps) H)
        (cut_par_sol (extend_par_sol_lt_le ps') H)
    := transitivity (extend_par_sol_lt_le_equiv_lt ps H)
         (transitivity psequiv
            (symmetry (extend_par_sol_lt_le_equiv_lt ps' H))).

  Lemma extend_par_sol_lt_le_iso_lt_fwd_pointwise {α}
    (ps : partial_solution (lt_dsp α))
    (H : dsp_included (lt_dsp α) (le_dsp α))
    : ∀ (β : downset (lt_dsp α)),
    forward (extend_par_sol_lt_le_iso_lt ps H) ₙ β =
      hom_trans
      eq_refl
      (extend_ord_ds_cat_func_o_map_lt
         (β := (dsp_include H β))
         (alg_func_on_cone (alg_lim_cone ps)) (unsquash (ds_in_dsp β)))
      (id _).
  Proof.
    intros; simpl.
    reflexivity.
  Qed.

  Lemma extend_par_sol_lt_le_iso_fwd_pointwise {α}
    (ps ps' : partial_solution (lt_dsp α))
    (H : dsp_included (lt_dsp α) (le_dsp α))
    (Hiso : ps ≃@{FuncCat _ _} ps')
    (β : downset (lt_dsp α))
    : (hom_trans
             (extend_ord_ds_cat_func_o_map_lt
                (β := (dsp_include H β))
                (alg_func_on_cone (alg_lim_cone ps)) (unsquash (ds_in_dsp β)))
             (extend_ord_ds_cat_func_o_map_lt
                (β := (dsp_include H β))
                (alg_func_on_cone (alg_lim_cone ps')) (unsquash (ds_in_dsp β)))
             (forward (extend_par_sol_lt_le_iso Hiso) ₙ (dsp_include H β)))
        = (forward Hiso ₙ β).
  Proof.
    simpl.
    unshelve rewrite extend_ord_ds_cat_nat_map_lt.
    { apply (unsquash (ds_in_dsp β)). }
    intros T.
    replace T with (unsquash (ds_in_dsp β)); last apply proof_irrel.
    rewrite -!hom_trans_trans.
    rewrite !eq_trans_sym_inv_l.
    rewrite hom_trans_refl.
    reflexivity.
  Qed.

  Lemma extend_par_sol_lt_le_iso_bwd_pointwise {α}
    (ps ps' : partial_solution (lt_dsp α))
    (H : dsp_included (lt_dsp α) (le_dsp α))
    (Hiso : ps ≃@{FuncCat _ _} ps')
    (β : downset (lt_dsp α))
    : (hom_trans
             (extend_ord_ds_cat_func_o_map_lt
                (β := (dsp_include H β))
                (alg_func_on_cone (alg_lim_cone ps')) (unsquash (ds_in_dsp β)))
             (extend_ord_ds_cat_func_o_map_lt
                (β := (dsp_include H β))
                (alg_func_on_cone (alg_lim_cone ps)) (unsquash (ds_in_dsp β)))
             (backward (extend_par_sol_lt_le_iso Hiso) ₙ (dsp_include H β)))
        = (backward Hiso ₙ β).
  Proof.
    simpl.
    unshelve rewrite extend_ord_ds_cat_nat_map_lt.
    { apply (unsquash (ds_in_dsp β)). }
    intros T.
    replace T with (unsquash (ds_in_dsp β)); last apply proof_irrel.
    rewrite -!hom_trans_trans.
    rewrite !eq_trans_sym_inv_l.
    rewrite hom_trans_refl.
    reflexivity.
  Qed.

  Lemma extend_par_sol_lt_le_iso_bwd_pointwise' {α}
    (ps ps' : partial_solution (lt_dsp α))
    (H : dsp_included (lt_dsp α) (le_dsp α))
    (Hiso : ps ≃@{FuncCat _ _} ps')
    (β : downset (lt_dsp α))
    : backward (extend_par_sol_lt_le_iso Hiso) ₙ (dsp_include H β)
        = hom_trans
             (eq_sym (extend_ord_ds_cat_func_o_map_lt
                (β := (dsp_include H β))
                (alg_func_on_cone (alg_lim_cone ps')) (unsquash (ds_in_dsp β))))
             (eq_sym (extend_ord_ds_cat_func_o_map_lt
                (β := (dsp_include H β))
                (alg_func_on_cone (alg_lim_cone ps)) (unsquash (ds_in_dsp β))))
             (backward Hiso ₙ β).
  Proof.
    simpl.
    unshelve rewrite extend_ord_ds_cat_nat_map_lt.
    { apply (unsquash (ds_in_dsp β)). }
    intros T.
    replace T with (unsquash (ds_in_dsp β)); last apply proof_irrel.
    f_equiv.
    reflexivity.
  Qed.

  Lemma extend_par_sol_lt_le_iso_fwd_pointwise' {α}
    (ps ps' : partial_solution (lt_dsp α))
    (H : dsp_included (lt_dsp α) (le_dsp α))
    (Hiso : ps ≃@{FuncCat _ _} ps')
    (β : downset (lt_dsp α))
    : forward (extend_par_sol_lt_le_iso Hiso) ₙ (dsp_include H β)
        = hom_trans
             (eq_sym (extend_ord_ds_cat_func_o_map_lt
                (β := (dsp_include H β))
                (alg_func_on_cone (alg_lim_cone ps)) (unsquash (ds_in_dsp β))))
             (eq_sym (extend_ord_ds_cat_func_o_map_lt
                (β := (dsp_include H β))
                (alg_func_on_cone (alg_lim_cone ps')) (unsquash (ds_in_dsp β))))
             (forward Hiso ₙ β).
  Proof.
    simpl.
    unshelve rewrite extend_ord_ds_cat_nat_map_lt.
    { apply (unsquash (ds_in_dsp β)). }
    intros T.
    replace T with (unsquash (ds_in_dsp β)); last apply proof_irrel.
    f_equiv.
    reflexivity.
  Qed.

  Lemma extend_par_sol_lt_le_iso_lt_bwd_pointwise {α}
    (ps : partial_solution (lt_dsp α))
    (H : dsp_included (lt_dsp α) (le_dsp α))
    : ∀ (β : downset (lt_dsp α)),
    backward (extend_par_sol_lt_le_iso_lt ps H) ₙ β =
      hom_trans
      (extend_ord_ds_cat_func_o_map_lt
         (β := (dsp_include H β))
         (alg_func_on_cone (alg_lim_cone ps)) (unsquash (ds_in_dsp β)))
      eq_refl
      (id _).
  Proof.
    intros; simpl.
    reflexivity.
  Qed.

  Program Definition partial_sol_cone_at {dsp} (ps : partial_solution dsp)
    (α : downset dsp) : cone (cut_par_sol ps (lt_dsp_included α))
    := MkCone (parsol_func ps ₒ α)
         (λ j, MkAlgHom
                 ((alg_hom_map
                     (ps ₕ index_lt_le_subrel j α
                        (unsquash (ds_in_dsp j))))) _) _.
  Next Obligation.
    intros; simpl.
    reflexivity.
  Defined.
  Next Obligation.
    intros; simpl.
    rewrite alg_hom_commutes.
    reflexivity.
  Qed.
  Next Obligation.
    intros; simpl.
    apply alg_hom_map_eq; simpl.
    unfold cut_ord_ds_cat_func_h_map.
    rewrite -alg_hom_map_comp.
    rewrite -h_map_comp.
    do 2 f_equiv.
    apply proof_irrel.
  Qed.

  Lemma iso_forward_trans {D : category} {a b c : obj D}
    (H1 : a ≃ b) (H2 : b ≃ c) :
    forward (isomorphic_trans H1 H2)
      = (forward H2) ∘ (forward H1).
  Proof. reflexivity. Qed.

  Lemma iso_backward_trans {D : category} {a b c : obj D}
    (H1 : a ≃ b) (H2 : b ≃ c) :
    backward (isomorphic_trans H1 H2)
      = (backward H1) ∘ (backward H2).
  Proof. reflexivity. Qed.

  Lemma iso_forward_sym {D : category} {a b : obj D}
    (H : a ≃ b) :
    forward (isomorphic_sym H)
      = backward H.
  Proof. reflexivity. Qed.

  Lemma iso_backward_sym {D : category} {a b : obj D}
    (H : a ≃ b) :
    backward (isomorphic_sym H)
      = forward H.
  Proof. reflexivity. Qed.

  Lemma iso_backward_equiv {D E : category} {a b : functor D E}
    (H : functor_equiv a b) x
    : backward (functor_eq_natural_iso H) ₙ x
        = hom_trans (func_eq_o_map H _) eq_refl (id _).
  Proof.
    unfold functor_eq_natural_iso.
    simpl.
    destruct (func_eq_o_map H x).
    reflexivity.
  Qed.

  Lemma iso_forward_equiv {D E : category} {a b : functor D E}
    (H : functor_equiv a b) x
    : forward (functor_eq_natural_iso H) ₙ x
        = hom_trans eq_refl (func_eq_o_map H _) (id _).
  Proof.
    unfold functor_eq_natural_iso.
    simpl.
    destruct (func_eq_o_map H x).
    reflexivity.
  Qed.

  Lemma functor_eq_natural_iso_trans_fwd {D E : category} {a b : functor D E}
    (H : functor_equiv a b)
    : forward (functor_eq_natural_iso H) = functor_eq_natural H.
  Proof.
    apply natural_equiv_unpack.
    intros ?; simpl.
    reflexivity.
  Qed.

  Lemma functor_eq_natural_iso_trans_bwd {D E : category} {a b : functor D E}
    (H : functor_equiv a b)
    : backward (functor_eq_natural_iso H) = functor_eq_natural_backward H.
  Proof.
    apply natural_equiv_unpack.
    intros ?; simpl.
    reflexivity.
  Qed.

  Lemma iso_backward_equiv' {D E : category} {a b : functor D E}
    (H : functor_equiv a b)
    : backward (functor_eq_natural_iso H)
        = forward (functor_eq_natural_iso (symmetry H)).
  Proof.
    unfold functor_eq_natural_iso.
    simpl.
    apply natural_equiv_unpack.
    intros ?.
    rewrite -functor_eq_natural_iso_trans_bwd /=.
    f_equiv.
    apply proof_irrelevance.
  Qed.

  Program Definition canon_ext_equiv {dsp dsp1 dsp2} (P : partial_solution dsp)
    (H : dsp_included dsp1 dsp2)
    (H1 : dsp_included dsp1 dsp)
    (H2 : dsp_included dsp2 dsp)
    :
    functor_equiv
      (cut_par_sol P H1)
      (cut_par_sol
         (cut_par_sol P H2) H)
    := MkFuncEq (λ a, eq_refl) _.
  Next Obligation.
    intros; simpl.
    rewrite hom_trans_refl.
    reflexivity.
  Qed.

  Definition is_canonical_par_sol {dsp} (ps : partial_solution dsp)
    := ∀ (α : downset dsp),
    cones_equiv (reflexivity _) (parsolext_cone
                                   (the_extension
                                      (cut_par_sol ps (lt_dsp_included α))))
      (partial_sol_cone_at ps α).

  Lemma canonicity_extend_v {dsp} (P : partial_solution dsp)
    (H : ∀ α, is_canonical_par_sol (cut_par_sol P (le_dsp_included α)))
    (α : downset dsp)
    : vertex (the_extension (cut_par_sol P (lt_dsp_included α))) =
        vertex (partial_sol_cone_at P α).
  Proof.
    rewrite -(cones_eq_vertexes (H α (MkDS (squash (reflexivity _))))).
    simpl.
    do 2 f_equal.
    apply functor_equiv_unpack, canon_ext_equiv.
  Qed.

  Lemma canonicity_extend
    {dsp} (P : partial_solution dsp)
    (H : ∀ α, is_canonical_par_sol (cut_par_sol P (le_dsp_included α)))
    : is_canonical_par_sol P.
  Proof.
    intros α.
    set (α' := (MkDS (le_dsp α) (squash (reflexivity _)))).
    pose proof (H α α') as G; clear H.
    assert (cones_equiv (reflexivity _)
              (partial_sol_cone_at P α)
              (the_extension (cut_par_sol P (lt_dsp_included α)))).
    {
      unshelve eapply MkConesEq.
      - refine (eq_trans (eq_sym (cones_eq_vertexes G))
                  (o_map_eq (alg_func_func F)
                     (alg_lim_alg_equiv_cong
                        (symmetry (canon_ext_equiv _ _ _ _))))).
      - intros; simpl.
        apply alg_hom_map_prop_eq; simpl.
        rewrite hom_trans_alg_hom_map /=.
        pose proof (cones_eq_sides G j) as G'.
        simpl in G'.
        apply alg_hom_map_eq_eq in G'.
        simpl in G'.
        rewrite hom_trans_alg_hom_map in G'.
        simpl in G'.
        unfold cut_ord_ds_cat_func_h_map in G'.
        simpl.
        rewrite G'; clear G'.
        rewrite -hom_trans_trans /=.
        rewrite func_eq_o_map_refl /=.
        rewrite hom_trans_trans /=.
        rewrite hom_trans_compose.
        rewrite hom_trans_refl.
        rewrite func_eq_o_map_refl /=.
        rewrite hom_trans_compose.
        rewrite hom_trans_refl.
        f_equal.
        rewrite !car_eq_eq_trans.
        rewrite -hom_trans_trans /=.
        rewrite car_eq_eq_symm.
        rewrite eq_trans_assoc.
        rewrite eq_trans_sym_inv_r.
        rewrite eq_trans_refl_l.
        match goal with
          |- context G [o_map_eq (alg_func_func F) ?H'] =>
            set (H := H')
        end.
        assert ((car_eq
                    (o_map_eq
                       (alg_func_func F)
                       H))
                 = (o_map_eq F
                      (car_eq
                         H)))
          as HEQ.
        { destruct H; reflexivity. }
        rewrite HEQ; clear HEQ.
        rewrite h_map_eq_l.
        f_equal.
        clear.
        assert (FEQ :
                 functor_equiv
                   (functor_compose
                      (cut_ord_ds_cat_func (lt_dsp α) (lt_dsp_included α')
                         (cut_ord_ds_cat_func (le_dsp α) (le_dsp_included α) P))
                      (forgetful F))
                   (functor_compose
                      (cut_ord_ds_cat_func (lt_dsp α) (lt_dsp_included α) P)
                      (forgetful F))).
        { apply (func_equiv_compose
                   (symmetry (canon_ext_equiv _ _ _ _))
                   (reflexivity (forgetful F))). }
        rewrite (cones_eq_sides (functor_equiv_lim FEQ) j).
        f_equal.
        + apply proof_irrelevance.
        + apply proof_irrelevance.
    }
    rewrite cones_equiv_eq /cones_eq /=.
    rewrite cones_equiv_eq /cones_eq /= in H.
    rewrite -H.
    reflexivity.
  Qed.

  Lemma canon_ind_equiv {dsp : downset_pred SI}
    {P : partial_solution dsp}
    {α : SI}
    (α' : downset (lt_dsp α))
    (T : dsp_included (lt_dsp α) dsp)
    (T' : dsp_included (le_dsp α') dsp)
  : cut_ord_ds_cat_func (lt_dsp α') (lt_dsp_included α') (cut_ord_ds_cat_func (lt_dsp α) T P) =
      cut_ord_ds_cat_func (lt_dsp α') (lt_dsp_included (dsp_le_top α'))
        (cut_ord_ds_cat_func (le_dsp α') T' P).
  Proof.
    apply functor_equiv_unpack.
    unshelve econstructor.
    - intros; simpl.
      rewrite /cut_ord_ds_cat_func_o_map //=.
    - intros; simpl.
      rewrite hom_trans_refl //=.
  Qed.

  Lemma canonicity_inductive {dsp} (P : partial_solution dsp) :
    (∀ α, is_canonical_par_sol (cut_par_sol P (lt_dsp_included α))
          → is_canonical_par_sol (cut_par_sol P (le_dsp_included α)))
    → is_canonical_par_sol P.
  Proof.
    intros H.
    apply canonicity_extend.
    intros α.
    destruct α as [α G].
    revert G.
    induction (index_lt_wf _ α) as [α _ IHα]; intros G.
    apply H; clear H.
    set (β := MkDS _ G).
    intros α'.
    pose proof (IHα α' (unsquash (ds_in_dsp α'))
                  (squash (dsp_included_trans
                             (le_dsp_included α')
                             (lt_dsp_included β) α'
                             (reflexivity _)))
                  (dsp_le_top α')) as IHβ.
    revert IHβ.
    match goal with
    | |- context G [cut_par_sol P ?a]  => set (T := a)
    end.
    simpl in T.
    assert (T' : dsp_included (le_dsp α') dsp).
    {
      apply T.
    }
    assert (T = T') as ->; first by apply proof_irrelevance.
    intros IHβ.
    assert (T : dsp_included (lt_dsp β) dsp).
    { apply (lt_dsp_included β). }
    assert (lt_dsp_included β = T) as ->; first by apply proof_irrelevance.
    subst β.
    simpl in *.
    clear G.
    clear IHα.
    unshelve econstructor.
    - refine (eq_trans (o_map_eq (alg_func_func _)
                          (cones_eq_vertexes
                             (Fequiv :=
                                functor_equiv_pack (canon_ind_equiv α' T T')) _))
                (cones_eq_vertexes IHβ)).
      refine (functor_equiv_lim (functor_equiv_pack (canon_ind_equiv α' T T'))).
    - intros j; simpl.
      apply alg_hom_map_prop_eq.
      rewrite hom_trans_alg_hom_map /=.
      unfold cut_ord_ds_cat_func_h_map.
      rewrite car_eq_eq_trans.
      clear.
      pose proof (cones_eq_sides IHβ j) as J; simpl in J.
      apply alg_hom_map_eq_eq in J.
      simpl in J.
      unfold cut_ord_ds_cat_func_h_map in J.
      rewrite J; clear J.
      simpl.
      rewrite hom_trans_alg_hom_map /=.
      rewrite hom_trans_compose.
      rewrite hom_trans_compose.
      f_equal.
      + rewrite -{2} (eq_trans_refl_l eq_refl).
        rewrite hom_trans_trans.
        assert ((car_eq
                    (o_map_eq
                       (alg_func_func F)
                       (cones_eq_vertexes
                          (functor_equiv_lim
                             (functor_equiv_pack (canon_ind_equiv (P := P) α' T T'))))))
                 = (o_map_eq F
                      (car_eq
                         (cones_eq_vertexes
                            (functor_equiv_lim
                               (functor_equiv_pack (canon_ind_equiv α' T T')))))))
          as HEQ.
        {
          destruct (cones_eq_vertexes
                      (functor_equiv_lim
                         (functor_equiv_pack (canon_ind_equiv α' T T')))).
          reflexivity.
        }
        rewrite HEQ; clear HEQ.
        rewrite h_map_eq_l.
        f_equal.
        match goal with
        | |- context G [functor_compose ?a ?b]
          => set (T1 := functor_compose a b)
        end.
        match goal with
        | |- context G [functor_compose ?a ?b]
          => set (T2 := functor_compose a b)
        end.
        assert (FEQ :
                 functor_equiv
                   T1
                   T2).
        {
          unshelve econstructor.
          - intros; simpl.
            reflexivity.
          - intros; simpl.
            rewrite hom_trans_refl.
            reflexivity.
        }
        assert (CEQ : cones_equiv
                        FEQ
                        (term
                           (complete T1))
                        (term
                           (complete T2))).
        {
          apply functor_equiv_lim.
        }
        rewrite (cones_eq_sides CEQ j).
        rewrite -hom_trans_trans.
        rewrite -(hom_trans_refl (side (term (complete T1)) j)).
        f_equal.
        match goal with
        | |- context G [_ = hom_trans ?a _ _]
          => assert (a = eq_refl) as ->
        end.
        { apply proof_irrelevance. }
        f_equal.
        apply proof_irrelevance.
      + f_equal.
        apply proof_irrelevance.
  Qed.

  Lemma canonical_eq_destruct {α}
    (P Q : partial_solution (le_dsp α))
    (J : dsp_included (lt_dsp α) (le_dsp α))
    (H : functor_equiv (cut_par_sol P J) (cut_par_sol Q J))
    (H' : P ₒ (dsp_le_top α) = Q ₒ (dsp_le_top α))
    (H'' : (∀ (β : downset (lt_dsp α))
                  (f : hom (C := (OrdDSCat (le_dsp α))ᵒᵖ)
                         (dsp_le_top α)
                         (dsp_include J β)),
                  (hom_trans (C := C) (car_eq H') (car_eq (func_eq_o_map H β))
                     (alg_hom_map (P ₕ f)) = alg_hom_map (Q ₕ f))))
    : functor_equiv P Q.
  Proof.
    unshelve econstructor.
    - intros.
      simpl in a.
      destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp a))) as [Hltβ|Heqβ].
      + epose proof (func_eq_o_map H (MkDS (lt_dsp α) (squash Hltβ))).
        simpl in H0.
        unfold cut_ord_ds_cat_func_o_map in H0.
        apply H0.
      + assert (ds_idx a = α).
        { done. }
        destruct a; simpl in *.
        subst.
        apply H'.
    - intros a b f.
      simpl.
      destruct (index_le_lt_eq_dec _ _ (unsquash _)) as [Hltγ|Heqγ];
        destruct (index_le_lt_eq_dec _ _ (unsquash _)) as [Hltγ'|Heqγ'].
      + set (a' := MkDS (lt_dsp α) (squash Hltγ)).
        set (b' := MkDS (lt_dsp α) (squash Hltγ')).
        unshelve eset (f' := _ : hom (C := OrdDSCat (lt_dsp α)) b' a').
        rewrite (func_eq_h_map H f').
        reflexivity.
      + destruct a, b; simpl in *.
        subst.
        exfalso.
        eapply index_lt_le_contradict; first apply Hltγ.
        apply f.
      + destruct a, b; simpl in *.
        subst.
        unfold eq_ind_r.
        simpl.
        pose proof (H'' (MkDS (lt_dsp α) (squash Hltγ'))) as G.
        simpl in G.
        apply alg_hom_map_eq.
        rewrite !hom_trans_alg_hom_map.
        rewrite (G f).
        reflexivity.
      + destruct a, b; simpl in *.
        subst.
        unfold eq_ind_r.
        simpl.
        set (f' := _ : hom (C := OrdDSCat _) (dsp_le_top α) (dsp_le_top α)).
        assert (f' = id _ :> hom (C := OrdDSCat _) _ _) as ->.
        { simpl. apply proof_irrelevance. }
        rewrite !h_map_id.
        rewrite hom_trans_id.
        reflexivity.
  Qed.

  Lemma canonical_eq {dsp} (P Q : partial_solution dsp)
    (PC : is_canonical_par_sol P) (QC : is_canonical_par_sol Q) :
    functor_equiv P Q.
  Proof.
    apply par_sol_extensional.
    intros α.
    destruct α as [α G].
    simpl le_dsp.
    revert PC QC.
    revert P Q.
    induction (index_lt_wf _ α) as [α _ IHα].
    intros P Q PC QC.
    set (α' := MkDS dsp G).
    assert (∀ γ : downset (lt_dsp α),
              ∀ H : dsp_included (le_dsp γ) dsp,
              functor_equiv
                (cut_ord_ds_cat_func (le_dsp γ) H P)
                (cut_ord_ds_cat_func (le_dsp γ) H Q)) as IH.
    {
      intros γ H.
      pose proof (IHα γ (unsquash (ds_in_dsp γ)) (squash (H γ (reflexivity _))))
        as J.
      match goal with
      | J : context G [cut_ord_ds_cat_func _ ?a] |- _ =>
          assert (a = H) as <-
      end; last apply J; [| done | done].
      apply proof_irrelevance.
    }
    rename IHα into IHremember.
    assert (∀ a : obj ((OrdDSCat (le_dsp α)) ᵒᵖ),
                (cut_ord_ds_cat_func (lt_dsp a)
                   (lt_dsp_included (dsp_include (le_dsp_included α') a)) P)
                = (cut_ord_ds_cat_func (lt_dsp a)
                     (lt_dsp_included (dsp_include (le_dsp_included α') a)) Q))
      as IHα.
    {
      intros a.
      apply functor_equiv_unpack.
      unshelve econstructor.
      - intros b; simpl.
        rewrite /cut_ord_ds_cat_func_o_map.
        simpl in IH.
        pose proof
          (func_eq_o_map (IH
             (MkDS (lt_dsp α)
                (squash (index_lt_le_trans _ _ _
                           (unsquash (ds_in_dsp b))
                           (unsquash (ds_in_dsp a)))))
             (λ x H, (dsp_pred_downwards dsp H
                        (dsp_pred_downwards dsp
                           (index_lt_le_subrel _ _ (unsquash (ds_in_dsp b)))
                           (dsp_pred_downwards dsp
                              (unsquash (ds_in_dsp a))
                              (unsquash G))))))
             (MkDS _ (squash (reflexivity _)))) as H;
          simpl in H.
        apply H.
      - intros γ1 γ2 f; simpl.
        match goal with
        | |- context G [func_eq_o_map (IH ?a ?b) ?c]
          => set (p1 := a); set (p2 := b); set (p3 := c)
        end.
        clearbody p2.
        match goal with
        | |- context G [hom_trans _ (func_eq_o_map (IH ?a ?b) ?c)]
          => set (t1 := a); set (t2 := b); set (t3 := c)
        end.
        clearbody t2.
        epose proof (λ δ γ g, func_eq_h_map (IH p1 p2) (a := δ) (b := γ) g)
          as HEQ.
        rewrite /= /cut_ord_ds_cat_func_h_map /= in HEQ.
        rewrite /cut_ord_ds_cat_func_h_map.
        symmetry.
        match goal with
        | |- context G [_ ₕ ?a = _] =>
            set (f' := a)
        end.
        simpl in f'.
        assert (f' = f) as ->.
        { apply proof_irrel. }
        simpl in f.
        rewrite -(HEQ
                    (MkDS (le_dsp γ1) (squash (reflexivity _)))
                    (MkDS (le_dsp γ1) (squash f))).
        f_equiv; last done.
        apply proof_irrelevance.
    }
    clear IH.
    assert (∀ a : obj ((OrdDSCat (le_dsp α)) ᵒᵖ),
              functor_equiv
                (cut_ord_ds_cat_func (lt_dsp a)
                   (lt_dsp_included (dsp_include (le_dsp_included α') a)) P)
                (cut_ord_ds_cat_func (lt_dsp a)
                   (lt_dsp_included (dsp_include (le_dsp_included α') a)) Q))
      as IHβ.
    {
      intros; rewrite IHα.
      reflexivity.
    }
    clear IHα IHremember.

    unshelve eapply (canonical_eq_destruct (cut_par_sol P (le_dsp_included α'))
                   (cut_par_sol Q (le_dsp_included α'))).
    { apply dsp_included_lt_le. }
    {
      etransitivity;
        first apply (symmetry
                       (canon_ext_equiv P
                          dsp_included_lt_le (lt_dsp_included _) (le_dsp_included α'))).
      etransitivity;
        last apply (canon_ext_equiv Q
                      dsp_included_lt_le (lt_dsp_included _) (le_dsp_included α')).
      apply (IHβ (dsp_le_top α)).
    }
    {
      apply (eq_trans
               (eq_sym
                  (cones_eq_vertexes
                     (PC (dsp_include (le_dsp_included α') (dsp_le_top α)))))
               (eq_trans
                  (o_map_eq (alg_func_func _)
                     (alg_lim_alg_equiv_cong (IHβ (dsp_le_top α))))
                  (cones_eq_vertexes
                     (QC (dsp_include (le_dsp_included α') (dsp_le_top α)))))).
    }
    {
      intros; simpl.
      simpl in *.
      rewrite -!func_eq_o_map_trans.
      rewrite -!func_eq_o_map_sym.
      rewrite !car_eq_eq_trans !car_eq_eq_symm.
      rewrite !hom_trans_trans.
      match goal with
      | |- context G [hom_trans _ ?a] =>
          assert (a = eq_trans a eq_refl) as ->
      end; first by rewrite eq_trans_refl_r.
      epose proof (cones_eq_sides
                     (QC (dsp_include (le_dsp_included α') (dsp_le_top α))) β) as H.
      simpl in H.
      apply alg_hom_map_prop_eq' in H.
      simpl in H.
      rewrite !hom_trans_alg_hom_map /= in H.
      match goal with
      | H : context G [?b = _] |- _ =>
          set (T1 := b)
      end.
      match goal with
      | |- context G [_ = ?a] =>
          set (T2 := a)
      end.
      assert (T1 = T2) as <-.
      {
        subst T1 T2 α'.
        do 2 f_equal.
        simpl.
        apply proof_irrelevance.
      }
      subst T1.
      rewrite H; clear H.
      f_equiv; first apply proof_irrelevance.

      epose proof (cones_eq_sides
                     (PC (dsp_include (le_dsp_included α') (dsp_le_top α))) β) as H.
      simpl in H.
      apply alg_hom_map_prop_eq' in H.
      simpl in H.
      rewrite !hom_trans_alg_hom_map /= in H.
      symmetry in H.
      apply hom_trans_sym_eq in H.
      symmetry in H.

      match goal with
      | H : context G [?b = _] |- _ =>
          set (T1 := b)
      end.
      match goal with
      | |- context G [hom_trans _ _ ?a] =>
          set (T2 := a)
      end.
      assert (T1 = T2) as <-.
      {
        subst T1 T2 α'.
        do 2 f_equal.
        - apply proof_irrelevance.
        - unfold cut_ord_ds_cat_func_h_map.
          simpl.
          f_equal.
          simpl.
          apply proof_irrelevance.
      }
      subst T1.
      rewrite H; clear H.
      clear PC QC.
      rewrite hom_trans_compose.
      match goal with
        |- context G [o_map_eq (alg_func_func F) ?H'] =>
          set (H := H')
      end.
      assert ((car_eq
                 (o_map_eq
                    (alg_func_func F)
                    H))
              = (o_map_eq F
                   (car_eq
                      H)))
        as HEQ.
      { destruct H; reflexivity. }
      rewrite HEQ; clear HEQ.
      rewrite h_map_eq_l.
      subst H.
      set (P' := cut_par_sol P (lt_dsp_included (dsp_include (le_dsp_included α') (dsp_le_top α)))).
      match goal with
      | |- context G [functor_compose ?a]
        => change a with (parsol_func P')
      end.
      match goal with
      | |- context G [cons ?a]
        => change a with (parsol_func P' ₒ β)
      end.
      set (Q' := cut_par_sol Q (lt_dsp_included (dsp_include (le_dsp_included α') (dsp_le_top α)))).
      symmetry.
      match goal with
      | |- context G [functor_compose ?a]
        => change a with (parsol_func Q')
      end.
      match goal with
      | |- context G [cons ?a]
        => change a with (parsol_func Q' ₒ β)
      end.
      assert (functor_equiv P' Q') as FEQ.
      {
        subst P' Q'.
        apply (IHβ (dsp_le_top α)).
      }
      set (R := (IHβ (dsp_le_top α))).
      clearbody R.
      assert (R = FEQ) as ->.
      { apply proof_irrelevance. }
      clear IHβ.
      change (@cut_ord_ds_cat_func SI dsp (@lt_dsp SI α) (@lt_dsp_included SI dsp α')
                (@Alg C F) (@parsol_func dsp P))
        with (parsol_func P').
      change (@cut_ord_ds_cat_func SI dsp (@lt_dsp SI α) (@lt_dsp_included SI dsp α')
                (@Alg C F) (@parsol_func dsp Q))
        with (parsol_func Q').
      clearbody P' Q'.
      clear P Q.
      pose proof (functor_equiv_unpack FEQ) as HEQ.
      destruct HEQ.
      clear Q'.
      rewrite func_eq_o_map_refl.
      rewrite hom_trans_refl.
      simpl.
      match goal with
      | |- context G [hom_trans ?a]
        => assert (a = eq_refl) as ->
      end.
      { apply proof_irrelevance. }
      rewrite hom_trans_refl.
      reflexivity.
    }
  Qed.

  Lemma cut_par_sol_canon {dsp} (ps : partial_solution dsp)
    {dsp' : downset_pred SI}
    (Hdsps : dsp_included dsp' dsp)
    (HC : is_canonical_par_sol ps)
    : is_canonical_par_sol (cut_par_sol ps Hdsps).
  Proof.
    intros α.
    unshelve econstructor.
    - simpl.
      unfold cut_ord_ds_cat_func_o_map.
      simpl.
      pose proof (cones_eq_vertexes (HC (MkDS _ (squash (Hdsps α (unsquash (ds_in_dsp α))))))) as H.
      simpl in H.
      refine (eq_trans ((o_map_eq (alg_func_func F))
                          (alg_lim_alg_equiv_cong _)) H).
      symmetry.
      apply canon_ext_equiv.
    - intros; simpl.
      apply alg_hom_map_prop_eq; simpl.
      rewrite hom_trans_alg_hom_map /=.
      assert (∀ H G, car_eq (eq_trans H G) = eq_trans (car_eq H) (car_eq G)) as ->.
      {
        intros H J; destruct H; destruct J.
        reflexivity.
      }
      assert (func_eq_o_map (reflexivity _) _ = eq_refl) as ->.
      { apply proof_irrelevance. }
      match goal with
      | |- context G [hom_trans _ ?a]
        => assert (a = eq_trans eq_refl eq_refl) as ->
      end; first by apply proof_irrelevance.
      rewrite hom_trans_trans /=.
      match goal with
      | |- context G [hom_trans (car_eq (cones_eq_vertexes ?a))]
        => set (A := a)
      end.
      simpl in A.
      match goal with
      | |- context G [hom_trans _ _
                       (hom_trans (car_eq (o_map_eq (alg_func_func F)
                                             (alg_lim_alg_equiv_cong ?a))) _ _)]
        => set (B := a)
      end.
      simpl in B.
      rewrite /cut_ord_ds_cat_func_h_map /=.
      pose proof (cones_eq_sides A j) as HEQ.
      simpl in HEQ.
      apply alg_hom_map_eq_eq in HEQ.
      rewrite hom_trans_alg_hom_map /= in HEQ.
      rewrite HEQ; clear HEQ.
      f_equal.
      + apply proof_irrelevance.
      + eassert ((car_eq
                    (o_map_eq (alg_func_func F) (alg_lim_alg_equiv_cong B)))
                 = (o_map_eq F
                      (car_eq
                         (alg_lim_alg_equiv_cong B))))
          as HEQ.
        {
          destruct (alg_lim_alg_equiv_cong B).
          reflexivity.
        }
        rewrite HEQ; clear HEQ.
        rewrite hom_trans_compose.
        rewrite h_map_eq_l.
        rewrite hom_trans_refl.
        f_equal.
        f_equal.
        clear A.
        match goal with
        | |- context G [side ?a]
          => set (cn := a)
        end.
        match goal with
        | |- context G [hom_trans _ _ (side ?a _)]
          => set (cn' := a)
        end.
        simpl in cn, cn'.
        simpl in B.
        assert (CEQ : cones_equiv (func_equiv_compose B (reflexivity _)) cn' cn).
        {
          subst cn cn'.
          apply functor_equiv_lim.
        }
        rewrite (cones_eq_sides CEQ j).
        f_equal.
        * apply proof_irrelevance.
        * apply proof_irrelevance.
  Qed.

  Opaque id comp.
  Program Definition tower {dsp}
    (collection : ∀ α : downset dsp, partial_solution (le_dsp α))
    (canon_fam : ∀ α : downset dsp, is_canonical_par_sol (collection α))
    : functor (OrdDSCat dsp)ᵒᵖ (Alg F)
    := MkFunc (λ x, (collection x ₒ (dsp_le_top x)))
         (λ a b f,
           let b' := MkDS (le_dsp a) (squash f) in
           let P : ∀ α : SI, le_dsp b α → le_dsp a α := λ _ P, transitivity P f in
           ((hom_trans (C := Alg _)
             eq_refl
             (func_eq_o_map
                (canonical_eq
                   (cut_par_sol (collection a)
                      _)
                   (collection b)
                   (cut_par_sol_canon _ P (canon_fam _))
                   (canon_fam b)) (dsp_le_top b)) (id _))
              ∘ h_map (a := dsp_le_top a) (b := b') (collection a) f))
         _ _.
  Next Obligation.
    intros; simpl.
    match goal with
    | |- context G [_ ∘ ?a]
      => assert (a = hom_trans eq_refl eq_refl a) as ->
    end; first by rewrite hom_trans_refl.
    rewrite -hom_trans_compose.
    rewrite left_id.
    match goal with
    | |- context G [hom_trans _ _ _ ∘ ?a]
      => assert (a = hom_trans eq_refl eq_refl a) as ->
    end; first by rewrite hom_trans_refl.
    rewrite -hom_trans_compose.
    rewrite left_id.
    match goal with
    | |- context G [hom_trans _ _ _ ∘ ?a]
      => assert (a = hom_trans eq_refl eq_refl a) as ->
    end; first by rewrite hom_trans_refl.
    rewrite -hom_trans_compose.
    rewrite left_id.
    match goal with
    | |- context G [hom_trans _ _ _ ∘ hom_trans _ ?a _]
      => assert (a = eq_sym (eq_sym a)) as ->
    end.
    { by rewrite eq_sym_involutive. }
    rewrite -hom_trans_compose_r.
    match goal with
    | |- context G [_ = hom_trans _ _ _ ∘ ?a]
      => assert (a = hom_trans eq_refl eq_refl a) as ->
    end; first by rewrite hom_trans_refl.
    rewrite hom_trans_compose_take_in_r.
    rewrite eq_sym_involutive.
    rewrite hom_trans_refl.
    match goal with
    | |- context G [hom_trans ?a]
      => set (P1 := a)
    end; clearbody P1.
    match goal with
    | |- context G [hom_trans _ (func_eq_o_map ?a _)]
      => set (P2 := a)
    end.
    match goal with
    | |- context G [_ = hom_trans ?a _ _]
      => set (P3 := a)
    end; clearbody P3.
    match goal with
    | |- context G [_ = hom_trans _ (func_eq_o_map ?a _) _]
      => set (P4 := a)
    end.
    match goal with
    | |- context G [_ ∘ hom_trans _ (func_eq_o_map ?a _) _]
      => set (P5 := a)
    end.
    assert (P1 = eq_refl) as ->.
    { apply proof_irrelevance. }
    assert (P3 = eq_refl) as ->.
    { apply proof_irrelevance. }
    set (a' := (dsp_le_top a)).
    simpl in *.
    set (b' := MkDS (le_dsp a) (squash f)).
    set (c' := MkDS (le_dsp a) _).
    set (f' := _ : hom (C := OrdDSCat (le_dsp a)) b' a').
    set (g' := _ : hom (C := OrdDSCat (le_dsp a)) c' b').
    rewrite (h_map_comp _ _ (collection a) a' b' c' f' g').
    rewrite !hom_trans_compose.
    clearbody P2 P4 P5.
    destruct (functor_equiv_unpack P2).
    destruct (functor_equiv_unpack P5).
    simpl.
    match goal with
    | |- context G [hom_trans _ ?a]
      => assert (a = eq_refl) as ->
    end.
    { apply proof_irrelevance. }
    rewrite !hom_trans_refl.
    match goal with
    | |- context G [_ ∘ hom_trans _ ?a _]
      => assert (a = eq_refl) as ->
    end.
    { apply proof_irrelevance. }
    rewrite hom_trans_refl.
    f_equiv.
    clear P2 P5.
    match goal with
    | |- context G [hom_trans _ ?a _]
      => assert (a = eq_refl) as ->
    end.
    { apply proof_irrelevance. }
    rewrite hom_trans_refl.
    reflexivity.
  Qed.
  Next Obligation.
    intros; simpl.
    set (T := collection a).
    match goal with
    | |- context G [func_eq_o_map ?a] =>
        set (R := a)
    end.
    unfold cut_ord_ds_cat_func_o_map; simpl.
    clearbody R.
    clearbody T.
    rewrite h_map_id.
    rewrite right_id.
    assert (eq_refl = func_eq_o_map R (dsp_le_top a)) as HEQ.
    { apply proof_irrelevance. }
    rewrite HEQ.
    rewrite hom_trans_id.
    reflexivity.
  Qed.
  Transparent id comp.

  Opaque id comp.
  Program Definition tower_par_sol {dsp}
    (collection : ∀ α : downset dsp, partial_solution (le_dsp α))
    (canon_fam : ∀ α : downset dsp, is_canonical_par_sol (collection α))
    : partial_solution dsp
    := MkParSol (tower collection canon_fam) _ _.
  Next Obligation.
    intros; simpl.
    rewrite ((alg_hom_map_comp _ _)).
    apply is_iso_at_compose.
    - apply (parsol_edge_iso (collection α)).
    - rewrite hom_trans_alg_hom_map.
      apply iso_at_hom_trans.
      apply is_iso_at_id.
  Qed.
  Next Obligation.
    intros; simpl.
    apply (parsol_cons_iso (collection α) (dsp_le_top α)).
  Qed.
  Transparent id comp.

  Record canonical_par_sol dsp
    := MkCanonSol {
           sol : partial_solution dsp;
           is_canon : is_canonical_par_sol sol;
         }.
  Arguments MkCanonSol {_}.
  Arguments sol {_}.
  Arguments is_canon {_}.

  Lemma is_canon_eq {dsp} (p p' : partial_solution dsp)
    (H : p = p' :> functor _ _) : is_canonical_par_sol p → is_canonical_par_sol p'.
  Proof.
    destruct p as [p1 p2 p3], p' as [p1' p2' p3']; simpl in *.
    destruct H.
    intros H α.
    apply cones_equiv_unpack.
    eapply packed_cones_equiv_trans.
    - apply (cones_equiv_pack _ _ _ (H α)).
    - eapply (cones_equiv_pack (reflexivity _)).
      unshelve econstructor.
      + reflexivity.
      + intros; apply alg_hom_map_eq; simpl.
        rewrite func_eq_o_map_refl hom_trans_refl; simpl.
        reflexivity.
  Qed.

  Lemma partial_cone_eq {dsp} (p p' : partial_solution dsp)
    (H : p = p' :> functor _ _) : ∀ α,
    packed_cones_equiv (partial_sol_cone_at p α) (partial_sol_cone_at p' α).
  Proof.
    destruct p as [p1 p2 p3], p' as [p1' p2' p3']; simpl in *.
    destruct H.
    intros α.
    eapply cones_equiv_pack with (reflexivity _).
    unshelve econstructor.
    - simpl.
      reflexivity.
    - intros; apply alg_hom_map_eq; simpl.
      rewrite func_eq_o_map_refl hom_trans_refl; simpl.
      reflexivity.
  Qed.

  Lemma the_extension_eq {dsp} (p p' : partial_solution dsp)
    (H : p = p' :> functor _ _) :
    packed_cones_equiv (the_extension p) (the_extension p').
  Proof.
    destruct p as [p1 p2 p3], p' as [p1' p2' p3']; simpl in *.
    destruct H.
    eapply cones_equiv_pack with (reflexivity _).
    unshelve econstructor.
    - simpl.
      reflexivity.
    - intros; apply alg_hom_map_eq; simpl.
      rewrite func_eq_o_map_refl hom_trans_refl; simpl.
      reflexivity.
  Qed.

  Lemma canonicity_extend_lt {α : SI}
    (P : partial_solution (lt_dsp α))
    (H : is_canonical_par_sol P)
    (β : downset (le_dsp α))
    (Hlt : β ≺ α)
    : cones_equiv (reflexivity _)
        (the_extension (cut_par_sol (extend_par_sol_lt_le P) (lt_dsp_included β)))
        (partial_sol_cone_at (extend_par_sol_lt_le P) β).
  Proof.
    set (β' := (MkDS (lt_dsp α) (squash Hlt))).
    assert (FEQ : functor_equiv
                    (cut_par_sol
                       (extend_par_sol_lt_le P)
                       (lt_dsp_included β))
                    (cut_par_sol P (lt_dsp_included β'))).
    {
      unshelve econstructor.
      - intros; simpl.
        apply (eq_trans
                 (extend_ord_ds_cat_func_o_map_lt
                    (β := dsp_include (lt_dsp_included _) a)
                    (alg_func_on_cone (alg_lim_cone P))
                    (transitivity (unsquash (ds_in_dsp a)) Hlt))).
        unfold cut_ord_ds_cat_func_o_map; simpl.
        reflexivity.
      - intros; simpl.
        rewrite extend_ord_ds_cat_func_h_map_lt_lt.
        { apply (transitivity (unsquash (ds_in_dsp a)) Hlt). }
        { apply (transitivity (unsquash (ds_in_dsp b)) Hlt). }
        intros Hyp1 Hyp2; simpl.
        rewrite -hom_trans_trans.
        simpl in *.
        assert (Hyp1 = (transitivity (unsquash (ds_in_dsp a)) Hlt)) as ->.
        { apply proof_irrelevance. }
        assert (Hyp2 = (transitivity (unsquash (ds_in_dsp b)) Hlt)) as ->.
        { apply proof_irrelevance. }
        rewrite !eq_trans_sym_inv_l.
        rewrite hom_trans_refl.
        reflexivity.
    }
    apply cones_equiv_unpack.
    eapply packed_cones_equiv_trans;
      first apply the_extension_eq, functor_equiv_unpack, FEQ.
    apply packed_cones_equiv_sym.
    eapply packed_cones_equiv_trans;
      last apply (packed_cones_equiv_sym _ _ (cones_equiv_pack _ _ _ (H β'))).
    eapply cones_equiv_pack with FEQ.
    unshelve econstructor.
    - simpl.
      eapply (eq_trans (extend_ord_ds_cat_func_o_map_lt
                          (alg_func_on_cone (alg_lim_cone P)) Hlt)).
      reflexivity.
    - intros; apply alg_hom_map_eq.
      rewrite !hom_trans_alg_hom_map /=.
      rewrite extend_ord_ds_cat_func_h_map_lt_lt; first last.
      + intros Hyp.
        rewrite !hom_trans_alg_hom_map /=.
        rewrite car_eq_eq_symm.
        rewrite -!hom_trans_trans.
        rewrite !eq_trans_sym_inv_l.
        match goal with
        | |- context G [hom_trans _ ?a]
          => assert (a = eq_refl) as ->
        end.
        { apply proof_irrelevance. }
        rewrite hom_trans_refl.
        reflexivity.
      + simpl.
        etransitivity; last apply Hlt.
        apply (unsquash (ds_in_dsp j)).
  Qed.

  Lemma canonicity_extend_at {α : SI}
    (P : partial_solution (lt_dsp α))
    : packed_cones_equiv
        (the_extension (cut_par_sol (extend_par_sol_lt_le P) (dsp_included_lt_le)))
        (parsolext_cone (the_extension P)).
  Proof.
    set (Q := (extend_par_sol_lt_le_equiv_lt P dsp_included_lt_le)).
    clearbody Q.
    apply the_extension_eq.
    symmetry.
    rewrite (functor_equiv_unpack Q).
    reflexivity.
  Qed.

  Lemma canonicity_extend_at' {α : SI}
    (P : partial_solution (lt_dsp α))
    (H : is_canonical_par_sol P)
    (β : downset (le_dsp α))
    (Heq : ds_idx β = α)
    : cones_equiv (reflexivity _)
        (the_extension (cut_par_sol (extend_par_sol_lt_le P) (lt_dsp_included β)))
        (partial_sol_cone_at (extend_par_sol_lt_le P) β).
  Proof.
    set (β' := dsp_le_top α).
    assert (β = β') as ->.
    { destruct β as [β1 β2]; simpl in *; subst. done. }
    clear Heq.
    assert ((lt_dsp_included β') = dsp_included_lt_le) as Heq.
    { apply proof_irrelevance. }

    assert (FEQ : functor_equiv P
                    (cut_par_sol (extend_par_sol_lt_le P) (lt_dsp_included β'))).
    {
      unshelve econstructor.
      - intros; simpl.
        apply (eq_trans (eq_sym (extend_ord_ds_cat_func_o_map_lt
                                   (β := dsp_include (dsp_included_lt_le) a)
                                   (alg_func_on_cone (alg_lim_cone P))
                                   (unsquash (ds_in_dsp a))))).
        reflexivity.
      - intros; simpl.
        rewrite extend_ord_ds_cat_func_h_map_lt_lt.
        { simpl. apply (unsquash (ds_in_dsp a)). }
        { simpl. apply (unsquash (ds_in_dsp b)). }
        intros; simpl.
        f_equiv.
        + apply proof_irrelevance.
        + apply proof_irrelevance.
        + f_equal.
    }
    apply cones_equiv_unpack.
    eapply packed_cones_equiv_trans.
    - rewrite Heq.
      apply canonicity_extend_at.
    - assert (FEQ' : functor_equiv P
                       (cut_par_sol (extend_par_sol_lt_le P) (lt_dsp_included β'))).
      {
        apply functor_equiv_pack.
        symmetry.
        apply functor_equiv_unpack.
        apply extend_par_sol_lt_le_equiv_lt.
      }
      apply (MkPackedConesEquiv FEQ').
      unshelve econstructor.
      * simpl.
        eapply (eq_trans
                  (eq_sym (extend_ord_ds_cat_func_o_map_at
                             (α := β') (β := β')
                             (alg_func_on_cone (alg_lim_cone P)) eq_refl))).
        simpl. reflexivity.
      * intros j; apply alg_hom_map_eq.
        rewrite !hom_trans_alg_hom_map /=.
        rewrite extend_ord_ds_cat_func_h_map_lt_eq.
        { simpl. apply (unsquash (ds_in_dsp j)). }
        intros Hyp.
        rewrite !hom_trans_alg_hom_map.
        rewrite !car_eq_eq_symm.
        symmetry.
        apply hom_trans_sym.
        simpl.
        rewrite -hom_trans_trans.
        rewrite hom_trans_compose.
        f_equiv.
        -- match goal with
           | |- context G [hom_trans ?a]
             => set (T := a)
           end.
           simpl in T.
           clearbody T.
           assert (T = eq_refl) as ->; first by apply proof_irrelevance.
           rewrite hom_trans_refl.
           reflexivity.
        -- match goal with
           | |- context G [hom_trans _ ?a]
             => assert (a = eq_refl) as ->
           end.
           { apply proof_irrelevance. }
           rewrite hom_trans_refl.
           reflexivity.
  Qed.

  Lemma canonicity_ext
    {α} (P : partial_solution (lt_dsp α))
    (H : is_canonical_par_sol P)
    : is_canonical_par_sol (extend_par_sol_lt_le P).
  Proof.
    intros β.
    destruct (index_le_lt_eq_dec β α (unsquash (ds_in_dsp β))) as [Hlt|Heq].
    { by apply canonicity_extend_lt. }
    { by apply canonicity_extend_at'. }
  Qed.

  Program Definition tower_package {dsp}
    (canon_collection : ∀ α : downset dsp, canonical_par_sol (le_dsp α))
    : canonical_par_sol dsp
    := MkCanonSol (tower_par_sol
                     (λ α, sol (canon_collection α))
                     (λ α, is_canon (canon_collection α)))
         _.
  Next Obligation.
    intros dsp coll.
    apply canonicity_inductive.
    intros β H γ.
    apply cones_equiv_unpack.
    eapply packed_cones_equiv_trans.
    {
      apply the_extension_eq.
      apply functor_equiv_unpack.
      symmetry.
      unshelve eapply canon_ext_equiv.
      {
        eapply dsp_included_trans; first apply dsp_included_lt_le.
        eapply dsp_included_trans; first apply le_dsp_included.
        apply le_dsp_included.
      }
    }
    assert (HHH' : dsp_included (lt_dsp γ) (lt_dsp β)).
    {
      intros x P; simpl in *.
      destruct (index_le_lt_eq_dec _ _ (unsquash (ds_in_dsp γ))).
      - etransitivity.
        + apply P.
        + done.
      - destruct γ; subst; simpl in *.
        subst.
        apply P.
    }
    eapply packed_cones_equiv_trans.
    {
      apply the_extension_eq.
      apply functor_equiv_unpack.
      apply canonical_eq; first last.
      - unshelve eapply (cut_par_sol_canon (sol (coll β))).
        + apply(lt_dsp_included γ).
        + apply (is_canon (coll β)).
      - eapply is_canon_eq; first last.
        + eapply cut_par_sol_canon.
          apply H.
        + apply functor_equiv_unpack.
          symmetry.
          apply canon_ext_equiv.
    }
    Unshelve.
    2: apply HHH'.
    eapply packed_cones_equiv_trans;
      first apply (cones_equiv_pack _ _ _ (is_canon (coll β) γ)).
    apply partial_cone_eq.
    apply functor_equiv_unpack.
    unshelve econstructor.
    - intros; simpl.
      pose (T1 := (coll β)).
      pose (T2 := (coll (dsp_include (le_dsp_included β) a))).
      simpl in *.
      assert (G : dsp_included (le_dsp a) (le_dsp β)).
      { intros x P; simpl in *.
        etransitivity; first apply P.
        apply (unsquash (ds_in_dsp a)).
      }
      pose proof (canonical_eq (cut_par_sol (sol T1) G)
                    (sol T2) (cut_par_sol_canon _ _ (is_canon T1)) (is_canon T2)) as J.
      eapply (eq_trans eq_refl (func_eq_o_map J (dsp_le_top a))).
    - intros a b f; simpl.
      rewrite !eq_trans_refl_l.
      apply alg_hom_map_eq.
      rewrite !hom_trans_alg_hom_map /=.
      rewrite !hom_trans_alg_hom_map /=.
      match goal with
      | |- context G [hom_trans ?a]
        => set (T1 := a)
      end; clearbody T1.
      match goal with
      | |- context G [hom_trans _ ?a]
        => set (T2 := a)
      end; clearbody T2.
      match goal with
      | |- context G [_ = hom_trans _ ?a _ ∘ _]
        => set (T3 := a)
      end; clearbody T3.
      simpl in *.
      destruct T2.
      assert (G : dsp_included (le_dsp a) (le_dsp β)).
      { intros x P; simpl in *.
        etransitivity; first apply P.
        apply (unsquash (ds_in_dsp a)).
      }
      pose proof (canonical_eq (cut_par_sol (sol (coll β)) G)
                    (sol (coll (dsp_include (le_dsp_included β) a)))
                    (cut_par_sol_canon _ _ (is_canon _)) (is_canon _)) as J.
      assert (G' : dsp_included (le_dsp b) (le_dsp β)).
      { intros x P; simpl in *.
        etransitivity; first apply P.
        apply (unsquash (ds_in_dsp b)).
      }
      pose proof (canonical_eq (cut_par_sol (sol (coll β)) G)
                    (sol (coll (dsp_include (le_dsp_included β) a)))
                    (cut_par_sol_canon _ _ (is_canon _)) (is_canon _)) as J'.
      rewrite hom_trans_compose_r.
      rewrite -hom_trans_compose.
      rewrite left_id.
      assert (T1 = car_eq (func_eq_o_map J (dsp_le_top a))) as ->.
      { apply proof_irrelevance. }
      assert ((car_eq (func_eq_o_map J (dsp_le_top a)))
              = car_eq (eq_trans (func_eq_o_map J (dsp_le_top a)) eq_refl)) as ->.
      { apply proof_irrelevance. }
      assert (eq_refl = car_eq eq_refl) as ->.
      { apply proof_irrelevance. }
      rewrite -hom_trans_alg_hom_map.
      assert (eq_refl = car_eq (eq_sym eq_refl)) as ->.
      { apply proof_irrelevance. }
      match goal with
      | |- context G [hom_trans _ ?a]
        => set (T := a)
      end.
      set (b' := MkDS (le_dsp a) (squash f)).
      assert (T = (eq_trans (func_eq_o_map J b') (eq_sym (func_eq_o_map J b')))) as ->.
      { apply proof_irrelevance. }
      rewrite hom_trans_trans.
      rewrite (@func_eq_h_map _ _ _ _ J (dsp_le_top a) b' f).
      rewrite hom_trans_alg_hom_map.
      f_equiv.
      + apply proof_irrelevance.
      + reflexivity.
  Qed.

  Lemma functor_collection
    : ∀ α, canonical_par_sol (le_dsp α).
  Proof.
    intros β.
    induction (index_lt_wf _ β) as [β _ IHβ].
    apply (MkCanonSol
             (extend_par_sol_lt_le
                (sol
                   (tower_package
                      (λ α : downset (lt_dsp β),
                          IHβ α (unsquash (ds_in_dsp α))))))).
    apply canonicity_ext.
    apply (is_canon
             (tower_package (λ α : downset (lt_dsp β),
                    IHβ α (unsquash (ds_in_dsp α))))).
  Qed.

End solution.

Theorem solver {SI : indexT} {C : category} `{!Complete C}
  `{!Enriched C (PSh (OrdCat SI))} `{!LimitsEnriched C}
  (F : functor C C) `{!LocallyContractiveFunctor F}
  : solution F.
Proof.
  apply total_partial_sol_sol; first done.
  eapply tower_package.
  intros α.
  apply functor_collection.
Qed.
