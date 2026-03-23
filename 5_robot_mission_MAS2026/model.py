"""
Group 5
Date: 2026-03-16
Members: Maxence Rossignol, Antoine Yezou, Daphné Maschas

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
    def __init__(self, width=15, height=10, initial_green_waste=10, initial_yellow_waste=10, initial_red_waste=10, n_green_robots=2, n_yellow_robots=2, n_red_robots=2):
        super().__init__()
        self.width = width
        self.height = height
        self.n_green_robots = n_green_robots
        self.n_yellow_robots = n_yellow_robots
        self.n_red_robots = n_red_robots

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

        # Initial wastes
        self._place_initial_wastes(initial_green_waste, initial_yellow_waste, initial_red_waste, z1_end, z2_end)

        # Initial robots
        self._setup_robots(z1_end, z2_end)

        # Data collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Green_Waste": lambda m: self.count_waste(m, "green"),
                "Yellow_Waste": lambda m: self.count_waste(m, "yellow"),
                "Red_Waste": lambda m: self.count_waste(m, "red"),
                "Total_Radioactivity": self.get_total_radioactivity,
                "Messages": lambda m: len(m.message_board)
            }
        )

    def _place_initial_wastes(self, g, y, r, z1, z2):
        """Helper to distribute initial waste."""
        for _ in range(g):
            self.grid.place_agent(Waste(self, 'green'), (random.randrange(z1), random.randrange(self.height)))
        for _ in range(y):
            self.grid.place_agent(Waste(self, 'yellow'), (random.randrange(z1, z2), random.randrange(self.height)))
        for _ in range(r):
            self.grid.place_agent(Waste(self, 'red'), (random.randrange(z2, self.width), random.randrange(self.height)))

    def _setup_robots(self, z1, z2):
        """Helper to initialize robots."""
        for _ in range(self.n_green_robots):
            self.add_robot(GreenAgent, (random.randrange(z1), random.randrange(self.height)))
        for _ in range(self.n_yellow_robots):
            self.add_robot(YellowAgent, (random.randrange(z1, z2), random.randrange(self.height)))
        for _ in range(self.n_red_robots):
            self.add_robot(RedAgent, (random.randrange(z2, self.width), random.randrange(self.height)))

    @staticmethod
    def count_waste(model, waste_type):
        """Compte les déchets d'un type précis sur la grille ET dans les inventaires."""
        count = 0
        # In the grid
        for obj in model.grid.coord_iter():
            cell_content, pos = obj
            count += len([w for w in cell_content if isinstance(w, Waste) and w.waste_type == waste_type])
        
        # In agent inventory
        for agent in model.agents:
            if hasattr(agent, 'knowledge'):
                count += len([w for w in agent.knowledge['inventory'] if w.waste_type == waste_type])
        return count

    def get_total_radioactivity(self):
        """Compute total radioactivity on the map and on robots."""
        weights = {"green": 1, "yellow": 2, "red": 4}
        total_radio = 0
        
        # In the grid
        for cell_content in self.grid.coord_iter():
            content, pos = cell_content
            for obj in content:
                if isinstance(obj, Waste):
                    total_radio += weights.get(obj.waste_type, 0)
        
        # In agent inventory
        for agent in self.agents:
            if hasattr(agent, 'knowledge'):
                for waste in agent.knowledge['inventory']:
                    total_radio += weights.get(waste.waste_type, 0)
                    
        return total_radio

    def add_robot(self, agent_class, pos):
        robot = agent_class(self)
        self.grid.place_agent(robot, pos)

    def save_data(self, filename="data/simulation_log.csv"):
        df = self.datacollector.get_model_vars_dataframe()
        
        df['n_green'] = self.n_green_robots 
        df['n_yellow'] = self.n_yellow_robots
        df['n_red'] = self.n_red_robots
        df.to_csv(filename)
        print(f"Données sauvegardées dans {filename}")

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

        if self.steps > 0 and self.steps % 50 == 0:
            self.save_data(f"data/sim_step_{self.steps}.csv")

        total_wastes = (self.count_waste(self, "green") + 
                        self.count_waste(self, "yellow") + 
                        self.count_waste(self, "red"))
        
        if total_wastes == 0:
            self.running = False
            self.save_simulation_data("data/final_results.csv")
            print("Mission accomplie : tous les déchets ont été évacués.")

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
                # Check if dropped on disposal zone
                cell_contents = self.grid.get_cell_list_contents(agent.pos)
                if any(isinstance(obj, WasteDisposalZone) for obj in cell_contents):
                    # Waste is "put away" (removed from the simulation)
                    waste.remove()
                else:
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
        # Remove ingredients from the simulation
        for w in agent.knowledge['inventory']:
            w.remove()
        
        agent.knowledge['inventory'] = []
        new_type = "yellow" if isinstance(agent, GreenAgent) else "red"
        new_waste = Waste(self, new_type)
        # The new_waste is in inventory, not on grid
        agent.knowledge['inventory'].append(new_waste)

    def is_move_valid(self, agent, pos):
        """Checks if a robot is allowed to enter a cell based on its zone."""
        # Get zone from RadioactivitySource at pos
        cell_contents = self.grid.get_cell_list_contents(pos)
        zone = next(obj.zone for obj in cell_contents if isinstance(obj, RadioactivitySource))
        
        if isinstance(agent, GreenAgent) and zone > 1: return False
        if isinstance(agent, YellowAgent) and zone > 2: return False
        return True
