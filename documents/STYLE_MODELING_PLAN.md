# Style Modeling Implementation Report

Date: 2026-04-07

## Scope Summary
Implement a new style_modeling module mirroring oppo_modeling. The goal is to add:
- Opponent-style encoder consuming the 15-move public action history (5x162).
- Opponent-conditioned Q-network that concatenates state with two opponent embeddings.
- Auxiliary multi-task head predicting opponent pass probability and next action category.
- Training pipeline that aligns auxiliary targets with the opponents' next-turn actions.

## What Will Be Implemented (New)

### 1) New style_modeling package layout
- Folder structure mirroring oppo_modeling:
  - style_modeling/dmc/ (models.py, dmc.py, env_utils.py, utils.py, arguments.py, file_writer.py)
  - style_modeling/env/ (env.py, game.py, move_detector.py, move_generator.py, move_selector.py, utils.py)
  - style_modeling/evaluation/ (if needed, optional)
  - style_modeling/test/ (if needed, optional)
- A new training entrypoint script (e.g., train_style.py) at repo root.

### 2) Opponent-style encoder
- A small LSTM-based encoder that consumes each opponent's public action history.
- Input format: 15 moves -> 5x162 as used by DouZero (same as obs_z).
- Output: two embeddings z_t^(1), z_t^(2) corresponding to the other two players.

### 3) Opponent-conditioned Q-network
- Modify the decision model to concatenate:
  - Standard observation vector x (obs_x / obs_x_no_action + action encoding).
  - LSTM output from the standard history encoder (if retained).
  - Two opponent embeddings.
- Score each legal action with Q_theta(s_t, a, z_t^(1), z_t^(2)).

### 4) Auxiliary prediction head and loss
- Single auxiliary head off each opponent embedding:
  - 15-class classifier for next action category (includes Pass).
- Auxiliary targets are aligned to the opponents' next-turn actions.
- Loss: RL MSE + lambda * CE auxiliary loss.
- Ignore invalid action class during CE loss (no invalid moves are executed).

### 5) Next-turn label alignment
- Extend environment/buffer pipeline to store next-turn labels for each opponent.
- For each timestep t, hold placeholder labels and fill when the opponent acts.
- Ensure labels are batched and aligned with obs_x / obs_z for training.

### 6) New training script
- A new script (e.g., train_style.py) that wires arguments, training loop, and evaluation hooks.
- Uses existing training patterns from oppo_modeling/dmc/dmc.py with modifications for:
  - Two opponent embeddings in the learner/actor models.
  - Auxiliary losses and lambda weight.
  - New buffers carrying auxiliary labels.

## What Can Be Copied or Reused (Reference Only)

### From oppo_modeling (primary reference)
- Training loop structure and multi-process actor/learner pattern:
  - oppo_modeling/dmc/dmc.py
- Buffer creation and batching utilities:
  - oppo_modeling/dmc/utils.py
- Environment wrapper and observation formatting:
  - oppo_modeling/dmc/env_utils.py
- Environment logic and observation construction:
  - oppo_modeling/env/env.py
  - oppo_modeling/env/game.py
- Move typing and constants for action categories:
  - oppo_modeling/env/move_detector.py
  - oppo_modeling/env/utils.py
- FileWriter logging utility:
  - oppo_modeling/dmc/file_writer.py
- Argument handling pattern:
  - oppo_modeling/dmc/arguments.py

### From douzero (secondary reference)
- Baseline model structure and feature dimensions:
  - douzero/dmc/models.py
- Observation input formats and action history encoding:
  - douzero/env/env.py
- Move typing and legal-action generation (if needed):
  - douzero/env/move_detector.py
  - douzero/env/move_generator.py

## New Data Flow Requirements

### Observations
- Continue using obs_x, obs_x_no_action, obs_action, obs_z as in oppo_modeling.
- Add fields for opponent-specific history (if splitting is needed) or reuse obs_z with role-aware separation logic.

### Labels
- Add buffers for:
  - opponent_next_action_type (int in [0..14])
- Align labels with the state before the opponent's next action.

## Open Design Choices (Pending)
- Whether to reuse existing LSTM history encoder or add a separate one dedicated to style embeddings.
- Exact embedding size for style encoder output.
- Whether to share encoder weights across opponents or use separate encoders per opponent.
- Exact lambda weights for auxiliary losses (default: 0.1 to 0.5).

## Notes
- The auxiliary task must predict opponents' next-turn actions, not their most recent actions.
- The 15 action categories align with DouDizhu move types; invalid types can be ignored in the loss.
- The new style_modeling folder should mirror oppo_modeling for compatibility and minimal friction.
