# Workflow: Measuring Gas

Sui's tools for measuring and inspecting gas. These are stable; build whatever measurement system you need on top of them.

## Per-test gas: `sui move test -s`

`sui move test` runs every `#[test]` in the package. The `-s` flag enables statistics — gas used and wall time per test.

```bash
sui move test -s --skip-fetch-latest-git-deps
```

Output is a pretty table by default. For machine-readable output:

```bash
sui move test -s csv --skip-fetch-latest-git-deps
```

The CSV block in stdout starts after a `name,nanos,gas` header line and ends at the `Test result:` summary. Lines in between are `<test_name>,<wall_nanos>,<gas>`.

### Reading the numbers

- The `gas` column is post-rounding (KeepHalfDigits, minimum 1).
- One small test isn't enough resolution. Subtle per-call differences (a few internal-gas units) round to the noise floor. To resolve them, write a test that loops the operation 1000× in a `#[test]` and divide.
- `-i <N>` raises the per-test gas budget (default 5,000,000). Stress tests that loop heavily need a higher limit.

### Capturing a baseline

`sui move test -s csv > before.csv`, make your change, `sui move test -s csv > after.csv`. A diff shows every test that moved. CI hooks can snapshot the table and fail on unexpected changes.

## Bytecode disassembly: `sui move build -d --disassemble`

```bash
sui move build -d --disassemble --skip-fetch-latest-git-deps
```

Output is `.mvb` files under `build/<package>/disassembly/`, one per module. **Important**: `sui move test` overwrites the build directory; run `build --disassemble` *after* any `test` invocation if you need the disassembly.

### What the disassembly tells you

For each function, you get:

1. **Header** with the function signature.
2. **Local declarations** (`L0: name#a#b: Type`).
3. **Blocks `B0:`, `B1:`, ...** containing sequential bytecode instructions.

The local declarations are the most useful single source of optimization signal. Locals fall into three groups by name prefix:

- **Letter prefix** (`x#1#0`, `pnl#1#0`): developer-named `let` binding.
- **`%` prefix** (`%#1`, `%#13`): HLIR-inserted temp. From `move-compiler/src/hlir/translate.rs`:`TEMP_PREFIX = "%"`. These appear from named-block binders (any value-returning macro in a binop context), `process_binops` LHS hoists (evaluation-order safety), and similar internal patterns. **Each one usually represents an avoidable `StLoc` + `MoveLoc` pair.**
- **`$` prefix** (`$stop#0#3`): macro parameter substitution slot. The macro expander wraps each `$param` reference in a Block, which lowers to its own `StLoc`/`MoveLoc` shuffle.

A function with zero `%`- or `$`-prefixed locals has no compiler-introduced binders. A function with several has either complex macro/binop interaction or branch-convergence overhead.

### Reading bytecode

The disassembly opcodes are mostly self-evident. The non-obvious ones:

| Opcode | What it does | Cost shape |
| --- | --- | --- |
| `LdU256(v)` | Push the literal `v` | size += 1 byte (per `Type::size()`) |
| `LdConst[i]` | Push the constant at pool index `i` | size += BCS-serialized length (32 bytes for u256) |
| `CopyLoc[i]` | Push a copy of local `i` | size += value's abstract memory size |
| `MoveLoc[i]` | Push local `i` and mark slot empty | size += value's abstract memory size |
| `StLoc[i]` | Pop top of stack into local `i` | size -= popped value size |
| `Add` / `Sub` / `Xor` / etc | Pop 2, push 1 | conservatively-typed |
| `Call <fn>` | Call a function | 1 inst + arg push/pop |
| `BrFalse(N)` | Pop bool; if false, jump to instruction N | 1 inst |

A binder shuffle for a u256 macro result looks like:

```
... compute value ...
StLoc[X](%#1: u256)
... maybe more work ...
MoveLoc[X](%#1: u256)
... consume value ...
```

In a healthy version, the value would stay on the stack and the surrounding op would consume it directly — no `StLoc`/`MoveLoc`.

## Per-module bytecode sizes: `.mv` file headers

The compiled `.mv` files in `build/<package>/bytecode_modules/` are BCS-serialized `CompiledModule`s. The binary header lists every non-empty table by `(kind, offset, size)`. Each table is independently sized.

