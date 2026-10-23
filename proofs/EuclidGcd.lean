/-!
# Euclid's algorithm, typed by what it returns

`Gcd a b` is the type of numbers whose divisors are exactly the common divisors of `a` and `b`.
A value of this type is a number *together with* the evidence. Returning one means the function
cannot return anything but the gcd.
-/

/-- The output type: `g` together with a proof that `Div(g) = Div(a) ∩ Div(b)`. -/
def Gcd (a b : Nat) := { g : Nat // ∀ d, d ∣ g ↔ d ∣ a ∧ d ∣ b }

/-- The one lemma: one step of Euclid does not change the set of common divisors.
    (`x % y = x - q*y`, so a common divisor of `y` and `x % y` divides `x`, and back.) -/
theorem step_keeps_common_divisors (x y d : Nat) :
    (d ∣ y ∧ d ∣ x % y) ↔ (d ∣ x ∧ d ∣ y) := by
  constructor
  · intro ⟨hy, hm⟩; exact ⟨(Nat.dvd_mod_iff hy).mp hm, hy⟩
  · intro ⟨hx, hy⟩; exact ⟨hy, (Nat.dvd_mod_iff hy).mpr hx⟩

/-- Euclid's algorithm. The *type* is the specification; the body is the proof. -/
def euclid (x : Nat) : (y : Nat) → Gcd x y
  | 0 =>      -- exit: every d divides 0, so the common divisors of (x, 0) are just Div(x)
    ⟨x, fun d => ⟨fun h => ⟨h, Nat.dvd_zero d⟩, fun h => h.1⟩⟩
  | y + 1 =>  -- step: recurse on (y+1, x % (y+1)); its common divisors are ours
    let ⟨g, hg⟩ := euclid (y + 1) (x % (y + 1))
    ⟨g, fun d => (hg d).trans (step_keeps_common_divisors x (y + 1) d)⟩
termination_by y => y
decreasing_by exact Nat.mod_lt _ (Nat.succ_pos _)

-- The value is the ordinary gcd, and the proof is erased at run time:
#eval (euclid 12 8).val    -- 4
#eval (euclid 1071 462).val -- 21
#eval (euclid 0 0).val     -- 0  (every number divides 0, so Div(0) = Div(0) ∩ Div(0))

/-- Sanity: the type pins the answer down uniquely (divisibility is antisymmetric on ℕ). -/
theorem gcd_type_is_a_singleton (a b : Nat) (g h : Gcd a b) : g.val = h.val :=
  Nat.dvd_antisymm ((h.property g.val).mpr ((g.property g.val).mp (Nat.dvd_refl _)))
                   ((g.property h.val).mpr ((h.property h.val).mp (Nat.dvd_refl _)))

/-- And it agrees with the library's `Nat.gcd`. -/
theorem euclid_eq_nat_gcd (a b : Nat) : (euclid a b).val = Nat.gcd a b :=
  gcd_type_is_a_singleton a b (euclid a b)
    ⟨Nat.gcd a b, fun _d => ⟨fun h => ⟨Nat.dvd_trans h (Nat.gcd_dvd_left a b),
                                      Nat.dvd_trans h (Nat.gcd_dvd_right a b)⟩,
                            fun ⟨ha, hb⟩ => Nat.dvd_gcd ha hb⟩⟩
