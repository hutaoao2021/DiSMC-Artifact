# Reproducibility guide

## Execution entry points

From the extracted `DiSMC-source/` directory:

| Command or profile | Purpose |
| --- | --- |
| `bash build.sh` | Compile the Java/Spark source |
| `bash scripts/check_selected.sh` | Run selected regression tests |
| `bash scripts/run_small_online.sh NEW_OUTPUT_PATH` | Run the bundled five-point smoke query |
| `bash scripts/run_profile.sh ...` | Run a distributed method profile or the single-machine ESMC baseline |

## Available profiles

- `hilbert_full` / `full`: complete DiSMC execution profile.
- `single_esmc`: single-machine ESMC baseline.
- `z_d0`, `hilbert_d0`, `grid_d0`: distributed baseline profiles.
- `hilbert_wo_planner`, `hilbert_wo_engine`: principal ablation profiles.
- `wo_planner`, `wo_engine`, `wo_dependency_partition`, `wo_sharing`, `wo_refinement`, `wo_new_bounds`, `wo_prepared_reuse`: additional source-supported ablation profiles.

For the Micro-Partition selector, `spark.skyline.microSelector=joint_peak` selects the joint planner and `spark.skyline.microSelector=work_greedy` selects the greedy comparison policy. These are selector settings, not separate launcher profiles.

## Inputs and parameters

The program input is UTF-8 text with one projected, translated `x y` coordinate pair per line and no header. Use prepared data accessible to the Spark driver and executors. Set query coordinates with both `QUERY_X` and `QUERY_Y`; set radius, partition count, density, and cell factor in the launcher arguments.

Use [`../configs/experiment-settings.md`](../configs/experiment-settings.md) and [`../configs/run-commands.md`](../configs/run-commands.md) for the paper workload values and executable examples.

## Scope

The packaged source, regression checks, and smoke query provide an executable entry point. The CSV files contain the paper-reported aggregate measurements. Exact historical timings depend on the corresponding prepared inputs, build, acquisition or frozen state, Spark resources, and timing boundary; the smoke query is not a substitute for those experiments.
