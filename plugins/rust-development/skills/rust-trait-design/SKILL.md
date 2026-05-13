---
name: rust-trait-design
description: Rust trait design covering small focused traits, dyn Trait vs generics tradeoffs, sealed traits, blanket impls, supertraits, GATs, newtypes, and the orphan rule. Use when designing public crate APIs, choosing between static and dynamic dispatch, implementing newtypes, or defining extensible abstractions.
---

# Rust Trait Design

## When to Use This Skill

- Designing the public API of a Rust crate or library
- Choosing between `dyn Trait` (dynamic dispatch) and generics (static dispatch)
- Implementing newtypes to enforce domain invariants
- Sealing a trait so only crate-internal types can implement it
- Deciding when GATs (generic associated types) are worth the complexity
- Understanding the orphan rule and why `impl ForeignTrait for ForeignType` is forbidden

## Core Concepts

| Concept | Rule |
|---------|------|
| **Small, focused traits** | One trait per capability; a trait with 10 methods is usually two or three traits |
| **Accept interfaces, return concretes** | Function parameters take `impl Trait` or `&dyn Trait`; return concrete types |
| **Static over dynamic by default** | Generics are zero-cost and allow inlining; `dyn Trait` is right when the impl set is open at runtime |
| **Sealed traits** | Use a private supertrait to prevent external implementations of a stable trait |
| **Derive before `impl`** | Use `#[derive(Debug, Clone, PartialEq, Eq, Hash)]` before writing manual impls |
| **Orphan rule** | You can only `impl` a trait for a type if you own the trait or the type (or both) |
| **Newtype for foreign traits** | Wrap a foreign type in a newtype to implement foreign traits on it |

## Quick Reference

```rust
// Small, focused traits
pub trait Read {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize>;
}
pub trait Write {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize>;
}
// NOT: pub trait ReadWrite { fn read...; fn write...; fn seek...; fn flush...; }

// Accept trait, return concrete
fn compress<W: Write>(input: &[u8], output: &mut W) { ... }     // static dispatch
fn process(handler: &dyn Handler) { handler.handle(); }         // dynamic dispatch

// Sealed trait: external crates cannot implement Sealed
mod private {
    pub trait Sealed {}
}
pub trait Config: private::Sealed {
    fn value(&self) -> &str;
}
impl private::Sealed for ProdConfig {}
impl Config for ProdConfig { fn value(&self) -> &str { &self.val } }

// Newtype to implement foreign traits
struct Wrapper(Vec<u32>);
impl fmt::Display for Wrapper {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?}", self.0)
    }
}

// Compile-time verification that a type implements a trait
const _: () = {
    fn assert_send<T: Send>() {}
    fn check() { assert_send::<MyService>(); }
};
```

## Newtypes

Introduce a newtype when a primitive has domain meaning callers could confuse or when you need to implement a foreign trait:

```rust
// Domain newtype (non-serialized)
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct UserId(String);

impl UserId {
    pub fn new(s: impl Into<String>) -> Self { Self(s.into()) }
    pub fn as_str(&self) -> &str { &self.0 }
}
impl fmt::Display for UserId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { f.write_str(&self.0) }
}

// Serialized newtype (serde-transparent to preserve wire format)
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
#[serde(transparent)]
pub struct SessionToken(String);
```

Do NOT add `Deref<Target=str>` on domain newtypes; it defeats the type boundary by letting callers treat the newtype as a plain string.

## `dyn Trait` vs Generics

| Factor | Use generics | Use `dyn Trait` |
|--------|-------------|-----------------|
| Impl set known at compile time | Yes | No |
| Monomorphization acceptable | Yes | Avoiding code bloat |
| Object safety needed | No | Yes |
| Stored in a heterogeneous collection | No | Yes |
| Hot path, inlining matters | Yes | No |

## Best Practices

1. **Start with generics.** Reach for `dyn Trait` only when generics won't work (heterogeneous collections, runtime dispatch, object safety).
2. **One method can return `impl Trait` in edition 2021+.** Prefer `-> impl Iterator<Item=T>` over boxing in free functions.
3. **Derive before writing manual impls.** `#[derive(Clone, PartialEq, Eq)]` is less error-prone than manual implementations.
4. **Add `+ Send + Sync` to `dyn` bounds in async/multi-thread code.** `Arc<dyn Trait>` won't compile without it.
5. **Use `#[must_use]` on traits that return results.** Callers that ignore a returned `Result` or important value get a compiler warning.
6. **Verify `Send + Sync` at compile time.** Add a `static_assertions::assert_impl_all!` or equivalent check in tests.

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| Fat traits with 10+ methods | Split into focused traits with clear responsibilities |
| `impl ForeignTrait for ForeignType` | Use a newtype wrapper to satisfy the orphan rule |
| `dyn Trait` without `+ Send` in async code | Add `+ Send + Sync` to the bound: `Arc<dyn Trait + Send + Sync>` |
| `Deref<Target=Inner>` on a domain newtype | Exposes inner API; use `as_inner()` or specific accessor methods |
| GATs for simple cases | GATs add compile complexity; try associated types or generic parameters first |
| Manual `Clone` or `PartialEq` when `#[derive]` works | Derive is less error-prone and auto-updates when fields change |

## Next Steps

- Review `rust-ownership-borrowing` for lifetime bounds on trait objects (`dyn Trait + 'a`)
- Review `rust-async-tokio` for `async_trait` and object-safe async methods
