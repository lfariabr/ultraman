from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from . import database

app = FastAPI(title="FastAPI Supabase Demo")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ItemBase(BaseModel):
    title: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Database model
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class ItemModel(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
database.Base.metadata.create_all(bind=database.engine)

# API endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with Supabase!"}

@app.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    items = db.query(ItemModel).offset(skip).limit(limit).all()
    return items

@app.post("/items/", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(database.get_db)):
    db_item = ItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item