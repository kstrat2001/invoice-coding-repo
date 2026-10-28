"""Stdlib reference grader: python3 eval/grade.py <reply file>.

Reads the reply's first JSON object and compares each invoice's code with
eval/expected.json. Prints fields correct/expected and exits 0 only when all
match, the same rule as the lab workload's verify.expect.
"""

import json
import sys
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
    expected = json.loads((Path(__file__).parent / "expected.json").read_text())
    reply = first_object(Path(sys.argv[1]).read_text())
    if reply is None:
        print(f"fields 0/{len(expected)}: no JSON object in the reply")
        return 1
    missed = []
    for number, code in expected.items():
        got = reply.get(number)
        got = str(got).strip() if isinstance(got, (str, int)) and not isinstance(got, bool) else None
        if got != code:
            missed.append(number)
    correct = len(expected) - len(missed)
    print(f"fields {correct}/{len(expected)}: " + (f"missed {', '.join(missed)}" if missed else "all match"))
    return 0 if not missed else 1


if __name__ == "__main__":
    sys.exit(main())
