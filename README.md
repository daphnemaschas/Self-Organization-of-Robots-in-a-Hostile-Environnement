# Self-Organization-of-Robots-in-a-Hostile-Environnement

## Project Overview
This project simulates a multi-agent system (MAS) where specialized robots collaborate to collect, transform, and dispose of radioactive waste in a segmented hostile environment. 

The environment is logically divided into three zones ($Z_1, Z_2, Z_3$) from West to East, each with specific radioactivity levels.


## Environment Setup
* **$Z_1$ (West)**: Low radioactivity (0.0 to 0.33). Contains initial green waste.
* **$Z_2$ (Middle)**: Medium radioactivity (0.33 to 0.66). Area for intermediate processing.
* **$Z_3$ (East)**: High radioactivity (0.66 to 1.0). Contains the final Waste Disposal Zone.

## Agents and Roles
The mission relies on three types of robots with specific movement constraints and tasks:

| Robot Type | Operational Zones | Task |
| :--- | :--- | :--- |
| **Green** | $Z_1$ only | Collects 2 green wastes $\rightarrow$ 1 yellow waste. |
| **Yellow** | $Z_1, Z_2$ | Collects 2 yellow wastes $\rightarrow$ 1 red waste. |
| **Red** | $Z_1, Z_2, Z_3$ | Collects 1 red waste $\rightarrow$ Waste Disposal Zone. |

## Architecture
5_robot_mission_MAS2026/
├── agents.py       # Classes GreenAgent, YellowAgent, RedAgent
├── objects.py      # Passive classes : Radioactivity, Waste, WasteDisposalZone
├── model.py        # RobotMission classes (Grid management and execution of actions)
├── server.py       # Visualisation configuration
├── run.py          # Script to run the simulation
└── README.md

## Authors
* Members: Maxence Rossignol, Antoine Yezou, Daphné Maschas
* Date: March 2026