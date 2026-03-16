"""Module defining the robot agents for the mission."""

from mesa import Agent

class RobotAgent(Agent):
    """Base class for all robot agents.

    Attributes:
        knowledge (dict): Internal representation of agent beliefs and memory.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.knowledge = {}

    def step(self):
        """Standard Mesa step calling the specific agent logic."""
        self.step_agent()
    
    def update(self, knowledge, percepts):
        """Update knowledge with new percepts."""
        knowledge['last_percepts'] = percepts

    def step_agent(self):
        """Procedural loop: update knowledge, deliberate, and execute action."""
        percepts = self.model.do(self, None)
        self.update(self.knowledge, percepts)
        action = self.deliberate(self.knowledge)
        percepts = self.model.do(self, action)

    def deliberate(self, knowledge):
        """Reasoning step to choose the next action.

        Args:
            knowledge (dict): The current knowledge of the agent.

        Returns:
            str: The chosen action.
        """
        raise NotImplementedError


class GreenAgent(RobotAgent):
    """Robot restricted to zone Z1 for green waste transformation."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.green_waste = 0
        self.yellow_waste = 0
    
    def move(self):
        """Moves to an empty neighboring cell."""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        empty_cells = [cell for cell in possible_steps if self.model.grid.is_cell_empty(cell)]

        if empty_cells:
            new_position = self.random.choice(empty_cells)
            self.model.grid.move_agent(self, new_position)
    
    def collect_waste(self):
        """Collect 1 green waste from neighboring cells."""
        neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        for cell in neighborhood:
            if cell in self.model.green_waste_cell and self.model.green_waste_cells[cell] > 0:
                self.model.green_waste_cells[cell] -= 1
                self.green_waste += 1
                print("One green waste successfully collected") # DEBUG
                break

    def transform_waste(self):
        """Transform 2 green wastes into 1 yellow waste"""
        if self.green_waste>=2:
            self.green_waste -= 2
            self.yellow_waste += 1
            print("Green waste successfully transformed into one yellow waste") # DEBUG
            return True
        return False

    def deliberate(self, knowledge):
        """Implementation of green waste collection and transformation logic."""

        if self.green_waste >=2: 
            return "transform"
        
        if self.green_waste < 2:
            return "collect"

        return "move" 


class YellowAgent(RobotAgent):
    """Robot restricted to zones Z1 and Z2 for yellow waste transformation."""

    def deliberate(self, knowledge):
        """Implementation of yellow waste collection and transformation logic."""
        # TODO: Logic for picking up 2 yellow wastes and transforming to red
        return "move"


class RedAgent(RobotAgent):
    """Robot moving in all zones for waste disposal in Z3."""

    def deliberate(self, knowledge):
        """Implementation of red waste transport logic."""
        # TODO: Logic for picking up 1 red waste and moving east
        return "move"