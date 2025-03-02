from database.table_methods import TableMethods
from database.db import DB
import sqlite3

def init_db(db_name: str):
    """
    Initialize the database with the required tables.
    """
    db = DB(sqlite3, db_name)
    table = TableMethods(db)

    table.create_table("API_calls", {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "params": "TEXT",
        "url": "TEXT NOT NULL",
        "response": "TEXT NOT NULL",
        "timestamp": "DATETIME DEFAULT CURRENT_TIMESTAMP"
    })

    db.close()