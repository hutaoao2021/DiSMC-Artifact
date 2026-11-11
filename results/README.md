# Experimental results

The CSV files contain the paper-reported aggregate values used for the main evaluation. They are provided so readers can inspect the plotted values and the corresponding measurement definitions.

| File | Paper location | Contents |
| --- | --- | --- |
| `online_fixed_queries.csv` | Fig. 4 | DiSMC and Static-Greedy, eight fixed queries, three-run means and sample standard deviations, complete online E2E |
| `esmc_scaleout.csv` | Fig. 8 | DiSMC versus single-threaded ESMC scale-out results; timeout values are marked as censored lower bounds |
| `core_scaling.csv` | Fig. 9 | Executor-core scaling, three-run means and sample standard deviations |
| `input_policy.csv` | Fig. 10 | Full-parent versus Dependency input-policy comparison |
| `full_data.csv` | Table I | Full-output GeoLife and TDrive results under the 10% additional-input budget |

These CSVs are reported aggregates, not fresh Spark runs performed during repository preparation. The supplementary PDF contains additional figures, tables, protocols, and correctness arguments.

Do not mix complete online E2E, frozen-state replay, and component-only measurements. The 10% full-data budget and the 5% standard online budget are distinct. Additional task-input record assignments are not network bytes.
