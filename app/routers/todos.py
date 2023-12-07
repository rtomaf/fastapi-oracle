from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from app import database
from sqlalchemy.orm import Session
from app import database_models
from app import pydantic_models
from app import oauth2

router = APIRouter()

@router.get('/')
async def get_all_todos(db: Annotated[Session, Depends(database.get_db)], username: Annotated[str, Depends(oauth2.get_current_username)]):


    list_of_todos: List[database_models.Todos] = db.query(database_models.Todos).filter(database_models.Todos.owner_username == username).all()

    return list_of_todos

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_todo(db: Annotated[Session, Depends(database.get_db)], todo: pydantic_models.Todo, username: Annotated[str, Depends(oauth2.get_current_username)]):

    new_todo = database_models.Todos(**todo.model_dump(), owner_username=username)

    # new_todo = database_models.Todos()
    # new_todo.title = todo.title
    # new_todo.description = todo.description

    try:
        db.add(new_todo)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Could not add new todo")

    return {"result" : "Todo created"}

@router.delete('/{id}')
async def delete_todo(db: Annotated[Session, Depends(database.get_db)], id: int, username: Annotated[str, Depends(oauth2.get_current_username)]):

    todo_with_id_query = db.query(database_models.Todos).filter(database_models.Todos.id == id, database_models.Todos.owner_username == username)

    todo_with_id = todo_with_id_query.first()

    if todo_with_id == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id: {id} does not exist.")
    
    todo_with_id_query.delete()
    db.commit()

    return {"result" : "todo deleted"}

@router.put('/{id}')
async def update_todo(db: Annotated[Session, Depends(database.get_db)], id: int, todo: pydantic_models.Todo, username: Annotated[str, Depends(oauth2.get_current_username)]):
    
    todo_with_id_query = db.query(database_models.Todos).filter(database_models.Todos.id == id, database_models.Todos.owner_username == username)

    todo_with_id = todo_with_id_query.first()

    if todo_with_id == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id: {id} does not exist.")
    
    todo_with_id_query.update(todo.model_dump())
    db.commit()

    return todo_with_id_query.first()