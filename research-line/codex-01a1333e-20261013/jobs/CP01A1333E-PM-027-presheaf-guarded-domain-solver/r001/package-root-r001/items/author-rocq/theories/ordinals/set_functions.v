(** This file has been adapted from Dominik Kirst's Bachelor Thesis
    "Formalised Set Theory: Well-Orderings and the Axiom of Choice",
    see https://www.ps.uni-saarland.de/~kirst/bachelor.php
*)

(** initial import of the development **)
From SynthDom.ordinals Require Import set_model set_sets.

Set Universe Polymorphism.
Set Universe Minimization ToSet.

Section set_functions.
Local Open Scope zf_scope.

Implicit Types (a b c A B C R S T f: set).

(** ** Relations *)

Definition relation R A B := R ⊆ product A B.

Definition dom R := replacement_set R (λ p, pi1 p).
Definition ran R := replacement_set R (λ p, pi2 p).
Definition field R := bunion_set (dom R) (ran R).

Definition symmetric R := ∀ a b, (a,b) ∈ R → (b,a) ∈ R.
Definition asymmetric R := ∀ a b, (a,b) ∈ R → (b,a) ∉ R.
Definition antisymmetric R := ∀ a b, (a,b) ∈ R → (b,a) ∈ R → a = b.
Definition transitive R := ∀ a b c, (a,b) ∈ R → (b,c) ∈ R → (a,c) ∈ R.
Definition reflexive R A := ∀ a, a ∈ A → (a,a) ∈ R.
Definition irreflexive R := ∀ a, (a,a) ∉ R.
Definition linear R A := ∀ a b, a ∈ A → b ∈ A → (a,b) ∈ R ∨ (b,a) ∈ R ∨ a = b.

Definition equivalence R A :=
  relation R A A ∧ symmetric R ∧ reflexive R A ∧ transitive R.

Definition lordering R A :=
  relation R A A ∧ asymmetric R ∧ transitive R ∧ linear R A.

Definition least R A x := x ∈ A ∧ ∀ y, y ∈ A → (x,y) ∈ R ∨ y = x.
Definition wfounded R A := ∀ M, M ⊆ A → M <> empty → ∃ x, least R M x.
Definition wordering R A := lordering R A ∧ wfounded R A.
Definition WO A := ∃ R, wordering R A.


Lemma rel_pair R A B p a b: relation R A B → p ∈ R → a = pi1 p → b = pi2 p → p = (a,b).
Proof.
intros I J. specialize (I p J). now apply (opair_pi A B).
Qed.

Lemma rel_pi f A B p: relation f A B → p ∈ f → (pi1 p, pi2 p) ∈ f.
Proof.
intros I J. now rewrite <- (@rel_pair f A B p (pi1 p) (pi2 p) I J) at 1.
Qed.

Lemma rel_pair1 R A B a b: relation R A B → (a,b) ∈ R → a ∈ A.
Proof.
intros I J. specialize (I (a,b) J). now apply product_opair in I.
Qed.

Lemma rel_pair2 R A B a b: relation R A B → (a,b) ∈ R → b ∈ B.
Proof.
intros I J. specialize (I (a,b) J). now apply product_opair in I.
Qed.

Lemma rel_pi1 R A B p: relation R A B → p ∈ R → pi1 p ∈ A.
Proof.
intros I J. specialize (I p J). now apply product_pi1 in I.
Qed.

Lemma rel_pi2 R A B p: relation R A B → p ∈ R → pi2 p ∈ B.
Proof.
intros I J. specialize (I p J). now apply product_pi2 in I.
Qed.

Lemma asym_irref R: asymmetric R → antisymmetric R ∧ irreflexive R.
Proof.
intros I. split.
- intros a b I1 I2. exfalso. now apply (I a b).
- intros a J. now apply (I a a).
Qed.

Lemma irref_asym R: antisymmetric R ∧ irreflexive R → asymmetric R.
Proof.
intros [I1 I2] a b J1 J2.
specialize (I1 a b J1 J2).
subst b. now apply (I2 a).
Qed.

Lemma trans_asym R: transitive R ∧ irreflexive R → asymmetric R.
Proof.
intros [I1 I2] a b J1 J2.
specialize (I1 a b a J1 J2).
now apply (I2 a).
Qed.

Lemma wo_irr R A: wordering R A → irreflexive R.
Proof.
intros I. apply asym_irref. apply I.
Qed.

Lemma wordering_empty: wordering empty empty.
Proof.
repeat split.
- intros p I. contradiction (zf_existence p I).
- intros x y I. contradiction (zf_existence (x,y) I).
- intros x y z I. contradiction (zf_existence (x,y) I).
- intros x y I. contradiction (zf_existence x I).
- intros M I J. exfalso. apply J. apply zf_extensionality; eauto using empty_subs.
Qed.



(** ** Functions *)

Definition total f A B := ∀ x, x ∈ A → ∃ y, y ∈ B ∧ (x,y) ∈ f.
Definition functional f := ∀ a b b', (a,b) ∈ f → (a,b') ∈ f → b' = b.

Definition surjective f A B := ∀ y, y ∈ B → ∃ x, x ∈ A ∧ (x,y) ∈ f.
Definition injective f := ∀ a a' b, (a,b) ∈ f → (a',b) ∈ f → a = a'.
Definition bijective f A B := surjective f A B ∧ injective f.

Definition function f A B := relation f A B ∧ total f A B ∧ functional f.

Definition surjection f A B := function f A B ∧ surjective f A B.
Definition injection f A B := function f A B ∧ injective f.
Definition bijection f A B := function f A B ∧ surjective f A B ∧ injective f.
Definition equi A B := ∃ f, bijection f A B.


