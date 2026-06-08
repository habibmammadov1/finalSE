from pydantic import BaseModel

class Flights(BaseModel):
    flightId : int
    flightNumber : str
    destionation : str
    price : float