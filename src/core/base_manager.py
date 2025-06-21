# src/core/base_manager.py

class BaseManager:
    """
    A base class that provides common attributes for other manager classes.
    In this case, it holds the path to the database file.
    """
    def __init__(self, db_path):
        """
        Initializes the BaseManager with the database path.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        self.db_path = db_path
        print(f"{self.__class__.__name__} initialized with DB path: {db_path}")