import uvicorn
from database.routes import app
from database.init_db import init_db

def initialize():
    """Initialize the database before running the FastAPI server."""
    init_db("stock_trading.db")

if __name__ == "__main__":
    initialize()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
