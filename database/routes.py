"""
routes.py - FastAPI routes for logging and retrieving API calls
"""
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from database.table_methods import TableMethods
from database.db import DB
import sqlite3
from database.api_call import APICall
from database.get_api_call_request import GetAPICallRequest
import json

app = FastAPI()

def get_db():
    return DB(sqlite3, 'stock_trading.db')

@app.post("/log_api_call")
def log_api_call(api_call: APICall):
    """
    RESTful endpoint to log an API call.
    Takes in the API call data, validates it, and saves it to the database.
    """
    ...
    if api_call.url == "" or api_call.url is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Missing required fields: 'params', 'url'"
        )
    try:
        db = get_db()
        table_methods = TableMethods(db)

        # Capture the current UTC timestamp
        timestamputc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        params_json = json.dumps(api_call.params)
        data_to_insert = {
            "params": params_json,
            "url": api_call.url,
            "response": api_call.response,
            "timestamp": timestamputc
        }

        table_methods.insert_to_table("API_calls", data_to_insert)
        db.commit()
        db.close()
        return {"data": data_to_insert, "status_code": HTTP_200_OK}

    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log API call: {str(e)}"
        )
    

@app.post("/get_api_call")
def get_api_call(request: GetAPICallRequest):
    """
    RESTful endpoint to retrieve API calls.
    """
    if not request.url:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Missing required fields: 'params', 'url'"
        )

    try:
        db = get_db()
        print(db)
        table_methods = TableMethods(db)

        # Convert params dictionary to JSON string
        params_json = json.dumps(request.params)
        response = table_methods.fetch_from_table(
            "API_calls",
            where_clause=f"params = '{params_json}' AND url = '{request.url}'"
        )
        if response is None or response == []:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No data found for the given parameters."
            )
        db.close()
        return {"data": response, "status_code": HTTP_200_OK}

    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get API call: {str(e)}"
        )
