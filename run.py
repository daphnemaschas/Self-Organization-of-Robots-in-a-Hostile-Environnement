"""
Group 5
Date: 2026-03-16
Members: Associate 1, Gemini CLI

Main script to launch the RobotMission simulation using Solara (Mesa 3.x).
"""

import subprocess
import os
import signal
import sys

if __name__ == "__main__":
    # Get the absolute path to the server file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(base_dir, "5_robot_mission_MAS2026", "server.py")
    
    # In Mesa 3.x, you run the visualization with: solara run <path_to_server.py>
    # Note: Solara handles the module import, so the numeric folder name should be fine here.
    
    print(f"Launching Solara server for {server_path}...")
    try:
        env = os.environ.copy()
        pkg_path = os.path.dirname(server_path)
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = pkg_path + os.pathsep + env["PYTHONPATH"]
        else:
            env["PYTHONPATH"] = pkg_path

        cmd = ["uv", "run", "solara", "run", server_path]
        
        if sys.platform == "win32":
            process = subprocess.Popen(cmd, env=env, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            process = subprocess.Popen(cmd, env=env, start_new_session=True)
            
        process.wait()

    except KeyboardInterrupt:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        print("\nSimulation stopped.")
    except Exception as e:
        print(f"Failed to launch simulation: {e}")
