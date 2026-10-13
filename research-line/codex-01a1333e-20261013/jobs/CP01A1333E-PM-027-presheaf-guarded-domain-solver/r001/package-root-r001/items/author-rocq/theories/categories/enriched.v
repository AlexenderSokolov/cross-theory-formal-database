From SynthDom Require Import prelude.
From SynthDom.categories Require Import category ord_cat.
From SynthDom Require Import stepindex.

Set Universe Polymorphism.
Unset Universe Minimization ToSet.

Opaque later next earlier_later_nat_iso.

Class LocallyContractiveFunctor {SI : indexT} {C D : category} `{!Enriched C (PSh (OrdCat SI))} `{!Enriched D (PSh (OrdCat SI))}
  (F : functor C D) := MkLocContrFunc {
  contr_enriched :: EnrichedFunctor F;
  contr_func_h_map : ∀ a b : obj C, hom (later ₒ (enr_hom a b)) (enr_hom (F ₒ a) (F ₒ b));
  contr_func_h_map_is_h_map :
  ∀ a b : obj C, enr_func_h_map F a b = (contr_func_h_map a b) ∘ (next ₙ (enr_hom a b));
  contr_func_h_map_comp : ∀ (a b c : obj C),
    contr_func_h_map a c ∘
    (later ₕ (enr_comp a b c)) ∘
    ((backward (later_prod (enr_hom a b) (enr_hom b c))) : hom (later ₒ enr_hom a b ×ₒ (later ₒ enr_hom b c)) (later ₒ (enr_hom a b ×ₒ enr_hom b c)))
    =
    (enr_comp (F ₒ a) (F ₒ b) (F ₒ c)) ∘
    ((contr_func_h_map a b) ×ₕ (contr_func_h_map b c));
  contr_func_h_map_id : ∀ a,
  (contr_func_h_map a a) ∘ (later ₕ ⌜id a⌝) ∘ (next ₙ (1ₒ)) = ⌜id (F ₒ a)⌝
}.
Global Arguments MkLocContrFunc {_ _ _ _ _ _ _} _ _ _ _.
Global Arguments contr_func_h_map {_ _ _ _ _} _ {_} _ _.
Global Arguments contr_func_h_map_is_h_map {_ _ _ _ _} _ {_} _ _.
Global Arguments contr_func_h_map_comp {_ _ _ _ _} _ {_} _ _ _.
Global Arguments contr_func_h_map_id {_ _ _ _ _} _ {_} _.

Global Instance locally_contractive_contractive
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))} (F : functor C C)
  `{!LocallyContractiveFunctor F} a b :
  Contractive (enr_func_h_map F a b) :=
  MkContr (contr_func_h_map F a b) (contr_func_h_map_is_h_map F a b).

Global Program Instance LocallyContractiveFunctor_comp_l
  {SI : indexT} {C D E : category} `{!Enriched C (PSh (OrdCat SI))}
  `{!Enriched D (PSh (OrdCat SI))} `{!Enriched E (PSh (OrdCat SI))}
  (F : functor C D) (G : functor D E)
  `{!LocallyContractiveFunctor F} `{!EnrichedFunctor G} :
  LocallyContractiveFunctor (functor_compose F G) :=
  MkLocContrFunc (λ a b, enr_func_h_map G (F ₒ a) (F ₒ b) ∘ contr_func_h_map F a b) _ _ _.
Next Obligation.
  intros ??????? F G ?? a b.
  apply natural_equiv_unpack; intros α.
  extensionality f; simpl in *.
  pose proof (equal_f (natural_equiv_pack (contr_func_h_map_is_h_map F a b) α) f) as Heq'.
  simpl in Heq'; rewrite -Heq' //.
Qed.
Next Obligation.
  intros ??????? F G ?? a b c.
  apply natural_equiv_unpack; intros α.
  extensionality l; destruct l as [la lb].
  simpl in *.
  pose proof (equal_f (natural_equiv_pack (contr_func_h_map_comp F a b c) α) (la, lb)) as Hfg;
    simpl in Hfg; rewrite Hfg; clear Hfg.
  epose proof (equal_f (natural_equiv_pack (enr_func_h_map_comp G (F ₒ a) (F ₒ b) (F ₒ c)) α)) as Hfg;
    simpl in Hfg; rewrite Hfg; clear Hfg.
  simpl; done.
Qed.
Next Obligation.
  intros ??????? F G ?? a.
  apply natural_equiv_unpack; intros α.
  extensionality l; destruct l as []; simpl in *.
  pose proof (equal_f (natural_equiv_pack (contr_func_h_map_id F a) α) ()) as Hid;
    simpl in Hid; rewrite Hid; clear Hid.
  epose proof (equal_f (natural_equiv_pack (enr_func_h_map_id G (F ₒ a)) α) ()) as Hg;
    simpl in Hg; rewrite -!Hg; clear Hg.
  done.
Qed.
Fail Next Obligation.

