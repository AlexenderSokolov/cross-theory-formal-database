From SynthDom Require Import prelude quotient.

Require Export Stdlib.Logic.PropExtensionality.
Require Export Stdlib.Logic.FunctionalExtensionality.
Require Export Stdlib.Logic.ProofIrrelevance.
Require Export Stdlib.Logic.Epsilon.
Require Export Stdlib.Logic.Classical_Prop.

(* Helper tactic. *)
Ltac solve_by_eq_rewrite :=
  by repeat match goal with
      Heq : context [eq _ _] |- _ => first [rewrite Heq| rewrite (Heq _)]
    end;
  eauto.

Local Set Universe Polymorphism.
Unset Universe Minimization ToSet.

Lemma equal_f@{i j} : forall {A : Type@{i}} {B : Type@{j}} {f g : A -> B},
  f = g -> forall x, f x = g x.
Proof. by intros ???? ->. Defined.

Inductive Empty@{i} : Type@{i} :=.

Global Hint Extern 0 => match goal with H : Empty |- _ => exfalso; inversion H end : core.

Record category := MkCat {
  obj : Type;
  hom : obj → obj → Type;
  id : ∀ a, hom a a;
  comp : ∀ a b c, hom a b → hom b c → hom a c;
  comp_assoc : ∀ a b c d (f : hom a b) (g : hom b c) (h : hom c d),
    comp _ _ _ f (comp _ _ _ g h) = comp _ _ _ (comp _ _ _ f g) h;
  left_id : ∀ a b (f : hom a b), comp _ _ _ f (id b) = f;
  right_id : ∀ a b (f : hom a b), comp _ _ _ (id a) f = f;
}.

Global Arguments hom {C} a b, _ _ _: rename.
Global Arguments id {C} a: rename.
Global Arguments comp C {a b c} f g : rename.
Global Arguments comp_assoc {C a b c d} f g h : rename.
Global Arguments left_id {C a b} f : rename.
Global Arguments right_id {C a b} f : rename.

Declare Scope category_scope.
Delimit Scope category_scope with category.

Local Open Scope category_scope.

Notation "g ∘@{ C } f" := (comp C f g) (at level 40, left associativity) : category_scope.
Notation "g ∘ f" := (comp _ f g) : category_scope.

Program Definition SingletonCat : category :=
  MkCat unit (λ _ _, unit) (λ _, ()) (λ _ _ _ _ _, ()) _ _ _.
Next Obligation. by intros ?? [] []. Qed.
Next Obligation. by intros ?? []. Qed.
Next Obligation. by intros ?? []. Qed.
Fail Next Obligation.

Record functor C D := MkFunc {
  o_map : obj C → obj D;
  h_map : ∀ a b, hom a b → hom (o_map a) (o_map b);
  h_map_comp : ∀ a b c (f : hom a b) (g : hom b c), h_map _ _ (g ∘ f) = h_map _ _ g ∘ h_map _ _ f;
  h_map_id : ∀ a, h_map _ _ (id a) = (id _);
}.

Global Arguments MkFunc {_ _} _ _ _ _.
Global Arguments o_map {C D} F a : rename.
Global Arguments h_map {C D} F [a b] f : rename.

Notation "( F ₒ)" := (o_map F) (format "( F ₒ)") : category_scope.
Notation "F 'ₒ' a" := (o_map F a) (at level 40, no associativity, format "F ₒ  a") :
    category_scope.
Notation "( F ₕ)" := (h_map F) (format "( F ₕ)") : category_scope.
Notation "F 'ₕ' f" := (h_map F f) (at level 40, no associativity, format "F ₕ  f" ) :
    category_scope.

Program Definition id_functor C : functor C C := MkFunc (λ c, c) (λ _ _ f, f) _ _.
Solve All Obligations with done.
Fail Next Obligation.

Program Definition functor_compose {C D E} (F : functor C D) (G : functor D E) : functor C E :=
MkFunc (λ c, G ₒ (F ₒ c)) (λ _ _ f, G ₕ (F ₕ f)) _ _.
Solve All Obligations with
  repeat intros ?; rewrite /= ?h_map_comp ?h_map_id; solve_by_eq_rewrite.
Fail Next Obligation.

Class FullFunctor {C D} (F : functor C D) :=
  full_func : ∀ a b (f : hom (F ₒ a) (F ₒ b)), {g : hom a b | F ₕ g = f}.
Global Arguments full_func {_ _} _ {_} [_ _] _.

Class FaithfulFunctor {C D} (F : functor C D) :=
  faithful_func : ∀ a b (f g : hom a b), F ₕ f = F ₕ g → f = g.
Global Arguments faithful_func {_ _} _ {_} [_ _] _ _.

Class FullyFaithfulFunctor {C D} (F : functor C D) := MkFFFunc {
  fully_faithful_full :: FullFunctor F;
  fully_faithful_faithful :: FaithfulFunctor F;
}.
Global Arguments MkFFFunc {_ _ _} _ _.

Definition hom_trans {C} {a b c d: obj C} (heq : a = c) (heq' : b = d) (f : hom a b) : hom c d :=
    match heq in _ = z return hom z _ with
      eq_refl =>
        match heq' in _ = w return hom _ w with
          eq_refl => f
        end
    end.

Lemma hom_trans_id {C a b} (Heq : a = b) : hom_trans Heq Heq (@id C a) = id b.
Proof. destruct Heq; done. Qed.

Lemma hom_trans_refl {C a b} (f : hom C a b) : hom_trans eq_refl eq_refl f = f.
Proof. done. Qed.

Lemma hom_trans_sym {C a b c d} heq heq' (f : hom C a b) (g : hom C c d) :
  hom_trans heq heq' f = g → f = hom_trans (eq_sym heq) (eq_sym heq') g.
Proof. destruct heq; destruct heq'; done. Qed.

Lemma hom_trans_sym' {C a b c d} heq heq' (f : hom C a b) (g : hom C c d) :
  hom_trans (eq_sym heq) (eq_sym heq') f = g → f = hom_trans heq heq' g.
Proof. destruct heq; destruct heq'; done. Qed.

Lemma hom_trans_sym_eq {C a b c d} heq heq' (f : hom C a b) (g : hom C c d) :
  hom_trans heq heq' f = g → f = hom_trans (eq_sym heq) (eq_sym heq') g.
Proof. destruct heq; destruct heq'; done. Qed.

Lemma hom_trans_sym_eq' {C a b c d} heq heq' (f : hom C a b) (g : hom C c d) :
  hom_trans (eq_sym heq) (eq_sym heq') f = g → f = hom_trans heq heq' g.
Proof. destruct heq; destruct heq'; done. Qed.

Lemma hom_trans_trans {C a b c d c' d'}
  (heq1 : a = c) (heq1' : b = d) (heq2 : c = c') (heq2' : d = d') (f : hom C a b) :
  hom_trans (eq_trans heq1 heq2) (eq_trans heq1' heq2') f =
  hom_trans heq2 heq2' (hom_trans heq1 heq1' f).
Proof. destruct heq1; destruct heq1'; destruct heq2; destruct heq2'; done. Qed.

