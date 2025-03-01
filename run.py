#!/Users/david/Desktop/ds/venv/bin/python3

#ds/run.py
import sys
import os
import subprocess

def main():
    # Determine the current operating system
    platform = sys.platform
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    if platform.startswith("win"):
        script = os.path.join(script_dir, "auto_commit_windows.py")
    elif platform == "darwin":
        script = os.path.join(script_dir, "auto_commit_mac.py")
    else:
        # Default to the mac version for other OS (e.g., Linux)
        script = os.path.join(script_dir, "auto_commit_mac.py")
    
    # Pass along any command-line arguments (excluding the script name)
    args = sys.argv[1:]
    
    # Execute the chosen script using the current Python interpreter
    result = subprocess.run([sys.executable, script] + args)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()