Global Program Instance LocallyContractiveFunctor_comp_r
  {SI : indexT} {C D E : category} `{!Enriched C (PSh (OrdCat SI))}
  `{!Enriched D (PSh (OrdCat SI))} `{!Enriched E (PSh (OrdCat SI))}
  (F : functor D E) (G : functor C D)
  `{!LocallyContractiveFunctor F} `{!EnrichedFunctor G} :
  LocallyContractiveFunctor (functor_compose G F) :=
  MkLocContrFunc
    (λ a b, contr_func_h_map F (G ₒ a) (G ₒ b) ∘ (later ₕ (enr_func_h_map G a b))) _ _ _.
Next Obligation.
  intros ??????? F G ?? a b.
  apply natural_equiv_unpack; intros α.
  extensionality f; simpl in *.
  pose proof (equal_f (natural_equiv_pack (contr_func_h_map_is_h_map
                                             F (G ₒ a) (G ₒ b)) α)
                ((enr_func_h_map G a b ₙ α) f))
    as Heq; simpl in Heq; rewrite Heq; clear Heq.
  f_equiv.
  pose proof (equal_f (natural_equiv_pack (naturality next (enr_func_h_map G a b)) α) f); done.
Qed.
Next Obligation.
  intros ??????? F G ?? a b c.
  apply natural_equiv_unpack; intros α.
  extensionality l; destruct l as [la lb].
  simpl in *.
  epose proof (equal_f (natural_equiv_pack
                          (h_map_comp _ _ later _ _ _
                             (enr_comp a b c) (enr_func_h_map G a c)) α)) as Hlc;
    simpl in Hlc; rewrite -Hlc; clear Hlc.
  epose proof (enr_func_h_map_comp G a b c) as Hcmp;
    simpl in Hcmp; rewrite Hcmp; clear Hcmp.
  epose proof (equal_f (natural_equiv_pack
                          (h_map_comp _ _ later _ _ _
                             (enr_func_h_map G a b ×ₕ enr_func_h_map G b c)
                             (enr_comp _ _ _)) α)) as Hlc;
    simpl in Hlc; rewrite Hlc; clear Hlc.
  epose proof (λ a b c d e f g h, equal_f (natural_equiv_pack
                          (@naturality _ _ _ _
                             (backward (later_preserves_prods_nat SI))
                             (a, b) (c, d) (e, f)) α) (g, h)) as Hn;
    simpl in Hn; rewrite -Hn; clear Hn.
  epose proof (λ a b c, equal_f (natural_equiv_pack (contr_func_h_map_comp F a b c) α))
    as Hcmp;
    simpl in Hcmp; rewrite Hcmp; clear Hcmp.
  done.
Qed.
Next Obligation.
  intros ??????? F G ?? a.
  apply natural_equiv_unpack; intros α.
  extensionality l; destruct l as []; simpl in *.
  pose proof (equal_f (natural_equiv_pack (naturality next ⌜ id a ⌝) α) ()) as Hn;
    simpl in Hn; rewrite -Hn; clear Hn.
  epose proof (λ x, equal_f (natural_equiv_pack (naturality next (enr_func_h_map G a a)) α) x) as Hn;
    simpl in Hn; rewrite -Hn; clear Hn.

  epose proof (equal_f (natural_equiv_pack (enr_func_h_map_id G a) α) ()) as Hg;
    simpl in Hg; rewrite !Hg; clear Hg.
  pose proof (equal_f (natural_equiv_pack (naturality next ⌜ id (G ₒ a) ⌝) α) ()) as Hn;
    simpl in Hn; rewrite Hn; clear Hn.
  pose proof (equal_f (natural_equiv_pack (contr_func_h_map_id F (G ₒ a)) α) ()) as Hid;
    simpl in Hid; rewrite Hid; done.
Qed.
Fail Next Obligation.

(* pointwiseness of limits in categories enriched over presheaves.  *)
Section enriched_limits.
  Context {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}.

  Record enr_cone {J} (F : functor J C) α := MkEnrCone {
    enr_vertex : obj C;
    enr_side : ∀ j : obj J, (enr_hom enr_vertex (F ₒ j)) ₒ α;
    enr_side_commutes : ∀ (j j' : obj J) (f : hom j j'),
      enr_side j' = (enr_comp enr_vertex (F ₒ j) (F ₒ j') ₙ α) (enr_side j, (⌜F ₕ f⌝ ₙ α) ());
  }.
  Arguments enr_vertex {_ _ _} _.
  Arguments enr_side {_ _ _} _ _.
  Arguments enr_side_commutes {_ _ _} _ [_ _] _.

  Program Definition enr_cone_natural {J} {F : functor J C} {α} (cn : enr_cone F α)
    {β} (Hle : β ⪯ α) : enr_cone F β :=
    MkEnrCone _ _ β (enr_vertex cn)
      (λ j, ((enr_hom (enr_vertex cn) (F ₒ j)) ₕ Hle) (enr_side cn j)) _.
  Next Obligation.
    intros ??? cn ? Hle ?? f; simpl in *.
    rewrite (enr_side_commutes cn f) /=.
    epose proof (λ x, equal_f (naturality (enr_comp (enr_vertex cn) (F ₒ j) (F ₒ j')) Hle) x) as Hn; simpl in Hn; rewrite -Hn; clear Hn.
    epose proof (equal_f (naturality ⌜ F ₕ f ⌝ Hle) ())
      as Hn; simpl in Hn.
    rewrite Hn.
    done.
  Qed.

  Program Definition cone_to_enr_cone {J} {F : functor J C} (cn : cone F) α : enr_cone F α :=
    MkEnrCone _ _ α (vertex cn) (λ j, (⌜side cn j⌝ ₙ α) ()) _.
  Next Obligation.
    repeat intros ?; simpl.
    epose proof (λ a b c x y z, equal_f (natural_equiv_pack (@enr_comp_comp _ _ _ _ _ a b c x y) z) ())
      as Hcmp;
      rewrite /= in Hcmp; rewrite -Hcmp /=; clear Hcmp.
    rewrite !enr_embed_project.
    rewrite -side_commutes //.
  Qed.
  Fail Next Obligation.

  Record enr_cone_hom {J} {F : functor J C} {α} (cn cn' : enr_cone F α) := MkEnrConeHom {
    enr_cone_hom_map : (enr_hom (enr_vertex cn) (enr_vertex cn'))ₒ α;
    enr_cone_hom_commutes : ∀ j : obj J,
      enr_side cn j = (enr_comp (enr_vertex cn) (enr_vertex cn') (F ₒ j) ₙ α)
       (enr_cone_hom_map, enr_side cn' j);
  }.
  Arguments enr_cone_hom_map {_ _ _ _ _} _.
  Arguments enr_cone_hom_commutes {_ _ _ _ _} _ _.

  Record enr_cone_is_limit {J} {F : functor J C} {α} (cn : enr_cone F α) := MkEnrConeIsLimit {
    enr_limit_hom : ∀ cn', enr_cone_hom cn' cn;
    enr_limit_hom_unique : ∀ cn' (h h' : enr_cone_hom cn' cn),
      enr_cone_hom_map h = enr_cone_hom_map h';
  }.

  Definition enr_limit {J} {F : functor J C} {c : obj C} (il : is_limit F c) :=
    ∀ α, enr_cone_is_limit (cone_to_enr_cone (cone_of_is_cone (il_is_cone il)) α).

  Lemma enr_hom_to_limit_unique {J} {F : functor J C} {α} {cn : enr_cone F α}
    (ecil : enr_cone_is_limit cn) (cn' : enr_cone F α)
    (h h' : enr_hom (enr_vertex cn') (enr_vertex cn)ₒ α) :
    (∀ j : obj J,
        enr_side cn' j = (enr_comp (enr_vertex cn') (enr_vertex cn) (F ₒ j) ₙ α)
          (h, enr_side cn j)) →
    (∀ j : obj J,
        enr_side cn' j = (enr_comp (enr_vertex cn') (enr_vertex cn) (F ₒ j) ₙ α)
          (h', enr_side cn j)) →
    h = h'.
  Proof.
    intros Hhcm Hh'cm.
    pose (MkEnrConeHom _ _ _ _ _ h Hhcm) as hch.
    pose (MkEnrConeHom _ _ _ _ _ h' Hh'cm) as h'ch.
    pose proof (enr_limit_hom_unique _ ecil _ hch h'ch); done.
  Qed.

End enriched_limits.
Global Arguments MkEnrCone {_ _ _ _ _ _} _ _ _.
Global Arguments enr_vertex {_ _ _ _ _ _} _.
Global Arguments enr_side {_ _ _ _ _ _} _ _.
Global Arguments enr_side_commutes {_ _ _ _ _ _} _ [_ _] _.
Global Arguments MkEnrConeHom {_ _ _ _ _ _ _ _} _ _.
Global Arguments enr_cone_hom_map {_ _ _ _ _ _ _ _} _.
Global Arguments enr_cone_hom_commutes {_ _ _ _ _ _ _ _} _ _.
Global Arguments MkEnrConeIsLimit {_ _ _ _ _ _ _} _ _.
Global Arguments enr_limit_hom {_ _ _ _ _ _ _} _ _.
Global Arguments enr_limit_hom_unique {_ _ _ _ _ _ _} _ [_] _ _.
Global Arguments enr_limit {_ _ _ _ _ _} _.

Class LimitsEnriched {SI : indexT} (C : category) `{!Enriched C (PSh (OrdCat SI))} :=
  limits_enriched : ∀ {J} {F : functor J C} {c : obj C} (il : is_limit F c), enr_limit il.

Global Arguments limits_enriched {_ _ _ _ _ _ _} il.

Section psh_limits_enriched.
  Context {SI : indexT} {J} {F : functor J (PSh (OrdCat SI))}
    {L : PreSheaf (OrdCat SI)} (il : is_limit F L).

  Local Instance : Enriched (PSh (OrdCat SI)) (PSh (OrdCat SI)) :=
    (@self_enriched (PSh (OrdCat SI)) _).

  (* Opaque func_cat_limits_pointwise. *)

  Program Definition psh_limits_enriched_enr_cone_to_pointwise_cone
    {α} (cn : enr_cone F α) : cone (pointwise_func F α) :=
    MkCone (enr_vertex cn ₒ α)
      (λ j, λ x, (enr_side cn j ₙ α) (reflexivity _, x)) _.
  Next Obligation.
    repeat intros ?; simpl in *.
    extensionality x; simpl.
    rewrite (equal_f (natural_equiv_pack (enr_side_commutes cn f) α)).
    simpl; repeat f_equiv.
    apply proof_irrelevance.
  Qed.
  Fail Next Obligation.

  Program Definition enr_cone_coherent_partial_cone {α} (cn : enr_cone F α) :
    coherent_partial_cone F α :=
    MkCohParCone _ _
      (psh_limits_enriched_enr_cone_to_pointwise_cone cn)
      (λ _ f, psh_limits_enriched_enr_cone_to_pointwise_cone (enr_cone_natural cn f))
      (λ _ f, enr_vertex cn ₕ f) _.
  Next Obligation.
    intros α cn β f j.
    extensionality x; simpl in *.
    pose proof (equal_f (naturality (enr_side cn j) f)) as Hn;
      simpl in Hn; rewrite -Hn /=; clear Hn; simpl.
    repeat f_equiv; simpl.
    unfold hom_prod; simpl.
    f_equiv; last done.
    apply proof_irrelevance.
  Qed.

  Opaque func_cat_limits_pointwise.
  Program Definition psh_limits_enriched_enr_cone_hom_back {α} (cn : enr_cone F α) :
    enr_cone_hom cn (cone_to_enr_cone (cone_of_is_cone (il_is_cone il)) α) :=
    MkEnrConeHom
      (MkNat (λ β, λ le_x,
           cone_hom_map
             (bang (il_is_limiting_cone _ _ (func_cat_limits_pointwise F il β))
                (psh_limits_enriched_enr_cone_to_pointwise_cone (enr_cone_natural cn le_x.1)))
             le_x.2) _) _.
  Next Obligation.
    intros α cn β γ f.
    extensionality x; destruct x as [le x]; simpl in *.
    epose proof (equal_f (func_cat_limits_pointwise_natural F il
                            (enr_cone_coherent_partial_cone (enr_cone_natural cn le))
                            f) x) as Hpln.
    simpl in Hpln; rewrite -Hpln /=; clear Hpln.
    erewrite <-(hom_to_limit_unique
             _ _ _ (func_cat_limits_pointwise F il γ)
             (cone_is_cone (psh_limits_enriched_enr_cone_to_pointwise_cone
                              (enr_cone_natural (enr_cone_natural cn le) f)))).
    - reflexivity.
    - intros ?.
      extensionality y; simpl in *.
      rewrite_cone_hom_commutes_back; simpl.
      f_equiv; done.
    - intros ?.
      extensionality y; simpl in *.
      rewrite_cone_hom_commutes_back; simpl.
      do 2 f_equiv.
      simpl; apply proof_irrelevance.
  Qed.
  Next Obligation.
    Transparent func_cat_limits_pointwise.
    intros α cn j.
    apply natural_equiv_unpack.
    intros β.
    extensionality x.
    destruct x as [le x]; simpl in *.
    epose proof (equal_f (cone_hom_commutes
                   (bang
                      (il_is_limiting_cone (pointwise_func F β)
                         (L ₒ β) (func_cat_limits_pointwise F il β))
                      (psh_limits_enriched_enr_cone_to_pointwise_cone
                         (enr_cone_natural cn (transitivity (reflexivity β) le))))
                   j)) as H.
    simpl in H.
    unfold func_cat_limits_pointwise in H.
    simpl in H.
    rewrite -H.
    do 2 f_equal.
    apply proof_irrel.
  Qed.
  Fail Next Obligation.

  Program Definition psh_limits_enr_cone_hom_to_cone_hom {α cn β} (le : β ⪯ α)
    (h : enr_cone_hom cn (cone_to_enr_cone (cone_of_is_cone (il_is_cone il)) α)) :
      cone_hom
        (psh_limits_enriched_enr_cone_to_pointwise_cone
           (enr_cone_natural cn le))
        (cone_of_is_cone (il_is_cone (func_cat_limits_pointwise F il β))) :=
  MkConeHom (λ x, (enr_cone_hom_map h ₙ β) (le, x)) _.
  Next Obligation.
    intros ???? h ?; simpl in *.
    epose proof (enr_cone_hom_commutes h j) as Hsc;
      simpl in Hsc; rewrite Hsc; clear.
    extensionality x; simpl.
    repeat f_equal; apply proof_irrel.
  Qed.
  Fail Next Obligation.

  Program Definition psh_limits_enriched : enr_limit il :=
    λ α, MkEnrConeIsLimit (λ cn, psh_limits_enriched_enr_cone_hom_back cn) _.
  Next Obligation.
    intros α cn h h'.
    apply natural_equiv_unpack.
    intros β.
    extensionality t; destruct t as [le x]; simpl in *.
    epose proof (equal_f (cone_hom_equiv_pack _
                            (@bang_unique _ _
                               (il_is_limiting_cone
                                  _ _
                                  (func_cat_limits_pointwise F il β))
                               (psh_limits_enriched_enr_cone_to_pointwise_cone
                                  (enr_cone_natural cn le))
                               (psh_limits_enr_cone_hom_to_cone_hom le h))) x) as Hbu;
      simpl in Hbu; rewrite Hbu; clear Hbu.
    epose proof (equal_f (cone_hom_equiv_pack _
                            (@bang_unique _ _
                               (il_is_limiting_cone _ _
                                  (func_cat_limits_pointwise F il β))
                               (psh_limits_enriched_enr_cone_to_pointwise_cone (enr_cone_natural cn le))
                               (psh_limits_enr_cone_hom_to_cone_hom le h'))) x) as Hbu;
      simpl in Hbu; rewrite Hbu; clear Hbu.
    done.
  Qed.

End psh_limits_enriched.

Section psh_limits_enriched.
  Context {SI : indexT} {J} {F : functor J (PSh (OrdCat SI))}.
  Local Instance : Enriched (PSh (OrdCat SI)) (PSh (OrdCat SI)) :=
    (@self_enriched (PSh (OrdCat SI)) _).

  Global Instance psh_limits_enriched_instance : LimitsEnriched (PSh (OrdCat SI))
    := λ _ _ _ il, psh_limits_enriched il.

End psh_limits_enriched.

(* α-isomorphism *)

Record isomorphism_at
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b α} (f : (enr_hom a b) ₒ α) (g : (enr_hom b a) ₒ α) : Prop := MkIsoAt {
  iso_at_lr : (enr_comp a b a ₙ α) (f , g) = (⌜id a⌝ ₙ α) ();
  iso_at_rl : (enr_comp b a b ₙ α) (g, f) = (⌜id b⌝ ₙ α) ();
}.
Global Arguments MkIsoAt {_ _ _ _ _ _ _ _} _ _.
Global Arguments iso_at_lr {_ _ _ _ _ _ _ _} _.
Global Arguments iso_at_rl {_ _ _ _ _ _ _ _} _.

Lemma compose_along_isomorphism_at_left
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))} {b c α}
  {h : (enr_hom b c) ₒ α} {hi : (enr_hom c b) ₒ α}
  (iso : isomorphism_at h hi) [a] (f g : (enr_hom a b) ₒ α) :
  (enr_comp a b c ₙ α) (f, h) = (enr_comp a b c ₙ α) (g, h) → f = g.
