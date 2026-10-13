From SynthDom Require Import prelude.

Require Export Stdlib.Logic.PropExtensionality.
Require Export Stdlib.Logic.FunctionalExtensionality.
Require Export Stdlib.Logic.ProofIrrelevance.
Require Export Stdlib.Logic.Epsilon.
Require Export Stdlib.Logic.Classical_Prop.

Section quotient.
  Context {A : Type} (R : relation A) {Equiv : Equivalence R}.

  Record quotient :=
    MkQuot {
        quotient_class : A → Prop;
        quotient_repr : ∃ x, quotient_class = R x;
      }.

  Program Definition quotient_el (x : A) : quotient
    := MkQuot (R x) (ex_intro _ x eq_refl).

  Lemma quotient_inj {x y} : quotient_el x = quotient_el y → R x y.
  Proof using A Equiv R.
    intros H; inversion H as [G]; rewrite G; reflexivity.
  Qed.

  Lemma eq_quotient {x y} : R x y → quotient_el x = quotient_el y.
  Proof using A Equiv R.
    intros H.
    rewrite /quotient_el.
    assert (R x = R y) as Hf.
    {
      extensionality c; apply propositional_extensionality.
      split; intros G.
      - etransitivity; last apply G; symmetry; apply H.
      - etransitivity; [apply H | apply G].
    }
    clear H.
    set (ex_intro _ y _); clearbody e.
    revert e; destruct Hf.
    intros; f_equal; apply proof_irrelevance.
  Qed.

  Lemma quotient_inv q : ∃ x, q = quotient_el x.
  Proof.
    destruct q as [cl [x repr]].
    exists x.
    rewrite /quotient_el.
    set (ex_intro _ x _); clearbody e.
    revert e; rewrite repr.
    intros; f_equal; apply proof_irrelevance.
  Qed.

  Definition unquotient q : A
    := proj1_sig (constructive_indefinite_description _ (quotient_inv q)).

  Lemma unquotient_quotient_el q : quotient_el (unquotient q) = q.
  Proof.
    unfold unquotient.
    by destruct constructive_indefinite_description.
  Qed.

  Lemma unquotient_quotient_cong x y :
    R x y → R (unquotient (quotient_el x)) (unquotient (quotient_el y)).
  Proof using A Equiv R.
    intros H.
    apply quotient_inj.
    rewrite !unquotient_quotient_el.
    apply eq_quotient, H.
  Qed.

  Lemma unquotient_quotient_cong_l x y :
    R x y → R (unquotient (quotient_el x)) y.
  Proof using A Equiv R.
    intros H.
    apply quotient_inj.
    rewrite !unquotient_quotient_el.
    apply eq_quotient, H.
  Qed.

  Lemma unquotient_quotient_cong_r x y :
    R x y → R x (unquotient (quotient_el y)).
  Proof using A Equiv R.
    intros H.
    apply quotient_inj.
    rewrite !unquotient_quotient_el.
    apply eq_quotient, H.
  Qed.

  Section rect.
    Context (B : quotient → Type) (f : ∀ x, B (quotient_el x)).
    Context (g : ∀ x y (Rxy : R x y),
               castT (f_equal B (eq_quotient Rxy)) (f x) = f y).

    Local Lemma quotient_rect_witness (q : quotient) :
      exists! a : B q, ∃ x (exq : quotient_el x = q), a = castT (f_equal B exq) (f x).
    Proof using A Equiv B R f g.
      destruct (quotient_inv q) as [x ->]; exists (f x); split.
      - exists x, eq_refl; reflexivity.
      - intros x' [y [G ->]].
        symmetry.
        rewrite -(g _ _ (quotient_inj G)).
        f_equiv; apply proof_irrelevance.
    Qed.

    Definition quotient_rect q : B q :=
      proj1_sig (constructive_definite_description _ (quotient_rect_witness q)).

    Lemma quotient_rect_eq x : quotient_rect (quotient_el x) = f x.
    Proof.
      rewrite /quotient_rect.
      destruct constructive_definite_description as [? [? [G ->]]].
      rewrite /= -(g _ _ (quotient_inj G)).
      f_equal; apply proof_irrelevance.
    Qed.

  End rect.

  Section rec.
    Context (B : quotient → Set) (f : ∀ x, B (quotient_el x)).
    Context (g : ∀ x y (Rxy : R x y),
               castS (f_equal B (eq_quotient Rxy)) (f x) = f y).

    Local Lemma quotient_rec_witness (q : quotient) :
      exists! a : B q, ∃ x (exq : quotient_el x = q), a = castS (f_equal B exq) (f x).
    Proof using A Equiv B R f g.
      destruct (quotient_inv q) as [x ->]; exists (f x); split.
      - exists x, eq_refl; reflexivity.
      - intros x' [y [G ->]].
        symmetry.
        rewrite -(g _ _ (quotient_inj G)).
        f_equiv; apply proof_irrelevance.
    Qed.

    Definition quotient_rec q : B q :=
      proj1_sig (constructive_definite_description _ (quotient_rec_witness q)).

    Lemma quotient_rec_eq x : quotient_rec (quotient_el x) = f x.
    Proof.
      rewrite /quotient_rec.
      destruct constructive_definite_description as [? [? [G ->]]].
      rewrite /= -(g _ _ (quotient_inj G)).
      f_equal; apply proof_irrelevance.
    Qed.

  End rec.

  Section ind.
    Context (B : quotient → Prop) (f : ∀ x, B (quotient_el x)).
    Context (g : ∀ x y (Rxy : R x y),
               castP (f_equal B (eq_quotient Rxy)) (f x) = f y).

    Local Lemma quotient_ind_witness (q : quotient) :
      exists! a : B q, ∃ x (exq : quotient_el x = q), a = castP (f_equal B exq) (f x).
    Proof using A Equiv B R f g.
      destruct (quotient_inv q) as [x ->]; exists (f x); split.
      - exists x, eq_refl; reflexivity.
      - intros x' [y [G ->]].
        symmetry.
        rewrite -(g _ _ (quotient_inj G)).
        f_equiv; apply proof_irrelevance.
    Qed.

    Definition quotient_ind q : B q :=
      proj1_sig (constructive_definite_description _ (quotient_ind_witness q)).

    Lemma quotient_ind_eq x : quotient_ind (quotient_el x) = f x.
    Proof.
      rewrite /quotient_ind.
      destruct constructive_definite_description as [? [? [G ->]]].
      rewrite /= -(g _ _ (quotient_inj G)).
      f_equal; apply proof_irrelevance.
    Qed.

  End ind.

  Section elim.
    Context B (f : A → B) (g : ∀ x y, R x y → f x = f y).

    Local Definition quotient_elim_cong : ∀ (x y : A) (Rxy : R x y),
      castT (f_equal (λ _ : quotient, B) (eq_quotient Rxy)) (f x) = f y
    := λ x y Rxy,
      match (eq_quotient Rxy) as e' return
            (castT (f_equal (λ _ : quotient, B) e') (f x) = f y) with
      | eq_refl => g x y Rxy : castT (f_equal (λ _ : quotient, B) eq_refl) (f x) = f y
      end.

    Definition quotient_elim : quotient -> B
      := quotient_rect (λ _, B) f quotient_elim_cong.

    Lemma quotient_elim_eq x : quotient_elim (quotient_el x) = f x.
    Proof. by rewrite /quotient_elim quotient_rect_eq. Qed.

  End elim.

End quotient.

Arguments quotient_class {_ _}.
Arguments quotient_repr {_ _}.
Arguments quotient_el {_ _}.
Arguments quotient_inj {_ _ _ _ _}.
Arguments eq_quotient {_ _ _ _ _}.
Arguments quotient_inv {_ _}.
Arguments unquotient {_ _}.
Arguments unquotient_quotient_el {_ _}.
Arguments unquotient_quotient_cong {_ _}.
Arguments unquotient_quotient_cong_l {_ _}.
Arguments unquotient_quotient_cong_r {_ _}.
Arguments quotient_rect_witness {_ _ _}.
Arguments quotient_rect {_ _ _}.
Arguments quotient_rect_eq {_ _ _}.
Arguments quotient_rec_witness {_ _ _}.
Arguments quotient_rec {_ _ _}.
Arguments quotient_rec_eq {_ _ _}.
Arguments quotient_ind_witness {_ _ _}.
Arguments quotient_ind {_ _ _}.
Arguments quotient_ind_eq {_ _ _}.
Arguments quotient_elim {_ _ _}.
Arguments quotient_elim_eq {_ _ _}.
