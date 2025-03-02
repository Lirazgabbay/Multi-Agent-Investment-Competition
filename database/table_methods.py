"""
    A class to manage database operations.
"""
from database.db import DB

class TableMethods:
    '''
        Contains a TableMethods class for higher-level operations,
        like creating tables and processing events, using the DB class
    '''
    def __init__(self, db: DB):
        self.db = db

    def create_table(self, table_name: str, columns: dict):
        """
        Create a table in the database.

        Args:
            table_name (str): The name of the table to create.
            columns (dict): A dictionary of column names and their SQL data types.
        """
        if not columns:
            raise Exception("Error creating table: No columns provided.")
        if table_name == "" or table_name is None:
            raise Exception("Error creating table: No table name provided.")
        try:
            # Build the column definitions from the provided dictionary
            column_definitions = ", ".join(f"{column_name} {data_type}" for column_name, data_type in columns.items())

            table_schema = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {column_definitions}
            );
            """

            self.db.execute(table_schema)
            self.db.commit()

            print(f"Table '{table_name}' created successfully.")

        except Exception as e:
            print(f"Error creating table '{table_name}': {e}")
            self.db.rollback()  # Rollback to maintain database integrity


    def insert_to_table(self, table_name: str, columns: dict):
        """
        Insert a row into a table in the database.

        Args:
            table_name (str): The name of the table to insert into.
            columns (dict): A dictionary of column names and their values to insert into the table for the row.
        """
        if not columns:
            raise Exception("Error inserting data: No data provided.")
        if table_name == "" or table_name is None:
            raise Exception("Error inserting data: No table name provided.")
        try:
            # Build the column names and placeholders for the query
            column_names = ", ".join(columns.keys())
            value_placeholders = ", ".join("?" for _ in columns)

            insert_query = f"""
            INSERT INTO {table_name} ({column_names})
            VALUES ({value_placeholders});
            """

            self.db.execute(insert_query, tuple(list(columns.values())))
            self.db.commit()

            print(f"Data inserted into table '{table_name}' successfully.")

        except Exception as e:
            print(f"Error inserting data into table '{table_name}': {e}")
            self.db.rollback()  # Rollback to maintain database integrity
  
  
    def fetch_from_table(self, table_name: str, columns: list = None, where_clause: str = None):
        """
        Fetches data from the specified table.

        Args:
            table_name (str): The name of the table to fetch data from.
            columns (list, optional): A list of column names to fetch. Defaults to None, which fetches all columns.
            where_clause (str, optional): A WHERE clause to filter the results. Defaults to None.

        Returns:
            list: A list of dictionaries, where each dictionary represents a row in the table.
        """
        try:
            if columns:
                columns_str = ", ".join(columns)
            else:
                columns_str = "*"

            query = f"""
            SELECT {columns_str}
            FROM {table_name}
            """

            if where_clause:
                query += f" WHERE {where_clause}"

            cursor = self.db.execute(query)
            result = cursor.fetchall()

            # Get column names from cursor description
            if not columns:
                columns = [column[0] for column in cursor.description]

            # Convert the result to a list of dictionaries
            fetched_data = []
            for row in result:
                row_dict = {}
                for i, column_value in enumerate(row):
                    row_dict[columns[i]] = column_value
                fetched_data.append(row_dict)

            return fetched_data

        except Exception as e:
            print(f"Error fetching data from table '{table_name}': {e}")
            self.db.rollback()
            return []  # Return empty list instead of None on error