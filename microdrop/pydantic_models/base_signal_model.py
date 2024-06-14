from pydantic import BaseModel


class SignalNameModel(BaseModel):
    """ Pydantic model for Dropbot signal names"""
    Signal: str
    Arg1: str
    Arg2: str
    Arg3: str  # etc....
