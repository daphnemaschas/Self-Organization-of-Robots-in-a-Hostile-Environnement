"""
Group 5
Date: 2026-03-16
Members: Associate 1, Gemini CLI

Main script to launch the RobotMission simulation using Solara (Mesa 3.x).
"""

import subprocess
import os
import sys

if __name__ == "__main__":
    # Get the absolute path to the server file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(base_dir, "5_robot_mission_MAS2026", "server.py")
    
    # In Mesa 3.x, you run the visualization with: solara run <path_to_server.py>
    # Note: Solara handles the module import, so the numeric folder name should be fine here.
    
    print(f"Launching Solara server for {server_path}...")
    try:
        # We add the package folder to PYTHONPATH so that server.py can import model/agents
        env = os.environ.copy()
        pkg_path = os.path.dirname(server_path)
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = pkg_path + os.pathsep + env["PYTHONPATH"]
        else:
            env["PYTHONPATH"] = pkg_path

        # We use 'uv run solara run' to ensure the environment is correctly set up
        cmd = ["uv", "run", "solara", "run", server_path]
        subprocess.run(cmd, env=env, check=True)
    except KeyboardInterrupt:
        print("\nSimulation stopped.")
    except Exception as e:
        print(f"Failed to launch simulation: {e}")
