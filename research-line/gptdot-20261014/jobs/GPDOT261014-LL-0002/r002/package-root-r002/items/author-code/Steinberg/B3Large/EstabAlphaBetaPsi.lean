
import Steinberg.B3Large.Basic
import Steinberg.B3Large.Setup

namespace Steinberg.B3Large

open Steinberg B3LargePosRoot GradedPartialChevalley GradedChevalleyGenerator GradedPartialChevalleyGroup

variable {F : Type TF} [Field F] (Fchar : (2 : F) ≠ 0)

/- ### Establishing α + β + ψ -/

private lemma interchange_αβψ_refl_v : forall_ijk_tu α β ψ,
    ⸨ψ, k, -1/2⸩ * ⸨αβ, i + j, t * u⸩ * ⸨ψ, k, 1⸩ * ⸨αβ, i + j, -t * u⸩ * ⸨ψ, k, -1/2⸩
      = ⸨βψ, j + k, -u/2⸩ * ⸨α, i, t⸩ * ⸨βψ, j + k, u⸩ * ⸨α, i, -t⸩ * ⸨βψ, j + k, -u/2⸩ := by
  intro i j k hi hj hk t u
  grw [raw_hom_lift_of_interchange_of_αβψ hi hj hk t u 1]

private lemma interchange_αβψ_refl_u : forall_ijk_tu α β ψ,
    ⸨ψ, k, -u/2⸩ * ⸨αβ, i + j, t⸩ * ⸨ψ, k, u⸩ * ⸨αβ, i + j, -t⸩ * ⸨ψ, k, -u/2⸩
      = ⸨βψ, j + k, -u/2⸩ * ⸨α, i, t⸩ * ⸨βψ, j + k, u⸩ * ⸨α, i, -t⸩ * ⸨βψ, j + k, -u/2⸩ := by
  intro i j k hi hj hk t u
  rw [← mul_one t, ← neg_mul]
  grw [raw_hom_lift_of_interchange_of_αβψ hi hj hk t 1 u]

private lemma interchange_αβψ_trans_βψ_α : forall_ijk_tu α β ψ,
    ⸨βψ, j + k, -1/2⸩ * ⸨α, i, t * u⸩ * ⸨βψ, j + k, 1⸩ * ⸨α, i, -t * u⸩ * ⸨βψ, j + k, -1/2⸩
      = ⸨βψ, j + k, -u/2⸩ * ⸨α, i, t⸩ * ⸨βψ, j + k, u⸩ * ⸨α, i, -t⸩ * ⸨βψ, j + k, -u/2⸩ := by
  intro i j k hi hj hk t u
  have aux₁ := raw_hom_lift_of_interchange_of_αβψ hi hj hk t u 1
  have aux₂ := raw_hom_lift_of_interchange_of_αβψ hi hj hk (t * u) 1 1
  simp only [one_mul, mul_one] at aux₁
  simp only [one_mul, mul_one, ←neg_mul] at aux₂
  rwa [aux₂] at aux₁

private lemma interchange_αβψ_trans_ψ_αβ : forall_ijk_tu α β ψ,
    ⸨ψ, k, -1 / 2⸩ * ⸨αβ, i + j, t * u⸩ * ⸨ψ, k, 1⸩ * ⸨αβ, i + j, -t * u⸩ * ⸨ψ, k, -1 / 2⸩
      = ⸨ψ, k, -u / 2⸩ * ⸨αβ, i + j, t⸩ * ⸨ψ, k, u⸩ * ⸨αβ, i + j, -t⸩ * ⸨ψ, k, -u / 2⸩ := by
  intro i j k hi hj hk t u
  have aux₁ := raw_hom_lift_of_interchange_of_αβψ hi hj hk 1 t u
  have aux₂ := raw_hom_lift_of_interchange_of_αβψ hi hj hk 1 (t * u) 1
  simp only [one_mul, mul_one, neg_mul] at aux₁
  simp only [one_mul, mul_one, neg_mul] at aux₂
  rwa [←aux₁, ←neg_mul] at aux₂

