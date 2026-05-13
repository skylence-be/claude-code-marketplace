---
name: rust-unsafe
description: Rust unsafe: FFI, raw pointers, MaybeUninit, SAFETY: comments. Use when writing FFI or reviewing unsafe soundness.
---

# Rust Unsafe Code

## When to Use This Skill

- Writing FFI bindings to C or C++ libraries
- Implementing low-level data structures with raw pointers
- Manually implementing `Send` or `Sync` on a type
- Using `MaybeUninit` for zero-initialization avoidance
- Reviewing existing `unsafe` blocks for soundness
- Deciding whether `unsafe` is the right tool or a safe abstraction exists

## Core Concepts

| Concept | Rule |
|---------|------|
| **`// SAFETY:` is mandatory** | Every `unsafe` block and `unsafe fn` must have a `// SAFETY:` comment explaining why the invariants hold |
| **`unsafe_op_in_unsafe_fn`** | Enable this lint so that calling an `unsafe` function inside an `unsafe fn` still requires an explicit `unsafe {}` block and comment |
| **Never bypass the borrow checker** | If `unsafe` is used to "fix" a borrow error, the design is wrong; restructure first |
| **Minimize unsafe surface** | Wrap `unsafe` in the smallest possible safe abstraction; callers should never need to write `unsafe` |
| **Prefer safe alternatives** | `bytemuck` for transmutes, `zerocopy` for zero-copy deserialization, `memoffset` for field offsets |
| **FFI requires validation** | All pointers from C must be checked for null before dereferencing; all lengths must be validated |
| **Manual `Send`/`Sync` requires proof** | Manually implementing these marker traits asserts thread-safety; document why the claim holds |

## Quick Reference

```rust
// SAFETY comment on every unsafe block
fn as_bytes(s: &str) -> &[u8] {
    // SAFETY: str is guaranteed to be valid UTF-8, which is a subset of
    // valid [u8], so reinterpreting the bytes is sound.
    unsafe { std::slice::from_raw_parts(s.as_ptr(), s.len()) }
}

// unsafe_op_in_unsafe_fn: explicit blocks inside unsafe fn
unsafe fn process_ptr(ptr: *const u8, len: usize) {
    // SAFETY: caller guarantees ptr is valid for `len` bytes and not aliased.
    let slice = unsafe { std::slice::from_raw_parts(ptr, len) };
    do_work(slice);
}

// FFI: null check before deref
#[no_mangle]
pub extern "C" fn process(data: *const u8, len: usize) -> i32 {
    if data.is_null() { return -1; }
    // SAFETY: caller guarantees data is valid for len bytes; null checked above.
    let slice = unsafe { std::slice::from_raw_parts(data, len) };
    do_work(slice) as i32
}

// Manual Send + Sync: document the invariant
struct MyHandle {
    ptr: *mut c_void,  // thread-safe by the C library's guarantee (documented in c_lib.h)
}
// SAFETY: The underlying C handle is documented as safe to share and send
// across threads (c_lib_handle_is_thread_safe guarantees this).
unsafe impl Send for MyHandle {}
unsafe impl Sync for MyHandle {}

// MaybeUninit for zero-copy initialization
use std::mem::MaybeUninit;
let mut buf: MaybeUninit<[u8; 1024]> = MaybeUninit::uninit();
let read = fill_buffer(buf.as_mut_ptr() as *mut u8, 1024);
// SAFETY: fill_buffer initialized exactly `read` bytes.
let initialized = unsafe { &(*buf.as_ptr())[..read] };
```

## Safe Abstraction Crates

Before reaching for raw `unsafe`, check whether a maintained safe crate already solves the problem:

| Need | Safe alternative |
|------|-----------------|
| Bit-level type transmutation | `bytemuck::cast`, `bytemuck::cast_slice` |
| Zero-copy deserialization | `zerocopy::FromBytes`, `zerocopy::AsBytes` |
| Field offset arithmetic | `memoffset::offset_of!` |
| Atomic operations | `std::sync::atomic::*` (no unsafe needed) |
| Shared memory across threads | `std::sync::Arc`, `crossbeam` |
| Lock-free data structures | `crossbeam`, `dashmap` |

## When `unsafe` Is Justified

Use `unsafe` only when all of the following are true:

1. A safe abstraction for the operation does not exist.
2. The performance gain (measured by benchmark) cannot be achieved safely.
3. The correctness invariants are clear, finite, and documented in a `// SAFETY:` comment.
4. The unsafe code is wrapped in the smallest possible safe public API.

FFI boundary code always requires `unsafe`; that is unavoidable. Everything else deserves scrutiny.

## Best Practices

1. **Write the `// SAFETY:` comment first.** If you cannot state the invariants clearly, you do not understand the code well enough to write it.
2. **Enable `unsafe_op_in_unsafe_fn`.** It forces explicit `unsafe {}` blocks inside `unsafe fn`, making the dangerous operations visible at a glance.
3. **Test with Miri.** `cargo +nightly miri test` catches undefined behavior that the compiler and sanitizers miss.
4. **Run `cargo-geiger`.** Quantifies the `unsafe` surface across your dependency tree; useful for audits.
5. **Use `#[deny(unsafe_code)]` in libraries.** If your library should have no `unsafe`, enforce it at compile time.
6. **Document invariants in the public API, not just in the `unsafe` block.** Callers of an `unsafe fn` need to know what they must guarantee.

## Common Pitfalls

| Anti-Pattern | Fix |
|-------------|-----|
| `unsafe` to silence a borrow error | Restructure the code; borrow errors are compiler-verified correctness bugs |
| Missing `// SAFETY:` comment | Required; no exceptions. Clippy `undocumented_unsafe_blocks` lint enforces this |
| `mem::transmute` between arbitrary types | Use `bytemuck::cast` which verifies layout compatibility at compile time |
| Manual `impl Send` without thread-safety proof | Document the invariant from the underlying C/system API |
| `*mut T` stored in a struct without a lifetime | Pair with a `PhantomData<&'a mut T>` to express the borrow relationship |
| Large `unsafe` blocks | Minimize to the single line that requires it; extract safe code out |

## Next Steps

- Review `rust-coding-standards` for the `unsafe_code = "warn"` workspace lint setup
- Review `rust-performance` for when `unsafe` optimization is warranted by profiling
