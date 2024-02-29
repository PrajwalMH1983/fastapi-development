from fastapi import Body, Depends, FastAPI,Response,status,HTTPException,APIRouter
from sqlalchemy.orm import Session
import models, schemas, utils
import database

router = APIRouter(
    prefix="/users",
    #This is for Swagger doc
    tags=['Users']
)

@router.post("/" ,status_code=status.HTTP_201_CREATED , response_model= schemas.UserResp)
def create_user(user: schemas.UserCreate ,db:Session = Depends(database.get_db)):
    #hash the password 
    user.password = utils.hash(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)    

    return new_user

@router.get("/{id}" , response_model=schemas.UserResp)
def get_user(id: int , db: Session=Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f"User with id: {id} does not exist")
    
    return user