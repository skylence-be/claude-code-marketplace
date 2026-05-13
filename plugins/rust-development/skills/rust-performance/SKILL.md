---
name: rust-performance
description: Rust performance: flamegraph/criterion, pre-allocation, &str vs Cow, dyn Trait. Use when optimizing hot paths.
---

# Rust Performance

## When to Use This Skill

- Writing performance-critical code paths
- Setting up benchmarks with `criterion` to measure before and after
- Reviewing code for avoidable allocations in hot paths
- Choosing between `String`, `&str`, `Cow`, `SmolStr`, and `Arc<str>`
- Understanding when `Box<dyn Trait>` costs more than generics
- Profiling with `cargo-flamegraph` or `perf`

## Core Concepts

| Concept | Rule |
|---------|------|
| **Profile first** | Never optimize without a benchmark or flamegraph; guessing is almost always wrong |
| **Allocations are expensive** | Every `String::new`, `Vec::new`, `Box::new` touches the allocator; minimize in hot loops |
| **Borrow over own in hot paths** | `&str` over `String`, `&[T]` over `Vec<T>` avoids clones and allocations |
| **Pre-allocate** | `Vec::with_capacity(n)`, `String::with_capacity(n)`, `HashMap::with_capacity(n)` when size is known |
| **`dyn Trait` has indirection cost** | Virtual dispatch prevents inlining; use generics on hot paths |
| **`#[inline]` judiciously** | Small, frequently called functions benefit; large functions or rarely-called ones do not |
| **`strconv` idiom** | Use `itoa`, `ryu`, or `std::fmt::Write` over `format!()` for numeric-to-string in hot paths |

## Quick Reference

```rust
// Pre-allocate when size is known
let mut buf = Vec::with_capacity(items.len() * 8);
let mut out = String::with_capacity(512);

// Reuse allocations across iterations
let mut buf = Vec::new();
for item in items {
    buf.clear();                     // reuse allocation; no heap round-trip
    serialize_into(&mut buf, item);
    send(&buf);
}

// &str over String in hot-path function signature
fn count_words(text: &str) -> usize {     // not: fn count_words(text: String)
    text.split_ascii_whitespace().count()
}

// Cow for sometimes-owned: zero allocation on the common path
use std::borrow::Cow;
fn normalize<'a>(s: &'a str) -> Cow<'a, str> {
    if s.contains("  ") { Cow::Owned(s.replace("  ", " ")) }
    else                 { Cow::Borrowed(s) }
}

// SmolStr for short, immutable, frequently-copied strings (avoids heap on <=22 bytes)
use smol_str::SmolStr;
let key: SmolStr = "my-config-key".into();

// Benchmark with criterion
use criterion::{criterion_group, criterion_main, Criterion};
fn bench_normalize(c: &mut Criterion) {
    c.bench_function("normalize clean", |b| {
        b.iter(|| normalize("hello world"))
    });
}
criterion_group!(benches, bench_normalize);
criterion_main!(benches);
```

## Profiling Workflow

1. **Benchmark first.** Write a `criterion` benchmark that exercises the suspected hot path.
2. **Get a flamegraph.** `cargo flamegraph --bin my-app -- <args>` (requires `perf` on Linux or `dtrace` on macOS).
3. **Read the flamegraph top-down.** Wide bars are where time is spent; narrow bars high in the stack are not worth optimizing.
4. **Measure the fix.** Run the benchmark again; if the improvement is under noise, revert.

## When to Use Small-String Types

| Type | When |
|------|------|
| `&str` | Read-only reference; zero cost |
| `String` | Owned, dynamic length |
| `Cow<'_, str>` | Sometimes borrowed, sometimes owned; avoids clone on the common path |
| `SmolStr` | Short identifiers, keys, or labels that are frequently cloned; inline storage up to 22 bytes |
| `Arc<str>` | Immutable string shared across many owners; single heap allocation, cheap clone |
| `Box<str>` | Immutable owned string; smaller than `String` (no capacity field) when length is fixed |

## Best Practices

1. **Benchmark before and after every optimization.** Perceived improvements without numbers are not improvements.
2. **Look at allocations, not just CPU time.** `dhat` or `heaptrack` surfaces allocation pressure that flamegraphs miss.
3. **`extend` over repeated `push`.** `vec.extend(iter)` is faster than a loop of `vec.push(item)` because it can batch.
4. **`iterator` chains are often zero-cost.** The optimizer flattens them; don't manually unroll unless profiling shows a gain.
5. **`#[inline(always)]` is rarely needed.** The optimizer inlines aggressively; `#[inline(always)]` can increase binary size and hurt icache.
6. **Reserve `unsafe` for measured wins.** If a safe alternative benchmarks within noise of the `unsafe` version, use the safe one.

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| `format!("{}{}", a, b)` in a loop | `String::with_capacity` + `write!` or `push_str` |
| `to_string()` on every iteration | Pass `&str`; convert once outside the loop |
| Cloning a `Vec` to pass to a function | Pass `&[T]` instead |
| `Box<dyn Trait>` on a path called millions of times | Use a generic `<T: Trait>` parameter; the monomorphized version inlines |
| `HashMap::new()` in a hot path | Move it outside the loop; reuse with `clear()` |
| Sorting inside a loop that processes the same data | Sort once outside; pass a sorted slice |

## Next Steps

- Review `rust-ownership-borrowing` for `Cow`, `Arc`, and borrowing strategies
- Review `rust-unsafe` for when `unsafe` is justified by performance profiling
