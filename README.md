# seal5_etiss_test_env

The [Core-V workflow](.github/workflows/xcorev.yml) generates the
`RV32IMACFDXCoreV` ETISS plugin on relevant pushes and pull requests,
upstream repository dispatches, and through **Run workflow**. There is no
scheduled trigger. [top.core_desc](CoreV_ISA_CoreDSL/top.core_desc) in the Core-V submodule is
adapted from [xmnn-isax-flow](https://github.com/PhilippvK/xmnn-isax-flow)
without XMNN. It uses the pinned `CoreV_ISA_CoreDSL` submodule, which owns
its own `rv_base` submodule and ETISS support definitions. The upstream `XCoreV` instruction set includes
MAC, memory, immediate branches, ALU, bit manipulation, and SIMD; hardware
loops are disabled in that upstream aggregate.

All Core-V CoreDSL files, including the ETISS top-level core definition, live
in `CoreV_ISA_CoreDSL`. `tum_mod.core_desc` and `tum_rva.core_desc` live
alongside `top.core_desc` and import that repository's own pinned `rv_base`.
Its base revision is independent of `etiss_arch_riscv`, which this workflow
does not use. Imports use filenames directly; the generator passes
`CoreV_ISA_CoreDSL/rv_base` using M2-ISA-R's `-I` option. No copies or symlinks
are needed.
Only models and generated output go into the scratch directory.

CI builds and installs ETISS with the generated plugin, then uses the shared
`build-examples` and `run-examples` actions to compile and execute
`hello_world`, `dhry`, and `example_cpp` with GCC JIT. The prebuilt Core-V GCC
20240530 archive is the Ubuntu 22.04 download used by `xvalid-corev-exp/dl`.
Examples use `RISCV_ARCH=rv32im_zicsr_zifencei_xcvmem_xcvmac_xcvalu_xcvbi_xcvbitmanip`
and `RISCV_ABI=ilp32`. Hardware loops are excluded, matching the CoreDSL aggregate.
`setup-gnu` downloads the toolchain and `build-etiss` builds the simulator;
neither LLVM nor a RISC-V toolchain is built from source.

Only after examples pass does CI upload `xcorev-etiss` and propose updates.
Example build/run logs and metrics are retained in `xcorev-examples`, including
on failures. All sources are pinned by this repository.
`generation.json` records the input revisions; generated timestamps are
normalized to avoid changes on otherwise identical runs.

Successful runs outside pull requests and upstream PR dispatches open or update `auto-update-xcorev`
in `tum-ei-eda/etiss-arch-plugins`. Configure `SEAL5_ACCESS_TOKEN` with contents
and pull-request write permissions for that repository to enable publication.
Without it, CI still generates, builds, and uploads the plugin. The workflow
updates only `RV32IMACFDXCoreV`, and does not automatically merge the PR or
advance this repository's plugin submodule pointer.

The workflow accepts `xcorev-cdsl-event`, `m2isar-event`, `etiss-event`, and
`examples-event`, using the existing dispatch payload convention: `from`,
`ref` (full commit SHA), `triggered_run_id`, and optional `is_pr: "true"`.
It checks out the dispatched revision before generation. Successful upstream
push dispatches also propose the validated submodule revision here, on
`pr_update_xcorev_<source>`. Upstream PR dispatches only validate; they do not
publish generated files or propose source updates.

The Core-V sender is in `CoreV_ISA_CoreDSL/.github/workflows/trigger.yml`.
The sender, top and support files, import fixes, and `rv_base` submodule pin
must be committed and merged in that upstream repository, and this repo must
pin the resulting revision.
Configure its `SEAL5_ACCESS_TOKEN` with access to dispatch events to this repo.
The existing M2-ISA-R, ETISS, and examples senders already use the event
types accepted above. This repo's token also needs contents and pull-request
write permissions here for source-reference PRs.

To reproduce generation locally (Python dependencies from `M2-ISA-R` and
clang-format 14 are required):

```sh
git submodule update --init --recursive M2-ISA-R CoreV_ISA_CoreDSL
python -m pip install -e ./M2-ISA-R
python scripts/generate_xcorev.py --work /tmp/xcorev-work
python scripts/prepare_etiss_arch.py /tmp/xcorev-work/output/RV32IMACFDXCoreV --formatter clang-format-14
```

Use a new `--work` directory on each run. Generation uses M2-ISA-R directly;
no Seal5, LLVM, or RISC-V GCC build or download is needed for generation alone.
The CI example checks additionally download the prebuilt Core-V GCC toolchain.