Proof.
  intros Heq.
  assert ((enr_comp a c b ₙ α) ((enr_comp a b c ₙ α) (f, h), hi) =
          (enr_comp a c b ₙ α) ((enr_comp a b c ₙ α) (g, h), hi)) as Heq'.
  { rewrite Heq //. }
  epose proof (equal_f (natural_equiv_pack (enr_comp_assoc a b c b) α) ((g, h), hi)) as Hca.
  simpl in Hca; rewrite <-Hca in Heq'; clear Hca.
  epose proof (equal_f (natural_equiv_pack (enr_comp_assoc a b c b) α) ((f, h), hi)) as Hca.
  simpl in Hca; rewrite <-Hca in Heq'; clear Hca.
  rewrite !(iso_at_lr iso) in Heq'.
  epose proof (equal_f (natural_equiv_pack (enr_left_id _ _) α) (f, ())) as Hli.
  simpl in Hli; rewrite Hli in Heq'; clear Hli.
  epose proof (equal_f (natural_equiv_pack (enr_left_id _ _) α) (g, ())) as Hli.
  simpl in Hli; rewrite Hli in Heq'; clear Hli.
  apply Heq'.
Qed.

Lemma compose_along_isomorphism_at_right
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))} {a b α}
  {h : (enr_hom a b) ₒ α} {hi : (enr_hom b a) ₒ α}
  (iso : isomorphism_at h hi) [c] (f g : (enr_hom b c) ₒ α) :
  (enr_comp a b c ₙ α) (h, f) = (enr_comp a b c ₙ α) (h, g) → f = g.
Proof.
  intros Heq.
  assert ((enr_comp b a c ₙ α) (hi, (enr_comp a b c ₙ α) (h, f)) =
          (enr_comp b a c ₙ α) (hi, (enr_comp a b c ₙ α) (h, g))) as Heq'.
  { rewrite Heq //. }
  epose proof (equal_f (natural_equiv_pack (enr_comp_assoc b a b c) α) ((hi, h), f)) as Hca.
  simpl in Hca; rewrite Hca in Heq'; clear Hca.
  epose proof (equal_f (natural_equiv_pack (enr_comp_assoc b a b c) α) ((hi, h), g)) as Hca.
  simpl in Hca; rewrite Hca in Heq'; clear Hca.
  rewrite !(iso_at_rl iso) in Heq'.
  epose proof (equal_f (natural_equiv_pack (enr_right_id _ _) α) ((), f)) as Hli.
  simpl in Hli; rewrite Hli in Heq'; clear Hli.
  epose proof (equal_f (natural_equiv_pack (enr_right_id _ _) α) ((), g)) as Hli.
  simpl in Hli; rewrite Hli in Heq'; clear Hli.
  done.
Qed.

Lemma isomorphism_at_id {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))} a α :
  isomorphism_at ((⌜id a⌝ ₙ α) ()) ((⌜id a⌝ ₙ α) ()).
Proof.
  split.
  - epose proof (equal_f (natural_equiv_pack (enr_comp_comp ⌜id a⌝ ⌜id a⌝) α) ()) as Hcmp.
    simpl in Hcmp; rewrite -Hcmp; clear Hcmp.
    rewrite enr_embed_project left_id //.
  - epose proof (equal_f (natural_equiv_pack (enr_comp_comp ⌜id a⌝ ⌜id a⌝) α) ()) as Hcmp.
    simpl in Hcmp; rewrite -Hcmp; clear Hcmp.
    rewrite enr_embed_project left_id //.
Qed.

Lemma isomorphism_at_swap {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b α} {f : (enr_hom a b) ₒ α} {g : (enr_hom b a) ₒ α} :
  isomorphism_at f g → isomorphism_at g f.
Proof. intros iso; split; apply iso. Qed.

Lemma isomorphism_at_compose {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b c α} {f : (enr_hom a b) ₒ α} {g : (enr_hom b a) ₒ α}
  {f' : (enr_hom b c) ₒ α} {g' : (enr_hom c b) ₒ α} :
  isomorphism_at f g → isomorphism_at f' g' →
  isomorphism_at ((enr_comp a b c ₙ α) (f, f')) ((enr_comp c b a ₙ α) (g', g)).
Proof.
  intros iso iso'; split.
  - epose proof (equal_f (natural_equiv_pack (enr_comp_assoc a c b a) α) (((enr_comp a b c ₙ α) (f, f'), g'), g)) as Hca.
    simpl in Hca; rewrite Hca; clear Hca.
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc a b c b) α) ((f, f'), g')) as Hca.
    simpl in Hca; rewrite -Hca; clear Hca.
    rewrite (iso_at_lr iso').
    epose proof (equal_f (natural_equiv_pack (enr_left_id a b) α) (f, ())) as Hli.
    simpl in Hli; rewrite Hli; clear Hli.
    apply iso.
  - epose proof (equal_f (natural_equiv_pack (enr_comp_assoc c a b c) α) ((enr_comp c b a ₙ α) (g', g), f, f')) as Hca.
    simpl in Hca; rewrite Hca; clear Hca.
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc c b a b) α) (g', g, f)) as Hca.
    simpl in Hca; rewrite -Hca; clear Hca.
    rewrite (iso_at_rl iso).
    epose proof (equal_f (natural_equiv_pack (enr_left_id c b) α) (g', ())) as Hli.
    simpl in Hli; rewrite Hli; clear Hli.
    apply iso'.
Qed.

Record is_iso_at {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b : obj C} (f : hom a b) (α : SI) := MkIsIsoAt
{
  inv_at : (enr_hom b a) ₒ α;
  iso_at : isomorphism_at ((⌜f⌝ ₙ α) ()) inv_at;
}.
Global Arguments MkIsIsoAt {_ _ _ _ _ _ _} _ _.
Global Arguments inv_at {_ _ _ _ _ _ _} _.
Global Arguments iso_at {_ _ _ _ _ _ _} _.

Lemma compose_along_is_iso_at_left
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))} {b c α}
  {f : hom b c} (iso : is_iso_at f α) [a] (g h : (enr_hom a b) ₒ α) :
  (enr_comp a b c ₙ α) (g, (⌜f⌝ ₙ α) ()) = (enr_comp a b c ₙ α) (h, (⌜f⌝ ₙ α) ()) → g = h.
