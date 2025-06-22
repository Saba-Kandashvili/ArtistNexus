class BaseManager:
    """
    base class
    """
    def __init__(self, db_path):
        """
        database path

        args:
            db_path (str): path to SQLite db file.
        """
        self.db_path = db_path
        print(f"{self.__class__.__name__} initialized with DB path: {db_path}")