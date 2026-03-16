"""
Group 5
Date: 2026-03-16
Members: Associate 1, Gemini CLI

This module defines the visualization for the RobotMission simulation using Mesa 3.x (Solara).
"""

import mesa
from mesa.visualization import SolaraViz, make_space_component
from mesa.visualization.components import AgentPortrayalStyle
from model import RobotMission
from agents import GreenAgent, YellowAgent, RedAgent
from objects import Waste, RadioactivitySource, WasteDisposalZone

def agent_portrayal(agent):
    # 1. Background Zones (RadioactivitySource)
    if isinstance(agent, RadioactivitySource):
        if agent.zone == 1:
            color = "#e8f5e9"  # Very light green
        elif agent.zone == 2:
            color = "#fff3e0"  # Very light orange/yellow
        else:
            color = "#ffebee"  # Very light red
        
        # Use a large square to fill the background cell
        return AgentPortrayalStyle(color=color, size=100, marker="s", zorder=-1)

    # 2. Robots (Bright circles)
    if isinstance(agent, GreenAgent):
        return AgentPortrayalStyle(color="green", size=60, marker="o", zorder=10)
    elif isinstance(agent, YellowAgent):
        return AgentPortrayalStyle(color="#FFD700", size=60, marker="o", zorder=10) # Gold
    elif isinstance(agent, RedAgent):
        return AgentPortrayalStyle(color="red", size=60, marker="o", zorder=10)

    # 3. Wastes (Small squares)
    if isinstance(agent, Waste):
        # Make wastes distinct from robots
        return AgentPortrayalStyle(color=agent.waste_type, size=25, marker="s", zorder=5)

    # 4. Disposal Zone
    if isinstance(agent, WasteDisposalZone):
        return AgentPortrayalStyle(color="blue", size=90, marker="s", zorder=1)

    # Default fallback to avoid NoneType errors
    return AgentPortrayalStyle(size=0)

# Model parameters for the UI
model_params = {
    "width": 15,
    "height": 10,
    "initial_green_waste": {
        "type": "SliderInt",
        "value": 15,
        "label": "Initial Green Waste",
        "min": 1,
        "max": 50,
        "step": 1,
    }
}

# Create a model instance for the initial view
model = RobotMission(width=15, height=10, initial_green_waste=15)

# Setup the space component
space_component = make_space_component(agent_portrayal)

# Create the Solara visualization page
page = SolaraViz(
    model,
    components=[space_component],
    model_params=model_params,
    name="Robot Mission MAS 2026"
)
