"""
    Generalized database interaction class to support multiple database backends.
"""

class DB:
    def __init__(self, db_connector, *args, **kwargs):
        """
        Initialize the database connection and cursor using the provided connector.

        Args:
            db_connector (module): The database connector module (e.g., sqlite3).
            *args: parameters for the db_connector.connect() function.
            **kwargs: parameters for the db_connector.connect() function (as key=value pairs).
        """
        self.connector = db_connector.connect(*args, **kwargs)
        self.cursor = self.connector.cursor()

    def execute(self, query: str, params=None):
        """
        Execute a query against the database.

        Args:
            query (str): The SQL query to execute.
            params (tuple or dict, optional): Parameters for the query.

        Returns:
            The result of the query execution.
        """
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor

    def commit(self):
        """Commit the current transaction."""
        self.connector.commit()

    def close(self):
        """Close the database connection."""
        self.connector.close()

    def rollback(self):
        """Rollback the current transaction. undoing any changes made since the last commit."""
        self.connector.rollback()
