# Opt-in 10% Micro-Partition budget: validation record

The official submission package is [`artifact/dismc-source.zip`](../artifact/dismc-source.zip). It contains the same validated `ExperimentConfig.java` as the earlier 10% compatibility test package and also retains the frozen-state replay tests. Setting `spark.skyline.budgetDiagnostic=true` permits `spark.skyline.shardReadBudget=0.10` for Micro-Partition execution. The default remains **1%**; existing 2%, 3%, and 5% diagnostic settings are preserved.

The earlier [`10% validation snapshot`](../artifact/DiSMC-source-20261111-budget10-validated.zip) is retained for test provenance. For paper reproduction, use the official package linked above.

## Checks executed

JDK **1.8.0_211**, Spark **3.2.0**, Scala **2.12.15**. Builds and tests ran in independent directories; historical source and results were not overwritten.

| Check | Result |
|---|---|
| Pre-fix historical baseline + 10% acceptance assertion | Rejected before applying the fix, confirming the regression test's sensitivity |
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

Extract the official source ZIP into a new directory. Set `JAVA_HOME` to JDK 8 and `SPARK_HOME` to Spark 3.2.0. From its `DiSMC-source` root:

```bash
bash scripts/check_budget10.sh /absolute/path/to/a/NEW/budget10-test
```

The script builds the JAR, runs the existing suite, runs `BudgetCompatibilityTest`, and executes the Micro-Partition/reference queries. Exact generated argv and per-run logs are written into the requested new test directory; existing output is rejected. Python 3 is required for the synthetic harness, with no third-party Python dependency.

See [verification metadata](../validation/budget10/verification.json), [validation logs](../validation/budget10/), and the [minimal production patch](../artifact/patches/micro-budget10.patch). JAR hashes identify individual builds; JAR timestamps mean that repeated builds need not be byte-identical. Java source hashes are also retained.

The above checks cover budget compatibility and the synthetic functional workload. Table I's full-data setup and experiment parameters are documented in [`configs/experiment-settings.md`](../configs/experiment-settings.md) and [`configs/run-commands.md`](../configs/run-commands.md).