-- height 0
private lemma expr_αβψ_as_βψ_α_βψ_α_βψ_00 : ∀ (t u : F),
    ⸨αβψ, 0, t * u⸩ = ⸨βψ, 0, -u/2⸩ * ⸨α, 0, t⸩ * ⸨βψ, 0, u⸩ * ⸨α, 0, -t⸩ * ⸨βψ, 0, -u/2⸩ := by
  intro t u
  have := @def_of_αβψ _ _ 0 (by trivial) (t * u)
  unfold split_3_into_1_2 at this
  rw [←this, ←neg_mul, @interchange_αβψ_trans_βψ_α _ _ 0 0 0 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_00 : ∀ (t u : F),
    ⸨αβψ, 0, t * u⸩ = ⸨ψ, 0, -u/2⸩ * ⸨αβ, 0, t⸩ * ⸨ψ, 0, u⸩ * ⸨αβ, 0, -t⸩ * ⸨ψ, 0, -u/2⸩ := by
  intro t u
  rw [expr_αβψ_as_βψ_α_βψ_α_βψ_00, ←@interchange_αβψ_refl_v _ _ 0 0 0 (by trivial) (by trivial) (by trivial),
  interchange_αβψ_trans_ψ_αβ (by trivial) (by trivial) (by trivial)]

-- height 1
private lemma expr_αβψ_as_βψ_α_βψ_α_βψ_01 : ∀ (t u : F),
    ⸨αβψ, 1, t * u⸩ = ⸨βψ, 1, -u/2⸩ * ⸨α, 0, t⸩ * ⸨βψ, 1, u⸩ * ⸨α, 0, -t⸩ * ⸨βψ, 1, -u/2⸩ := by
  intro t u
  have := @def_of_αβψ _ _ 1 (by trivial) (t * u)
  unfold split_3_into_1_2 at this
  rw [←this, ←neg_mul, @interchange_αβψ_trans_βψ_α _ _ 0 1 0 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_01 : ∀ (t u : F),
    ⸨αβψ, 1, t * u⸩ = ⸨ψ, 1, -u/2⸩ * ⸨αβ, 0, t⸩ * ⸨ψ, 1, u⸩ * ⸨αβ, 0, -t⸩ * ⸨ψ, 1, -u/2⸩ := by
  intro t u
  rw [expr_αβψ_as_βψ_α_βψ_α_βψ_01, @interchange_αβψ_refl_u _ _ 0 0 1 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_10 : ∀ (t u : F),
    ⸨αβψ, 1, t * u⸩ = ⸨ψ, 0, -u/2⸩ * ⸨αβ, 1, t⸩ * ⸨ψ, 0, u⸩ * ⸨αβ, 1, -t⸩ * ⸨ψ, 0, -u/2⸩ := by
  intro t u
  rw [expr_αβψ_as_βψ_α_βψ_α_βψ_01, ←@interchange_αβψ_refl_v _ _ 0 1 0 (by trivial) (by trivial) (by trivial),
  interchange_αβψ_trans_ψ_αβ (by trivial) (by trivial) (by trivial)]

private lemma expr_αβψ_as_βψ_α_βψ_α_βψ_10 : ∀ (t u : F),
    ⸨αβψ, 1, t * u⸩ = ⸨βψ, 0, -u/2⸩ * ⸨α, 1, t⸩ * ⸨βψ, 0, u⸩ * ⸨α, 1, -t⸩ * ⸨βψ, 0, -u/2⸩ := by
  intro t u
  rw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_10, @interchange_αβψ_refl_u _ _ 1 0 0 (by trivial) (by trivial) (by trivial)]

-- height 2
private lemma expr_αβψ_as_βψ_α_βψ_α_βψ_11 : ∀ (t u : F),
    ⸨αβψ, 2, t * u⸩ = ⸨βψ, 1, -u/2⸩ * ⸨α, 1, t⸩ * ⸨βψ, 1, u⸩ * ⸨α, 1, -t⸩ * ⸨βψ, 1, -u/2⸩ := by
  intro t u
  have := @def_of_αβψ _ _ 2 (by trivial) (t * u)
  unfold split_3_into_1_2 at this
  rw [←this, ←neg_mul, @interchange_αβψ_trans_βψ_α _ _ 1 1 0 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_20 : ∀ (t u : F),
    ⸨αβψ, 2, t * u⸩ = ⸨ψ, 0, -u/2⸩ * ⸨αβ, 2, t⸩ * ⸨ψ, 0, u⸩ * ⸨αβ, 2, -t⸩ * ⸨ψ, 0, -u/2⸩ := by
  intro t u
  rw [expr_αβψ_as_βψ_α_βψ_α_βψ_11, @interchange_αβψ_refl_u _ _ 1 1 0 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_11 : ∀ (t u : F),
    ⸨αβψ, 2, t * u⸩ = ⸨ψ, 1, -u/2⸩ * ⸨αβ, 1, t⸩ * ⸨ψ, 1, u⸩ * ⸨αβ, 1, -t⸩ * ⸨ψ, 1, -u/2⸩ := by
  intro t u
  rw [expr_αβψ_as_βψ_α_βψ_α_βψ_11, @interchange_αβψ_refl_u _ _ 1 0 1 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβψ_as_βψ_α_βψ_α_βψ_02 : ∀ (t u : F),
    ⸨αβψ, 2, t * u⸩ = ⸨βψ, 2, -u/2⸩ * ⸨α, 0, t⸩ * ⸨βψ, 2, u⸩ * ⸨α, 0, -t⸩ * ⸨βψ, 2, -u/2⸩ := by
  intro t u
  rw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_11, @interchange_αβψ_refl_u _ _ 0 1 1 (by trivial) (by trivial) (by trivial)]

-- height 3
private lemma expr_αβψ_as_βψ_α_βψ_α_βψ_12 : ∀ (t u : F),
    ⸨αβψ, 3, t * u⸩ = ⸨βψ, 2, -u/2⸩ * ⸨α, 1, t⸩ * ⸨βψ, 2, u⸩ * ⸨α, 1, -t⸩ * ⸨βψ, 2, -u/2⸩ := by
  intro t u
  have := @def_of_αβψ _ _ 3 (by trivial) (t * u)
  unfold split_3_into_1_2 at this
  rw [←this, ←neg_mul, @interchange_αβψ_trans_βψ_α _ _ 1 1 1 (by trivial) (by trivial) (by trivial)]

private lemma expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_21 : ∀ (t u : F),
    ⸨αβψ, 3, t * u⸩ = ⸨ψ, 1, -u/2⸩ * ⸨αβ, 2, t⸩ * ⸨ψ, 1, u⸩ * ⸨αβ, 2, -t⸩ * ⸨ψ, 1, -u/2⸩ := by
  intro t u
  rw [expr_αβψ_as_βψ_α_βψ_α_βψ_12, @interchange_αβψ_refl_u _ _ 1 1 1 (by trivial) (by trivial) (by trivial)]

-- 8.116a
theorem expr_αβψ_as_ψ_αβ_ψ_αβ_ψ : forall_ij_tu αβ ψ,
    ⸨αβψ, i + j, t * u⸩ = ⸨ψ, j, -u/2⸩ * ⸨αβ, i, t⸩ * ⸨ψ, j, u⸩ * ⸨αβ, i, -t⸩ * ⸨ψ, j, -u/2⸩ := by
  intro i j hi hj t u
  match i, j with
  | 0, 0 => rw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_00]
  | 1, 0 => rw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_10]
  | 0, 1 => rw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_01]
  | 2, 0 => rw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_20]
  | 1, 1 => rw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_11]
  | 2, 1 => rw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ_21]

