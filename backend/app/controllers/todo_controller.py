from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.utilis.logger import get_logger
from typing import List, Optional
from app.models.todo import Todo
import uuid
from datetime import datetime
from app.utilis.paginator import paginate
from datetime import timezone


logger = get_logger(__name__)

class TodoController:
    
    @staticmethod
    def index(
            current_user: User, 
            db: Session, 
            page: Optional[int], 
            page_size: Optional[int], 
            search: Optional[str], 
            completed: Optional[bool], 
            due_date: Optional[str], 
            priority: Optional[str]) -> List[Todo]:
        try:
            todos = db.query(Todo).filter(Todo.user_id == current_user.id)
            
            if search:
                todos = todos.filter(Todo.title.contains(search))
            
            # apply completed filter only when explicitly provided (True or False)
            if completed is not None:
                todos = todos.filter(Todo.is_completed == completed)
            
            if due_date:
                todos = todos.filter(Todo.due_date == due_date)
            
            if priority:
                todos = todos.filter(Todo.priority == priority)
            
            # order todos by their explicit order value (1 = top)
            todos = todos.order_by(Todo.order.asc()).all()

            # sane defaults and max limit for page size
            if not page_size:
                page_size = 20
            elif page_size > 50:
                page_size = 50

            # aplica paginação
            items_on_page, paginator = paginate(todos, page or 1, page_size)

            # retorna no formato desejado
            return {
                "items": items_on_page,
                "page": paginator.page,
                "page_size": paginator.page_size,
                "total": paginator.total_items,
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Index todo error for user {current_user.id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="We found some issue trying to get your todos")

    
    @staticmethod
    def today(current_user: User, db: Session, priority: Optional[str] = None) -> List[Todo]:
        try:
            now_utc = datetime.now(timezone.utc)
            start_of_day = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day.replace(hour=23, minute=59, second=59, microsecond=999999)

            todos = db.query(Todo).filter(
                Todo.user_id == current_user.id,
                Todo.is_completed == False,  # noqa: E712
                Todo.due_date >= start_of_day,
                Todo.due_date <= end_of_day,
            )

            if priority:
                todos = todos.filter(Todo.priority == priority)

            todos = todos.order_by(Todo.order.asc()).all()

            page_size = 50
            items_on_page, paginator = paginate(todos, 1, page_size)

            return {
                "items": items_on_page,
                "page": paginator.page,
                "page_size": paginator.page_size,
                "total": paginator.total_items,
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Today todo error for user {current_user.id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="We found some issue trying to get your today todos")

    
    @staticmethod
    def store(current_user: User, db: Session, title: str, description: str, priority: str, due_date: datetime) -> dict:
        try:
            #check if title already exists
            chekSameTitleTodo = db.query(Todo).filter(Todo.user_id == current_user.id, Todo.title == title).first()
            if chekSameTitleTodo:
                raise HTTPException(status_code=409, detail="Title already exists")

            #get more high order todo
            getMoreHighOrderTodo = db.query(Todo).filter(Todo.user_id == current_user.id).order_by(Todo.order.desc()).first()
            if not getMoreHighOrderTodo:
                order = 1
            else:
                order = getMoreHighOrderTodo.order + 1

            newTodo = Todo(
                id=uuid.uuid4(),
                order=order,
                user_id=current_user.id,
                title=title,
                description=description,
                is_completed=False,
                due_date=due_date,
                priority=priority,
            )

            db.add(newTodo)
            db.flush()

            return {
                "message": "Todo stored successfully",
                "todo": {
                    "id": newTodo.id,
                    "order": newTodo.order,
                    "title": newTodo.title,
                    "description": newTodo.description,
                    "is_completed": newTodo.is_completed,
                    "due_date": newTodo.due_date,
                    "priority": newTodo.priority,
                }
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Store todo error for user {current_user.id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="We found some issue trying to store your todo")

    
    @staticmethod
    def update(current_user: User, db: Session, id: uuid.UUID, title: str, description: str, priority: str, due_date: datetime) -> dict:
        try:
            # get todo
            todo = db.query(Todo).filter(Todo.id == id, Todo.user_id == current_user.id).first()
            if not todo:
                raise HTTPException(status_code=404, detail="Todo not found")

            # check if title already exists
            if title != todo.title:
                chekSameTitleTodo = db.query(Todo).filter(Todo.user_id == current_user.id, Todo.title == title).first()
                if chekSameTitleTodo:
                    raise HTTPException(status_code=409, detail="Title already exists")

            # check if due date is not empty and is not the past if user changed the value
            if due_date is not None and todo.due_date is not None and due_date <= todo.due_date:
                if due_date <= datetime.now(timezone.utc):
                   raise HTTPException(status_code=422, detail="Due date must be in the future")

            #update todo
            todo.title = title
            todo.description = description
            todo.priority = priority
            todo.due_date = due_date
            db.add(todo)
            db.flush()

            return {
                "message": "Todo completed updated successfully",
                "todo": {
                    "id": todo.id,
                    "order": todo.order,
                    "title": todo.title,
                    "description": todo.description,
                    "is_completed": todo.is_completed,
                    "due_date": todo.due_date,
                    "priority": todo.priority,
                }
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Update todo error for user {current_user.id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="We found some issue trying to update your todo")

    
    @staticmethod
    def update_order(current_user: User, db: Session, id: uuid.UUID, order: int) -> dict:
        try:
            # get todos for the user ordered by current position
            todos = db.query(Todo).filter(Todo.user_id == current_user.id).order_by(Todo.order).all()

            # find the todo with the given id
            current_index = next((idx for idx, t in enumerate(todos) if t.id == id), None)
            if current_index is None:
                raise HTTPException(status_code=404, detail="Todo not found")

            # interpret `order` as the desired 1-based position in the list
            if order < 1:
                new_index = 0
            elif order > len(todos):
                new_index = len(todos) - 1
            else:
                new_index = order - 1

            # remove the todo from its current position and insert at the new index
            todo_to_move = todos.pop(current_index)
            todos.insert(new_index, todo_to_move)

            # re-assign sequential order values so DB matches visual order
            for idx, todo in enumerate(todos, start=1):
                todo.order = idx
                db.add(todo)

            db.flush()

            return {
                "message": "Todo order updated successfully",
                "todo": {
                    "id": todo_to_move.id,
                    "order": todo_to_move.order,
                    "title": todo_to_move.title,
                    "description": todo_to_move.description,
                    "is_completed": todo_to_move.is_completed,
                    "due_date": todo_to_move.due_date,
                    "priority": todo_to_move.priority,
                }
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Update todo order error for user {current_user.id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="We found some issue trying to update your todo order")

    @staticmethod
    def update_completed(current_user: User, db: Session, id: uuid.UUID, is_completed: bool) -> dict:
        try:
            #get todo
            todo = db.query(Todo).filter(Todo.id == id, Todo.user_id == current_user.id).first()
            if not todo:
                raise HTTPException(status_code=404, detail="Todo not found")

            #update todo completed
            todo.is_completed = is_completed
            db.add(todo)
            db.flush()

            return {
                "message": "Todo completed updated successfully",
                "todo": {
                    "id": todo.id,
                    "order": todo.order,
                    "title": todo.title,
                    "description": todo.description,
                    "is_completed": todo.is_completed,
                    "due_date": todo.due_date,
                    "priority": todo.priority,
                }
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Update todo completed error for user {current_user.id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="We found some issue trying to update your todo completed")
    
    @staticmethod
    def destroy(current_user: User, db: Session, id: uuid.UUID) -> dict:
        try:
            #get todo
            todo = db.query(Todo).filter(Todo.id == id, Todo.user_id == current_user.id).first()
            if not todo:
                raise HTTPException(status_code=404, detail="Todo not found")

            #delete todo
            db.delete(todo)
            db.flush()

            # normalize remaining todos order so it stays contiguous (1..N)
            remaining_todos = db.query(Todo).filter(Todo.user_id == current_user.id).order_by(Todo.order).all()
            for idx, t in enumerate(remaining_todos, start=1):
                t.order = idx
                db.add(t)

            db.flush()

            return {
                "message": "Todo deleted successfully",
                "todo": {
                    "id": todo.id,
                    "order": todo.order,
                    "title": todo.title,
                    "description": todo.description,
                    "is_completed": todo.is_completed,
                    "due_date": todo.due_date,
                    "priority": todo.priority,
                }
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Destroy todo error for user {current_user.id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="We found some issue trying to delete your todo")