Proof.
  intros Heq.
  apply (compose_along_isomorphism_at_left (iso_at iso)); done.
Qed.

Lemma compose_along_is_iso_at_right
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))} {a b α}
  {f : hom b a} (iso : is_iso_at f α) [c] (g h : (enr_hom b c) ₒ α) :
  (enr_comp a b c ₙ α) (inv_at iso, g) = (enr_comp a b c ₙ α) (inv_at iso, h) → g = h.
Proof.
  intros Heq.
  apply (compose_along_isomorphism_at_right (isomorphism_at_swap (iso_at iso))); done.
Qed.

Lemma compose_along_is_iso_at_right'
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))} {a b α}
  {f : hom a b} (iso : is_iso_at f α) [c] (g h : (enr_hom b c) ₒ α) :
  (enr_comp a b c ₙ α) ((⌜f⌝ ₙ α) (), g) = (enr_comp a b c ₙ α) ((⌜f⌝ ₙ α) (), h) → g = h.
Proof.
  intros Heq.
  apply (compose_along_isomorphism_at_right (iso_at iso)); done.
Qed.

Lemma compose_along_is_iso_at_left'
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))} {b c α}
  {f : hom c b} (iso : is_iso_at f α) [a] (g h : (enr_hom a b) ₒ α) :
  (enr_comp a b c ₙ α) (g, inv_at iso) = (enr_comp a b c ₙ α) (h, inv_at iso) → g = h.
Proof.
  intros Heq.
  apply (compose_along_isomorphism_at_left (isomorphism_at_swap (iso_at iso))); done.
Qed.

Program Definition is_iso_at_proper {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b : obj C} {f f': hom a b} {α : SI} (fiso : is_iso_at f α) (Heq : f = f') : is_iso_at f' α :=
  MkIsIsoAt (inv_at fiso) _.
Next Obligation. intros ???????? iso <-; apply iso. Qed.
Fail Next Obligation.

Program Definition is_iso_at_compose {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b c : obj C} {f : hom a b} {g : hom b c} {α : SI}
  (fiso : is_iso_at f α) (giso : is_iso_at g α) : is_iso_at (g ∘ f) α :=
  MkIsIsoAt ((enr_comp c b a ₙ α) (inv_at giso, inv_at fiso)) _.
Next Obligation.
  intros ?????? f g ? fiso giso.
  rewrite -{1}(enr_embed_project f) -{1}(enr_embed_project g).
  rewrite enr_comp_comp /=.
  split.
  - epose proof (equal_f (natural_equiv_pack (enr_comp_assoc a b c a) α)
                   (((⌜ f ⌝ₙ α) (), (⌜ g ⌝ₙ α) ()),
                     (enr_comp c b a ₙ α) (inv_at giso, inv_at fiso))) as Hca;
      simpl in Hca; rewrite -Hca; clear Hca.
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc b c b a) α)
                   ((⌜ g ⌝ₙ α) (), inv_at giso, inv_at fiso)) as Hca;
      simpl in Hca; rewrite Hca; clear Hca.
    rewrite (iso_at_lr (iso_at giso)).
    epose proof (equal_f (natural_equiv_pack (enr_right_id b a) α) ((), inv_at fiso)) as Hli;
      simpl in Hli; rewrite Hli; clear Hli.
    apply (iso_at_lr (iso_at fiso)).
  - epose proof (equal_f (natural_equiv_pack (enr_comp_assoc c b a c) α)
                   (inv_at giso, inv_at fiso,
                     (enr_comp a b c ₙ α) ((⌜ f ⌝ₙ α) (), (⌜ g ⌝ₙ α) ()))) as Hca;
      simpl in Hca; rewrite -Hca; clear Hca.
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc b a b c) α)
                   (inv_at fiso, (⌜ f ⌝ₙ α) (), (⌜ g ⌝ₙ α) ())) as Hca;
      simpl in Hca; rewrite Hca; clear Hca.
    rewrite (iso_at_rl (iso_at fiso)).
    epose proof (equal_f (natural_equiv_pack (enr_right_id b c) α) ((), (⌜ g ⌝ₙ α) ())) as Hi;
      simpl in Hi; rewrite Hi; clear Hi.
    apply (iso_at_rl (iso_at giso)).
Qed.
Fail Next Obligation.

Program Definition is_iso_at_uncompose_l {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b c : obj C} {f : hom a b} {g : hom b c} {α : SI}
  (fiso : is_iso_at f α) (ciso : is_iso_at (g ∘ f) α) : is_iso_at g α :=
  MkIsIsoAt ((enr_comp c a b ₙ α) (inv_at ciso, (⌜f⌝ ₙ α) ())) _.
Next Obligation.
  intros ?????? f g ? fiso ciso; split.
  - apply (compose_along_is_iso_at_right' fiso).
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc a b c b) α)
                   ((⌜ f ⌝ₙ α) (), (⌜ g ⌝ₙ α) (), (enr_comp c a b ₙ α) (inv_at ciso, (⌜ f ⌝ₙ α) ()))) as Hca;
      simpl in Hca; rewrite Hca; clear Hca.
    epose proof (equal_f (natural_equiv_pack (enr_comp_comp ⌜f⌝ ⌜g⌝) α) ()) as Hcmp;
      simpl in Hcmp; rewrite -Hcmp; clear Hcmp.
    rewrite !enr_embed_project.
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc a c a b) α)
                   ((⌜ g ∘ f ⌝ₙ α) (), inv_at ciso, (⌜ f ⌝ₙ α) ())) as Hca;
      simpl in Hca; rewrite Hca; clear Hca.
    rewrite (iso_at_lr (iso_at ciso)).

    epose proof (equal_f (natural_equiv_pack (enr_right_id a b) α) ((), (⌜ f ⌝ₙ α) ())) as Hi;
      simpl in Hi; rewrite Hi; clear Hi.
    epose proof (equal_f (natural_equiv_pack (enr_left_id a b) α) ((⌜ f ⌝ₙ α) (), ())) as Hi;
      simpl in Hi; rewrite Hi; clear Hi.
    done.
  - epose proof (equal_f (natural_equiv_pack (enr_comp_assoc c a b c) α)
                   (inv_at ciso, (⌜ f ⌝ₙ α) (), (⌜ g ⌝ₙ α) ())) as Hca;
      simpl in Hca; rewrite -Hca; clear Hca.
    epose proof (equal_f (natural_equiv_pack (enr_comp_comp ⌜f⌝ ⌜g⌝) α) ()) as Hcmp;
      simpl in Hcmp; rewrite -Hcmp; clear Hcmp.
    rewrite !enr_embed_project.
    rewrite (iso_at_rl (iso_at ciso)) //.
Qed.
Fail Next Obligation.

Program Definition is_iso_at_uncompose_r {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b c : obj C} {f : hom a b} {g : hom b c} {α : SI}
  (giso : is_iso_at g α) (ciso : is_iso_at (g ∘ f) α) : is_iso_at f α :=
  MkIsIsoAt ((enr_comp _ _ _ ₙ α) ((⌜g⌝ ₙ α) (), inv_at ciso)) _.
Next Obligation.
  intros ?????? f g ? giso ciso; split.
  - epose proof (equal_f (natural_equiv_pack (enr_comp_assoc a b c a) α)
                   ((⌜ f ⌝ₙ α) (), (⌜ g ⌝ₙ α) (), inv_at ciso)) as Hca;
      simpl in Hca; rewrite Hca; clear Hca.
    epose proof (equal_f (natural_equiv_pack (enr_comp_comp ⌜f⌝ ⌜g⌝) α) ()) as Hcmp;
      simpl in Hcmp; rewrite -Hcmp; clear Hcmp.
    rewrite !enr_embed_project.
    rewrite (iso_at_lr (iso_at ciso)) //.
  - apply (compose_along_is_iso_at_left giso).
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc b c a b) α)
                   ((⌜ g ⌝ₙ α) (), inv_at ciso, (⌜ f ⌝ₙ α) ())) as Hca;
      simpl in Hca; rewrite -Hca; clear Hca.
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc b c b c) α)
                   ((⌜ g ⌝ₙ α) (), (enr_comp c a b ₙ α) (inv_at ciso, (⌜ f ⌝ₙ α) ()), (⌜ g ⌝ₙ α) ())) as Hca;
      simpl in Hca; rewrite -Hca; clear Hca.
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc c a b c) α)
                   (inv_at ciso, (⌜ f ⌝ₙ α) (), (⌜ g ⌝ₙ α) ())) as Hca;
      simpl in Hca; rewrite -Hca; clear Hca.
    epose proof (equal_f (natural_equiv_pack (enr_comp_comp ⌜f⌝ ⌜g⌝) α) ()) as Hcmp;
      simpl in Hcmp; rewrite -Hcmp; clear Hcmp.
    rewrite !enr_embed_project.
    rewrite (iso_at_rl (iso_at ciso)).
    epose proof (equal_f (natural_equiv_pack (enr_right_id b c) α) ((), (⌜ g ⌝ₙ α) ())) as Hi;
      simpl in Hi; rewrite Hi; clear Hi.
    epose proof (equal_f (natural_equiv_pack (enr_left_id b c) α) ((⌜ g ⌝ₙ α) (), ())) as Hi;
      simpl in Hi; rewrite Hi; clear Hi.
    done.
Qed.
Fail Next Obligation.

