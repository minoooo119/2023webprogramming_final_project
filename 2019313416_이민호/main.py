from fastapi import FastAPI, Depends, HTTPException, status,Request,Response, WebSocket
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import FileResponse, RedirectResponse

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

from models import Base, User, Chat
from fastapi.staticfiles import StaticFiles

from crud import db_register_user,  db_add_friend, add_chat, get_chat,db_add_group
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from typing import List
import json
from sqlalchemy import and_

from schema import  UserSchema, UserSchemaAddFriend, ChatRequest, ChatRequestCreate,UserSchemaAddGroup

class NotAuthenticatedException(Exception):
    pass

Base.metadata.create_all(bind=engine)


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
SECRET="super-secret-key"
manager=LoginManager(SECRET,'/login',use_cookie=True,
                        custom_exception=NotAuthenticatedException)



@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request:Request, exc:NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    return RedirectResponse(url="/login")

@manager.user_loader
def get_user(username:str, db:Session=None):
    if not db:
        with SessionLocal() as db:
            return db.query(User).filter(User.name==username).first()
        return db.query(User).filter(User.name==username).first()

@app.get("/getuser")
def get_user_list(db:Session=Depends(get_db)):
    return db.query(User).all()

@app.get("/current_user")
def get_current_user(user=Depends(manager)):
    return user.name


@app.get("/getfriendslist")
def get_friendslist(user=Depends(manager)):
    return user.friends

@app.get("/getgroupslist")
def get_groupslist(user=Depends(manager)):
    return user.groups_name

@app.post("/registerUser")
def register_user(response:Response,
                  data:OAuth2PasswordRequestForm=Depends(),
                  db:Session=Depends(get_db)):
    username=data.username
    password=data.password
    user=db_register_user(db,username,password)
    if user:
        access_token=manager.create_access_token(
            data={'sub':username}
        )
        manager.set_cookie(response,access_token)
        return "User created"
    else:
        return "Failed"
    
@app.get("/register")
def get_register():
    return FileResponse("register.html")

@app.get("/friendchat/{friend_name}")
def get_friendschat(friend_name:str, user=Depends(manager)):
    return FileResponse("client.html")

@app.get("/groupchat/{group_name}")
def get_groupchat(group_name:str, user=Depends(manager)):
    return FileResponse("client.html")


@app.get("/")
def get_root(user=Depends(manager)):
    return FileResponse("onlyfriends.html")

@app.get("/chatlist")
def get_chatlist(user=Depends(manager)):
    return FileResponse("friends.html")

@app.get("/chatcontent")
def get_chatcontent(user=Depends(manager)):
    print(user.friends_json)
    return FileResponse("chatcontent.html")


@app.post("/addfriend")
def get_addfriend(friend_req: UserSchemaAddFriend, db: Session = Depends(get_db), user=Depends(manager)):
     # 사용자 확인
    user = db.query(User).filter(User.id == user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user.id} not found")

    friend_name=  friend_req.friendname;
    # 이미 친구인지 확인
    if friend_name in user.friends:
        raise HTTPException(status_code=400, detail=f"{friend_name} is already a friend")

    # 친구 사용자 확인
    friend_user = db.query(User).filter(User.name == friend_name).first()
    if not friend_user:
        raise HTTPException(status_code=404, detail=f"User {friend_name} not found")
    if friend_user.id == user.id:
        raise HTTPException(status_code=400, detail=f"Cannot add yourself as a friend")

    return db_add_friend(db, user, friend_name), db_add_friend(db, friend_user, user.name)

@app.post("/addgroup")
def get_addgroup(group_req:UserSchemaAddGroup,db:Session=Depends(get_db), user=Depends(manager)):
    print(group_req.groupname)
    print(group_req.members)
    user = db.query(User).filter(User.id == user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user.id} not found")
    db_add_group(db,user,group_req.groupname)

    for member in group_req.members:
        member_user=db.query(User).filter(User.name==member).first()
        if not member_user:
            raise HTTPException(status_code=404, detail=f"User {member} not found")
        db_add_group(db,member_user,group_req.groupname)

    return "Group added"
    



