"""
Pydantic model for the request body.

Uses the BaseModel class from Pydantic to validate incoming request data against the model, 
raise errors for missing/incorrect fields, and convert JSON into a Python object.
"""
from pydantic import BaseModel
from typing import Dict, Optional, Any

class GetAPICallRequest(BaseModel):
    params: Optional[Dict[str, Any]] = {}
    url: str