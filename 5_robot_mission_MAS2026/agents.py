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

    def get_zone(self, pos=None):
        """Get zone by checking radioactivity at given position (default: current position)."""
        if pos is None:
            pos = self.pos
        
        cell_contents = self.model.grid.get_cell_list_contents(pos)
        for obj in cell_contents:
            if hasattr(obj, 'radioactivity'):
                rad = obj.radioactivity
                if 0 <= rad < 0.33:
                    return "z1"
                elif 0.33 <= rad < 0.66:
                    return "z2"
                elif 0.66 <= rad <= 1.0:
                    return "z3"
        return None

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
    """Robot restricted to zone z1 for green waste transformation."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.green_waste = 0
        self.yellow_waste = 0
    
    def is_at_z1_z2_boundary(self):
        """Check if adjacent cell to the east is in z2."""
        east_pos = (self.pos[0] + 1, self.pos[1])
        return self.get_zone(self.pos) == "z1" and self.get_zone(east_pos) == "z2"
    
    def move_east(self):
        """Moves east within z1 to transport yellow waste towards z2."""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        
        valid_cells = []
        for cell in possible_steps:
            if self.get_zone(cell) == "z1" and cell[0] > self.pos[0]:
                contents = self.model.grid.get_cell_list_contents(cell)
                has_robot = any(isinstance(obj, RobotAgent) for obj in contents)
                if not has_robot:
                    valid_cells.append(cell)
                
        if valid_cells:
            target = self.random.choice(valid_cells)
            self.model.grid.move_agent(self, target)
    
    def move(self):
        """Moves to an empty neighboring cell within z1."""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        
        valid_cells = []
        cells_with_waste = []
        for cell in possible_steps:
            if self.get_zone(cell) == "z1":
                contents = self.model.grid.get_cell_list_contents(cell)
                has_robot = any(isinstance(obj, RobotAgent) for obj in contents)
                if not has_robot:
                    valid_cells.append(cell)
                    has_waste = any(hasattr(obj, 'waste_type') and obj.waste_type == 'green' for obj in contents)
                    if has_waste:
                        cells_with_waste.append(cell)

        # Prioritize cells with green waste
        target = None
        if cells_with_waste:
            target = self.random.choice(cells_with_waste)
        elif valid_cells:
            target = self.random.choice(valid_cells)
        
        if target:
            self.model.grid.move_agent(self, target)
    
    def collect_waste(self):
        """Collect 1 green waste from current cell."""
        cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        for obj in cell_contents:
            if hasattr(obj, 'waste_type') and obj.waste_type == 'green':
                self.green_waste += 1
                self.model.grid.remove_agent(obj)
                print("Successfully collected a green waste") # DEBUG
                break
    
    def drop_waste(self):
        """Drop 1 yellow waste on current cell."""
        if self.yellow_waste > 0:
            waste = YellowWaste(self.model)  # TBD
            self.model.grid.place_agent(waste, self.pos)
            self.yellow_waste -= 1
            print("Yellow waste dropped")

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
        if self.yellow_waste > 0:
            if self.is_at_z1_z2_boundary():
                return "drop_waste"
            else:
                return "move_east"
        
        if self.green_waste >=2: 
            return "transform"
        
        # Always explore to find waste (even if green_waste < 2)
        # collect_waste() will be called in model.do() and collect if on a cell with waste
        return "move" 


class YellowAgent(RobotAgent):
    """Robot restricted to zones z1 and z2 for yellow waste transformation."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.yellow_waste = 0
        self.red_waste = 0
    
    def move_east(self):
        """Moves east within z1 and z2 to transport yellow waste towards z3."""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        
        valid_cells = []
        for cell in possible_steps:
            if self.get_zone(cell) in ["z1", "z2"] and cell[0] > self.pos[0]:
                contents = self.model.grid.get_cell_list_contents(cell)
                has_robot = any(isinstance(obj, RobotAgent) for obj in contents)
                if not has_robot:
                    valid_cells.append(cell)
                
        if valid_cells:
            target = self.random.choice(valid_cells)
            self.model.grid.move_agent(self, target)
    
    def move(self):
        """Moves to an empty neighboring cell within z1 and z2."""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        
        valid_cells = []
        cells_with_waste = []
        for cell in possible_steps:
            if self.get_zone(cell) in ["z1", "z2"]:
                contents = self.model.grid.get_cell_list_contents(cell)
                has_robot = any(isinstance(obj, RobotAgent) for obj in contents)
                if not has_robot:
                    valid_cells.append(cell)
                    has_waste = any(hasattr(obj, 'waste_type') and obj.waste_type == 'yellow' for obj in contents)
                    if has_waste:
                        cells_with_waste.append(cell)

        # Prioritize cells with yellow waste
        target = None
        if cells_with_waste:
            target = self.random.choice(cells_with_waste)
        elif valid_cells:
            target = self.random.choice(valid_cells)
        
        if target:
            self.model.grid.move_agent(self, target)
    
    def collect_waste(self):
        """Collect 1 yellow waste from current cell."""
        cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        for obj in cell_contents:
            if hasattr(obj, 'waste_type') and obj.waste_type == 'yellow':
                self.yellow_waste += 1
                self.model.grid.remove_agent(obj)
                print("Successfully collected a yellow waste") # DEBUG
                break
    
    def drop_waste(self):
        """Drop 1 red waste on current cell."""
        if self.yellow_waste > 0:
            waste = RedWaste(self.model)  # TBD
            self.model.grid.place_agent(waste, self.pos)
            self.red_waste -= 1
            print("Yellow waste dropped")

    def transform_waste(self):
        """Transform 2 yellow wastes into 1 red waste"""
        if self.yellow_waste>=2:
            self.yellow_waste -= 2
            self.red_waste += 1
            print("Yellow waste successfully transformed into one red waste") # DEBUG
            return True
        return False

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