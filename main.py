from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Todo(BaseModel):
	id : int = 0
	title : str
	description : str
	done : bool = False
	priority : str = "medium"

todos = []

@app.get("/")
def root():
	return {"message" : "todo api is running."}

@app.get("/todos")
def get_todos():
	return todos

@app.post("/todos")
def create_todo(todo : Todo):
	todo.id = len(todos)
	todos.append(todo)
	return {"message" : "todo api is created."}

@app.get("/todos/{todo_id}")
def get_id(todo_id : int):
	if todo_id >= len(todos):
		return {"message" : "todo api doesnt exists"}
	else:
		return todos[todo_id]

@app.delete("/todos/{todo_id}")
def del_todo(todo_id : int):
	if todo_id >= len(todos):
		return {"message" : "todo api doenst exists"}
	else:
		return todos.pop(todo_id)

@app.put("/todos/{todo_id}")
def add_todo(todo_id : int, up_todo : Todo):
	if todo_id >= len(todos):
		return {"message" : "todo api doesnt exists"}
	else:
		todos[todo_id] = up_todo
		return {"message" : "Todo updated"}

