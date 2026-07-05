from pathlib import Path
import sqlite3, json, re, sys

ROOT = Path(__file__).resolve().parents[2]
errors = []

files = [p for p in ROOT.rglob("*") if p.is_file()]
if any(p.name == "txn_enriched.pkl" for p in files):
    errors.append("Working cache txn_enriched.pkl is shipped.")

gt = ROOT / "ground_truth" / "ground_truth.json"
if not gt.exists():
    errors.append("ground_truth.json missing from isolated folder.")
if any(p.name == "ground_truth.json" and p.parent.name != "ground_truth" for p in files):
    errors.append("ground_truth.json duplicated outside isolated folder.")

db = ROOT / "data" / "northbridge.db"
if not db.exists():
    errors.append("northbridge.db missing.")
else:
    con = sqlite3.connect(db)
    cur = con.cursor()
    checks = {
        "transactions": ("SELECT COUNT(*) FROM transactions", 6000),
        "alerts": ("SELECT COUNT(*) FROM alerts", 960),
        "claims": ("SELECT COUNT(*) FROM claims", 180),
        "data_quality_issues": ("SELECT COUNT(*) FROM data_quality_issues", 12),
    }
    for name, (sql, expected) in checks.items():
        actual = cur.execute(sql).fetchone()[0]
        if actual != expected:
            errors.append(f"{name}: expected {expected}, got {actual}")
    con.close()

public_ext = {".md", ".html", ".txt"}
banned = [
    r"\bfraudulent\b", r"\bis guilty\b", r"\bcriminal enterprise\b",
    r"\bsanctioned entity\b", r"\bconfirmed fraud\b", r"\bproven guilt\b"
]
for p in files:
    if p.suffix.lower() in public_ext and "ground_truth" not in p.parts:
        text = p.read_text(errors="ignore").lower()
        for pat in banned:
            if re.search(pat, text):
                errors.append(f"Banned phrase pattern {pat!r} in {p.relative_to(ROOT)}")

readme = (ROOT/"README.md").read_text(errors="ignore")
for required in ["6,000 transactions", "16.0%", "3.0%"]:
    if required not in readme:
        errors.append(f"README missing required control value: {required}")

# Verify markdown-style repository paths that clearly point to package artefacts.
path_tokens = re.findall(r'`([^`\n]+(?:\.md|\.html|\.db|/))`', readme)
for token in path_tokens:
    token = token.rstrip("/")
    if token and not (ROOT/token).exists():
        errors.append(f"README path does not resolve: {token}")

print(f"Files scanned: {len(files)}")
if errors:
    print("QA RESULT: FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)
print("QA RESULT: PASS")
