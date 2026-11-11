# Opt-in 10% Micro-Partition budget: validated candidate

The original formal source ZIP is retained unchanged. The separately named `artifact/DiSMC-source-20261111-budget10-validated.zip` adds one production change: `ExperimentConfig` permits `0.10` when `spark.skyline.budgetDiagnostic=true`. No query engine, selector, numerical predicate or non-Micro-Partition branch is modified. Compared with the recovered historical fixed `ExperimentConfig.java`, the current integrated file also retains its existing frozen-state-load task-order exception; the old class was not copied wholesale over it. The default remains **1%**. Existing explicit diagnostic 2%, 3%, 5% settings remain valid.

The specifically named `DiSMC-source-20261111-budget-fix.zip` was not found in the searched locations. This candidate is instead based on the **recovered historical 10% allowance** and the repository's current 2026-11-02 integrated source. It is not asserted to be that missing ZIP.

## Checks executed

JDK **1.8.0_211**, Spark **3.2.0**, Scala **2.12.15**. Builds and tests ran in independent directories; historical source and results were not overwritten.

| Check | Result |
|---|---|
| Original source + 10% opt-in acceptance assertion | Fails as expected: original validator rejects 10% |
| Candidate compilation | Pass |
| Default 1%; explicit 1%, 2%, 3%, 5%, 10% | Pass under their documented opt-in conditions |
| 10% without diagnostic opt-in | Rejected, as intended |
| Micro config: 0, 1, negative, NaN/infinity, off-list values adjacent to 10% | Rejected by the retained whitelist |
| Planner API boundary 0 and 1; 1%, 5%, 10% | Correct floor-based caps; selected charge within cap |
| Planner negative, >1, NaN, infinity | Rejected |
| Non-micro config compatibility | No budget whitelist added; permissive legacy config behavior retained |
| Existing regression entry points | 14 pass |
| Portable validation script from a second extraction/build | Pass |

The config whitelist and planner API have different domains: a 0% or 100% planner boundary test does **not** mean that the Micro-Partition command-line whitelist accepts it. Non-micro config-only acceptance of legacy values is not a claim that every downstream computation accepts such values.

## Actual Micro-Partition E2E

Synthetic 240-point input, `local[2]`, 8 logical owners, 10% opt-in. The planner produced **11 physical tasks**, with original assigned population **240**, budget **24 records**, and actual extra charge **0**. Zero charge is valid for this separated-cluster fixture; it is not a budget-binding performance experiment.

The 5 representative circles match the non-micro same-kernel reference. All **288 exported member rows** match as multisets; a separate direct coverage scan of this fixture also matches. This is stronger than a count-only comparison, but is limited to the synthetic fixture.

## Reproduce the validation

Extract the new candidate ZIP into a new directory. Set `JAVA_HOME` to JDK 8 and `SPARK_HOME` to Spark 3.2.0. From its `DiSMC-source` root:

```bash
bash scripts/check_budget10.sh /absolute/path/to/a/NEW/budget10-test
```

The script builds the JAR, runs the existing suite, runs `BudgetCompatibilityTest`, and executes the Micro-Partition/reference queries. Exact generated argv and per-run logs are written into the requested new test directory; existing output is rejected. Python 3 is required for the synthetic harness, with no third-party Python dependency.

See [verification metadata](../validation/budget10/verification.json), [validation logs](../validation/budget10/), and the [minimal production patch](../artifact/patches/micro-budget10.patch). JAR hashes identify individual builds; JAR timestamps mean that repeated builds need not be byte-identical. Java source hashes are also retained.

**This does not reproduce Table I.** Its historical input hashes, constructor/build versions, cluster and full workload remain distinct from the integrated-source functional test.