Program Definition is_iso_at_downwards {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b : obj C} (f : hom a b) {α β} (Hle : β ⪯ α) (iso : is_iso_at f α) :
  is_iso_at f β :=
  MkIsIsoAt (((enr_hom b a) ₕ Hle) (inv_at iso)) _.
Next Obligation.
  intros ? ? ? a b f α β Hle iso.
  split.
  - pose proof ((_ : Proper ((=) ==> (=)) (enr_hom a a ₕ Hle)) _ _ (iso_at_lr (iso_at iso)))
      as Hlr.
    epose proof (equal_f (naturality (enr_comp a b a) Hle)
                   ((⌜ f ⌝ₙ α) (), inv_at iso)) as Hn;
      simpl in Hn; rewrite -Hn /= in Hlr; clear Hn.
    rewrite /hom_prod /= in Hlr.
    epose proof (equal_f (naturality ⌜ f ⌝ Hle) ()) as Hn;
      simpl in Hn; rewrite -Hn /= in Hlr; clear Hn.
    epose proof (equal_f (naturality ⌜ id a ⌝ Hle) ()) as Hn;
      simpl in Hn; rewrite -Hn /= in Hlr; clear Hn.
    done.
  - pose proof ((_ : Proper ((=) ==> (=)) (enr_hom b b ₕ Hle)) _ _ (iso_at_rl (iso_at iso)))
      as Hlr.
    epose proof (equal_f (naturality (enr_comp b a b) Hle) (inv_at iso, (⌜ f ⌝ₙ α) ())) as Hn;
      simpl in Hn; rewrite -Hn /= in Hlr; clear Hn.
    rewrite /hom_prod /= in Hlr.
    epose proof (equal_f (naturality ⌜ f ⌝ Hle) ()) as Hn;
      simpl in Hn; rewrite -Hn /= in Hlr; clear Hn.
    epose proof (equal_f (naturality ⌜ id b ⌝ Hle) ()) as Hn;
      simpl in Hn; rewrite -Hn /= in Hlr; clear Hn.
    done.
Qed.
Fail Next Obligation.

