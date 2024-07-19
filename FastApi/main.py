from fastapi import FastAPI  , HTTPException ,Depends
from typing import Annotated, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal ,engine
import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origns =[
    "http://localhost:3000",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origns,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],)
class TransactionBase(BaseModel):
    amount: float
    category: str
    description: str
    is_income: bool
    date_created: str

class TransactionModel(TransactionBase):
    id: int

    class Config:
        from_attributes = True



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependencies =Annotated[Session ,Depends(get_db)]
models.Base.metadata.create_all(bind=engine)


@app.post("/transactions/", response_model=TransactionModel)
async def create_transaction(transaction: TransactionBase, db:  db_dependencies):
    new_transaction=models.Transaction(**transaction.dict())
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


@app.get("/transactions/" , response_model=List[TransactionModel])

async def get_transactions(db:  db_dependencies , skip: int=0 ,limit: int=100):
    transaction=db.query(models.Transaction).offset(skip).limit(limit).all()
    return transaction
