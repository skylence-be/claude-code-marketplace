---
name: rust-ownership-borrowing
description: Rust ownership, borrowing, and lifetime patterns covering move vs borrow vs copy, lifetime elision, Cow for sometimes-owned data, Arc vs Rc vs Box, and interior mutability (Cell/RefCell/Mutex/RwLock). Use when designing APIs with lifetime parameters, choosing between owned and borrowed data, or debugging borrow checker errors.
---

# Rust Ownership and Borrowing

## When to Use This Skill

- Designing function signatures that take owned vs borrowed data
- Choosing between `String` and `&str`, `Vec<T>` and `&[T]`, `PathBuf` and `&Path`
- Understanding when lifetime annotations are required vs elided
- Selecting the right interior mutability primitive
- Debugging borrow checker errors about lifetimes or conflicting borrows

## Core Concepts

| Concept | Rule |
|---------|------|
| **Borrow by default** | Accept `&T` or `&str` unless you need to own the value |
| **Move semantics** | Non-`Copy` types transfer ownership on assignment; use `clone()` only when you genuinely need two owners |
| **Lifetime elision** | Most lifetimes are elided; only write `'a` when the compiler cannot infer the relationship |
| **`Cow` for sometimes-owned** | `Cow<'_, str>` accepts both `&str` and `String`; allocates only when mutation is needed |
| **`Box<T>` for heap, single owner** | Recursive types, large stack values, or trait objects (`Box<dyn Trait>`) |
| **`Rc<T>` for shared, single-thread** | Cheap reference counting but `!Send`; use within one thread only |
| **`Arc<T>` for shared, multi-thread** | Atomic reference counting; `Send + Sync` when `T` is |
| **Interior mutability** | `Cell<T>` for `Copy` types, `RefCell<T>` for single-thread runtime borrow checking, `Mutex<T>` for multi-thread |

## Quick Reference

```rust
// Prefer borrowed in function signatures
fn process(name: &str) -> usize { name.len() }       // not: fn process(name: String)
fn sum(values: &[i32]) -> i32 { values.iter().sum() } // not: fn sum(values: Vec<i32>)
fn canonicalize(p: &Path) -> PathBuf { p.join("..") } // not: fn canonicalize(p: PathBuf)

// Cow: accept both &str and String without cloning
use std::borrow::Cow;

fn normalize(input: Cow<'_, str>) -> Cow<'_, str> {
    if input.contains("  ") {
        Cow::Owned(input.replace("  ", " "))
    } else {
        input  // no allocation when already clean
    }
}

// Interior mutability choices
use std::cell::Cell;
use std::cell::RefCell;
use std::sync::{Arc, Mutex};

struct Counter { value: Cell<u32> }          // single-thread, Copy inner
struct Cache   { map: RefCell<HashMap<...>> } // single-thread, non-Copy
struct Shared  { data: Arc<Mutex<Vec<...>>> } // multi-thread

// Lifetime annotation only when elision can't infer it
fn first_word(s: &str) -> &str {              // elision: single input lifetime
    &s[..s.find(' ').unwrap_or(s.len())]
}

struct Tokenizer<'a> {                        // struct holding a borrow needs explicit 'a
    source: &'a str,
    pos: usize,
}
```

## Choosing the Right Pointer Type

| Scenario | Type |
|----------|------|
| Unique ownership, heap allocation | `Box<T>` |
| Shared ownership, single thread | `Rc<T>` |
| Shared ownership, multi-thread | `Arc<T>` |
| Shared mutable state, multi-thread | `Arc<Mutex<T>>` or `Arc<RwLock<T>>` |
| Optional value, nullable pointer | `Option<Box<T>>` |
| Dynamic dispatch, single owner | `Box<dyn Trait>` |
| Dynamic dispatch, shared | `Arc<dyn Trait + Send + Sync>` |

## Best Practices

1. **Borrow first, clone only when needed.** If a function only reads a value, take a reference.
2. **Accept the most general type.** `&str` accepts `String`; `&[T]` accepts `Vec<T>`; `&Path` accepts `PathBuf`.
3. **`Cow` over overloading.** A single `Cow<'_, str>` parameter handles both borrowed and owned inputs.
4. **Avoid `Arc<Mutex<T>>` by reflex.** Ask if `&mut self`, channels, or splitting ownership solves it without shared mutation.
5. **Don't fight the borrow checker by cloning.** A clone that silences an error is often a sign the design has a borrow cycle; restructure the data flow.
6. **Annotate structs holding references.** Structs that store `&T` always need `<'a>` on the struct; the compiler will tell you.

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| `fn f(s: String)` when only reading | `fn f(s: &str)` and callers pass `.as_str()` or `&string` |
| Cloning to resolve a borrow error | Restructure so the borrow ends before the conflicting use |
| `Rc<RefCell<T>>` across thread boundaries | `Rc` is `!Send`; use `Arc<Mutex<T>>` for multi-thread |
| Long-lived `RefCell` borrow that panics | Call `.borrow()` and `.borrow_mut()` in the smallest possible scope |
| `'static` lifetime used broadly to avoid annotations | Use proper lifetime parameters instead; `'static` means forever |
| Storing a reference in a struct without a lifetime | Add `<'a>` to the struct and the reference field |

## Next Steps

- Review `rust-trait-design` for lifetime bounds on trait objects (`dyn Trait + 'a`)
- Review `rust-async-tokio` for `!Send` types and `Arc` patterns in async code
