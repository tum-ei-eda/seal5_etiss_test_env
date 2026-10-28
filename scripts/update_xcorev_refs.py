"""Apply a supported upstream dispatch to the corresponding pinned submodule."""

import json
import os
from pathlib import Path
import re
import subprocess


SOURCES = {
    "xcorev-cdsl": "CoreV_ISA_CoreDSL",
    "m2isar": "M2-ISA-R",
    "etiss": "etiss",
    "examples": "etiss_riscv_examples",
}


def update(event):
    payload = event["client_payload"]
    source = payload["from"]
    if event["action"] != f"{source}-event" or source not in SOURCES:
        raise ValueError("Unsupported dispatch source/event combination")
    ref = payload["ref"]
    if not isinstance(ref, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", ref):
        raise ValueError("Dispatch ref must be a full commit SHA")
    repo = SOURCES[source]
    subprocess.run(["git", "-C", repo, "fetch", "origin", ref], check=True)
    subprocess.run(["git", "-C", repo, "checkout", "--detach", ref], check=True)
    subprocess.run(["git", "-C", repo, "submodule", "update", "--init", "--recursive"], check=True)
    subprocess.run(["git", "add", repo], check=True)
    return source


if __name__ == "__main__":
    source = update(json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text()))
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        output.write(f"source={source}\n")
