
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Todo as TodoModel, User as UserModel
from auth import hash_password, verify_password, create_access_token, get_current_user

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

class Todo(BaseModel):
	title : str
	description : str
	done : bool = False
	priority : str = "medium"

class UserCreate(BaseModel):
	username : str
	password :str

class UserLogin(BaseModel):
	username : str
	password : str

@app.get("/")
def root():
	return {"Message" : "Your API is runnning."}

@app.get("/todos")
def get_todos(db : Session = Depends(get_db)):
	return db.query(TodoModel).all()

@app.post("/todos")
def create_todos(todo:Todo, db : Session = Depends(get_db), current_user: str = Depends(get_current_user)):
	db_todo = TodoModel(
		title = todo.title,
		description = todo.description,
		done = todo.done,
		priority = todo.priority
	)
	db.add(db_todo)
	db.commit()
	db.refresh(db_todo)
	return db_todo

@app.get("/todos/{todo_id}")
def get_todo(todo_id : int, db : Session = Depends(get_db)):
	todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
	if not todo:
		return {"error" : "todo not found"}
	else:
		return todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id : int, db : Session = Depends(get_db), current_user: str = Depends(get_current_user)):
	todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
	if not todo:
		return {"error" : "todo not found"}
	else:
		db.delete(todo)
		db.commit()
		return {"message" : "todo list deleted"}

@app.put("/todos/{todo_id}")
def update_todo(todo_id : int, updated : Todo, db : Session = Depends(get_db), current_user: str = Depends(get_current_user)):
	todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
	if not todo:
		return {"error" : "todo not found"}
	else:
		todo.title = updated.title
		todo.description = updated.description
		todo.done = updated.done
		todo.priority = updated.priority
		db.commit()
		db.refresh(todo)
		return todo

@app.post("/register")
def register(user : UserCreate, db : Session = Depends(get_db)):
	hashed = hash_password(user.password)
	
	db_user = UserModel(
		username = user.username,
		hashed_password = hashed
		)
	db.add(db_user)
	db.commit()
	return db_user

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
	db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
	if not db_user:
		return {"error" : "Username not found"}
	if not verify_password(user.password, db_user.hashed_password):
		return {"error" : "Incorrect password"}
	token = create_access_token({"username": db_user.username})
	return {"access_token": token}
