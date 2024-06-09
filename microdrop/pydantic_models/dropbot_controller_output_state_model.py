from pydantic import BaseModel


class DBOutputStateModel(BaseModel):
    """ Pydantic model for Dropbot output state """
    Signal: str
    OutputState: bool


class DBChannelsChangedModel(BaseModel):
    """ Pydantic model for Dropbot channels changed """
    Signal: str
    Channels: str


class DBVoltageChangedModel(BaseModel):
    """ Pydantic model for Dropbot voltage changed """
    Signal: str
    Voltage: str


class DBChannelsMetastateChanged(BaseModel):
    """ Pydantic model for Dropbot channels metastate changed """
    Signal: str
    Drops: str
