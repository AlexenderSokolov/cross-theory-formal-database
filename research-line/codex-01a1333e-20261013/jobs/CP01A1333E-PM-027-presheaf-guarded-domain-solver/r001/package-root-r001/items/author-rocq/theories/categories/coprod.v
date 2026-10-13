From SynthDom Require Import prelude.
From SynthDom.categories Require Import category.

Open Scope category.

Record coproduct {C} (a b : obj C) := MkCoprod {
  coprd : obj C;
  inj1 : hom a coprd;
  inj2 : hom b coprd;
  coprd_hom d (p1 : hom a d) (p2 : hom b d) : hom coprd d;
  coprd_hom_commutes1 d p1 p2 : p1 = (coprd_hom d p1 p2) ∘ inj1;
  coprd_hom_commutes2 d p1 p2 : p2 = (coprd_hom d p1 p2) ∘ inj2;
  coprd_hom_unique d p1 p2 (h : hom coprd d) :
    p1 = h ∘ inj1 → p2 = h ∘ inj2 → h = coprd_hom d p1 p2;
}.

Global Arguments MkCoprod {_ _ _} _ _ _ _ _ _ _.
Global Arguments coprd {_ _ _} _.
Global Arguments inj1 {_ _ _} _.
Global Arguments inj2 {_ _ _} _.
Global Arguments coprd_hom {_ _ _} _ {_} _ _.
Global Arguments coprd_hom_commutes1 {_ _ _} _ {_} _ _.
Global Arguments coprd_hom_commutes2 {_ _ _} _ {_} _ _.
Global Arguments coprd_hom_unique {_ _ _} _ {_} _ _ _.

Lemma coprd_hom_unique' {C} {a b : obj C} (p : coproduct a b) {d : obj C}
  (p1 : hom a d) (p2 : hom b d) (h1 h2 : hom (coprd p) d) :
  p1 = h1 ∘ inj1 p → p2 = h1 ∘ inj2 p → p1 = h2 ∘ inj1 p → p2 = h2 ∘ inj2 p → h1 = h2.
Proof.
  intros.
  erewrite (coprd_hom_unique _ _ _ h1); [|eassumption|eassumption].
  erewrite (coprd_hom_unique _ _ _ h2); [|eassumption|eassumption].
  done.
Qed.

Class HasCoproducts C := coproduct_of (a b : obj C) : coproduct a b.
Global Arguments coproduct_of {_ _} _ _, _ {_} _ _.

Definition obj_coprod `{!HasCoproducts C} a b : obj C := coprd (coproduct_of a b).

(* Coproduct of two homomorphisms. *)
Definition hom_coprod `{!HasCoproducts C} {a b c d} (f : hom c a) (g : hom d b) :
  hom (obj_coprod c d) (obj_coprod a b) := coprd_hom _ (inj1 _ ∘ f) (inj2 _ ∘ g).

(* Morphism from an object from a coproduct. *)
Definition hom_to_coprod `{!HasCoproducts C} {a c d} (f : hom c a) (g : hom d a) :
  hom (obj_coprod c d) a := coprd_hom _ f g.

Infix "+ₒ@{ C }" := (obj_coprod (C := C)) (at level 40, left associativity) : category_scope.
Infix "+ₒ" := obj_coprod (at level 40, left associativity) : category_scope.
Infix "+ₕ@{ C }" := (hom_coprod (C := C)) (at level 40, left associativity) : category_scope.
Infix "+ₕ" := hom_coprod (at level 40, left associativity) : category_scope.
Notation "<< f | g >>" :=
  (hom_to_coprod f g) (at level 20, no associativity) : category_scope.

Lemma hom_coprod_comp `{!HasCoproducts C} {a b c d e f}
  (g1 : hom c a) (g2 : hom e c) (h1 : hom d b) (h2 : hom f d) :
  (h1 ∘ h2) +ₕ (g1 ∘ g2) = (h1 +ₕ g1) ∘ (h2 +ₕ g2).
Proof.
  symmetry; apply coprd_hom_unique.
  - rewrite !comp_assoc -coprd_hom_commutes1 -!comp_assoc -coprd_hom_commutes1 //.
  - rewrite !comp_assoc -coprd_hom_commutes2 -!comp_assoc -coprd_hom_commutes2 //.