-- 8.116b
theorem expr_αβψ_as_βψ_α_βψ_α_βψ : forall_ij_tu α βψ,
    ⸨αβψ, i + j, t * u⸩ = ⸨βψ, j, -u/2⸩ * ⸨α, i, t⸩ * ⸨βψ, j, u⸩ * ⸨α, i, -t⸩ * ⸨βψ, j, -u/2⸩ := by
  intro i j hi hj t u
  match i, j with
  | 0, 0 => rw [expr_αβψ_as_βψ_α_βψ_α_βψ_00]
  | 1, 0 => rw [expr_αβψ_as_βψ_α_βψ_α_βψ_10]
  | 0, 1 => rw [expr_αβψ_as_βψ_α_βψ_α_βψ_01]
  | 0, 2 => rw [expr_αβψ_as_βψ_α_βψ_α_βψ_02]
  | 1, 1 => rw [expr_αβψ_as_βψ_α_βψ_α_βψ_11]
  | 1, 2 => rw [expr_αβψ_as_βψ_α_βψ_α_βψ_12]

-- 8.117
theorem comm_of_α_αβψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project ⟨α, αβψ⟩ := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.mpr
  rcases decompose αβ.height ψ.height j hj with ⟨ j₁, j₂, ⟨ rfl, hj₁, hj₂ ⟩ ⟩
  rw [← one_mul u]
  grw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hj₁ hj₂, expr_α_ψ_as_ψ_α hi hj₂,
    expr_α_αβ_as_αβ_α hi hj₁, expr_α_ψ_as_ψ_α hi hj₂,
    expr_α_αβ_as_αβ_α hi hj₁, expr_α_ψ_as_ψ_α hi hj₂]
