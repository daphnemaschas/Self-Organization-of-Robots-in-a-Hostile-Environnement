"""
Group 5
Date: 2026-03-16
Members: Maxence Rossignol, Antoine Yezou, Daphné Maschas

This module defines the robot agents with communication capabilities (Step 2).
"""

import mesa
import random
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative


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
    def __init__(self, model):
        super().__init__(model)

    def deliberate(self, knowledge):
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']
        
        # 1. If 2 green -> Transform
        if len([w for w in inventory if w.waste_type == "green"]) >= 2:
            return ("transform",)

        # 2. If 1 yellow -> Move to EASTERNMOST border of Z1 and Drop
        yellow_wastes = [w for w in inventory if w.waste_type == "yellow"]
        if yellow_wastes:
            z1_end = self.model.width // 3
            target_x = z1_end - 1
            if self.pos[0] < target_x:
                # Move East
                return ("move", (self.pos[0] + 1, self.pos[1]))
            elif self.pos[0] == target_x:
                self.model.do(self, ("post_message", {"type": "waste_ready", "waste": "yellow", "pos": self.pos}))
                return ("drop",)
            else:
                # Should not happen for GreenAgent, but move West if it does
                return ("move", (self.pos[0] - 1, self.pos[1]))

        # 3. If green waste here -> Pick up
        green_id = self.get_pos_id(percepts, self.pos, "Waste", "waste_green")
        if green_id is not None and len(inventory) < 2:
            return ("pick_up", green_id)

        # 4. Search green waste in percepts
        for pos, contents in percepts.items():
            if "waste_green" in contents:
                return ("move", pos)
        
        # 5. Patrol/Search within Z1 if needs more green waste
        if len(inventory) < 2:
            for pos, contents in percepts.items():
                if "waste_green" in contents:
                    return ("move", pos)
            # Stay in Z1
            neighbors = [p for p in percepts.keys() if p[0] < (self.model.width // 3)]
            if neighbors: return ("move", random.choice(neighbors))
        
        return None

class YellowAgent(RobotAgent):
    def __init__(self, model, patrol=False):
        super().__init__(model)
        self.patrol = patrol

    def deliberate(self, knowledge):
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']
        z1_end = self.model.width // 3
        z2_end = 2 * (self.model.width // 3)

        # 1. Transformation
        if len([w for w in inventory if w.waste_type == "yellow"]) >= 2:
            return ("transform",)

        # 2. Delivery: Move to EASTERNMOST border of Z2 and Drop
        red_wastes = [w for w in inventory if w.waste_type == "red"]
        if red_wastes:
            target_x = z2_end - 1
            if self.pos[0] < target_x:
                return ("move", (self.pos[0] + 1, self.pos[1]))
            elif self.pos[0] == target_x:
                self.model.do(self, ("post_message", {"type": "waste_ready", "waste": "red", "pos": self.pos}))
                return ("drop",)
            else:
                return ("move", (self.pos[0] - 1, self.pos[1]))

        # 3. Collection: If yellow waste here
        yellow_id = self.get_pos_id(percepts, self.pos, "Waste", "waste_yellow")
        if yellow_id is not None and len(inventory) < 2:
            return ("pick_up", yellow_id)

        # 4. Search for nearby waste in percepts
        for pos, contents in percepts.items():
            if "waste_yellow" in contents:
                return ("move", pos)

        # 5. Patrol Z1/Z2 border if waiting for more yellow waste if it is a patrolling agent
        if not red_wastes and len(inventory) < 2 and self.patrol:
            target_x = z1_end # First column of Z2
            if self.pos[0] > target_x:
                return ("move", (self.pos[0] - 1, self.pos[1]))
            elif self.pos[0] < target_x:
                return ("move", (self.pos[0] + 1, self.pos[1]))
            else:
                # Patrol vertically along the border
                adj_y = [p for p in percepts.keys() if p[0] == target_x and p != self.pos]
                if adj_y: return ("move", random.choice(adj_y))

        # 6. Default: Random exploration within Z2
        neighbors = [p for p in percepts.keys() if z1_end <= p[0] < z2_end]
        if neighbors: return ("move", random.choice(neighbors))
        return None

class RedAgent(RobotAgent):
    def __init__(self,model, patrol=False):
        super().__init__(model)
        self.patrol = patrol
    
    def deliberate(self, knowledge):
        percepts = knowledge['last_percepts']
        inventory = knowledge['inventory']
        z2_end = 2 * (self.model.width // 3)

        # 1. Disposal Logic
        red_wastes = [w for w in inventory if w.waste_type == "red"]
        if red_wastes:
            # Check if disposal zone is in percepts (Highest priority)
            for pos, contents in percepts.items():
                if "type_WasteDisposalZone" in contents:
                    if self.pos == pos: 
                        knowledge['disposal_phase'] = "down" # Reset for next time
                        return ("drop",)
                    return ("move", pos)
            
            # Step-by-step search pattern
            target_x = self.model.width - 1
            # A. Go to eastern border
            if self.pos[0] < target_x:
                return ("move", (self.pos[0] + 1, self.pos[1]))
            
            # B. Now at eastern border, perform vertical search
            phase = knowledge.get('disposal_phase', "down")
            if phase == "down":
                if self.pos[1] > 0:
                    return ("move", (self.pos[0], self.pos[1] - 1))
                else:
                    knowledge['disposal_phase'] = "up"
                    return ("move", (self.pos[0], self.pos[1] + 1))
            else: # phase == "up"
                if self.pos[1] < self.model.height - 1:
                    return ("move", (self.pos[0], self.pos[1] + 1))
                else:
                    knowledge['disposal_phase'] = "down"
                    return ("move", (self.pos[0], self.pos[1] - 1))

        # 2. Collection: If red waste here
        red_id = self.get_pos_id(percepts, self.pos, "Waste", "waste_red")
        if red_id is not None and not red_wastes:
            return ("pick_up", red_id)

        # 3. Search for nearby waste in percepts
        for pos, contents in percepts.items():
            if "waste_red" in contents:
                return ("move", pos)

        # 4. Patrol Z2/Z3 border (Waiting for Yellow robots) if is needs to patrol
        if not inventory and self.patrol:
            target_x = z2_end # First column of Z3
            if self.pos[0] > target_x:
                return ("move", (self.pos[0] - 1, self.pos[1]))
            elif self.pos[0] < target_x:
                return ("move", (self.pos[0] + 1, self.pos[1]))
            else:
                adj_y = [p for p in percepts.keys() if p[0] == target_x and p != self.pos]
                if adj_y: return ("move", random.choice(adj_y))

        # 5. Default: Random exploration within Z3
        neighbors = [p for p in percepts.keys() if p[0] >= z2_end]
        if neighbors: return ("move", random.choice(neighbors))
        return None
