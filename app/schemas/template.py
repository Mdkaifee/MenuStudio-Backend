from pydantic import BaseModel, Field


class TemplateSelectionRequest(BaseModel):
    template_id: str


class TemplateCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    description: str = Field(default='', max_length=200)
    asset_url: str = Field(default='', max_length=5_000_000)
    asset_type: str = Field(default='', max_length=20)


class TemplateUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    description: str = Field(default='', max_length=200)
    asset_url: str = Field(default='', max_length=5_000_000)
    asset_type: str = Field(default='', max_length=20)


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    style_id: str
    is_custom: bool
    asset_url: str = ''
    asset_type: str = ''