declare_B3Large_trivial_span_expr_thm F α αβψ

-- 8.118
theorem comm_of_αβ_αβψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project ⟨αβ, αβψ⟩ := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.mpr
  rcases decompose αβ.height ψ.height j hj with ⟨ j₁, j₂, ⟨ rfl, hj₁, hj₂ ⟩ ⟩
  rw [deg_add_comm αβψ j₁ j₂, ← one_mul u]
  grw [expr_αβψ_as_βψ_α_βψ_α_βψ hj₂ hj₁, expr_αβ_βψ_as_βψ_αβ hi hj₁,
    ← expr_α_αβ_as_αβ_α hj₂ hi, expr_αβ_βψ_as_βψ_αβ hi hj₁,
    ← expr_α_αβ_as_αβ_α hj₂ hi, expr_αβ_βψ_as_βψ_αβ hi hj₁]
declare_B3Large_trivial_span_expr_thm F αβ αβψ

-- 8.119
theorem comm_of_β_αβψ :
    trivialSpanPropOfRootPair (weakB3LargeGraded F).project ⟨β, αβψ⟩ := by
  intro i j hi hj t u
  apply triv_comm_iff_commutes.mpr
  rcases decompose αβ.height ψ.height j hj with ⟨ j₁, j₂, ⟨ rfl, hj₁, hj₂ ⟩ ⟩
  have hj₂i : j₂ + i ≤ βψ.height := by ht
  rw [deg_add_comm αβψ j₁ j₂, ← one_mul u]
  grw [expr_αβψ_as_βψ_α_βψ_α_βψ hj₂ hj₁, expr_β_βψ_as_βψ_β hi hj₁,
    expr_β_α_as_αβ_α_β hj₂ hi, expr_β_βψ_as_βψ_β hi hj₁,
    expr_β_α_as_αβ_α_β hj₂ hi, expr_β_βψ_as_βψ_β hi hj₁,
    ← expr_α_αβ_as_αβ_α hj₂ hj₂i, expr_αβ_βψ_as_βψ_αβ hj₂i hj₁]
declare_B3Large_trivial_span_expr_thm F β αβψ

-- 8.120a
@[simp, chev_simps]
private lemma inv_doub_of_αβψ_a : forall_i_t αβψ, ⸨αβψ, i, t⸩ * ⸨αβψ, i, -t⸩ = 1 := by
  intro i hi t
  rcases decompose αβ.height ψ.height i hi with ⟨ i₁, i₂, ⟨ rfl, hi₁, hi₂ ⟩ ⟩
  rw [← mul_one t]
  grw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi₁ hi₂]
  have expand := expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi₁ hi₂ t (-1)
  chev_simp at expand
  grw [expand]

-- restatement of 8.120a using our naming conventions
@[simp, chev_simps]
theorem inv_of_αβψ : forall_i_t αβψ, ⸨αβψ, i, t⸩⁻¹ = ⸨αβψ, i, -t⸩ := by
  intro i hi t
  have := eq_inv_of_mul_eq_one_left (inv_doub_of_αβψ_a hi (-t))
  rw [neg_neg] at this
  exact this.symm

-- 8.120b
include Fchar
theorem doub_of_αβψ : forall_i_t αβψ, ⸨αβψ, i, t⸩ * ⸨αβψ, i, t⸩ = ⸨αβψ, i, 2 * t⸩ := by
  intros i hi t
  rcases decompose αβ.height ψ.height i hi with ⟨ i₁, i₂, ⟨ rfl, hi₁, hi₂ ⟩ ⟩
  rw [← mul_one t, expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi₁ hi₂]
  have := raw_hom_lift_of_doub_of_αβψ hi₁ hi₂ t 1 1
  rw [mul_one, neg_mul, mul_one, mul_one] at this
  grw [this, mul_comm 2 t, expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi₁ hi₂, div_self Fchar]