Qed.
Lemma hom_coprod_id `{!HasCoproducts C} {a b} : (id a) +ₕ (id b) = id (a +ₒ b).
Proof. symmetry; apply coprd_hom_unique; rewrite left_id right_id //. Qed.

Lemma hom_coprod_comp_left_id `{!HasCoproducts C} {a b d f}
  (h1 : hom b d) (h2 : hom d f) : (id a) +ₕ (h2 ∘ h1) = (id a +ₕ h2) ∘ (id a +ₕ h1).
Proof. rewrite -{1}(left_id (id a)) hom_coprod_comp //. Qed.
Lemma hom_coprod_comp_right_id `{!HasCoproducts C} {a b c e}
  (g1 : hom a c) (g2 : hom c e) : (g2 ∘ g1) +ₕ (id b) = (g2 +ₕ id b) ∘ (g1 +ₕ id b).
Proof. rewrite -{1}(left_id (id b)) hom_coprod_comp //. Qed.

Lemma hom_coprod_split `{!HasCoproducts C} {a b c d} (f : hom a c) (g : hom b d) :
  f +ₕ g = id _ +ₕ g ∘ (f +ₕ id _).
Proof. rewrite -hom_coprod_comp left_id right_id //. Qed.

Lemma hom_coprod_inj1 `{!HasCoproducts C} {a b c d} (f : hom a c) (g : hom b d) :
  (f +ₕ g) ∘ inj1 _ = inj1 _ ∘ f.
Proof. rewrite /hom_coprod -coprd_hom_commutes1 //. Qed.
Lemma hom_coprod_inj2 `{!HasCoproducts C} {a b c d} (f : hom a c) (g : hom b d) :
  (f +ₕ g) ∘ inj2 _ = inj2 _ ∘ g.
Proof. rewrite /hom_coprod -coprd_hom_commutes2 //. Qed.

