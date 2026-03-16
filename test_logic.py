import os
import sys

# Ensure the package is in sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, "5_robot_mission_MAS2026"))

from model import RobotMission
from agents import GreenAgent
from objects import Waste

def test_mission():
    print("Initializing RobotMission...")
    # 1. Setup model with 3 green robots and 15 green waste
    model = RobotMission(width=15, height=10, initial_green_waste=15, n_green_robots=3)
    
    # 2. Check initial state
    robots = [a for a in model.agents if isinstance(a, GreenAgent)]
    wastes = [a for a in model.agents if isinstance(a, Waste) and a.waste_type == "green"]
    print(f"Initial: {len(robots)} robots, {len(wastes)} green wastes.")
    
    # 3. Run for 20 steps
    for i in range(1, 21):
        model.step()
        robots = [a for a in model.agents if isinstance(a, GreenAgent)]
        carried_total = sum(len(r.knowledge['inventory']) for r in robots)
        
        # Count remaining green waste on the grid
        grid_wastes = [a for a in model.agents if isinstance(a, Waste) and a.pos is not None]
        
        print(f"Step {i:2d}: Robots at {[r.pos for r in robots]} | Carried: {carried_total} | On Grid: {len(grid_wastes)}")
        
        # If any robot has a yellow waste (transformation success!)
        for r in robots:
            inv_types = [w.waste_type for w in r.knowledge['inventory']]
            if "yellow" in inv_types:
                print(f"SUCCESS: Robot {r.unique_id} transformed waste into YELLOW!")
                return True

    print("Finished 20 steps.")
    return False

if __name__ == "__main__":
    test_mission()