Lemma fun_pi f A B p: function f A B → p ∈ f → (pi1 p, pi2 p) ∈ f.
Proof.
intros [I I'] J. eauto using rel_pi.
Qed.

Lemma fun_pair f A B p: function f A B → p ∈ f → p = (pi1 p, pi2 p).
Proof.
intros [I I'] J. specialize (I p J). now apply (opair_pi A B (pi1 p) (pi2 p)) in I.
Qed.

Lemma fun_product f A B p: function f A B → p ∈ f → p ∈ product A B.
Proof.
intros [I _] J. auto.
Qed.

Lemma fun_pi1 f A B p: function f A B → p ∈ f → pi1 p ∈ A.
Proof.
intros I J. apply (product_pi1 A B). apply (@fun_product f); assumption.
Qed.

Lemma fun_pi2 f A B p: function f A B → p ∈ f → pi2 p ∈ B.
Proof.
intros I J. apply (product_pi2 A B). apply (fun_product f); assumption.
Qed.

Lemma fun_pair1 f A B a b: function f A B → (a,b) ∈ f → a ∈ A.
Proof.
intros FF PE. apply (rel_pair1 f A B a b); trivial. apply FF.
Qed.

Lemma fun_pair2 f A B a b: function f A B → (a,b) ∈ f → b ∈ B.
Proof.
intros FF PE. apply (rel_pair2 f A B a b); trivial. apply FF.
Qed.

Lemma fun_el1 f A B a b: function f A B → (a,b) ∈ f → a ∈ A.
Proof.
intros [I _] J. specialize (I (a,b) J). apply product_opair in I as [I _]. assumption.
Qed.

Lemma fun_el2 f A B a b: function f A B → (a,b) ∈ f → b ∈ B.
Proof.
intros [I _] J. specialize (I (a,b) J). apply product_opair in I as [_ I]. assumption.
Qed.

Lemma fun_el_dom f a b: (a,b) ∈ f → a ∈ dom f.
Proof.
intros I. apply zf_replacement.
exists (a,b). rewrite pi1_cor. split; trivial.
Qed.

Lemma fun_el_ran f a b: (a,b) ∈ f → b ∈ ran f.
Proof.
intros I. apply zf_replacement.
exists (a,b). rewrite pi2_cor. split; trivial.
Qed.

Lemma sur_ran1 f A B: relation f A B → surjective f A B → ran f = B.
Proof.
intros H I. apply zf_extensionality; split; intros y Y.
- apply zf_replacement in Y as [p [P1 P2]].
  subst y. now apply (rel_pi2 f A B).
- apply zf_replacement. destruct (I y Y) as [x [X1 X2]].
  exists (x,y). rewrite pi2_cor. split; trivial.
Qed.

Lemma sur_ran2 f A B: relation f A B → ran f = B → surjective f A B.
Proof.
intros H I y Y. apply extenE in I as [_ I]. specialize (I y Y).
apply zf_replacement in I as [p [P1 P2]]. subst y.
exists (pi1 p). split; eauto using rel_pi1.
eauto using rel_pi.
Qed.

Lemma sur_ran f A B: relation f A B → (surjective f A B ↔ ran f = B).
Proof.
intros H. split; intros I.
- now apply (sur_ran1 f A B).
- now apply (sur_ran2 f A B).
Qed.

Lemma fun_ran_subs f A B: function f A B → ran f ⊆ B.
Proof.
intros I y Y. apply zf_replacement in Y as [p [P1 P2]].
subst y. now apply (fun_pi2 f A B).
Qed.

Lemma tot_dom1 f A B: relation f A B → total f A B → dom f = A.
Proof.
intros H I. apply zf_extensionality; split; intros x X.
- apply zf_replacement in X as [p [P1 P2]].
  subst x. now apply (rel_pi1 f A B).
- apply zf_replacement. destruct (I x X) as [y [Y1 Y2]].
  exists (x,y). rewrite pi1_cor. split; trivial.
Qed.

Lemma tot_dom2 f A B: relation f A B → dom f = A → total f A B.
intros H I x X. apply extenE in I as [_ I]. specialize (I x X).
apply zf_replacement in I as [p [P1 P2]]. subst x.
exists (pi2 p). split; eauto using rel_pi2.
eauto using rel_pi.
Qed.

Lemma tot_dom f A B: relation f A B → (total f A B ↔ dom f = A).
Proof.
intros H. split; intros I.
- now apply (tot_dom1 f A B).
- now apply (tot_dom2 f A B).
Qed.

Lemma bijec_empty f A: bijection f A empty → A = empty.
Proof.
intros [[R[T F]][S I]]. apply zf_extensionality; split; eauto using empty_subs.
intros x J. specialize (T x J). destruct T as [y [T _]].
contradiction (zf_existence y T).
Qed.

Lemma fun_step_rel f A B x y: function f A B → x ∉ A → y ∈ B →
  relation (bunion_set f (singleton (x,y))) (bunion_set A (singleton x)) B.
Proof.
intros [FR[FT FF]] XA YB p P. apply bunionE in P as [P|P].
- apply (product_subs1 (bunion_set A (singleton x)) A).
+ apply bunion_subs1. apply subseq.
+ now apply FR.
- apply single_el in P. subst p.
  apply product_opair. split; trivial.
  apply bunionI2. now apply single_el.
Qed.

Lemma fun_step_tot f A B x y: function f A B → x ∉ A → y ∈ B →
  total (bunion_set f (singleton (x,y))) (bunion_set A (singleton x)) B.
Proof.
intros [FR[FT FF]] XA YB a AE. apply bunionE in AE as [AE|AE].
- destruct (FT a AE) as [b [BE1 BE2]].
  exists b. split; trivial.
  now apply bunionI1.
- apply single_el in AE. subst a.
  exists y. split; trivial.
  apply bunionI2. now apply single_el.
Qed.

Lemma fun_step_fun f A B x y: function f A B → x ∉ A → y ∈ B →
  functional (bunion_set f (singleton (x,y))).
Proof.
intros [FR[FT FF]] XA YB a b b' I1 I2.
apply bunionE in I1 as [I1|I1]; apply bunionE in I2 as [I2|I2].
- now apply (FF a b b').
- apply single_el in I2. apply opair_eq in I2 as [I2 I3]. subst.
  exfalso. apply XA. apply (fun_pair1 f A B x b); trivial. repeat split; assumption.
- apply single_el in I1. apply opair_eq in I1 as [I1 I3]. subst.
  exfalso. apply XA. apply (fun_pair1 f A B x b'); trivial. repeat split; assumption.
- apply single_el in I1. apply single_el in I2.
  apply opair_eq in I1 as [_ I1].
  apply opair_eq in I2 as [_ I2].
  congruence.
Qed.

Lemma fun_step f A B x y: function f A B → x ∉ A → y ∈ B →
  function (bunion_set f (singleton (x,y))) (bunion_set A (singleton x)) B.
Proof.
intros FF XA YB. repeat split.
- now apply fun_step_rel.
- now apply fun_step_tot.
- eapply fun_step_fun; try apply FF; assumption.
Qed.

Lemma fun_expand f A B B': function f A B → B ⊆ B' → function f A B'.
Proof.
intros [I1[I2 I3]] J. repeat split.
- intros p P. specialize (I1 p P). now apply (product_subs2 A B B').
- intros x X. destruct (I2 x X) as [y[Y1 Y2]].
  exists y. split; auto.
- assumption.
Qed.



(** ** Application *)

Definition xgraph f x := specification_set f (λ p, pi1 p = x).
Definition ximages f x := replacement_set (xgraph f x) (λ p, pi2 p).
Definition app f x := union_set (ximages f x).
Notation "f '[' x ']'" := (app f x) (at level 10).


Lemma xgraph_cor f x y: (x,y) ∈ f → (x,y) ∈ xgraph f x.
Proof.
intros I. apply zf_specification. split; eauto using pi1_cor.
Qed.

Lemma im_cor f x y A B: function f A B → (x,y) ∈ f → ximages f x = singleton y.
Proof.
intros [I [I' I'']] J. apply zf_extensionality; split; intros y' H.
- apply single_el. apply (I'' x y y').
+ assumption.
+ apply zf_replacement in H as [p [H H']]. apply zf_specification in H as [H H''].
  assert (P: p = (x,y')) by eauto using rel_pair. now rewrite <- P.
- apply single_el in H. rewrite H. apply zf_replacement. exists (x,y). split.
+ now apply xgraph_cor.
+ now rewrite pi2_cor.
Qed.

Lemma app_cor f x A B: function f A B → x ∈ A → (x,f[x]) ∈ f ∧ f[x] ∈ B.
Proof.
intros [I [I' I'']] J.
assert (F: function f A B) by (repeat split; assumption).
destruct (I' x J) as [y [J'' J']]. cut (y = f[x]).
- intros H. subst y. now split.
- unfold app. rewrite (im_cor f x y A B F J'). now rewrite single_union_set.
Qed.

Lemma app_cor1 f x A B: function f A B → x ∈ A → (x,f[x]) ∈ f.
Proof.
intros I J. specialize (app_cor f x A B I J). now intros [H H'].
Qed.

Lemma app_cor2 f x A B: function f A B → x ∈ A → f[x] ∈ B.
Proof.
intros I J. specialize (app_cor f x A B I J). now intros [H H'].
Qed.

Lemma app_eq f x y A B: function f A B → (x,y) ∈ f → y = f[x].
Proof.
intros I J. specialize (im_cor f x y A B I J). intros H.
unfold app. rewrite H. now rewrite single_union_set.
Qed.

Lemma app_sur f A B y: surjection f A B → y ∈ B → ∃ x, x ∈ A ∧ y = f[x].
Proof.
intros [I I'] Y. destruct (I' y Y) as [x [J I'']].
exists x. split; try assumption. now apply (app_eq f x y A B).
Qed.

Lemma app_inj f A B x x': injection f A B → x ∈ A → x' ∈ A → f[x] = f[x'] → x = x'.
Proof.
intros [I I'] X X' J. specialize (I' x x' (f[x])). apply I'.
- eauto using app_cor1.
- rewrite J. eauto using app_cor1.
Qed.

Lemma fun_app f A B p: function f A B → p ∈ f → pi2 p = f[pi1 p].
Proof.
intros I J. apply (app_eq f (pi1 p) (pi2 p) A B); auto. now apply (fun_pi f A B).
Qed.

Lemma fun_appel f A B p: function f A B → p ∈ f → p = (pi1 p, f[pi1 p]).
Proof.
intros I J. rewrite <- (fun_app f A B); trivial.
now apply (fun_pair f A B).
Qed.

Lemma bij_app f A B p: bijection f A B → p ∈ f → pi2 p = f[pi1 p].
Proof.
intros [I] J. now apply (fun_app f A B).
Qed.

Lemma fun_shrink A B B' f: function f A B → (∀ x, x ∈ A → f[x] ∈ B') → function f A B'.
Proof.
intros FF BB. repeat split.
- intros p P.
  specialize (fun_appel f A B p FF P).
  intros PP. rewrite PP. rewrite PP in P. apply product_opair.
  assert (P1: pi1 p ∈ A) by eauto using fun_pair1.
  split; trivial. now apply BB.
- assert (FT: total f A B) by apply FF.
  intros x X. destruct (FT x X) as [y [Y1 Y2]].
  exists y. split; trivial. rewrite (app_eq f x y A B); trivial.
  now apply BB.
- apply FF.
Qed.



(** ** Restriction *)

Definition restriction f A := specification_set f (λ p, pi1 p ∈ A).
Notation "f '|*' A" := (restriction f A) (at level 8).

Definition rel_restriction R A := specification_set R (λ p, p ∈ product A A).
Notation "R '|>' A" := (rel_restriction R A) (at level 9).


Lemma res_functional f A: functional f → functional f|*A.
Proof.
intros I x y y'. intros P1 P2.
apply spec_subs in P1. apply spec_subs in P2.
now apply (I x y y').
Qed.

Lemma res_injective f A: injective f → injective f|*A.
Proof.
intros I x x' y. intros P1 P2.
apply spec_subs in P1. apply spec_subs in P2.
now apply (I x x' y).
Qed.

Lemma res_fun f A B A': function f A B → A' ⊆ A → function (f|*A') A' B.
Proof.
intros [I [I' I'']]. repeat split.
- intros p J. apply zf_specification in J as [J J']. apply product_el.
  exists (pi1 p), (pi2 p). repeat split; eauto using opair_pi, product_pi2.
- intros x J. specialize (I' x (H x J)). destruct I' as [y [X Y]].
  exists y. split; eauto. apply zf_specification. split; eauto. now rewrite pi1_cor.
- now apply res_functional.
Qed.

Lemma res_el f A B A' x y: function f A B → A' ⊆ A → (x,y) ∈ f |* A' → x ∈ A'.
Proof.
intros I H. specialize (res_fun f A B A' I H). intros J J'.
now apply (fun_el1 (f|*A') A' B x y).
Qed.

Lemma res_eq f A B A' x: function f A B → A' ⊆ A → x ∈ A' → f [x] = f|*A' [x].
Proof.
intros I I' I''. specialize (res_fun f A B A' I I'). intros J.
specialize (app_cor1 f x A B I (I' x I'')). intros J'.
specialize (app_cor1 f|*A' x A' B J I''). intros J''.
apply spec_subs in J''. destruct I as [I [H H']]. symmetry. now apply (H' x (f[x]) (f |* A' [x])).
Qed.

Lemma res_opair f A B A' a b: function f A B → A' ⊆ A → (a,b) ∈ f → a ∈ A' → (a,b) ∈ f |* A'.
Proof.
intros I1 I2 I3 I4. apply zf_specification. split; eauto. now rewrite pi1_cor.
Qed.

Lemma res_res f A B: A ⊆ B → (f|*B)|*A = f|* A.
Proof.
intros I. apply zf_extensionality; split; intros p P;
apply zf_specification in P as [P1 P2]; apply zf_specification.
- apply zf_specification in P1 as [P1 _]. split; assumption.
- split; trivial. apply zf_specification. split; auto.
Qed.

Lemma relres_rel R A': relation (R|>A') A' A'.
Proof.
intros p P. apply zf_specification in P as [_ P]. assumption.
Qed.

Lemma relres_asym R A': asymmetric R → asymmetric (R|>A').
Proof.
intros I a b J1 J2.
apply zf_specification in J1 as [J1 _].
apply zf_specification in J2 as [J2 _].
now apply (I a b).
Qed.

Lemma relres_trans R A': transitive R → transitive (R|>A').
Proof.
intros I a b c J1 J2.
apply zf_specification in J1 as [J1 J1'].
apply zf_specification in J2 as [J2 J2'].
apply zf_specification. split.
+ now apply (I a b c).
+ apply product_opair in J1' as [J1' _].
  apply product_opair in J2' as [_ J2'].
  apply product_opair. split; assumption.
Qed.

Lemma relres_linear R A A': linear R A → A' ⊆ A → linear (R|>A') A'.
Proof.
intros I J a b J1 J2. destruct (I a b) as [H|[H|H]]; auto.
- left. apply zf_specification. split; trivial.
  apply product_opair. split; assumption.
- right. left. apply zf_specification. split; trivial.
  apply product_opair. split; assumption.
Qed.

Lemma relres_wf R A A': wfounded R A → A' ⊆ A → wfounded (R|>A') A'.
Proof.
intros I J B B1 B2. destruct (I B) as [x [H1 H2]].
- now apply (subs_trans) with (B:=A').
- assumption.
- exists x. split; trivial.
  intros y Y. destruct (H2 y Y) as [H|H].
+ left. apply zf_specification. split; trivial.
  apply product_opair. split; auto.
+ right. assumption.
Qed.

Lemma worder_subs R A A': wordering R A → A' ⊆ A → wordering (R|>A') A'.
Proof.
intros WOR S. repeat split.
- apply relres_rel.
- apply relres_asym. apply WOR.
- apply relres_trans. apply WOR.
- apply (relres_linear R A); trivial. apply WOR.
- apply (relres_wf R A); trivial. apply WOR.
Qed.

Lemma equi_empty A B: equi A B → A <> empty → B <> empty.
Proof.
intros [f [I H]] I'. apply empty_el in I' as [x I']. apply empty_el.
exists (f[x]). eauto using app_cor2.
Qed.



(** ** Image *)

Definition image f A := replacement_set f|* A (λ p, pi2 p).
Notation "f '[(' A ')]'" := (image f A) (at level 10).


Lemma image_subs f A B A': function f A B → image f A' ⊆ B.
Proof.
intros I y H. apply zf_replacement in H as [p [H H']]. rewrite H'.
apply zf_specification in H as [H _]. now apply (fun_pi2 f A).
Qed.

Lemma image_empty f A B A': function f A B → A' ⊆ A → A' <> empty → image f A' <> empty.
Proof.
intros I I' I''. apply empty_el in I'' as [x I'']. apply empty_el.
exists (f[x]). apply zf_replacement. exists (x,f[x]). split.
- rewrite (res_eq f A B A'); eauto using app_cor1, res_fun.
- now rewrite pi2_cor.
Qed.

Lemma im_el f A B A' x y: injection f A B → A' ⊆ A → (x,y) ∈ f → y ∈ image f A' → x ∈ A'.
Proof.
intros [I I'] I'' J J'. apply zf_replacement in J' as [p [J' J'']]. subst y.
specialize (I' x (pi1 p) (pi2 p) J). rewrite I'.
- destruct (res_fun f A B A' I I'') as [H H']. specialize (H p J'). eauto using product_pi1.
- apply spec_subs in J'. eauto using fun_pi.
Qed.

Lemma image_el f A B A' x: function f A B → A' ⊆ A → x ∈ A' → f[x] ∈ image f A'.
Proof.
intros I I' I''. apply zf_replacement. exists (x,f[x]). split.
- specialize (res_fun f A B A' I I'). intros H. rewrite (res_eq f A B A'); eauto using app_cor1.
- now rewrite pi2_cor.
Qed.

Lemma image_res f A B A': function f A B → A' ⊆ A → f|*A'[(A')] = f[(A')].
Proof.
intros I J. apply zf_extensionality; split; intros y Y;
apply zf_replacement; apply zf_replacement in Y as [p [P1 P2]];
exists p; split; auto.
+ now apply zf_specification in P1 as [].
+ apply zf_specification. split; auto. now apply zf_specification in P1 as [].
Qed.

Lemma image_rel f A B A': bijection f A B → A' ⊆ A → relation (f|*A') A' (f[(A')]).
Proof.
intros [[re [to fu]] [I2 I3]] J.
assert (F: function f A B) by (repeat split; eauto).
intros p I. apply zf_specification in I as [J1 J2]. apply product_el. exists (pi1 p), (f[pi1 p]).
assert (H: (pi1 p, pi2 p) ∈ f) by eauto using fun_pi. repeat split; eauto.
- apply zf_replacement. exists p. split; first by apply zf_specification.
  symmetry. apply (app_eq f (pi1 p) (pi2 p) A B); eauto.
- specialize (re p J1). apply (opair_pi A B (pi1 p) (f[pi1 p])) in re; eauto.
  apply (fu (pi1 p) (pi2 p) (f[pi1 p])); eauto. apply (app_cor1 f (pi1 p) A B); eauto.
Qed.

Lemma image_tot f A B A': bijection f A B → A' ⊆ A → total (f|*A') A' (f[(A')]).
Proof.
intros [[re [to fu]] [I2 I3]] J.
assert (F: function f A B) by (repeat split; eauto).
intros x I. specialize (to x (J x I)). destruct to as [y [H1 H2]]. exists y. split.
- apply zf_replacement. exists (x,y). split; first by eauto using res_opair. now rewrite pi2_cor.
- eauto using res_opair.
Qed.

Lemma image_sur f A B A': bijection f A B → A' ⊆ A → surjective (f|*A') A' (f[(A')]).
Proof.
intros [F [I2 I3]] J.
intros y H. apply zf_replacement in H as [p [H1 H2]]. exists (pi1 p). split.
+ apply zf_specification in H1 as [_ H]. assumption.
+ subst y. eauto using fun_pi, res_fun.
Qed.

Lemma image_bijection f A B A': bijection f A B → A' ⊆ A → bijection (f|*A') A' (f[(A')]).
Proof.
intros I1 I2. repeat split.
- now apply (image_rel f A B).
- now apply (image_tot f A B).
- apply res_functional. apply I1.
- now apply (image_sur f A B).
- apply res_injective. apply I1.
Qed.

Lemma image_bij f A B A': bijection f A B → A' ⊆ A → bijection (f|*A') A' (f|*A'[(A')]).
Proof.
intros I1 I2. cut (f|*A'[(A')] = f[(A')]).
- intros I. rewrite I. apply (image_bijection f A B); assumption.
- apply (image_res f A B); trivial; apply I1.
Qed.

Lemma fun_ran f A B: function f A B → function f A (ran f).
Proof.
intros [I [I' I'']]. repeat split.
- intros p J. specialize (I p J). apply product_el in I as [a [b [H [H' H'']]]]. subst p.
  apply product_el. exists a, b. repeat split; eauto. apply zf_replacement.
  exists (a,b). rewrite pi2_cor. now split.
- intros x J. destruct (I' x J) as [y [H H']]. exists y. split; eauto.
  apply zf_replacement. exists (x,y). rewrite pi2_cor. now split.
- assumption.
Qed.

Lemma image_ran f A B A': A' ⊆ A → function f A B → image f A' = ran (f|*A').
Proof.
intros I [I' I'']. assert (F: function f A B); first by split; eauto.
apply zf_extensionality; split; intros y J.
- apply zf_replacement. apply zf_replacement in J as [p [J J']]. exists p. now split.
- apply zf_replacement. apply zf_replacement in J as [p [J' J'']]. exists p. now split.
Qed.

Lemma equi_subs A B A': equi A B → A' ⊆ A → ∃ B', B' ⊆ B ∧ equi A' B'.
Proof.
intros [f FF] J. exists (image f A'). split.
- apply (image_subs f A); trivial. apply FF.
- exists (f|*A'). now apply (image_bijection f A B).
Qed.



(** ** Inverse *)

Definition inverse f := replacement_set f (λ p, (pi2 p, pi1 p)).
Notation "f ^" := (inverse f) (at level 5).


Lemma inv_el1 f x y: (x,y) ∈ f → (y,x) ∈ f^.
Proof.
intros I. apply zf_replacement. exists (x,y). split; eauto. now rewrite pi1_cor pi2_cor.
Qed.

Lemma inv_el2 f x y A B: relation f A B → (y,x) ∈ f^ → (x,y) ∈ f.
Proof.
intros Rel I. apply zf_replacement in I as [p [I I']]. apply opair_eq in I' as [H H'].
assert (J: p = (x,y)) by eauto using opair_pi. now rewrite <- J at 1.
Qed.

Lemma inv_bij f A B: bijection f A B → bijection f^ B A.
Proof.
intros [[I [J H]] [I' I'']]. repeat split.
- intros p H'. apply zf_replacement in H' as [p' [H' H'']]. apply product_el.
  exists (pi2 p'), (pi1 p'). repeat split; [eapply product_pi2; eauto | eapply product_pi1; eauto | eauto].
- intros x H'. specialize (I' x H'). destruct I' as [y [I' H'']].
  exists y. split; eauto. now apply inv_el1.
- intros x y y'. intros H' H''. symmetry. apply (I'' y y' x); eauto using inv_el2.
- intros x H'. specialize (J x H'). destruct J as [y [J J']]. eauto using inv_el1.
- intros x x' y J' J''. symmetry. apply (H y x x'); eauto using inv_el2.
Qed.

Lemma inv_el f A B y: bijection f A B → y ∈ B → f^[y] ∈ A.
Proof.
intros I J. apply (app_cor2 f^ y B); eauto.
apply inv_bij in I as [I _]. assumption.
Qed.

Lemma inv_element f A B y: bijection f A B → y ∈ B → (f^[y], y) ∈ f.
Proof.
intros I J. apply (inv_el2 f (f^[y]) y A B).
- apply I.
- apply (app_cor1 f^ y B A); auto.
  apply inv_bij in I. apply I.
Qed.

Lemma inv_idem f A B: bijection f A B → f = f^^.
Proof.
intros [fct[sur inj]]. apply zf_extensionality; split; intros p I.
- apply zf_replacement. exists (pi2 p, pi1 p). rewrite pi1_cor pi2_cor.
  setoid_rewrite (fun_pair f A B p) at 3; eauto. split; eauto.
  apply zf_replacement. exists p. split; eauto.
- apply zf_replacement in I as [q[I J1]].
  apply zf_replacement in I as [r[I J2]].
  rewrite J2 in J1. rewrite pi1_cor pi2_cor in J1.
  rewrite J1. apply (fun_pair f A B r) in fct; eauto.
  now rewrite <- fct.
Qed.

Lemma inv1 f A B x: bijection f A B → x ∈ A → x = f^[f[x]].
Proof.
intros I1 I2. apply (app_eq f^ (f[x]) x B A).
- destruct (inv_bij f A B) as [J _]; eauto.
- apply inv_el1. apply (app_cor1 f x A B).
+ now destruct I1.
+ assumption.
Qed.

Lemma inv2 f A B y: bijection f A B → y ∈ B → y = f[f^[y]].
Proof.
intros I1 I2. setoid_rewrite (inv_idem f A B) at 1.
- apply (inv1 f^ B A y).
+ apply inv_bij. assumption.
+ assumption.
- assumption.
Qed.

Lemma equi_com A B: equi A B → equi B A.
Proof.
intros [f I]. exists (f^). now apply inv_bij.
Qed.



(** ** Composition *)

Definition comp f g :=
  specification_set (product (dom g) (ran f)) (λ p, ∃ b, (pi1 p, b) ∈ g ∧ (b, pi2 p) ∈ f).


Lemma comp_rel f g A B C: function f B C → function g A B → relation (comp f g) A C.
Proof.
intros [FR[FT FF]] [GR[GT GF]].
apply subs_trans with (B:=product (dom g) (ran f)); eauto using spec_subs.
destruct (tot_dom g A B GR) as [H _]. rewrite (H GT).
apply product_subs2. apply fun_ran_subs with (A:=B). repeat split; assumption.
Qed.

Lemma comp_tot f g A B C: function f B C → function g A B → total (comp f g) A C.
Proof.
intros [FR[FT FF]] [GR[GT GF]] a I1.
destruct (GT a I1) as [b [I2 I3]]. destruct (FT b I2) as [c [I4 I5]].
exists c. split; auto. apply zf_specification. split.
- apply product_opair. split; eauto using fun_el_dom, fun_el_ran.
- rewrite pi1_cor pi2_cor. exists b. split; assumption.
Qed.

Lemma comp_fct f g A B C: function f B C → function g A B → functional (comp f g).
Proof.
intros [FR[FT FF]] [GR[GT GF]] a c c' I1 I2.
apply zf_specification in I1 as [I1[b [GB FB]]].
apply zf_specification in I2 as [I2[b' [GB' FB']]].
rewrite pi1_cor in GB; rewrite pi1_cor in GB'.
rewrite pi2_cor in FB; rewrite pi2_cor in FB'.
specialize (GF a b b' GB GB'). subst b'.
specialize (FF b c c' FB FB'). assumption.
Qed.

Lemma comp_fun f g A B C: function f B C → function g A B → function (comp f g) A C.
Proof.
intros FF FG. repeat split; eauto using comp_rel, comp_tot, comp_fct.
Qed.

Lemma comp_app A B C f g x: bijection f B C → bijection g A B → x ∈ A → (comp f g)[x] = f[g[x]].
Proof.
intros [I1 _] [I2 _] I3.
cut ((x, (comp f g) [x]) ∈ (comp f g));
eauto using app_cor1, comp_fun.
intros J. apply zf_specification in J as [J1[y[J2 J3]]].
rewrite pi1_cor in J2. rewrite pi2_cor in J3.
assert (GY: y = g[x]) by eauto using app_eq. subst y.
eauto using app_eq.
Qed.

Lemma comp_sur f g A B C: bijection f B C → bijection g A B → surjective (comp f g) A C.
Proof.
intros [F1[F2 F3]] [G1[G2 G3]] c I1.
destruct (F2 c I1) as [b [I2 I3]].
destruct (G2 b I2) as [a [I4 I5]].
exists a. split; auto. apply zf_specification. split.
- apply product_opair. split; eauto using fun_el_dom, fun_el_ran.
- exists b. rewrite pi1_cor pi2_cor. split; assumption.
Qed.

Lemma comp_inj f g A B C: bijection f B C → bijection g A B → injective (comp f g).
Proof.
intros [F1[F2 F3]] [G1[G2 G3]] a a' c I1 I2.
apply zf_specification in I1 as [I1[b [GB FB]]].
apply zf_specification in I2 as [I2[b' [GB' FB']]].
rewrite pi1_cor in GB. rewrite pi1_cor in GB'.
rewrite pi2_cor in FB. rewrite pi2_cor in FB'.
specialize (F3 b b' c FB FB'). subst b'.
specialize (G3 a a' b GB GB'). assumption.
Qed.

Lemma comp_bij f g A B C: bijection f B C → bijection g A B → bijection (comp f g) A C.
Proof.
intros BF BG. assert (FF: function f B C) by apply BF. assert (FG: function g A B) by apply BG.
split; eauto using comp_fun. split; eauto using comp_sur, comp_inj.
Qed.

Lemma equi_trans A B C: equi A B → equi B C → equi A C.
Proof.
intros [g I] [f J]. exists (comp f g). now apply comp_bij with (B:=B).
Qed.



(** ** The Identity Function *)

Definition id A := specification_set (product A A) (λ p, pi1 p = pi2 p).

Lemma id_bijection A: bijection (id A) A A.
Proof.
repeat split.
- apply spec_subs.
- intros x X. exists x. split; trivial. apply zf_specification.
  rewrite pi1_cor pi2_cor. split; trivial. apply product_opair. split; assumption.
- intros x y y' I J. apply zf_specification in I as [_ I]. apply zf_specification in J as [_ J].
  rewrite pi1_cor pi2_cor in I. rewrite pi1_cor pi2_cor in J. congruence.
- intros y Y. exists y. split; trivial. apply zf_specification.
  rewrite pi1_cor pi2_cor. split; trivial. apply product_opair. split; assumption.
- intros x x' y I J. apply zf_specification in I as [_ I]. apply zf_specification in J as [_ J].
  rewrite pi1_cor pi2_cor in I. rewrite pi1_cor pi2_cor in J. congruence.
Qed.

Lemma id_app A a: a ∈ A → (id A)[a] = a.
Proof.
intros I. symmetry. apply (app_eq (id A) a a A A).
- apply id_bijection.
- apply zf_specification. rewrite pi1_cor pi2_cor. split; trivial. apply product_opair. now split.
Qed.

Lemma id_equal A B: bijection (id A) A B → A = B.
Proof.
intros ID. assert (ID': bijection (id A)^ B A) by eauto using inv_bij.
assert (IDF: function (id A) A B) by now destruct ID.
assert (IDF': function (id A)^ B A) by now destruct ID'.
apply zf_extensionality; split; intros x X.
- specialize (app_cor1 (id A) x A B IDF X). intros I.
  apply zf_specification in I as [_ I].
  rewrite pi1_cor pi2_cor in I. rewrite I.
  apply (app_cor2 (id A) x A); assumption.
- specialize (app_cor1 (id A)^ x B A IDF' X). intros I.
  apply (inv_el2 (id A) ((id A)^[x]) x A B) in I; try now destruct IDF.
  apply zf_specification in I as [_ I].
  rewrite pi1_cor pi2_cor in I. rewrite <- I.
  apply (inv_el (id A) A B); assumption.
Qed.

Lemma id_rel f A B: function f A B → (∀ x, x ∈ A → (x,x) ∈ f) → relation f A A.
Proof.
intros FF I p P. specialize (fun_pair f A B p FF P).
intros J. rewrite J. apply product_opair.
assert (H: pi1 p ∈ A) by now apply (fun_pi1 f A B). split; trivial.
specialize (I (pi1 p) H). cut (pi2 p = pi1 p).
- intros PP. now rewrite PP.
- destruct FF as [_ [_ FF]]. rewrite J in P.
  now apply (FF (pi1 p) (pi1 p) (pi2 p)).
Qed.


Lemma id_fun f A B: function f A B → (∀ x, x ∈ A → (x,x) ∈ f) → id A = f.
Proof.
intros FF I. apply zf_extensionality; split; intros p P.
- apply zf_specification in P as [P1 P2].
  assert (PI1: pi1 p ∈ A) by eauto using product_pi1.
  specialize (I (pi1 p) PI1).
  rewrite (product_p A A p); auto.
  rewrite <- P2. assumption.
- apply zf_specification. split.
  {
    eapply (id_rel f A B FF I p), P.
    (* curiously, the following eauto does not work, although it produces the same proof term (only different universes) *)
    (*eauto using (id_rel f A B FF I p).*)
  }
  assert (fct: functional f) by now destruct FF as [_[]].
  apply (fct (pi1 p)); [eapply fun_pi; eauto |  eapply I; eapply fun_pi1; eauto].
  Qed.

(** ** Functions are Extensional *)

Lemma fun_subs1 A B f g: function f A B → function g A B →
  (∀ b, b ∈ A → f[b] = g[b]) → f ⊆ g.
Proof.
intros FF GF E. intros p P.
assert (PA: pi1 p ∈ A) by eauto using fun_pi1.
apply (fun_appel f A B) in P; trivial.
rewrite P. rewrite E; trivial.
eauto using app_cor1.
Qed.

Lemma fun_subs2 A B f g: function f A B → function g A B →
  (∀ b, b ∈ A → f[b] = g[b]) → g ⊆ f.
Proof.
intros FF GF E. apply (fun_subs1 A B); trivial.
intros b I. now rewrite (E b I).
Qed.

Lemma fun_eq A B f g: function f A B → function g A B →
  (∀ b, b ∈ A → f[b] = g[b]) → f = g.
Proof.
intros FF GF E. apply zf_extensionality; eauto using fun_subs1, fun_subs2.
Qed.

Lemma fun_eq_gen A B B' f g: function f A B → function g A B' →
  (∀ x, x ∈ A → f[x] = g[x]) → f = g.
Proof.
intros FF GF E. apply (fun_eq A B); trivial.
apply fun_shrink with (B:=B'); trivial.
intros x X. rewrite <- (E x X). eauto using app_cor2.
Qed.

Lemma fun_res_eq A B B' f g A': function f A B → function g A B' → A' ⊆ A →
  (∀ b, b ∈ A' → f[b] = g[b]) → f|*A' = g|*A'.
Proof.
intros FF GF S E. apply (fun_eq_gen A' B B'); eauto using res_fun.
intros b BE.
rewrite <- (res_eq _ A B); trivial.
rewrite <- (res_eq _ A B'); trivial.
now apply E.
Qed.

Lemma fun_subs f g A B A' x: function f A B → function g A' B → x ∈ A'
  → g ⊆ f → g [x] = f [x].
Proof.
intros FF FG X S.
apply (app_eq f x (g[x]) A B); trivial.
apply S. apply (app_cor1 g x A' B); assumption.
Qed.

Lemma fun_subs_res f g A B A' C: function f A B → function g A' B
  → g ⊆ f → C ⊆ A' → A' ⊆ A → f|*C = g|*C.
Proof.
intros FF FG S1 S2 S3. apply (fun_eq C B).
- apply res_fun with (A:=A); trivial.
  now apply subs_trans with (B:=A').
- now apply res_fun with (A:=A').
- intros b BE.
  rewrite <- (res_eq f A B C); eauto using subs_trans.
  rewrite <- (res_eq g A' B C); trivial.
  symmetry. apply (fun_subs f g A B A'); auto.
Qed.



(** ** Meta-Functions and Object-Functions *)

Definition lam (F: set → set) A := replacement_set A (λ a, (a,F a)).
Definition sur (F: set → set) A B := ∀ y, y ∈ B → ∃ x, x ∈ A ∧ F x = y.
Definition inj (F: set → set) A:= ∀ x x' (y:set), x ∈ A → x' ∈ A → F x = y → F x' = y → x = x'.

Lemma lam_el F A x y: (x,y) ∈ (lam F A) → F x = y ∧ x ∈ A.
Proof.
intros I. apply zf_replacement in I as [a [AA I]].
apply opair_eq in I. destruct I as [I1 I2].
split; congruence.
Qed.

Lemma lam_fun F A B: (∀ x, x ∈ A → F x ∈ B) → function (lam F A) A B.
Proof.
intros I. repeat split.
- intros p P. apply zf_replacement in P as [x [P1 P2]].
  rewrite P2. apply product_opair. split; auto.
- intros x X. exists (F x). split; auto.
  apply zf_replacement. exists x. split; eauto using opair_eq.
- intros x y y' I1 I2.
  apply zf_replacement in I1 as [x1 [_ I1]].
  apply zf_replacement in I2 as [x2 [_ I2]].
  apply opair_eq in I1 as [I1 I1'].
  apply opair_eq in I2 as [I2 I2'].
  congruence.
Qed.

Lemma lam_app F A B x: (∀ x, x ∈ A → F x ∈ B) → x ∈ A → F x = (lam F A) [x].
Proof.
intros I X. apply app_eq with (A:=A) (B:=B).
- now apply lam_fun.
- apply zf_replacement. exists x. split; auto.
Qed.

Lemma lam_app2 F A B x: function (lam F A) A B → x ∈ A → F x = (lam F A) [x].
Proof.
intros I X. apply app_eq with (A:=A) (B:=B).
- assumption.
- apply zf_replacement. exists x. split; auto.
Qed.

Lemma lam_subs F A A': A' ⊆ A → (lam F A) |* A' = lam F A'.
Proof.
intros I. apply zf_extensionality; split; intros p P.
- apply zf_specification in P as [P1 P2].
  apply zf_replacement in P1 as [x[X1 X2]]. subst p.
  apply zf_replacement. rewrite pi1_cor in P2.
  exists x. split; trivial.
- apply zf_replacement in P as [x[X1 X2]]. subst p.
  apply zf_specification. rewrite pi1_cor. split; trivial.
  apply zf_replacement. exists x. split; auto.
Qed.

Lemma lam_sur F A B: sur F A B → surjective (lam F A) A B.
Proof.
intros I y Y. destruct (I y Y) as [x [I1 I2]].
exists x. split; auto. rewrite <- I2.
apply zf_replacement. exists x. split; auto.
Qed.

Lemma lam_inj F A: inj F A → injective (lam F A).
Proof.
intros I x x' y I1 I2.
apply lam_el in I1 as [I1 I1'].
apply lam_el in I2 as [I2 I2'].
apply I with (y:=y); assumption.
Qed.

End set_functions.
Notation "f '[(' A ')]'" := (image f A) (at level 10) : zf_scope.
Notation "f '[' x ']'" := (app f x) (at level 10) : zf_scope.
Notation "f ^" := (inverse f) (at level 5) : zf_scope.
Notation "f '|*' A" := (restriction f A) (at level 8) : zf_scope.
Notation "R '|>' A" := (rel_restriction R A) (at level 9) : zf_scope.
