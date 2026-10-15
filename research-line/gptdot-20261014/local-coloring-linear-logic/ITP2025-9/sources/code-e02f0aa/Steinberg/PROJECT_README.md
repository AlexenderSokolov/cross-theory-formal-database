
# Project readme

This document contains a few tips for navigating the Lean code for our paper.

## Organization

The central files to compile are `A3.lean`, `B3Small.lean`, and especially `B3Large.lean`
located in the current directory. These files each pull imports from their respective
`A3`, `B3Small`, and `B3Large` subfolders. In each subfolder, the first file to be imported is
`Defs.lean`, which defines the (graded) "weak" and "full" groups we are trying to reason about,
and the last file to be imported is `Thm.lean`, which concludes with a final theorem statement
named `full_relations_implied_by_weak_relations` which encodes the equivalence of the
(graded) weak and full groups. The second file to be imported in each subfolder is `Basic.lean`, which
uses macros to declare theorems which express all the equalities which hold inside the
(graded) weak groups by virtue of their corresponding sets of relations.

The `A3` and `B3Small` subdirectories only contain these three files. The `B3Large` proof is
much larger and so we opted to split it across several files; the order in which to read
these files is the same as in `B3Large.lean`. The `A3` proof is the simplest.

## Definitions

The main files to look at in the `Defs` subdirectory are:

* `PositiveRootSystem.lean`. This file contains the definitions of the `PositiveRootSystem` and
`PartialChevalleySystem` typeclasses. The latter encodes the data which defines a (sub)set of
Steinberg relations and is the basis for creating all the groups we consider, whether weak or full,
graded or ungraded.

* `GradedPartialChevalleyGroup.lean`. This file defines `GradedChevalleyGenerator`s and
`GradedPartialChevalleyGroup`s, which are (or rather, which build) `PresentedGroup`s on
these generators.

* `DegreeReflection.lean`. This file defines the reflection symmetry which is helpful
for reducing the number of cases we have to consider in some of the proofs.

(In their current state, the files in the `Defs` subdirectory are probably nicer to look at,
versus the files in the other subdirectories.)

## Upstream

These are files which we hope to eventually contribute to Mathlib:

* `PresentedGroup.lean` -- contains some useful lemmas about group presentations. We highlight
`eq_one_of_mem_rels`, which states that the image of a free group element vanishes in a
presented group if that free group element is in the set of relations defining the presented
group, and `toPresentedGroup`, which is used to define homomorphisms between two presented
groups (building on the `toGroup` function already present in Mathlib).
* `Commutator.lean` -- contains numerous identities about commutators which we use regularly
throughout the formalization. Unfortunately, some are redundant with Mathlib; we will clean
this up in the final version of this project.
* `Chevalley/IndicatorMatrix.lean` -- formalizes basic facts about matrices with a single
nonzero entry.
* `Chevalley/TypeA.lean` and `Chevalley/TypeB/TypeB.lean` -- formalize the Steinberg relations
for concrete realizations of type-A and type-B Chevalley groups (cf. Section 2.3 of our
submitted paper). We are not sure about contributing these to Mathlib, because it is
challenging to write general theorems which get the Chevalley constants right in all
cases, particularly the signs. (We do write theorems verifying the signs for our cases in
the `FullValid.lean` files in the `B3Small` and `B3Large` subdirectories.)
