"""
Group 5
Date: 2026-03-16
Members: Associate 1, Gemini CLI

This module defines the RobotMission model and its central logic.
"""

import mesa
import random
from agents import GreenAgent, YellowAgent, RedAgent
from objects import RadioactivitySource, Waste, WasteDisposalZone

class RobotMission(mesa.Model):
    """The central model for the robot mission simulation.
    
    Attributes:
        grid (MultiGrid): The spatial environment.
        width (int): Grid width.
        height (int): Grid height.
    """
    def __init__(self, width=15, height=10, initial_green_waste=10, n_green_robots=2, n_yellow_robots=2, n_red_robots=2):
        super().__init__()
        self.width = width
        self.height = height
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        self.message_board = [] # Step 2: Communication

        # Define zone boundaries
        z1_end = width // 3
        z2_end = 2 * (width // 3)

        # Setup environment: radioactivity and disposal zone
        for x in range(width):
            for y in range(height):
                if x < z1_end:
                    zone = 1
                    radio_val = random.uniform(0, 0.33)
                elif x < z2_end:
                    zone = 2
                    radio_val = random.uniform(0.33, 0.66)
                else:
                    zone = 3
                    radio_val = random.uniform(0.66, 1.0)
                
                radio = RadioactivitySource(self, zone, radio_val)
                self.grid.place_agent(radio, (x, y))

        # Disposal zone on the far east side
        disposal_y = random.randrange(height)
        disposal_zone = WasteDisposalZone(self)
        self.grid.place_agent(disposal_zone, (width - 1, disposal_y))

        # Initial green waste in Z1
        for _ in range(initial_green_waste):
            x = random.randrange(z1_end)
            y = random.randrange(height)
            waste = Waste(self, 'green')
            self.grid.place_agent(waste, (x, y))

        # Place all robots
        for _ in range(n_green_robots):
            self.add_robot(GreenAgent, (random.randrange(z1_end), random.randrange(self.height)))
        for _ in range(n_yellow_robots):
            self.add_robot(YellowAgent, (random.randrange(z1_end, z2_end), random.randrange(self.height)))
        for _ in range(n_red_robots):
            self.add_robot(RedAgent, (random.randrange(z2_end, self.width), random.randrange(self.height)))

    def place_robots(self, z1_end, z2_end):
        # Example setup: 2 of each robot
        for _ in range(2):
            self.add_robot(GreenAgent, (random.randrange(z1_end), random.randrange(self.height)))
            self.add_robot(YellowAgent, (random.randrange(z1_end, z2_end), random.randrange(self.height)))
            self.add_robot(RedAgent, (random.randrange(z2_end, self.width), random.randrange(self.height)))

    def add_robot(self, agent_class, pos):
        robot = agent_class(self)
        self.grid.place_agent(robot, pos)

    def step(self):
        self.agents.shuffle_do("step")

    def do(self, agent, action):
        """Processes an agent's action and returns percepts."""
        if action:
            if action[0] == "post_message":
                self.message_board.append(action[1])
            elif action[0] == "read_messages":
                pass # Already available via agent.model.message_board
            else:
                self.execute_action(agent, action)
        
        # Return percepts: current tile and neighbors
        neighbors = self.grid.get_neighborhood(agent.pos, moore=True, include_center=True)
        percepts = {}
        for pos in neighbors:
            cell_contents = self.grid.get_cell_list_contents(pos)
            percepts[pos] = []
            # Include more details if it's a Waste or Radioactivity
            for obj in cell_contents:
                percepts[pos].append(f"type_{type(obj).__name__}")
                percepts[pos].append(f"id_{obj.unique_id}")
                if isinstance(obj, Waste):
                    percepts[pos].append(f"waste_{obj.waste_type}")
                if isinstance(obj, RadioactivitySource):
                    percepts[pos].append(f"radio_{obj.radioactivity:.2f}")
                    percepts[pos].append(f"zone_{obj.zone}")

        return percepts

    def execute_action(self, agent, action):
        """Verifies and applies an action to the environment."""
        if not action or not isinstance(action, tuple):
            return

        cmd = action[0]
        
        if cmd == "move":
            new_pos = action[1]
            if self.is_move_valid(agent, new_pos):
                self.grid.move_agent(agent, new_pos)

        elif cmd == "pick_up":
            waste_id = action[1]
            # Verify the waste is at agent's position
            cell_contents = self.grid.get_cell_list_contents(agent.pos)
            waste_obj = next((obj for obj in cell_contents if isinstance(obj, Waste) and obj.unique_id == waste_id), None)
            
            if waste_obj:
                # Check constraints (Green picks up 2 green, etc.)
                if self.can_pick_up(agent, waste_obj):
                    agent.knowledge['inventory'].append(waste_obj)
                    self.grid.remove_agent(waste_obj)

        elif cmd == "transform":
            # Transformation logic
            if self.can_transform(agent):
                self.perform_transformation(agent)

        elif cmd == "drop":
            if agent.knowledge['inventory']:
                waste = agent.knowledge['inventory'].pop()
                self.grid.place_agent(waste, agent.pos)

    def can_pick_up(self, agent, waste):
        if isinstance(agent, GreenAgent):
            return waste.waste_type == "green" and len(agent.knowledge['inventory']) < 2
        elif isinstance(agent, YellowAgent):
            return waste.waste_type == "yellow" and len(agent.knowledge['inventory']) < 2
        elif isinstance(agent, RedAgent):
            return waste.waste_type == "red" and len(agent.knowledge['inventory']) < 1
        return False

    def can_transform(self, agent):
        inv = agent.knowledge['inventory']
        if isinstance(agent, GreenAgent):
            return len([w for w in inv if w.waste_type == "green"]) == 2
        elif isinstance(agent, YellowAgent):
            return len([w for w in inv if w.waste_type == "yellow"]) == 2
        return False

    def perform_transformation(self, agent):
        # Remove ingredients and add new product to inventory
        agent.knowledge['inventory'] = [] # Simplified: consume all
        new_type = "yellow" if isinstance(agent, GreenAgent) else "red"
        new_waste = Waste(self, new_type)
        # Note: the new_waste is in inventory, not on grid
        agent.knowledge['inventory'].append(new_waste)

    def is_move_valid(self, agent, pos):
        """Checks if a robot is allowed to enter a cell based on its zone."""
        # Get zone from RadioactivitySource at pos
        cell_contents = self.grid.get_cell_list_contents(pos)
        zone = next(obj.zone for obj in cell_contents if isinstance(obj, RadioactivitySource))
        
        if isinstance(agent, GreenAgent) and zone > 1: return False
        if isinstance(agent, YellowAgent) and zone > 2: return False
        return True
