"""Stdlib reference grader: python3 eval/grade.py <batch> <reply file>.

Reads the reply's first JSON object and compares each invoice's code with the
batch's entry in eval/answer-key.json. Prints fields correct/expected, the
same measure as the lab workload's verify.expect, then the misses broken down
by policy rule (tag), and exits 0 only when every invoice matches.
"""

import json
import sys
from collections import Counter
from pathlib import Path


def first_object(text: str):
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch == "{":
            try:
                value, _ = decoder.raw_decode(text, i)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
    return None


def main() -> int:
    batch, reply_path = sys.argv[1], sys.argv[2]
    key = json.loads((Path(__file__).parent / "answer-key.json").read_text())[batch]
    reply = first_object(Path(reply_path).read_text())
    if reply is None:
        print(f"fields 0/{len(key)}: no JSON object in the reply")
        return 1
    missed = []
    for number, entry in key.items():
        got = reply.get(number)
        got = str(got).strip() if isinstance(got, (str, int)) and not isinstance(got, bool) else None
        if got != entry["code"]:
            missed.append((number, entry, got))
    correct = len(key) - len(missed)
    print(f"fields {correct}/{len(key)}: " + (f"missed {', '.join(n for n, _, _ in missed)}" if missed else "all match"))
    for number, entry, got in missed:
        print(f"  {number}: expected {entry['code']} ({entry['kind']}), got {got}")
    if missed:
        by_tag = Counter(tag or "plain" for _, e, _ in missed for tag in (e["tags"] or [""]))
        print("  misses by rule: " + ", ".join(f"{t} {n}" for t, n in by_tag.most_common()))
    return 0 if not missed else 1


if __name__ == "__main__":
    sys.exit(main())
