from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List


class UserSchema(BaseModel):
    id: Optional[int]
    name: str
    password: str
    friends: str
    class Config:
        orm_mode = True

class UserSchemaAddFriend(BaseModel):
    friendname: str

class UserSchemaAddGroup(BaseModel):
    groupname: str
    members: List[str]


class ChatRequestBase(BaseModel):
    sender_name: str
    receiver_name: str
    in_sender_message: str
    in_receiver_message:str

class ChatRequestCreate(ChatRequestBase):
    pass

class ChatRequest(ChatRequestBase):
    index: Optional[int]
    class Config:
        orm_mode=True