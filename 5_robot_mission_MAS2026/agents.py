"""
Group 5
Date: 2026-03-16
Members: Associate 1, Gemini CLI

This module defines the robot agents for the mission.
"""

import mesa

class RobotAgent(mesa.Agent):
    """Base class for all robot agents."""

    def __init__(self, model):
        super().__init__(model)
        self.knowledge = {
            'inventory': [],
            'last_percepts': {}
        }

    def step(self):
        """Standard Mesa step calling the specific agent logic."""
        self.step_agent()

    def step_agent(self):
        """Procedural loop: percepts, deliberate, do."""
        # The first call to do(None) gets initial percepts
        percepts = self.model.do(self, None)
        self.update_knowledge(percepts)
        
        action = self.deliberate(self.knowledge)
        
        # Execute action and get new percepts for the next step
        new_percepts = self.model.do(self, action)
        self.update_knowledge(new_percepts)

    def update_knowledge(self, percepts):
        """Updates the agent's internal state based on environmental feedback."""
        self.knowledge['last_percepts'] = percepts

    def deliberate(self, knowledge):
        """Reasoning step to choose the next action."""
        raise NotImplementedError


import random

class GreenAgent(RobotAgent):
    """Robot restricted to zone Z1 for green waste transformation."""

    def deliberate(self, knowledge):
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']

        # 1. Transformation: if holding 2 green, transform to yellow
        green_wastes = [w for w in inventory if w.waste_type == "green"]
        if len(green_wastes) >= 2:
            return ("transform",)

        # 2. Delivery: if holding 1 yellow, move east and drop at boundary
        yellow_wastes = [w for w in inventory if w.waste_type == "yellow"]
        if yellow_wastes:
            # Move towards east as much as possible (boundary of Z1)
            # Find the max X in the current percepts that is zone 1
            z1_positions = [pos for pos, contents in percepts.items() if any("zone_1" in c for c in contents)]
            if z1_positions:
                target_pos = max(z1_positions, key=lambda p: p[0])
                if self.pos == target_pos:
                    return ("drop",)
                return ("move", target_pos)

        # 3. Collection: if green waste on current tile, pick up
        current_cell_contents = percepts.get(self.pos, [])
        green_waste_id = next((int(c.split('_')[1]) for c in current_cell_contents if "Waste" in c and "green" in c), None)
        if green_waste_id is not None and len(green_wastes) < 2:
            return ("pick_up", green_waste_id)

        # 4. Search: move to a neighbor that has green waste, or move randomly
        for pos, contents in percepts.items():
            if any("waste_green" in c for c in contents):
                return ("move", pos)

        # Random exploration
        neighbors = list(percepts.keys())
        return ("move", random.choice(neighbors))


class YellowAgent(RobotAgent):
    """Robot restricted to zones Z1 and Z2 for yellow waste transformation."""

    def deliberate(self, knowledge):
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']

        # 1. Transformation
        yellow_wastes = [w for w in inventory if w.waste_type == "yellow"]
        if len(yellow_wastes) >= 2:
            return ("transform",)

        # 2. Delivery: if holding red, move to Z2/Z3 boundary
        red_wastes = [w for w in inventory if w.waste_type == "red"]
        if red_wastes:
            z2_positions = [pos for pos, contents in percepts.items() if any("zone_2" in c for c in contents)]
            if z2_positions:
                target_pos = max(z2_positions, key=lambda p: p[0])
                if self.pos == target_pos:
                    return ("drop",)
                return ("move", target_pos)

        # 3. Collection: if yellow waste on current tile
        current_cell_contents = percepts.get(self.pos, [])
        yellow_waste_id = next((int(c.split('_')[1]) for c in current_cell_contents if "Waste" in c and "yellow" in c), None)
        if yellow_waste_id is not None and len(yellow_wastes) < 2:
            return ("pick_up", yellow_waste_id)

        # 4. Search
        for pos, contents in percepts.items():
            if any("waste_yellow" in c for c in contents):
                return ("move", pos)

        neighbors = list(percepts.keys())
        return ("move", random.choice(neighbors))


class RedAgent(RobotAgent):
    """Robot moving in all zones for waste disposal in Z3."""

    def deliberate(self, knowledge):
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']

        # 1. Disposal: if holding red, move to disposal zone
        red_wastes = [w for w in inventory if w.waste_type == "red"]
        if red_wastes:
            # Search for disposal zone in percepts
            for pos, contents in percepts.items():
                if "WasteDisposalZone" in contents:
                    if self.pos == pos:
                        return ("drop",)
                    return ("move", pos)
            # Otherwise move East
            neighbors = list(percepts.keys())
            target_pos = max(neighbors, key=lambda p: p[0])
            return ("move", target_pos)

        # 2. Collection: if red waste on tile
        current_cell_contents = percepts.get(self.pos, [])
        red_waste_id = next((int(c.split('_')[1]) for c in current_cell_contents if "Waste" in c and "red" in c), None)
        if red_waste_id is not None and not red_wastes:
            return ("pick_up", red_waste_id)

        # 3. Search
        for pos, contents in percepts.items():
            if any("waste_red" in c for c in contents):
                return ("move", pos)

        neighbors = list(percepts.keys())
        return ("move", random.choice(neighbors))