# DMC and Evaluation Comparison (douzero vs oppo_modeling)

This report compares folders at the file level and explains the purpose of the extra test folder in oppo_modeling.

## Folder overview

- douzero/dmc: [douzero/dmc](douzero/dmc)
- douzero/evaluation: [douzero/evaluation](douzero/evaluation)
- oppo_modeling/dmc: [oppo_modeling/dmc](oppo_modeling/dmc)
- oppo_modeling/evaluation: [oppo_modeling/evaluation](oppo_modeling/evaluation)
- oppo_modeling/test: [oppo_modeling/test](oppo_modeling/test)

## File-level similarities

### DMC folders

Both DMC folders implement the same pipeline pieces, but with different model inputs:

- Core training loop and checkpointing in [douzero/dmc/dmc.py](douzero/dmc/dmc.py) and [oppo_modeling/dmc/dmc.py](oppo_modeling/dmc/dmc.py).
- Environment wrapper and observation formatting in [douzero/dmc/env_utils.py](douzero/dmc/env_utils.py) and [oppo_modeling/dmc/env_utils.py](oppo_modeling/dmc/env_utils.py).
- Models for landlord and farmer in [douzero/dmc/models.py](douzero/dmc/models.py) and [oppo_modeling/dmc/models.py](oppo_modeling/dmc/models.py).
- Actor + buffer utilities in [douzero/dmc/utils.py](douzero/dmc/utils.py) and [oppo_modeling/dmc/utils.py](oppo_modeling/dmc/utils.py).

### Evaluation folders

Both evaluation folders run self-play over a fixed eval set and report WP/ADP metrics:

- Simulation driver in [douzero/evaluation/simulation.py](douzero/evaluation/simulation.py) and [oppo_modeling/evaluation/simulation.py](oppo_modeling/evaluation/simulation.py).
- Neural agent wrapper in [douzero/evaluation/deep_agent.py](douzero/evaluation/deep_agent.py) and [oppo_modeling/evaluation/deep_agent.py](oppo_modeling/evaluation/deep_agent.py).

## File-level differences

### DMC differences

- Argument parsing exists only in [douzero/dmc/arguments.py](douzero/dmc/arguments.py). The opponent training entrypoint reuses this parser and injects extra flags in train_oppo.py.
- Logging helper exists only in [douzero/dmc/file_writer.py](douzero/dmc/file_writer.py); opponent training imports FileWriter from that location.
- Model structure differs:
  - Baseline models in [douzero/dmc/models.py](douzero/dmc/models.py) take only state features (z, x).
  - Opponent models in [oppo_modeling/dmc/models.py](oppo_modeling/dmc/models.py) add prediction networks and append predicted hand features to decision inputs.
- Buffer contents differ:
  - Baseline buffers omit prediction labels and legality masks in [douzero/dmc/utils.py](douzero/dmc/utils.py).
  - Opponent buffers add hand_legal and down_label in [oppo_modeling/dmc/utils.py](oppo_modeling/dmc/utils.py), and the actor runs both prediction and decision models.
- Init and checkpoint handling:
  - Opponent training loads compatible weights from a bootstrap directory and saves both decision and prediction weights in [oppo_modeling/dmc/dmc.py](oppo_modeling/dmc/dmc.py).

### Evaluation differences

- Baseline evaluation supports random and RLCard agents in [douzero/evaluation/random_agent.py](douzero/evaluation/random_agent.py) and [douzero/evaluation/rlcard_agent.py](douzero/evaluation/rlcard_agent.py). The opponent evaluation folder does not include these.
- Opponent evaluation includes a baseline agent wrapper in [oppo_modeling/evaluation/baseline_agent.py](oppo_modeling/evaluation/baseline_agent.py) so tests can mix baseline and opponent models in the same run.
- Opponent deep agent loads both decision and prediction weights; baseline deep agent loads only decision weights.

## Why oppo_modeling/test exists (and douzero has none)

The test folder under oppo_modeling is a **training-time evaluation harness** for opponent-model checkpoints. It automates comparisons against baseline models and logs results.

- [oppo_modeling/test/ADP_test.py](oppo_modeling/test/ADP_test.py) and [oppo_modeling/test/sl_test.py](oppo_modeling/test/sl_test.py) run scripted evaluations that:
  - copy the most recent checkpoint,
  - run evaluation twice (landlord vs farmer roles),
  - append results to log files.
- [oppo_modeling/test/evaluate.py](oppo_modeling/test/evaluate.py) is a thin wrapper around the standard evaluation pipeline with extra CLI fields used by the test scripts.
- [oppo_modeling/test/get_most_recent.sh](oppo_modeling/test/get_most_recent.sh) syncs the latest weights to a stable path.

Douzero does not include a parallel test folder because its baseline training does not wire in this automated “compare vs baseline on every checkpoint” workflow. Instead, evaluation is run manually via the repo-level scripts like evaluate.py and generate_eval_data.py.

## Summary

- The two DMC and evaluation folders share the same structure, but the opponent version adds prediction modeling, extra buffers, and baseline-comparison agents.
- The oppo_modeling/test folder exists to automate periodic checkpoint evaluation and role-swap comparisons during opponent training.
- Douzero omits this folder because its baseline training pipeline expects manual evaluation rather than built-in testing on each checkpoint.
