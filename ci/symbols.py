"""Structured ranges for Almide declarations; no model calls."""
from pathlib import Path
import json, subprocess, tempfile
BIN = Path(__file__).resolve().parents[1] / 'gramide_almide'
def symbols(path):
    p = subprocess.run([str(BIN), 'symbols', str(path)], capture_output=True, text=True, check=True)
    d = json.loads(p.stdout); assert d['schema_version'] == 1 and d['complete'] is True
    return d['symbols']
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    almd = root / 'ranges.almd'; almd.write_text('fn real() -> Int = {\n  1\n}\n')
    assert [(s['name'], s['start'], s['end']) for s in symbols(almd)] == [('real', 1, 3)]
    almd.write_text('fn real() -> String = """\nhello\n"""\n')
    assert [(s['name'], s['start'], s['end']) for s in symbols(almd)] == [('real', 1, 3)]
    almd.write_text('// — a multi-byte character above the name\ntype P = { x: Int }\nfn area(p: P) -> Int = p.x\n')
    rows = symbols(almd)
    assert [s['name'] for s in rows] == ['P', 'P.x', 'area'] or [s['name'] for s in rows] == ['P', 'x', 'area'], rows
    raw = almd.read_bytes()
    for s in rows: assert raw[s['start_byte']:s['end_byte']].strip()
    broken = root / 'broken.almd'; broken.write_text('fn real() -> Int = 1\nfn broken(\n')
    p = subprocess.run([str(BIN), 'symbols', str(broken)], capture_output=True, text=True)
    assert p.returncode != 0 and not p.stdout, (p.returncode, p.stdout, p.stderr)
print('Structured ranges passed: blocks, heredocs, UTF-8 above a name, invalid input')
