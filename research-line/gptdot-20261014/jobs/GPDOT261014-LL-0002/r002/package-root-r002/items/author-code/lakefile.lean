import Lake
open Lake DSL

require mathlib from git "https://github.com/leanprover-community/mathlib4" @ "a988e8b369e20ae90b4998923e4efcd732a1da62"

package «steinberg» where
  -- add package configuration options here

lean_lib «Steinberg» where
  -- add library configuration options here

@[default_target]
lean_exe «steinberg» where
  root := `Steinberg