lemma half_add_half (u : F) : (u / 2) + (u / 2) = u := by
  have : ((2 : F) / 2) = 1 := (div_eq_one_iff_eq Fchar).mpr rfl
  rw [← mul_two, div_mul_comm, this, one_mul]

-- 8.121
theorem generic_comm_of_αβ_ψ :
  forall_ij_tu 2 1,
    ⁅⸨αβ, i, t⸩, ⸨ψ, j, u⸩⁆ = ⸨αβψ, i + j, t * u⸩ * ⁅⸨αβψ, i + j, -t * u⸩, ⸨ψ, j, u / 2⸩⁆
    ∧ ⁅⸨αβ, i, t⸩, ⸨ψ, j, u⸩⁆ = ⁅⸨αβψ, i + j, t * u⸩, ⸨ψ, j, u / 2⸩⁆⁻¹ * ⸨αβψ, i + j, t * u⸩ := by
  intro i j hi hj t u
  set x := ⸨αβ, i, t⸩ with hx
  set y := ⸨ψ, j, u/2⸩ with hy
  have xinv : x⁻¹ = ⸨αβ, i, -t⸩ := by rw [inv_of_αβ]
  have ysquare : y^2 = ⸨ψ, j, u⸩ := by
    rw [pow_two, lin_of_ψ, ←two_mul, mul_div_left_comm, div_self Fchar, mul_one]
  have yinv : y⁻¹ = ⸨ψ, j, -(u / 2)⸩ := by rw [inv_of_ψ]
  have x_star_y : (x ⋆ y) = ⸨αβψ, i + j, t * u⸩ := by
    unfold starCommutator_def x y
    grw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ hi hj, inv_of_ψ, pow_two, inv_of_αβ,
    lin_of_ψ, half_add_half Fchar u]
  have x_star_y_inv : (x ⋆ y)⁻¹ = ⸨αβψ, i + j, -t * u⸩ := by
    rw [x_star_y, eq_inv_of_mul_eq_one_left (inv_doub_of_αβψ_a (add_le_add hi hj) (t * u)), inv_inv, neg_mul]
  rw [←ysquare, ←x_star_y, ←x_star_y_inv]
  exact ⟨(star_commutator x y).symm, (commutator_star x y).symm⟩

-- 8.122
theorem generic_comm_of_α_βψ :
  forall_ij_tu 1 2,
    ⁅⸨α, i, t⸩, ⸨βψ, j, u⸩⁆ = ⸨αβψ, i + j, t * u⸩ * ⁅⸨αβψ, i + j, -t * u⸩, ⸨βψ, j, u / 2⸩⁆
    ∧ ⁅⸨α, i, t⸩, ⸨βψ, j, u⸩⁆ = ⁅⸨αβψ, i + j, t * u⸩, ⸨βψ, j, u / 2⸩⁆⁻¹ * ⸨αβψ, i + j, t * u⸩ := by
  intro i j hi hj t u
  set x := ⸨α, i, t⸩ with hx
  set y := ⸨βψ, j, u / 2⸩ with hy
  have ysquare : y^2 = ⸨βψ, j, u⸩ := by
    rw [pow_two, hy, lin_of_βψ, half_add_half Fchar u]
  have x_star_y : (x ⋆ y) = ⸨αβψ, i + j, t * u⸩ := by
    unfold starCommutator_def x y
    grw [expr_αβψ_as_βψ_α_βψ_α_βψ hi hj, inv_of_βψ, pow_two, lin_of_βψ, half_add_half Fchar u, inv_of_α]
  have x_star_y_inv : (x ⋆ y)⁻¹ = ⸨αβψ, i + j, -t * u⸩ := by
    rw [x_star_y, eq_inv_of_mul_eq_one_left (inv_doub_of_αβψ_a (add_le_add hi hj) (t * u)), inv_inv, neg_mul]
  rw [←ysquare, ←x_star_y, ←x_star_y_inv]
  exact ⟨(star_commutator x y).symm, (commutator_star x y).symm⟩

