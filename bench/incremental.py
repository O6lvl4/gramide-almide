"""The cost of one edit: the same keystroke sequence the other language
packages replay against tree-sitter (a 31-bit LCG seeds positions; every
edit types or deletes one letter six letters into a word of thirteen or
more, so the file stays what it was syntactically), through gramide's
`reparse-bench`, every --verify edits checked against a whole parse.
There is no tree-sitter grammar for Almide to set beside it. Writes the
evidence the README cites.

    python3 bench/incremental.py --edits 1000 --seed 7 --out docs/evidence/incremental-parser-almd.json FILE...
"""
from pathlib import Path
import argparse, hashlib, json, platform, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("--gramide", type=Path, default=Path(__file__).resolve().parent.parent / "gramide_almide")
ap.add_argument("--edits", type=int, default=1000)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--verify", type=int, default=50)
ap.add_argument("--out", type=Path, required=True)
ap.add_argument("files", nargs="+", type=Path)
args = ap.parse_args()
gramide = args.gramide.resolve()

rows = []
for f in args.files:
    f = f.resolve()
    g = subprocess.run([str(gramide), "reparse-bench", str(f), "--edits", str(args.edits), "--seed", str(args.seed), "--verify", str(args.verify)], capture_output=True, text=True)
    if g.returncode:
        rows.append({"path": str(f), "error": g.stderr.strip()[:500]}); continue
    rows.append({"path": str(f), "bytes": f.stat().st_size, "gramide": json.loads(g.stdout.strip().splitlines()[-1])})

report = {"platform": platform.platform(), "edits": args.edits, "seed": args.seed, "verify_every": args.verify,
          "gramide_sha256": hashlib.sha256(gramide.read_bytes()).hexdigest(), "files": rows}
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(report, indent=1) + "\n")
for r in rows:
    if "error" in r: print(r["path"], "ERROR", r["error"][:200]); continue
    g = r["gramide"]
    print(f'{Path(r["path"]).name} ({r["bytes"]:,} B): median {g["median_us"]} us, p90 {g["p90_us"]}, whole {g["whole_parse_median_us"]} us, fallbacks {g["fallbacks"]}, mismatches {g["mismatches"]}, node id breaks {g["node_id_breaks"]}')