@app.post('/token')
def login(response:Response,data:OAuth2PasswordRequestForm=Depends()):
    username=data.username
    password=data.password
    
    user =get_user(username)
    if not user:
        raise InvalidCredentialsException
    if user.password!=password:
        raise InvalidCredentialsException
    access_token=manager.create_access_token(
        data={'sub':username}
    )
    manager.set_cookie(response,access_token)
    return {'access_token':access_token}


@app.get("/login")
def get_login():
    return FileResponse("login.html")

@app.get("/logout")
def logout(response:Response):
    response=RedirectResponse("/login",status_code=302)
    response.delete_cookie(key="access_token")
    return response

class ConnectionManager: 
    def __init__(self):
        self.active_connections = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
manager_socket = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager_socket.connect(websocket) 
    try:
        while True:
            data = await websocket.receive_text()
            await manager_socket.broadcast(f"{data}")
    except Exception as e:
        pass
    finally:
        await manager_socket.disconnect(websocket)

@app.get("/getchat",response_model=List[ChatRequest])
def get_chat_data(db:Session=Depends(get_db), user=Depends(manager)):
    return get_chat(db)

@app.post("/postchat",response_model=List[ChatRequest])
def post_chat(chat_req:ChatRequestCreate,db:Session=Depends(get_db), user=Depends(manager)):
    return add_chat(db,chat_req)

@app.get("/getlastchat")
def get_last_chat(friend_name:str,db:Session=Depends(get_db), user=Depends(manager)):
    print("username: ",user.name,"  friendname: ",friend_name)
    user = db.query(User).filter(User.id == user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user.id} not found")
    # # chat=db.query(Chat).filter(and_(Chat.sender_name == user.name, Chat.receiver_name == friend_name)).first();
    # print(chat)
    recent_chat = (
        db.query(Chat)
        .filter(
            (
                (Chat.sender_name == friend_name) & (Chat.receiver_name == user.name)
            )
            | (
                (Chat.sender_name == user.name) & (Chat.receiver_name == friend_name)
            )
        )
        .order_by(Chat.index.desc())
        .first()
    )
    print(recent_chat)
    if recent_chat!=None:  return recent_chat.in_sender_message
    else : return "No chat"

@app.get("/getlastgroupchat")
def get_last_groupchat(group_name:str,db:Session=Depends(get_db), user=Depends(manager)):
    print("username: ",user.name,"  groupname: ",group_name)
    user = db.query(User).filter(User.id == user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID not found")
    # # chat=db.query(Chat).filter(and_(Chat.sender_name == user.name, Chat.receiver_name == friend_name)).first();
    # print(chat)
    recent_chat = (
        db.query(Chat)
        .filter(
            (
                (Chat.sender_name != user.name) & (Chat.receiver_name == group_name)
            )
            | (
                (Chat.sender_name == user.name) & (Chat.receiver_name == group_name)
            )
        )
        .order_by(Chat.index.desc())
        .first()
    )
    print(recent_chat)
    if recent_chat!=None:  return recent_chat.in_sender_message
    else : return "No chat"

@app.get("/getProfileInfo")
def get_profileInfo(thisPerson:str,db:Session=Depends(get_db),user=Depends(manager)):
    print("username: ",user.name,"  thisPerson: ",thisPerson)
    user = db.query(User).filter(User.name == thisPerson).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID not found")
    return user.profile_massage, user.profile_photo

class UserProfileUpdate(BaseModel):
    profile_photo: str
    profile_message: str

@app.post("/changeProfileInfo")
def change_profileInfo(profile_info:UserProfileUpdate,db:Session=Depends(get_db),user=Depends(manager)):
    print("Profile Photo:", profile_info.profile_photo)
    print("Profile Message:", profile_info.profile_message)
    user = db.query(User).filter(User.id == user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user.id} not found")
    user.profile_massage=profile_info.profile_message
    user.profile_photo=profile_info.profile_photo
    db.commit()
    db.refresh(user)
    return "Profile changed"
