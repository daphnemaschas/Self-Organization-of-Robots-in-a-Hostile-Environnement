import subprocess
import os
import sys
import time

def check_solara():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(base_dir, "5_robot_mission_MAS2026", "server.py")
    
    env = os.environ.copy()
    pkg_path = os.path.dirname(server_path)
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = pkg_path + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = pkg_path

    print(f"Testing Solara launch for {server_path}...")
    
    # We use Popen so we can check it periodically
    process = subprocess.Popen(
        ["uv", "run", "solara", "run", server_path],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it 15 seconds to start up or fail
    start_time = time.time()
    while time.time() - start_time < 15:
        if process.poll() is not None:
            # It finished, which means it failed (it's a server)
            stdout, stderr = process.communicate()
            print("Solara server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        time.sleep(1)
    
    # Still running, assuming success
    print("Solara server seems to have started successfully.")
    process.terminate()
    return True

if __name__ == "__main__":
    if check_solara():
        sys.exit(0)
    else:
        sys.exit(1)
