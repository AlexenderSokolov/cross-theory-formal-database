#!/usr/bin/env python3
"""Compile one assembled material using its own packaged BibTeX styles."""
import argparse
import json
import os
from pathlib import Path
import sys

P = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(P.parents[1] / "corpus-work/scripts"))
import prepared_delivery as delivery

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--job", type=Path, required=True)
parser.add_argument("--resume", action="store_true")
args = parser.parse_args()
job = args.job.resolve()
state = json.loads((job / "job-state.json").read_text())
package = job / state["package"]
row = json.loads((package / "manifest.json").read_text())["items"][0]
item_dir = (package / row["item_path"]).parent
os.environ["BSTINPUTS"] = str(item_dir) + os.pathsep + os.environ.get("BSTINPUTS", "")
os.environ["BIBINPUTS"] = str(package) + os.pathsep + os.environ.get("BIBINPUTS", "")
sys.argv = [sys.argv[0], "compile-job", *sys.argv[1:]]
raise SystemExit(delivery.main())
