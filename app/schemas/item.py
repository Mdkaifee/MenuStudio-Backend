from pydantic import BaseModel, Field


class MenuItemCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    description: str = Field(default='', max_length=300)
    image_url: str = Field(default='', max_length=2_000_000)
    price: float = Field(gt=0)


class MenuItemUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    description: str = Field(default='', max_length=300)
    image_url: str = Field(default='', max_length=2_000_000)
    price: float = Field(gt=0)


class MenuItemResponse(BaseModel):
    id: str
    restaurant_id: str
    name: str
    category: str
    description: str
    image_url: str
    price: float
