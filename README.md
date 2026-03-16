# Self-Organization-of-Robots-in-a-Hostile-Environnement

## Project Overview
This project simulates a multi-agent system (MAS) where specialized robots collaborate to collect, transform, and dispose of radioactive waste in a segmented hostile environment. 

The environment is logically divided into three zones ($Z_1, Z_2, Z_3$) from West to East, each with specific radioactivity levels[cite: 9, 10, 11, 12].


## Environment Setup
* **$Z_1$ (West)**: Low radioactivity (0.0 to 0.33). Contains initial green waste[cite: 10, 49].
* **$Z_2$ (Middle)**: Medium radioactivity (0.33 to 0.66). Area for intermediate processing[cite: 10, 49].
* **$Z_3$ (East)**: High radioactivity (0.66 to 1.0). Contains the final Waste Disposal Zone[cite: 12, 49, 51].

## Agents and Roles
The mission relies on three types of robots with specific movement constraints and tasks:

| Robot Type | Operational Zones | Task |
| :--- | :--- | :--- |
| **Green** | $Z_1$ only | Collects 2 green wastes $\rightarrow$ 1 yellow waste[cite: 15, 19]. |
| **Yellow** | $Z_1, Z_2$ | Collects 2 yellow wastes $\rightarrow$ 1 red waste[cite: 15, 19]. |
| **Red** | $Z_1, Z_2, Z_3$ | Collects 1 red waste $\rightarrow$ Waste Disposal Zone[cite: 15, 19]. |

## Architecture
The implementation follows a modular approach:
* **notebooks/**: Gather all notebooks used for visualization purposes.
* **`src/`**: Contains the core MAS logic (Agent behavior, Environment rules, Visualization).
* **`utils/`**: Shared constants (radioactivity thresholds) and helper functions.
* **`run.py`**: Executes the simulation.

## Authors
* Members: Maxence Rossignol, Antoine Yezou, Daphné Maschas
* Date: March 2026