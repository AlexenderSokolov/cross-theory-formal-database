From SynthDom Require Import prelude.
From SynthDom.categories Require Import category ord_cat.
From SynthDom Require Import stepindex.

Set Universe Polymorphism.
Unset Universe Minimization ToSet.

Open Scope category.

Declare Scope logic_scope.
Delimit Scope logic_scope with logic.

Local Open Scope logic_scope.

Record Sieve {C : category} (c : obj C) := MkSieve {
    sieve_arrows :> ∀ {d : obj C},
      hom (C := Typ) (hom_typ d c) Prop;
    sieve_closed : ∀ {d e : obj C} (f : hom d c) (g : hom e d),
      sieve_arrows f → sieve_arrows (f ∘ g);
  }.
Arguments MkSieve {_ _}.
Arguments sieve_arrows {_ _} _ {_}.
Arguments sieve_closed {_ _} _ {_ _}.

Notation "'λsieve' δ , e" :=
  (MkSieve (λ δ, e) _)
    (at level 120, δ binder, no associativity) : category_scope.

Global Instance sieve_eq {C} {c : obj C} : Equiv (Sieve c) :=
  λ a b, ∀ (d : obj C) (f : hom d c), sieve_arrows a f = sieve_arrows b f.

Global Instance sieve_eq_equiv {C} {c : obj C}
  : Equivalence (@sieve_eq C c).
Proof.
  split.
  - intros η; by intros ?.
  - intros η η' H.
    intros ?; by symmetry.
  - intros ??? H J.
    intros d f.
    by rewrite (H d) (J d).
Qed.

Lemma sieve_equiv_unpack {C} {c : obj C}
  {η ρ : Sieve c}
  (p : sieve_eq η ρ) : η = ρ.
Proof.
  destruct η as [η1 η2];
    destruct ρ as [ρ1 ρ2].
  simpl in *.
  assert (η1 = ρ1) as Hf.
  { apply functional_extensionality_dep; intros x.
    apply functional_extensionality_dep; intros f.
    apply p. }
  destruct Hf.
  assert (η2 = ρ2) as Hf.
  { apply proof_irrelevance. }
  destruct Hf.
  reflexivity.
Qed.

