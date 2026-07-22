## CI/CD Permissions

Since this flow utilizes a multi-repository CI/CD setup, workloads must have extended permissions to enable:
- Triggering a workflow run on another repository (`repository_dispatch`)
- Push commits/create branches
- Create/update pull requests
- Create/update comments on PRs

An organization-wide token on the `tum-ei-eda` scope is used for this. Hence, all included repositories should belong to the same namespace.

### How to create the access token?

Click on GitHub profile -> Developer Settings -> Personal access tokens -> Fine-grained tokens -> Generate new token

Instead of giving the access token full-access to all repositories, we use a ore fine-grained token limited to the following projects:

**Organization:** `tum-ei-eda`

**Repository access:**

- `tum-ei-eda/seal5_etiss_test_env`
- `tum-ei-eda/etiss`
- `tum-ei-eda/M2-ISA-R`
- `tum-ei-eda/etiss_riscv_tests`
- `tum-ei-eda/etiss_arch_riscv`
- `tum-ei-eda/seal5`
- `tum-ei-eda/etiss_riscv_examples`
- `tum-ei-eda/etiss-arch-plugins`
- `tum-ei-eda/etiss_riscv_examples_s4e`
- `tum-ei-eda/riscv-coredsl-extensions`
- `tum-ei-eda/riscv-tests`
- `tum-ei-eda/CoreV_ISA_CoreDSL`
- `tum-ei-eda/etiss-perf-sim`
- `tum-ei-eda/etiss_riscv_rust_examples`
- `tum-ei-eda/RISCV_ISA_CoreDSL`

Optional:

- `tum-ei-eda/etiss-xvalid-flow`

**Repository permissions:**

The following permissions have to be enabled:

- Actions (read & write)
- Contents (read & write)
- Issues (read & write)
- Metadata (read only)
- Pull requests (read & write)

### How to enter the secrets

The token has to be available as a GitHub Actions secret in all repositories listed above.

A organization-wide secret is enough to be available in all relevent repos:

Open organization page -> Settings -> Secrets and variables -> Actions -> New organization secret

**Name:** `SEAL5_ACCESS_TOKEN`

**Value:** The access token generated above

**Repository access:** Selected repositories (see above)

*Warning:* The name has to match with the one used in all of the CI scripts.

The secrets can be checked per-repo via:

Open repository page -> Settings -> Secrets and veriables -> Actions
