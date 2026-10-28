# invoice-coding-eval

A darkmux eval of accounts-payable work. A model is given a small business's
cost-code chart, its coding policy and a batch of 50 vendor invoices, and
replies with one JSON object that gives each invoice one cost code. The reply
is graded exactly against an answer key.

The business, a bike shop called Copperleaf Cycle Works, is invented, as are
its vendors and every invoice. Nothing here is real financial data.

## At a glance

| | |
| --- | --- |
| Kind | Structured output: no tools; the model reads one text and replies with one JSON object |
| Version | 1.0 (tag `1.0`, commit `e2406af`) |
| Criteria | One graded field per invoice, 50 per batch; a batch passes when every invoice gets the right code, and the run records how many did |
| Results | [evals.darkmux.com/evals/invoice-coding-eval](https://evals.darkmux.com/evals/invoice-coding-eval) |
| Needs | darkmux 5.9.0 or later |
| License | MIT |

The eval's page on evals.darkmux.com names the approved commit.

## What the model is given

Each batch is one text, `inputs/batch-NN.txt`: the chart and policy from
`chart/cost-codes.md` (34 cost codes and 8 coding rules), then 50 invoices,
each starting with `=== INVOICE <number> ===`. The model runs as the eval's own
`ap-coder` role, whose instructions ask for a flat JSON object mapping each
invoice number to its four-digit code. The role lives in `eval/roles/` and is
pinned by `role_sha256` in `evals/invoice-coding.json`.

The invoices are written to test the policy, not only the chart: a vendor that
sells something other than what it usually sells, equipment priced either side
of the $2,500.00 line, freight billed on its own invoice, consumables bought
for resale, expenses billed months ahead, deposits, and repairs coded by what
was repaired.

## The four batches

There are four workloads, one per batch of 50 invoices:

| Workload | Input |
| --- | --- |
| `invoice-coding-batch-01` | `inputs/batch-01.txt` |
| `invoice-coding-batch-02` | `inputs/batch-02.txt` |
| `invoice-coding-batch-03` | `inputs/batch-03.txt` |
| `invoice-coding-batch-04` | `inputs/batch-04.txt` |

`tools/generate.py` wrote every batch once, from a fixed seed (20261028), and
the results are committed with their hashes in `SHA256SUMS`, so nothing is
generated on the machine that runs the eval. `invoices/` holds the same
invoices one file each, for reading.

## Run it with darkmux

```bash
git clone https://github.com/kstrat2001/invoice-coding-repo
cd invoice-coding-repo
git checkout <approved commit>     # named on the eval's page
darkmux lab fixture register .
darkmux lab run invoice-coding-batch-01 -p <profile>
darkmux run inspect <run id>       # the verdict, time and turns
```

Run the other batches the same way. A model may reply until its context window
is full. The room for the reply is the profile's context window less the
prompt; both are recorded with the run, because context is part of the
machine's configuration, not the eval's.

Leave the checkout unchanged: a run from any other commit, or from a checkout
with changes in it, cannot be shared. To share runs on evals.darkmux.com, run
`darkmux lab submit <run id> [<run id>...] --dry-run` to see exactly what would
be sent, then the same command without `--dry-run`. The
[share-runs guide](https://darkmux.com/guide/share-runs.html) covers upload
access and what a bundle carries.

## Grading

Each lab workload in `eval/workloads/` carries its batch's answers as
`verify.expect`: one field per invoice number, accepting the code as a string
or a number. A batch passes when all 50 match; the number that matched is
recorded beside the verdict. `eval/answer-key.json` is the answer key with each
invoice's kind and the policy rules it tests, and `eval/grade.py <batch>
<reply file>` is the standard-library reference grader, which also breaks the
misses down by policy rule.

## The eval is defined here

This repository defines the whole eval: `eval/` holds the workloads, the
answer key, the reference grader and the role. darkmux processes the eval; it
does not define it. Each run reports the sha256 of the workload document and
role files it used.

## License

MIT. See `LICENSE`.