Lemma hom_trans_compose {C} {a b c d e : obj C} (heq : a = d) (heq' : c = e)
  (f : hom a b) (g : hom b c) :
  hom_trans heq heq' (g ∘ f) = hom_trans eq_refl heq' g ∘ hom_trans heq eq_refl f.
Proof. destruct heq; destruct heq'; done. Qed.

Lemma hom_trans_compose_l {C} {a b c d e : obj C} (heq : a = c) (heq' : b = d)
  (f : hom a b) (g : hom d e) :
  g ∘ hom_trans heq heq' f = hom_trans (eq_sym heq') eq_refl g ∘ hom_trans heq eq_refl f.
Proof. destruct heq; destruct heq'; done. Qed.

Lemma hom_trans_compose_r {C} {e a b c d : obj C} (heq : a = c) (heq' : b = d)
  (f : hom a b) (g : hom e c) :
  hom_trans heq heq' f ∘ g = hom_trans eq_refl heq' f ∘ hom_trans eq_refl (eq_sym heq) g.
Proof. destruct heq; destruct heq'; done. Qed.

Lemma hom_trans_compose_take_in_l {C} {a b c d e : obj C} (heq : a = c) (heq' : b = d)
  (f : hom a b) (g : hom d e) :
  g ∘ hom_trans heq heq' f = hom_trans heq eq_refl (hom_trans (eq_sym heq') eq_refl g ∘ f).
Proof. destruct heq; destruct heq'; done. Qed.

Lemma hom_trans_compose_take_in_r {C} {e a b c d : obj C} (heq : a = c) (heq' : b = d)
  (f : hom a b) (g : hom e c) :
  hom_trans heq heq' f ∘ g = hom_trans eq_refl heq' (f ∘ hom_trans eq_refl (eq_sym heq) g).
Proof. destruct heq; destruct heq'; done. Qed.

Global Arguments hom_trans : simpl never.

Record functor_equiv {C D} (F G : functor C D) := MkFuncEq {
  func_eq_o_map : ∀ a, F ₒ a = G ₒ a;
  func_eq_h_map :
    ∀ a b (f : hom C a b), hom_trans (func_eq_o_map a) (func_eq_o_map b) (F ₕ f) = G ₕ f;
}.
Global Arguments MkFuncEq {_ _ _ _} _ _, {_ _} _ _ _ _.
Global Arguments func_eq_o_map {_ _ _ _} _ _.
Global Arguments func_eq_h_map {_ _ _ _} _ [_ _] _.

Global Instance functor_equiv_instance C D : Equiv (functor C D) := functor_equiv.
Global Instance functor_equiv_equiv C D : Equivalence (@functor_equiv C D).
Proof.
  split.
  - intros F; refine (MkFuncEq (λ _, eq_refl) _); done.
  - intros F G [Hoeq Hheq].
    refine (MkFuncEq (λ _, eq_sym (Hoeq _)) _).
    intros.
    symmetry; apply hom_trans_sym; rewrite Hheq; done.
  - intros ??? [Hoeq Hheq] [Hoeq' Hheq'].
    refine (MkFuncEq (λ _, eq_trans (Hoeq _) (Hoeq' _)) _).
    intros ???; rewrite hom_trans_trans Hheq; done.
Qed.

Lemma functor_equiv_uip {C D} {F G : functor C D}
  (p q : functor_equiv F G) : p = q.
Proof. apply proof_irrelevance. Qed.

Lemma functor_equiv_unpack {C D} {F G : functor C D}
  (p : functor_equiv F G) : F = G.
Proof.
  destruct F as [F1 F2 F3 F4];
    destruct G as [G1 G2 G3 G4].
  destruct p as [p1 p2].
  simpl in *.
  assert (F1 = G1) as Hf.
  { apply functional_extensionality, p1. }
  destruct Hf.
  assert (p1 = λ _, eq_refl).
  { apply proof_irrelevance. }
  subst p1.
  assert (F2 = G2) as Hf.
  {
    apply functional_extensionality_dep; intros x.
    apply functional_extensionality_dep; intros y.
    apply functional_extensionality; intros f.
    rewrite /hom_trans in p2.
    apply (p2 x y f).
  }
  destruct Hf.
  assert (F3 = G3) as ->.
  { apply proof_irrelevance. }
  assert (F4 = G4) as ->.
  { apply proof_irrelevance. }
  reflexivity.
Qed.

Lemma functor_equiv_pack {C D} {F G : functor C D}
  (p : F = G) : functor_equiv F G.
Proof. by rewrite p. Qed.

Lemma functor_equiv_pack_unpack {C D} {F G : functor C D}
  (p : F = G) : functor_equiv_unpack (functor_equiv_pack p) = p.
Proof. apply proof_irrelevance. Qed.

Lemma functor_equiv_unpack_pack {C D} {F G : functor C D}
  (p : functor_equiv F G) : functor_equiv_pack (functor_equiv_unpack p) = p.
Proof. apply proof_irrelevance. Qed.

Lemma functor_equiv_canon {C D} {F G : functor C D}
  (J : functor_equiv F G)
  (H : F = G) : H = functor_equiv_unpack J.
Proof. apply proof_irrelevance. Qed.

Definition o_map_eq {C D} (F : functor C D) {a b : obj C} (Heq : a = b) : F ₒ a = F ₒ b :=
  f_equal (F ₒ) Heq.

Lemma o_map_eq_refl {C D} (F : functor C D) (a : obj C) : @o_map_eq _ _ F a a eq_refl = eq_refl.
Proof. done. Qed.

Lemma o_map_eq_sym {C D} (F : functor C D) {a b : obj C} (Heq : a = b) :
  o_map_eq F (eq_sym Heq) = eq_sym (o_map_eq F Heq).
Proof. rewrite /o_map_eq eq_sym_map_distr //. Qed.

Lemma o_map_eq_trans {C D} (F : functor C D) {a b c : obj C} (Heq : a = b) (Heq' : b = c) :
  o_map_eq F (eq_trans Heq Heq') = eq_trans (o_map_eq F Heq) (o_map_eq F Heq').
Proof. rewrite /o_map_eq eq_trans_map_distr //. Qed.

Lemma h_map_eq {C D} (F : functor C D) {a b a' b': obj C} (Heqa : a = a') (Heqb : b = b')
  (h : hom a b) :
  hom_trans (o_map_eq F Heqa) (o_map_eq F Heqb) (F ₕ h) = F ₕ (hom_trans Heqa Heqb h).
Proof. destruct Heqa; destruct Heqb; done. Qed.

Lemma h_map_eq_l {C D} (F : functor C D) {a b a': obj C} (Heqa : a = a')
  (h : hom a b) :
  hom_trans (o_map_eq F Heqa) eq_refl (F ₕ h) = F ₕ (hom_trans Heqa eq_refl h).
Proof. destruct Heqa; done. Qed.

Lemma h_map_eq_r {C D} (F : functor C D) {a b b': obj C} (Heqb : b = b')
  (h : hom a b) :
  hom_trans eq_refl (o_map_eq F Heqb) (F ₕ h) = F ₕ (hom_trans eq_refl Heqb h).
Proof. destruct Heqb; done. Qed.

Program Definition Cat : category :=
  MkCat category functor id_functor (λ _ _ _ F G, functor_compose F G) _ _ _.
Next Obligation.
  intros ???? F G H; rewrite /=.
  apply functor_equiv_unpack.
  refine (MkFuncEq (functor_compose F (functor_compose G H))
    (functor_compose (functor_compose F G) H) (λ _, eq_refl) _); done.
Qed.
Next Obligation.
  intros ?? F; rewrite /=.
  apply functor_equiv_unpack.
  refine (MkFuncEq (functor_compose F (id_functor _)) F (λ _, eq_refl) _); done.
Qed.
Next Obligation.
  intros ?? F; rewrite /=.
  apply functor_equiv_unpack.
  refine (MkFuncEq (functor_compose (id_functor _) F) F (λ _, eq_refl) _); done.
Qed.

Program Definition cat_prod (C D : category) : category :=
  MkCat
    (obj C * obj D)
    (λ cd cd', hom C cd.1 cd'.1 * hom D cd.2 cd'.2)%type
    (λ cd, (id cd.1, id cd.2))
    (λ _ _ _ f g, (g.1 ∘ f.1, g.2 ∘ f.2))
    _ _ _.
Solve All Obligations with
  repeat first [intros []|intros ?]; simpl in *; try f_equiv; solve_by_eq_rewrite.
Fail Next Obligation.

Program Definition cat_proj1 C D : functor (cat_prod C D) C :=
  MkFunc (λ cd, cd.1) (λ _ _ f, f.1) (λ _ _ _ _ _, reflexivity _) (λ _, reflexivity _).
Program Definition cat_proj2 C D : functor (cat_prod C D) D :=
  MkFunc (λ cd, cd.2) (λ _ _ f, f.2) (λ _ _ _ _ _, reflexivity _) (λ _, reflexivity _).

Program Definition functor_prod {C D C' D'} (F : functor C D) (G : functor C' D') :
  functor (cat_prod C C') (cat_prod D D') :=
  MkFunc (λ ab, (F ₒ ab.1, G ₒ ab.2)) (λ _ _ f, (F ₕ f.1, G ₕ f.2)) _ _.
Solve All Obligations with
  repeat intros ?; rewrite /=; f_equiv; rewrite ?h_map_comp ?h_map_id; solve_by_eq_rewrite.
Fail Next Obligation.

Program Definition functor_diag {C} :
  functor C (cat_prod C C) :=
  MkFunc (λ x, (x, x)) (λ _ _ f, (f, f)) _ _.
Solve All Obligations with
  repeat intros ?; rewrite /=; f_equiv; rewrite ?h_map_comp ?h_map_id; solve_by_eq_rewrite.
Fail Next Obligation.

Program Definition functor_to_prod {C D E} (F : functor C D) (G : functor C E) :
  functor C (cat_prod D E) :=
  MkFunc (λ a, (F ₒ a, G ₒ a)) (λ _ _ f, (F ₕ f, G ₕ f)) _ _.
Solve All Obligations with
  repeat intros ?; rewrite /=; f_equiv; rewrite ?h_map_comp ?h_map_id; solve_by_eq_rewrite.
Fail Next Obligation.

Program Definition const_functor {C} (c : obj C) : functor SingletonCat C :=
  MkFunc (λ _, c) (λ _ _ _, id c) _ _.
Solve All Obligations with repeat intros ?; rewrite /= ?left_id //.
Fail Next Obligation.

Record natural {C D} (F G : functor C D) := MkNat {
  nat_map : ∀ c, hom (F ₒ c) (G ₒ c);
  naturality : ∀ a b (f : hom a b), nat_map b ∘ (F ₕ f) = (G ₕ f) ∘ nat_map a;
}.
Global Arguments MkNat {_ _ _ _} _ _.
Global Arguments nat_map {C D F G} η c : rename.
Global Arguments naturality {C D F G} η [a b] f : rename.

Notation "( η ₙ)" := (nat_map η) (format "( η ₙ)") : category_scope.
Notation "η 'ₙ' c" := (nat_map η c) (at level 40, no associativity, format "η ₙ  c") :
    category_scope.

(* Functor categories *)

Global Instance natural_eq {C D} {F G : functor C D} : Equiv (natural F G) :=
  λ η ρ, ∀ a, η ₙ a = ρ ₙ a.

Global Instance natural_eq_equiv C D (F G : functor C D)
  : Equivalence (@natural_eq _ _ F G).
Proof.
  split.
  - intros η; by intros ?.
  - intros η η' H.
    intros ?; by symmetry.
  - intros ??? H J.
    by intros c; rewrite (H c) (J c).
Qed.

Program Definition natural_id {C D} (F : functor C D) : natural F F := MkNat (λ x, id (F ₒ x)) _.
Solve All Obligations with by intros ??????; rewrite /= left_id right_id.
Fail Next Obligation.

Program Definition natural_comp {C D} {F G H : functor C D} (η : natural F G) (ρ : natural G H) :
  natural F H := MkNat (λ c, (ρ ₙ c) ∘ (η ₙ c)) _.
Solve All Obligations with
  by repeat intros ?; rewrite /= !comp_assoc naturality -!comp_assoc naturality.
Fail Next Obligation.

Lemma natural_equiv_uip {C D} {F G : functor C D} {η η' : natural F G}
  (p q : natural_eq η η') : p = q.
Proof. apply proof_irrelevance. Qed.

Lemma natural_equiv_unpack {C D} {F G : functor C D}
  {η ρ : natural F G}
  (p : natural_eq η ρ) : η = ρ.
Proof.
  destruct η as [η1 η2];
    destruct ρ as [ρ1 ρ2].
  simpl in *.
  assert (η1 = ρ1) as Hf.
  { apply functional_extensionality_dep; intros x. apply p. }
  destruct Hf.
  assert (η2 = ρ2) as Hf.
  { apply proof_irrelevance. }
  destruct Hf.
  reflexivity.
Qed.

Lemma natural_equiv_pack {C D} {F G : functor C D}
  {η η' : natural F G}
  (p : η = η') : natural_eq η η'.
Proof. rewrite p. apply natural_eq_equiv. Qed.

Lemma natural_equiv_pack_unpack {C D} {F G : functor C D}
  {η η' : natural F G}
  (p : η = η') : natural_equiv_unpack (natural_equiv_pack p) = p.
Proof. apply proof_irrelevance. Qed.

Lemma natural_equiv_unpack_pack {C D} {F G : functor C D}
  {η η' : natural F G}
  (p : natural_eq η η') : natural_equiv_pack (natural_equiv_unpack p) = p.
Proof. apply proof_irrelevance. Qed.

Lemma natural_equiv_canon {C D} {F G : functor C D}
  {η η' : natural F G}
  (J : natural_eq η η')
  (H : η = η') : H = natural_equiv_unpack J.
Proof. apply proof_irrelevance. Qed.

Lemma natural_comp_left_id :
  ∀ (C D : category) (F G : functor C D) (η : natural F G), natural_comp η (natural_id _) = η.
Proof.
  repeat intros ?.
  apply natural_equiv_unpack. intros ?. rewrite /= left_id //.
Qed.
Lemma natural_comp_right_id :
  ∀ (C D : category) (F G : functor C D) (η : natural F G), natural_comp (natural_id _) η = η.
Proof.
  repeat intros ?.
  apply natural_equiv_unpack. intros ?. rewrite /= right_id //.
Qed.

Program Definition FuncCat C D :=
  MkCat (functor C D) natural natural_id (@natural_comp C D) _ _ _.
Next Obligation.
  intros.
  apply natural_equiv_unpack.
  intros ?; simpl.
  by rewrite comp_assoc.
Qed.
Next Obligation.
  intros.
  apply natural_equiv_unpack.
  intros ?; simpl.
  by rewrite left_id.
Qed.
Next Obligation.
  intros.
  apply natural_equiv_unpack.
  intros ?; simpl.
  by rewrite right_id.
Qed.
Fail Next Obligation.

Lemma hom_trans_nat {C D} {F G F' G' : functor C D}
  (p : F = F' :> obj (FuncCat _ _)) (q : G = G') (f : natural F G)
  : ∀ a, nat_map (hom_trans p q (f : hom (C := FuncCat _ _) F G)) a
         = hom_trans (equal_f (f_equal o_map p) a)
             (equal_f (f_equal o_map q) a) (nat_map f a).
Proof.
  intros.
  destruct p, q.
  simpl.
  rewrite hom_trans_refl.
  rewrite /equal_f /eq_ind_r /= hom_trans_refl.
  reflexivity.
Qed.

Program Definition functor_fix_left_o_map
  {C D E : category} (F : functor (cat_prod C D) E) (c : obj C) : functor D E :=
  MkFunc
    (λ d, @o_map (cat_prod C D) E F (c, d))
    (λ d d' f, @h_map (cat_prod C D) E F (c, d) (c, d') (id c, f)) _ _.
Next Obligation. repeat intros ?; rewrite -h_map_comp /= left_id //. Qed.
Next Obligation. repeat intros ?; rewrite /= h_map_id //. Qed.
Fail Next Obligation.

Program Definition functor_fix_left_h_map
  {C D E : category} (F : functor (cat_prod C D) E) [c c': obj C] (h : hom c c') :
  natural (functor_fix_left_o_map F c) (functor_fix_left_o_map F c') :=
  MkNat
    (λ d, @h_map (cat_prod C D) E F (c, d) (c', d) (h, id d))
    _.
Next Obligation. repeat intros ?; rewrite /= -!h_map_comp /= !left_id !right_id //. Qed.
Fail Next Obligation.

Program Definition functor_fix_left
  {C D E : category} (F : functor (cat_prod C D) E) :
  functor C (FuncCat D E) :=
  MkFunc
    (functor_fix_left_o_map F)
    (functor_fix_left_h_map F) _ _.
Next Obligation.
  repeat intros ?; apply natural_equiv_unpack.
  intros ?.
  rewrite /= -h_map_comp /= left_id //.
Qed.
Next Obligation.
  repeat intros ?; apply natural_equiv_unpack.
  intros ?.
  rewrite /= h_map_id //.
Qed.
Fail Next Obligation.

Program Definition functor_fix_right_o_map
  {C D E : category} (F : functor (cat_prod C D) E) (d : obj D) : functor C E :=
  MkFunc
    (λ c, @o_map (cat_prod C D) E F (c, d))
    (λ c c' f, @h_map (cat_prod C D) E F (c, d) (c', d) (f, id d)) _ _.
Next Obligation. repeat intros ?; rewrite -h_map_comp /= left_id //. Qed.
Next Obligation. repeat intros ?; rewrite /= h_map_id //. Qed.
Fail Next Obligation.

Program Definition functor_fix_right_h_map
  {C D E : category} (F : functor (cat_prod C D) E) [d d': obj D] (h : hom d d') :
  natural (functor_fix_right_o_map F d) (functor_fix_right_o_map F d') :=
  MkNat
    (λ c, @h_map (cat_prod C D) E F (c, d) (c, d') (id c, h))
    _.
Next Obligation. repeat intros ?; rewrite /= -!h_map_comp /= !left_id !right_id //. Qed.
Fail Next Obligation.

Program Definition functor_fix_right
  {C D E : category} (F : functor (cat_prod C D) E) :
  functor D (FuncCat C E) :=
  MkFunc
    (functor_fix_right_o_map F)
    (functor_fix_right_h_map F) _ _.
Next Obligation.
  repeat intros ?; apply natural_equiv_unpack.
  intros ?.
  rewrite /= -h_map_comp /= left_id //.
Qed.
Next Obligation.
  repeat intros ?; apply natural_equiv_unpack.
  intros ?.
  rewrite /= h_map_id //.
Qed.
Fail Next Obligation.

Program Definition hor_comp {C D E} {F G : functor C D} {F' G' : functor D E}
  (η : natural F G) (η' : natural F' G') : natural (functor_compose F F') (functor_compose G G') :=
  MkNat (λ a, (η' ₙ (G ₒ a)) ∘ (F' ₕ (η ₙ a))) _.
Next Obligation.
  repeat intros ?; rewrite /=.
  rewrite !naturality !comp_assoc !naturality -!comp_assoc -!h_map_comp !naturality //.
Qed.
Fail Next Obligation.

Program Definition functor_compose_func C D E :
  functor (cat_prod (FuncCat C D) (FuncCat D E)) (FuncCat C E) :=
  MkFunc (λ FG, functor_compose FG.1 FG.2) (λ _ _ ηη', hor_comp ηη'.1 ηη'.2) _ _.
Next Obligation.
  intros ??? [F1 G1] [F2 G2] [F3 G3].
  intros [η12 η12'] [η23 η23'].
  apply natural_equiv_unpack.
  intros ?; simpl in *.
  rewrite !comp_assoc; f_equiv.
  rewrite !naturality h_map_comp !comp_assoc; done.
Qed.
Next Obligation. repeat intros ?; apply natural_equiv_unpack; intros ?; rewrite /= h_map_id left_id //. Qed.
Fail Next Obligation.

Definition functor_compose_on_left {C D} (F : functor C D) E :
  functor (FuncCat D E) (FuncCat C E) :=
  functor_fix_left_o_map (functor_compose_func C D E) F.

Definition functor_compose_on_right {C D} (F : functor C D) A :
  functor (FuncCat A C) (FuncCat A D) :=
  functor_fix_right_o_map (functor_compose_func A C D) F.

Program Definition functor_eq_natural {C D} {F G : functor C D} (Heq : functor_equiv F G) : natural F G :=
  MkNat (λ a, hom_trans eq_refl (func_eq_o_map Heq a) (id _)) _.
Next Obligation.
  repeat intros ?; simpl.
  rewrite hom_trans_compose_take_in_r left_id /= hom_trans_refl.
  rewrite hom_trans_compose_take_in_l right_id /= hom_trans_refl.
  change (eq_refl (G ₒ b)) with (eq_sym (eq_refl (G ₒ b))).
  apply hom_trans_sym.
  rewrite -hom_trans_trans /= eq_trans_refl_l.
  apply Heq.
Qed.
Fail Next Obligation.

Definition opposite C :=
  MkCat (obj C) (λ a b, hom C b a) id (λ a b c, flip (comp C))
  (λ _ _ _ _ f g h, symmetry (comp_assoc h g f))
  (λ _ _ f, right_id f)
  (λ _ _ f, left_id f).

Notation "C 'ᵒᵖ'" := (opposite C) (at level 1, format "C ᵒᵖ").

Program Definition opposite_func {C D} (F : functor C D) : functor (C ᵒᵖ) (D ᵒᵖ) :=
  MkFunc (λ c : obj (C ᵒᵖ), F ₒ c) (λ _ _ f, F ₕ f) _ _.
Solve All Obligations
  with repeat intros ?; rewrite /= ?h_map_comp ?h_map_id; solve_by_eq_rewrite.
Fail Next Obligation.

(* Isomorphisms *)

Record isomorphism {C a b} (f : hom C a b) (g : hom C b a) := MkIso {
  iso_lr : g ∘ f = id _;
  iso_rl : f ∘ g = id _;
}.
Global Arguments MkIso {_ _ _ _ _} _ _.
Global Arguments iso_lr {_ _ _ _ _} _.
Global Arguments iso_rl {_ _ _ _ _} _.

Record isomorphic {C} a b := MkIsoIc {
  forward : hom C a b;
  backward : hom C b a;
  is_iso : isomorphism forward backward
}.
Global Arguments MkIsoIc {_ _ _} _ _ _.
Global Arguments forward {_ _ _} _.
Global Arguments backward {_ _ _} _.
Global Arguments is_iso {_ _ _} _.

Infix "≃" := isomorphic (at level 70, no associativity) : category_scope.
Infix "≃@{ C }" := (@isomorphic C) (at level 70, only parsing, no associativity) : category_scope.

Program Definition isomorphism_id {C} c : isomorphism (@id C c) (@id C c) := MkIso _ _.
Solve All Obligations with by repeat intros ?; rewrite left_id.
Fail Next Obligation.
Definition isomorphism_swap {C a b} {f : hom C a b} {g : hom C b a} (iso : isomorphism f g) :
  isomorphism g f := MkIso (iso_rl iso) (iso_lr iso).
Program Definition isomorphism_compose {C a b c}
  {f : hom C a b} {g : hom C b a} (iso : isomorphism f g)
  {h : hom C b c} {i : hom C c b} (iso : isomorphism h i) :
  isomorphism (h ∘ f) (g ∘ i) := MkIso _ _.
Next Obligation.
  intros ???? f g isofg h i isohi.
  rewrite (comp_assoc _ _ g) -(comp_assoc _ _ i) (iso_lr isohi) left_id (iso_lr isofg) //.
Qed.
Next Obligation.
  intros ???? f g isofg h i isohi.
  rewrite (comp_assoc _ _ h) -(comp_assoc _ _ f) (iso_rl isofg) left_id (iso_rl isohi) //.
Qed.
Fail Next Obligation.

Definition isomorphic_refl {C} (c : obj C) : isomorphic c c := MkIsoIc _ _ (isomorphism_id _).
Definition isomorphic_sym {C} {a b : obj C} : isomorphic a b → isomorphic b a :=
  λ iso, MkIsoIc _ _ (isomorphism_swap (is_iso iso)).
Definition isomorphic_trans {C} {a b c : obj C} :
  isomorphic a b → isomorphic b c → isomorphic a c :=
  λ iso1 iso2, MkIsoIc _ _ (isomorphism_compose (is_iso iso1) (is_iso iso2)).

Definition isomorphic_of {C a b} {f : hom C a b} {g : hom C b a} (iso : isomorphism f g) :
  isomorphic a b := MkIsoIc _ _ iso.

Lemma compose_along_iso_right {C} {a b : obj C} (iso : a ≃ b) {c} (f g : hom b c) :
  f ∘ forward iso = g ∘ forward iso → f = g.
Proof.
  intros Heq.
  rewrite -(right_id f) -(right_id g).
  rewrite -(iso_rl (is_iso iso)) -!comp_assoc Heq //.
Qed.

Lemma compose_along_iso_left {C} {b c : obj C} (iso : b ≃ c) [a] (f g : hom a b) :
  forward iso ∘ f = forward iso ∘ g → f = g.
Proof.
  intros Heq.
  rewrite -(left_id f) -(left_id g).
  rewrite -(iso_lr (is_iso iso)) !comp_assoc Heq //.
Qed.

Program Definition functor_preserves_iso
  {C D} (F : functor C D) [a b : obj C] (iso : a ≃ b) : F ₒ a ≃ F ₒ b :=
  MkIsoIc (F ₕ (forward iso)) (F ₕ (backward iso)) _.
Next Obligation.
  intros ????? iso; split;
    rewrite -h_map_comp ?(iso_lr (is_iso iso)) ?(iso_rl (is_iso iso)) h_map_id //.
Qed.
Fail Next Obligation.

Program Definition prod_of_isos {C D c c' d d'} (iso1 : c ≃@{C} c') (iso2 : d ≃@{D} d') :
  (c, d) ≃@{cat_prod C D} (c', d') :=
  MkIsoIc (forward iso1, forward iso2) (backward iso1, backward iso2) _.
Next Obligation.
  repeat intros ?; split; rewrite /=.
  - rewrite (iso_lr (is_iso iso1)) (iso_lr (is_iso iso2)) //.
  - rewrite (iso_rl (is_iso iso1)) (iso_rl (is_iso iso2)) //.
Qed.
Fail Next Obligation.

Program Definition iso_op {C c d} (iso : c ≃@{C} d) : c ≃@{C ᵒᵖ} d :=
  MkIsoIc (backward iso) (forward iso) _.
Next Obligation.
  intros ??? iso; split.
  - apply (iso_lr (is_iso iso)).
  - apply (iso_rl (is_iso iso)).
Qed.
Fail Next Obligation.

Program Definition natural_iso_proj
  {C D} {F G : functor C D} (iso : F ≃@{FuncCat C D} G) (c : obj C) :
  F ₒ c ≃ G ₒ c :=
  MkIsoIc (forward iso ₙ c) (backward iso ₙ c) _.
Next Obligation.
  intros ?? F G iso c; split; pose proof (is_iso iso) as [H1 H2]; simpl.
  - by apply natural_equiv_pack in H1.
  - by apply natural_equiv_pack in H2.
Qed.
Fail Next Obligation.

(* fully faithful functors reflect isomorphisms. *)
Program Definition fully_faithful_iso {C D} (F : functor C D) `{!FullyFaithfulFunctor F}
  [a b : obj C] (iso : F ₒ a ≃ F ₒ b) : a ≃ b :=
  MkIsoIc `(full_func F (forward iso)) `(full_func F (backward iso)) _.
Next Obligation.
  intros ?? F ? ?? iso.
  pose proof (is_iso iso) as [Hfb Hbf].
  rewrite -(proj2_sig (full_func F (forward iso))) in Hfb.
  rewrite -(proj2_sig (full_func F (forward iso))) in Hbf.
  rewrite -(proj2_sig (full_func F (backward iso))) in Hfb.
  rewrite -(proj2_sig (full_func F (backward iso))) in Hbf.
  rewrite -h_map_comp -h_map_id in Hfb.
  rewrite -h_map_comp -h_map_id in Hbf.
  apply (faithful_func F) in Hfb, Hbf.
  split; done.
Qed.
Fail Next Obligation.

(* Discrete categories *)

Program Definition Discr (A : Type) :=
  MkCat A (=) (@eq_refl A) (@eq_trans A) _ _ _.
Next Obligation.
  intros; simpl.
  apply proof_irrelevance.
Qed.
Next Obligation.
  by intros; simpl.
Qed.
Next Obligation.
  intros; simpl.
  by rewrite eq_trans_refl_l.
Qed.
Fail Next Obligation.

Definition EmpCat := Discr Empty.

Program Definition func_from_EmpCat C : functor EmpCat C :=
  MkFunc (λ a, Empty_rect _ a) (λ a _ _, Empty_rect (λ _, hom C _ _) a) _ _.
Solve All Obligations with by simpl.
Fail Next Obligation.

Definition UnitCat := Discr unit.

Program Definition func_to_UnitCat C : functor C UnitCat :=
  MkFunc (λ _, ()) (λ _ _ _, reflexivity _) _ _.
Solve All Obligations with by repeat intros ?.
Fail Next Obligation.

Definition id_fun A : A → A := λ x, x.
Arguments id_fun A x /.
Definition compose_fun A B C : (A → B) → (B → C) → A → C :=
  λ f g x, g (f x).
Arguments compose_fun A B C f g / x.

Program Definition Typ :=
  MkCat Type (→) (id_fun) (compose_fun) _ _ _.
Next Obligation.
  intros; simpl.
  by extensionality x.
Qed.
Next Obligation.
  intros; simpl.
  by extensionality x.
Qed.
Next Obligation.
  intros; simpl.
  by extensionality x.
Qed.
Fail Next Obligation.

Lemma typ_iso_inj {A B : Type} (iso : A ≃@{Typ} B) (x y : A) :
  forward iso x = forward iso y → x = y.
Proof.
  intros Heq.
  change x with (id_fun A x).
  change y with (id_fun A y).
  pose proof (iso_lr (is_iso iso)) as Hlr; simpl in Hlr; rewrite -Hlr.
  rewrite Heq.
  by f_equiv.
Qed.

Definition typ_conv {A B : Type} (Heq : A = B) (a : A) : B :=
  match Heq in _ = u return u with eq_refl => a end.

Lemma hom_trans_typ_conv {A B C D : Type}
  (Heq : A = C) (Heq' : B = D) (f : A → B) (x : C) :
  hom_trans (C := Typ) Heq Heq' f x =
  hom_trans (C := Typ) eq_refl Heq' f (typ_conv (eq_sym Heq) x).
Proof. destruct Heq; done. Qed.

Lemma hom_trans_typ_conv' {A B C D : Type}
  (Heq : A = C) (Heq' : B = D) (f : A → B) (x : C) :
  hom_trans (C := Typ) Heq Heq' f x =
  typ_conv Heq' (f (typ_conv (eq_sym Heq) x)).
Proof. destruct Heq; destruct Heq'; done. Qed.

Lemma typ_conv_trans {A B C : Type} (Heq : A = B) (Heq' : B = C) x :
  typ_conv (eq_trans Heq Heq') x = typ_conv Heq' (typ_conv Heq x).
Proof. destruct Heq; destruct Heq'; done. Qed.

Lemma typ_conv_sym {A B : Type} (Heq : A = B) (a : A) (b : B) :
  typ_conv Heq a = b ↔ a = typ_conv (eq_sym Heq) b.
Proof. destruct Heq; done. Qed.

Program Definition natural_set {C D} (F G : functor C D) : Type :=
  natural F G.

(* Presheaf categories *)

Definition PreSheaf C := functor (C ᵒᵖ) Typ.

Definition PSh C := FuncCat (C ᵒᵖ) Typ.

(* A version of naturality tailored to presheaves useful for rewriting. *)
Lemma psh_naturality {C} {F G : PreSheaf C} (η : natural F G) :
  ∀ (a b : obj C) (f : hom a b) z , (η ₙ a) ((F ₕ f) z) = ((G ₕ f)) ((η ₙ b) z).
Proof.
  repeat intros ?.
  apply (equal_f (naturality η _) _).
Qed.

(* Hom functor *)

Program Definition hom_typ {C} (a b : obj C) : Type := hom C a b.

Definition compose_as_hom_typ_map {C a b c d} (f : hom C a b) (g : hom C c d) :
  (hom_typ b c) → (hom_typ a d) := λ h, g ∘ h ∘ f.
Arguments compose_as_hom_typ_map {_ _ _ _ _} f g / _.

Program Definition Hom C : functor (cat_prod (C ᵒᵖ) C) Typ :=
  MkFunc (λ ab, hom_typ (C := C) ab.1 ab.2)
    (λ _ _ f, compose_as_hom_typ_map (C := C) f.1 f.2) _ _.
Next Obligation.
  intros; simpl.
  extensionality x; simpl.
  rewrite !comp_assoc.
  reflexivity.
Qed.
Next Obligation.
  intros; simpl.
  extensionality x; simpl.
  rewrite left_id right_id //=.
Qed.
Fail Next Obligation.

Program Definition in_left_of_hom C D :
  functor ((FuncCat C D) ᵒᵖ) (FuncCat (cat_prod (C ᵒᵖ) D) Typ) :=
  MkFunc
    (λ F, functor_compose (functor_prod (opposite_func F) (id_functor D)) (Hom D))
    (λ _ _ η, MkNat (λ cd, (λ f, f ∘ (η ₙ cd.1))) _)
    _
    _.
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality x.
  rewrite !comp_assoc -naturality //.
Qed.
Next Obligation.
  repeat intros ?; simpl in *.
  apply natural_equiv_unpack; intros ?; simpl.
  extensionality h; simpl.
  rewrite comp_assoc.
  reflexivity.
Qed.
Next Obligation.
  repeat intros ?; simpl in *.
  apply natural_equiv_unpack; intros ?; simpl.
  extensionality h; simpl.
  rewrite right_id.
  reflexivity.
Qed.
Fail Next Obligation.

Program Definition in_left_of_hom_full C D : FullFunctor (in_left_of_hom C D) :=
  λ F G η, exist _ (MkNat (λ c, (η ₙ (c, F ₒ c)) (id (F ₒ c))) _) _.
Next Obligation.
  intros ?? F G η a b f; simpl in *.
  pose proof (equal_f (@naturality _ _ _ _ η (a, F ₒ a) (a, F ₒ b) (id _, F ₕ f)) (id _)) as Hn.
  rewrite /= !h_map_id !right_id in Hn.
  rewrite -Hn.
  pose proof (equal_f (@naturality _ _ _ _ η (b, F ₒ b) (a, F ₒ b) (f, id _)) (id _)) as Hn'.
  rewrite /= !left_id in Hn'.
  rewrite -Hn' //.
Qed.
Next Obligation.
  intros ?? F G η. apply natural_equiv_unpack; intros [a b].
  extensionality f. simpl.
  pose proof (equal_f (@naturality _ _ _ _ η (a, F ₒ a) (a, b) (id _, f))
                 (id _)) as Hn.
  rewrite /= !h_map_id !right_id in Hn.
  rewrite -Hn //.
Qed.
Fail Next Obligation.

Lemma in_left_of_hom_faithful C D : FaithfulFunctor (in_left_of_hom C D).
Proof.
  intros F G η η' Heq; apply natural_equiv_unpack; intros c.
  pose proof (equal_f (natural_equiv_pack Heq (c, F ₒ c)) (id _)) as H.
  simpl in H.
  rewrite !left_id in H. done.
Qed.

Global Instance in_left_of_hom_fully_faithful C D :
  FullyFaithfulFunctor (in_left_of_hom C D) :=
  MkFFFunc (in_left_of_hom_full C D) (in_left_of_hom_faithful C D).

Program Definition in_right_of_hom C D :
  functor (FuncCat D C) (FuncCat (cat_prod (C ᵒᵖ) D) Typ) :=
  MkFunc
    (λ F, functor_compose (functor_prod (id_functor (C ᵒᵖ)) F) (Hom C))
    (λ _ _ η, MkNat (λ cd, (λ f, (η ₙ cd.2) ∘ f)) _)
    _
    _.
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality x.
  rewrite -!comp_assoc naturality //.
Qed.
Next Obligation.
  repeat intros ?; simpl in *.
  apply natural_equiv_unpack.
  intros x; simpl.
  extensionality h.
  rewrite comp_assoc //.
Qed.
Next Obligation.
  repeat intros ?; simpl in *.
  apply natural_equiv_unpack.
  intros x; simpl.
  extensionality h.
  rewrite left_id //.
Qed.
Fail Next Obligation.

Program Definition in_right_of_hom_full C D : FullFunctor (in_right_of_hom C D) :=
  λ F G η, exist _ (MkNat (λ c, (η ₙ (F ₒ c, c)) (id (F ₒ c))) _) _.
Next Obligation.
  intros ?? F G η a b f; simpl in *.
  pose proof (equal_f (@naturality _ _ _ _ η (F ₒ b, b) (F ₒ a, b) (F ₕ f, id _))
                (id _)) as Hn.
  rewrite /= !h_map_id !left_id in Hn.
  rewrite -Hn.
  pose proof (equal_f (@naturality _ _ _ _ η (F ₒ a, a) (F ₒ a, b) (id _, f))
                (id _)) as Hn'.
  rewrite /= !right_id in Hn'.
  rewrite -Hn' //.
Qed.
Next Obligation.
  intros ?? F G η. apply natural_equiv_unpack; intros [a b].
  extensionality f; simpl in *.
  pose proof (equal_f (@naturality _ _ _ _ η (F ₒ b, b) (a, b) (f, id _))
                 (id _)) as Hn.
  rewrite /= !h_map_id !left_id in Hn.
  rewrite -Hn //.
Qed.
Fail Next Obligation.

Lemma in_right_of_hom_faithful C D : FaithfulFunctor (in_right_of_hom C D).
Proof.
  intros F G η η' Heq.
  apply natural_equiv_unpack; intros c.
  pose proof (equal_f (natural_equiv_pack Heq (F ₒ c, c)) (id _)) as H.
  rewrite /= !right_id in H; done.
Qed.

Program Definition discr_psh {C} (A : Type) : obj (PSh C) :=
  MkFunc (λ _, A) (λ a b f, id_fun _) _ _.
Next Obligation. repeat intros ?; done. Qed.
Next Obligation. repeat intros ?; done. Qed.
Fail Next Obligation.

Notation "Δ{ A }" := (discr_psh A)
                       (at level 20, no associativity) : category_scope.

Global Instance in_right_of_hom_fully_faithful C D :
  FullyFaithfulFunctor (in_right_of_hom C D) :=
  MkFFFunc (in_right_of_hom_full C D) (in_right_of_hom_faithful C D).

(* Adjunctions. *)

Definition adjunction {C D} (F : functor C D) (U : functor D C) : Type :=
  in_left_of_hom C D ₒ F ≃@{FuncCat (cat_prod (C ᵒᵖ) D) Typ} in_right_of_hom C D ₒ U.

(* Yoneda embedding *)

Program Definition yoneda C : functor C (PSh C) := functor_fix_right (Hom C).

Global Arguments yoneda {_}, _.

Program Definition yoneda_lemma_forward {C} (F : PreSheaf C) :
  natural
    (functor_compose (opposite_func yoneda) (functor_fix_right (Hom (PSh C)) ₒ F))
    F :=
  MkNat (λ c, λ f, (f ₙ c) (id c)) _.
Next Obligation.
  intros ?????. extensionality η; simpl in *.
  rewrite !right_id -(psh_naturality η) /= !left_id //.
Qed.
Fail Next Obligation.
Program Definition yoneda_lemma_backward {C} (F : PreSheaf C) :
  natural
    F
    (functor_compose (opposite_func yoneda) (functor_fix_right (Hom (PSh C)) ₒ F)) :=
  MkNat (λ c, λ x, (MkNat (λ w, λ f, (F ₕ f) x) _)) _.
Next Obligation.
  repeat intros ?. extensionality z; simpl in *. rewrite left_id h_map_comp //.
Qed.
Next Obligation.
  repeat intros ?; extensionality z; simpl in *.
  apply natural_equiv_unpack.
  intros ?; simpl.
  extensionality z'.
  rewrite right_id h_map_comp //.
Qed.
Fail Next Obligation.

Program Definition yoneda_lemma {C} (F : PreSheaf C) :
  functor_compose (opposite_func yoneda) (functor_fix_right (Hom (PSh C)) ₒ F)
  ≃@{PSh C} F :=
  MkIsoIc (yoneda_lemma_forward F) (yoneda_lemma_backward F) _.
Next Obligation.
  repeat intros ?; split.
  - apply natural_equiv_unpack.
    intros ?.
    extensionality η.
    apply natural_equiv_unpack.
    intros x.
    extensionality X.
    simpl in *.
    rewrite -(psh_naturality η) /= !left_id //.
  - repeat intros ?; simpl in *.
    apply natural_equiv_unpack.
    intros ?; simpl.
    extensionality x.
    rewrite h_map_id //=.
Qed.

Program Definition yoneda_full C : FullFunctor (yoneda C) :=
  λ a b (f : hom (yoneda C ₒ a) (yoneda C ₒ b)), exist _ ((f ₙ a) (id a)) _.
Next Obligation.
  intros C a b f.
  apply natural_equiv_unpack.
  intros c.
  extensionality z.
  simpl in *.
  rewrite /= right_id.
  pose proof (equal_f (naturality f z) (id a)) as Hn.
  simpl in *.
  rewrite !left_id in Hn.
  done.
Qed.

Lemma yoneda_faithful C : FaithfulFunctor (yoneda C).
  intros a b f g Heq.
  pose proof (equal_f (natural_equiv_pack Heq a) (id a)) as H.
  rewrite /= !right_id in H; done.
Qed.

Global Instance yoneda_fully_faithful C : FullyFaithfulFunctor (yoneda C) :=
  MkFFFunc (yoneda_full C) (yoneda_faithful C).

(* Terminal Object *)

Record is_terminal {C} (t : obj C) :=
  MkIsTerm { bang : ∀ c, hom c t; bang_unique : ∀ c (f : hom c t), f = bang c }.
Global Arguments MkIsTerm {_} _ _.
Global Arguments bang {_ _} _.
Global Arguments bang_unique {_ _} _ [_] _.

Record terminal C := MkTerm { term : obj C; term_is_terminal : is_terminal term; }.
Global Arguments MkTerm {_} _ _.
Global Arguments term {_} _.
Global Arguments term_is_terminal {_} _.

Program Definition is_term_unique {C} {t t' : obj C} :
  is_terminal t → is_terminal t' → t ≃ t' :=
  λ it it', MkIsoIc (bang it' t) (bang it t') _.
Next Obligation.
Proof.
  split.
  - rewrite ?(bang_unique it (id _)) ?(bang_unique it (_ ∘ _)) //.
  - rewrite ?(bang_unique it' (id _)) ?(bang_unique it' (_ ∘ _)) //.
Qed.
Fail Next Obligation.

Class HasTerm C := term_of : terminal C.
Global Arguments term_of _ {_}.

Definition term_obj C `{!HasTerm C} : obj C := term (term_of C).

Definition term_hom `{!HasTerm C} (c : obj C) : hom c (term_obj C) :=
  bang (term_is_terminal (term_of C)) c.

Notation "1ₒ@{ C }" := (term_obj C) (at level 20, no associativity) : category_scope.
Notation "'1ₒ'" := (term_obj _) (at level 20, no associativity) : category_scope.
Notation "'!ₕ'" := term_hom (at level 20, no associativity) : category_scope.

Lemma term_hom_unique `{!HasTerm C} {c} (f : hom c (1ₒ)) : f = !ₕ c.
Proof. apply bang_unique. Qed.

Lemma term_hom_unique' `{!HasTerm C} {c} (f g : hom c (1ₒ)) : f = g.
Proof. rewrite (term_hom_unique f) (term_hom_unique g) //. Qed.

Lemma term_hom_is_id `{!HasTerm C} : !ₕ (1ₒ) = id (1ₒ).
Proof. apply term_hom_unique'. Qed.

Global Program Instance cat_has_term : HasTerm Cat :=
  MkTerm SingletonCat (MkIsTerm _ (λ c, MkFunc (λ _, ()) (λ _ _ _, ()) _ _) _).
Next Obligation. repeat intros ?; done. Qed.
Next Obligation. repeat intros ?; done. Qed.
Next Obligation.
  repeat intros ?; simpl.
  erewrite functor_equiv_unpack; first reflexivity.
  unshelve econstructor.
  - intros; simpl.
    by destruct (f ₒ a).
  - intros; simpl.
    apply unit_pi.
Qed.
Fail Next Obligation.

(* Initial Object *)

Record is_initial {C} (i : obj C) := MkIsInit {
  inverted_bang : ∀ c, hom i c;
  inverted_bang_unique : ∀ c (f : hom i c), f = inverted_bang c }.
Global Arguments MkIsInit {_} _ _.
Global Arguments inverted_bang {_ _} _.
Global Arguments inverted_bang_unique {_ _} _ [_] _.

Record initial C := MkInit { init : obj C; init_is_initial : is_initial init; }.
Global Arguments MkInit {_} _ _.
Global Arguments init {_} _.
Global Arguments init_is_initial {_} _.

Program Definition is_initial_unique {C} (i i' : obj C) :
  is_initial i → is_initial i' → i ≃ i' :=
  λ ii ii', MkIsoIc (inverted_bang ii i') (inverted_bang ii' i) _.
Next Obligation.
Proof.
  split.
  - rewrite ?(inverted_bang_unique ii (id _)) ?(inverted_bang_unique ii (_ ∘ _)) //.
  - rewrite ?(inverted_bang_unique ii' (id _)) ?(inverted_bang_unique ii' (_ ∘ _)) //.
Qed.
Fail Next Obligation.

Class HasInit C := init_of : initial C.
Global Arguments init_of _ {_}.

Definition init_obj C `{!HasInit C} : obj C := init (init_of C).

Definition init_hom `{!HasInit C} (c : obj C) : hom (init_obj C) c :=
  inverted_bang (init_is_initial (init_of C)) c.

Notation "0ₒ@{ C }" := (init_obj C) (at level 20, no associativity) : category_scope.
Notation "'0ₒ'" := (init_obj _) (at level 20, no associativity) : category_scope.
Notation "'¡ₕ'" := init_hom (at level 20, no associativity) : category_scope.

Lemma init_hom_unique `{!HasInit C} {c} (f : hom (0ₒ) c) : f = ¡ₕ c.
Proof. apply inverted_bang_unique. Qed.

Lemma init_hom_unique' `{!HasInit C} {c} (f g : hom (0ₒ) c) : f = g.
Proof. rewrite (init_hom_unique f) (init_hom_unique g) //. Qed.

(* Terminal object of Typ and PSh. *)

Global Program Instance typ_has_term : HasTerm Typ :=
  MkTerm unit (MkIsTerm _ (λ _, λ _, ()) _).
Next Obligation. repeat intros ?; simpl. extensionality x. apply unit_pi. Qed.
Fail Next Obligation.

Program Definition term_func C D `{!HasTerm D} : functor C D :=
  MkFunc (λ _, 1ₒ) (λ _ _ _, !ₕ _) _ _.
Solve All Obligations with repeat intros ?; rewrite /=; apply term_hom_unique'.
Fail Next Obligation.

Program Definition func_cat_has_term C D `{!HasTerm D} : HasTerm (FuncCat C D) :=
  MkTerm (term_func C D) (MkIsTerm _ (λ _, MkNat (λ _, !ₕ _) _) _).
Next Obligation.
  intros; simpl.
  apply term_hom_unique'.
Qed.
Next Obligation.
  intros; simpl.
  apply natural_equiv_unpack.
  intros ?; simpl.
  apply term_hom_unique'.
Qed.
Fail Next Obligation.

Global Instance psh_has_term C : HasTerm (PSh C) := func_cat_has_term _ _.

(* Products *)

Record product {C} (a b : obj C) := MkProd {
  prd : obj C;
  prj1 : hom prd a;
  prj2 : hom prd b;
  prd_hom d (p1 : hom d a) (p2 : hom d b) : hom d prd;
  prd_hom_commutes1 d p1 p2 : p1 = prj1 ∘ (prd_hom d p1 p2);
  prd_hom_commutes2 d p1 p2 : p2 = prj2 ∘ (prd_hom d p1 p2);
  prd_hom_unique d p1 p2 (h : hom d prd) :
    p1 = prj1 ∘ h → p2 = prj2 ∘ h → h = prd_hom d p1 p2;
}.

Global Arguments MkProd {_ _ _} _ _ _ _ _ _ _.
Global Arguments prd {_ _ _} _.
Global Arguments prj1 {_ _ _} _.
Global Arguments prj2 {_ _ _} _.
Global Arguments prd_hom {_ _ _} _ {_} _ _.
Global Arguments prd_hom_commutes1 {_ _ _} _ {_} _ _.
Global Arguments prd_hom_commutes2 {_ _ _} _ {_} _ _.
Global Arguments prd_hom_unique {_ _ _} _ {_} _ _ _.

Lemma prd_hom_unique' {C} {a b : obj C} (p : product a b) {d : obj C}
  (p1 : hom d a) (p2 : hom d b) (h1 h2 : hom d (prd p)) :
  p1 = prj1 p ∘ h1 → p2 = prj2 p ∘ h1 → p1 = prj1 p ∘ h2 → p2 = prj2 p ∘ h2 → h1 = h2.
Proof.
  intros.
  erewrite (prd_hom_unique _ _ _ h1); [|eassumption|eassumption].
  erewrite (prd_hom_unique _ _ _ h2); [|eassumption|eassumption].
  done.
Qed.

Class HasProducts C := product_of (a b : obj C) : product a b.
Global Arguments product_of {_ _} _ _, _ {_} _ _.

Definition obj_prod `{!HasProducts C} a b : obj C := prd (product_of a b).

(* Product of two homomorphisms. *)
Definition hom_prod `{!HasProducts C} {a b c d} (f : hom a c) (g : hom b d) :
  hom (obj_prod a b) (obj_prod c d) := prd_hom _ (f ∘ prj1 _) (g ∘ prj2 _).

(* Morphism from an object into a product. *)
Definition hom_to_prod `{!HasProducts C} {a c d} (f : hom a c) (g : hom a d) :
  hom a (obj_prod c d) := prd_hom _ f g.

Infix "×ₒ@{ C }" := (obj_prod (C := C)) (at level 40, left associativity) : category_scope.
Infix "×ₒ" := obj_prod (at level 40, left associativity) : category_scope.
Infix "×ₕ@{ C }" := (hom_prod (C := C)) (at level 40, left associativity) : category_scope.
Infix "×ₕ" := hom_prod (at level 40, left associativity) : category_scope.
Notation "<< f , g >>" :=
  (hom_to_prod f g) (at level 20, no associativity) : category_scope.

Lemma hom_prod_comp `{!HasProducts C} {a b c d e f}
  (g1 : hom a c) (g2 : hom c e) (h1 : hom b d) (h2 : hom d f) :
  (g2 ∘ g1) ×ₕ (h2 ∘ h1) = (g2 ×ₕ h2) ∘ (g1 ×ₕ h1).
Proof.
  symmetry; apply prd_hom_unique.
  - rewrite -!comp_assoc -prd_hom_commutes1 !comp_assoc -prd_hom_commutes1 //.
  - rewrite -!comp_assoc -prd_hom_commutes2 !comp_assoc -prd_hom_commutes2 //.
Qed.
Lemma hom_prod_id `{!HasProducts C} {a b} : (id a) ×ₕ (id b) = id (a ×ₒ b).
Proof. symmetry; apply prd_hom_unique; rewrite left_id right_id //. Qed.

Lemma hom_prod_comp_left_id `{!HasProducts C} {a b d f}
  (h1 : hom b d) (h2 : hom d f) : (id a) ×ₕ (h2 ∘ h1) = (id a ×ₕ h2) ∘ (id a ×ₕ h1).
Proof. rewrite -{1}(left_id (id a)) hom_prod_comp //. Qed.
Lemma hom_prod_comp_right_id `{!HasProducts C} {a b c e}
  (g1 : hom a c) (g2 : hom c e) : (g2 ∘ g1) ×ₕ (id b) = (g2 ×ₕ id b) ∘ (g1 ×ₕ id b).
Proof. rewrite -{1}(left_id (id b)) hom_prod_comp //. Qed.

Lemma hom_prod_split `{!HasProducts C} {a b c d} (f : hom a c) (g : hom b d) :
  f ×ₕ g = id _ ×ₕ g ∘ (f ×ₕ id _).
Proof. rewrite -hom_prod_comp left_id right_id //. Qed.

Lemma hom_prod_prj1 `{!HasProducts C} {a b c d} (f : hom a c) (g : hom b d) :
  prj1 _ ∘ (f ×ₕ g) = f ∘ prj1 _.
Proof. rewrite /hom_prod -prd_hom_commutes1 //. Qed.
Lemma hom_prod_prj2 `{!HasProducts C} {a b c d} (f : hom a c) (g : hom b d) :
  prj2 _ ∘ (f ×ₕ g) = g ∘ prj2 _.
Proof. rewrite /hom_prod -prd_hom_commutes2 //. Qed.

Program Definition prod_func C `{!HasProducts C} : functor (cat_prod C C) C :=
  MkFunc (λ ab, ab.1 ×ₒ ab.2) (λ _ _ h, h.1 ×ₕ h.2) _ _.
Next Obligation. repeat intros ?; apply hom_prod_comp. Qed.
Next Obligation. repeat intros ?; apply hom_prod_id. Qed.
Fail Next Obligation.

Program Definition iso_prod `{!HasProducts C} {a b c d} (iso : a ≃@{C} c) (iso' : b ≃@{C} d) :
  (a ×ₒ b) ≃ (c ×ₒ d) :=
  MkIsoIc (forward iso ×ₕ forward iso') (backward iso ×ₕ backward iso') _.
Next Obligation.
  repeat intros; split.
  - rewrite -hom_prod_comp.
    destruct (is_iso iso) as [-> _]. destruct (is_iso iso') as [-> _].
    rewrite hom_prod_id //.
  - rewrite -hom_prod_comp.
    destruct (is_iso iso) as [_ ->]. destruct (is_iso iso') as [_ ->].
    rewrite hom_prod_id //.
Qed.

Lemma hom_to_prod_comp `{!HasProducts C} {a b c d e}
  (g1 : hom a b) (g2 : hom b d) (h1 : hom a c) (h2 : hom c e) :
  <<g2 ∘ g1, h2 ∘ h1>> = (g2 ×ₕ h2) ∘ <<g1, h1>>.
Proof.
  symmetry; apply prd_hom_unique.
  - rewrite -!comp_assoc -prd_hom_commutes1 !comp_assoc -prd_hom_commutes1 //.
  - rewrite -!comp_assoc -prd_hom_commutes2 !comp_assoc -prd_hom_commutes2 //.
Qed.
Lemma hom_to_prod_prj1 `{!HasProducts C} {a b c} (f : hom a b) (g : hom a c) :
  prj1 _ ∘ <<f, g>> = f.
Proof. rewrite /hom_prod -prd_hom_commutes1 //. Qed.
Lemma hom_to_prod_prj2 `{!HasProducts C} {a b c} (f : hom a b) (g : hom a c) :
  prj2 _ ∘ <<f, g>> = g.
Proof. rewrite /hom_prod -prd_hom_commutes2 //. Qed.
Lemma hom_to_prod_comp_left_id `{!HasProducts C} {a b d}
  (h1 : hom a b) (h2 : hom b d) : <<id a, h2 ∘ h1>> = (id a ×ₕ h2) ∘ <<id a, h1>>.
Proof. rewrite -hom_to_prod_comp left_id //. Qed.
Lemma hom_to_prod_comp_right_id `{!HasProducts C} {a b d}
  (h1 : hom a b) (h2 : hom b d) : <<h2 ∘ h1, id a>> = (h2 ×ₕ id a) ∘ <<h1,id a>>.
Proof. rewrite -hom_to_prod_comp right_id //. Qed.
Lemma hom_to_prod_split `{!HasProducts C} {a b c} (f : hom a b) (g : hom a c) :
  <<f, g>> = (id b ×ₕ g) ∘ <<f, id a>>.
Proof. rewrite -hom_to_prod_comp left_id right_id //. Qed.
Lemma hom_to_prod_split' `{!HasProducts C} {a b c} (f : hom a b) (g : hom a c) :
  <<f, g>> = (f ×ₕ id c) ∘ <<id a, g>>.
Proof. rewrite -hom_to_prod_comp left_id right_id //. Qed.
Lemma hom_to_prod_to_hom_prod `{!HasProducts C} {a b c} (f : hom a b) (g : hom a c) :
  <<f, g>> = (f ×ₕ g) ∘ <<id a, id a>>.
Proof. rewrite -hom_to_prod_comp !right_id //. Qed.
Lemma hom_to_prod_comp_r `{!HasProducts C} {a b c d}
  (g1 : hom b c) (g2 : hom b d) (h : hom a b) :
  <<g1, g2>> ∘ h =  <<g1 ∘ h, g2 ∘ h>>.
Proof.
  eapply prd_hom_unique'.
  - rewrite -comp_assoc hom_to_prod_prj1; reflexivity.
  - rewrite -comp_assoc hom_to_prod_prj2; reflexivity.
  - rewrite hom_to_prod_prj1; reflexivity.
  - rewrite hom_to_prod_prj2; reflexivity.
Qed.
Lemma hom_to_prod_of_prjs `{!HasProducts C} {a b c} (f : hom a (b ×ₒ c)) :
  << prj1 _ ∘ f, prj2 _ ∘ f>> =  f.
Proof.
  eapply prd_hom_unique'; [| |reflexivity|reflexivity].
  - rewrite hom_to_prod_prj1 //.
  - rewrite hom_to_prod_prj2 //.
Qed.

Definition term_times_proj `{!HasTerm C, !HasProducts C} (a : obj C) : hom (1ₒ ×ₒ a) a := prj2 _.
Definition term_times_inj `{!HasTerm C, !HasProducts C} (a : obj C) : hom a (1ₒ ×ₒ a) :=
  <<!ₕ _, id _>>.

Lemma hom_to_prod_bangs `{!HasTerm C, !HasProducts C} :
  <<id (1ₒ), id (1ₒ)>> = term_times_inj (1ₒ).
Proof. apply prd_hom_unique; apply term_hom_unique'. Qed.

Lemma term_times_proj_inj `{!HasTerm C, !HasProducts C} a :
  term_times_proj a ∘ term_times_inj a = id a.
Proof. rewrite /term_times_proj /term_times_inj hom_to_prod_prj2 //. Qed.

Lemma term_times_inj_proj `{!HasTerm C, !HasProducts C} a :
  term_times_inj a ∘ term_times_proj a = id (1ₒ ×ₒ a).
Proof.
  rewrite /term_times_proj /term_times_inj.
  eapply prd_hom_unique'; [| |by rewrite right_id|by rewrite right_id].
  - rewrite -comp_assoc hom_to_prod_prj1; apply term_hom_unique'.
  - rewrite -comp_assoc hom_to_prod_prj2 left_id //.
Qed.

Definition term_times_isomorphic `{!HasTerm C, !HasProducts C} a : (1ₒ ×ₒ a) ≃ a :=
  MkIsoIc _ _ (MkIso (term_times_inj_proj _) (term_times_proj_inj _)).

Definition commutator `{!HasProducts C} (a b : obj C) : hom (a ×ₒ b) (b ×ₒ a) :=
  <<prj2 _, prj1 _>>.

Lemma commutator_involutive `{!HasProducts C} a b : commutator a b ∘ commutator b a = id (b ×ₒ a).
Proof.
  rewrite /commutator; eapply prd_hom_unique';
    [| |by rewrite right_id|by rewrite right_id].
  - rewrite -comp_assoc hom_to_prod_prj1 hom_to_prod_prj2 //.
  - rewrite -comp_assoc hom_to_prod_prj2 hom_to_prod_prj1 //.
Qed.

Definition product_comm `{!HasProducts C} a b : (a ×ₒ b) ≃ (b ×ₒ a) :=
  MkIsoIc _ _ (MkIso (commutator_involutive _ _) (commutator_involutive _ _)).

Lemma commute_hom_prod `{!HasProducts C} {a b c d} (f : hom a c) (g : hom b d) :
  (f ×ₕ g) ∘ commutator _ _ = commutator _ _ ∘ (g ×ₕ f).
Proof.
  rewrite /commutator -hom_to_prod_comp.
  eapply prd_hom_unique';
    [rewrite hom_to_prod_prj1 //|rewrite hom_to_prod_prj2 //| |].
  - rewrite -comp_assoc hom_to_prod_prj1 hom_prod_prj2 //.
  - rewrite -comp_assoc hom_to_prod_prj2 hom_prod_prj1 //.
Qed.

Lemma commute_hom_to_prod `{!HasProducts C} {a b c} (f : hom a b) (g : hom a c) :
  commutator b c ∘ <<f, g>> = <<g, f>>.
Proof.
  rewrite /commutator; eapply prd_hom_unique.
  - rewrite -comp_assoc hom_to_prod_prj1 hom_to_prod_prj2 //.
  - rewrite -comp_assoc hom_to_prod_prj2 hom_to_prod_prj1 //.
Qed.

Lemma commute_term_times_proj `{!HasTerm C, !HasProducts C} a :
  (term_times_proj a) ∘ (commutator a (1ₒ)) =  prj1 (product_of a (1ₒ)).
Proof. rewrite /commutator /term_times_proj hom_to_prod_prj2 //. Qed.

Lemma proj_term_times_inj `{!HasTerm C, !HasProducts C} a :
  term_times_inj a ∘ prj1 (product_of a (1ₒ)) = commutator a (1ₒ).
Proof.
  rewrite /commutator /term_times_inj; apply prd_hom_unique.
  - rewrite -!comp_assoc hom_to_prod_prj1; apply term_hom_unique'.
  - rewrite -!comp_assoc hom_to_prod_prj2 left_id //.
Qed.

Definition associator `{!HasProducts C} (a b c : obj C) : hom ((a ×ₒ b) ×ₒ c) (a ×ₒ (b ×ₒ c)) :=
  <<prj1 _ ∘ prj1 _, <<prj2 _ ∘ prj1 _, prj2 _>>>>.

Definition associator' `{!HasProducts C} (a b c : obj C) : hom (a ×ₒ (b ×ₒ c)) ((a ×ₒ b) ×ₒ c) :=
  <<<<prj1 _, prj1 _ ∘ prj2 _>>, prj2 _ ∘ prj2 _>>.

Lemma associator_associator' `{!HasProducts C} a b c :
  associator a b c ∘ associator' a b c = id (a ×ₒ (b ×ₒ c)).
Proof.
  rewrite /associator /associator';
    eapply prd_hom_unique'; [| |by rewrite right_id|by rewrite right_id].
  { rewrite -comp_assoc hom_to_prod_prj1 comp_assoc !hom_to_prod_prj1 //. }
  rewrite -comp_assoc hom_to_prod_prj2.
  eapply prd_hom_unique'; [| |reflexivity|reflexivity].
  - rewrite -comp_assoc hom_to_prod_prj1.
    rewrite !comp_assoc !hom_to_prod_prj1 !hom_to_prod_prj2 //.
  - rewrite -comp_assoc !hom_to_prod_prj2 //.
Qed.

Lemma associator'_associator `{!HasProducts C} a b c :
  associator' a b c ∘ associator a b c = id ((a ×ₒ b) ×ₒ c).
Proof.
  rewrite /associator /associator';
    eapply prd_hom_unique'; [| |by rewrite right_id|by rewrite right_id];
    last first.
  { rewrite -comp_assoc !hom_to_prod_prj2 comp_assoc !hom_to_prod_prj2 //. }
  rewrite -comp_assoc hom_to_prod_prj1.
  eapply prd_hom_unique'; [| |reflexivity|reflexivity].
  - rewrite -comp_assoc !hom_to_prod_prj1 //.
  - rewrite -comp_assoc hom_to_prod_prj2.
    rewrite !comp_assoc !hom_to_prod_prj2 !hom_to_prod_prj1 //.
Qed.

Definition product_assoc `{!HasProducts C} a b c :
  (a ×ₒ (b ×ₒ c)) ≃ ((a ×ₒ b) ×ₒ c) :=
  MkIsoIc _ _
    (MkIso (associator_associator' _ _ _) (associator'_associator _ _ _)).

Lemma prj1_associator `{!HasProducts C} (a b c : obj C) :
  prj1 _ ∘ associator a b c = prj1 _ ∘ prj1 _.
Proof. rewrite /associator hom_to_prod_prj1 //. Qed.

Lemma prj2_associator `{!HasProducts C} (a b c : obj C) :
  prj2 _ ∘ associator a b c = <<prj2 _ ∘ prj1 _, prj2 _>>.
Proof. rewrite /associator hom_to_prod_prj2 //. Qed.

Lemma prj1_associator' `{!HasProducts C} (a b c : obj C) :
  prj1 _ ∘ associator' a b c = <<prj1 _, prj1 _ ∘ prj2 _>>.
Proof. rewrite /associator hom_to_prod_prj1 //. Qed.

Lemma prj2_associator' `{!HasProducts C} (a b c : obj C) :
  prj2 _ ∘ associator' a b c = prj2 _ ∘ prj2 _.
Proof. rewrite /associator hom_to_prod_prj2 //. Qed.

Lemma pentagon `{!HasProducts C} (a b c d : obj C) :
  (id a ×ₕ associator b c d) ∘ associator a (b ×ₒ c) d ∘ ((associator a b c) ×ₕ id d) =
  associator a b (c ×ₒ d) ∘ associator (a ×ₒ b) c d.
Proof.
  eapply prd_hom_unique'.
  { rewrite -!comp_assoc hom_prod_prj1 left_id.
    rewrite prj1_associator comp_assoc hom_prod_prj1 //. }
  { rewrite -!comp_assoc hom_prod_prj2 //. }
  { rewrite -!comp_assoc !prj1_associator !comp_assoc !prj1_associator //. }
  rewrite -comp_assoc prj2_associator.
  eapply prd_hom_unique'.
  { rewrite -!comp_assoc prj1_associator.
    rewrite !comp_assoc -(comp_assoc _ _ (prj2 _)).
    rewrite prj2_associator.
    rewrite -(comp_assoc _ (<<_, _>>)) hom_to_prod_prj1.
    rewrite !comp_assoc hom_prod_prj1.
    rewrite -(comp_assoc _ _ (prj2 _)).
    rewrite prj2_associator -comp_assoc hom_to_prod_prj1.
    done. }
  { rewrite -!comp_assoc prj2_associator //. }
  { rewrite -comp_assoc hom_to_prod_prj1 !comp_assoc prj1_associator //. }
  rewrite -comp_assoc hom_to_prod_prj2 prj2_associator.
  eapply prd_hom_unique'.
  { rewrite -!comp_assoc hom_to_prod_prj1.
    rewrite !(comp_assoc _ (prj2 _)) prj2_associator.
    rewrite (comp_assoc _ (prj1 _)) hom_to_prod_prj1.
    rewrite !comp_assoc hom_prod_prj1.
    rewrite -!comp_assoc (comp_assoc _ (prj2 _)) prj2_associator.
    rewrite hom_to_prod_prj2 //. }
  { rewrite -!comp_assoc hom_to_prod_prj2.
    rewrite !(comp_assoc _ (prj2 _)) prj2_associator.
    rewrite !hom_to_prod_prj2 left_id //. }
  { rewrite hom_to_prod_prj1 //. }
  rewrite hom_to_prod_prj2 //.
Qed.

Lemma pentagon' `{!HasProducts C} (a b c d : obj C) :
  ((associator' a b c) ×ₕ id d) ∘ associator' a (b ×ₒ c) d ∘ (id a ×ₕ associator' b c d) =
   associator' (a ×ₒ b) c d ∘ associator' a b (c ×ₒ d).
Proof.
  apply (compose_along_iso_right (isomorphic_sym (product_assoc _ _ _))); simpl.
  rewrite !comp_assoc associator'_associator right_id.
  apply (compose_along_iso_right (isomorphic_sym (product_assoc _ _ _))); simpl.
  rewrite !comp_assoc associator'_associator.
  rewrite -!comp_assoc.
  apply (compose_along_iso_left
           (iso_prod
              (isomorphic_sym (product_assoc _ _ _))
              (isomorphic_refl _))); simpl.
  rewrite right_id.
  rewrite -!comp_assoc.
  epose proof (is_iso
                 (iso_prod
                  (isomorphic_sym (product_assoc a b c))
                  (isomorphic_refl d))) as [_ Hrl];
    simpl in Hrl; rewrite Hrl; clear Hrl.
  rewrite left_id.
  apply (compose_along_iso_left (isomorphic_sym (product_assoc _ _ _))); simpl.
  rewrite -!comp_assoc associator_associator' left_id.
  apply (compose_along_iso_left
           (iso_prod
              (isomorphic_refl a)
              (isomorphic_sym (product_assoc b c d)))); simpl.
  rewrite -!comp_assoc.
  epose proof (is_iso
               (iso_prod
                  (isomorphic_refl a)
                  (isomorphic_sym (product_assoc b c d)))).
  epose proof (is_iso
               (iso_prod
                  (isomorphic_refl a)
                  (isomorphic_sym (product_assoc b c d)))) as [_ Hrl];
    simpl in Hrl; rewrite Hrl; clear Hrl.
  rewrite left_id.
  rewrite pentagon //.
Qed.

Lemma associate_hom_to_prod `{!HasProducts C} {a b c d} (f : hom a b) (g : hom a c) (h : hom a d) :
  associator b c d ∘ <<<<f, g>>, h>> = <<f, <<g, h>>>>.
Proof.
  rewrite /associator.
  eapply prd_hom_unique.
  { rewrite -comp_assoc -prd_hom_commutes1 comp_assoc !hom_to_prod_prj1 //. }
  eapply prd_hom_unique'.
  { rewrite !hom_to_prod_prj1 //. }
  { rewrite !hom_to_prod_prj2 //. }
  - repeat rewrite -(comp_assoc (prd_hom _ _ _)) -?prd_hom_commutes2 -?prd_hom_commutes1.
    rewrite comp_assoc -prd_hom_commutes1.
    rewrite hom_to_prod_prj2 //.
  - repeat rewrite -(comp_assoc (prd_hom _ _ _)) -?prd_hom_commutes2 -?prd_hom_commutes1 //.
Qed.

Lemma associate'_hom_to_prod `{!HasProducts C} {a b c d} (f : hom a b) (g : hom a c) (h : hom a d) :
  associator' b c d ∘ <<f, <<g, h>>>> = <<<<f, g>>, h>>.
Proof.
  apply (compose_along_iso_left (isomorphic_sym (product_assoc _ _ _))).
  rewrite /= -!comp_assoc associator_associator' left_id.
  rewrite associate_hom_to_prod //.
Qed.

Lemma associator_twist1 `{!HasProducts C} {a b c a' b' c'}
 (f : hom a a') (g : hom b b') (h : hom c c') :
  associator a' b' c' ∘ (f ×ₕ g ×ₕ h) ∘ associator' a b c = (f ×ₕ (g ×ₕ h)).
Proof.
  rewrite /associator /associator'.
  eapply prd_hom_unique'; [| |by rewrite hom_prod_prj1|by rewrite hom_prod_prj2].
  - rewrite -!comp_assoc -prd_hom_commutes1.
    rewrite !comp_assoc -(comp_assoc _ (f ×ₕ g ×ₕ h)) hom_prod_prj1.
    rewrite comp_assoc -prd_hom_commutes1.
    rewrite -comp_assoc -prd_hom_commutes1 comp_assoc -prd_hom_commutes1 //.
  - rewrite -!comp_assoc -prd_hom_commutes2.
    eapply prd_hom_unique';
      [by rewrite -comp_assoc hom_prod_prj1|
       by rewrite -comp_assoc hom_prod_prj2| |].
    + rewrite -!comp_assoc -prd_hom_commutes1.
      rewrite !comp_assoc -(comp_assoc _ (f ×ₕ g ×ₕ h)) hom_prod_prj1.
      rewrite !comp_assoc -prd_hom_commutes1.
      rewrite -!comp_assoc hom_prod_prj2.
      rewrite !comp_assoc -prd_hom_commutes2 //.
    + rewrite -!comp_assoc -prd_hom_commutes2.
      rewrite !comp_assoc -(comp_assoc _ (f ×ₕ g ×ₕ h)) hom_prod_prj2.
      rewrite !comp_assoc -prd_hom_commutes2 //.
Qed.

Lemma associator_twist2 `{!HasProducts C} {a b c a' b' c'}
 (f : hom a a') (g : hom b b') (h : hom c c') :
  associator a' b' c' ∘ (f ×ₕ g ×ₕ h) = (f ×ₕ (g ×ₕ h)) ∘ associator a b c.
Proof.
  apply (compose_along_iso_right (product_assoc _ _ _)).
  rewrite /= !comp_assoc associator_associator' right_id -comp_assoc.
  apply associator_twist1.
Qed.

Lemma associator'_twist1 `{!HasProducts C} {a b c a' b' c'}
 (f : hom a a') (g : hom b b') (h : hom c c') :
  associator' a' b' c' ∘ (f ×ₕ (g ×ₕ h)) ∘ associator a b c = (f ×ₕ g ×ₕ h).
Proof.
  apply (compose_along_iso_left (isomorphic_sym (product_assoc _ _ _))).
  rewrite /= -!comp_assoc associator_associator' left_id.
  apply (compose_along_iso_right (product_assoc _ _ _)).
  rewrite /= comp_assoc associator_associator' right_id.
  symmetry; apply associator_twist1.
Qed.

Lemma associator'_twist2 `{!HasProducts C} {a b c a' b' c'}
 (f : hom a a') (g : hom b b') (h : hom c c') :
  associator' a' b' c' ∘ (f ×ₕ (g ×ₕ h)) = (f ×ₕ g ×ₕ h) ∘ associator' a b c.
Proof.
  apply (compose_along_iso_right (isomorphic_sym (product_assoc _ _ _))).
  rewrite /= !comp_assoc associator'_associator right_id -comp_assoc.
  apply associator'_twist1.
Qed.

Lemma associate'_term_times_inj `{!HasTerm C, !HasProducts C} a :
  associator' a (1ₒ) (1ₒ) ∘ (id a ×ₕ term_times_inj (1ₒ)) =
  (commutator _ _ ∘ term_times_inj a) ×ₕ id (1ₒ).
Proof.
  rewrite /associator' /commutator /term_times_inj.
  eapply prd_hom_unique';
    [|apply term_hom_unique'|by rewrite -prd_hom_commutes1|reflexivity].
  eapply prd_hom_unique'; [|apply term_hom_unique'|reflexivity| reflexivity].
  rewrite -!comp_assoc -!prd_hom_commutes1 -!prd_hom_commutes2.
  rewrite !comp_assoc -(comp_assoc (_ ×ₕ _)) -!prd_hom_commutes1.
  rewrite -!comp_assoc -!prd_hom_commutes1 //.
Qed.

(* Products in Typ and PSh. *)

Global Program Instance typ_has_products : HasProducts Typ :=
  λ A B, MkProd (A * B)%type (λ ab, ab.1) (λ ab, ab.2)
           (λ _ p1 p2, λ x, (p1 x, p2 x)) _ _ _.
Next Obligation.
  intros; simpl.
  reflexivity.
Qed.
Next Obligation.
  intros; simpl.
  reflexivity.
Qed.
Next Obligation.
  intros ????? h H G; simpl.
  extensionality x.
  simpl in *.
  rewrite H G //.
  destruct (h x); reflexivity.
Qed.
Fail Next Obligation.

Program Definition func_prod {C D} `{!HasProducts D} (F G : functor C D) : functor C D :=
  MkFunc (λ c, (F ₒ c) ×ₒ (G ₒ c)) (λ _ _ f, (F ₕ f) ×ₕ (G ₕ f)) _ _.
Solve All Obligations with
  repeat intros ?; rewrite /= ?h_map_comp ?h_map_id
  ?hom_prod_comp ?hom_prod_id //; solve_by_eq_rewrite.
Fail Next Obligation.

Program Definition func_prj1 {C D} `{!HasProducts D} (F G : functor C D) : natural (func_prod F G) F :=
  MkNat (λ c, prj1 _) _.
Next Obligation. repeat intros ?; rewrite /= hom_prod_prj1 //. Qed.
Fail Next Obligation.

Program Definition func_prj2  {C D} `{!HasProducts D} (F G : functor C D) : natural (func_prod F G) G :=
  MkNat (λ c, prj2 _) _.
Next Obligation. repeat intros ?; rewrite /= hom_prod_prj2 //. Qed.
Fail Next Obligation.

Program Definition func_prd_hom  {C D} `{!HasProducts D} (F G H : functor C D)
  (p1 : natural H F) (p2 : natural H G) : natural H (func_prod F G) :=
  MkNat (λ c, prd_hom _ (p1 ₙ c) (p2 ₙ c)) _.
Next Obligation.
  repeat intros ?; rewrite /=; eapply prd_hom_unique';
    [rewrite -comp_assoc -prd_hom_commutes1 //|rewrite -comp_assoc -prd_hom_commutes2 //| |].
  - rewrite -comp_assoc hom_prod_prj1 comp_assoc -prd_hom_commutes1 naturality //.
  - rewrite -comp_assoc hom_prod_prj2 comp_assoc -prd_hom_commutes2 naturality //.
Qed.
Fail Next Obligation.

Program Definition func_cat_has_products C D `{!HasProducts D} : HasProducts (FuncCat C D) :=
  λ F G, MkProd (func_prod F G) (func_prj1 F G) (func_prj2 F G) (func_prd_hom F G) _ _ _.
Next Obligation.
  repeat intros ?.
  apply natural_equiv_unpack; intros ?.
  rewrite /= -prd_hom_commutes1 //.
Qed.
Next Obligation.
  repeat intros ?.
  apply natural_equiv_unpack; intros ?.
  rewrite /= -prd_hom_commutes2 //.
Qed.
Next Obligation.
  intros ????????? Hcm1 Hcm2.
  apply natural_equiv_unpack; intros c.
  rewrite /=; apply prd_hom_unique; by [rewrite Hcm1|rewrite Hcm2].
Qed.

Global Instance psh_has_products C : HasProducts (PSh C) :=
  @func_cat_has_products (C ᵒᵖ) Typ _.

(* Enrichment *)
Class Enriched (C E : category) `{!HasTerm E, !HasProducts E} := MkEnr {
  enr_hom : obj C → obj C → obj E;
  enr_embed : ∀ a b (f : hom a b), hom (1ₒ) (enr_hom a b);
  enr_project : ∀ a b (f : hom (1ₒ) (enr_hom a b)), hom a b;
  enr_comp : ∀ a b c, hom (enr_hom a b ×ₒ enr_hom b c) (enr_hom a c);
  enr_embed_project :
    ∀ a b (f : hom a b), enr_project _ _ (enr_embed _ _ f) = f;
  enr_project_embed :
    ∀ a b (f : hom (1ₒ) (enr_hom a b)), enr_embed _ _ (enr_project _ _ f) = f;
  enr_comp_comp :
    ∀ a b c (f : hom (1ₒ) (enr_hom a b)) (g : hom (1ₒ) (enr_hom b c)),
    enr_embed _ _ (enr_project _ _ g ∘ (enr_project _ _ f)) =
    (enr_comp _ _ _) ∘ <<f, g>>;
  enr_comp_assoc :
    ∀ a b c d,
      enr_comp a b d ∘ (id (enr_hom a b) ×ₕ enr_comp b c d) ∘
      associator (enr_hom a b) (enr_hom b c) (enr_hom c d)
      =
      (enr_comp a c d ∘ (enr_comp a b c ×ₕ id (enr_hom c d)));
  enr_left_id :
    ∀ a b,
    enr_comp a b b ∘ (id (enr_hom a b) ×ₕ (enr_embed _ _ (id b))) =
    prj1 _;
  enr_right_id :
    ∀ a b,
    enr_comp a a b ∘ ((enr_embed _ _ (id a)) ×ₕ id (enr_hom a b)) =
    prj2 _;
}.
Global Arguments MkEnr {_ _ _ _} _ _ _ _ _ _ _ _ _.
Global Arguments enr_hom {_ _ _ _ _} a b : rename.
Global Arguments enr_embed {_ _ _ _ _ _ _} f.
Global Arguments enr_project {_ _ _ _ _ _ _} f.
Global Arguments enr_comp {_ _ _ _ _} a b c.
Global Arguments enr_embed_project {_ _ _ _ _ _ _} f.
Global Arguments enr_project_embed {_ _ _ _ _ _ _} f.
Global Arguments enr_comp_comp {_ _ _ _ _ _ _ _} f g.
Global Arguments enr_comp_assoc {_ _ _ _ _} _ _ _ _.
Global Arguments enr_left_id {_ _ _ _ _} _ _.
Global Arguments enr_right_id { _ _ _ _ _} _ _.

Notation "⌜ f ⌝" := (enr_embed f).
Notation "⌞ f ⌟" := (enr_project f).

Lemma enr_embed_inj {C E} `{!HasTerm E, !HasProducts E} `{!Enriched C E}
  {a b} (f g : hom a b) : ⌜f⌝ = ⌜g⌝ → f = g.
Proof.
  rewrite -{2}(enr_embed_project f) -{2}(enr_embed_project g).
  intros ?; f_equiv; done.
Qed.
Lemma enr_project_inj {C E} `{!HasTerm E, !HasProducts E} `{!Enriched C E}
  {a b} (f g : hom (1ₒ) (enr_hom a b)) : ⌞f⌟ = ⌞g⌟ → f = g.
Proof.
  rewrite -{2}(enr_project_embed f) -{2}(enr_project_embed g).
  intros ?; f_equiv; done.
Qed.

Lemma enr_comp_assoc'
  {C E} `{!HasTerm E, !HasProducts E} `{!Enriched C E}
  (a b c d : obj C) :
  enr_comp a b d ∘ (id (enr_hom a b) ×ₕ enr_comp b c d)
  = enr_comp a c d ∘ (enr_comp a b c ×ₕ id (enr_hom c d)) ∘
  associator' (enr_hom a b) (enr_hom b c) (enr_hom c d).
Proof.
  apply (compose_along_iso_right
    (isomorphic_sym (product_assoc _ _ _))).
  rewrite /= !comp_assoc associator'_associator right_id.
  rewrite -!comp_assoc enr_comp_assoc //.
Qed.

Definition enr_comp_r {C} `{!HasTerm E, !HasProducts E, !Enriched C E} {a b c}
  (f : hom a b) : hom (enr_hom b c) (enr_hom a c) :=
  enr_comp a b c ∘ (⌜f⌝ ×ₕ id (enr_hom b c)) ∘ term_times_inj (enr_hom b c).

Lemma enr_comp_r_comp {C} `{!HasTerm E, !HasProducts E, !Enriched C E} {a b c}
  (f : hom a b) (g : hom (1ₒ) (enr_hom b c)) :
  enr_comp_r f ∘ g = enr_comp _ _ _ ∘ <<⌜f⌝, g>>.
Proof.
  rewrite /enr_comp_r !comp_assoc.
  f_equiv.
  apply prd_hom_unique.
  - rewrite -!comp_assoc hom_prod_prj1.
    rewrite !comp_assoc -{1}(right_id ⌜f⌝); f_equiv.
    apply term_hom_unique'.
  - rewrite -!comp_assoc hom_prod_prj2 left_id.
    rewrite -prd_hom_commutes2 left_id //.
Qed.

Definition enr_comp_l {C} `{!HasTerm E, !HasProducts E, !Enriched C E} {a b c}
  (g : hom b c) : hom (enr_hom a b) (enr_hom a c) :=
  enr_comp a b c ∘ (id (enr_hom a b) ×ₕ ⌜g⌝) ∘ commutator _ _ ∘ term_times_inj (enr_hom a b).

Lemma enr_comp_l_comp {C} `{!HasTerm E, !HasProducts E, !Enriched C E} {a b c}
  (f : hom (1ₒ) (enr_hom a b)) (g : hom b c) :
  enr_comp_l g ∘ f = enr_comp _ _ _ ∘ <<f, ⌜g⌝>>.
Proof.
  rewrite /enr_comp_l !comp_assoc.
  f_equiv.
  apply prd_hom_unique.
  - rewrite -!comp_assoc hom_prod_prj1 left_id.
    rewrite -{1}(left_id f); f_equiv.
    rewrite -prd_hom_commutes1 -prd_hom_commutes2 //.
  - rewrite -!comp_assoc hom_prod_prj2 !comp_assoc.
    rewrite -{1}(right_id ⌜g⌝); f_equiv.
    apply term_hom_unique'.
Qed.

Class EnrichedFunctor {C D} `{!HasTerm E, !HasProducts E, !Enriched C E, !Enriched D E}
  (F : functor C D) := MkEnrFunc {
  enr_func_h_map : ∀ a b : obj C, hom (enr_hom a b) (enr_hom (F ₒ a) (F ₒ b));
  enr_func_h_map_is_h_map : ∀ (a b : obj C) (f : hom (1ₒ) (enr_hom a b)),
    ⌜F ₕ ⌞f⌟⌝ = enr_func_h_map a b ∘ f;
  enr_func_h_map_comp : ∀ (a b c : obj C),
     enr_func_h_map a c ∘ (enr_comp a b c) =
       (enr_comp (F ₒ a) (F ₒ b) (F ₒ c)) ∘ (enr_func_h_map a b ×ₕ enr_func_h_map b c);
  enr_func_h_map_id : ∀ (a : obj C),
     enr_func_h_map a a ∘ ⌜id a⌝ = ⌜id (F ₒ a)⌝;
}.
Global Arguments MkEnrFunc {_ _ _ _ _ _ _ _} _ _.
Global Arguments enr_func_h_map {_ _ _ _ _ _ _} _ {_} _ _.
Global Arguments enr_func_h_map_is_h_map {_ _ _ _ _ _ _} _ {_} [_ _] _.
Global Arguments enr_func_h_map_comp {_ _ _ _ _ _ _} _ {_} _ _ _.
Global Arguments enr_func_h_map_id {_ _ _ _ _ _ _} _ {_} _.

Global Program Instance EnrichedFunctor_comp {A B C E}
  `{!HasTerm E, !HasProducts E, !Enriched A E, !Enriched B E, !Enriched C E}
  (F : functor A B) (G : functor B C) `{!EnrichedFunctor F} `{!EnrichedFunctor G}
  : EnrichedFunctor (functor_compose F G) :=
  MkEnrFunc (λ a b : obj A, enr_func_h_map G (F ₒ a) (F ₒ b) ∘ enr_func_h_map F a b) _ _ _.
Next Obligation.
  intros ????????? F G ?????; rewrite /=.
  rewrite comp_assoc -!enr_func_h_map_is_h_map enr_embed_project //.
Qed.
Next Obligation.
  intros ????????? F G ?????; rewrite /=.
  rewrite comp_assoc enr_func_h_map_comp.
  rewrite -!comp_assoc enr_func_h_map_comp.
  rewrite !hom_prod_comp -!comp_assoc //.
Qed.
Next Obligation.
  intros ????????? F G ???; rewrite /=.
  rewrite comp_assoc !enr_func_h_map_id //.
Qed.
Fail Next Obligation.

(* Exponentials *)

Record exponential `{!HasTerm C, !HasProducts C} (a b : obj C) := MkExp {
  exp : obj C;
  eval : hom (a ×ₒ exp) b;
  exp_hom d (f : hom (a ×ₒ d) b) : hom d exp;
  exp_hom_commutes d f : f = eval ∘ (id a ×ₕ exp_hom d f);
  exp_hom_unique d f h : f = eval ∘ (id a ×ₕ h) → h = exp_hom d f;
}.

Global Arguments MkExp {_ _ _ _ _} _ _ _ _ _.
Global Arguments exp {_ _ _ _ _} _.
Global Arguments eval {_ _ _ _ _} _.
Global Arguments exp_hom {_ _ _ _ _} _ {_} _.
Global Arguments exp_hom_commutes {_ _ _ _ _} _ {_} _.
Global Arguments exp_hom_unique {_ _ _ _ _} _ {_} _ _ _.

Lemma exp_hom_commutes_gen `{!HasTerm C, !HasProducts C} {a b c d}
  (e : exponential a b) (g : hom d a) f :
  eval e ∘ (g ×ₕ exp_hom e f) = f ∘ (g ×ₕ id c).
Proof. rewrite hom_prod_split -comp_assoc -exp_hom_commutes //. Qed.

Lemma exp_hom_unique' `{!HasTerm C, !HasProducts C} {a b e d}
  (f : hom (a ×ₒ d) b) (h1 h2 : hom d (exp e)) :
  f = eval e ∘ (id a ×ₕ h1) → f = eval e ∘ (id a ×ₕ h2) → h1 = h2.
Proof.
  intros. rewrite (exp_hom_unique _ f h1) // (exp_hom_unique _ f h2) //.
Qed.

Class HasExponentials C `{!HasTerm C, !HasProducts C} :=
  exponential_of (a b : obj C) : exponential a b.
Global Arguments exponential_of {_ _ _ _} _ _, _ {_ _ _} _ _.

Definition obj_exp `{!HasTerm C, !HasProducts C, !HasExponentials C} b a : obj C :=
  exp (exponential_of a b).

Definition hom_exp `{!HasTerm C, !HasProducts C, !HasExponentials C} {a b c d}
  (g : hom b d) (f : hom a c) : hom (obj_exp b c) (obj_exp d a) :=
  exp_hom _ (eval (exponential_of c d) ∘ (f ×ₕ (exp_hom _ (g ∘ eval _)))).

Infix "↑ₒ@{ C }" := (obj_exp (C := C)) (at level 40, left associativity) :
    category_scope.
Infix "↑ₒ" := obj_exp (at level 40, left associativity) :
    category_scope.
Infix "↑ₕ@{ C }" := (hom_exp (C := C)) (at level 40, left associativity) :
    category_scope.
Infix "↑ₕ" := hom_exp (at level 40, left associativity) : category_scope.

Lemma hom_exp_comp `{!HasTerm C, !HasProducts C, !HasExponentials C} {a b c d e f}
  (g1 : hom a c) (g2 : hom c e) (h1 : hom b d) (h2 : hom d f) :
  (h2 ∘ h1) ↑ₕ (g2 ∘ g1) = (h2 ↑ₕ g1) ∘ (h1 ↑ₕ g2).
Proof.
  rewrite /hom_exp.
  symmetry; apply exp_hom_unique.
  rewrite !exp_hom_commutes_gen.
  rewrite  hom_prod_comp_left_id -!comp_assoc -!exp_hom_commutes.
  rewrite !comp_assoc -hom_prod_comp right_id -{2}(left_id g1) hom_prod_comp.
  rewrite hom_prod_id left_id.
  rewrite !exp_hom_commutes_gen.
  rewrite !comp_assoc -hom_prod_comp left_id //.
Qed.
Lemma hom_exp_id `{!HasTerm C, !HasProducts C, !HasExponentials C} {a b} :
  (id a) ↑ₕ (id b) = id (a ↑ₒ b).
Proof.
  symmetry; apply exp_hom_unique.
  rewrite -!exp_hom_commutes hom_prod_id left_id right_id //.
Qed.

Program Definition exp_func `{!HasTerm C, !HasProducts C, !HasExponentials C} :
  functor (cat_prod (C ᵒᵖ) C) C :=
  MkFunc (λ ab, ab.2 ↑ₒ@{C} ab.1) (λ _ _ h, h.2 ↑ₕ@{C} h.1) _ _.
Next Obligation. repeat intros ?; simpl; apply hom_exp_comp. Qed.
Next Obligation. repeat intros ?; simpl; apply hom_exp_id. Qed.
Fail Next Obligation.

(* Exponentials in Typ and PSh. *)

Program Definition typ_exp (A B : Type) : Type := A → B.

Global Program Instance typ_has_exponentials : HasExponentials Typ :=
  λ A B, MkExp (typ_exp A B) (λ af, af.2 af.1) (λ _ f, λ d, λ a, f (a, d))
           _ _.
Next Obligation.
  intros; simpl.
  extensionality x.
  f_equal.
  by destruct x.
Qed.
Next Obligation.
  intros ????? H; simpl.
  extensionality x; simpl.
  extensionality a; simpl.
  by rewrite H.
Qed.
Fail Next Obligation.

Program Definition psh_exp {C} (F G : PreSheaf C) : PreSheaf C :=
  MkFunc (λ c, natural_set ((yoneda (C := C) ₒ c) ×ₒ@{PSh C} F) G)
    (λ _ _ f, λ η, MkNat (λ c, λ g, (η ₙ c) (f ∘ g.1, g.2)) _) _ _.
Next Obligation.
  intros ?????? η ???.
  apply functional_extensionality; intros x; simpl in *.
  rewrite -(psh_naturality η) /= !left_id //.
  destruct x; simpl in *.
  f_equiv.
  rewrite /hom_prod /=.
  rewrite left_id comp_assoc.
  reflexivity.
Qed.
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality x; simpl.
  apply natural_equiv_unpack; intros ?; simpl.
  extensionality y; simpl.
  rewrite !comp_assoc //.
Qed.
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality x; simpl.
  apply natural_equiv_unpack; intros ?; simpl.
  extensionality y; simpl.
  rewrite left_id.
  by destruct y.
Qed.
Fail Next Obligation.

Program Definition psh_eval {C} (F G : PreSheaf C) : natural (F ×ₒ@{PSh C} psh_exp F G) G :=
  MkNat (λ c, λ a, (a.2 ₙ c) (id c, a.1)) _.
Next Obligation.
  intros ??????.
  extensionality c; simpl.
  rewrite -(psh_naturality c.2) //=.
  rewrite /hom_prod //= !left_id right_id.
  done.
Qed.
Fail Next Obligation.

Program Definition psh_exp_hom {C} {F G : PreSheaf C} (H : PreSheaf C)
  (η : natural (F ×ₒ@{PSh C} H) G) : natural H (psh_exp F G) :=
  MkNat (λ c, λ h, MkNat (λ d, λ g, (η ₙ d) (g.2, (H ₕ g.1) h)) _) _.
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality x; simpl.
  rewrite -(psh_naturality η) left_id /= h_map_comp.
  solve_by_eq_rewrite.
Qed.
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality x; simpl.
  apply natural_equiv_unpack; intros y; simpl.
  extensionality z; simpl.
  rewrite h_map_comp.
  solve_by_eq_rewrite.
Qed.
Fail Next Obligation.

Global Program Instance psh_has_exponentials C : HasExponentials (PSh C) :=
  λ F G, MkExp (psh_exp F G) (psh_eval F G) (λ _ η, psh_exp_hom _ η) _ _.
Next Obligation.
  repeat intros ?; simpl in *.
  apply natural_equiv_unpack; intros ?; simpl.
  extensionality x; simpl.
  rewrite h_map_id /=.
  by destruct x.
Qed.
Next Obligation.
  intros ?????? H; simpl in *.
  apply natural_equiv_unpack; intros ?; simpl.
  extensionality x; simpl.
  apply natural_equiv_unpack; intros ?; simpl.
  extensionality y; simpl.
  destruct y; simpl.
  rewrite H //=.
  rewrite (psh_naturality) /= right_id /=.
  reflexivity.
Qed.
Fail Next Obligation.

Definition transpose `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b c : obj C} (f : hom (b ×ₒ a) c) : hom a (c ↑ₒ b) :=
  exp_hom (exponential_of b c) f.

Definition untranspose `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b c : obj C} (f : hom a (c ↑ₒ b)) : hom (b ×ₒ a) c :=
  eval (exponential_of b c) ∘ (id b ×ₕ f).

Lemma transpose_untranspose `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b c : obj C} (f : hom a (c ↑ₒ b)) : transpose (untranspose f) = f.
Proof. rewrite /transpose /untranspose; symmetry; apply exp_hom_unique; done. Qed.
Lemma untranspose_transpose `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b c : obj C} (f : hom (b ×ₒ a) c) : untranspose (transpose f) = f.
Proof. rewrite /transpose /untranspose -exp_hom_commutes //. Qed.

Lemma eval_transpose `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b c d : obj C} (f : hom (b ×ₒ a) c) (g : hom d b) :
  eval (exponential_of b c) ∘ (g ×ₕ transpose f) = f ∘ (g ×ₕ id a).
Proof.
  replace (g ×ₕ transpose f) with ((id b ×ₕ transpose f) ∘ (g ×ₕ id a))
    by rewrite -hom_prod_comp left_id right_id //.
  rewrite -comp_assoc -exp_hom_commutes //.
Qed.

Lemma eval_transpose2 `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b c : obj C} (f : hom (b ×ₒ a) c) :
  eval (exponential_of b c) ∘ (id b ×ₕ transpose f) = f.
Proof. rewrite eval_transpose hom_prod_id right_id //. Qed.

Definition transpose' `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {b c : obj C} (f : hom b c) : hom (1ₒ) (c ↑ₒ b) :=
  transpose (f ∘ term_times_proj _ ∘ commutator _ _).

Definition untranspose' `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {b c : obj C} (f : hom (1ₒ) (c ↑ₒ b)) : hom b c :=
  untranspose f ∘ commutator _ _ ∘ term_times_inj _.

Lemma transpose'_untranspose' `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {b c : obj C} (f : hom (1ₒ) (c ↑ₒ b)) : transpose' (untranspose' f) = f.
Proof.
  rewrite /transpose' /untranspose' /transpose /untranspose.
  rewrite !comp_assoc -(comp_assoc (commutator _ _)) term_times_inj_proj.
  rewrite left_id commutator_involutive right_id.
  symmetry; apply exp_hom_unique; done.
Qed.
Lemma untranspose'_transpose' `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {b c : obj C} (f : hom b c) : untranspose' (transpose' f) = f.
Proof.
  rewrite /transpose' /untranspose' /transpose /untranspose.
  rewrite exp_hom_commutes_gen hom_prod_id right_id.
  rewrite !comp_assoc -(comp_assoc _ _ (commutator _ _)).
  rewrite commutator_involutive left_id term_times_proj_inj right_id //.
Qed.

Definition inner_comp `{!HasTerm C, !HasProducts C, !HasExponentials C}
  (a b c : obj C) : hom (b ↑ₒ a ×ₒ (c ↑ₒ b)) (c ↑ₒ a) :=
  transpose (eval _ ∘ (eval _ ×ₕ id _) ∘ associator' _ _ _).

Lemma eval_inner_comp `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b c z w : obj C} (f : hom z (b ↑ₒ a)) (g : hom w (c ↑ₒ b)) :
  eval (exponential_of a c) ∘ (id a ×ₕ (inner_comp a b c ∘ (f ×ₕ g))) =
  eval (exponential_of b c) ∘ ((eval (exponential_of a b) ∘ (id a ×ₕ f)) ×ₕ g) ∘
  associator' a z w.
Proof.
  rewrite comp_assoc !hom_prod_comp_left_id.
  rewrite -!comp_assoc.
  rewrite eval_transpose2 /=.
  rewrite !comp_assoc.
  rewrite associator'_twist2.
  f_equiv.
  rewrite -!comp_assoc.
  f_equiv.
  rewrite -hom_prod_comp left_id //.
Qed.

Lemma eval_inner_comp' `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b c: obj C} :
  eval (exponential_of a c) ∘ (id a ×ₕ (inner_comp a b c)) =
  eval (exponential_of b c) ∘ ((eval (exponential_of a b)) ×ₕ id (c ↑ₒ b)) ∘
  associator' a (b ↑ₒ a) (c ↑ₒ b).
Proof.
  rewrite -(right_id (inner_comp a b c)) -hom_prod_id.
  rewrite eval_inner_comp hom_prod_id right_id //.
Qed.

Lemma inner_comp_transpose `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b c : obj C} (f : hom (1ₒ) (b ↑ₒ a)) (g : hom (1ₒ) (c ↑ₒ b)) :
  transpose' (untranspose' g ∘ untranspose' f) = inner_comp a b c ∘ << f, g >>.
Proof.
  rewrite -(transpose'_untranspose' f).
  rewrite -(transpose'_untranspose' g).
  rewrite !untranspose'_transpose'.
  generalize (untranspose' f); clear f; intros f.
  generalize (untranspose' g); clear g; intros g.
  rewrite /inner_comp.
  eapply exp_hom_unique'.
  { rewrite /transpose' eval_transpose2; reflexivity. }
  rewrite !hom_prod_comp_left_id -!comp_assoc eval_transpose2.
  rewrite hom_to_prod_to_hom_prod.
  rewrite !comp_assoc hom_prod_comp_left_id.
  rewrite -!comp_assoc !(comp_assoc _ (associator' _ _ _)) associator'_twist2.
  rewrite !comp_assoc -!(comp_assoc (_ ×ₕ _)).
  rewrite -!(comp_assoc (associator' _ _ _)).
  rewrite -hom_prod_comp left_id.
  rewrite exp_hom_commutes_gen.
  rewrite !comp_assoc.
  f_equiv.
  rewrite -exp_hom_commutes -!comp_assoc.
  rewrite commute_term_times_proj !comp_assoc !commute_term_times_proj.
  rewrite hom_to_prod_bangs.
  rewrite associate'_term_times_inj.
  rewrite !hom_prod_comp_right_id -!hom_prod_comp hom_prod_prj1.
  rewrite !comp_assoc; f_equiv.
  rewrite proj_term_times_inj commutator_involutive right_id //.
Qed.

Lemma inner_comp_assoc `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b c d : obj C} :
  inner_comp a b d ∘ (id (b ↑ₒ a) ×ₕ inner_comp b c d) ∘
  associator (b ↑ₒ a) (c ↑ₒ b) (d ↑ₒ c)
  = inner_comp a c d ∘ (inner_comp a b c ×ₕ id (d ↑ₒ c)).
Proof.
  repeat intros ?; simpl.
  eapply exp_hom_unique'; last first.
  { rewrite eval_inner_comp.
    rewrite eval_inner_comp'; reflexivity. }
  rewrite hom_prod_comp_left_id.
  rewrite -!comp_assoc.
  rewrite eval_inner_comp.
  rewrite hom_prod_id right_id.
  rewrite (hom_prod_split _ (inner_comp _ _ _)).
  rewrite -!comp_assoc.
  rewrite eval_inner_comp'.
  rewrite !comp_assoc.
  f_equiv.
  rewrite -hom_prod_id.
  rewrite -(comp_assoc _ _ (associator' _ _ _)).
  rewrite associator'_twist2.
  rewrite -!comp_assoc.
  rewrite -hom_prod_comp left_id.
  apply (compose_along_iso_right
           (iso_prod
              (isomorphic_refl _)
              (product_assoc _ _ _))); simpl.
  rewrite !comp_assoc.
  epose proof (iso_lr (is_iso
               (iso_prod
                  (isomorphic_refl a)
                  (@product_assoc C _ (b ↑ₒ a) (c ↑ₒ b) (d ↑ₒ c))))) as H.
  simpl in H; rewrite H; clear H.
  rewrite right_id.
  rewrite -pentagon'.
  rewrite -!comp_assoc.
  rewrite -hom_prod_comp right_id //.
Qed.

Lemma inner_left_id `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b : obj C} :
  inner_comp a b b ∘ (id (b ↑ₒ a) ×ₕ transpose' (id b))
  = prj1 (product_of (b ↑ₒ a) (1ₒ)).
Proof.
  eapply exp_hom_unique'.
  { rewrite eval_inner_comp hom_prod_id.
    rewrite eval_transpose left_id right_id.
    rewrite commute_term_times_proj hom_prod_prj1.
    rewrite comp_assoc prj1_associator' //. }
  f_equiv.
  eapply prd_hom_unique'.
  { rewrite hom_to_prod_prj1 //. }
  { rewrite hom_to_prod_prj2 //. }
  - rewrite hom_prod_prj1 left_id //.
  - rewrite hom_prod_prj2 //.
Qed.

Lemma inner_right_id `{!HasTerm C, !HasProducts C, !HasExponentials C}
  {a b : obj C} :
  inner_comp a a b ∘ (transpose' (id a) ×ₕ id (b ↑ₒ a))
  = prj2 (product_of (1ₒ) (b ↑ₒ a)).
Proof.
  eapply exp_hom_unique'.
  { rewrite eval_inner_comp.
    rewrite eval_transpose left_id hom_prod_id right_id.
    rewrite commute_term_times_proj //. }
  rewrite !comp_assoc.
  f_equiv.
  eapply prd_hom_unique'.
  { rewrite -comp_assoc hom_prod_prj1.
    rewrite comp_assoc prj1_associator' hom_to_prod_prj1 //. }
  { rewrite -comp_assoc hom_prod_prj2 left_id prj2_associator' //. }
  - rewrite hom_prod_prj1 left_id //.
  - rewrite hom_prod_prj2 //.
Qed.

Class CCC C := MkCCC {
  CCC_HT :: HasTerm C;
  CCC_HP :: HasProducts C;
  CCC_HE :: HasExponentials C
}.

(* Typ and PSh are CCC categories. *)

Global Instance typ_ccc : CCC Typ := MkCCC _ _ _ _.
Global Instance psh_ccc C : CCC (PSh C) := MkCCC _ _ _ _.

(* CCC's are self-enriched. Stated as Definition, not Instnace! *)
Definition self_enriched C `{!CCC C} : Enriched C C :=
  MkEnr
    (λ a b, b ↑ₒ a)
    (λ _ _ f, transpose' f)
    (λ _ _ f, untranspose' f)
    inner_comp
    (@untranspose'_transpose' _ _ _ _)
    (@transpose'_untranspose' _ _ _ _)
    (@inner_comp_transpose _ _ _ _)
    (@inner_comp_assoc _ _ _ _)
    (@inner_left_id _ _ _ _)
    (@inner_right_id _ _ _ _).

(* Right adjoints preserve products. *)

Definition functor_compose_iso_proper {C D E} {F F' : functor C D} {G G' : functor D E}
  (iso : F ≃@{FuncCat C D} F') (iso' : G ≃@{FuncCat D E} G') :
  functor_compose F G ≃@{FuncCat C E} functor_compose F' G' :=
  functor_preserves_iso (functor_compose_func C D E) (prod_of_isos iso iso').

Program Definition adj_compose_swap {A B C D}
  (G : functor A (C ᵒᵖ)) (H : functor B D)
  {F : functor C D} {U : functor D C}
  (adj : adjunction F U) :
  functor_compose (functor_prod G (functor_compose H U)) (Hom C)
  ≃@{FuncCat (cat_prod A B) Typ}
  functor_compose (functor_prod (functor_compose G (opposite_func F)) H) (Hom D) :=
  MkIsoIc
    (MkNat (λ ab, λ f, (backward adj ₙ (G ₒ ab.1, H ₒ ab.2)) f) _)
    (MkNat (λ ab, λ f, (forward adj ₙ) (G ₒ ab.1, H ₒ ab.2) f) _) _.
Next Obligation.
  intros ???? G H F U adj ? ? f.
  extensionality x; simpl in *.
  apply (equal_f (@naturality _ _ _ _ (backward adj) (_, _) (_, _) (G ₕ f.1, H ₕ f.2)) x).
Qed.
Next Obligation.
  intros ???? G H F U adj ? ? f.
  extensionality x; simpl in *.
  apply (equal_f (@naturality _ _ _ _ (forward adj) (_, _) (_, _)
                    (G ₕ f.1, H ₕ f.2)) x).
Qed.
Next Obligation.
  intros ???? G H F U adj; split.
  - apply natural_equiv_unpack.
    intros ab.
    extensionality f; simpl in *.
    pose proof (is_iso adj) as [_ Hfb].
    apply (equal_f (natural_equiv_pack Hfb (G ₒ ab.1, H ₒ ab.2))).
  - apply natural_equiv_unpack.
    intros ab.
    extensionality f; simpl in *.
    pose proof (is_iso adj) as [Hfb _].
    apply (equal_f (natural_equiv_pack Hfb (G ₒ ab.1, H ₒ ab.2))).
Qed.
Fail Next Obligation.

Program Definition prod_in_codom_of_hom_iso {A B C} `{!HasProducts B} `{!HasProducts C}
  (F : functor A (C ᵒᵖ)) (G : functor B C) :
  functor_compose (functor_prod F (functor_compose (functor_prod G G) (prod_func C))) (Hom C)
  ≃@{FuncCat (cat_prod A (cat_prod B B)) Typ}
  functor_compose
    (functor_to_prod
       (functor_compose (functor_prod F (functor_compose (cat_proj1 B B) G)) (Hom C))
       (functor_compose (functor_prod F (functor_compose (cat_proj2 B B) G)) (Hom C)))
    (prod_func Typ) :=
  MkIsoIc
    (MkNat (λ ab, λ f, (prj1 _ ∘ f, prj2 _ ∘ f)) _)
    (MkNat (λ ab, λ f, << f.1, f.2 >>) _) _.
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality x.
  rewrite -!comp_assoc hom_prod_prj1 hom_prod_prj2 //.
  rewrite /hom_prod //=.
  by rewrite -!comp_assoc.
Qed.
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality x.
  rewrite -hom_to_prod_comp hom_to_prod_comp_r //.
Qed.
Next Obligation.
  repeat intros ?; split; repeat intros ?; simpl in *.
  - apply natural_equiv_unpack.
    intros ?; simpl.
    extensionality y.
    apply hom_to_prod_of_prjs.
  - apply natural_equiv_unpack.
    intros ?; simpl.
    extensionality y.
    rewrite hom_to_prod_prj1 hom_to_prod_prj2 //.
    by destruct y.
Qed.
Fail Next Obligation.

Program Definition prod_in_codom_of_hom_iso' {A C} `{!HasProducts C} (F : functor A (C ᵒᵖ)) :
  functor_compose (functor_prod F (prod_func C)) (Hom C)
  ≃@{FuncCat (cat_prod A (cat_prod C C)) Typ}
  functor_compose
    (functor_to_prod
       (functor_compose (functor_prod F (cat_proj1 C C)) (Hom C))
       (functor_compose (functor_prod F (cat_proj2 C C)) (Hom C)))
    (prod_func Typ) :=
  MkIsoIc
    (MkNat (λ ab, λ f, (prj1 _ ∘ f, prj2 _ ∘ f)) _)
    (MkNat (λ ab, λ f, << f.1, f.2 >>) _) _.
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality y.
  rewrite -!comp_assoc hom_prod_prj1 hom_prod_prj2 //.
  rewrite /hom_prod //=.
  rewrite -!comp_assoc.
  reflexivity.
Qed.
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality y.
  rewrite -hom_to_prod_comp hom_to_prod_comp_r //.
Qed.
Next Obligation.
  repeat intros ?; split; repeat intros ?; simpl in *.
  - apply natural_equiv_unpack.
    intros ?; simpl.
    extensionality y.
    apply hom_to_prod_of_prjs.
  - apply natural_equiv_unpack.
    intros ?; simpl.
    extensionality y.
    rewrite hom_to_prod_prj1 hom_to_prod_prj2 //.
    by destruct y.
Qed.
Fail Next Obligation.

Program Definition functor_to_prod_iso_proper {C D E} {F F' : functor C D} {G G' : functor C E}
  (iso : F ≃@{FuncCat C D} F') (iso' : G ≃@{FuncCat C E} G') :
  functor_to_prod F G ≃@{FuncCat C (cat_prod D E)} functor_to_prod F' G' :=
  MkIsoIc
    (MkNat (λ c, (forward iso ₙ c, forward iso' ₙ c)) _)
    (MkNat (λ c, (backward iso ₙ c, backward iso' ₙ c)) _)
    _.
Next Obligation. repeat intros ?; rewrite /= !naturality //. Qed.
Next Obligation. repeat intros ?; rewrite /= !naturality //. Qed.
Next Obligation.
  intros ??????? iso iso'; split; apply natural_equiv_unpack; intros c; simpl in *.
  - destruct (is_iso iso) as [Hfb _]; pose proof (natural_equiv_pack Hfb c) as H;
      simpl in H; rewrite H.
    destruct (is_iso iso') as [Hfb' _]; pose proof (natural_equiv_pack Hfb' c) as H';
      simpl in H'; rewrite H' //.
  - destruct (is_iso iso) as [_ Hbf]; pose proof (natural_equiv_pack Hbf c) as H;
      simpl in H; rewrite H.
    destruct (is_iso iso') as [_ Hbf']; specialize (natural_equiv_pack Hbf' c) as H';
      simpl in H'; rewrite H' //.
Qed.
Fail Next Obligation.

Definition right_adj_preserves_prods
  `{!HasProducts C} `{!HasProducts D} {F : functor C D} {U : functor D C}
  (adj : adjunction F U) :
  functor_compose (prod_func D) U
  ≃@{FuncCat (cat_prod D D) C}
  functor_compose (functor_prod U U) (prod_func C) :=
  fully_faithful_iso (in_right_of_hom C (cat_prod D D))
    (isomorphic_trans
       (adj_compose_swap _ _ adj)
       (isomorphic_trans
          (prod_in_codom_of_hom_iso'
             (functor_compose (id_functor C ᵒᵖ) (opposite_func F)))
          (isomorphic_trans
             (functor_compose_iso_proper
                (functor_to_prod_iso_proper
                   (isomorphic_sym
                      (adj_compose_swap (id_functor C ᵒᵖ) (cat_proj1 D D) adj))
                   (isomorphic_sym
                      (adj_compose_swap (id_functor C ᵒᵖ) (cat_proj2 D D) adj)))
                (isomorphic_refl _))
             (isomorphic_sym (prod_in_codom_of_hom_iso (id_functor C ᵒᵖ) U))))).

Program Definition right_adj_preserves_prods_simpler_forward
  `{!HasProducts C} `{!HasProducts D} {F : functor C D} {U : functor D C}
  (adj : adjunction F U):
  natural
    (functor_compose (prod_func D) U)
    (functor_compose (functor_prod U U) (prod_func C)) :=
  MkNat (λ dd', <<U ₕ (prj1 _), U ₕ (prj2 _) >>) _.
Next Obligation.
  repeat intros ?; simpl in *.
  rewrite -hom_to_prod_comp hom_to_prod_comp_r.
  rewrite -!h_map_comp hom_prod_prj1 hom_prod_prj2 //.
Qed.

Lemma right_adj_preserves_prods_forward
  `{!HasProducts C} `{!HasProducts D} {F : functor C D} {U : functor D C}
  (adj : adjunction F U) :
  forward (right_adj_preserves_prods adj) =
  right_adj_preserves_prods_simpler_forward adj.
Proof.
  apply natural_equiv_unpack.
  intros [d d']; simpl.
  apply prd_hom_unique.
  - rewrite hom_to_prod_prj1 /=.
    pose proof (equal_f (@naturality _ _ _ _ (backward adj)
      (U ₒ (d ×ₒ d'), d ×ₒ d') (U ₒ (d ×ₒ d'), d) (id _, prj1 _)) (id _))
      as Hn.
    rewrite /= h_map_id !right_id in Hn.
    rewrite -Hn.
    pose proof (is_iso adj) as [_ Hbf].
    pose proof (equal_f (natural_equiv_pack Hbf (U ₒ (d ×ₒ d'), d))
                  (U ₕ prj1 (product_of d d'))) as H.
    simpl in H. rewrite H //.
  - rewrite hom_to_prod_prj2 /=.
    pose proof (equal_f (@naturality _ _ _ _ (backward adj)
      (U ₒ (d ×ₒ d'), d ×ₒ d') (U ₒ (d ×ₒ d'), d') (id _, prj2 _)) (id _)) as Hn.
    rewrite /= h_map_id !right_id in Hn; rewrite -Hn.
    pose proof (is_iso adj) as [_ Hbf].
    pose proof (equal_f (natural_equiv_pack Hbf (U ₒ (d ×ₒ d'), d'))
                  (U ₕ prj2 (product_of d d'))) as H.
    simpl in H; rewrite H //.
Qed.

Lemma right_adj_preserves_prods_backward_comm {C D}
  `{!HasProducts C, !HasProducts D} {F : functor C D} {G : functor D C}
  (H : adjunction F G) (a b : obj D)
  : (backward (right_adj_preserves_prods H)) ₙ (b, a) ∘ commutator (G ₒ a) (G ₒ b)
      = G ₕ (commutator a b) ∘ ((backward (right_adj_preserves_prods H))ₙ (a, b)).
Proof.
  rewrite /right_adj_preserves_prods //=.
  rewrite !right_id.
  rewrite -(right_id ((forward H ₙ (G ₒ a ×ₒ (G ₒ b), a ×ₒ b))
        (<< (backward H ₙ (G ₒ a ×ₒ (G ₒ b), a)) (prj1 (product_of (G ₒ a) (G ₒ b))),
          (backward H ₙ (G ₒ a ×ₒ (G ₒ b), b)) (prj2 (product_of (G ₒ a) (G ₒ b))) >>))).
  rewrite -commutator_involutive.
  rewrite -!comp_assoc.
  epose proof (equal_f
                 (@naturality _ _ _ _ (forward H)
                    (G ₒ a ×ₒ (G ₒ b), a ×ₒ b)
                    (G ₒ b ×ₒ (G ₒ a), b ×ₒ a) (commutator _ _, commutator a b))
                    (<< (backward H ₙ (G ₒ a ×ₒ (G ₒ b), a)) (prj1 (product_of (G ₒ a) (G ₒ b))),
                      (backward H ₙ (G ₒ a ×ₒ (G ₒ b), b)) (prj2 (product_of (G ₒ a) (G ₒ b))) >>)) as Hn'.
  simpl in Hn'.
  rewrite -Hn'; clear Hn'.
  rewrite commute_hom_to_prod.
  do 2 f_equiv.
  rewrite hom_to_prod_comp_r.
  f_equiv.
  - epose proof (equal_f
                   (@naturality _ _ _ _ (backward H) (G ₒ a ×ₒ (G ₒ b), b)
                      (G ₒ b ×ₒ (G ₒ a), b)
                      (commutator _ _, id _)) (prj2 (product_of (G ₒ a) (G ₒ b)))) as Hn.
    simpl in Hn.
    rewrite left_id in Hn.
    rewrite <-Hn; clear Hn.
    rewrite h_map_id.
    rewrite left_id.
    rewrite hom_to_prod_prj2.
    reflexivity.
  - epose proof (equal_f
                   (@naturality _ _ _ _ (backward H) (G ₒ a ×ₒ (G ₒ b), a)
                      (G ₒ b ×ₒ (G ₒ a), a)
                      (commutator _ _, id _)) (prj1 (product_of (G ₒ a) (G ₒ b)))) as Hn.
    simpl in Hn.
    rewrite left_id in Hn.
    rewrite <-Hn; clear Hn.
    rewrite h_map_id.
    rewrite left_id.
    rewrite hom_to_prod_prj1.
    reflexivity.
Qed.

Lemma right_adj_preserves_prods_backward_prj1 {C D}
  `{!HasProducts C, !HasProducts D} {F : functor C D} {G : functor D C}
  (H : adjunction F G) (a b : obj D) (x y : obj C) (f : hom x (G ₒ a)) (g : hom y (G ₒ b))
  : ((G ₕ (prj1 _) : hom (G ₒ (a ×ₒ b)) (G ₒ a))
       ∘ ((backward (right_adj_preserves_prods H)) ₙ (a, b) : hom (G ₒ a ×ₒ (G ₒ b)) (G ₒ (a ×ₒ b)))
       ∘ (f ×ₕ g))
      = (f ∘ (prj1 _) : hom (x ×ₒ y) (G ₒ a)).
Proof.
  rewrite /right_adj_preserves_prods //=.
  rewrite !right_id.
  unshelve epose proof
    (equal_f (@naturality _ _ _ _ (forward H)
                (G ₒ a ×ₒ (G ₒ b), a ×ₒ b)
                (G ₒ a ×ₒ (G ₒ b), a)
                (id _, prj1 (product_of a b)))
                (<< (backward H ₙ (G ₒ a ×ₒ (G ₒ b), a)) (prj1 (product_of (G ₒ a) (G ₒ b))),
                  (backward H ₙ (G ₒ a ×ₒ (G ₒ b), b)) (prj2 (product_of (G ₒ a) (G ₒ b))) >>)) as Hn.
  simpl in Hn.
  rewrite right_id in Hn.
  rewrite -Hn; clear Hn.
  rewrite hom_to_prod_prj1.
  rewrite h_map_id right_id.
  pose proof (equal_f (iso_rl (is_iso (natural_iso_proj H (G ₒ a ×ₒ (G ₒ b), a))))
                (prj1 (product_of (G ₒ a) (G ₒ b)))) as HEQ.
  simpl in HEQ; rewrite HEQ; clear HEQ.
  apply hom_prod_prj1.
Qed.

Lemma right_adj_preserves_prods_backward_prj2 {C D}
  `{!HasProducts C, !HasProducts D} {F : functor C D} {G : functor D C}
  (H : adjunction F G) (a b : obj D) (x y : obj C) (f : hom x (G ₒ a)) (g : hom y (G ₒ b))
  : ((G ₕ (prj2 _) : hom (G ₒ (a ×ₒ b)) (G ₒ b))
       ∘ ((backward (right_adj_preserves_prods H)) ₙ (a, b) : hom (G ₒ a ×ₒ (G ₒ b)) (G ₒ (a ×ₒ b)))
       ∘ (f ×ₕ g))
      = (g ∘ (prj2 _) : hom (x ×ₒ y) (G ₒ b)).
Proof.
  rewrite /right_adj_preserves_prods //=.
  rewrite !right_id.
  unshelve epose proof
    (equal_f (@naturality _ _ _ _ (forward H)
                 (G ₒ a ×ₒ (G ₒ b), a ×ₒ b)
                 (G ₒ a ×ₒ (G ₒ b), b)
                 (id _, prj2 (product_of a b)))
                 (<< (backward H ₙ (G ₒ a ×ₒ (G ₒ b), a)) (prj1 (product_of (G ₒ a) (G ₒ b))),
                   (backward H ₙ (G ₒ a ×ₒ (G ₒ b), b)) (prj2 (product_of (G ₒ a) (G ₒ b))) >>)) as Hn.
  simpl in Hn.
  rewrite right_id in Hn.
  rewrite -Hn; clear Hn.
  rewrite hom_to_prod_prj2.
  rewrite h_map_id right_id.
  pose proof (equal_f (iso_rl (is_iso (natural_iso_proj H (G ₒ a ×ₒ (G ₒ b), b))))
                (prj2 (product_of (G ₒ a) (G ₒ b)))) as HEQ.
  simpl in HEQ; rewrite HEQ; clear HEQ.
  apply hom_prod_prj2.
Qed.

Opaque right_adj_preserves_prods.
Program Definition right_adj_preserves_prods_trivial_prod
  `{!HasProducts C, !HasProducts D} {F : functor C D} {G : functor D C}
  (H : adjunction F G) (c : obj D)
  : product (G ₒ c) (G ₒ c) :=
  MkProd (G ₒ (c ×ₒ c)) (G ₕ (prj1 _)) (G ₕ (prj2 _))
    (λ d f g, (backward (right_adj_preserves_prods H)ₙ (c, c) ∘ (<< f, g >>))) _ _ _.
Next Obligation.
  intros ????????.
  intros d p1 p2; simpl.
  rewrite -comp_assoc.
  rewrite -{2}(right_id p1).
  rewrite -(right_id p2).
  rewrite hom_to_prod_comp.
  rewrite -!comp_assoc.
  rewrite right_adj_preserves_prods_backward_prj1.
  rewrite !comp_assoc.
  rewrite hom_to_prod_prj1.
  rewrite right_id.
  reflexivity.
Qed.
Next Obligation.
  intros ????????.
  intros d p1 p2; simpl.
  rewrite -comp_assoc.
  rewrite -(right_id p1).
  rewrite -{2}(right_id p2).
  rewrite hom_to_prod_comp.
  rewrite -!comp_assoc.
  rewrite right_adj_preserves_prods_backward_prj2.
  rewrite !comp_assoc.
  rewrite hom_to_prod_prj2.
  rewrite right_id.
  reflexivity.
Qed.
Next Obligation.
  intros ????????.
  intros ???? HEQ1 HEQ2; simpl.
  rewrite HEQ1 HEQ2.
  rewrite -{1}(left_id h).
  rewrite -(iso_lr (is_iso (natural_iso_proj (right_adj_preserves_prods H) (c, c)))).
  rewrite !comp_assoc.
  f_equiv; last done.
  simpl.
  rewrite right_adj_preserves_prods_forward.
  simpl.
  rewrite hom_to_prod_comp_r.
  reflexivity.
Qed.
Transparent right_adj_preserves_prods.

Opaque right_adj_preserves_prods.
Lemma right_adj_preserves_prods_backward_diag {C D}
  `{!HasProducts C, !HasProducts D} {F : functor C D} {G : functor D C}
  (H : adjunction F G) (c : obj D)
  : G ₕ << id c, id c >>
                   = backward (right_adj_preserves_prods H)ₙ (c, c)
                   ∘ << id (G ₒ c), id (G ₒ c) >>.
Proof.
  eapply (prd_hom_unique' (right_adj_preserves_prods_trivial_prod H c));
    [reflexivity | reflexivity | |]; simpl.
  - rewrite -(left_id (id (G ₒ c))).
    rewrite hom_to_prod_comp.
    rewrite -!comp_assoc.
    rewrite right_adj_preserves_prods_backward_prj1.
    rewrite left_id.
    rewrite -h_map_comp.
    rewrite !hom_to_prod_prj1.
    rewrite h_map_id.
    reflexivity.
  - rewrite -(left_id (id (G ₒ c))).
    rewrite hom_to_prod_comp.
    rewrite -!comp_assoc.
    rewrite right_adj_preserves_prods_backward_prj2.
    rewrite left_id.
    rewrite -h_map_comp.
    rewrite !hom_to_prod_prj2.
    rewrite h_map_id.
    reflexivity.
Qed.
Transparent right_adj_preserves_prods.

Opaque right_adj_preserves_prods.
Lemma right_adj_preserves_prods_backward_prd_hom {C D}
  `{!HasProducts C, !HasProducts D} {F : functor C D} {G : functor D C}
  (H : adjunction F G) (a b c : obj D) (f : hom c a) (g : hom c b)
  : (G ₕ (<< f, g>>))
      = (((backward (right_adj_preserves_prods H) ₙ (a, b)))
           ∘ (<<(G ₕ f), (G ₕ g)>>)).
Proof.
  rewrite -(right_id (G ₕ f)).
  rewrite -(right_id (G ₕ g)).
  rewrite hom_to_prod_comp.
  rewrite -comp_assoc.
  epose proof (@naturality _ _ _ _
                 (backward (right_adj_preserves_prods H))
                 (c, c)
                 (a, b)
                 (f, g)) as Hn.
  simpl in Hn; rewrite Hn; clear Hn.
  rewrite -{1}(right_id f).
  rewrite -{1}(right_id g).
  rewrite hom_to_prod_comp.
  rewrite h_map_comp.
  rewrite !comp_assoc.
  f_equiv.
  apply right_adj_preserves_prods_backward_diag.
Qed.
Transparent right_adj_preserves_prods.

Opaque right_adj_preserves_prods.
Lemma right_adj_preserves_prods_backward_assoc {C D}
  `{!HasProducts C, !HasProducts D} {F : functor C D} {G : functor D C}
  (H : adjunction F G) (a b c : obj D) :
  (((backward (right_adj_preserves_prods H) ₙ (a ×ₒ b, c)))
     ∘ (((backward (right_adj_preserves_prods H) ₙ (a, b))) ×ₕ id (G ₒ _))
     ∘ associator' (G ₒ a) (G ₒ b) (G ₒ c))
    = ((G ₕ (associator' a b c))
         ∘ ((backward (right_adj_preserves_prods H) ₙ (a, b ×ₒ c)))
         ∘ (id (G ₒ a)
              ×ₕ (backward (right_adj_preserves_prods H) ₙ (b, c)))).
Proof.
  unfold associator'.
  rewrite (right_adj_preserves_prods_backward_prd_hom H).
  rewrite !comp_assoc.
  f_equiv; last done.
  rewrite -hom_to_prod_comp.
  rewrite hom_to_prod_comp_r.
  f_equiv.
  - rewrite (right_adj_preserves_prods_backward_prd_hom H).
    rewrite !comp_assoc.
    f_equiv; last done.
    rewrite hom_to_prod_comp_r.
    f_equiv.
    + rewrite -!comp_assoc.
      rewrite right_adj_preserves_prods_backward_prj1.
      rewrite left_id.
      reflexivity.
    + rewrite h_map_comp.
      rewrite (comp_assoc _ (G ₕ prj2 (product_of a (b ×ₒ c)))).
      rewrite -(comp_assoc _ _ (G ₕ prj2 (product_of a (b ×ₒ c)))).
      rewrite right_adj_preserves_prods_backward_prj2.
      simpl.
      rewrite -comp_assoc.
      f_equiv.
      rewrite -(right_id (G ₕ prj1 (product_of b c)
                            ∘ (backward (right_adj_preserves_prods H)ₙ (b, c)))).
      rewrite -hom_prod_id.
      rewrite right_adj_preserves_prods_backward_prj1.
      rewrite left_id.
      reflexivity.
  - rewrite left_id.
    rewrite h_map_comp.
    rewrite (comp_assoc _ (G ₕ prj2 (product_of a (b ×ₒ c)))).
    rewrite -(comp_assoc _ _ (G ₕ prj2 (product_of a (b ×ₒ c)))).
    rewrite right_adj_preserves_prods_backward_prj2.
    simpl.
    rewrite -comp_assoc.
    f_equiv.
    rewrite -(right_id (G ₕ prj2 (product_of b c)
                          ∘ (backward (right_adj_preserves_prods H)ₙ (b, c)))).
    rewrite -hom_prod_id.
    rewrite right_adj_preserves_prods_backward_prj2.
    rewrite left_id.
    reflexivity.
Qed.
Transparent right_adj_preserves_prods.

Global Opaque right_adj_preserves_prods.

(* Right adjoints preserve terminal objects. *)

Program Definition hom_to_term_iso {A B C} `{!HasTerm B} `{!HasTerm C}
  (F : functor A (B ᵒᵖ)) (G : functor A (C ᵒᵖ)) :
  functor_compose (functor_prod F (const_functor (1ₒ))) (Hom B)
  ≃@{FuncCat (cat_prod A SingletonCat) Typ}
  functor_compose (functor_prod G (const_functor (1ₒ))) (Hom C) :=
  MkIsoIc (MkNat (λ _, λ _, !ₕ _) _) (MkNat (λ _, λ _, !ₕ _) _) _.
Next Obligation.
  repeat intros ?.
  extensionality c; simpl.
  apply term_hom_unique'.
Qed.
Next Obligation.
  repeat intros ?.
  extensionality c; simpl.
  apply term_hom_unique'.
Qed.
Next Obligation.
  split; simpl; repeat intros ?.
  - apply natural_equiv_unpack; intros ?; simpl.
    extensionality c; simpl.
    apply term_hom_unique'.
  - apply natural_equiv_unpack; intros ?; simpl.
    extensionality c; simpl.
    apply term_hom_unique'.
Qed.

Definition right_adj_preserves_terminal
  `{!HasTerm C} `{!HasTerm D} {F : functor C D} {U : functor D C}
  (adj : adjunction F U) :
  functor_compose (const_functor (1ₒ)) U ≃@{FuncCat SingletonCat C} const_functor (1ₒ) :=
   fully_faithful_iso (in_right_of_hom C SingletonCat)
     (isomorphic_trans (adj_compose_swap _ _ adj) (hom_to_term_iso _ _)).

Global Opaque right_adj_preserves_terminal.

(* Limits *)
Section Limit.
  Context {J C} (F : functor J C).

  Record cone := MkCone {
    vertex : obj C;
    side : ∀ j, hom vertex (F ₒ j);
    side_commutes : ∀ j j' f, side j' = F ₕ f ∘ side j;
  }.

  Record cone_hom cn cn' := MkConeHom {
    cone_hom_map : hom (vertex cn) (vertex cn');
    cone_hom_commutes : ∀ j, side cn j = side cn' j ∘ cone_hom_map;
  }.
  Arguments MkConeHom {_ _} _ _.
  Arguments cone_hom_map {_ _} _.

  Global Instance cone_hom_eq :
    ∀ cn cn', Equiv (cone_hom cn cn') := λ _ _ ch ch', cone_hom_map ch = cone_hom_map ch'.

  Global Instance cone_hom_eq_equiv {cn cn'} : Equivalence (cone_hom_eq cn cn').
  Proof.
    split;
      rewrite /equiv /cone_hom_eq /=;
        repeat intros ?.
    - reflexivity.
    - by symmetry.
    - by etrans.
  Qed.

  Lemma cone_hom_equiv_unpack {cn cn'} {f g : cone_hom cn cn'}
    (p : cone_hom_eq _ _ f g) : f = g.
  Proof.
    destruct f as [F1 F2];
      destruct g as [G1 G2].
    unfold cone_hom_eq in p.
    simpl in *.
    assert (F1 = G1) as Hf.
    { apply p. }
    destruct Hf.
    assert (F2 = G2) as Hf.
    { apply proof_irrelevance. }
    destruct Hf.
    reflexivity.
  Qed.

  Lemma cone_hom_equiv_pack {cn cn'} {f g : cone_hom cn cn'}
    (p : f = g) : cone_hom_eq _ _ f g.
  Proof. by rewrite p. Qed.

  Program Definition cone_hom_id cn : cone_hom cn cn := MkConeHom (id _) _.
  Solve All Obligations with by repeat intros ?; rewrite /= right_id.
  Fail Next Obligation.

  Program Definition cone_hom_comp {cn cn' cn''} (ch : cone_hom cn cn') (ch' : cone_hom cn' cn'') :
    cone_hom cn cn'' :=
  MkConeHom (cone_hom_map ch' ∘ cone_hom_map ch) _.
  Solve All Obligations with by repeat intros ?; rewrite -comp_assoc -!cone_hom_commutes.
  Fail Next Obligation.

  Lemma cone_hom_comp_assoc :
    ∀ cn1 cn2 cn3 cn4 (ch1 : cone_hom cn1 cn2) (ch2 : cone_hom cn2 cn3) (ch3 : cone_hom cn3 cn4),
      cone_hom_comp ch1 (cone_hom_comp ch2 ch3) = cone_hom_comp (cone_hom_comp ch1 ch2) ch3.
  Proof.
    intros ???? [c1] [c2] [c3].
    apply cone_hom_equiv_unpack; simpl.
    unfold cone_hom_comp; simpl.
    unfold cone_hom_eq; simpl.
    apply comp_assoc.
  Qed.
  Lemma cone_hom_comp_left_id :
    ∀ cn cn' (ch : cone_hom cn cn'), cone_hom_comp ch (cone_hom_id _) = ch.
  Proof.
    intros ?? [].
    apply cone_hom_equiv_unpack; simpl.
    unfold cone_hom_comp; simpl.
    unfold cone_hom_eq; simpl.
    apply left_id.
  Qed.
  Lemma cone_hom_comp_right_id :
    ∀ cn cn' (ch : cone_hom cn cn'), cone_hom_comp (cone_hom_id _) ch = ch.
  Proof.
    intros ?? [].
    apply cone_hom_equiv_unpack; simpl.
    unfold cone_hom_comp; simpl.
    unfold cone_hom_eq; simpl.
    apply right_id.
  Qed.

  Program Definition ConeCat :=
    MkCat cone cone_hom cone_hom_id (@cone_hom_comp) _ _ _.
  Next Obligation. apply cone_hom_comp_assoc. Qed.
  Next Obligation. apply cone_hom_comp_left_id. Qed.
  Next Obligation. apply cone_hom_comp_right_id. Qed.
  Fail Next Obligation.

  Program Definition cone_iso_vertex {cn cn' : cone} (iso : cn ≃@{ConeCat} cn') :
    vertex cn ≃ vertex cn' :=
    MkIsoIc (cone_hom_map (forward iso)) (cone_hom_map (backward iso)) _.
  Next Obligation.
    intros ?? iso; split; destruct (is_iso iso) as [H1 H2].
    - apply (cone_hom_equiv_pack H1).
    - apply (cone_hom_equiv_pack H2).
  Qed.
  Fail Next Obligation.

  Definition is_limiting_cone cn := @is_terminal ConeCat cn.

  Definition limit := terminal ConeCat.

  (* an alternative formulation *)

  Record is_cone c := MkIsCone {
    ic_side : ∀ j, hom c (F ₒ j);
    ic_side_commutes : ∀ j j' f, ic_side j' = F ₕ f ∘ ic_side j;
  }.

  Definition cone_of_is_cone {c} (ic : is_cone c) : cone :=
    MkCone c (ic_side _ ic) (ic_side_commutes _ ic).

  Definition cone_is_cone cn : is_cone (vertex cn) :=
    MkIsCone _ (side cn) (side_commutes cn).

  Record is_limit c := MkIsLimit {
    il_is_cone : is_cone c;
    il_is_limiting_cone : is_limiting_cone (cone_of_is_cone il_is_cone);
  }.

  Definition is_limit_trans
    {a b : obj C} (Heq : a = b) (il : is_limit a) : is_limit b :=
    match Heq in _ = Z return is_limit Z with eq_refl => il end.

  Lemma trans_side_of_is_limit_trans {a b : obj C}
    (Heq : a = b) (il : is_limit a) :
    ∀ j, ic_side _ (il_is_cone _ (is_limit_trans Heq il)) j =
           hom_trans Heq eq_refl (ic_side _ (il_is_cone _ il) j).
  Proof. destruct Heq; done. Qed.

  Lemma bang_of_is_limit_trans
    {a b : obj C} (Heq : a = b) (il : is_limit a) c :
    (cone_hom_map (bang (il_is_limiting_cone _ (is_limit_trans Heq il)) c)) =
      hom_trans eq_refl Heq (cone_hom_map (bang (il_is_limiting_cone _ il) c)).
  Proof. destruct Heq; done. Qed.

  Program Definition limit_is_limit (l : limit) :=
    (MkIsLimit (vertex (term l)) (cone_is_cone (term l)) _).
  Next Obligation.
    intros l.
    pose proof (term_is_terminal l).
    destruct term; done.
  Qed.

  Definition cone_of_is_limit {c} (il : is_limit c) : cone :=
    cone_of_is_cone (il_is_cone _ il).

  Definition limiting_cone_is_limit cn :
    is_limiting_cone cn → is_limit (vertex cn) :=
    match cn as u return is_limiting_cone u → is_limit (vertex u) with
      (MkCone v s c) => MkIsLimit v (MkIsCone _ s c)
    end.

  Lemma ic_side_limiting_cone_is_limit cn ilc c :
    ic_side _ (il_is_cone _ (limiting_cone_is_limit cn ilc)) c = side cn c.
  Proof. rewrite /limiting_cone_is_limit; destruct cn; done. Qed.

  Definition is_limit_limiting_cone {c} (il : is_limit c) :
    is_limiting_cone (cone_of_is_limit il) := il_is_limiting_cone _ il.

  (* useful lemma *)
  Lemma hom_to_limit_unique {c l} (f g : hom C c l) (il : is_limit l) :
    ∀ ic : is_cone c,
      (∀ j, ic_side _ ic j = ic_side _ (il_is_cone _ il) j ∘ f) →
      (∀ j, ic_side _ ic j = ic_side _ (il_is_cone _ il) j ∘ g) →
      f = g.
  Proof.
    intros ic Hf Hg.
    pose (@MkConeHom (cone_of_is_cone ic) (cone_of_is_limit il) f Hf) as fc.
    change f with (cone_hom_map fc).
    pose (@MkConeHom (cone_of_is_cone ic) (cone_of_is_limit il) g Hg) as gc.
    change g with (cone_hom_map gc).
    rewrite (bang_unique (il_is_limiting_cone _ il) fc).
    rewrite (bang_unique (il_is_limiting_cone _ il) gc).
    done.
  Qed.

  (* extending cones *)

  Program Definition extend_cone {c cn} (f : hom C c (vertex cn)) : cone :=
    MkCone c (λ j, side cn j ∘ f) _.
  Next Obligation.
    intros ??????; simpl.
    rewrite -!comp_assoc.
    rewrite -side_commutes //.
  Qed.
  Fail Next Obligation.

  Program Definition extend_cone_hom {c cn} (f : hom C c (vertex cn)) :
    cone_hom (extend_cone f) cn :=
    MkConeHom f _.
  Next Obligation. intros ????; rewrite //. Qed.
  Fail Next Obligation.

  (* A cone with a vertex isomorphic to the limit is also the limit. *)

  Program Definition iso_cones_equi_limit {cn cn' : cone} (iso : cn ≃@{ConeCat} cn')
    (ilc : is_limiting_cone cn) : is_limiting_cone cn' :=
    MkIsTerm cn' (λ cn'', cone_hom_comp (bang ilc cn'') (forward iso)) _.
  Next Obligation.
    intros ?? iso ilc cn'' f; simpl.
    apply (compose_along_iso_left (isomorphic_sym iso)); simpl.
    rewrite -cone_hom_comp_assoc.
    pose proof (iso_lr (is_iso iso)) as Hlr; simpl in Hlr; rewrite Hlr; clear Hlr.
    rewrite cone_hom_comp_left_id.
    apply (bang_unique ilc).
  Qed.

End Limit.
Global Arguments MkCone {_ _ _} _ _ _.
Global Arguments vertex {_ _ _} _.
Global Arguments side {_ _ _} _ _.
Global Arguments side_commutes {_ _ _} _ [_ _] _.
Global Arguments MkConeHom {_ _ _ _ _} _ _.
Global Arguments cone_hom {_ _ _} _ _.
Global Arguments cone_hom_map {_ _ _ _ _} _.
Global Arguments cone_hom_commutes {_ _ _ _ _} _ _.
Global Arguments cone_iso_vertex {_ _ _ _ _} _.
Global Arguments is_limiting_cone {_ _ _} _.
Global Arguments MkIsCone {_ _ _ _} _ _, {_ _ _} _ _ _.
Global Arguments is_cone {_ _} _ _.
Global Arguments ic_side {_ _ _ _} _ _.
Global Arguments ic_side_commutes {_ _ _ _} _ [_ _] _.
Global Arguments cone_of_is_cone {_ _ _ _} _.
Global Arguments cone_is_cone {_ _ _} _.
Global Arguments MkIsLimit {_ _ _ _} _ _, {_ _ _} _ _ _.
Global Arguments is_limit {_ _} _ _.
Global Arguments limit_is_limit {_ _ _} _.
Global Arguments il_is_cone {_ _ _ _} _.
Global Arguments cone_of_is_limit {_ _ _ _} _.
Global Arguments is_limit_limiting_cone {_ _ _ _} _.
Global Arguments limiting_cone_is_limit {_ _ _ _} _.
Global Arguments extend_cone {_ _ _ _} _ _, {_ _ _ _ _} _.
Global Arguments extend_cone_hom {_ _ _ _} _ _, {_ _ _ _ _} _.
Global Arguments is_limit_trans {_ _ _ _ _} _ _.
Global Arguments trans_side_of_is_limit_trans {_ _ _ _ _} _ _ _.
Global Arguments bang_of_is_limit_trans {_ _ _ _ _} _ _ _.
Global Arguments iso_cones_equi_limit {_ _ _ _ _} _ _.

Program Definition trans_cone_along_natural {C J} {F G : functor J C} (η : natural F G)
  (cn : cone F) : cone G :=
  MkCone (vertex cn) (λ j, η ₙ j ∘ side cn j) _.
Next Obligation.
  repeat intros ?; rewrite /= -comp_assoc -naturality comp_assoc -side_commutes //.
Qed.
Fail Next Obligation.

Class Complete C := complete : ∀ J (F : functor J C), limit F.
Arguments complete {_ _ _} _, _ {_ _} _.

(* Completeness proofs *)

Section typ_limit.
  Context {J} (F : functor J Typ).

  Program Definition typ_lim_obj :=
    { p : ∀ j, (F ₒ j) | ∀ j j' (f : hom J j j'), (F ₕ f) (p j) = p j' }.

  Program Definition typ_lim_side : ∀ j, hom Typ typ_lim_obj (F ₒ j) :=
    λ j, λ x, proj1_sig x j.
  Solve All Obligations with intros ? [] [] ?; simpl in *; solve_by_eq_rewrite.
  Fail Next Obligation.

  Program Definition typ_lim_cone : cone F := MkCone typ_lim_obj typ_lim_side _.
  Next Obligation.
    intros.
    rewrite /typ_lim_side /=.
    extensionality x; simpl.
    rewrite -(proj2_sig x _ _ f).
    reflexivity.
  Qed.
  Fail Next Obligation.

  Program Definition typ_fun_to_typ_lim_cone (cn : cone F) :
    (vertex cn) → (vertex typ_lim_cone) :=
    λ x, exist _ (λ j, side cn j x)
      (λ _ _ f, symmetry (equal_f (side_commutes cn f) x)).
  Fail Next Obligation.

  Program Definition cone_hom_to_typ_lim_cone cn : cone_hom cn typ_lim_cone :=
    MkConeHom (typ_fun_to_typ_lim_cone cn) _.
  Next Obligation.
    intros; simpl.
    extensionality x.
    reflexivity.
  Qed.
  Fail Next Obligation.

  Program Definition typ_lim_cone_is_limiting_cone : is_limiting_cone typ_lim_cone :=
    MkIsTerm typ_lim_cone cone_hom_to_typ_lim_cone _.
  Next Obligation.
  Proof.
    intros cn [chm chmc].
    apply cone_hom_equiv_unpack; rewrite /cone_hom_eq //=.
    extensionality x.
    unfold typ_lim_cone in chmc.
    simpl in *.
    apply sig_eq_pi.
    - intros; simpl.
      intros ??.
      apply proof_irrelevance.
    - simpl.
      extensionality j.
      rewrite chmc.
      reflexivity.
  Qed.
  Fail Next Obligation.

End typ_limit.

Global Program Instance typ_complete : Complete Typ :=
  λ _ F, MkTerm (typ_lim_cone F) (typ_lim_cone_is_limiting_cone F).

Section typ_colimit.
  Context {J} (F : functor J (Typ ᵒᵖ)).

  Definition typ_colim_obj_carrier : Type := sigT (F ₒ).

  Inductive typ_colim_obj_rel : relation typ_colim_obj_carrier
    :=
  | typ_colim_obj_rel_refl {x} : typ_colim_obj_rel x x
  | typ_colim_obj_rel_step {x y a b : obj J}
      {X : F ₒ x} {Y : F ₒ y} {A : F ₒ a} {B : F ₒ b}
      (f : hom a x) (g : hom a b)
      (H : (F ₕ f) X = A) (G : (F ₕ g) B = A)
    :
    typ_colim_obj_rel (existT b B) (existT y Y)
    → typ_colim_obj_rel (existT x X) (existT y Y).

  Local Instance typ_colim_obj_rel_reflexive : Reflexive typ_colim_obj_rel.
  Proof. intros ?; constructor. Qed.

  Lemma typ_colim_obj_rel_gen {j j' : obj J}
    {X : F ₒ j} {Y : F ₒ j'}
    (ϕ : hom (J ᵒᵖ) j j') (H : (F ₕ ϕ) X = Y)
    : typ_colim_obj_rel (existT j X) (existT j' Y).
  Proof.
    apply (typ_colim_obj_rel_step (B := Y) ϕ (id _) H).
    - rewrite h_map_id //=.
    - reflexivity.
  Qed.

  Local Instance typ_colim_obj_rel_transitive : Transitive typ_colim_obj_rel.
  Proof.
    intros ???.
    intros H.
    revert z.
    induction H as [| ???? ???? f g H G L IHL]; first done.
    intros [z Z] K.
    apply (typ_colim_obj_rel_step f g H G), IHL, K.
  Qed.

  Local Instance typ_colim_obj_rel_symmetric : Symmetric typ_colim_obj_rel.
  Proof.
    intros ?? H.
    induction H as [| ???? ???? f g H G L IHL]; first done.
    etransitivity; first apply IHL.
    eapply (typ_colim_obj_rel_step g (id _) G).
    - rewrite h_map_id /=.
      reflexivity.
    - unshelve eapply (typ_colim_obj_rel_step (id _) f _ H).
      + rewrite h_map_id //=.
      + reflexivity.
  Qed.

  Local Instance typ_colim_obj_rel_equiv : Equivalence typ_colim_obj_rel.
  Proof.
    split.
    - apply typ_colim_obj_rel_reflexive.
    - apply typ_colim_obj_rel_symmetric.
    - apply typ_colim_obj_rel_transitive.
  Qed.

  Program Definition typ_colim_obj : Type :=
      (quotient typ_colim_obj_rel).

  Program Definition typ_colim_side : ∀ j, hom Typ (F ₒ j) typ_colim_obj :=
  λ j, λ x, quotient_el (existT j x).

  Program Definition typ_colim_cone : cone F :=
    MkCone typ_colim_obj typ_colim_side _.
  Next Obligation.
    intros ?? f.
    extensionality t.
    rewrite /typ_lim_side /=.
    apply eq_quotient.
    eapply typ_colim_obj_rel_gen.
    reflexivity.
  Qed.
  Fail Next Obligation.

  Program Definition typ_fun_from_typ_colim_cone (cn : cone F) :
    (vertex typ_colim_cone) → (vertex cn)
    := λ x, (side cn (projT1 (unquotient x)) (projT2 (unquotient x))).

  Lemma typ_colim_rel_side_eq (cn : cone F)
  (x y : typ_colim_obj_carrier)
  (H : typ_colim_obj_rel x y)
    : side cn (projT1 x) (projT2 x) = side cn (projT1 y) (projT2 y).
  Proof.
    induction H as [| ???? ???? f g H G L IHL]; first reflexivity; simpl in *.
    rewrite -IHL.
    rewrite (side_commutes cn f).
    rewrite (side_commutes cn g).
    rewrite /= H G //=.
  Qed.

  Program Definition cone_hom_from_typ_colim_cone (cn : cone F) :
    cone_hom cn typ_colim_cone :=
    MkConeHom (typ_fun_from_typ_colim_cone cn) _.
  Next Obligation.
    intros; simpl.
    extensionality x; simpl.
    rewrite /typ_fun_from_typ_colim_cone.
    unfold unquotient.
    destruct constructive_indefinite_description as [? H]; simpl.
    apply quotient_inj in H.
    apply typ_colim_rel_side_eq with cn _ _ in H; simpl in H.
    by rewrite H.
  Qed.

  Program Definition typ_colim_cone_is_colimiting_cone :
    is_limiting_cone typ_colim_cone :=
    MkIsTerm typ_colim_cone cone_hom_from_typ_colim_cone _.
  Next Obligation.
    intros cn [chm chmc].
    apply cone_hom_equiv_unpack; unfold cone_hom_eq; simpl.
    extensionality x.
    pose proof (equal_f (chmc (projT1 (unquotient x)))
                  (projT2 (unquotient x))) as H; clear chmc.
    unfold typ_fun_from_typ_colim_cone.
    simpl in *; rewrite H; clear H.
    f_equiv.
    unfold unquotient.
    destruct constructive_indefinite_description as [? ->]; simpl.
    unfold typ_colim_side.
    rewrite -sigT_eta.
    reflexivity.
  Qed.
  Fail Next Obligation.

End typ_colimit.

Global Program Instance typ_cocomplete : Complete (Typ ᵒᵖ) :=
  λ _ F, MkTerm (typ_colim_cone F) (typ_colim_cone_is_colimiting_cone F).

Section func_cat_limit.
  Context {C D} `{!Complete D} {J} (F : functor J (FuncCat C D)).

  Ltac rewrite_cone_hom_commutes_back :=
    match goal with
      |- context [side _ ?j ∘ cone_hom_map ?c] => rewrite -(cone_hom_commutes c j)
    | |- context [ic_side _ ?j ∘ cone_hom_map ?c] => rewrite -(cone_hom_commutes c j)
    end.

  Program Definition pointwise_func : ∀ c : obj C, functor J D :=
    λ c, MkFunc (λ j, (F ₒ j) ₒ c) (λ _ _ f, F ₕ f ₙ c) _ _.
  Solve All Obligations with
    repeat first [intros ->|intros ?]; rewrite /= ?h_map_comp ?h_map_id //=.
  Fail Next Obligation.

  Definition func_limit_func_o_map (c : obj C) : obj D :=
    vertex (term (complete (pointwise_func c))).

  Program Definition cone_on_pointwise_func {c c' : obj C} (f : hom c c') :
    cone (pointwise_func c') :=
    MkCone (func_limit_func_o_map c)
      (λ j, ((F ₒ j)ₕ f) ∘ (side (term (complete (pointwise_func c))) j)) _.
  Next Obligation.
    repeat intros ?; rewrite /= -comp_assoc naturality comp_assoc -side_commutes //.
  Qed.
  Fail Next Obligation.

  Definition func_limit_func_h_map {c c' : obj C} (f : hom c c') :
    hom (func_limit_func_o_map c) (func_limit_func_o_map c') :=
    (cone_hom_map
       (bang (term_is_terminal (complete (pointwise_func c'))) (cone_on_pointwise_func f))).

  Program Definition func_limit_func : functor C D :=
    MkFunc func_limit_func_o_map (@func_limit_func_h_map) _ _.
  Next Obligation.
    intros a b c f g; rewrite /func_limit_func_h_map.
    apply (hom_to_limit_unique
             _ _ _ (limit_is_limit (complete (pointwise_func c)))
             (cone_is_cone (cone_on_pointwise_func (g ∘ f)))).
    - intros ?; rewrite_cone_hom_commutes_back; done.
    - intros ?; rewrite -comp_assoc; rewrite_cone_hom_commutes_back; simpl.
      rewrite comp_assoc.
      rewrite_cone_hom_commutes_back.
      rewrite h_map_comp comp_assoc //.
  Qed.
  Next Obligation.
    intros c; rewrite /func_limit_func_h_map.
    apply (hom_to_limit_unique
             _ _ _ (limit_is_limit (complete (pointwise_func c)))
             (cone_is_cone (cone_on_pointwise_func (id c)))).
    - intros ?; rewrite -cone_hom_commutes //.
    - intros ?; rewrite /= h_map_id left_id right_id //.
  Qed.
  Fail Next Obligation.

  Program Definition func_limit_cone_side (j : obj J) : natural func_limit_func (F ₒ j) :=
    MkNat (λ c, side (term (complete (pointwise_func c))) j) _.
  Next Obligation.
    intros j a b f; rewrite /= /func_limit_func_h_map /=.
    rewrite -(cone_hom_commutes (bang (term_is_terminal (complete _)) (cone_on_pointwise_func f))).
    done.
  Qed.
  Fail Next Obligation.

  Program Definition func_limit_cone : cone F :=
    MkCone func_limit_func func_limit_cone_side _.
  Next Obligation.
    intros ???.
    apply natural_equiv_unpack.
    intros ?; rewrite /= -side_commutes //.
  Qed.
  Fail Next Obligation.

  Program Definition func_cone_to_cone (cn : cone F) c : cone (pointwise_func c) :=
    MkCone (vertex cn ₒ c) (λ j, (side cn j) ₙ c) _.
  Next Obligation.
    intros ?????; simpl.
    rewrite (side_commutes cn f).
    reflexivity.
  Qed.
  Fail Next Obligation.

  Program Definition func_cone_hom_pointwise {cn cn' : cone F}
    c (h : cone_hom cn cn') :
    cone_hom (func_cone_to_cone cn c) (func_cone_to_cone cn' c) :=
    MkConeHom (cone_hom_map h ₙ c) _.
  Next Obligation.
    intros ?????; simpl.
    rewrite (cone_hom_commutes h).
    reflexivity.
  Qed.
  Fail Next Obligation.

  Program Definition func_cone_to_limit_pointwise {cn : cone F}
    (h : cone_hom cn func_limit_cone) c :
    cone_hom (func_cone_to_cone cn c) (term (complete (pointwise_func c))) :=
    MkConeHom (cone_hom_map h ₙ c) _.
  Next Obligation.
    repeat intros ?; simpl.
    rewrite (cone_hom_commutes h).
    reflexivity.
  Qed.
  Fail Next Obligation.

  Program Definition cone_hom_to_func_limit_cone (cn : cone F) : cone_hom cn func_limit_cone :=
    MkConeHom
      (MkNat (λ c, cone_hom_map (bang (term_is_terminal (complete (pointwise_func c)))
        (func_cone_to_cone cn c))) _)
      _.
  Next Obligation.
    intros cn a b f; simpl in *.
    rewrite /func_limit_func_h_map /=.
    apply (hom_to_limit_unique
             _ _ _ (limit_is_limit (complete (pointwise_func b)))
             (cone_is_cone (@extend_cone _ _ _ _ (func_cone_to_cone cn b) (vertex cn ₕ f)))).
    - intros ?; rewrite /=.
      rewrite -comp_assoc.
      rewrite_cone_hom_commutes_back.
      rewrite naturality //.
    - intros ?; rewrite /= -comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite /= comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite naturality //.
  Qed.
  Next Obligation.
    intros cn j.
    apply natural_equiv_unpack; intros c; simpl.
    rewrite_cone_hom_commutes_back; done.
  Qed.
  Fail Next Obligation.

  Program Definition func_limit_cone_is_limiting_cone : is_limiting_cone func_limit_cone :=
    MkIsTerm func_limit_cone cone_hom_to_func_limit_cone _.
  Next Obligation.
    intros cn f.
    apply cone_hom_equiv_unpack.
    unfold cone_hom_eq.
    apply natural_equiv_unpack; intros c; simpl.
    pose proof (bang_unique (term_is_terminal (complete (pointwise_func c)))
                  (func_cone_to_limit_pointwise f c)) as H.
    apply cone_hom_equiv_pack in H.
    apply H.
  Qed.
  Fail Next Obligation.

  Definition func_limit : limit F := MkTerm _ func_limit_cone_is_limiting_cone.

  Program Definition func_cone_to_cone_preserves_isos
    {cn cn' : cone F} (iso : cn ≃@{ConeCat F} cn') c :
    func_cone_to_cone cn c ≃@{ConeCat (pointwise_func c)} func_cone_to_cone cn' c :=
    MkIsoIc ((func_cone_hom_pointwise c (forward iso))) (func_cone_hom_pointwise c (backward iso)) _.
  Next Obligation.
    intros; split; simpl.
    - pose proof (iso_lr (is_iso iso)).
      match goal with
      Heq : ?A = ?B |- _ =>
        assert (func_cone_hom_pointwise c A = func_cone_hom_pointwise c B)
        by rewrite Heq //
      end.
      apply cone_hom_equiv_unpack.
      apply cone_hom_equiv_pack in H.
      apply natural_equiv_pack in H.
      apply H.
    - pose proof (iso_rl (is_iso iso)).
      match goal with
      Heq : ?A = ?B |- _ =>
        assert (func_cone_hom_pointwise c A = func_cone_hom_pointwise c B)
        by rewrite Heq //
      end.
      apply cone_hom_equiv_unpack.
      apply cone_hom_equiv_pack in H.
      apply natural_equiv_pack in H.
      apply H.
  Qed.

  Program Definition func_cone_to_cone_func_limit_cone_iso c :
    (func_cone_to_cone func_limit_cone c) ≃@{ConeCat (pointwise_func c)}
    (term (complete (pointwise_func c))) :=
    MkIsoIc (MkConeHom (id _) _) (MkConeHom (id _) _) _.
  Next Obligation. repeat intros; rewrite right_id //. Qed.
  Next Obligation. repeat intros; rewrite right_id //. Qed.
  Next Obligation.
    intros c; split; apply cone_hom_equiv_unpack; unfold cone_hom_eq; simpl;
      by rewrite right_id.
  Qed.

  Definition func_cat_limits_pointwise {L : functor C D} (il : is_limit F L) c :
    is_limit (pointwise_func c) (L ₒ c) :=
    MkIsLimit (cone_is_cone (func_cone_to_cone (cone_of_is_cone (il_is_cone il)) c))
      (iso_cones_equi_limit
         (func_cone_to_cone_preserves_isos
            (is_term_unique func_limit_cone_is_limiting_cone (il_is_limiting_cone F L il)) c)
         (iso_cones_equi_limit (isomorphic_sym (func_cone_to_cone_func_limit_cone_iso c))
            (term_is_terminal (complete (pointwise_func c))))).

  (* This is a poor man's enriched cone. *)
  Record coherent_partial_cone c := MkCohParCone {
    coh_par_cone : cone (pointwise_func c);
    coh_par_cone_down c' (f : hom c c') : cone (pointwise_func c');
    coh_par_cone_hom c' (f : hom c c') :
      hom (vertex coh_par_cone) (vertex (coh_par_cone_down c' f));
    coh_par_cone_hom_natural c' (f : hom c c') j :
      side (coh_par_cone_down _ f) j ∘ coh_par_cone_hom _ f =
      (F ₒ j)ₕ f ∘ side coh_par_cone j
  }.
  Arguments coh_par_cone {_} _.
  Arguments coh_par_cone_down {_} _ {_} _.
  Arguments coh_par_cone_hom {_} _ {_} _.
  Arguments coh_par_cone_hom_natural {_} _ {_} _ _.

  Lemma func_cat_limits_pointwise_natural
    {L : functor C D} (il : is_limit F L) {c} (cn : coherent_partial_cone c)
    {c' : obj C} (f : hom c c') :
    cone_hom_map
      (bang (il_is_limiting_cone _ _ (func_cat_limits_pointwise il c'))
         (coh_par_cone_down cn f)) ∘ (coh_par_cone_hom cn f) =
    (L ₕ f) ∘
    cone_hom_map (bang (il_is_limiting_cone _ _
      (func_cat_limits_pointwise il c)) (coh_par_cone cn)).
  Proof.
    apply (hom_to_limit_unique
             _ _ _ (func_cat_limits_pointwise il c')
             (cone_is_cone (extend_cone (coh_par_cone_down cn f) (coh_par_cone_hom cn f)))).
    - intros ?; simpl in *.
      rewrite left_id -!comp_assoc.
      pose proof (cone_hom_commutes (bang (il_is_limiting_cone F L il) func_limit_cone) j) as Hchc; rewrite /= in Hchc.
      apply natural_equiv_pack in Hchc.
      unfold natural_eq in Hchc.
      specialize (Hchc c'); simpl in Hchc.
      rewrite -Hchc; clear Hchc.
      rewrite_cone_hom_commutes_back; done.
    - intros ?.
      rewrite /= left_id.
      rewrite -!(comp_assoc _ _ (L ₕ _)).
      epose proof (naturality (cone_hom_map (bang (il_is_limiting_cone F L il) func_limit_cone)) f)
        as Hn; rewrite /= in Hn; rewrite -Hn; clear Hn.
      rewrite -!comp_assoc.
      epose proof (natural_equiv_pack (cone_hom_commutes (bang (il_is_limiting_cone F L il) func_limit_cone) j) c')
        as Hchc; rewrite /= in Hchc; rewrite -Hchc /=; clear Hchc.
      rewrite /func_limit_func_h_map.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      apply coh_par_cone_hom_natural.
  Qed.

End func_cat_limit.

Definition func_cat_complete {C D} `{!Complete D} : Complete (FuncCat C D) :=
  λ J F, func_limit F.

Global Program Instance psh_complete C : Complete (PSh C) := func_cat_complete.

Section func_cat_colimit.
  Context {C D} `{!Complete (D ᵒᵖ)} {J} (F : functor J ((FuncCat C D) ᵒᵖ)).

  Ltac rewrite_cocone_hom_commutes_back :=
    match goal with
      |- context [cone_hom_map ?c ∘ side _ ?j] =>
        let H := fresh "H" in
        pose proof (cone_hom_commutes c j)
          as H; simpl in H; rewrite -H; clear H
    | |- context [cone_hom_map ?c ∘ ic_side _ ?j] =>
        let H := fresh "H" in
        pose proof (cone_hom_commutes c j)
          as H; simpl in H; rewrite H; clear H
    end.

  Program Definition pointwise_func_colim : ∀ c : obj C, functor J (D ᵒᵖ) :=
    λ c, MkFunc (λ j, (F ₒ j) ₒ c) (λ _ _ f, F ₕ f ₙ c) _ _.
  Solve All Obligations with
    repeat first [intros ->|intros ?]; rewrite /= ?h_map_comp ?h_map_id //=.
  Fail Next Obligation.

  Definition func_colimit_func_o_map (c : obj C) : obj (D ᵒᵖ) :=
    vertex (term (complete (pointwise_func_colim c))).

  Program Definition cocone_on_pointwise_func_colim
    {c c' : obj (C ᵒᵖ)} (f : hom c c') :
    cone (pointwise_func_colim c') :=
    MkCone (func_colimit_func_o_map c)
      (λ j, ((F ₒ j)ₕ f) ∘ (side (term (complete (pointwise_func_colim c))) j)) _.
  Next Obligation.
    intros ????? g; rewrite /=. rewrite comp_assoc -naturality -comp_assoc.
    rewrite (side_commutes (term (complete (pointwise_func_colim c))) g).
    reflexivity.
  Qed.
  Fail Next Obligation.

  Definition func_colimit_func_h_map {c c' : obj (C ᵒᵖ)} (f : hom c c') :
    hom (func_colimit_func_o_map c) (func_colimit_func_o_map c') :=
    (cone_hom_map
       (bang (term_is_terminal (complete (pointwise_func_colim c')))
          (cocone_on_pointwise_func_colim f))).

  Program Definition func_colimit_func : obj ((FuncCat C D) ᵒᵖ) :=
    MkFunc func_colimit_func_o_map (λ c' c, @func_colimit_func_h_map c c') _ _.
  Next Obligation.
    intros a b c f g; rewrite /func_colimit_func_h_map.
    apply (hom_to_limit_unique
             _ _ _ (limit_is_limit (complete (pointwise_func_colim a)))
             (cone_is_cone (cocone_on_pointwise_func_colim (g ∘ f)))).
    - intros ?; simpl; rewrite_cocone_hom_commutes_back; done.
    - intros ?; rewrite -comp_assoc; simpl; rewrite_cocone_hom_commutes_back; simpl.
      rewrite -comp_assoc.
      rewrite_cocone_hom_commutes_back.
      rewrite h_map_comp comp_assoc //.
  Qed.
  Next Obligation.
    intros c; rewrite /func_colimit_func_h_map.
    apply (hom_to_limit_unique
             _ _ _ (limit_is_limit (complete (pointwise_func_colim c)))
             (cone_is_cone (cocone_on_pointwise_func_colim (id c)))).
    - intros ?; rewrite -cone_hom_commutes //.
    - intros ?; rewrite /= h_map_id left_id right_id //.
  Qed.
  Fail Next Obligation.

  Program Definition func_colimit_cocone_side (j : obj J)
    : natural (F ₒ j) func_colimit_func :=
    MkNat (λ c, side (term (complete (pointwise_func_colim c))) j) _.
  Next Obligation.
    intros j a b f; rewrite /= /func_colimit_func_h_map /=.
    rewrite_cocone_hom_commutes_back.
    reflexivity.
  Qed.
  Fail Next Obligation.

  Program Definition func_colimit_cocone : cone F :=
    MkCone func_colimit_func func_colimit_cocone_side _.
  Next Obligation.
    intros ???.
    apply natural_equiv_unpack; intros ?.
    rewrite /= (side_commutes _ f) // //=.
  Qed.
  Fail Next Obligation.

  Program Definition func_cocone_to_cocone (cn : cone F) c : cone (pointwise_func_colim c) :=
    MkCone (vertex cn ₒ c) (λ j, (side cn j) ₙ c) _.
  Next Obligation.
    repeat intros ?; simpl.
    apply (natural_equiv_pack (side_commutes cn f) c).
  Qed.
  Fail Next Obligation.

  Program Definition func_cocone_hom_pointwise {cn cn' : cone F}
    c (h : cone_hom cn cn') :
    cone_hom (func_cocone_to_cocone cn c) (func_cocone_to_cocone cn' c) :=
    MkConeHom (cone_hom_map h ₙ c) _.
  Next Obligation.
    repeat intros ?; simpl.
    apply (natural_equiv_pack (cone_hom_commutes h j) c).
  Qed.
  Fail Next Obligation.

  Program Definition func_cocone_to_colimit_pointwise {cn : cone F}
    (h : cone_hom cn func_colimit_cocone) c :
    cone_hom (func_cocone_to_cocone cn c) (term (complete (pointwise_func_colim c))) :=
    MkConeHom (cone_hom_map h ₙ c) _.
  Next Obligation.
    repeat intros ?; simpl.
    apply (natural_equiv_pack (cone_hom_commutes h j) c).
  Qed.
  Fail Next Obligation.

  Program Definition cocone_hom_to_func_colimit_cocone (cn : cone F) : cone_hom cn func_colimit_cocone :=
    MkConeHom
      (MkNat (λ c, cone_hom_map (bang (term_is_terminal (complete (pointwise_func_colim c)))
        (func_cocone_to_cocone cn c))) _)
      _.
  Next Obligation.
    intros cn a b f; simpl in *.
    rewrite /func_limit_func_h_map /=.
    apply (hom_to_limit_unique
             _ _ _ (limit_is_limit (complete (pointwise_func_colim a)))
             (cone_is_cone (@extend_cone _ _ _ _ (func_cocone_to_cocone cn a) (vertex cn ₕ f)))).
    - intros ?; rewrite /=.
      rewrite comp_assoc.
      simpl.
      epose proof (@cone_hom_commutes _ _ _
                     _
                     (term (complete (pointwise_func_colim a)))
                     (bang (term_is_terminal (complete (pointwise_func_colim a))) (cocone_on_pointwise_func_colim f))) as H.
      simpl in H.
      rewrite -H.
      rewrite -naturality //.
      rewrite -comp_assoc.
      rewrite_cocone_hom_commutes_back.
      reflexivity.
    - intros ?; rewrite /= comp_assoc.
      rewrite_cocone_hom_commutes_back.
      reflexivity.
  Qed.
  Next Obligation.
    intros cn j; simpl.
    apply natural_equiv_unpack; intros c; simpl.
    rewrite_cocone_hom_commutes_back.
    reflexivity.
  Qed.
  Fail Next Obligation.

  Program Definition func_colimit_cocone_is_colimiting_cocone : is_limiting_cone func_colimit_cocone :=
    MkIsTerm func_colimit_cocone cocone_hom_to_func_colimit_cocone _.
  Next Obligation.
    intros cn f.
    apply cone_hom_equiv_unpack.
    apply natural_equiv_unpack; intros c; simpl.
    rewrite -(bang_unique (term_is_terminal (complete (pointwise_func_colim c)))
                (func_cocone_to_colimit_pointwise f c)).
    done.
  Qed.
  Fail Next Obligation.

  Definition func_colimit : limit F
    := MkTerm _ func_colimit_cocone_is_colimiting_cocone.

  Program Definition func_cocone_to_cocone_preserves_isos
    {cn cn' : cone F} (iso : cn ≃@{ConeCat F} cn') c :
    func_cocone_to_cocone cn c
      ≃@{ConeCat (pointwise_func_colim c)} func_cocone_to_cocone cn' c :=
    MkIsoIc ((func_cocone_hom_pointwise c (forward iso)))
      (func_cocone_hom_pointwise c (backward iso)) _.
  Next Obligation.
    intros; split; simpl.
    - pose proof (iso_lr (is_iso iso)).
      match goal with
      Heq : ?A = ?B |- _ =>
        assert (func_cocone_hom_pointwise c A = func_cocone_hom_pointwise c B)
        by rewrite Heq //
      end.
      apply cone_hom_equiv_unpack.
      apply cone_hom_equiv_pack in H.
      apply natural_equiv_pack in H.
      apply H.
    - pose proof (iso_rl (is_iso iso)).
      match goal with
      Heq : ?A = ?B |- _ =>
        assert (func_cocone_hom_pointwise c A = func_cocone_hom_pointwise c B)
        by rewrite Heq //
      end.
      apply cone_hom_equiv_unpack.
      apply cone_hom_equiv_pack in H.
      apply natural_equiv_pack in H.
      apply H.
  Qed.

  Program Definition func_cocone_to_cocone_func_colimit_cocone_iso c :
    (func_cocone_to_cocone func_colimit_cocone c)
      ≃@{ConeCat (pointwise_func_colim c)}
    (term (complete (pointwise_func_colim c))) :=
    MkIsoIc (MkConeHom (id _) _) (MkConeHom (id _) _) _.
  Next Obligation. repeat intros; rewrite right_id //. Qed.
  Next Obligation. repeat intros; rewrite right_id //. Qed.
  Next Obligation.
    repeat intros; split; apply cone_hom_equiv_unpack; unfold cone_hom_eq; simpl;
      rewrite right_id //.
  Qed.

  Definition func_cat_colimits_pointwise {L : functor C D} (il : is_limit F L) c :
    is_limit (pointwise_func_colim c) (L ₒ c) :=
    MkIsLimit (cone_is_cone (func_cocone_to_cocone (cone_of_is_cone (il_is_cone il)) c))
      (iso_cones_equi_limit
         (func_cocone_to_cocone_preserves_isos
            (is_term_unique func_colimit_cocone_is_colimiting_cocone (il_is_limiting_cone F L il)) c)
         (iso_cones_equi_limit (isomorphic_sym (func_cocone_to_cocone_func_colimit_cocone_iso c))
            (term_is_terminal (complete (pointwise_func_colim c))))).

  Record coherent_partial_cocone c :=
    MkCohParCocone {
        coh_par_cocone : cone (pointwise_func_colim c);
        coh_par_cocone_down c' (f : hom c c') : cone (pointwise_func_colim c');
        coh_par_cocone_hom c' (f : hom c c') :
        hom (vertex (coh_par_cocone_down c' f)) (vertex coh_par_cocone);
        coh_par_cocone_hom_natural c' (f : hom c c') j :
        (side (coh_par_cocone_down c' f) j ∘ ((F ₒ j) ₕ f)) =
          ((side (coh_par_cocone) j) ∘ (coh_par_cocone_hom c' f))
      }.
  Arguments coh_par_cocone {_} _.
  Arguments coh_par_cocone_down {_} _ {_} _.
  Arguments coh_par_cocone_hom {_} _ {_} _.
  Arguments coh_par_cocone_hom_natural {_} _ {_} _ _.

  Program Definition extend_cocone (L : functor C D)
    (il : is_limit F L)
    (c' : obj C)
    (cn : coherent_partial_cocone c')
    (c : obj C)
    (f : hom c' c)
    : is_cone (pointwise_func_colim c') (vertex (coh_par_cocone_down cn f))
    := MkIsCone (λ j, ((F ₒ j) ₕ f) ∘ (side (coh_par_cocone_down cn f) j))
         (λ j j' g, _).
  Next Obligation.
    intros; simpl.
    by rewrite (side_commutes (coh_par_cocone_down cn f) g) comp_assoc
    -naturality -comp_assoc.
  Qed.

  Lemma func_cat_colimits_pointwise_natural
    {L : functor C D} (il : is_limit F L) {c'} (cn : coherent_partial_cocone c')
    {c : obj C} (f : hom c' c) :
    (cone_hom_map (bang (il_is_limiting_cone _ _
                           (func_cat_colimits_pointwise il c'))
                     (coh_par_cocone cn)) ∘ coh_par_cocone_hom cn f)
      =
      (L ₕ f ∘ cone_hom_map (bang (il_is_limiting_cone _ _ (func_cat_colimits_pointwise il c))
                               (coh_par_cocone_down cn f))).
  Proof.
    apply (@hom_to_limit_unique J _ (pointwise_func_colim c') _ _ _ _
             (func_cat_colimits_pointwise il c') (extend_cocone L il _ _ _ _)).
    - intros j; simpl.
      rewrite right_id !comp_assoc.
      epose proof (natural_equiv_pack (cone_hom_commutes (bang (il_is_limiting_cone F L il) func_colimit_cocone) j) c')
        as Hchc; rewrite /= in Hchc; rewrite -Hchc; clear Hchc.
      rewrite_cocone_hom_commutes_back.
      apply coh_par_cocone_hom_natural.
    - intros j; simpl.
      rewrite right_id.
      rewrite !(comp_assoc (L ₕ _)).
      epose proof (naturality (cone_hom_map (bang (il_is_limiting_cone F L il) func_colimit_cocone)) f)
        as Hn; rewrite /= in Hn; rewrite Hn; clear Hn.
      rewrite !comp_assoc.
      epose proof (natural_equiv_pack (cone_hom_commutes (bang (il_is_limiting_cone F L il) func_colimit_cocone) j) c')
        as Hchc; rewrite /= in Hchc; rewrite -Hchc /=; clear Hchc.
      rewrite /func_colimit_func_h_map.
      rewrite_cocone_hom_commutes_back; simpl.
      rewrite -comp_assoc.
      rewrite_cocone_hom_commutes_back; simpl.
      reflexivity.
  Qed.

End func_cat_colimit.

Definition func_cat_cocomplete {C D} `{!Complete (D ᵒᵖ)}
  : Complete ((FuncCat C D) ᵒᵖ) :=
  λ J F, func_colimit F.

(* Global Program Instance psh_cocomplete C : Complete ((PSh C) ᵒᵖ) *)
(*   := func_cat_cocomplete. *)

(* special cases of lemmas for presheaves and typs *)
Lemma psh_side_commutes {J C : category} {F : functor J (PSh C)}
  (cn : cone F) [j j' : obj J] (f : hom j j') (c : obj C) (x : vertex cn ₒ c) :
  (side cn j' ₙ c) x = ((F ₕ f)ₙ c) ((side cn j ₙ c) x).
Proof. by rewrite (@side_commutes _ _ F _ _ _ f). Qed.
Lemma psh_cone_hom_commutes {J C : category} {F : functor J (PSh C)}
  {cn cn' : cone F} (ch : cone_hom cn cn') (j : obj J)
  (c : obj C) (x : vertex cn ₒ c) :
  (side cn j ₙ c) x = (side cn' j ₙ c) ((cone_hom_map ch ₙ c) x).
Proof. by rewrite (@cone_hom_commutes _ _ F cn cn' ch). Qed.
Lemma psh_h_map_comp {C : category} {X : PreSheaf C}
  (a b c : obj C) (f : hom a b) (g : hom b c) (x : X ₒ c) :
  (X ₕ (g ∘ f)) x = (X ₕ f) ((X ₕ g) x).
Proof. by rewrite (@h_map_comp _ _ X). Qed.

Lemma typ_side_commutes {J : category} {F : functor J Typ}
  (cn : cone F) [j j' : obj J] (f : hom j j') (x : vertex cn) :
  (side cn j') x = (F ₕ f) ((side cn j) x).
Proof. by rewrite (@side_commutes _ _ F _ _ _ f). Qed.
Lemma typ_cone_hom_commutes {J : category} {F : functor J Typ}
  {cn cn' : cone F} (ch : cone_hom cn cn') (j : obj J) (x : vertex cn) :
  (side cn j) x = (side cn' j) ((cone_hom_map ch) x).
Proof. by rewrite (@cone_hom_commutes _ _ F cn cn' ch). Qed.

Ltac rewrite_cone_hom_commutes_back :=
  match goal with
    |- context [side _ ?j ∘ cone_hom_map ?c] => rewrite -(cone_hom_commutes c j)
  | |- context [ic_side _ ?j ∘ cone_hom_map ?c] => rewrite -(cone_hom_commutes c j)
  | |- context [(side _ ?j)
                 ((cone_hom_map ?c) ?d)] =>
      ltac:(let H := fresh in
            pose proof (typ_cone_hom_commutes c j d) as H;
            simpl in H;
            rewrite -H
           )
  | |- context [(ic_side _ ?j)
                 ((cone_hom_map ?c) ?d)] =>
      ltac:(let H := fresh in
            pose proof (typ_cone_hom_commutes c j d) as H;
            simpl in H;
            rewrite -H
           )
  | |- context [(typ_lim_side _ ?j)
                 ((cone_hom_map ?c) ?d)] =>
      ltac:(let H := fresh in
            pose proof (typ_cone_hom_commutes c j d) as H;
            simpl in H;
            rewrite -H
           )
  end.

Ltac rewrite_cocone_hom_commutes_back :=
  match goal with
    |- context [cone_hom_map ?c ∘ side _ ?j] =>
      let H := fresh "H" in
      pose proof (cone_hom_commutes c j)
        as H; simpl in H; rewrite -H; clear H
  | |- context [cone_hom_map ?c ∘ ic_side _ ?j] =>
      let H := fresh "H" in
      pose proof (cone_hom_commutes c j)
        as H; simpl in H; rewrite H; clear H
  end.

Record equiv_cones {J C} {F F' : functor J C}
  (Fiso : F ≃@{FuncCat J C} F') (cn : cone F) (cn' : cone F') := MkEqCones {
  eq_cones_vertexes : vertex cn ≃ vertex cn';
  eq_cones_sides :
    ∀ j, (forward Fiso ₙ j) ∘ side cn j = side cn' j ∘ (forward eq_cones_vertexes);
  (* This simply follows from the previous but we include it for simplicity. *)
  eq_cones_sides' :
    ∀ j, (backward Fiso ₙ j) ∘ side cn' j = side cn j ∘ (backward eq_cones_vertexes);
}.
Arguments MkEqCones {_ _ _ _ _ _ _} _ _.
Arguments eq_cones_vertexes {_ _ _ _ _ _ _} _.
Arguments eq_cones_sides {_ _ _ _ _ _ _} _ _.
Arguments eq_cones_sides' {_ _ _ _ _ _ _} _ _.

Program Definition MkEqCones' {J C} {F F' : functor J C} {Fiso : F ≃@{FuncCat J C} F'}
  {cn : cone F} {cn' : cone F'} (eq_cones_vertexes : vertex cn ≃ vertex cn')
  (eq_cones_sides : ∀ j : obj J,
      forward Fiso ₙ j ∘ side cn j = side cn' j ∘ forward eq_cones_vertexes) :
  equiv_cones Fiso cn cn' :=
  MkEqCones eq_cones_vertexes eq_cones_sides _.
Next Obligation.
  intros ???? iso ?? Heqv Heqs j.
  apply (compose_along_iso_left (natural_iso_proj iso j)).
  rewrite /= -!comp_assoc (iso_rl (is_iso (natural_iso_proj iso j))) left_id.
  apply (compose_along_iso_right Heqv).
  rewrite /= !comp_assoc (iso_lr (is_iso Heqv)) right_id; done.
Qed.
Fail Next Obligation.

Program Definition limit_of_isos_cone {C J} {F G : functor J C} (iso : F ≃@{FuncCat J C} G)
  (l : limit F) : cone G :=
  MkCone (vertex (term l)) (λ j, (forward iso ₙ j) ∘ side (term l) j) _.
Next Obligation.
  intros ???? iso ? j j' f; rewrite /=.
  apply (compose_along_iso_left (natural_iso_proj (isomorphic_sym iso) j')).
  rewrite /= -!comp_assoc.
  pose proof (natural_equiv_pack (iso_lr (is_iso iso)) j') as Hn; simpl in Hn; rewrite Hn; clear Hn.
  rewrite left_id.
  rewrite naturality.
  rewrite !comp_assoc -(comp_assoc _ _ (backward iso ₙ _)).
  pose proof (natural_equiv_pack (iso_lr (is_iso iso)) j) as Hn; simpl in Hn; rewrite Hn; clear Hn.
  rewrite left_id -side_commutes //.
Qed.
Fail Next Obligation.

Program Definition limit_of_isos_equiv_cones {C J} {F G : functor J C} (iso : F ≃@{FuncCat J C} G)
  (l : limit F) (l' : limit G) : equiv_cones iso (term l) (term l') :=
  @MkEqCones' _ _ _ _ iso _ _
    (MkIsoIc
       (cone_hom_map (bang (term_is_terminal l') (limit_of_isos_cone iso l)))
       (cone_hom_map (bang (term_is_terminal l) (limit_of_isos_cone (isomorphic_sym iso) l')))
       _)
    _.
Next Obligation.
  intros ? ? ? ? iso l l'; split.
  - apply (hom_to_limit_unique _ _ _ (limit_is_limit l)
             (cone_is_cone (term l))).
    + intros j; rewrite /= -comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite -comp_assoc.
      pose proof (natural_equiv_pack (iso_lr (is_iso iso)) j) as Hn; simpl in Hn; rewrite Hn; clear Hn.
      rewrite left_id //.
    + intros j; rewrite /= right_id //.
  - apply (hom_to_limit_unique _ _ _ (limit_is_limit l')
             (cone_is_cone (term l'))).
    + intros j; rewrite /= -comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite comp_assoc.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite -comp_assoc.
      pose proof (natural_equiv_pack (iso_rl (is_iso iso)) j) as Hn; simpl in Hn; rewrite Hn; clear Hn.
      rewrite left_id //.
    + intros j; rewrite /= right_id //.
Qed.
Next Obligation. intros; simpl; rewrite_cone_hom_commutes_back; done. Qed.
Fail Next Obligation.

(* algebras *)

Record algebra {C : category} (T : functor C C) := MkAlg {
  car : obj C;
  cons : hom (T ₒ car) car;
}.
Global Arguments MkAlg {_ _} _ _.
Global Arguments car {_ _} _.
Global Arguments cons {_ _} _.

Record alg_hom {C : category} {T : functor C C} (A B : algebra T) := MkAlgHom {
  alg_hom_map : hom (car A) (car B);
  alg_hom_commutes : alg_hom_map ∘ cons A = cons B ∘ (T ₕ alg_hom_map);
}.
Global Arguments MkAlgHom {_ _ _ _} _ _.
Global Arguments alg_hom_map {_ _ _ _} _.
Global Arguments alg_hom_commutes {_ _ _ _} _.

Global Instance alg_hom_eq {C : category} {T : functor C C} (A B : algebra T) :
  Equiv (alg_hom A B) := λ f g, alg_hom_map f = alg_hom_map g.

Global Instance alg_hom_eq_eq {C : category} {T : functor C C} (A B : algebra T) :
  Equivalence (alg_hom_eq A B).
Proof.
  rewrite /alg_hom_eq.
  split.
  - intros []; reflexivity.
  - intros [] []; simpl; done.
  - intros [] [] []; simpl; intros ->; done.
Qed.

Lemma alg_hom_map_eq {C : category} {T : functor C C} {A B : algebra T} (f g : alg_hom A B) :
  alg_hom_map f = alg_hom_map g → f = g.
Proof.
  intros H.
  destruct f, g.
  simpl in H.
  destruct H.
  f_equal.
  apply proof_irrelevance.
Qed.
Lemma alg_hom_map_eq' {C : category} {T : functor C C} {A B : algebra T} (f g : alg_hom A B) :
  f = g → alg_hom_map f = alg_hom_map g.
Proof.
  by intros ->.
Qed.
Lemma alg_hom_map_eq_eq {C : category} {T : functor C C} {A B : algebra T}
  (f g : alg_hom A B) :
  f = g → alg_hom_map f = alg_hom_map g.
Proof. intros ->. reflexivity. Qed.

Program Definition alg_hom_id {C : category} {T : functor C C} (A : algebra T) :
  alg_hom A A :=
  MkAlgHom (id (car A)) _.
Next Obligation. repeat intros ?; rewrite left_id h_map_id right_id //. Qed.
Fail Next Obligation.

Program Definition alg_hom_comp {C : category} {T : functor C C} {A B D : algebra T}
  (f : alg_hom A B) (g : alg_hom B D) : alg_hom A D :=
  MkAlgHom ((alg_hom_map g) ∘ (alg_hom_map f)) _.
Next Obligation.
  repeat intros ?.
  rewrite comp_assoc alg_hom_commutes.
  rewrite -comp_assoc alg_hom_commutes.
  rewrite comp_assoc -h_map_comp //.
Qed.
Fail Next Obligation.

Lemma alg_hom_assoc {C : category} {T : functor C C} {A B D E : algebra T}
  (f : alg_hom A B) (g : alg_hom B D) (h : alg_hom D E) :
    alg_hom_comp f (alg_hom_comp g h) = alg_hom_comp (alg_hom_comp f g) h.
Proof.
  rewrite /alg_hom_comp.
  apply alg_hom_map_eq; simpl.
  rewrite comp_assoc //.
Qed.

Lemma alg_hom_left_id {C : category} {T : functor C C} {A B : algebra T}
  (f : alg_hom A B) : alg_hom_comp f (alg_hom_id B) = f.
Proof.
  rewrite /alg_hom_comp.
  apply alg_hom_map_eq; simpl.
  rewrite left_id //.
Qed.

Lemma alg_hom_right_id {C : category} {T : functor C C} {A B : algebra T}
  (f : alg_hom A B) : alg_hom_comp (alg_hom_id A) f = f.
Proof.
  rewrite /alg_hom_comp.
  apply alg_hom_map_eq; simpl.
  rewrite right_id //.
Qed.

Program Definition Alg {C : category} (T : functor C C) : category :=
 MkCat
   (algebra T)
   (@alg_hom _ T)
   (@alg_hom_id _ T)
   (@alg_hom_comp _ T)
   (@alg_hom_assoc _ T)
   (@alg_hom_left_id _ T)
   (@alg_hom_right_id _ T).

Lemma alg_hom_map_comp {C : category} {T : functor C C} {A B D : algebra T}
  (f : alg_hom A B) (g : alg_hom B D) :
  alg_hom_map (g ∘@{Alg T} f) = alg_hom_map g ∘ alg_hom_map f.
Proof. done. Qed.

Program Definition alg_iso {C : category} {T : functor C C} {A B : algebra T}
  (iso : A ≃@{Alg T} B) : (car A) ≃@{C} (car B) :=
  MkIsoIc (alg_hom_map (forward iso)) (alg_hom_map (backward iso)) _.
Next Obligation.
  split.
  - rewrite /= -alg_hom_map_comp (iso_lr (is_iso iso)) //.
  - rewrite /= -alg_hom_map_comp (iso_rl (is_iso iso)) //.
Qed.
Fail Next Obligation.

Definition car_eq {C : category} {T : functor C C} {A B : algebra T} (Heq : A = B) :
  car A = car B :=
  match Heq in (_ = z) return (car A = car z) with
   | eq_refl => eq_refl
   end.

Lemma hom_trans_alg_hom_map {C : category} {T : functor C C}
  {A A' B B' : algebra T} (Heq : A = A') (Heq' : B = B') (h : alg_hom A B) :
  alg_hom_map (hom_trans (C := Alg T) Heq Heq' h) =
    hom_trans (car_eq Heq) (car_eq Heq') (alg_hom_map h).
Proof. destruct Heq; destruct Heq'; rewrite /= !hom_trans_refl //. Qed.

Program Definition forgetful {C : category} (T : functor C C) : functor (Alg T) C :=
  MkFunc car (λ _ _ f, alg_hom_map f) _ _.
Solve All Obligations with repeat intros; simpl in *; done.
Fail Next Obligation.

Program Definition alg_func_on_alg {C : category} {T : functor C C} (A : algebra T) : algebra T :=
  MkAlg (T ₒ (car A)) (T ₕ (cons A)).

Program Definition alg_func_on_alg_h_map {C : category} {T : functor C C}
  {A B : algebra T} (f : alg_hom A B) : alg_hom (alg_func_on_alg A) (alg_func_on_alg B) :=
  MkAlgHom (T ₕ (alg_hom_map f)) _.
Next Obligation. intros; rewrite /= -!h_map_comp alg_hom_commutes //. Qed.
Fail Next Obligation.

Program Definition alg_func_func {C : category} (T : functor C C) : functor (Alg T) (Alg T) :=
  MkFunc alg_func_on_alg (λ _ _ f, alg_func_on_alg_h_map f) _ _.
Next Obligation.
  repeat intros ?; apply alg_hom_map_eq; rewrite /= -h_map_comp //.
Qed.
Next Obligation.
  repeat intros ?; apply alg_hom_map_eq; rewrite /= -h_map_id //.
Qed.
Fail Next Obligation.

Program Definition alg_func_on_cone {C : category} {T : functor C C}
  {J} {F : functor J (Alg T)} (cn : cone F) : cone F :=
  MkCone (alg_func_func T ₒ (vertex cn))
  (λ j, MkAlgHom (cons (F ₒ j) ∘ (alg_hom_map (alg_func_func T ₕ (side cn j)))) _) _.
Next Obligation. intros; rewrite /= comp_assoc -h_map_comp alg_hom_commutes //. Qed.
Next Obligation.
  intros ???? cn j j' f; apply alg_hom_map_eq; rewrite /=.
  rewrite -comp_assoc alg_hom_commutes comp_assoc.
  rewrite -h_map_comp.
  pose proof (side_commutes cn f) as Hsc;
  apply alg_hom_map_eq' in Hsc; rewrite /= /alg_hom_comp /= in Hsc;
    rewrite -Hsc //.
Qed.
Fail Next Obligation.

Program Definition alg_func_on_eq_cones {C : category} {T : functor C C}
  {J} {F F' : functor J (Alg T)} {iso : F ≃@{FuncCat J (Alg T)} F'}
  {cn : cone F} {cn' : cone F'} (cneq : equiv_cones iso cn cn') :
  equiv_cones iso (alg_func_on_cone cn) (alg_func_on_cone cn') :=
  @MkEqCones' _ _ _ _ _ (alg_func_on_cone cn) (alg_func_on_cone cn')
    (functor_preserves_iso (alg_func_func T) (eq_cones_vertexes cneq)) _.
Next Obligation.
  intros ????? iso ?? cneq j; apply alg_hom_map_eq; rewrite /= -!alg_hom_commutes /=.
  rewrite !comp_assoc -!alg_hom_commutes /= -!comp_assoc.
  epose proof (eq_cones_sides cneq j) as Heqcs; apply alg_hom_map_eq' in Heqcs;
    simpl in Heqcs; rewrite Heqcs //.
Qed.
Fail Next Obligation.

Section algebra_limits.
  Context `{!Complete C} {T : functor C C} {J} (F : functor J (Alg T)).

  Notation F' := (functor_compose F (forgetful T)).

  Definition alg_lim_obj := vertex (term (complete F')).

  Program Definition alg_lim_cone_for_cons : cone F' :=
    MkCone (T ₒ alg_lim_obj)
      (λ c, cons (F ₒ c) ∘ (T ₕ (side (term (complete F')) c)))
      _.
  Next Obligation.
    intros ?? f; rewrite /=.
    rewrite -comp_assoc (alg_hom_commutes (F ₕ f)) comp_assoc -h_map_comp.
    rewrite -side_commutes //.
  Qed.
  Fail Next Obligation.

  Definition alg_lim_alg : algebra T :=
    MkAlg alg_lim_obj (cone_hom_map (bang (term_is_terminal (complete F')) alg_lim_cone_for_cons)).

  Program Definition alg_lim_cone_side j : alg_hom alg_lim_alg (F ₒ j) :=
    MkAlgHom (side (term (complete F')) j) _.
  Next Obligation.
    intros ?; rewrite /=.
    rewrite_cone_hom_commutes_back; done.
  Qed.
  Fail Next Obligation.

  Program Definition alg_lim_cone : cone F :=
    MkCone alg_lim_alg alg_lim_cone_side _.
  Next Obligation.
    intros ?? f; apply alg_hom_map_eq; rewrite /alg_lim_cone_side /= -side_commutes //.
  Qed.
  Fail Next Obligation.

  Program Definition hom_to_alg_lim_cone (cn : cone F) : cone F' :=
    MkCone (forgetful T ₒ (vertex cn)) (λ c, forgetful T ₕ (side cn c)) _.
  Next Obligation. intros cn ?? f; rewrite /= (side_commutes cn f) //. Qed.
  Fail Next Obligation.

  Program Definition hom_to_alg_lim (cn : cone F) : cone_hom cn alg_lim_cone :=
    MkConeHom
      (MkAlgHom
         (cone_hom_map (bang (term_is_terminal (complete F')) (hom_to_alg_lim_cone cn)))
         _)
      _.
  Next Obligation.
    intros; rewrite /=.
    apply (hom_to_limit_unique _ _ _
                               (limiting_cone_is_limit (term_is_terminal (complete F')))
             (cone_is_cone (extend_cone (hom_to_alg_lim_cone cn) (cons (vertex cn))))).
    - intros c; rewrite /= -comp_assoc ic_side_limiting_cone_is_limit.
      rewrite_cone_hom_commutes_back; done.
    - intros c; rewrite /= -comp_assoc.
      rewrite ic_side_limiting_cone_is_limit.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite comp_assoc -h_map_comp.
      rewrite_cone_hom_commutes_back; simpl.
      rewrite -(alg_hom_commutes (side cn c)) //.
  Qed.
  Next Obligation.
    intros ??; rewrite /=.
    rewrite /equiv /alg_hom_eq /=.
    apply alg_hom_map_eq; simpl.
    rewrite_cone_hom_commutes_back; done.
  Qed.
  Fail Next Obligation.

  Program Definition cone_hom_of_alg_cone_hom {cn : cone F} (f : cone_hom cn alg_lim_cone) :
    cone_hom (hom_to_alg_lim_cone cn) (term (complete F')) :=
    MkConeHom (alg_hom_map (cone_hom_map f)) _.
  Next Obligation.
    intros cn f c.
    unfold hom_to_alg_lim_cone; simpl.
    rewrite (cone_hom_commutes f c) //.
  Qed.
  Fail Next Obligation.

  Program Definition alg_lim : limit F :=
    MkTerm alg_lim_cone (MkIsTerm alg_lim_cone hom_to_alg_lim _).
  Next Obligation.
    intros cn f.
    apply cone_hom_equiv_unpack.
    apply alg_hom_map_eq; simpl.
    rewrite -(bang_unique (term_is_terminal (complete F')) (cone_hom_of_alg_cone_hom f)) //.
  Qed.
  Fail Next Obligation.

End algebra_limits.

Global Instance alg_complete `{!Complete C} (T : functor C C) : Complete (Alg T) :=
  λ _ F, alg_lim F.

Program Definition prod_exp_forward {C : category} `{!CCC C} (y : obj C) :
  natural
    (in_left_of_hom C C ₒ (functor_fix_right (prod_func _) ₒ y))
    (in_right_of_hom C C ₒ (functor_fix_left exp_func ₒ y))
  := (MkNat (λ c, λ f, (transpose (f ∘ commutator _ _))) _).
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality x.
  rewrite comp_assoc.
  rewrite commute_hom_prod.
  rewrite !comp_assoc.
  rewrite /hom_exp.
  erewrite <-exp_hom_unique; last reflexivity.
  symmetry.
  apply exp_hom_unique.
  rewrite /transpose.
  rewrite -!comp_assoc.
  rewrite -(left_id (id _)).
  rewrite hom_prod_comp.
  rewrite -(left_id (id _)).
  rewrite hom_prod_comp.
  rewrite -!comp_assoc.
  rewrite -exp_hom_commutes.
  f_equiv.
  - by rewrite !left_id.
  - rewrite !comp_assoc.
    f_equiv.
    by rewrite -exp_hom_commutes.
Qed.

Program Definition prod_exp_backward {C : category} `{!CCC C} (y : obj C) :
  natural
    (in_right_of_hom C C ₒ (functor_fix_left exp_func ₒ y))
    (in_left_of_hom C C ₒ (functor_fix_right (prod_func _) ₒ y))
  := (MkNat (λ c, λ f, untranspose f ∘ commutator _ _) _).
Next Obligation.
  repeat intros ?; simpl in *.
  extensionality x.
  rewrite /untranspose.
  rewrite !comp_assoc.
  rewrite /hom_exp.
  rewrite -exp_hom_commutes.
  rewrite -(left_id (id _)).
  rewrite hom_prod_comp.
  rewrite -!comp_assoc.
  rewrite -exp_hom_commutes.
  rewrite !comp_assoc.
  do 2 f_equiv.
  rewrite left_id.
  rewrite commute_hom_prod.
  rewrite -!comp_assoc.
  rewrite commute_hom_prod.
  rewrite !comp_assoc.
  rewrite -hom_prod_comp.
  rewrite left_id.
  reflexivity.
Qed.

Program Definition prod_exp_adj {C : category} `{!CCC C} (y : obj C)
  : (adjunction (C := C)
        (functor_fix_right (prod_func _) ₒ y) (functor_fix_left exp_func ₒ y))
  := MkIsoIc (prod_exp_forward y)
       (prod_exp_backward y)
       _.
Next Obligation.
  intros; simpl.
  constructor.
  - repeat intros ?; simpl in *.
    apply natural_equiv_unpack; intros x; simpl.
    extensionality z.
    rewrite untranspose_transpose.
    rewrite comp_assoc.
    rewrite commutator_involutive.
    by rewrite right_id.
  - apply natural_equiv_unpack; intros x; simpl.
    extensionality z.
    rewrite /transpose.
    erewrite (exp_hom_unique _ _ z); last reflexivity.
    rewrite untranspose_transpose.
    rewrite !comp_assoc.
    rewrite commutator_involutive.
    rewrite right_id.
    reflexivity.
Qed.

Program Definition functor_prod_iso_proper {C D E H} {F F' : functor C D} {G G' : functor E H}
  (iso : F ≃@{FuncCat C D} F') (iso' : G ≃@{FuncCat E H} G') :
  functor_prod F G ≃@{FuncCat (cat_prod C E) (cat_prod D H)} functor_prod F' G'
  := MkIsoIc
       (MkNat (λ α, (nat_map (forward iso) α.1, nat_map (forward iso') α.2)) _)
       (MkNat (λ α, (nat_map (backward iso) α.1, nat_map (backward iso') α.2)) _)
       _.
Next Obligation.
  intros; simpl.
  rewrite !naturality.
  reflexivity.
Qed.
Next Obligation.
  intros; simpl.
  rewrite !naturality.
  reflexivity.
Qed.
Next Obligation.
  intros; simpl.
  split.
  - apply natural_equiv_unpack; intros x; simpl.
    pose proof (natural_equiv_pack (iso_lr (is_iso iso)) x.1) as HEQ.
    simpl in HEQ.
    rewrite HEQ.
    pose proof (natural_equiv_pack (iso_lr (is_iso iso')) x.2) as HEQ'.
    simpl in HEQ'.
    rewrite HEQ'.
    reflexivity.
  - apply natural_equiv_unpack; intros x; simpl.
    pose proof (natural_equiv_pack (iso_rl (is_iso iso)) x.1) as HEQ.
    simpl in HEQ.
    rewrite HEQ.
    pose proof (natural_equiv_pack (iso_rl (is_iso iso')) x.2) as HEQ'.
    simpl in HEQ'.
    rewrite HEQ'.
    reflexivity.
Qed.

Program Definition functor_eq_natural_backward {C D : category} {F G : functor C D}
  : functor_equiv F G → natural G F
  := λ H, MkNat (λ c, hom_trans eq_refl (eq_sym (func_eq_o_map H c)) (id (G ₒ c))) _.
Next Obligation.
  repeat intros ?; simpl.
  rewrite hom_trans_compose_take_in_r left_id /= hom_trans_refl.
  rewrite hom_trans_compose_take_in_l right_id /= hom_trans_refl.
  change (eq_refl (G ₒ a)) with (eq_sym (eq_refl (G ₒ a))).
  symmetry.
  apply hom_trans_sym.
  rewrite eq_sym_involutive.
  rewrite -hom_trans_trans /= eq_trans_refl_l.
  apply H.
Qed.

Program Definition functor_eq_natural_iso {C D} {F G : obj (FuncCat C D)}
  : functor_equiv F G → F ≃ G
  := λ H, MkIsoIc (C := FuncCat _ _)
            (functor_eq_natural H)
            (functor_eq_natural_backward H) _.
Next Obligation.
  intros.
  split.
  - apply natural_equiv_unpack; intros ?; simpl.
    rewrite hom_trans_compose_take_in_r left_id /= hom_trans_refl.
    destruct (func_eq_o_map H a).
    simpl.
    rewrite hom_trans_refl.
    reflexivity.
  - apply natural_equiv_unpack; intros ?; simpl.
    rewrite hom_trans_compose_take_in_r left_id /= hom_trans_refl.
    destruct (func_eq_o_map H a).
    simpl.
    rewrite hom_trans_refl.
    reflexivity.
Qed.

Program Definition functor_compose_left_id_iso {C D}
  {F : functor C D} :
  F ≃@{FuncCat C D} functor_compose (id_functor _) F
  := MkIsoIc
       (MkNat (λ α, id _) _)
       (MkNat (λ α, id _) _)
       _.
Next Obligation.
  intros; simpl.
  by rewrite left_id right_id.
Qed.
Next Obligation.
  intros; simpl.
  by rewrite left_id right_id.
Qed.
Next Obligation.
  by intros; split; apply natural_equiv_unpack; intros ?; simpl; rewrite left_id.
Qed.

Program Definition functor_compose_right_id_iso {C D}
  {F : functor C D} :
  F ≃@{FuncCat C D} functor_compose F (id_functor _)
  := MkIsoIc
       (MkNat (λ α, id _) _)
       (MkNat (λ α, id _) _)
       _.
Next Obligation.
  intros; simpl.
  by rewrite left_id right_id.
Qed.
Next Obligation.
  intros; simpl.
  by rewrite left_id right_id.
Qed.
Next Obligation.
  by intros; split; apply natural_equiv_unpack; intros ?; simpl; rewrite left_id.
Qed.

Program Definition functor_compose_assoc_iso {A B C D}
  {F : functor A B} {G : functor B C} {H : functor C D} :
  functor_compose F (functor_compose G H) ≃@{FuncCat A D}
    functor_compose (functor_compose F G) H
  := MkIsoIc
       (MkNat (λ α, id _) _)
       (MkNat (λ α, id _) _)
       _.
Next Obligation.
  intros; simpl.
  by rewrite left_id right_id.
Qed.
Next Obligation.
  intros; simpl.
  by rewrite left_id right_id.
Qed.
Next Obligation.
  by intros; split; apply natural_equiv_unpack; intros ?; simpl; rewrite left_id.
Qed.

Program Definition functor_prod_prod_iso {C D C' D' E E'}
  {F : functor C D} {F' : functor D E}
  {G : functor C' D'} {G' : functor D' E'}
  : functor_compose (functor_prod F G) (functor_prod F' G')
      ≃@{FuncCat (cat_prod C C') (cat_prod E E')}
      functor_prod (functor_compose F F') (functor_compose G G')
  := MkIsoIc
       (MkNat (λ α, (F' ₕ (F ₕ (id _)), G' ₕ (G ₕ (id _)))) _)
       (MkNat (λ α, (F' ₕ (F ₕ (id _)), G' ₕ (G ₕ (id _)))) _)
       _.
Next Obligation.
  intros; simpl.
  rewrite !h_map_id.
  rewrite !left_id.
  rewrite !right_id.
  reflexivity.
Qed.
Next Obligation.
  intros; simpl.
  rewrite !h_map_id.
  rewrite !left_id.
  rewrite !right_id.
  reflexivity.
Qed.
Next Obligation.
  intros; simpl; split.
  - apply natural_equiv_unpack; intros ?; simpl.
    rewrite !h_map_id.
    rewrite !left_id.
    reflexivity.
  - apply natural_equiv_unpack; intros ?; simpl.
    rewrite !h_map_id.
    rewrite !left_id.
    reflexivity.
Qed.

Program Definition functor_fix_left_proper_iso {C D E}
  {F G : functor (cat_prod C D) E} (H : F ≃@{FuncCat _ _} G) :
  functor_fix_left F ≃@{FuncCat _ _} functor_fix_left G
  := MkIsoIc
       (MkNat (λ α,
            MkNat (λ β, forward (natural_iso_proj H (α, β)))
              (λ a b f, naturality (forward H) (id α, f))) _)
       (MkNat (λ α,
            MkNat (λ β, backward (natural_iso_proj H (α, β)))
              (λ a b f, naturality (backward H) (id α, f))) _)
       _.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl.
  apply natural_equiv_unpack; intros ?; simpl.
  rewrite naturality.
  reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl.
  apply natural_equiv_unpack; intros ?; simpl.
  rewrite naturality.
  reflexivity.
Defined.
Next Obligation.
  intros; simpl.
  split; apply natural_equiv_unpack; intros ?; simpl;
    apply natural_equiv_unpack; intros ?; simpl.
  - rewrite iso_lr; first reflexivity.
    apply (is_iso (natural_iso_proj H _)).
  - rewrite iso_rl; first reflexivity.
    apply (is_iso (natural_iso_proj H _)).
Defined.

Program Definition functor_fix_right_proper_iso {C D E}
  {F G : functor (cat_prod C D) E} (H : F ≃@{FuncCat _ _} G) :
  functor_fix_right F ≃@{FuncCat _ _} functor_fix_right G
  := MkIsoIc
       (MkNat (λ α,
            MkNat (λ β, forward (natural_iso_proj H (β, α)))
              (λ a b f, naturality (forward H) (f, id α))) _)
       (MkNat (λ α,
            MkNat (λ β, backward (natural_iso_proj H (β, α)))
              (λ a b f, naturality (backward H) (f, id α))) _)
       _.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl.
  apply natural_equiv_unpack; intros ?; simpl.
  rewrite naturality.
  reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl; reflexivity.
Defined.
Next Obligation.
  intros; simpl.
  apply natural_equiv_unpack; intros ?; simpl.
  rewrite naturality.
  reflexivity.
Defined.
Next Obligation.
  intros; simpl.
  split; apply natural_equiv_unpack; intros ?; simpl;
    apply natural_equiv_unpack; intros ?; simpl.
  - rewrite iso_lr; first reflexivity.
    apply (is_iso (natural_iso_proj H _)).
  - rewrite iso_rl; first reflexivity.
    apply (is_iso (natural_iso_proj H _)).
Defined.

Program Definition functor_opposite_compose {C D E}
  {F : functor C D}
  {G : functor D E} :
  functor_compose (opposite_func F) (opposite_func G)
    ≃@{FuncCat (C ᵒᵖ) (E ᵒᵖ)} opposite_func (functor_compose F G)
  := MkIsoIc
       (MkNat (λ x, id _) _)
       (MkNat (λ x, id _) _)
       _.
Next Obligation.
  intros; simpl.
  by rewrite left_id right_id.
Qed.
Next Obligation.
  intros; simpl.
  by rewrite left_id right_id.
Qed.
Next Obligation.
  intros; split; apply natural_equiv_unpack; intros ?; simpl; by rewrite left_id.
Qed.

Program Definition functor_opposite_proper {C D} {F G : functor C D}
  (H : F ≃@{FuncCat C D} G)
  : opposite_func F ≃@{FuncCat (C ᵒᵖ) (D ᵒᵖ)} opposite_func G
  := MkIsoIc
       (MkNat (λ x, (backward H ₙ) x) _)
       (MkNat (λ x, (forward H ₙ) x) _)
       _.
Next Obligation.
  intros; simpl.
  by rewrite naturality.
Qed.
Next Obligation.
  intros; simpl.
  by rewrite naturality.
Qed.
Next Obligation.
  intros; split; apply natural_equiv_unpack; intros ?; simpl.
  - apply (natural_equiv_pack (iso_lr (is_iso H))).
  - apply (natural_equiv_pack (iso_rl (is_iso H))).
Qed.

Program Definition functor_fix_right_post_comp {C D E E'}
  {F : functor (cat_prod C D) E} {G : functor E E'}
  {X : obj D}
  : functor_compose (functor_fix_right F ₒ X) G
      ≃@{FuncCat C E'}
      functor_fix_right (functor_compose F G) ₒ X
  := MkIsoIc
       (MkNat (λ X, id _) _)
       (MkNat (λ X, id _) _)
       _.
Next Obligation.
  intros; simpl; by rewrite left_id right_id.
Qed.
Next Obligation.
  intros; simpl; by rewrite left_id right_id.
Qed.
Next Obligation.
  intros; split; apply natural_equiv_unpack; intros ?; simpl; by rewrite right_id.
Qed.

Program Definition functor_fix_right_pre_comp {C C' D E}
  {F : functor (cat_prod C D) E} {G : functor C' C}
  {X : obj D}
  : functor_compose G (functor_fix_right F ₒ X)
      ≃@{FuncCat C' E}
      functor_fix_right (functor_compose (functor_prod G (id_functor _)) F) ₒ X
  := MkIsoIc
       (MkNat (λ X, id _) _)
       (MkNat (λ X, id _) _)
       _.
Next Obligation.
  intros; simpl; by rewrite left_id right_id.
Qed.
Next Obligation.
  intros; simpl; by rewrite left_id right_id.
Qed.
Next Obligation.
  intros; split; apply natural_equiv_unpack; intros ?; simpl; by rewrite right_id.
Qed.

Program Definition functor_fix_right_commute {C D E}
  {F : functor (cat_prod C D) E} {G : functor C D}
  {X : obj C}
  : functor_fix_right F ₒ (G ₒ X)
      ≃@{FuncCat C E}
      functor_fix_right (functor_compose (functor_prod (id_functor _) G) F) ₒ X
  := MkIsoIc
       (MkNat (λ X, id _) _)
       (MkNat (λ X, id _) _)
       _.
Next Obligation.
  intros; simpl; by rewrite left_id right_id h_map_id.
Qed.
Next Obligation.
  intros; simpl; by rewrite left_id right_id h_map_id.
Qed.
Next Obligation.
  intros; split; apply natural_equiv_unpack; intros ?; simpl; by rewrite right_id.
Qed.
