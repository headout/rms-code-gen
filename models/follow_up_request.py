from pydantic import BaseModel

class PluguinFollowUp(BaseModel):
    session_id: str
    message: str