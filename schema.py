from pydantic import BaseModel
from typing import Optional



class StudentCreate(BaseModel):
    name:str
    age:int

class StudentResponse(BaseModel):
    id:int
    name:str
    age:int



class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None