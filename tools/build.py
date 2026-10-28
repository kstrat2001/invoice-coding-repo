"""Build the model input, the answer key and the lab workload from the sources.

The prompt is assembled here, once, and committed with its hash, so nothing is
converted on the machine that runs the eval. Run from the repo root:

    python3 tools/build.py
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = "october"
FIXTURE = "invoice-coding-eval@1.0"
ROLE = "ap-coder"

# The answer key. Each invoice has one right code; the list beside it says
# which rule decides it, for eval/README.md.
ANSWERS = {
    "BW-88213": ("6450", "rule 1 (a parts vendor selling tools) and rule 2 (each tool under $2,500.00)"),
    "RWE-2026-0417": ("1500", "rule 2 ($3,200.00 stand) and rule 3 (its freight goes with it)"),
    "BW-88390": ("5100", "rule 3 (freight on parts for resale is not 6550)"),
    "SPL-55102": ("6300", "rule 4 (software billed ahead is still 6300, not 1400)"),
    "TLP-1107": ("1300", "rule 5 (a refundable deposit is not rent)"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_prompt() -> str:
    parts = [
        (ROOT / "chart" / "cost-codes.md").read_text().rstrip(),
        "",
        "# Invoices to code",
        "",
        f"There are {len(ANSWERS)} invoices in this batch.",
    ]
    for number in ANSWERS:
        parts += ["", f"=== INVOICE {number} ===", "", (ROOT / "invoices" / f"{number}.md").read_text().rstrip()]
    return "\n".join(parts) + "\n"


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    prompt_path = ROOT / "inputs" / f"{BATCH}.txt"
    prompt_path.write_text(build_prompt())

    expected = {number: code for number, (code, _) in ANSWERS.items()}
    write_json(ROOT / "eval" / "expected.json", expected)

    # A code written as a number is still the code: accept 6450 as "6450".
    expect = {number: {"anyOf": [code, int(code)]} for number, code in expected.items()}
    write_json(
        ROOT / "eval" / "workloads" / f"invoice-coding-{BATCH}.json",
        {
            "schema_version": "1.1",
            "workload": {
                "id": f"invoice-coding-{BATCH}",
                "provider": "prompt",
                "role": ROLE,
                "requires_fixture": FIXTURE,
                "promptFile": f"inputs/{BATCH}.txt",
                "replyRoom": "context",
                "verify": {"expect": expect},
            },
        },
    )

    write_json(
        ROOT / "evals" / f"{BATCH}.json",
        {
            "id": f"invoice-coding-{BATCH}",
            "satisfies": f"invoice-coding-{BATCH}@1.0",
            "description": (
                "The model is handed Copperleaf Cycle Works' cost-code chart, its coding policy and five "
                "vendor invoices as one text (assembled once by tools/build.py and committed with its hash) "
                "and replies with one JSON object giving each invoice one cost code. No tools."
            ),
            "role": ROLE,
            "role_sha256": {f"roles/{ROLE}.{ext}": sha256(ROOT / "roles" / f"{ROLE}.{ext}") for ext in ("json", "md")},
            "input": f"inputs/{BATCH}.txt",
            "input_sha256": sha256(prompt_path),
            "reply_room": "context: the run's context window (the profile's n_ctx) minus the prompt. Context is the run's configuration, recorded with it, not part of the eval.",
            "pass": "every invoice gets the code in eval/expected.json (the lab workload in eval/workloads/ carries the same rule, generated from it; eval/grade.py is the stdlib reference). Fields correct out of five are recorded beside the verdict.",
        },
    )


if __name__ == "__main__":
    main()
