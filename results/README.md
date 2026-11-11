# Experimental results

The CSV files contain the paper-reported aggregate values used for the main evaluation. They are provided so readers can inspect the plotted values and the corresponding measurement definitions.

| File | Paper location | Contents |
| --- | --- | --- |
| `online_fixed_queries.csv` | Fig. 4 | DiSMC and Static-Greedy, eight fixed queries, three-run means and sample standard deviations, complete online E2E |
| `esmc_scaleout.csv` | Fig. 8 | DiSMC versus single-threaded ESMC scale-out results; timeout values are marked as censored lower bounds |
| `core_scaling.csv` | Fig. 9 | Executor-core scaling, three-run means and sample standard deviations |
| `input_policy.csv` | Fig. 10 | Full-parent versus Dependency input-policy comparison |
| `full_data.csv` | Table I | Full-output GeoLife and TDrive results under the 10% additional-input budget |

These CSVs preserve the aggregate measurements reported in the paper. The supplementary PDF provides additional results, protocols and correctness arguments.

The paper reports complete online E2E, frozen replay and component diagnostics under their respective timing boundaries. Full-data experiments use a 10% additional-input budget; standard online experiments use 5%. The budget is expressed in task-input assignments.
