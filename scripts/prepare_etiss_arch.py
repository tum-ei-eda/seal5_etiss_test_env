"""Prepare generated architectures for ETISS's header and formatting checks."""

import argparse
from pathlib import Path
import subprocess


def prepare(directory, formatter):
    for header in sorted(directory.glob("*GDBCore.h")):
        source = header.read_text()
        include = '#include "etiss/jit/CPU.h"'
        if include not in source:
            # getInstructionPointer accesses CPU members; GDBCore.h only
            # forward-declares ETISS_CPU when checked as a standalone header.
            anchor = '#include "etiss/IntegratedLibrary/gdb/GDBCore.h"'
            if anchor not in source:
                raise ValueError(f"Missing GDBCore include in {header}")
            header.write_text(source.replace(anchor, anchor + "\n" + include, 1))

    sources = sorted(p for p in directory.rglob("*") if p.suffix in {".c", ".cpp", ".h"})
    if sources:
        subprocess.run([formatter, "-i", *map(str, sources)], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--formatter", default="clang-format")
    args = parser.parse_args()
    prepare(args.directory, args.formatter)