Lemma sieve_equiv_pack {C} {c : obj C}
  {η η' : Sieve c}
  (p : η = η') : sieve_eq η η'.
Proof. rewrite p. apply sieve_eq_equiv. Qed.

Program Definition total_sieve {C : category} (c : obj C) : Sieve c
  := MkSieve (λ d, λ f, True) _.
Solve All Obligations with done.
Fail Next Obligation.

Program Definition subobject_classifier_psh C : obj (PSh C) :=
  MkFunc (λ x, Sieve (C := C) x)
    (λ a b f, λ s, λsieve x, λ y, s x (f ∘ y))
    _ _.
Next Obligation.
  intros ???? s ? f g h H; simpl in *.
  rewrite -comp_assoc.
  by apply sieve_closed.
Qed.
Next Obligation.
  repeat intros ?; simpl.
  extensionality x; simpl.
  apply sieve_equiv_unpack.
  intros d h; simpl.
  rewrite comp_assoc.
  reflexivity.
Qed.
Next Obligation.
  repeat intros ?; simpl.
  extensionality x; simpl.
  apply sieve_equiv_unpack.
  intros d h; simpl.
  rewrite left_id.
  reflexivity.
Qed.
Fail Next Obligation.

Notation "Ωₒ@{ C }" := (subobject_classifier_psh C) (at level 20, no associativity)
    : category_scope.
Notation "'Ωₒ'" := (subobject_classifier_psh _) (at level 20, no associativity)
    : category_scope.

Section logic.
  Context {C : category}.

  Definition entails {Γ : obj (PSh C)}
    (P Q : hom Γ (Ωₒ)) : Prop :=
    ∀ n γ m f, (P ₙ n) γ m f → (Q ₙ n) γ m f.

  Infix "⊢ᵢ" := entails (at level 99, no associativity) : logic_scope.

  Lemma entails_refl {Γ : obj (PSh C)} (P : hom Γ (Ωₒ)) :
    P ⊢ᵢ P.
  Proof. now intros n γ m f Px. Qed.

  Lemma entails_trans {Γ : obj (PSh C)} (P Q R : hom Γ (Ωₒ)) :
    P ⊢ᵢ Q → Q ⊢ᵢ R → P ⊢ᵢ R.
  Proof.
    intros H1 H2 n γ m f Px.
    apply H2, H1, Px.
  Qed.

  Lemma entails_subst {Γ A : obj (PSh C)} (t : hom Γ A) (P Q : hom A (Ωₒ)) :
    P ⊢ᵢ Q → P ∘ t ⊢ᵢ Q ∘ t.
  Proof.
    now intros H n γ m f Ptx; apply H.
  Qed.

  Program Definition eqI {X : obj (PSh C)}
    : hom (X ×ₒ X) (Ωₒ)
    := MkNat (λ x, λ y, λsieve p, λ t, ((X ₕ t) (fst y) = (X ₕ t) (snd y))) _.
  Next Obligation.
    intros ?? [? ?] ?.
    repeat intros ?; simpl.
    rewrite h_map_comp /=.
    by rewrite H.
  Qed.
  Next Obligation.
    repeat intros ?; simpl.
    extensionality x.
    apply sieve_equiv_unpack.
    intros ??; simpl.
    rewrite h_map_comp /=.
    reflexivity.
  Qed.

  Definition eq
    {Γ A : obj (PSh C)} (t u : hom Γ A) : hom Γ (Ωₒ)
    := eqI ∘ << t , u >>.

  Infix "≡ᵢ" := eq (at level 70, no associativity) : logic_scope.

  Program Definition true_arr
    : hom (C := PSh C) (1ₒ) (Ωₒ)
    := MkNat (λ _, λ _, total_sieve _) _.
  Next Obligation.
    repeat intros ?.
    extensionality x; simpl.
    apply sieve_equiv_unpack.
    intros ?; simpl.
    done.
  Qed.
  Fail Next Obligation.

  Program Definition true {Γ : obj (PSh C)} : hom Γ (Ωₒ)
    := true_arr ∘ (!ₕ _).

  Notation "'⊤ᵢ'" := true : logic_scope.

  Program Definition falseI
    : hom (C := PSh C) (1ₒ) (Ωₒ)
    := MkNat (λ _, λ _, λsieve _, λ _, False) _.
  Next Obligation.
    repeat intros ?.
    done.
  Qed.
  Next Obligation.
    repeat intros ?.
    extensionality x; simpl.
    apply sieve_equiv_unpack.
    intros ?; simpl.
    done.
  Qed.
  Fail Next Obligation.

  Definition false {Γ : obj (PSh C)} : hom Γ (Ωₒ)
    := falseI ∘ (!ₕ _).

  Notation "'⊥ᵢ'" := false : logic_scope.

  Program Definition conj_arr : hom ((Ωₒ) ×ₒ@{PSh C} (Ωₒ)) (Ωₒ)
    := MkNat (λ x, λ y, λsieve p, λ t, (fst y p t) ∧ (snd y p t)) _.
  Next Obligation.
    intros; simpl in *.
    split; now apply sieve_closed.
  Qed.
  Next Obligation.
    repeat intros ?.
    extensionality x; simpl.
    apply sieve_equiv_unpack.
    intros ?; simpl.
    done.
  Qed.
  Fail Next Obligation.

  Definition conj {Γ : obj (PSh C)} (P Q : hom Γ (Ωₒ)) : hom Γ (Ωₒ)
    := conj_arr ∘ << P , Q >>.

  Infix "∧ᵢ" := conj (at level 80, right associativity) : logic_scope.

  Program Definition disjI : hom ((Ωₒ) ×ₒ@{PSh C} (Ωₒ)) (Ωₒ)
    := MkNat (λ x, λ y, λsieve p, λ t, (fst y p t) ∨ (snd y p t)) _.
  Next Obligation.
    intros ?????? [H | H]; simpl in *.
    - left; now apply sieve_closed.
    - right; now apply sieve_closed.
  Qed.
  Next Obligation.
    repeat intros ?.
    extensionality x; simpl.
    apply sieve_equiv_unpack.
    intros ?; simpl.
    done.
  Qed.
  Fail Next Obligation.

  Definition disj {Γ : obj (PSh C)} (P Q : hom Γ (Ωₒ)) : hom Γ (Ωₒ)
    := disjI ∘ << P , Q >>.

  Infix "∨ᵢ" := disj (at level 85, right associativity) : logic_scope.

  Program Definition implI : hom ((Ωₒ) ×ₒ@{PSh C} (Ωₒ)) (Ωₒ)
    := MkNat (λ x, λ y, λsieve p, λ t,
           (∀ q (e : hom q p), fst y q (t ∘ e) → snd y q (t ∘ e))) _.
  Next Obligation.
    intros ?????? H; simpl in *.
    intros ?? K.
    rewrite comp_assoc.
    apply H.
    rewrite -comp_assoc.
    apply K.
  Qed.
  Next Obligation.
    repeat intros ?.
    extensionality x; simpl.
    apply sieve_equiv_unpack.
    intros ?; simpl.
    intros; simpl.
    extensionality y; simpl.
    extensionality z; simpl.
    rewrite comp_assoc.
    done.
  Qed.
  Fail Next Obligation.

  Definition impl {Γ : obj (PSh C)} (P Q : hom Γ (Ωₒ)) : hom Γ (Ωₒ)
    := implI ∘ << P , Q >>.

  Infix "→ᵢ" := impl (at level 90, right associativity) : logic_scope.

  Program Definition all_arr {X : obj (PSh C)}
    : hom ((Ωₒ) ↑ₒ X) (Ωₒ)
    := MkNat (λ x, λ y,
           λsieve p, λ t,
           ∀ q (e : hom q p) (r : X ₒ q), (y ₙ q) (t ∘ e, r) q (id _)) _.
  Next Obligation.
    intros ??????? H ???; simpl.
    simpl in *.
    rewrite (comp_assoc _ _ _).
    apply H.
  Qed.
  Next Obligation.
    repeat intros ?.
    extensionality x; simpl.
    apply sieve_equiv_unpack.
    repeat intros ?; simpl.
    extensionality y; extensionality z.
    rewrite comp_assoc.
    done.
  Qed.

  Definition all {Γ : obj (PSh C)}
    A (P : hom (A ×ₒ Γ) (Ωₒ)) : hom Γ (Ωₒ)
    := all_arr ∘ (transpose P).

  Notation "∀ᵢ[ A ] P" :=
    (all A P)
      (at level 95, P at level 95, format "∀ᵢ[ A ]  P")
      : logic_scope.

  Program Definition existI {X : obj (PSh C)} : hom ((Ωₒ) ↑ₒ X) (Ωₒ) :=
    MkNat (λ x, λ y, λsieve p, λ t,
        ∃ (r : X ₒ p), (y ₙ p) (t, r) p (id _)) _.
  Next Obligation.
    intros ?????? g [r H]; simpl in *.
    exists ((X ₕ g) r).
    pose proof (equal_f (naturality y g) (f, r)) as G.
    rewrite /= /hom_prod /= left_id in G.
    rewrite G /= right_id; clear G.
    eapply sieve_closed in H.
    rewrite left_id in H.
    apply H.
  Qed.
  Next Obligation.
    repeat intros ?.
    extensionality x; simpl.
    apply sieve_equiv_unpack.
    intros ?; simpl.
    done.
  Qed.
  Fail Next Obligation.

  Definition exist {Γ : obj (PSh C)} A
    (P : hom (A ×ₒ Γ) (Ωₒ)) : hom Γ (Ωₒ)
    := existI ∘ transpose P.

  Notation "∃ᵢ[ A ] P" := (exist A P)
                            (at level 95, P at level 95, format "∃ᵢ[ A ]  P")
      : logic_scope.

  Program Definition pureI (P : Prop) : hom (1ₒ) (Ωₒ@{C}) :=
    MkNat (λ x, λ y, λsieve p, λ t, P) _.
  Next Obligation.
    repeat intros ?; simpl.
    assumption.
  Qed.
  Next Obligation.
    repeat intros ?.
    extensionality x; simpl.
    apply sieve_equiv_unpack.
    intros ?; simpl.
    done.
  Qed.
  Fail Next Obligation.

  Definition pure {Γ : obj (PSh C)} (P : Prop) : hom Γ (Ωₒ@{C})
    := pureI P ∘ (!ₕ _).

  Notation "'⌜' P '⌝ᵢ'" := (pure P) : logic_scope.

  Lemma eq_refl {Γ A} (t : hom Γ A) :
    ⊤ᵢ ⊢ᵢ t ≡ᵢ t.
  Proof.
    intros ?????; by simpl.
  Qed.

  Lemma eq_sym {Γ A} (t u : hom Γ A) :
    t ≡ᵢ u ⊢ᵢ u ≡ᵢ t.
  Proof.
    intros n γ m f H; simpl.
    by rewrite H.
  Qed.

  Lemma eq_trans {Γ A} (t u v : hom Γ A) :
    t ≡ᵢ u ∧ᵢ u ≡ᵢ v ⊢ᵢ t ≡ᵢ v.
  Proof.
    intros n γ m f [H1 H2]; simpl in *.
    by rewrite H1 H2.
  Qed.

  Lemma eq_subst {Γ A B} (t u : hom Γ A) (D : hom A B) :
    t ≡ᵢ u ⊢ᵢ D ∘ t ≡ᵢ D ∘ u.
  Proof.
    intros n γ m f He; simpl in *.
    rewrite -!psh_naturality.
    f_equiv.
    rewrite !psh_naturality.
    apply He.
  Qed.

  Lemma eq_coerce {Γ} (P Q : hom Γ (Ωₒ)) :
    P ≡ᵢ Q ∧ᵢ P ⊢ᵢ Q.
  Proof.
    intros n γ m f [He HP]; simpl in *.
    pose proof (sieve_equiv_pack He m (id _)) as G.
    rewrite /= right_id in G.
    rewrite -G; clear G.
    apply HP.
  Qed.

  Lemma true_intro {Γ} {P : hom Γ (Ωₒ)} :
    P ⊢ᵢ ⊤ᵢ.
  Proof.
    by intros.
  Qed.

  Lemma false_elim {Γ} {P : hom Γ (Ωₒ)} :
    ⊥ᵢ ⊢ᵢ P.
  Proof.
    intros ???? [].
  Qed.

  Lemma conj_intro {Γ} {R P Q : hom Γ (Ωₒ)} :
    R ⊢ᵢ P →
    R ⊢ᵢ Q →
    R ⊢ᵢ P ∧ᵢ Q.
  Proof.
    intros HP HQ n γ m f Rx; simpl.
    split; by [apply HP | apply HQ].
  Qed.

  Lemma conj_elim_l {Γ} {P Q : hom Γ (Ωₒ)} :
    P ∧ᵢ Q ⊢ᵢ P.
  Proof.
    by intros n γ m f [Px Qx].
  Qed.

  Lemma conj_elim_r {Γ} {P Q : hom Γ (Ωₒ)} :
    P ∧ᵢ Q ⊢ᵢ Q.
  Proof.
    by intros n γ m f [Px Qx].
  Qed.

  Lemma disj_intro_l {Γ} {P Q : hom Γ (Ωₒ)} :
    P ⊢ᵢ P ∨ᵢ Q.
  Proof.
    by intros n γ m f Px; left; simpl in *.
  Qed.

  Lemma disj_intro_r {Γ} {P Q : hom Γ (Ωₒ)} :
    Q ⊢ᵢ P ∨ᵢ Q.
  Proof.
    by intros n γ m f Px; right; simpl in *.
  Qed.

  Lemma disj_elim {Γ} {P Q R : hom Γ (Ωₒ)} :
    P ⊢ᵢ R →
    Q ⊢ᵢ R →
    P ∨ᵢ Q ⊢ᵢ R.
  Proof.
    by intros HP HQ n γ m f [Px | Qx]; [apply HP | apply HQ].
  Qed.

  Lemma impl_intro {Γ} {P Q R : hom Γ (Ωₒ)} :
    R ∧ᵢ P ⊢ᵢ Q →
    R ⊢ᵢ P →ᵢ Q.
  Proof.
    intros H n γ m f Rx j Hj Px; simpl in *.
    apply (H n γ j (f ∘ Hj)).
    split.
    - apply sieve_closed, Rx.
    - apply Px.
  Qed.

  Lemma impl_elim {Γ} {P Q : hom Γ (Ωₒ)} :
    (P →ᵢ Q) ∧ᵢ P ⊢ᵢ Q.
  Proof.
    intros n γ m f [H Px]; simpl in *.
    specialize (H m (id _)).
    assert (Px' : (P ₙ) n γ m (f ∘ (id _))).
    { by rewrite right_id. }
    specialize (H Px').
    rewrite right_id in H.
    apply H.
  Qed.

  Lemma all_intro {Γ A} (R : hom Γ (Ωₒ)) (P : hom (A ×ₒ Γ) (Ωₒ)) :
    R ∘ (prj2 _) ⊢ᵢ P → R ⊢ᵢ ∀ᵢ[A] P.
  Proof.
    intros H n γ m f Rx j Hj y; simpl.
    apply H; simpl.
    rewrite (psh_naturality R j n (f ∘ Hj) γ) /=.
    rewrite right_id.
    apply sieve_closed.
    apply Rx.
  Qed.

  Lemma all_elim {Γ A} (P : hom (A ×ₒ Γ) (Ωₒ))
    (t : hom Γ A) :
    ∀ᵢ[A] P ⊢ᵢ P ∘ << t , (id _) >>.
  Proof.
    intros n γ m f H; simpl.
    specialize (H m (id _) ((t ₙ) m ((Γ ₕ f) γ))).
    simpl in H.
    pose proof (psh_naturality P _ _ (f ∘ (id _)) (((t ₙ n) γ), γ)) as G.
    rewrite /= (right_id f) in G.
    rewrite /= (right_id f) in H.
    pose proof (sieve_equiv_pack G _ (id _)) as J; clear G.
    rewrite /= right_id in J.
    rewrite -J.
    rewrite /hom_prod /=.
    rewrite -(psh_naturality t _ _ f).
    apply H.
  Qed.

  Lemma exist_intro {Γ A} (P : hom (A ×ₒ Γ) (Ωₒ))
    (t : hom Γ A) :
    (P ∘ (<< t , (id _) >>) ⊢ᵢ ∃ᵢ[A] P).
  Proof.
    intros n γ m f Px.
    exists ((t ₙ m) ((Γ ₕ f) γ)).
    simpl in *.
    rewrite psh_naturality.
    pose proof (psh_naturality P m n f ((A ₕ (id _)) ((t ₙ n) γ), (Γ ₕ (id _)) γ)) as H.
    rewrite /= !h_map_id /= in H.
    rewrite (sieve_equiv_pack H _ (id _)).
    apply sieve_closed, Px.
  Qed.

  Lemma exist_elim {Γ A} (P : hom (A ×ₒ Γ) (Ωₒ)) (Q : hom Γ (Ωₒ)) :
    (P ⊢ᵢ Q ∘ (prj2 _) → ∃ᵢ[A] P ⊢ᵢ Q).
  Proof.
    intros H n γ m f [y Py]; simpl in *.
    pose proof (H m (y, ((Γ ₕ f) γ)) m (id _) Py) as J.
    simpl in J.
    rewrite psh_naturality /= right_id in J.
    apply J.
  Qed.

  Lemma pure_intro {Γ} {P : hom Γ (Ωₒ)} {Q : Prop} (q : Q) :
    P ⊢ᵢ ⌜ Q ⌝ᵢ.
  Proof.
    by intros H n γ m f.
  Qed.

  Lemma pure_elim {Γ} {P : hom Γ (Ωₒ)}
    (φ : Prop) : (φ → ⊤ᵢ ⊢ᵢ P) → (⌜ φ ⌝ᵢ) ⊢ᵢ P.
  Proof.
    intros H n γ m f G.
    by apply H.
  Qed.

  Opaque entails true false conj disj impl all exist pure.

  Lemma false_elim' {Γ} (R P : hom Γ (Ωₒ)) :
    R ⊢ᵢ ⊥ᵢ →
    R ⊢ᵢ P.
  Proof.
    intros H.
    eapply entails_trans; [apply H |].
    apply false_elim.
  Qed.

  Lemma conj_true_l_inv {Γ} (P : hom Γ (Ωₒ)) :
    P ⊢ᵢ ⊤ᵢ ∧ᵢ P.
  Proof.
    apply conj_intro; [apply true_intro | apply entails_refl].
  Qed.

  Lemma conj_true_r_inv {Γ} (P : hom Γ (Ωₒ)) :
    P ⊢ᵢ P ∧ᵢ ⊤ᵢ.
  Proof.
    apply conj_intro; [apply entails_refl | apply true_intro].
  Qed.

  Lemma conj_comm {Γ} (P Q : hom Γ (Ωₒ)) :
    P ∧ᵢ Q ⊢ᵢ Q ∧ᵢ P.
  Proof.
    apply conj_intro.
    - apply conj_elim_r.
    - apply conj_elim_l.
  Qed.

  Lemma conj_mono {Γ} (P P' Q Q' : hom Γ (Ωₒ)) :
    P ⊢ᵢ P' →
    Q ⊢ᵢ Q' →
    P ∧ᵢ Q ⊢ᵢ P' ∧ᵢ Q'.
  Proof.
    intros H1 H2.
    apply conj_intro.
    - eapply entails_trans; [| apply H1].
      apply conj_elim_l.
    - eapply entails_trans; [| apply H2].
      apply conj_elim_r.
  Qed.

  Lemma conj_mono_l {Γ} (P P' Q : hom Γ (Ωₒ)) :
    P ⊢ᵢ P' →
    P ∧ᵢ Q ⊢ᵢ P' ∧ᵢ Q.
  Proof.
    intros H.
    eapply conj_mono.
    - apply H.
    - apply entails_refl.
  Qed.

  Lemma conj_mono_r {Γ} (P Q Q' : hom Γ (Ωₒ)) :
    Q ⊢ᵢ Q' →
    P ∧ᵢ Q ⊢ᵢ P ∧ᵢ Q'.
  Proof.
    intros H.
    eapply conj_mono.
    - apply entails_refl.
    - apply H.
  Qed.

  Lemma conj_elim_l' {Γ} (P Q R : hom Γ (Ωₒ)) :
    R ⊢ᵢ P ∧ᵢ Q →
    R ⊢ᵢ P.
  Proof.
    intros H.
    eapply entails_trans.
    - apply H.
    - apply conj_elim_l.
  Qed.

  Lemma conj_elim_r' {Γ} (P Q R : hom Γ (Ωₒ)) :
    R ⊢ᵢ P ∧ᵢ Q →
    R ⊢ᵢ P.
  Proof.
    intros H.
    eapply entails_trans.
    - apply H.
    - apply conj_elim_l.
  Qed.

  Lemma disj_false_l {Γ} (P : hom Γ (Ωₒ)) :
    ⊥ᵢ ∨ᵢ P ⊢ᵢ P.
  Proof.
    eapply disj_elim.
    - apply false_elim.
    - apply entails_refl.
  Qed.

  Lemma disj_false_r {Γ} (P : hom Γ (Ωₒ)) :
    P ∨ᵢ ⊥ᵢ ⊢ᵢ P.
  Proof.
    eapply disj_elim.
    - apply entails_refl.
    - apply false_elim.
  Qed.

  Lemma disj_comm {Γ} (P Q : hom Γ (Ωₒ)) :
    P ∨ᵢ Q ⊢ᵢ Q ∨ᵢ P.
  Proof.
    eapply disj_elim.
    - apply disj_intro_r.
    - apply disj_intro_l.
  Qed.

  Lemma disj_mono {Γ} (P P' Q Q' : hom Γ (Ωₒ)) :
    P ⊢ᵢ P' →
    Q ⊢ᵢ Q' →
    P ∨ᵢ Q ⊢ᵢ P' ∨ᵢ Q'.
  Proof.
    intros H1 H2.
    apply disj_elim.
    - apply entails_trans with P'.
      + apply H1.
      + apply disj_intro_l.
    - apply entails_trans with Q'.
      + apply H2.
      + apply disj_intro_r.
  Qed.

  Lemma disj_mono_l {Γ} (P P' Q : hom Γ (Ωₒ)) :
    P ⊢ᵢ P' →
    P ∨ᵢ Q ⊢ᵢ P' ∨ᵢ Q.
  Proof.
    intros H.
    apply disj_mono.
    - apply H.
    - apply entails_refl.
  Qed.

  Lemma disj_mono_r {Γ} (P Q Q' : hom Γ (Ωₒ)) :
    Q ⊢ᵢ Q' →
    P ∨ᵢ Q ⊢ᵢ P ∨ᵢ Q'.
  Proof.
    intros H.
    apply disj_mono.
    - apply entails_refl.
    - apply H.
  Qed.

  Lemma disj_intro_l' {Γ} (P Q R : hom Γ (Ωₒ)) :
    R ⊢ᵢ P →
    R ⊢ᵢ P ∨ᵢ Q.
  Proof.
    intros H.
    eapply entails_trans.
    - apply H.
    - apply disj_intro_l.
  Qed.

  Lemma disj_intro_r' {Γ} (P Q R : hom Γ (Ωₒ)) :
    R ⊢ᵢ Q →
    R ⊢ᵢ P ∨ᵢ Q.
  Proof.
    intros H.
    eapply entails_trans.
    - apply H.
    - apply disj_intro_r.
  Qed.

  Lemma impl_elim' {Γ} (P Q R : hom Γ (Ωₒ)) :
    R ⊢ᵢ P →ᵢ Q →
    R ∧ᵢ P ⊢ᵢ Q.
  Proof.
    intros H.
    eapply entails_trans.
    - apply conj_mono_l, H.
    - apply impl_elim.
  Qed.

  Lemma entails_impl {Γ} (P Q : hom Γ (Ωₒ)) :
    P ⊢ᵢ Q →
    ⊤ᵢ ⊢ᵢ P →ᵢ Q.
  Proof.
    intros H.
    apply impl_intro.
    apply entails_trans with P.
    - apply conj_elim_r.
    - apply H.
  Qed.

  Lemma impl_entails {Γ} (P Q : hom Γ (Ωₒ)) :
    ⊤ᵢ ⊢ᵢ P →ᵢ Q →
    P ⊢ᵢ Q.
  Proof.
    intros H.
    apply entails_trans with (⊤ᵢ ∧ᵢ P).
    - apply conj_true_l_inv.
    - apply impl_elim', H.
  Qed.

  Lemma all_elim' {Γ A} (P : hom (A ×ₒ Γ) (Ωₒ))
    (t : hom Γ A) (R : hom Γ (Ωₒ)) :
    R ⊢ᵢ ∀ᵢ[A] P →
    R ⊢ᵢ P ∘ << t , id _ >>.
  Proof.
    intros H.
    eapply entails_trans.
    - apply H.
    - apply all_elim.
  Qed.

  Lemma exist_intro' {Γ A} (P : hom (A ×ₒ Γ) (Ωₒ))
    (t : hom Γ A) (R : hom Γ (Ωₒ)) :
    R ⊢ᵢ P ∘ (<< t , id _ >>) →
    (R ⊢ᵢ ∃ᵢ[A] P).
  Proof.
    intros H.
    eapply entails_trans.
    - apply H.
    - apply exist_intro.
  Qed.

  Lemma soundness {P : Prop} (n : obj C) :
    ⊤ᵢ ⊢ᵢ @pure (1ₒ) P → P.
  Proof.
    intros H.
    by apply (H n () n (id _)).
  Qed.

  Lemma soundness_eq {A B : obj (PSh C)} (t u : hom (1ₒ) A) :
    ⊤ᵢ ⊢ᵢ t ≡ᵢ u → t ≡ u.
  Proof.
    intros H x.
    extensionality y; destruct y.
    specialize (H x () x (id _)).
    rewrite /= in H.
    rewrite h_map_id /= in H.
    by apply H.
  Qed.

End logic.

Notation "'⊤ᵢ'" := true : logic_scope.
Notation "'⊥ᵢ'" := false : logic_scope.
Infix "≡ᵢ" := eq (at level 70, no associativity) : logic_scope.
Infix "∧ᵢ" := conj (at level 80, right associativity) : logic_scope.
Infix "∨ᵢ" := disj (at level 85, right associativity) : logic_scope.
Infix "→ᵢ" := impl (at level 90, right associativity) : logic_scope.
Notation "∀ᵢ[ A ] P" :=
  (all A P)
    (at level 95, P at level 95, format "∀ᵢ[ A ]  P")
    : logic_scope.
Notation "∃ᵢ[ A ] P" :=
  (exist A P)
    (at level 95, P at level 95, format "∃ᵢ[ A ]  P")
    : logic_scope.
Notation "'⌜' P '⌝ᵢ'" := (pure P) : logic_scope.
Infix "⊢ᵢ" := entails (at level 99, no associativity) : logic_scope.

Section si_logic.
  Context {SI : indexT}.

  Lemma ord_cat_sieve_thin {x : obj (OrdCat SI)}
    {y : Sieve x} {α β : obj (OrdCat SI)}
    (f : hom α x) (g : hom β x) (h : hom β α)
    : y α f → y β g.
  Proof.
    intros H.
    assert (g = f ∘ h) as ->.
    { simpl; apply proof_irrelevance. }
    apply sieve_closed, H.
  Qed.

  Lemma index_min_mono_l {γ β α : SI} : γ ⪯ β → index_min γ α ⪯ index_min β α.
  Proof.
    intros H. unfold index_min.
    destruct (index_le_total γ α) as [H1 | H1];
      destruct (index_le_total β α) as [H2 | H2]; try done.
    left. eapply index_le_ge_eq; auto. etransitivity; eauto.
  Qed.

  Lemma index_succ_hom {α : SI}
    : hom (C := OrdCat SI) α (succ α).
  Proof. by apply index_lt_le_subrel. Qed.

  Lemma index_min_le_l_hom (α β : SI)
    : hom (C := OrdCat SI) (index_min α β) α.
  Proof. apply index_min_le_l. Qed.

  Lemma index_min_le_r_hom (α β : SI)
    : hom (C := OrdCat SI) (index_min α β) β.
  Proof. apply index_min_le_r. Qed.

  Lemma index_min_le_l_hom_decomp {a b : SI} (q : hom (C := OrdCat SI) b a)
    : index_min_le_l_hom a b ≡ q ∘ index_min_le_r_hom a b.
  Proof. done. Qed.

  Lemma index_min_le_r_hom_decomp {a b : SI} (q : hom (C := OrdCat SI) b a)
    : index_min_le_r_hom b a ≡ q ∘ index_min_le_l_hom b a.
  Proof. done. Qed.

  Program Definition index_lt_le_subrel_hom {a b : SI}
    (f : a ≺ b) : hom (C := OrdCat SI) a b := index_lt_le_subrel _ _ f.

  Program Definition laterI : hom (C := (PSh (OrdCat SI))) (Ωₒ) (Ωₒ) :=
    MkNat (λ m, λ γ, λsieve n, λ f,
        ∀ n' (g : n' ≺ n), (γ n' (f ∘ (index_lt_le_subrel_hom g)))) _.
  Next Obligation.
    intros x y d e f g H h j.
    eapply ord_cat_sieve_thin;
      last apply (H h (index_lt_le_trans _ _ _ j g)).
    apply id.
  Qed.
  Next Obligation.
    repeat intros ?.
    extensionality x; simpl.
    apply sieve_equiv_unpack.
    intros ??; simpl.
    extensionality y; simpl.
    extensionality z; simpl.
    f_equiv.
    apply proof_irrel.
  Qed.
  Fail Next Obligation.

  Definition laterP {Γ} (P : hom Γ (Ωₒ)) : hom Γ (Ωₒ)
    := laterI ∘ P.

  Notation "'▷ᵢ' P" := (laterP P) (at level 80) : logic_scope.

  Lemma laterI_intro {Γ} (P : hom Γ (Ωₒ)) :
    P ⊢ᵢ ▷ᵢ P.
  Proof.
    intros n γ m f Px h g.
    simpl in *.
    eapply ord_cat_sieve_thin;
      last apply Px.
    apply (index_lt_le_subrel_hom g).
  Qed.

  Lemma laterI_mono {Γ} (P Q : hom Γ (Ωₒ)) :
    P ⊢ᵢ Q →
    ▷ᵢ P ⊢ᵢ ▷ᵢ Q.
  Proof.
    intros n γ m f h Px j g.
    apply n, Px.
  Qed.

  Lemma laterI_loeb {Γ} (P : hom Γ (Ωₒ)) :
    ▷ᵢ P ⊢ᵢ P →
    ⊤ᵢ ⊢ᵢ P.
  Proof.
    intros n γ m f h Px.
    revert γ m h Px.
    induction (index_lt_wf _ f) as [f _ IHf]; intros γ m h Px.
    simpl in *.
    apply n.
    simpl.
    intros n' g.
    unshelve eapply (ord_cat_sieve_thin _ _ (id _));
      last apply (IHf _ g); last done.
    apply (index_lt_le_subrel_hom (index_lt_le_trans _ _ _ g h)).
  Qed.

  Lemma laterI_false_em {Γ} (P : hom Γ (Ωₒ)) : ▷ᵢ P ⊢ᵢ ▷ᵢ ⊥ᵢ ∨ᵢ (▷ᵢ ⊥ᵢ →ᵢ P).
  Proof.
    intros n γ m f Px.
    simpl in *.
    destruct (index_is_zero m) as [->| Hnz].
    - left; intros.
      by eapply index_lt_zero_is_normal.
    - right.
      intros q e G.
      eapply ord_cat_sieve_thin; last apply (Px zero Hnz).
      rewrite (index_zero_is_unique q G).
      apply id.
  Qed.

  Lemma laterP_elim (P : hom (1ₒ) (Ωₒ)) :
    ⊤ᵢ ⊢ᵢ ▷ᵢ P →
    ⊤ᵢ ⊢ᵢ P.
  Proof.
    intros n γ [] f Px G.
    rewrite (psh_naturality P γ (succ γ) index_succ_hom ()) /=.
    eapply ord_cat_sieve_thin;
      last apply
        (n (succ γ) () (succ f)
           (index_le_succ_mono _ _ Px) G f (index_succ_greater _)).
    apply id.
  Qed.

  Lemma laterP_forall {Γ A} (Φ : hom (A ×ₒ Γ) (Ωₒ))
    : ▷ᵢ (∀ᵢ[A] Φ) ⊢ᵢ (∀ᵢ[A] (laterI ∘ Φ)).
  Proof.
    intros n γ m f Px h.
    intros g.
    intros q e r.
    rewrite left_id.
    pose proof (sieve_equiv_pack (psh_naturality Φ _ _ (index_lt_le_subrel_hom r) (q, (Γ ₕ transitivity g f) γ)) _ (id _)) as H.
    simpl in H.
    simpl.
    replace (index_lt_le_subrel_hom r) with
      (transitivity (reflexivity e) (index_lt_le_subrel_hom r));
      last apply proof_irrel.
    rewrite -H; clear H.
    rewrite h_map_comp.
    rewrite /hom_prod /=.
    pose proof (Px e (index_lt_le_trans _ _ _ r g) e (id _)
                  ((A ₕ index_lt_le_subrel_hom r) q)) as H.
    rewrite right_id in H.
    simpl in *.
    replace ((Γ ₕ index_lt_le_subrel_hom r) ((Γ ₕ g) ((Γ ₕ f) γ))) with
      ((Γ ₕ transitivity (index_lt_le_subrel_hom (index_lt_le_trans e h m r g)) f) γ);
      first apply H; clear H.
    epose proof (equal_f (h_map_comp _ _ Γ _ _ _ f g) γ) as H.
    simpl in H.
    rewrite -H; clear H.
    epose proof (equal_f (h_map_comp _ _ Γ _ _ _ (transitivity g f) (index_lt_le_subrel_hom r)) γ) as H.
    simpl in H.
    rewrite -H; clear H.
    f_equiv.
    apply proof_irrel.
  Qed.

  (* TODO: only with finite index *)
  (* Lemma later_discr_exist_false `{FiniteIndex SI} {A} (Φ : A → (global_sections ₒ (Ωₒ))) : *)
  (*   (▷ᵢ ∃ᵢ a, Φ a) ⊢ᵢ ▷ᵢ ⊥ᵢ ∨ᵢ (∃ᵢ a, ▷ᵢ (Φ a)). *)
  (* Proof. *)
  (*   intros n [] m f Px. *)
  (*   admit. *)
  (* Admitted. *)

  Local Opaque earlier_later_pointwise_iso.

  Lemma next_proj (A : obj (PSh (OrdCat SI))) (m : SI) (α β : A ₒ m) :
    (∀ (n' : SI) (g : n' ≺ m),
       ((A ₕ (index_lt_le_subrel_hom g)) α = ((A ₕ (index_lt_le_subrel_hom g))) β))
    <->
      ((((next ₙ A)ₙ m) α) = (((next ₙ A)ₙ m) β)).
  Proof.
    split.
    - intros Px.
      apply equiv_of_into_later_psh.
      intros p Hlt.
      set (p' := (MkDS (lt_dsp m) (squash Hlt))).
      replace Hlt with (unsquash (squash Hlt)) by apply proof_irrelevance.
      rewrite (side_of_later' A p').
      simpl; f_equiv.
      specialize (Px p Hlt); simpl in Px.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite_cone_hom_commutes_back; simpl.
      assert (in_lt_dsp m p' = index_lt_le_subrel_hom Hlt) as ->.
      { apply proof_irrelevance. }
      apply Px.
    - intros Px p Hlt.
      set (β' := (MkDS (lt_dsp m) (squash Hlt))).
      assert (((later ₒ A) ₕ (index_succ_le_lt2 _ _ Hlt)) (((next ₙ A)ₙ m) α)
                =
                ((later ₒ A) ₕ (index_succ_le_lt2 _ _ Hlt)) (((next ₙ A)ₙ m) β)) as Qx.
      { by rewrite Px. }
      replace Hlt with (unsquash (squash Hlt)) in Qx by apply proof_irrelevance.
      rewrite (side_of_later' A β') /= in Qx.
      match goal with
      | [ H : context ctx [(ic_side _ ?j) ((cone_hom_map ?c) ?x)] |- _ ] =>
          pose proof (equal_f (cone_hom_commutes c j) x) as G
      end.
      simpl in G.
      rewrite -G in Qx; clear G.
      match goal with
      | [ H : context ctx [(ic_side _ ?j)
                             ((cone_hom_map ?c) ?x)] |- _ ] =>
          pose proof (equal_f (cone_hom_commutes c j) x) as G
      end.
      simpl in G.
      rewrite -G in Qx; clear G.
      assert (index_lt_le_subrel_hom Hlt = in_lt_dsp m β') as ->.
      { simpl; apply proof_irrelevance. }
      assert (Rx :
               forward (earlier_later_pointwise_iso A
                          (later_func_o_map A) (later_func_o_map_is_limit A) p)
                 (backward
                    (earlier_later_pointwise_iso A
                       (later_func_o_map A) (later_func_o_map_is_limit A) p)
                    ((A ₕ in_lt_dsp m β') α))
                 =
                 forward (earlier_later_pointwise_iso A
                            (later_func_o_map A) (later_func_o_map_is_limit A) p)
                 (backward
                    (earlier_later_pointwise_iso A
                       (later_func_o_map A) (later_func_o_map_is_limit A) p)
                    ((A ₕ in_lt_dsp m β') β))).
      { f_equiv; apply Qx. }
      pose proof (equal_f (iso_rl (is_iso ((earlier_later_pointwise_iso A
                                     (later_func_o_map A)
                                     (later_func_o_map_is_limit A) p))))
                    ((A ₕ in_lt_dsp m β') α)) as H.
      simpl in H.
      rewrite H in Rx; clear H.
      pose proof (equal_f (iso_rl (is_iso ((earlier_later_pointwise_iso A
                                     (later_func_o_map A)
                                     (later_func_o_map_is_limit A) p))))
                    ((A ₕ in_lt_dsp m β') β)) as H.
      simpl in H.
      rewrite H in Rx.
      apply Rx.
  Qed.

  Lemma laterP_eq {Γ A} (t u : hom Γ A) :
    ▷ᵢ (t ≡ᵢ u) ⊢ᵢ (next ₙ _) ∘ t ≡ᵢ (next ₙ _) ∘ u.
  Proof.
    intros n γ m f Px.
    apply equiv_of_into_later_psh.
    intros β Hlt.
    set (β' := (MkDS (lt_dsp m) (squash Hlt))).
    replace Hlt with (unsquash (squash Hlt)) by apply proof_irrelevance.
    rewrite (side_of_later' A β') -!psh_naturality.
    simpl; f_equiv.
    specialize (Px β Hlt); simpl in Px.
    rewrite -!psh_naturality h_map_comp
      (psh_naturality t) (psh_naturality u) /= in Px.
    rewrite_cone_hom_commutes_back; simpl.
    rewrite_cone_hom_commutes_back; simpl.
    assert (in_lt_dsp m β' = index_lt_le_subrel_hom Hlt) as ->.
    { apply proof_irrelevance. }
    apply Px.
  Qed.

  Lemma laterP_eq_inv {Γ A} (t u : hom Γ A) :
    (next ₙ _) ∘ t ≡ᵢ (next ₙ _) ∘ u ⊢ᵢ ▷ᵢ (t ≡ᵢ u).
  Proof.
    intros n γ m f Px h g; simpl.
    rewrite h_map_comp /=.
    apply next_proj.
    rewrite !psh_naturality.
    apply Px.
  Qed.

  Transparent later next.

  Lemma later_intro {Γ} (P R : hom Γ (Ωₒ)) :
    R ⊢ᵢ P →
    R ⊢ᵢ ▷ᵢ P.
  Proof.
    intros H.
    eapply entails_trans.
    - apply H.
    - apply laterI_intro.
  Qed.

  Lemma later_mono {Γ} : Proper ((@entails _ Γ) ==> (@entails _ Γ)) laterP.
  Proof.
    intros P R H.
    apply laterI_mono.
    apply H.
  Qed.

  Lemma later_loeb {Γ} (P : hom Γ (Ωₒ)) :
    (▷ᵢ P ⊢ᵢ P) → (⊤ᵢ ⊢ᵢ P).
  Proof.
    intros H.
    apply laterI_loeb.
    apply H.
  Qed.

  Lemma later_false_em {Γ} (R P : hom Γ (Ωₒ))
    : R ⊢ᵢ ▷ᵢ P →
      R ⊢ᵢ ▷ᵢ ⊥ᵢ ∨ᵢ (▷ᵢ ⊥ᵢ →ᵢ P).
  Proof.
    intros H.
    eapply entails_trans.
    - apply H.
    - apply laterI_false_em.
  Qed.

End si_logic.

Notation "'▷ᵢ' P" := (laterP P) (at level 80) : logic_scope.
