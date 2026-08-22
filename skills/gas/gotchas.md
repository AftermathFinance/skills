# Gotchas

Non-obvious traps from working on Aftermath's Move codebases. Each entry includes the cause so you can recognize a similar shape elsewhere.

## `#[error]` attributes are stripped through macro parameters

```move
#[error(code = 12001)]
const EOverflow: vector<u8> = b"...";

// Inside a macro:
public macro fun assert_nonneg($x: u256, $err: u64) {
    assert!($x < min_value!(), $err);  // <-- $err loses #[error]
}
```

When the constant flows through a macro param, its `#[error]` annotation is dropped. The abort code still works but the error message lookup may not. **Workaround**: don't pass `#[error]` constants through macro params. Either inline the assert at the call site, or use plain `u64` codes without the attribute on macro-bound errors.

## `assert!(!is_neg!(x), err)` costs an extra instruction

`!cond` lowers as `cond; Not`. Use the positively-stated form when available:

```move
// 2 ops (Ge, Not)
assert!(!is_neg!(x), err);

// 1 op (Lt)
assert!(is_nonneg!(x), err);
```

This is per-call. On a hot path, +1 op × #calls adds up.

This is a very general concept: do not assume the compiler zero-costs anything.

## Macros' `return` is a labeled break, not a function return

```move
public macro fun triple_or($a: bool, $b: bool, $c: bool, $body: || -> ()) {
    'blk: {
        if ($a) { return 'blk };
        if ($b) { return 'blk };
        if ($c) { return 'blk };
        return  // <-- breaks out of macro scope, NOT the caller
    };
    $body();
}
```

`return` inside a `macro fun` translates to `break <return_label>` during expansion. It does NOT return from the enclosing function. Useful for early-exit control flow within a macro, but easy to misread.

## `sui move test` clobbers the disassembly directory

`sui move test` rebuilds in test mode, which overwrites `build/<pkg>/`. Any `.mvb` files produced by an earlier `sui move build --disassemble` are gone. To keep disassembly available for inspection, always run `sui move build -d --disassemble` *after* any test invocation.

## `-d` is needed for the package to build at all in development branches

Many packages have dev-only addresses or dev-only dependencies that fail without `-d`. `sui move build` alone may produce `Unresolved addresses: [...]`. Always use `sui move build -d`. The output is the publishable shape — `#[test_only]` functions are stripped — despite the `-d` flag's name.

## `Type::size()` is 1 for every primitive

Don't expect `u8` arithmetic to cost less than `u256`. The compiler charges 1 byte of stack-size for either. This makes "use smaller types to save gas" advice from other languages a non-rule here.

BCS is smaller for smaller numbers, so it does save on storage costs. Useful for declaring struct fields, etc.

## `LdConst` and `LdU256` look identical but cost 32× different

`const FOO: u256 = ...;` lowers to `LdConst[i]`, which charges the BCS-serialized length (32 bytes for u256). A `public macro fun foo(): u256 { <literal> }` lowers to `LdU256(literal)`, which charges 1 byte. The macro form is dramatically cheaper, and it allows public visibility whereas constants are always private.

## The compiler folds simple constant expressions

`(1u256 + 1)` and `add!(1, 1)` (for a simple `add!` macro) both collapse to `LdU256(2)` at compile time. Microbenchmarks that compute on literals don't reproduce real workload behavior. **Use function parameters, loop counters, or struct reads** to defeat folding.

## Macro-binder shuffle requires a binop to materialize

A naked macro call like `let x = my_macro!(...)` produces no extra binder — the macro result is assigned directly. The binder shuffle appears when the macro result feeds into a *surrounding* binop:

```move
let x = my_macro!(...);                 // no extra binder
let x = my_macro!(...) + something;     // extra binder for the macro AND `something`
acc = acc + my_macro!(...);             // extra binders for both sides
```

When optimizing, check the disassembly to confirm a binder is actually present before "fixing" a non-problem.

## Building inside the wrong directory silently does nothing

`sui move build` without arguments only works from a directory containing `Move.toml` (or a subdirectory of one). Running from a parent of multiple packages produces `Unable to find package manifest at '<cwd>/Move.toml' or in its parents`. Bash sessions in tooling reset cwd between commands; if you're scripting, either pass `-p <package-path>` or chain commands in one shell with `cd ... &&`.

## `sui move build -d --disassemble` writes ONLY non-test modules' `.mvb`

Test-only modules (`#[test_only] module foo;`) get `.mv` and `.mvb` files only under `--test` mode. If you're looking for the disassembly of a test gas-benchmark module, build with `sui move build -d --disassemble --test`. Note this also marks every module's `.mv` as unpublishable (magic = `0xDEADC0DE`).