Definition enr_hom_eq {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a a' b b' : obj C} (Heq : a = a') (Heq' : b = b') α :
  enr_hom a b ₒ α = enr_hom a' b' ₒ α :=
  match Heq in _ = z return enr_hom a b ₒ α = enr_hom z b' ₒ α with
  | eq_refl =>
      match Heq' in _ = w return enr_hom a b ₒ α = enr_hom a w ₒ α with
      | eq_refl => eq_refl
      end
  end.

Definition enr_hom_trans {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a a' b b' : obj C} (Heq : a = a') (Heq' : b = b') {α} (f : enr_hom a b ₒ α) :
  enr_hom a' b' ₒ α := typ_conv (enr_hom_eq Heq Heq' α) f.

Program Definition iso_at_hom_trans {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a a' b b' : obj C} (Heq : a = a') (Heq' : b = b') {f : hom a b} {α} (iso : is_iso_at f α) :
  is_iso_at (hom_trans Heq Heq' f) α :=
  MkIsIsoAt (enr_hom_trans Heq' Heq (inv_at iso)) _.
Next Obligation.
  intros; split.
  - destruct Heq; destruct Heq'; rewrite /enr_hom_trans /=.
    apply (iso_at_lr (iso_at iso)).
  - destruct Heq; destruct Heq'; rewrite /enr_hom_trans /=.
    apply (iso_at_rl (iso_at iso)).
Qed.
Fail Next Obligation.

Program Definition iso_at_hom_trans' {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a a' b b' : obj C} (Heq : a = a') (Heq' : b = b') {f : hom a b} {α}
  (iso : is_iso_at (hom_trans Heq Heq' f) α) :
  is_iso_at f α :=
  MkIsIsoAt (enr_hom_trans (eq_sym Heq') (eq_sym Heq) (inv_at iso)) _.
Next Obligation.
  intros; split.
  - destruct Heq; destruct Heq'; rewrite /enr_hom_trans /=.
    apply (iso_at_lr (iso_at iso)).
  - destruct Heq; destruct Heq'; rewrite /enr_hom_trans /=.
    apply (iso_at_rl (iso_at iso)).
Qed.
Fail Next Obligation.

Program Definition is_iso_at_id {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  (a : obj C) α : is_iso_at (id a) α :=
  MkIsIsoAt ((⌜id a⌝ₙ α) ()) _.
Next Obligation.
  intros; split.
  - epose proof (equal_f (natural_equiv_pack (enr_left_id a a) α) ((⌜ id a ⌝ₙ α) (), ())) as Hi;
      simpl in Hi; rewrite Hi; clear Hi.
    done.
  - epose proof (equal_f (natural_equiv_pack (enr_left_id a a) α) ((⌜ id a ⌝ₙ α) (), ())) as Hi;
      simpl in Hi; rewrite Hi; clear Hi.
    done.
Qed.
Fail Next Obligation.

(* despite iso_at being downwards closed, we generalize it to apply down downsets to also support
   downsets that do not have a maximal ordinal. *)

Definition is_iso_upto {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b : obj C} (f : hom a b) (dsp : downset_pred SI) :=
  ∀ β : downset dsp, is_iso_at f β.

Lemma is_iso_upto_functorial
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b : obj C} (f : hom a b) (dsp : downset_pred SI)
  (iso : is_iso_upto f dsp) [α β : downset dsp] (Hle : β ⪯ α) :
  inv_at (iso β) = (enr_hom b a ₕ Hle) (inv_at (iso α)).
Proof.
  apply (compose_along_is_iso_at_right' (iso β)).
  rewrite (iso_at_lr (iso_at (iso β))).
  epose proof (equal_f (naturality ⌜ f ⌝ Hle) ()) as Hn;
    simpl in Hn; rewrite Hn; clear Hn.
  epose proof (equal_f (naturality (enr_comp a b a) Hle)
                 (((⌜ f ⌝ₙ (ds_idx α)) ()), (inv_at (iso α)))) as Hn;
    rewrite /= /hom_prod /= in Hn; rewrite Hn; clear Hn.
  rewrite (iso_at_lr (iso_at (iso α))).
  epose proof (equal_f (naturality ⌜ id a ⌝ Hle) ()) as Hn;
    simpl in Hn; rewrite -Hn; clear Hn.
  done.
Qed.

Program Definition is_iso_upto_inv_embedded
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b : obj C} (f : hom a b) (dsp : downset_pred SI)
  (iso : is_iso_upto f dsp) :
  hom (PSh (OrdDSCat dsp))
    (lift_func dsp (1ₒ : PreSheaf _))
    (lift_func dsp (enr_hom b a)) :=
  MkNat (λ α, λ _, inv_at (iso α)) _.
Next Obligation.
  repeat intros ?.
  extensionality x.
  apply is_iso_upto_functorial.
Qed.

Definition is_iso_upto_total_inv_embedded
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b : obj C} (f : hom a b) (iso : is_iso_upto f (total_dsp SI)) :
  hom (1ₒ) (enr_hom b a) :=
  unlift_natural (is_iso_upto_inv_embedded f _ iso).

Definition is_iso_upto_total_inv
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b : obj C} (f : hom a b) (iso : is_iso_upto f (total_dsp SI)) :
  hom b a := ⌞is_iso_upto_total_inv_embedded f iso⌟.

Lemma is_iso_upto_total_isomorphism {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b : obj C} (f : hom a b) (iso : is_iso_upto f (total_dsp SI)) :
  isomorphism f (is_iso_upto_total_inv f iso).
Proof.
  split.
  - rewrite -{1}(enr_embed_project f).
    apply enr_embed_inj.
    apply natural_equiv_unpack; intros α.
    extensionality x.
    rewrite /is_iso_upto_total_inv /is_iso_upto_total_inv_embedded.
    rewrite enr_comp_comp /=.
    destruct x.
    apply ((iso_at_lr (iso_at (iso (MkDS (ds_idx := α) (total_dsp SI) (squash I)))))).
  - rewrite -{2}(enr_embed_project f).
    apply enr_embed_inj.
    apply natural_equiv_unpack; intros α.
    extensionality x.
    destruct x.
    rewrite /is_iso_upto_total_inv /is_iso_upto_total_inv_embedded.
    rewrite enr_comp_comp /=.
    apply iso_at_rl, (iso (MkDS (total_dsp SI) (squash I))).
Qed.

Definition is_iso_upto_total {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {a b : obj C} (f : hom a b) (iso : is_iso_upto f (total_dsp SI)) :
  isomorphic a b := MkIsoIc _ _ (is_iso_upto_total_isomorphism f iso).

Program Definition is_iso_at_func
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  (F : functor C C) `{!EnrichedFunctor F}
  {a b : obj C} (f : hom a b) {α} (iso : is_iso_at f α) :
  is_iso_at (F ₕ f) α :=
  MkIsIsoAt ((enr_func_h_map F b a ₙ α) (inv_at iso)) _.
Next Obligation.
  intros ??? F ? a b f α iso; simpl in *.
  split.
  - rewrite -{1}(enr_embed_project f) enr_func_h_map_is_h_map /=.

    epose proof (equal_f (natural_equiv_pack (enr_func_h_map_comp F a b a) α)
                   (((⌜ f ⌝ₙ α) ()), (inv_at iso)))
      as Hcmp; simpl in Hcmp; rewrite -Hcmp; clear Hcmp.
    rewrite (iso_at_lr (iso_at iso)).
    epose proof (equal_f (natural_equiv_pack (enr_func_h_map_id F a) α) ()); simpl in *; done.
  - rewrite -{2}(enr_embed_project f) enr_func_h_map_is_h_map /=.
    epose proof (equal_f (natural_equiv_pack (enr_func_h_map_comp F b a b) α)
                   ((inv_at iso), ((⌜ f ⌝ₙ α) ())))
      as Hcmp; simpl in Hcmp; rewrite -Hcmp; clear Hcmp.
    rewrite (iso_at_rl (iso_at iso)).
    epose proof (equal_f (natural_equiv_pack (enr_func_h_map_id F b) α) ());
      simpl in *; done.
Qed.
Fail Next Obligation.

Definition is_iso_upto_func
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  (F : functor C C) `{!EnrichedFunctor F}
  {a b : obj C} (f : hom a b) {dsp} (iso : is_iso_upto f dsp) : is_iso_upto (F ₕ f) dsp :=
  λ α, is_iso_at_func F f (iso α).

(* TODO: MOVE *)
Lemma compose_along_iso_right_typ {A B} (iso : A ≃@{Typ} B) (x y : A) :
  forward iso x = forward iso y → x = y.
Proof.
  intros Heq.
  change x with (id A x); change y with (id A y).
  rewrite -(iso_lr (is_iso iso)) /= Heq //.
Qed.

Program Definition iso_upto_contr_func
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  (F : functor C C) `{!LocallyContractiveFunctor F}
  {a b : obj C} (f : hom a b) {dsp} (iso : is_iso_upto f dsp) α
  (Hdsp : ∀ β, β ≺ α → dsp β) : is_iso_at (F ₕ f) α :=
  MkIsIsoAt
    ((contr_func_h_map F b a ₙ α)
       (into_later_psh _
          (λ β (Hβ : β ≺ α), inv_at (iso (MkDS dsp (squash (Hdsp _ Hβ))))) _))
    _.
Next Obligation.
  intros ???????? dsp ?? Hdsp β γ Hβ Hγ Hle; simpl in *.
  symmetry.
  apply (is_iso_upto_functorial _ _ _
    (Hle : (MkDS dsp (squash (Hdsp _ Hβ))) ⪯ (MkDS dsp (squash (Hdsp _ Hγ))))).
Qed.
Next Obligation.
  intros ??? F ? a b f dsp iso α Hdsp; simpl in *.
  split.
  - rewrite -{1}(enr_embed_project f) enr_func_h_map_is_h_map /=.
    rewrite -enr_func_h_map_id.
    rewrite !contr_func_h_map_is_h_map /=.
    epose proof (equal_f (natural_equiv_pack (contr_func_h_map_comp F a b a) α)
      (_, _))
      as Hcmp; simpl in Hcmp; rewrite <-Hcmp; clear Hcmp.
    f_equiv.
    apply equiv_of_into_later_psh.
    intros β Hβ.
    rewrite -(psh_naturality (next ₙ enr_hom _ _)) /=.
    epose proof (psh_naturality (⌜id _⌝)) as Hn;
      simpl in Hn; rewrite <-Hn; clear Hn.
    epose proof (psh_naturality (later ₕ enr_comp _ _ _)) as Hn;
      simpl in Hn; rewrite <-Hn; clear Hn.
    epose proof (psh_naturality (backward (later_prod (enr_hom a b) (enr_hom b a))))
      as Hn; simpl in Hn; rewrite <-Hn; simpl; clear Hn.
    rewrite /hom_prod /=.
    rewrite -(psh_naturality (next ₙ enr_hom _ _)) /=.
    epose proof (psh_naturality (⌜f⌝)) as Hn;
      simpl in Hn; rewrite -Hn; clear Hn.
    pose proof (side_of_later' (enr_hom b a) (MkDS (lt_dsp α) (squash Hβ))) as Hsdl;
      simpl in Hsdl.
    replace (unsquash _) with Hβ in Hsdl by apply proof_irrel.
    rewrite Hsdl /=; clear Hsdl.
    rewrite into_later_side_psh /=.
    apply (compose_along_iso_right_typ
             (natural_iso_proj
                (natural_iso_proj earlier_later_nat_iso (enr_hom a a)) β)); simpl.
    epose proof (equal_f (natural_equiv_pack
                   (naturality (forward (earlier_later_nat_iso (SI := SI) (C := Typ)))
                      (enr_comp a b a)) β)) as Hn;
      rewrite /= h_map_id /= in Hn; rewrite Hn; clear Hn.
    epose proof (equal_f (natural_equiv_pack
                            (earlier_later_earlier_later_prod
                               (enr_hom a b) (enr_hom b a)) β) (_, _)) as Heq.
    simpl in Heq; unfold hom_prod in Heq; simpl in Heq;
    rewrite !h_map_id in Heq; simpl in Heq; rewrite ->Heq; clear Heq.
    epose proof (equal_f
                   (natural_equiv_pack
                      (iso_rl (is_iso (natural_iso_proj (earlier_later_nat_iso)
                                         (enr_hom b a)))) β)) as Hfb;
      simpl in Hfb; rewrite Hfb; clear Hfb.
    epose proof (equal_f
                   (natural_equiv_pack
                      (forward_earlier_later_nat_iso_next (C := Typ) (enr_hom a a)) β)) as Heq;
      simpl in Heq; rewrite !h_map_id in Heq; simpl in Heq; rewrite Heq; clear Heq.
    epose proof (equal_f (naturality ⌜ id a ⌝ (index_lt_le_subrel β (succ β) (index_succ_greater β)))) as Hn;
      simpl in Hn; rewrite -Hn; clear Hn.
    epose proof (equal_f
                   (natural_equiv_pack
                      (forward_earlier_later_nat_iso_next (C := Typ)
                         (enr_hom a b)) β)) as Heq;
      simpl in Heq; rewrite h_map_id in Heq; simpl in Heq; rewrite Heq; clear Heq.
    epose proof (equal_f
                   (naturality ⌜ f ⌝
                      (index_lt_le_subrel β (succ β) (index_succ_greater β)))) as Hn;
      simpl in Hn; rewrite -Hn; clear Hn.
    apply (iso_at_lr (iso_at (iso (MkDS dsp (squash (Hdsp _ Hβ)))))).
  - rewrite -{3}(enr_embed_project f) enr_func_h_map_is_h_map /=.
    rewrite -enr_func_h_map_id.
    rewrite !contr_func_h_map_is_h_map /=.
    epose proof (equal_f ((natural_equiv_pack (contr_func_h_map_comp F b a b)) α) (_, _))
      as Hcmp; simpl in Hcmp.
    rewrite <-Hcmp; clear Hcmp.
    f_equiv.
    apply equiv_of_into_later_psh.
    intros β Hβ.
    rewrite -(psh_naturality (next ₙ enr_hom _ _)) /=.
    epose proof (psh_naturality (⌜id _⌝)) as Hn;
      simpl in Hn; rewrite <-Hn; clear Hn.
    epose proof (psh_naturality (later ₕ enr_comp _ _ _)) as Hn;
      simpl in Hn; rewrite <-Hn; clear Hn.
    epose proof (psh_naturality (backward (later_prod (enr_hom b a) (enr_hom a b))))
      as Hn; simpl in Hn; rewrite -Hn /=; clear Hn.
    rewrite /hom_prod /=.
    rewrite -(psh_naturality (next ₙ enr_hom _ _)) /=.
    epose proof (psh_naturality (⌜f⌝)) as Hn;
      simpl in Hn; rewrite -Hn; clear Hn.
    pose proof (side_of_later' (enr_hom b a) (MkDS (lt_dsp α) (squash Hβ))) as Hsdl.
    replace (unsquash _) with Hβ in Hsdl by apply proof_irrel.
    simpl in Hsdl; rewrite Hsdl /=; clear Hsdl.
    rewrite into_later_side_psh /=.
    apply (compose_along_iso_right_typ
             (natural_iso_proj
                (natural_iso_proj earlier_later_nat_iso (enr_hom b b)) β)); simpl.
    epose proof (equal_f
                   (natural_equiv_pack
                      (naturality (forward (earlier_later_nat_iso (SI := SI) (C := Typ)))
                         (enr_comp b a b)) β) _) as Hn;
      simpl in Hn; rewrite h_map_id in Hn; simpl in Hn; rewrite ->Hn; clear Hn.

    epose proof (equal_f
                   (natural_equiv_pack
                      (earlier_later_earlier_later_prod
                         (enr_hom b a) (enr_hom a b)) β) (_, _)) as Heq;
      simpl in Heq; unfold hom_prod in Heq; simpl in Heq.
    rewrite !h_map_id in Heq; simpl in Heq. rewrite ->Heq; clear Heq.
    epose proof (equal_f
                   (natural_equiv_pack
                      (iso_rl (is_iso (natural_iso_proj
                                         (earlier_later_nat_iso)
                                         (enr_hom b a)))) β)) as Hfb;
      simpl in Hfb; rewrite Hfb; clear Hfb.
    epose proof (equal_f
                   (natural_equiv_pack
                      (forward_earlier_later_nat_iso_next (C := Typ) (enr_hom b b)) β)) as Heq.
    simpl in Heq; rewrite h_map_id in Heq; simpl in Heq; rewrite Heq; clear Heq.
    epose proof (equal_f
                   (naturality ⌜ id b ⌝
                      (index_lt_le_subrel β (succ β) (index_succ_greater β)))) as Hn.
    simpl in Hn; rewrite <-Hn; clear Hn.
    epose proof (equal_f
                   (natural_equiv_pack
                      (forward_earlier_later_nat_iso_next (C := Typ) (enr_hom a b)) β)) as Heq.
    simpl in Heq; rewrite h_map_id in Heq; rewrite Heq; clear Heq.
    epose proof (equal_f
                   (naturality ⌜ f ⌝
                      (index_lt_le_subrel β (succ β) (index_succ_greater β)))) as Hn.
    simpl in Hn; rewrite -Hn; clear Hn.
    apply (iso_at_rl (iso_at (iso (MkDS dsp (squash (Hdsp _ Hβ)))))).
Qed.
Fail Next Obligation.

(* move *)
Definition strongly_connected_category (C : category) := ∀ c c' : obj C, hom c c' + hom c' c.
Definition mere_preorder (C : category) : Prop := ∀ a b (f f' : hom C a b), f = f'.

Program Definition strongly_connected_iso_at_diagram_enr_cone
  {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {J} (Hsc : strongly_connected_category J) (Hmp : mere_preorder J) {F : functor J C}
  {α} (isos : ∀ j j' (f : hom J j j'), is_iso_at (F ₕ f) α)
  j : enr_cone F α :=
  MkEnrCone
    (F ₒ j)
    (λ j',
      match Hsc j j' return enr_hom (F ₒ j) (F ₒ j') ₒ α with
      | inl f => (⌜F ₕ f⌝ ₙ α) ()
      | inr f => inv_at (isos _ _ f)
      end)
    _.
Next Obligation.
  intros ? ? ? ? Hsc Hmp F α isos j j' j'' f; simpl in *.
  destruct (Hsc j j') as [h|h]; destruct (Hsc j j'') as [h'|h'].
  - epose proof (equal_f (natural_equiv_pack (enr_comp_comp ⌜ F ₕ h ⌝ ⌜ F ₕ f ⌝) α)) as Hcmp.
    simpl in Hcmp; rewrite <-Hcmp; clear Hcmp.
    rewrite !enr_embed_project -h_map_comp (Hmp _ _ h' (f ∘ h)); done.
  - epose proof (equal_f (natural_equiv_pack (enr_comp_comp ⌜ F ₕ _ ⌝ ⌜ F ₕ _ ⌝) α)) as Hcmp;
      simpl in Hcmp; rewrite <-Hcmp; clear Hcmp.
    rewrite !enr_embed_project -h_map_comp.
    apply (compose_along_is_iso_at_right' (isos _ _ h')).
    rewrite (iso_at_lr (iso_at (isos _ _ h'))).
    epose proof (equal_f (natural_equiv_pack (enr_comp_comp ⌜ F ₕ _ ⌝ ⌜ F ₕ _ ⌝) α)) as Hcmp;
      simpl in Hcmp; rewrite <-Hcmp; clear Hcmp.
    rewrite !enr_embed_project -h_map_comp.
    rewrite (Hmp _ _ (f ∘ h ∘ h') (id _)) h_map_id //.
  - apply (compose_along_is_iso_at_right' (isos _ _ h)).
    epose proof (equal_f (natural_equiv_pack (enr_comp_comp ⌜ F ₕ _ ⌝ ⌜ F ₕ _ ⌝) α)) as Hcmp;
      simpl in Hcmp; rewrite <-Hcmp; clear Hcmp.
    rewrite !enr_embed_project -h_map_comp.
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc _ _ _ _) _) ((_, _), _)) as Hca;
      simpl in Hca; rewrite ->Hca; clear Hca.
    rewrite (iso_at_lr (iso_at (isos _ _ h))).
    epose proof (equal_f (natural_equiv_pack (enr_right_id _ _) _) ((), _)) as Hi;
      simpl in Hi; rewrite ->Hi; clear Hi.
    rewrite (Hmp _ _ (h' ∘ h) f) //.
  - apply (compose_along_is_iso_at_right' (isos _ _ h)).
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc _ _ _ _) _) ((_, _), _)) as Hca;
      simpl in Hca; rewrite ->Hca; clear Hca.
    rewrite (iso_at_lr (iso_at (isos _ _ h))).
    epose proof (equal_f (natural_equiv_pack (enr_right_id _ _) _) ((), _)) as Hi;
      simpl in Hi; rewrite ->Hi; clear Hi.
    apply (compose_along_is_iso_at_left (isos _ _ h')).
    epose proof (equal_f (natural_equiv_pack (enr_comp_assoc _ _ _ _) _) ((_, _), _)) as Hca;
      simpl in Hca; rewrite <-Hca; clear Hca.
    rewrite (iso_at_rl (iso_at (isos _ _ h'))).
    epose proof (equal_f (natural_equiv_pack (enr_left_id _ _) α) (_, ())) as Hi;
      simpl in Hi; rewrite ->Hi; clear Hi.
    epose proof (equal_f (natural_equiv_pack (enr_comp_comp ⌜ F ₕ _ ⌝ ⌜ F ₕ _ ⌝) α)) as Hcmp;
      simpl in Hcmp; rewrite <-Hcmp; clear Hcmp.
    rewrite !enr_embed_project -h_map_comp.
    rewrite (Hmp _ _ (h' ∘ f) h) //.
Qed.

Program Definition limit_side_iso_at' {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  {J} (Hsc : strongly_connected_category J) (Hmp : mere_preorder J) {F : functor J C}
  {c} {il : is_limit F c} (eil : enr_limit il)
  {α} (isos : ∀ j j' (f : hom J j j'), is_iso_at (F ₕ f) α)
  j : is_iso_at (ic_side (il_is_cone il) j) α :=
  MkIsIsoAt
    (enr_cone_hom_map
       (enr_limit_hom (eil α)
          (strongly_connected_iso_at_diagram_enr_cone Hsc Hmp isos j)))
    _.
Next Obligation.
  intros ???? Hsc Hmp ? ? il eil α isos j.
  split.
  - apply (enr_hom_to_limit_unique (eil α)
      (cone_to_enr_cone (cone_of_is_cone (il_is_cone il)) α)).
    + intros j'; simpl.
      epose proof (equal_f
                     (natural_equiv_pack
                        (enr_comp_assoc _ _ _ _) _) ((_, _), _)) as Hca;
        simpl in Hca; rewrite <-Hca; clear Hca.
      pose proof (enr_cone_hom_commutes
        (enr_limit_hom (eil α)
           (strongly_connected_iso_at_diagram_enr_cone Hsc Hmp isos j))) as Hchc;
      simpl in Hchc; rewrite -Hchc; clear Hchc.
      destruct Hsc.
      * epose proof (equal_f
                       (natural_equiv_pack
                          (enr_comp_comp ⌜ _ ⌝ ⌜ _ ⌝) _) ()) as Hcmp;
          simpl in Hcmp; rewrite <-Hcmp; clear Hcmp.
        rewrite !enr_embed_project.
        rewrite -ic_side_commutes //.
      * apply (compose_along_is_iso_at_left (isos _ _ h)).
        epose proof (equal_f
                       (natural_equiv_pack
                          (enr_comp_comp ⌜ _ ⌝ ⌜ _ ⌝) _) ()) as Hcmp;
          simpl in Hcmp; rewrite <-Hcmp; clear Hcmp.
        rewrite !enr_embed_project.
        rewrite -ic_side_commutes //.
        epose proof (equal_f
                       (natural_equiv_pack
                          (enr_comp_assoc _ _ _ _) _) ((_, _), _)) as Hca;
        simpl in Hca; rewrite <-Hca; clear Hca.
        rewrite (iso_at_rl (iso_at (isos _ _ h))).
        epose proof (equal_f
                       (natural_equiv_pack
                          (enr_left_id _ _) _) (_, ())) as Hi;
          simpl in Hi; rewrite ->Hi; clear Hi.
        done.
    + intros j'; simpl.
      epose proof (equal_f
                     (natural_equiv_pack
                        (enr_right_id _ _) _) ((), _)) as Hi;
        simpl in Hi; rewrite ->Hi; clear Hi.
      done.
  - pose proof (enr_cone_hom_commutes
      (enr_limit_hom (eil α)
         (strongly_connected_iso_at_diagram_enr_cone Hsc Hmp isos j))) as Hchc;
      simpl in Hchc; rewrite -Hchc; clear Hchc.
    destruct Hsc.
    + rewrite (Hmp _ _ h (id _)) h_map_id //.
    + apply (compose_along_is_iso_at_left (isos _ _ h)).
      rewrite (iso_at_rl (iso_at (isos _ _ h))).
      epose proof (equal_f
                     (natural_equiv_pack
                        (enr_right_id _ _) _) ((), _)) as Hi;
        simpl in Hi; rewrite ->Hi; clear Hi.
      rewrite (Hmp _ _ h (id _)) h_map_id //.
Qed.
Fail Next Obligation.

Definition limit_side_iso_at {SI : indexT} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  `{!LimitsEnriched C}
  {J} (Hsc : strongly_connected_category J) (Hmp : mere_preorder J) {F : functor J C}
  {c} (il : is_limit F c)
  α (isos : ∀ j j' (f : hom J j j'), is_iso_at (F ₕ f) α)
  j : is_iso_at (ic_side (il_is_cone il) j) α :=
  limit_side_iso_at' Hsc Hmp (limits_enriched il) isos j.

#[projections(primitive = yes)] Record downset_up {SI} (dsp : downset_pred SI) α :=
  MkDSUP { ds_up_idx :> index_car SI; ds_up_in_dsp : squashed (dsp ds_up_idx); ds_up_up : α ⪯ ds_up_idx }.

Global Arguments MkDSUP {_ _ _ _} _ _.
Global Arguments ds_up_idx {_ _ _} _.
Global Arguments ds_up_in_dsp {_ _ _} _.
Global Arguments ds_up_up {_ _ _} _.

Definition downset_up_to_downset {SI} {dsp : downset_pred SI} {α} (γ : downset_up dsp α) :
  downset dsp := MkDS (ds_up_in_dsp γ).

Definition downset_to_downset_up {SI} {dsp : downset_pred SI} {α}
  (γ : downset dsp) (Hle : α ⪯ γ) : downset_up dsp α := MkDSUP (ds_in_dsp γ) Hle.

Lemma downset_to_downset_up_eq {SI} {dsp : downset_pred SI} {α}
  (γ : downset dsp) (Hle : α ⪯ γ) :
  downset_up_to_downset (downset_to_downset_up γ Hle) = γ.
Proof. by destruct γ. Qed.

Lemma downset_to_downset_up_eq_eq {SI} {dsp : downset_pred SI} {α}
  {γ} (Hγ : dsp γ) (Hle : α ⪯ γ) :
  downset_to_downset_up_eq (MkDS (squash Hγ)) Hle = eq_refl.
Proof. apply proof_irrelevance. Qed.

Program Definition OrdDSUpCat {SI} (dsp : downset_pred SI) α : category :=
  MkCat (downset_up dsp α) (λ β γ, β ⪯ γ)
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

Program Definition ord_ds_up_cat_inject {SI} (dsp : downset_pred SI) α :
  functor (OrdDSUpCat dsp α) (OrdDSCat dsp) :=
  MkFunc downset_up_to_downset (λ _ _ f, f) _ _.
Solve All Obligations with done.
Fail Next Obligation.

Program Definition is_limit_up_cone {SI} {dsp : downset_pred SI}
  {C} {F : functor ((OrdDSCat dsp)ᵒᵖ) C} (cn : cone F) α:
  cone (functor_compose (opposite_func (ord_ds_up_cat_inject dsp α)) F) :=
  (MkCone (vertex cn) (λ j, side cn (downset_up_to_downset j)) _).
Next Obligation. repeat intros ?; apply (side_commutes cn). Qed.
Fail Next Obligation.

Program Definition is_limit_up_make_cone {SI} {dsp : downset_pred SI}
  {C} {F : functor ((OrdDSCat dsp)ᵒᵖ) C} {α} (Hα : dsp α)
  (cn : cone (functor_compose (opposite_func (ord_ds_up_cat_inject dsp α)) F)) :
  cone F :=
  MkCone (vertex cn)
    (λ j,
      match index_le_lt_dec α j return hom (vertex cn) (F ₒ j) with
      | left Hle =>
          match downset_to_downset_up_eq j Hle in _ = Z return hom (vertex cn) (F ₒ Z) with
            eq_refl => side cn (MkDSUP (ds_in_dsp j) Hle)
          end
      | right Hlt => (@h_map _ _ F (MkDS (squash Hα)) j (index_lt_le_subrel _ _ Hlt)) ∘
                       side cn (MkDSUP (squash Hα) (reflexivity _))
      end)
    _.
Next Obligation.
  intros ???? α Hα cn j j' f; simpl in *.
  destruct (index_le_lt_dec α j) as [Hlej|Hltj];
    destruct (index_le_lt_dec α j') as [Hlej'|Hltj'].
  - destruct j as [j Hj]; destruct j' as [j' Hj'];
      rewrite (downset_to_downset_up_eq_eq (unsquash Hj) _) /=; simpl in *.
    rewrite (downset_to_downset_up_eq_eq (unsquash Hj') _) /=; simpl in *.
    apply (@side_commutes _ _ _ cn (MkDSUP Hj Hlej) (MkDSUP Hj' Hlej') f).
  - destruct j as [j Hj];
      rewrite (downset_to_downset_up_eq_eq (unsquash Hj) _) /=; simpl in *.
    rewrite (@side_commutes _ _ _ cn (MkDSUP Hj Hlej) (MkDSUP (squash Hα) (reflexivity _)) Hlej).
    rewrite /= -comp_assoc -h_map_comp.
    repeat f_equiv; apply proof_irrel.
  - assert (j' ≺ α).
    { eapply index_le_lt_trans; eauto. }
    exfalso; eapply index_le_lt_contradict; eauto.
  - rewrite /= -comp_assoc -h_map_comp.
    repeat f_equiv; apply proof_irrel.
Qed.
Fail Next Obligation.

Program Definition is_limit_up_cone_hom {SI} {dsp : downset_pred SI} {C} {α} (Hα : dsp α)
  {F : functor ((OrdDSCat dsp)ᵒᵖ) C}
  (cn : cone F) (cn' : cone (functor_compose (opposite_func (ord_ds_up_cat_inject dsp α)) F))
  (h : cone_hom (is_limit_up_make_cone Hα cn') cn) :
  cone_hom cn' (cone_of_is_cone (cone_is_cone (is_limit_up_cone cn α))) :=
  MkConeHom (cone_hom_map h) _.
Next Obligation.
  intros ??? α Hα F cn cn' h j; simpl in *.
  pose proof (cone_hom_commutes h (downset_up_to_downset j)) as Hcm.
  simpl in *.
  destruct index_le_lt_dec as [Hle|Hlt].
  - destruct j as [j Hj Hjle]; simpl in *.
    rewrite (downset_to_downset_up_eq_eq (unsquash Hj) Hle) /= in Hcm.
    replace Hjle with Hle by apply proof_irrel.
    rewrite -Hcm.
    reflexivity.
  - rewrite -Hcm.
    rewrite -side_commutes //.
Qed.

Program Definition is_limit_up_cone_hom' {SI} {dsp : downset_pred SI} {C} {α} (Hα : dsp α)
  {F : functor ((OrdDSCat dsp)ᵒᵖ) C}
  (cn : cone (functor_compose (opposite_func (ord_ds_up_cat_inject dsp α)) F))
  (cn' : cone F)
  (h : cone_hom cn (cone_of_is_cone (cone_is_cone (is_limit_up_cone cn' α)))) :
   cone_hom (is_limit_up_make_cone Hα cn) cn' :=
  MkConeHom (cone_hom_map h) _.
Next Obligation.
  intros ??? α Hα F cn cn' h j; simpl in *.
  destruct index_le_lt_dec as [Hle|Hlt].
  - pose proof (cone_hom_commutes h (downset_to_downset_up j Hle)) as Hcm.
    destruct j as [j Hj]; simpl in *.
    rewrite (downset_to_downset_up_eq_eq (unsquash Hj)) /=.
    rewrite Hcm //.
  - rewrite (cone_hom_commutes h (MkDSUP (squash Hα) (reflexivity _))).
    rewrite -comp_assoc.
    rewrite -(side_commutes cn') //.
Qed.

Program Definition is_limit_up {SI} {dsp : downset_pred SI} {C c}
  {F : functor ((OrdDSCat dsp)ᵒᵖ) C} (il : is_limit F c) {α} (Hα : dsp α) :
  is_limit (functor_compose (opposite_func (ord_ds_up_cat_inject dsp α)) F) c :=
  MkIsLimit
    (cone_is_cone (is_limit_up_cone (cone_of_is_cone (il_is_cone il)) α))
    (MkIsTerm _ (λ cn', is_limit_up_cone_hom Hα _ _
       (bang (il_is_limiting_cone _ _ il) (is_limit_up_make_cone Hα cn'))) _).
Next Obligation.
  intros ???????? cn f; simpl in *.
  rewrite -(bang_unique (il_is_limiting_cone _ _ il) (is_limit_up_cone_hom' Hα cn
                                                        (cone_of_is_cone (il_is_cone il)) f)).
  by apply cone_hom_equiv_unpack.
Qed.
Fail Next Obligation.

Lemma ord_ds_up_cat_strongly_connected_category {SI} (dsp : downset_pred SI) α :
  strongly_connected_category ((OrdDSUpCat dsp α)ᵒᵖ).
Proof. intros γ δ; pose proof (index_le_total γ δ) as [|]; [right|left]; done. Qed.

Lemma ord_ds_up_cat_mere_preorder {SI} (dsp : downset_pred SI) α :
  mere_preorder ((OrdDSUpCat dsp α)ᵒᵖ).
Proof.
  intros ????.
  apply proof_irrel.
Qed.

Definition limit_side_iso_at_cofinal
  {SI : indexT} {dsp : downset_pred SI} {C : category} `{!Enriched C (PSh (OrdCat SI))}
  `{!LimitsEnriched C} {F : functor ((OrdDSCat dsp)ᵒᵖ) C}
  {c} (il : is_limit F c) α
  {δ} (Hδ : dsp δ)
  (isos : ∀ (β γ : downset dsp) (Hβγ : β ⪯ γ), δ ⪯ β → δ ⪯ γ → is_iso_at (F ₕ Hβγ) α)
  (β : downset dsp) (Hβ : δ ⪯ β) : is_iso_at (ic_side (il_is_cone il) β) α :=
  match β as u return δ ⪯ u → is_iso_at (ic_side (il_is_cone il) u) α with
  | MkDS _ =>
      λ Hu,
      limit_side_iso_at
        (ord_ds_up_cat_strongly_connected_category dsp δ)
        (ord_ds_up_cat_mere_preorder dsp δ)
        (is_limit_up il Hδ) α
        (λ (j j' : downset_up dsp δ) (f : j' ⪯ j),
          isos (downset_up_to_downset j') (downset_up_to_downset j)
            f (ds_up_up j') (ds_up_up j))
        (downset_to_downset_up _ Hu)
  end Hβ.
