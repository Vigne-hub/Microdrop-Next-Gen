from pydantic import BaseModel


class DBOutputStateModel(BaseModel):
    Signal: str
    OutputState: bool


class DBChannelsChangedModel(BaseModel):
    Signal: str
    Channels: str


class DBVoltageChangedModel(BaseModel):
    Signal: str
    Voltage: str


class DBChannelsMetastateChanged(BaseModel):
    Signal: str
    Drops: str
