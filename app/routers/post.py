from typing import List, Optional
from fastapi import Body, Depends, FastAPI,Response,status,HTTPException,APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
import models, schemas, oauth2
import database

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

#@router.get("/" , response_model=List[schemas.Post])
@router.get("/" , response_model=List[schemas.PostVote])
#@router.get("/")
def get_posts(db:Session=Depends(database.get_db) , current_user: int = Depends(oauth2.get_current_user) , limit:int = 10 , skip: int = 0 , search: Optional[str] = ""):
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    results = db.query(models.Post , func.count(models.Vote.post_id).label("votes")).join(
        models.Vote , models.Vote.post_id == models.Post.id , isouter=True).group_by(models.Post.id).all()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    #eturn posts
    #print(posts)
    return posts

@router.post("/" ,status_code=status.HTTP_201_CREATED , response_model=schemas.Post)
def create_posts(post: schemas.PostCreate , db: Session = Depends(database.get_db) , current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute(""" INSERT INTO posts(title , content , published) VALUES (%s , %s , %s) RETURNING * """ , (post.title , post.content , post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    print(current_user)
    new_post = models.Post(owner_id=current_user.id ,  **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


#title str and response str

@router.get("/{id}" , response_model=schemas.PostVote)
def get_post(id: int , db:Session=Depends(database.get_db) , current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s""" , (str(id)))
    # new_post = cursor.fetchone()
    #new_post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    #post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f"post with id: {id} was not found")
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail=f"Not Authorized to perform requested action")
    return post

@router.delete("/{id}" , status_code= status.HTTP_204_NO_CONTENT)
def delete_post(id:int , db: Session=Depends(database.get_db) , current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """ , (str(id) ,))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if deleted_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f"post with id: {id} does not exist")
    
    if deleted_post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail=f"Not Authorized to perform requested action")

    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}" , response_model=schemas.Post)
def update_post(id: int , post: schemas.PostCreate , db: Session=Depends(database.get_db)  , current_user: int = Depends(oauth2.get_current_user)):
    # index = find_post_index_id(id)
    # cursor.execute(""" UPDATE posts SET title = %s , content = %s , published = %s WHERE id = %s RETURNING * """ , (post.title , post.content , post.published , str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    updated_post = db.query(models.Post).filter(models.Post.id == id)

    if updated_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f"post with id: {id} does not exist")
    
    if update_post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail=f"Not Authorized to perform requested action")
    
    updated_post.update(post.model_dump() , synchronize_session=False)
    db.commit()
    
    # post_dict = post.model_dump()
    # post_dict['id'] = id
    # my_posts[index] = post_dict
    return updated_post.first()