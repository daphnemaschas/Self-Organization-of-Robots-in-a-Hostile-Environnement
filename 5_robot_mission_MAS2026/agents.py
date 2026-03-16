"""Module defining the robot agents for the mission."""

import mesa

class RobotAgent(mesa.Agent):
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

    def step_agent(self):
        """Procedural loop: update knowledge, deliberate, and execute action."""
        # Update knowledge with previous percepts if they exist
        percepts = self.model.do(self, None)  # Initial percepts
        self.knowledge['last_percepts'] = percepts
        
        action = self.deliberate(self.knowledge)
        self.knowledge['last_percepts'] = self.model.do(self, action)

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


    def deliberate(self, knowledge):
        """Implementation of green waste collection and transformation logic."""
        # TODO: Logic for picking up 2 green wastes and transforming to yellow
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