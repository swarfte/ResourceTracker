"""
PyInstaller build script for ResourceTracker
Run this script to create a standalone .exe file

Prerequisites:
    pip install pyinstaller

Usage:
    python build_exe.py
"""

import os
import subprocess
import sys

def build_exe():
    """Build the standalone executable using PyInstaller"""

    print("=" * 60)
    print("ResourceTracker - Building standalone executable")
    print("=" * 60)
    print()

    # Check if pyinstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("ERROR: PyInstaller not found!")
        print("Please install it first: pip install pyinstaller")
        return False

    # PyInstaller command for Streamlit app
    # We need to include streamlit, pandas, numpy, and other dependencies
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=ResourceTracker",
        "--onefile",  # Create single executable
        "--windowed",  # No console window (optional)
        "--icon=NONE",  # You can add an icon file here
        "--add-data=app.py;.",  # Include the main app file
        "--add-data=utils;utils",  # Include utils folder
        "--add-data=pages;pages",  # Include pages folder
        "--hidden-import=streamlit",
        "--hidden-import=streamlit.runtime.scriptrunner",
        "--hidden-import=streamlit.runtime.stats",
        "--hidden-import=pandas",
        "--hidden-import=numpy",
        "--hidden-import=openpyxl",
        "--hidden-import=xlrd",
        "--hidden-import=python-dateutil",
        "streamlit_run_wrapper.py",  # Entry point
    ]

    # Create the wrapper script first
    create_wrapper_script()

    print("\nBuilding executable with PyInstaller...")
    print("This may take several minutes...\n")

    try:
        result = subprocess.run(
            pyinstaller_cmd,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print("\n" + "=" * 60)
        print("Build completed successfully!")
        print(f"Executable location: dist\\ResourceTracker.exe")
        print("=" * 60)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Build failed!")
        print(f"Return code: {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        return False

def create_wrapper_script():
    """Create a wrapper script that runs streamlit run app.py"""
    wrapper_content = '''"""
Wrapper script for PyInstaller to run Streamlit application
"""
import sys
import subprocess

def main():
    """Run the Streamlit app"""
    app_path = getattr(sys, '_MEIPASS', '.') + '\\\\app.py'
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', app_path])

if __name__ == '__main__':
    main()
'''

    with open('streamlit_run_wrapper.py', 'w') as f:
        f.write(wrapper_content)
    print("Created wrapper script: streamlit_run_wrapper.py")

def build_simple_exe():
    """
    Alternative: Simple executable that just runs a batch command
    This is simpler and more reliable for Streamlit apps
    """
    print("\nAlternative: Building simple launcher executable...")

    import PyInstaller.__main__

    PyInstaller.__main__.run([
        '--name=ResourceTracker',
        '--onefile',
        '--windowed',
        'simple_launcher.py'
    ])

if __name__ == '__main__':
    print("\nChoose build option:")
    print("1. Full PyInstaller build (includes all dependencies - larger file)")
    print("2. Simple launcher (requires Python installed - smaller file)")
    print("3. Exit")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == '1':
        build_exe()
    elif choice == '2':
        create_simple_launcher()
        build_simple_exe()
    elif choice == '3':
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice")

def create_simple_launcher():
    """Create a simple launcher script"""
    launcher_content = '''"""
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
    subprocess.run([python_exe, '-m', 'streamlit', 'run', app_path])

if __name__ == '__main__':
    main()
'''

    with open('simple_launcher.py', 'w') as f:
        f.write(launcher_content)
    print("Created simple launcher: simple_launcher.py")
