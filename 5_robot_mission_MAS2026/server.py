"""
Group 5
Date: 2026-03-16
Members: Maxence Rossignol, Antoine Yezou, Daphné Maschas

This module defines the visualization for the RobotMission simulation using Mesa 3.x (Solara).
Following EXACTLY the pattern from the Wolf-Sheep example in Mesa 3.5.1.
"""
import solara
import mesa
from mesa.visualization import SolaraViz, SpaceRenderer
from mesa.visualization.components import AgentPortrayalStyle, make_plot_component
from mesa.visualization.utils import update_counter
from model import RobotMission
from agents import GreenAgent, YellowAgent, RedAgent
from objects import Waste, RadioactivitySource, WasteDisposalZone

def agent_portrayal(agent):
    """How an agent is drawn on the grid."""
    if agent is None:
        return

    # Start with default as in Wolf-Sheep
    portrayal = AgentPortrayalStyle(
        size=200,
        marker="o",
        zorder=2,
    )

    if isinstance(agent, RadioactivitySource):
        if agent.zone == 1:
            color = "#e8f5e9"  # Light Green
        elif agent.zone == 2:
            color = "#fff3e0"  # Light Orange
        else:
            color = "#ffebee"  # Light Red
        portrayal.update(("color", color), ("marker", "s"), ("size", 350), ("zorder", 1))

    elif isinstance(agent, GreenAgent):
        portrayal.update(("color", "green"))
    elif isinstance(agent, YellowAgent):
        portrayal.update(("color", "#FFD700"))
    elif isinstance(agent, RedAgent):
        portrayal.update(("color", "red"))

    elif isinstance(agent, Waste):
        portrayal.update(("color", agent.waste_type), ("marker", "s"), ("size", 45))

    elif isinstance(agent, WasteDisposalZone):
        portrayal.update(("color", "blue"), ("marker", "P"), ("size", 180), ("zorder", 2))
    
    else:
        # Hide unknown agents
        portrayal.update(("alpha", 0))

    return portrayal

@solara.component
def MessageBoardComponent(model):
    """Composant Solara personnalisé pour afficher l'historique des messages."""
    update_counter.get()
    
    solara.Markdown("### Historique des Communications")
    
    messages = getattr(model, 'message_history', [])
    msg_count = len(messages)
    
    if msg_count == 0:
        solara.Info("Aucun message reçu pour le moment.")
        return
    
    recent_messages = messages[-15:]
    messages_text = "\n".join([f"- {msg_str}" for msg_str in reversed(recent_messages)])
    
    with solara.Column(style={"max-height": "300px", "overflow-y": "auto", "background-color": "#f8f9fa", "padding": "10px", "border-radius": "5px"}):
        solara.Markdown(messages_text)

# 1. Setup Model and Parameters
model_params = {
    "width": 15,
    "height": 10,
    "n_green_robots": {
        "type": "SliderInt",
        "value": 2,
        "label": "Green Robots",
        "min": 0,
        "max": 10,
        "step": 1,
    },
    "n_yellow_robots": {
        "type": "SliderInt",
        "value": 2,
        "label": "Yellow Robots",
        "min": 0,
        "max": 10,
        "step": 1,
    },
    "n_red_robots": {
        "type": "SliderInt",
        "value": 2,
        "label": "Red Robots",
        "min": 0,
        "max": 10,
        "step": 1,
    },
    "initial_green_waste": {
        "type": "SliderInt",
        "value": 15,
        "label": "Initial Green Waste",
        "min": 0,
        "max": 50,
        "step": 1,
    },
    "initial_yellow_waste": {
        "type": "SliderInt",
        "value": 15,
        "label": "Initial Yellow Waste",
        "min": 0,
        "max": 50,
        "step": 1,
    },
    "initial_red_waste": {
        "type": "SliderInt",
        "value": 15,
        "label": "Initial Red Waste",
        "min": 0,
        "max": 50,
        "step": 1,
    },
    "use_memory": {
        "type": "Checkbox",
        "value": True,
        "label": "Use Spatial Memory",
    }
}

# 2. Create the model instance
model = RobotMission(width=15, height=10, initial_green_waste=15, n_green_robots=2, n_yellow_robots=2, n_red_robots=2, use_memory=True)

# 3. Setup the SpaceRenderer following the Wolf-Sheep pattern exactly
renderer = SpaceRenderer(
    model,
    backend="matplotlib",
).setup_agents(agent_portrayal)

# Added following the wolf_sheep example
renderer.render()

# Add a graph for waste stocks
waste_plot = make_plot_component({
    "Green_Waste": "green", 
    "Yellow_Waste": "#FFD700", 
    "Red_Waste": "red"
})

# Add a graph for total radioactivity
radio_plot = make_plot_component("Total_Radioactivity")

# 4. Create the Solara visualization page
# Note: wolf_sheep passes (model, renderer, components=..., model_params=...)
page = SolaraViz(
    model,
    renderer,
    model_params=model_params,
    name="Robot Mission MAS 2026",
    components=[waste_plot, radio_plot, MessageBoardComponent]
)

