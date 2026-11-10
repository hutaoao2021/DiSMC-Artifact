# Experiment index

This file points to the primary experimental categories in the DiSMC manuscript. It is a navigation guide, not an independent record of completed runs.

| Paper figure or table | Experimental question | Main comparison |
| --- | --- | --- |
| Fig. 4 | Complete online query efficiency | DiSMC vs. same-resource Static-Greedy across eight fixed queries |
| Fig. 5 | Planning cost and formal-execution savings | Online stage-level contribution analysis |
| Fig. 6 | Distributed system comparisons | Complete external-query speedups versus routing and spatial-operator baselines |
| Fig. 7 | Performance across query positions | Sparse, medium and dense locations |
| Fig. 8 | Input-size comparison | DiSMC vs. single-threaded ESMC |
| Fig. 9 | Scaling with compute resources | Complete online E2E versus executor cores |
| Table I | Full-data execution | GeoLife and TDrive full-input query outcomes |
| Fig. 10 | Dependency-complete input organization | Full-parent versus Dependency under matched acquisition/work signals |
| Fig. 11 | Planning mechanisms | Online calibration and fixed-state selector replay |
| Fig. 12 | Work-estimation signals | Unit, Static and Sampled under matched-information controls |
| Fig. 13 | Probe reuse | Complete online E2E of four reuse settings |
| Fig. 14 | Probe reuse | Formal task candidate-generation/counting checks |

**Execution and parameter details:** [experiment settings](../configs/experiment-settings.md), [run commands](../configs/run-commands.md), and [fixed query coordinates](../configs/fixed-query-coordinates.csv).

The current integrated release cannot directly use a 10% budget in its Micro-Partition configuration-validation path; do not represent the Table I full-data protocol as a directly runnable 5%-to-10% parameter substitution. State-dependent selector and reuse controls likewise need matching frozen inputs. See the linked command guide.

## Reading the supplementary tables

The supplementary technical document provides dataset preparation notes, precise controls, additional quantitative summaries and proof details.

Keep these distinctions when interpreting results:

- **Complete online E2E** includes the stages explicitly identified in the main text; it is not equivalent to private-task duration alone.
- **Frozen-state replay** conditions on previously acquired responsibility/input information and excludes the acquisition operations identified in the experiment.
- **Additional task-input record assignments** are accounting units defined relative to initial owner-level assignments. They are not network bytes and are not themselves runtime.
- **Budget fraction** is specific to an experiment. Read it from the experiment's recorded protocol rather than assuming that every experiment used the same fraction.

For execution commands, use corresponding frozen query coordinates, subset definitions and application flags; do not substitute default query parameters when reproducing a plotted result.
