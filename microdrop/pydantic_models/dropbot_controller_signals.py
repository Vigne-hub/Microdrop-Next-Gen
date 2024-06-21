from pydantic import BaseModel


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


class DBConnectionStateModel(BaseModel):
    """ Pydantic model for Dropbot connection """
    Signal: str
    Connected: str


class DBChipInsertStateModel(BaseModel):
    """ Pydantic model for Dropbot chip inserted state """
    Signal: str
    ChipInserted: str


class DBErrorModel(BaseModel):
    """ Pydantic model for Dropbot error """
    Signal: str
    Error: str
