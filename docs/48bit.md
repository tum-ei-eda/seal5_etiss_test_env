# Experimental 48-bit instruction flow

[48bit.yml](../.github/workflows/48bit.yml) generates `RV32IMACFDK` and
`RV64IMACFDK` and proposes updates to those directories in
`tum-ei-eda/etiss-arch-plugins`, on branch `auto-update-48bit`.
Publication waits for both architectures to pass generation, ETISS compilation,
the shared `run-examples` action (`hello_world`, `dhry`, `example_cpp`), and
the dedicated 48-bit instruction regression. It uses `SEAL5_ACCESS_TOKEN`,
like the Core-V flow. Without that secret, tested plugin artifacts are still
uploaded. Pull requests and dispatches with `is_pr: true` only validate.

The pinned [48bit-riscv-flow](https://github.com/PhilippvK/48bit-riscv-flow)
submodule supplies `cdsl/RVK.core_desc`. Its other submodules are unused and
are not initialized. Base instructions, ETISS support, and the nested pinned
`rv_base` come from `etiss_arch_riscv`, as in the default flow.
No CoreDSL files are duplicated in this CI repository.

`generate_48bit.py` creates a scratch top from the maintained RV32/RV64 top,
adds `RV32K` to both cores, and renames the resulting cores. The extension's
operations use `XLEN`, so the same definitions work with RV64. The scratch
extension adds an explicit modular unsigned cast to `K_ADDI` for strict type
validation. That overlay fails with a review request if the upstream assignment
changes. `generation.json` records the source revisions, input hashes, and
overlay; generated timestamps are normalized.

The ETISS pin includes upstream 48-bit instruction-fetch support (merged in
`44a8dd3035324d2fe3cd65c6b878cb84404df25b`). No simulator patch is applied by
this flow. Both plugins check the required 64-bit instruction word at compile
time, and `generation.json` records this requirement.

The reference implements `k.lli`, `k.addi`, and `k.andi`. Its two
load/store-multiple definitions have empty placeholder behavior and are
retained as supplied; the regression makes no claim to validate those
unimplemented operations. This experimental `K` is the reference's naming,
not the standardized RISC-V cryptography extension.

The ordinary GNU multilib toolchain uses `rv32imafdc`/`ilp32d` and
`rv64imafdc`/`lp64d`. The regression emits 48-bit instructions as raw
halfwords, so a custom compiler is unnecessary. It checks immediate loads,
signed 24-bit addition, modular wraparound, unsigned AND immediates, writes
to `x0`, and mixed 16/32/48-bit instruction streams. RV64 additionally checks
values above 32 bits and zero-extension of the 32-bit immediate load.
The runner requires an explicit `48-bit regression: PASS` output, since a
successful simulator process alone does not prove guest success.

The workflow runs on relevant pushes/PRs, manual dispatch, and repository
dispatch; it has no scheduled trigger. Supported dispatch sources are:

| Event | `client_payload.from` | Updated submodule |
| --- | --- | --- |
| `48bit-cdsl-event` | `48bit-cdsl` | `riscv-48bit-flow` |
| `cdsl-event` | `cdsl` | `etiss_arch_riscv` |
| `m2isar-event` | `m2isar` | `M2-ISA-R` |
| `etiss-event` | `etiss` | `etiss` |
| `examples-event` | `examples` | `etiss_riscv_examples` |

`client_payload.ref` must be a full commit SHA. Successful non-PR dispatches
also propose the tested source pin here on `pr_update_48bit_<source>`.
The sender is in
`riscv-48bit-flow/.github/workflows/trigger.yml`, following the Core-V sender.
Push the sender commit upstream and configure `SEAL5_ACCESS_TOKEN` there to
notify this flow automatically when its sources change. Manual runs use the
committed submodule pin. The existing base/M2-ISA-R/ETISS/example senders use their
existing events.

Local generation, using an installed M2-ISA-R environment:

```sh
git submodule update --init riscv-48bit-flow
git submodule update --init --recursive M2-ISA-R etiss etiss_arch_riscv etiss_riscv_examples
python scripts/generate_48bit.py --xlen 32 --work /tmp/48bit-rv32
python scripts/generate_48bit.py --xlen 64 --work /tmp/48bit-rv64
```

After building/installing ETISS with the generated plugin and building the
examples, run the focused test with:

```sh
python scripts/test_48bit.py --gcc /path/to/gnu/bin/riscv64-unknown-elf-gcc \
  --examples etiss_riscv_examples --etiss /path/to/etiss-install \
  --work /tmp/48bit-regression --arch rv64imafdc --abi lp64d --cpu RV64IMACFDK
```
