"""
Group 5
Date: 2026-03-16
Members: Associate 1, Gemini CLI

This module defines the passive objects in the environment that do not have autonomous behavior.
"""

import mesa

class RadioactivitySource(mesa.Agent):
    """Represents the radioactivity level of a cell.
    
    Attributes:
        zone (int): The zone index (1, 2, or 3).
        radioactivity (float): The radioactivity level (0 to 1).
    """
    def __init__(self, model, zone, radioactivity):
        super().__init__(model)
        self.zone = zone
        self.radioactivity = radioactivity


class Waste(mesa.Agent):
    """Represents a piece of waste in the environment.
    
    Attributes:
        waste_type (str): 'green', 'yellow', or 'red'.
    """
    def __init__(self, model, waste_type):
        super().__init__(model)
        self.waste_type = waste_type


class WasteDisposalZone(mesa.Agent):
    """Represents the final destination for transformed red waste."""
    def __init__(self, model):
        super().__init__(model)
