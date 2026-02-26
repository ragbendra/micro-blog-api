from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str = None

class PostBase(BaseModel):
    title: str
    content: str

class UserCreate(UserBase):
    pass

class PostCreate(PostBase):
    pass

class Post(PostBase): # Response Schema
    id: int
    author_id: int
    model_config = {"from_attributes": True}

class User(UserBase): # Response Schema
    id: int
    posts: list[Post] = []
    model_config = {"from_attributes": True}