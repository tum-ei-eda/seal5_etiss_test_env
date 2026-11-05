"""Compile and execute the 48-bit instruction regression with the generated CPU."""

import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test(gcc, examples, etiss, work, arch, abi, cpu):
    work.mkdir(parents=True, exist_ok=True)
    elf = work / "regression"
    build = examples / "build"
    subprocess.run([str(gcc), f"-march={arch}", f"-mabi={abi}", "-O2",
                    "-L" + str(build / "riscv_crt0"),
                    "--specs=" + str(examples / "etiss-semihost.specs"),
                    "-T", str(build / "etiss.ld"), str(ROOT / "tests/48bit/regression.c"),
                    "-o", str(elf), str(build / "riscv_crt0/libetiss_crt0.a")], check=True)
    ini = (build / "install/ini/hello_world.ini").read_text()
    ini, count = re.subn(r"(?m)^vp\.elf_file=.*$", "vp.elf_file=" + str(elf), ini)
    if count != 1:
        raise ValueError("Expected one ELF path in example INI")
    (work / "regression.ini").write_text(ini)
    with (work / "regression.log").open("w") as log:
        subprocess.run([str(etiss / "bin/bare_etiss_processor"),
                        "-i" + str(work / "regression.ini"), "--arch.cpu=" + cpu,
                        "--jit.type=GCCJIT", "--vp.stats_file_path=" + str(work / "stats.json")],
                       cwd=work, stdout=log, stderr=subprocess.STDOUT, timeout=300, check=True)
    output = (work / "regression.log").read_text()
    print(output)
    # ETISS can exit successfully even when the guest returns a failure code.
    if "48-bit regression: PASS" not in output.splitlines():
        raise RuntimeError("48-bit regression did not report success")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("gcc", "examples", "etiss", "work"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("arch", "abi", "cpu"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    test(args.gcc.resolve(), args.examples.resolve(), args.etiss.resolve(),
         args.work.resolve(), args.arch, args.abi, args.cpu)
