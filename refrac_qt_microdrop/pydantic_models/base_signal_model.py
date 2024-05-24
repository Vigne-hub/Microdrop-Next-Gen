from pydantic import BaseModel


class SignalNameModel(BaseModel):
    Signal: str
    Arg1: type
    Arg2: type
    Arg3: type  # etc....
