from pydantic import BaseModel, Field
from datetime import date as Date

class ArticleCreate(BaseModel):
    """Create new article"""
    title: str = Field(default=..., title="Article title", description="The title of the article", max_length=100)
    description: str | None = Field(title="Article description", description="Short summary of the article", default=None, max_length=225)
    tags: list[str] = Field(title="Tags", description="List of keywords", default_factory=list)
    date: Date = Field(..., title="Article date", description="Publication or updating the article")
    excerpt: str | None = Field(title="Excerpt", description="Preview text of the article", default=None, max_length=225)
    image: str | None = Field(title="Image URL", description="URL of the main image associated with the article", default=None)
    imageAlt: str | None = Field(title="Image Alt Text", description="Alternative text for the article image for accessibility purposes", default=None)

class ArticleUpdate(BaseModel):
    """Update article"""
    title: str | None = Field(title="Article title", description="The title of the article", default=None, max_length=100)
    description: str | None = Field(title="Article description", description="Short summary of the article", default=None, max_length=225)
    tags: list[str] | None = Field(title="Tags", description="List of keywords", default=None)
    date: Date | None = Field(title="Article date", description="Publication or updating the article", default=None)
    excerpt: str | None = Field(title="Excerpt", description="Preview text of the article", default=None)
    image: str | None = Field(title="Image URL", description="URL of the main image associated with the article", default=None)
    imageAlt: str | None = Field(title="Image Alt Text", description="Alternative text for the article image for accessibility purposes", default=None)

class ArticleResponse(BaseModel):
    """Get article"""
    id: int = Field(..., title="Article ID", description="The article ID")
    title: str = Field(default=..., title="Article title", description="The title of the article", max_length=100)
    description: str | None = Field(title="Article description", description="Short summary of the article", default=None, max_length=225)
    tags: list[str] = Field(title="Tags", description="List of keywords", default_factory=list)
    date: Date = Field(..., title="Article date", description="Publication or updating the article")
    excerpt: str | None = Field(title="Excerpt", description="Preview text of the article", default=None, max_length=225)
    image: str | None = Field(title="Image URL", description="URL of the main image associated with the article", default=None)
    imageAlt: str | None = Field(title="Image Alt Text", description="Alternative text for the article image for accessibility purposes", default=None)

    model_config = {"from_attributes": True}