from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default='', max_length=220)
    image_url: str = Field(default='', max_length=2_000_000)


class CategoryUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default='', max_length=220)
    image_url: str = Field(default='', max_length=2_000_000)


class CategoryResponse(BaseModel):
    id: str
    restaurant_id: str
    name: str
    description: str
    image_url: str
