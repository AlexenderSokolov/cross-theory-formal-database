/-
Copyright (c) 2025 The Steinberg Group
Released under the Apache License v2.0; see LICENSE for full text.
-/

import Mathlib.Tactic.Attr.Register

/-!

Declares class and simp attributes for the Steinberg project.

These attributes are used to tag certain theorem for use in
custom tactics (see `Macro/Group`).

-/


namespace Steinberg

register_simp_attr chev_simps
register_simp_attr height_simps

end Steinberg
