from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

# CORS setup (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)

Base.metadata.create_all(bind=engine)

class TaskCreate(BaseModel):
    title: str
    description: str

class TaskRead(TaskCreate):
    id: int

@app.post("/tasks/", response_model=TaskRead)
def create_task(task: TaskCreate):
    db = SessionLocal()
    db_task = Task(title=task.title, description=task.description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return db_task

@app.get("/tasks/", response_model=List[TaskRead])
def read_tasks():
    db = SessionLocal()
    tasks = db.query(Task).all()
    db.close()
    return tasks

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    db.close()
    return {"message": "Task deleted"}
