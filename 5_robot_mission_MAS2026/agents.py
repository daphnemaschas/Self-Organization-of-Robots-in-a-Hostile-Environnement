"""
Group 5
Date: 2026-03-16
Members: Associate 1, Gemini CLI

This module defines the robot agents with communication capabilities (Step 2).
"""

import mesa
import random

class RobotAgent(mesa.Agent):
    """Base class for all robot agents."""

    def __init__(self, model):
        super().__init__(model)
        self.knowledge = {
            'inventory': [],
            'last_percepts': {}
        }

    def step(self):
        self.step_agent()

    def step_agent(self):
        # 1. Get percepts
        percepts = self.model.do(self, None)
        self.knowledge['last_percepts'] = percepts
        
        # 2. Deliberate
        action = self.deliberate(self.knowledge)
        
        # 3. Act and update
        new_percepts = self.model.do(self, action)
        self.knowledge['last_percepts'] = new_percepts

    def deliberate(self, knowledge):
        raise NotImplementedError

    def get_pos_id(self, percepts, pos, obj_type, detail=None):
        """Helper to find an object's ID in percepts."""
        contents = percepts.get(pos, [])
        found_id = None
        is_correct_type = False
        
        # Percepts are formatted as ["type_Waste", "id_10", "waste_green", ...]
        # We need to find the ID that follows the correct type and detail
        for i, item in enumerate(contents):
            if f"type_{obj_type}" == item:
                # Look ahead for ID
                if i + 1 < len(contents) and contents[i+1].startswith("id_"):
                    potential_id = int(contents[i+1].split("_")[1])
                    # Check detail if provided
                    if detail:
                        if detail in contents:
                            return potential_id
                    else:
                        return potential_id
        return None

class GreenAgent(RobotAgent):
    def deliberate(self, knowledge):
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']
        
        # 1. If 2 green -> Transform
        if len([w for w in inventory if w.waste_type == "green"]) >= 2:
            return ("transform",)

        # 2. If 1 yellow -> Move to border and Drop + Notify
        yellow_wastes = [w for w in inventory if w.waste_type == "yellow"]
        if yellow_wastes:
            # Find max x in zone 1
            z1_pos = [p for p, c in percepts.items() if any("zone_1" in item for item in c)]
            if z1_pos:
                target = max(z1_pos, key=lambda p: p[0])
                if self.pos == target:
                    # Notify others before dropping (Step 2: Communication)
                    self.model.do(self, ("post_message", {"type": "waste_ready", "waste": "yellow", "pos": self.pos}))
                    return ("drop",)
                return ("move", target)

        # 3. If green waste here -> Pick up
        green_id = self.get_pos_id(percepts, self.pos, "Waste", "waste_green")
        if green_id is not None and len(inventory) < 2:
            return ("pick_up", green_id)

        # 4. Search
        for pos, contents in percepts.items():
            if "waste_green" in contents:
                return ("move", pos)
        
        neighbors = list(percepts.keys())
        return ("move", random.choice(neighbors))

class YellowAgent(RobotAgent):
    def deliberate(self, knowledge):
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']

        if len([w for w in inventory if w.waste_type == "yellow"]) >= 2:
            return ("transform",)

        red_wastes = [w for w in inventory if w.waste_type == "red"]
        if red_wastes:
            z2_pos = [p for p, c in percepts.items() if any("zone_2" in item for item in c)]
            if z2_pos:
                target = max(z2_pos, key=lambda p: p[0])
                if self.pos == target:
                    self.model.do(self, ("post_message", {"type": "waste_ready", "waste": "red", "pos": self.pos}))
                    return ("drop",)
                return ("move", target)

        yellow_id = self.get_pos_id(percepts, self.pos, "Waste", "waste_yellow")
        if yellow_id is not None and len(inventory) < 2:
            return ("pick_up", yellow_id)

        # Communication: Check for signaled yellow waste
        for msg in self.model.message_board:
            if msg["type"] == "waste_ready" and msg["waste"] == "yellow":
                # Move towards signaled pos (simple logic: move East if target is East)
                if msg["pos"][0] > self.pos[0]:
                    neighbors = [p for p in percepts.keys() if p[0] > self.pos[0]]
                    if neighbors: return ("move", random.choice(neighbors))

        for pos, contents in percepts.items():
            if "waste_yellow" in contents:
                return ("move", pos)
        
        neighbors = list(percepts.keys())
        return ("move", random.choice(neighbors))

class RedAgent(RobotAgent):
    def deliberate(self, knowledge):
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']

        red_wastes = [w for w in inventory if w.waste_type == "red"]
        if red_wastes:
            for pos, contents in percepts.items():
                if "type_WasteDisposalZone" in contents:
                    if self.pos == pos: return ("drop",)
                    return ("move", pos)
            # Move East
            neighbors = [p for p in percepts.keys() if p[0] > self.pos[0]]
            if neighbors: return ("move", random.choice(neighbors))

        red_id = self.get_pos_id(percepts, self.pos, "Waste", "waste_red")
        if red_id is not None and not red_wastes:
            return ("pick_up", red_id)

        # Communication
        for msg in self.model.message_board:
            if msg["type"] == "waste_ready" and msg["waste"] == "red":
                if msg["pos"][0] > self.pos[0]:
                    neighbors = [p for p in percepts.keys() if p[0] > self.pos[0]]
                    if neighbors: return ("move", random.choice(neighbors))

        for pos, contents in percepts.items():
            if "waste_red" in contents:
                return ("move", pos)
        
        neighbors = list(percepts.keys())
        return ("move", random.choice(neighbors))