### Header format

```
[magic: 4 bytes = 0xA1 0x1C 0xEB 0x0B]   # 0xDE 0xAD 0xC0 0xDE for unpublishable
[version: u32 LE = 4 bytes]
[table_count: ULEB128]
for each non-empty table:
  [kind: u8]
  [offset: ULEB128]
  [size: ULEB128]
[table contents...]
[self_module_handle_idx: ULEB128]
```

`kind` values (from `move-binary-format/src/file_format_common.rs` `TableType`):

| Kind | Table |
| --- | --- |
| 0x01 | module_handles |
| 0x02 | datatype_handles |
| 0x03 | function_handles |
| 0x04 | function_instantiations |
| 0x05 | signatures |
| 0x06 | constant_pool |
| 0x07 | identifiers |
| 0x08 | address_identifiers |
| 0x0A | struct_defs |
| 0x0B | struct_def_instantiations |
| 0x0C | function_defs |
| 0x0D | field_handles |
| 0x0E | field_instantiations |
| 0x0F | friend_decls |
| 0x10 | metadata |
| 0x11 | enum_defs |
| 0x12 | enum_def_instantiations |
| 0x13 | variant_handles |
| 0x14 | variant_instantiation_handles |

`function_defs` is the bytecode bodies of all functions. `identifiers` is symbol names. `constant_pool` is `LdConst` data.

### Why per-table sizes matter

The on-chain package size formula in `sui-types/src/move_package.rs::MovePackage::size()` sums `module_bytes_len` across all modules in a package. The 100 KiB mainnet limit blocks `publish` and `upgrade` when crossed. When a package approaches the limit, knowing **which** table is growing tells you what to do: `function_defs` growth → bytecode bloat (look at the largest functions); `identifiers` growth → too many distinct symbols; `constant_pool` growth → too many large constants (convert hot ones to macros).

### Dev vs. publishable builds

`sui move build -d` produces publishable `.mv` files: `#[test_only]` functions are stripped out. Without `-d` the package may fail to build at all if it uses dev-only dependencies. **Magic bytes `0xA1 0x1C 0xEB 0x0B` = publishable; `0xDE 0xAD 0xC0 0xDE` = unpublishable.** The latter appears under `sui move build --test` or `sui move test`, both of which include test-only code.

For tracking on-chain size, use `sui move build -d` and read the publishable `.mv` files. Anything measured under `--test` or via `sui move test` is inflated by test-only code.

## Workflow: snapshot tables

Every Aftermath move package now hosts a `tables/` directory at repo root with a small set of CSV snapshots, generated by scripts in `scripts/`. The current set:

- `tables/gas.csv` — per-test gas.
- `tables/unexpected-locals.csv` — per-function count of `%`- and `$`-prefixed locals.
- `tables/package-size.csv` — per-(module, table) `.mv` byte sizes.

An orchestrator (`scripts/update-tables.py`) runs `sui move test -s csv` and `sui move build -d --disassemble`, then feeds outputs to per-table parsers. Two modes:

- `--write`: regenerate every table (developer flow).
- `--check`: verify every table matches the current code (CI flow).

The orchestrator is the only thing that runs `sui`. A pinned version lives in `tables/sui-version.txt` and the orchestrator refuses to run on a mismatch. This keeps measurements comparable across machines and over time.

If the table system isn't present in a repo, copy it from an Aftermath Move repo that already has it, or build the same idea using the underlying sui commands above. The system is a current best guess; the underlying sui flags and `.mv`/`.mvb` formats are stable.

## When to reach for which tool

| Goal | Tool |
| --- | --- |
| "Did my change move gas?" | `sui move test -s csv`, diff before/after |
| "Where is the binder/shuffle overhead in this function?" | Disassembly: read `.mvb`, look at the local list |
| "Is this package near the 100 KiB limit?" | `.mv` file headers; sum per-table sizes |
| "Which functions have unexpected compiler-inserted locals?" | Grep `.mvb` for `^L\d+:\s*[%$]` |
| "Is this `--check` failure a real change or noise?" | Run `--check` twice; if numbers are stable, it's real |