-- 8.123
omit Fchar
theorem lift_hom_interchange_of_αβ2ψ :
  forall_ijk_tuv,
    ⁅⸨αβψ, i + j + k, t * u⸩, ⸨ψ, k, v⸩⁆ = ⁅⸨α, i, t⸩, ⸨β2ψ, j + 2 * k, -2 * u * v⸩⁆ := by
  intro i j k hi hj hk t u v
  rcases eq_or_ne v 0 with hv | hv
  · rw [hv, mul_zero, id_of_ψ, id_of_β2ψ]; group
  have expr_αβ2ψ := raw_hom_lift_of_interchange_of_αβ2ψ hi hj hk t (u / v) v
  have : -2 * (u / v) * v^2 = -2 * u * v := by field_simp; group
  rw [this] at expr_αβ2ψ
  have expr_αβψ := expr_αβψ_as_ψ_αβ_ψ_αβ_ψ (add_le_add hi hj) hk (t * (u / v)) v
  have : t * (u / v) * v = t * u := by field_simp
  rw [this] at expr_αβψ
  grw [←expr_αβ2ψ, expr_αβψ, neg_mul]


-- 8.124
theorem lift_hom_comm_of_βψ_α_β2ψ : forall_ijk_tuv,
    ⁅⸨βψ, j + k, t⸩, ⁅⸨α, i, u⸩, ⸨β2ψ, j + 2 * k, v⸩⁆⁆ = 1 := by
  intro i j k hi hj hk t u v
  rcases eq_or_ne v 0 with hv | hv
  · rw [hv, id_of_β2ψ]; group
  rcases eq_or_ne t 0 with ht | ht
  · rw [ht, id_of_βψ]; group
  have hβψ := raw_hom_lift_of_comm_of_βψ_α_β2ψ hi hj hk u (t^2 / v) (v / t)
  have : t^2 / v * (v / t) = t := by rw [pow_two]; field_simp
  rw [this] at hβψ
  have : t^2 / v * (v / t)^2 = v := by field_simp; group
  rw [this] at hβψ
  exact hβψ

-- 8.125a
theorem lift_hom_inv_doub_of_α_β2ψ_a : forall_ij_tu α β2ψ,
    ⁅⸨α, i, t⸩, ⸨β2ψ, j, u⸩⁆ = ⁅⸨α, i, -t⸩, ⸨β2ψ, j, -u⸩⁆ := by
  intro i j hi hj t u
  rcases decompose_3_into_booleans_1_2 j hj with ⟨j₁, j₂, ⟨ rfl, hj₁, hj₂⟩ ⟩
  have := raw_hom_lift_of_inv_doub_of_α_β2ψ_a hi hj₁ hj₂ t u 1
  field_simp at this
  exact this

-- 8.125b
theorem lift_hom_inv_doub_of_α_β2ψ_b : forall_ij_tu α β2ψ,
    ⁅⸨α, i, t⸩, ⸨β2ψ, j, u⸩⁆ * ⁅⸨α, i, t⸩, ⸨β2ψ, j, -u⸩⁆ = 1 := by
  intro i j hi hj t u
  rcases decompose_3_into_booleans_1_2 j hj with ⟨j₁, j₂, ⟨ rfl, hj₁, hj₂⟩ ⟩
  have := raw_hom_lift_of_inv_doub_of_α_β2ψ_b hi hj₁ hj₂ t u 1
  field_simp at this
  exact this

theorem inv_of_comm_of_α_β2ψ : forall_ij_tu α β2ψ,
    ⁅⸨α, i, t⸩, ⸨β2ψ, j, u⸩⁆⁻¹ = ⁅⸨α, i, t⸩, ⸨β2ψ, j, -u⸩⁆ := by
  intro i j hi hj t u
  exact inv_eq_of_mul_eq_one_right (lift_hom_inv_doub_of_α_β2ψ_b hi hj t u)

-- 8.125c
theorem lift_hom_inv_doub_of_α_β2ψ_c : forall_ij_tu α β2ψ,
    ⁅⸨α, i, t⸩, ⸨β2ψ, j, u⸩⁆ * ⁅⸨α, i, t⸩, ⸨β2ψ, j, u⸩⁆ = ⁅⸨α, i, t⸩, ⸨β2ψ, j, 2 * u⸩⁆ := by
  intro i j hi hj t u
  rcases decompose_3_into_booleans_1_2 j hj with ⟨j₁, j₂, ⟨ rfl, hj₁, hj₂⟩ ⟩
  have := raw_hom_lift_of_inv_doub_of_α_β2ψ_c hi hj₁ hj₂ t u 1
  field_simp at this
  exact this

