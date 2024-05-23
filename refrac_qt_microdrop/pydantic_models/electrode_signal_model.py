from pydantic import BaseModel

class ElectrodeStateChanged(BaseModel):
    Signal: str
    Channel: int
    State: bool

class MetastateChanged(BaseModel):
    Signal: str
    Channel: int
    Metastate: object

class StateChanged(BaseModel):
    Signal: str
    Channel: int
    State: bool