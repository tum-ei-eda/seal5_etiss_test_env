# Shared workflow actions

Local actions require the repository to be checked out first. Keep cache decisions,
artifact naming, matrix configuration, and publishing in the calling workflow.

## Install Ubuntu dependencies

```yaml
- uses: actions/checkout@v7
- uses: ./.github/actions/install-apt
  timeout-minutes: 15
  with:
    packages: cmake make libboost-system-dev
    # Optional; used by the S4E workflow before installing LLVM 15:
    # remove-packages: llvm-* clang-* libllvm* libclang*
```

Uses the Ubuntu archive mirror for runner mirror files and legacy Azure source
URLs. APT retries three times with 30-second HTTP/HTTPS connection timeouts.
The caller's step timeout bounds the entire operation, including slow streams.
Package lists are space-separated; removal patterns are passed literally to APT.
Installation uses `--no-install-recommends`.

## Restore submodule refs

```yaml
- uses: ./.github/actions/restore-refs
  if: ${{ needs.check.outputs.num_changed != '0' && success() }}
```

Downloads `refs-patch` (override with `artifact-name`) containing
`update_refs.patch`, applies it with `git am`, updates submodules recursively,
then restores the original HEAD and leaves the updated refs unstaged. Requires
Git identity to be configured and the parent commit to be available, as in the
existing workflows with `fetch-depth: 0`. The temporary patch is removed after
success. The caller must skip this action when no refs patch was produced.

## Set up M2-ISA-R

```yaml
- uses: ./.github/actions/setup-m2isar
  with:
    python-version: '3.10'
    source-dir: M2-ISA-R
    summary-message: M2-ISA-R ready
```

Requires `virtualenv` and the requested Python to be installed. Creates
`<source-dir>/venv` and installs the checked-out source in editable mode. Later
shell steps still need to activate that virtual environment themselves.
`source-dir` defaults to `M2-ISA-R`; the summary message is optional.

## Build ETISS

```yaml
- uses: ./.github/actions/build-etiss
  with:
    source-dir: etiss
    build-dir: etiss/build
    install-dir: etiss/build/install
    build-type: Release
    # Optional settings used by the default workflow:
    compiler-launcher: sccache
    coredsl-coverage: 'ON'
    filelogger-plugin-dir: etiss_riscv_tests/FileLoggerPlugin
    log-file: etiss_compile_out.txt
```

Configures, builds, and installs the checked-out source using CMake. Paths are
relative to the workspace unless absolute. The first four inputs above show
the defaults. `jobs` defaults to `nproc`; set it to limit build parallelism.
An empty compiler launcher or coverage input leaves the corresponding CMake
option unspecified. Plugin linking is optional and expects the source directory
to contain `PluginImpl`; an existing FileLoggerPlugin link causes failure, as in
the original workflow.

When `log-file` is supplied, CMake stdout and stderr are appended to that file
and streamed to the job log. Every failed phase stops the action and prevents
later phases from running, including when output is piped through `tee`.
Cache decisions, patching, compiler-launcher installation, failure summaries,
and artifact uploads remain the caller's responsibility.

## Set up LLVM

```yaml
- uses: ./.github/actions/setup-llvm
  with:
    version: '19.1.1'
    platform: x86_64-linux-gnu
    os: ubuntu-22.04
    install-dir: llvm
    enable-summary: true
```

Downloads the matching `clang+llvm` archive from the existing
`PhilippvK/riscv-tools` releases and extracts it without stripping directories.
Tar preserves the executable permissions. `version` is required; the example
shows defaults for the other inputs. Installation paths are relative to the
workspace unless absolute. The destination must not already exist. Cache
restoration and cache-hit conditions stay in the caller.

## Build RISC-V ISA tests

```yaml
- uses: ./.github/actions/build-riscv-tests
  with:
    xlen: '32'
    source-dir: riscv-tests
    gnu-dir: gnu
    riscv-prefix: riscv64-unknown-elf-
```