-- 8.126
theorem lift_hom_comm_of_β2ψ_αβψ : forall_ijk_tu α β ψ,
    ⁅⸨β2ψ, j + 2 * k, t⸩, ⸨αβψ, i + j + k, u⸩⁆ = 1 := by
  intro i j k hi hj hk t u
  rcases eq_or_ne t 0 with (rfl | ht)
  · chev_simp
  · have expr_β2ψ := raw_hom_lift_of_comm_of_β2ψ_αβψ hi hj hk (u / t) t 1
    rw [← mul_one u]
    grw [expr_αβψ_as_ψ_αβ_ψ_αβ_ψ (add_le_add hi hj) hk u 1]
    field_simp at expr_β2ψ
    have : -(u * t) / t = -u := by field_simp
    grw [this] at expr_β2ψ
    exact expr_β2ψ

-- 8.127
theorem comm_of_ψ_α_β2ψ : forall_ijk_tuv ψ α β2ψ,
    ⁅⸨ψ, i, t⸩, ⁅⸨α, j, u⸩, ⸨β2ψ, k, v⸩⁆⁆ = 1 := by
  intro i j k hi hj hk t u v
  apply triv_comm_iff_commutes.mpr
  grw [commutatorElement_def, ← expr_α_ψ_as_ψ_α hj hi, expr_ψ_β2ψ_as_β2ψ_ψ hi hk,
       ← expr_α_ψ_as_ψ_α hj hi, expr_ψ_β2ψ_as_β2ψ_ψ hi hk]

@[group_reassoc]
theorem expr_ψ_comm_α_β2ψ_as_comm_α_β2ψ_ψ : forall_ijk_tuv ψ α β2ψ,
    ⸨ψ, i, t⸩ * ⁅⸨α, j, u⸩, ⸨β2ψ, k, v⸩⁆ = ⁅⸨α, j, u⸩, ⸨β2ψ, k, v⸩⁆ * ⸨ψ, i, t⸩ := by
  intro i j k hi hj hk t u v
  exact triv_comm_iff_commutes.1 (comm_of_ψ_α_β2ψ hi hj hk t u v)

-- 8.128
theorem comm_of_α_αβψ_ψ : forall_ijk_tuv α αβψ ψ,
    ⁅⸨α, i, t⸩, ⁅⸨αβψ, j, u⸩, ⸨ψ, k, v⸩⁆⁆ = 1 := by
  intro i j k hi hj hk t u v
  apply triv_comm_iff_commutes.mpr
  rw [commutatorElement_def]
  grw [inv_of_αβψ hj, expr_α_αβψ_as_αβψ_α hi hj, expr_α_ψ_as_ψ_α hi hk,
    expr_α_αβψ_as_αβψ_α hi hj, expr_α_ψ_as_ψ_α hi hk]

@[group_reassoc]
theorem expr_α_comm_αβψ_ψ_as_comm_αβψ_ψ_α : forall_ijk_tuv α αβψ ψ,
    ⸨α, i, t⸩ * ⁅⸨αβψ, j, u⸩, ⸨ψ, k, v⸩⁆ = ⁅⸨αβψ, j, u⸩, ⸨ψ, k, v⸩⁆ * ⸨α, i, t⸩ := by
  intro i j k hi hj hk t u v
  exact triv_comm_iff_commutes.1 (comm_of_α_αβψ_ψ hi hj hk t u v)