Program Definition coprod_func C `{!HasCoproducts C} : functor (cat_prod C C) C :=
  MkFunc (λ ab, ab.1 +ₒ ab.2) (λ _ _ h, h.1 +ₕ h.2) _ _.
Next Obligation. repeat intros ?; apply hom_coprod_comp. Qed.
Next Obligation. repeat intros ?; apply hom_coprod_id. Qed.
Fail Next Obligation.

Program Definition iso_coprod `{!HasCoproducts C} {a b c d} (iso : a ≃@{C} c)
  (iso' : b ≃@{C} d) :
  (a +ₒ b) ≃ (c +ₒ d) :=
  MkIsoIc (forward iso +ₕ forward iso') (backward iso +ₕ backward iso') _.
Next Obligation.
  repeat intros; split.
  - rewrite -hom_coprod_comp.
    destruct (is_iso iso) as [-> _]. destruct (is_iso iso') as [-> _].
    rewrite hom_coprod_id //.
  - rewrite -hom_coprod_comp.
    destruct (is_iso iso) as [_ ->]. destruct (is_iso iso') as [_ ->].
    rewrite hom_coprod_id //.
Qed.

Lemma hom_to_coprod_comp `{!HasCoproducts C} {a b c d e}
  (g1 : hom b a) (g2 : hom d b) (h1 : hom c a) (h2 : hom e c) :
  <<g1 ∘ g2 | h1 ∘ h2>> = <<g1 | h1>> ∘ (g2 +ₕ h2).
Proof.
  symmetry; apply coprd_hom_unique.
  - rewrite !comp_assoc -coprd_hom_commutes1 -!comp_assoc -coprd_hom_commutes1 //.
  - rewrite !comp_assoc -coprd_hom_commutes2 -!comp_assoc -coprd_hom_commutes2 //.
Qed.
Lemma hom_to_coprod_inj1 `{!HasCoproducts C} {a b c} (f : hom b a) (g : hom c a) :
  <<f | g>> ∘ inj1 _ = f.
Proof. rewrite /hom_coprod -coprd_hom_commutes1 //. Qed.
Lemma hom_to_coprod_inj2 `{!HasCoproducts C} {a b c} (f : hom b a) (g : hom c a) :
  <<f | g>> ∘ inj2 _ = g.
Proof. rewrite /hom_coprod -coprd_hom_commutes2 //. Qed.
Lemma hom_to_coprod_comp_left_id `{!HasCoproducts C} {a b d}
  (h1 : hom b a) (h2 : hom d b) : <<id a | h1 ∘ h2>> = <<id a | h1>> ∘ (id a +ₕ h2).
Proof. rewrite -hom_to_coprod_comp left_id //. Qed.
Lemma hom_to_coprod_comp_right_id `{!HasCoproducts C} {a b d}
  (h1 : hom b a) (h2 : hom d b) : <<h1 ∘ h2 | id a>> = <<h1 | id a>> ∘ (h2 +ₕ id a).
Proof. rewrite -hom_to_coprod_comp right_id //. Qed.
Lemma hom_to_coprod_split `{!HasCoproducts C} {a b c} (f : hom b a) (g : hom c a) :
  <<f | g>> = <<f | id a>> ∘ (id b +ₕ g).
Proof. rewrite -hom_to_coprod_comp left_id right_id //. Qed.
Lemma hom_to_coprod_split' `{!HasCoproducts C} {a b c} (f : hom b a) (g : hom c a) :
  <<f | g>> = <<id a | g>> ∘ (f +ₕ id c).
Proof. rewrite -hom_to_coprod_comp left_id right_id //. Qed.
Lemma hom_to_coprod_to_hom_coprod `{!HasCoproducts C} {a b c}
  (f : hom b a) (g : hom c a) :
  <<f | g>> = <<id a | id a>> ∘ (f +ₕ g).
Proof. rewrite -hom_to_coprod_comp !left_id //. Qed.
Lemma hom_to_coprod_comp_r `{!HasCoproducts C} {a b c d}
  (g1 : hom c b) (g2 : hom d b) (h : hom b a) :
  h ∘ <<g1 | g2>> =  <<h ∘ g1 | h ∘ g2>>.
Proof.
  eapply coprd_hom_unique'.
  - rewrite comp_assoc hom_to_coprod_inj1; reflexivity.
  - rewrite comp_assoc hom_to_coprod_inj2; reflexivity.
  - rewrite hom_to_coprod_inj1; reflexivity.
  - rewrite hom_to_coprod_inj2; reflexivity.
Qed.
Lemma hom_to_coprod_of_injs `{!HasCoproducts C} {a b c} (f : hom (b +ₒ c) a) :
  << f ∘ inj1 _ | f ∘ inj2 _ >> =  f.
Proof.
  eapply coprd_hom_unique'; [| |reflexivity|reflexivity].
  - rewrite hom_to_coprod_inj1 //.
  - rewrite hom_to_coprod_inj2 //.
Qed.

Definition init_plus_inj `{!HasInit C, !HasCoproducts C} (a : obj C)
  : hom a (a +ₒ 0ₒ) := inj1 _.
Definition init_plus_proj `{!HasInit C, !HasCoproducts C} (a : obj C)
  : hom (a +ₒ 0ₒ) a :=
  <<id _ | ¡ₕ _ >>.

Lemma hom_to_coprod_bangs `{!HasInit C, !HasCoproducts C} :
  <<id (0ₒ) | id (0ₒ)>> = init_plus_proj (0ₒ).
Proof. apply coprd_hom_unique; apply init_hom_unique'. Qed.

Lemma init_plus_inj_proj `{!HasInit C, !HasCoproducts C} a :
  init_plus_proj a ∘ init_plus_inj a = id a.
Proof. rewrite /init_plus_inj /init_plus_proj hom_to_coprod_inj1 //. Qed.

Lemma init_plus_proj_inj `{!HasInit C, !HasCoproducts C} a :
  init_plus_inj a ∘ init_plus_proj a = id (a +ₒ 0ₒ).
Proof.
  rewrite /init_plus_proj /init_plus_inj.
  eapply coprd_hom_unique'; [| |by rewrite left_id|by rewrite left_id].
  - rewrite comp_assoc hom_to_coprod_inj1 right_id //.
  - rewrite comp_assoc hom_to_coprod_inj2. apply init_hom_unique'.
Qed.

Definition init_plus_isomorphic `{!HasInit C, !HasCoproducts C} a : (a +ₒ 0ₒ) ≃ a :=
  MkIsoIc _ _ (MkIso (init_plus_proj_inj _) (init_plus_inj_proj _)).

Definition cocommutator `{!HasCoproducts C} (a b : obj C) : hom (a +ₒ b) (b +ₒ a) :=
  <<inj2 _ | inj1 _>>.

Lemma cocommutator_involutive `{!HasCoproducts C} a b
  : cocommutator a b ∘ cocommutator b a = id (b +ₒ a).
Proof.
  rewrite /cocommutator; eapply coprd_hom_unique';
    [| |by rewrite left_id|by rewrite left_id].
  - rewrite comp_assoc hom_to_coprod_inj1 hom_to_coprod_inj2 //.
  - rewrite comp_assoc hom_to_coprod_inj2 hom_to_coprod_inj1 //.
Qed.

Definition coproduct_comm `{!HasCoproducts C} a b : (a +ₒ b) ≃ (b +ₒ a) :=
  MkIsoIc _ _ (MkIso (cocommutator_involutive _ _) (cocommutator_involutive _ _)).

Lemma cocommute_hom_coprod `{!HasCoproducts C} {a b c d} (f : hom a c) (g : hom b d) :
  (f +ₕ g) ∘ cocommutator _ _ = cocommutator _ _ ∘ (g +ₕ f).
Proof.
  rewrite /cocommutator -hom_to_coprod_comp.
  eapply coprd_hom_unique';
    [| | rewrite hom_to_coprod_inj1 //|rewrite hom_to_coprod_inj2 //].
  - rewrite comp_assoc hom_to_coprod_inj1 hom_coprod_inj2 //.
  - rewrite comp_assoc hom_to_coprod_inj2 hom_coprod_inj1 //.
Qed.

Lemma cocommute_hom_to_coprod `{!HasCoproducts C} {a b c} (f : hom b a) (g : hom c a) :
  <<g | f>> ∘ cocommutator b c = <<f | g>>.
Proof.
  rewrite /cocommutator; eapply coprd_hom_unique.
  - rewrite comp_assoc hom_to_coprod_inj1 hom_to_coprod_inj2 //.
  - rewrite comp_assoc hom_to_coprod_inj2 hom_to_coprod_inj1 //.
Qed.

Lemma cocommute_init_plus_inj `{!HasInit C, !HasCoproducts C} a :
  (cocommutator a (0ₒ)) ∘ (init_plus_inj a) =  inj2 (coproduct_of (0ₒ) a).
Proof. rewrite /cocommutator /init_plus_inj hom_to_coprod_inj1 //. Qed.

Lemma inj_init_plus_proj `{!HasInit C, !HasCoproducts C} a :
  inj2 (coproduct_of (0ₒ) a) ∘ init_plus_proj a = cocommutator a (0ₒ).
Proof.
  rewrite /cocommutator /init_plus_proj; apply coprd_hom_unique.
  - rewrite !comp_assoc hom_to_coprod_inj1 right_id //.
  - rewrite !comp_assoc hom_to_coprod_inj2. apply init_hom_unique'.
Qed.

(* Coproducts in Setoid and PSh. *)

Global Program Instance type_has_coproducts : HasCoproducts Typ :=
  λ A B, MkCoprod (A + B)%type (λ ab, inl ab) (λ ab, inr ab)
           (λ d f g, λ ab, sum_rect _ (λ a, f a) (λ a, g a) ab) _ _ _.
Next Obligation.
  intros ?????.
  extensionality x; by simpl.
Qed.
Next Obligation.
  intros ?????.
  extensionality x; by simpl.
Qed.
Next Obligation.
  intros ?????.
  intros ? G H.
  extensionality x.
  destruct x as [a | b]; simpl; [rewrite G | rewrite H]; by simpl.
Qed.
Fail Next Obligation.

Program Definition func_coprod {C D} `{!HasCoproducts D}
  (F G : functor C D) : functor C D :=
  MkFunc (λ c, (F ₒ c) +ₒ (G ₒ c)) (λ _ _ f, (F ₕ f) +ₕ (G ₕ f)) _ _.
Solve All Obligations with
  repeat intros ?; rewrite /= ?h_map_comp ?h_map_id
  ?hom_coprod_comp ?hom_coprod_id //; solve_by_eq_rewrite.
Fail Next Obligation.

Program Definition func_inj1 {C D} `{!HasCoproducts D} (F G : functor C D)
  : natural F (func_coprod F G) :=
  MkNat (λ c, inj1 _) _.
Next Obligation. repeat intros ?; rewrite /= hom_coprod_inj1 //. Qed.
Fail Next Obligation.

Program Definition func_inj2  {C D} `{!HasCoproducts D} (F G : functor C D)
  : natural G (func_coprod F G) :=
  MkNat (λ c, inj2 _) _.
Next Obligation. repeat intros ?; rewrite /= hom_coprod_inj2 //. Qed.
Fail Next Obligation.

Program Definition func_coprd_hom  {C D} `{!HasCoproducts D}
  (F G H : functor C D)
  (p1 : natural F H) (p2 : natural G H) : natural (func_coprod F G) H :=
  MkNat (λ c, coprd_hom _ (p1 ₙ c) (p2 ₙ c)) _.
Next Obligation.
  repeat intros ?; rewrite /=; eapply coprd_hom_unique';
    [ rewrite comp_assoc -coprd_hom_commutes1 //
    | rewrite comp_assoc -coprd_hom_commutes2 //| |].
  - rewrite comp_assoc -coprd_hom_commutes1
            -comp_assoc -coprd_hom_commutes1 naturality //.
  - rewrite comp_assoc -coprd_hom_commutes2
            -comp_assoc -coprd_hom_commutes2 naturality //.
Qed.
Fail Next Obligation.

Program Definition func_cat_has_coproducts C D `{!HasCoproducts D}
  : HasCoproducts (FuncCat C D) :=
  λ F G, MkCoprod (func_coprod F G) (func_inj1 F G) (func_inj2 F G)
           (func_coprd_hom F G) _ _ _.
Next Obligation.
  intros.
  apply natural_equiv_unpack; intros x; simpl.
  rewrite -coprd_hom_commutes1 //.
Qed.
Next Obligation.
  intros.
  apply natural_equiv_unpack; intros x; simpl.
  rewrite -coprd_hom_commutes2 //.
Qed.
Next Obligation.
  intros ????????? Hcm1 Hcm2.
  apply natural_equiv_unpack; intros c; simpl.
  rewrite /=; apply coprd_hom_unique; by [rewrite Hcm1|rewrite Hcm2].
Qed.

Global Instance psh_has_coproducts C : HasCoproducts (PSh C) :=
  @func_cat_has_coproducts (C ᵒᵖ) Typ _.

Program Definition distributor_left {C} `{!HasCoproducts C, !HasProducts C}
  {a b c}
  : hom ((a ×ₒ c) +ₒ (b ×ₒ c)) ((a +ₒ b) ×ₒ c)
  := << inj1 _ ×ₕ id _ | inj2 _ ×ₕ id _ >>.

Class Distributive C `{!HasCoproducts C, !HasProducts C}
  := MkDistributive {
         distributor_right (a b c : obj C)
         : hom ((a +ₒ b) ×ₒ c) ((a ×ₒ c) +ₒ (b ×ₒ c));
         distributor_iso {a b c : obj C}
         : isomorphism distributor_left (distributor_right a b c);
       }.

Program Definition distributor_right_setoid (a b c : obj Typ)
  : hom (C := Typ) ((a +ₒ b) ×ₒ c) ((a ×ₒ c) +ₒ (b ×ₒ c))
  := λ x, (sum_rect (λ _, (a * c + b * c)%type)
             (λ y, inl (y, x.2))
             (λ y, inr (y, x.2)) x.1).

Lemma distributor_iso_setoid (a b c : obj Typ)
  : isomorphism distributor_left (distributor_right_setoid a b c).
Proof.
  split.
  - extensionality x; simpl.
    destruct x as [[x1 x2] | [x1 x2]]; by simpl.
  - extensionality x; simpl.
    destruct x as [[x1 | x1] x2]; by simpl.
Qed.

Global Program Instance DistributiveSetoid : Distributive Typ
  := MkDistributive Typ _ _ distributor_right_setoid _.
Next Obligation.
  intros; apply distributor_iso_setoid.
Qed.

Section distributor_psh.
  Context {C : category}.

  Program Definition distributor_right_psh (a b c : obj (PSh C))
    : hom (C := PSh C) ((a +ₒ b) ×ₒ c) ((a ×ₒ c) +ₒ (b ×ₒ c))
    := MkNat (λ x, distributor_right (a ₒ x) (b ₒ x) (c ₒ x)) _.
  Next Obligation.
    intros; simpl.
    extensionality x.
    destruct x as [x1 x2]; simpl.
    destruct x1 as [x1 | x1]; reflexivity.
  Qed.

  Lemma distributor_iso_psh (a b c : obj (PSh C))
    : isomorphism distributor_left (distributor_right_psh a b c).
  Proof.
    split.
    - apply natural_equiv_unpack; intros x; simpl.
      extensionality y.
      destruct y as [[y1 y2] | [y1 y2]]; done.
    - apply natural_equiv_unpack; intros x; simpl.
      extensionality y.
      destruct y as [[y1 | y1] y2]; done.
  Qed.

  Global Program Instance DistributivePSh : Distributive (PSh C)
    := MkDistributive (PSh C) _ _ distributor_right_psh _.
  Next Obligation.
    intros; apply distributor_iso_psh.
  Qed.

End distributor_psh.
