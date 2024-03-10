from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean, LargeBinary
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    friends=Column(JSON,default=[])
    groups_name=Column(JSON,default=[])
    password = Column(String)
    profile_photo = Column(String,default="empty")
    profile_massage = Column(String,default="상태메세지를 입력하세요")
    # 이거 추하면 사진 정보도 저장할 수 있음
    # photo_data = Column(LargeBinary)

class Chat(Base):
    __tablename__ = "chat"
    index = Column(Integer, primary_key=True)
    sender_name = Column(String)
    receiver_name = Column(String)
    in_sender_message = Column(String)
    in_receiver_message = Column(String)
    group=Column(Boolean,default=False)