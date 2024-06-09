from pydantic import BaseModel


class SignalNameModel(BaseModel):
    """ Pydantic model for Dropbot signal names"""
    Signal: str
    Arg1: type
    Arg2: type
    Arg3: type  # etc....
