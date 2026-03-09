"""
Simple launcher for ResourceTracker
This script runs streamlit run app.py
"""
import subprocess
import sys
import os

def main():
    """Run the Streamlit app"""
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Activate virtual environment if it exists
    venv_python = os.path.join(script_dir, '.venv', 'Scripts', 'python.exe')
    if os.path.exists(venv_python):
        python_exe = venv_python
        print("Using virtual environment...")
    else:
        python_exe = sys.executable
        print("Using system Python...")

    # Run streamlit
    app_path = os.path.join(script_dir, 'app.py')
    print(f"Starting ResourceTracker from: {app_path}")
    subprocess.run([python_exe, '-m', 'streamlit', 'run', app_path])

if __name__ == '__main__':
    main()
