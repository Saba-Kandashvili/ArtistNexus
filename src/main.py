# src/main.py (Final Version: GUI Launcher)

import os
import sys

# another weird path stuff
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

from ui.main_window import AppGUI

if __name__ == "__main__":
    # ui
    app = AppGUI(db_path=config.DATABASE_NAME)

    app.mainloop()