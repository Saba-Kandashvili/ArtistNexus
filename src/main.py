# src/main.py (Final Version: GUI Launcher)

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

# Import the GUI class from our 'ui' package
from ui.main_window import AppGUI

# --- Main Execution Block ---
if __name__ == "__main__":
    # 1. Create an instance of our application's GUI
    app = AppGUI(db_path=config.DATABASE_NAME)

    # 2. Start the Tkinter event loop.
    # This will display the window and wait for user interactions (e.g., clicks).
    app.mainloop()