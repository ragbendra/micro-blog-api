from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr


class PostBase(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1, max_length=500)


class UserCreate(UserBase):
    password: str = Field(min_length=6)
    model_config = {"from_attributes": True}


class PostCreate(PostBase):
    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str


class Post(PostBase):
    id: int
    author_id: int
    model_config = {"from_attributes": True}


class User(UserBase):
    id: int
    posts: list[Post] = Field(default_factory=list)
    model_config = {"from_attributes": True}
