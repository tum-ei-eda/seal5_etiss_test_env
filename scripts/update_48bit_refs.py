"""Apply a validated 48-bit flow dispatch to its pinned source submodule."""

import json
import os
from pathlib import Path
import re
import subprocess

SOURCES = {
    "48bit-cdsl": "riscv-48bit-flow",
    "cdsl": "etiss_arch_riscv",
    "m2isar": "M2-ISA-R",
    "etiss": "etiss",
    "examples": "etiss_riscv_examples",
}


def update(event):
    payload = event["client_payload"]
    source = payload["from"]
    if source not in SOURCES or event["action"] != f"{source}-event":
        raise ValueError("Unsupported dispatch source/event combination")
    ref = payload["ref"]
    if not isinstance(ref, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", ref):
        raise ValueError("Dispatch ref must be a full commit SHA")
    repo = SOURCES[source]
    subprocess.run(["git", "-C", repo, "fetch", "origin", ref], check=True)
    subprocess.run(["git", "-C", repo, "checkout", "--detach", ref], check=True)
    # The reference's toolchain, simulator and rv_base submodules are unused.
    if source != "48bit-cdsl":
        subprocess.run(["git", "-C", repo, "submodule", "update", "--init", "--recursive"], check=True)
    subprocess.run(["git", "add", repo], check=True)
    return source


if __name__ == "__main__":
    source = update(json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text()))
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        output.write(f"source={source}\n")
