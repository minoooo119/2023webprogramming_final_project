from sqlalchemy.orm import Session
from models import User, Chat
from schema import UserSchema, UserSchemaAddFriend, ChatRequest, ChatRequestCreate
import json

def db_register_user(db:Session, name,password):
    db_item=User(name=name,password=password)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def db_add_friend(db:Session, user:User, friend_name:str):
    
    # Add friend to the user's friend list
    friends_list = json.loads(user.friends) if user.friends else []
    friends_list.append(friend_name)
    user.friends = json.dumps(friends_list,ensure_ascii=False)

    db.commit()
    db.refresh(user)
    print(user.friends)

    return user

def db_add_group(db:Session, user:User, group_name:str):
    
    # Add friend to the user's friend list
    groups_list = json.loads(user.groups_name) if user.groups_name else []
    groups_list.append(group_name)
    user.groups_name = json.dumps(groups_list,ensure_ascii=False)

    db.commit()
    db.refresh(user)
    print(user.groups_name)

    return user


def add_chat(db:Session, item:ChatRequest):
    db_item=Chat(sender_name=item.sender_name, receiver_name=item.receiver_name, 
                 in_sender_message=item.in_sender_message, in_receiver_message=item.in_receiver_message)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db.query(Chat).all()

def get_chat(db:Session):
    return db.query(Chat).all()