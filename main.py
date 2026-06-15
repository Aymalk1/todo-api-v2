from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Todo as TodoModel

app = FastAPI()

Base.metadata.create_all(bind=engine)

class Todo(BaseModel):
    title: str
    description: str
    done: bool = False
    priority: str = "medium"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "todo api is running"}

@app.get("/todos")
def get_todos(db: Session = Depends(get_db)):
    return db.query(TodoModel).all()

@app.post("/todos")
def create_todo(todo: Todo, db: Session = Depends(get_db)):
    db_todo = TodoModel(
        title=todo.title,
        description=todo.description,
        done=todo.done,
        priority=todo.priority
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        return {"error": "Todo not found"}
    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        return {"error": "Todo not found"}
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted"}

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated: Todo, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        return {"error": "Todo not found"}
    todo.title = updated.title
    todo.description = updated.description
    todo.done = updated.done
    todo.priority = updated.priority
    db.commit()
    db.refresh(todo)
    return todo
