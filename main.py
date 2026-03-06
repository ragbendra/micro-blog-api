from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.security import create_access_token, decode_access_token
from db import crud, schemas
from db.database import SessionLocal, engine
from db.models import Base, User

Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    email = decode_access_token(token)
    user = crud.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@app.post("/auth/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, email=credentials.email, password=credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token({"sub": user.email}),
        "token_type": "bearer",
    }


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db=db, user_id=user_id)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db=db, skip=skip, limit=limit)


@app.post("/users/{user_id}/posts", response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return crud.create_user_post(db=db, post=post, user_id=user_id)


@app.get("/posts", response_model=list[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_posts(db=db, skip=skip, limit=limit)
