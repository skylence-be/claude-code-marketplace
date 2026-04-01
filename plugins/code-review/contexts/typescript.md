# TypeScript Review Rules

Technology-specific review rules for TypeScript code. Loaded when `.ts` or `.tsx` files are in the changeset or `tsconfig.json` exists.

## Detection
- `.ts` or `.tsx` files in the changeset
- `tsconfig.json` exists in project root
- `package.json` contains `typescript` in `devDependencies`

## Anti-Patterns to Flag

### Using any Type
`any` disables all type checking, defeating the purpose of TypeScript.
- **Severity:** Medium
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `: any`, `as any`, `<any>`, function parameters typed as `any`
- **Fix:** Use `unknown` (for values of unknown shape), specific types, or generics
- **Exception:** Reduce confidence if the codebase has `any` widely (might be intentional migration in progress)

### Unsafe Type Assertions
Using `as` to force a type without validation hides real type errors.
- **Severity:** Medium
- **Pattern:** `value as SpecificType` without prior type narrowing or validation
- **Fix:** Use type guards: `if (isSpecificType(value)) { ... }` or runtime validation with Zod/io-ts

### Non-Null Assertion Without Justification
Using `!` to assert non-null without explaining why the value is guaranteed to exist.
- **Severity:** Medium
- **Pattern:** `object!.property` or `array[0]!` without a preceding null check or comment
- **Fix:** Use optional chaining `object?.property`, add a null check, or add a comment explaining the guarantee

### Non-Exhaustive Switch on Union Types
Switch statement on a discriminated union that doesn't handle all cases.
- **Severity:** High (correctness)
- **Confidence boost:** +2 (known anti-pattern)
- **Pattern:** `switch (status) { case 'active': ...; case 'inactive': ... }` without `default: { const _exhaustive: never = status; }`
- **Fix:** Add exhaustive check: `default: { const _: never = status; throw new Error(\`Unhandled: \${status}\`); }`

### Missing Generic Constraints
Generics without constraints accept `any` implicitly, losing type safety.
- **Severity:** Low
- **Pattern:** `function process<T>(item: T)` where T should be constrained to a specific shape
- **Fix:** Add constraint: `function process<T extends BaseItem>(item: T)`

### Index Signature Abuse
Using `[key: string]: any` instead of proper Record types or Maps.
- **Severity:** Low
- **Pattern:** `interface Config { [key: string]: any }` or loose index signatures
- **Fix:** Use `Record<string, SpecificType>`, `Map<string, SpecificType>`, or explicit properties

### Enum Misuse
Using runtime enums where const enums or union types would be more appropriate.
- **Severity:** Low
- **Pattern:** `enum Status { Active, Inactive }` for simple string sets
- **Fix:** Use union type `type Status = 'active' | 'inactive'` or `const enum` if numeric values are needed
- **Note:** Union types are generally preferred in modern TypeScript for better tree-shaking

### Optional Chaining Abuse
Excessive `?.` chains masking null checks that should be explicit.
- **Severity:** Low
- **Pattern:** `data?.user?.profile?.settings?.theme?.color` — deep optional chains suggest a structural issue
- **Fix:** Validate data shape at the boundary, then access properties confidently
