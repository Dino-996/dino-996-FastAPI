from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import get_db, get_current_user
from app.models.article import Article
from app.models.user import User
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("", response_model=list[ArticleResponse])
async def list_articles(limit: int = Query(5, ge=1, le=20), offset: int = Query(0, ge=0, le=0), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Returns the list of articles of the authenticated user """
    result = await db.execute(
        select(Article)
        .where(Article.owner_id == current_user.id)
        .order_by(Article.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Return a single article of the authenticated user """
    article = await get_user_article(db, article_id, current_user.id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article

@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(payload: ArticleCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Create a new article associated with the authentication user """
    article = Article(
        **payload.model_dump(),       # Expands the schema fields
        owner_id=current_user.id,     # Associate the article with the current user
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article

@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(article_id: int, payload: ArticleUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Update the article fields in the body """
    article = await get_user_article(db, article_id, current_user.id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    # Update only fields that are not None in the payload
    update_data = payload.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(article, field, value)

    await db.commit()
    await db.refresh(article)
    return article

@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user),):
    """ Deleted an article """
    article = await get_user_article(db, article_id, current_user.id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    await db.delete(article)
    await db.commit()

# Helper function
async def get_user_article(db, article_id, user_id):
    """ Returns a user article """
    result = await db.execute(select(Article).where(Article.id == article_id, Article.owner_id == user_id))
    return result.scalar_one_or_none()