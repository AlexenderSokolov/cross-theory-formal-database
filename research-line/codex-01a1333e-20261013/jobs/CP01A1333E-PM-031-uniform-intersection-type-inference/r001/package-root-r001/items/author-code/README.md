# uniform-intersection
Equivalence between the simple type system and the uniform non-idempotent intersection type system.

- `stlc.v`
  simple type system
- `nitlc.v`
  uniform non-idempotent intersection type system

Main result in `nitlc_typ.v`: any simply typed lambda-term is equivalently typable in the uniform non-idempotent intersection type system.
```
Theorem nitlc_type_inference M Gamma0 t : stlc Gamma0 M t ->
  exists Gamma A,
    nitlc Gamma M A /\
    Forall2 (fun s u => u <> [] /\ Forall (ssim s) u) Gamma0 Gamma /\
    ssim t A.
```

Verification instructions using Coq 8.19
```
git clone git@github.com:tudo-seal/uniform-intersection.git
cd uniform-intersection
make
```
resulting in `nitlc_type_inference` being `Closed under the global context`.