Runs `autoconf`, `./configure`, and `make isa` in the source tree, placing the
GNU toolchain's `bin` directory first on PATH. `xlen` is required. `jobs` defaults
to `nproc`. Other example inputs show their defaults. The build remains in the
source tree so the caller can cache and upload `riscv-tests/isa` as before.

Combined output is appended to `log-file` (default
`riscv-tests/etiss_riscv_tests_build_out.txt`, relative to the workspace).
A failed phase stops the build; the action writes its log to the failure summary
unless `enable-summary: false` is passed. Cache handling and artifact uploads
remain in the caller.

## Run RISC-V ISA tests

```yaml
- uses: ./.github/actions/run-riscv-tests
  with:
    arch: RV32IMACFD
    xlen: '32'
    extensions: imacf
    jit: TCC
```

Creates and activates `etiss_riscv_tests/venv`, installs the runner requirements,
makes the ETISS executable runnable, and invokes `test.py` from the workspace.
Required inputs are `arch`, `xlen`, and `extensions`. Optional path inputs are
`runner-dir` (default `etiss_riscv_tests`), `tests-dir` (`riscv-tests/isa`), and
`etiss-exe` (`etiss/build/install/bin/bare_etiss_processor`).

The execution defaults match the existing workflow: `jit: TCC` (converted to
lowercase), `virt: p`, `runlevel: msu`, `timeout: '20'` seconds per test, and
`keep-output: both`. Combined output is appended to `log-file` (default
`etiss_riscv_tests_run_out.txt`). Runner failures propagate through `tee`.
The runner's `results_*` directories remain in the workspace. Expected-failure
filtering, result summaries, and artifact uploads stay in the caller.

## Validation

From the repository root, run `python3 scripts/check_composite_actions.py`
(requires PyYAML). It checks Bash syntax and exercises the scripts with temporary
APT fixtures, command shims, a real temporary Git repository, and a small real
CMake project. It also checks ETISS build options and failure propagation. It does not
install packages or modify the host's APT configuration.

Run `python3 scripts/check_toolchain_test_actions.py` for the LLVM and RISC-V test
actions. It exercises real archive extraction with a local executable fixture,
both target widths, runner argument compatibility, and download/build/runner
failure handling using command shims. It performs no network requests.

## Generate LLVM with Seal5

```yaml
- uses: ./.github/actions/setup-seal5
  with:
    python-version: '3.10'
- uses: ./.github/actions/generate-seal5
  with:
    cdsl-dir: riscv-coredsl-extensions
    llvm-dir: ${{ github.workspace }}/seal5_llvm
    out-dir: ${{ github.workspace }}/seal5_out
    llvm-ref: llvmorg-19.1.7
    build-config: release
```

Setup requires `virtualenv` and installs the checked-out `seal5` source and its
requirements into `seal5/venv`. Both actions accept `source-dir`. Generation
accepts `demo-script` (default `examples/s4e_demo.py`, relative to the source),
`patch-file` (default `llvm.patch`), and the inputs shown above. Other paths are
relative to the workspace unless absolute. The demo runs with tests, install,
and export enabled; errors stop generation before patch/archive creation.
It writes a diff against `llvm-ref` and archives the LLVM tree to
`<llvm-dir>.tar.xz`, including the build products. Cache both the archive and
patch in the caller, and unpack the archive at the same absolute location on a
cache hit. Artifact uploads and publishing stay in the workflow.

The shared `build-examples` action also accepts `toolchain-file` for example
repositories without CMake presets. When supplied, it uses that file and
`build-type` instead of a preset. `llvm-dir/bin` is placed on PATH for toolchain
files that resolve Clang by name, as the S4E examples do.

Run `python3 scripts/check_s4e_actions.py` for offline Seal5 generation checks,
including patch creation, real archive round trips, and failure propagation.
It also checks local action inputs in the S4E workflow and Bash syntax across
the shared actions. It does not build LLVM.