include Fchar
-- 8.129
theorem comm_of_α_α_β2ψ : forall_ijk_tuv α α β2ψ,
    ⁅⸨α, i, t⸩, ⁅⸨α, j, u⸩, ⸨β2ψ, k, v⸩⁆⁆ = 1 := by
  intro i j k hi hj hk t u v
  apply triv_comm_iff_commutes.2
  rcases decompose_3_into_booleans_1_2 k hk with ⟨ j', k', ⟨ rfl, hj', hk' ⟩ ⟩
  have : v = -2 * v * (-1 / 2) := by field_simp
  rw [this, ←lift_hom_interchange_of_αβ2ψ hj hj' hk', expr_α_comm_αβψ_ψ_as_comm_αβψ_ψ_α hi (by ht) hk']

@[group_reassoc] theorem expr_α_comm_α_β2ψ_as_comm_α_β2ψ_α :
  forall_ijk_tuv α α β2ψ,
    ⸨α, i, t⸩ * ⁅⸨α, j, u⸩, ⸨β2ψ, k, v⸩⁆ = ⁅⸨α, j, u⸩, ⸨β2ψ, k, v⸩⁆ * ⸨α, i, t⸩ := by
  intro i j k hi hj hk t u v
  exact triv_comm_iff_commutes.1 (comm_of_α_α_β2ψ Fchar hi hj hk t u v)

-- Proposition 8.130
theorem sufficient_conditions_for_comm_of_αβψ_and_ψ :
  ∀ ⦃i j k : ℕ⦄ (hi : i ≤ α.height) (hj : j ≤ βψ.height) (hk : k ≤ ψ.height)
  (hyp : ∀ (t u v : F), ⁅⸨βψ, j, t⸩, ⁅⸨α, i, u⸩, ⸨β2ψ, j + k, v⸩⁆⁆ = 1),
    ∀ (t u v : F), ⁅⸨αβψ, i + j, t * u⸩'(by height_simp at hi hj ⊢; omega), ⸨ψ, k, v⸩⁆
        = ⁅⸨α, i, t⸩, ⸨β2ψ, j + k, -2 * u * v⸩'(by height_simp at hj hk ⊢; omega)⁆ := by
  intro i j k hi hj hk hyp t u v
  have hjk : j + k ≤ β2ψ.height := by height_simp at hj hk ⊢; omega
  apply eq_comm_of_reorder_left
  grw [expr_αβψ_as_βψ_α_βψ_α_βψ hi hj, expr_βψ_ψ_as_ψ_β2ψ_βψ hk hj,
    expr_α_ψ_as_ψ_α hi hk, expr_βψ_ψ_as_ψ_β2ψ_βψ hk hj,
    expr_α_ψ_as_ψ_α hi hk, expr_βψ_ψ_as_ψ_β2ψ_βψ hk hj]
  simp_rw [deg_add_comm β2ψ k j]
  have : 2 * v * (u / 2) = u * v := by field_simp; group
  rw [this]
  clear this
  have hyp' := fun t' u' v' => triv_comm_iff_commutes.1 (hyp t' u' v')
  have aux₁ : ⸨β2ψ, j + k, u * v⸩ * ⸨α, i, t⸩ = ⁅⸨α, i, t⸩, ⸨β2ψ, j + k, -u * v⸩⁆ * ⸨α, i, t⸩ * ⸨β2ψ, j + k, u * v⸩ := by
    rw [comm_left_rev, inv_of_comm_of_α_β2ψ hi hjk, neg_mul]
  grw [← expr_βψ_β2ψ_as_β2ψ_βψ hj hjk (-(u / 2)) (u * v), aux₁]
  clear aux₁
  have aux₂ : ⸨α, i, -t⸩ * ⸨β2ψ, j + k, u * v⸩ = ⸨β2ψ, j + k, u * v⸩ * ⸨α, i, -t⸩ * ⁅⸨α, i, t⸩, ⸨β2ψ, j + k, -u * v⸩⁆ := by
    rw [← inv_of_α, neg_mul, ← inv_of_β2ψ]
    group
  have : u * v + -(2 * v * u) + u * v = 0 := by ring
  grw [aux₂, expr_βψ_β2ψ_as_β2ψ_βψ hj hjk u (u * v), this]
  clear aux₂ this
  grw [hyp' (-(u / 2)),
        expr_ψ_comm_α_β2ψ_as_comm_α_β2ψ_ψ hk hi hjk,
        expr_α_comm_α_β2ψ_as_comm_α_β2ψ_α Fchar hi hi hjk,
        hyp' u,
        expr_α_comm_α_β2ψ_as_comm_α_β2ψ_α Fchar hi hi hjk,
        hyp' (-(u / 2)),
        expr_ψ_comm_α_β2ψ_as_comm_α_β2ψ_ψ hk hi hjk,
        lift_hom_inv_doub_of_α_β2ψ_c hi hjk, mul_assoc]
