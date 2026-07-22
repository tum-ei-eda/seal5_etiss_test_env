## CI/CD Triggers


### Types of events/triggers

The trigger types are used by GitHub to decide which workflows to execute in case of a `repository_dispatch` event:

```yaml
on:
  repository_dispatch:
    types: [cdsl-event, seal5-event, etiss-event, m2isar-event, examples-event]
```

In the following the currently used triggers and their source repository are listed:

- `cdsl-event` (https://github.com/tum-ei-eda/etiss_arch_riscv)
- `etiss-event` (https://github.com/tum-ei-eda/etiss)
- `m2isar-event` (https://github.com/tum-ei-eda/M2-ISA-R)
- `examples-event` (https://github.com/tum-ei-eda/etiss_riscv_examples)
- `riscv-tests-event` (https://github.com/tum-ei-eda/riscv-tests)
- `etiss-riscv-tests-event` (https://github.com/tum-ei-eda/etiss_riscv_tests)
- `seal5-event` (https://github.com/tum-ei-eda/seal5)
- `s4e-cdsl-event` (https://github.com/tum-ei-eda/riscv-coredsl-extensions)
- `s4e-examples-event` (https://github.com/tum-ei-eda/etiss_riscv_examples_s4e)

**TODO:** add etiss-arch-plugins-event?


### Workflows sending out triggers

Triggers can be send out by one of the following CI/CD workflows:

- `trigger.yml`: Triggered by a push on the default branch. A workflow run is this repository is started using the SHA (Commit Ref) causing the trigger. In case the run was successful and relevant changes are detected, a PR is automatically created within this repository to update the submodule reference to the new HEAD.
- `pr_trigger.yml`: Triggered if a PR branch is created/updated and waits for completion to report success/failure within PR context.

Each of the repositories listed above should have at least the `trigger.yml` workflow on the default branch. The `pr_trigger.yml` is optional.

*Warning:** Do not allow non-default branches to use the trigger workflows. As the submodules can one track one ref we should avoid overriding if from different sources.


### Trigger Payloads

Whenever a workflow shall be triggered, some metadata has to be passed using the `client_payload` field.



Receiving workflows can obtain those values via:

```yaml
- name: Check Payload
  run: |
    echo "github.event.client_payload.ref=${{ github.event.client_payload.ref }}"
    echo "github.event.client_payload.from=${{ github.event.client_payload.from }}"
    echo "github.event.client_payload.is_pr=${{ github.event.client_payload.is_pr }}"
```

*Hint:* Instead of using the event name, to device on the source of the trigger, always check the `from` field in the payload.
