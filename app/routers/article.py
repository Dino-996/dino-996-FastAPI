from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_db, get_current_user
from app.models.article import Article
from app.models.user import User
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from app.services.article import get_article_or_404
from app.services.exceptions import ArticleNotFound, ArticleForbidden

router = APIRouter(prefix="/articles", tags=["articles"])

# GET all articles
@router.get(path="", response_model=list[ArticleResponse])
async def list_articles(limit: int = Query(5, ge=1, le=20), offset: int = Query(0, ge=0), db: AsyncSession = Depends(get_db)):
    """ Returns the list of articles of the authenticated user"""
    result = await db.execute(
        select(Article)
        .order_by(Article.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()

# GET single article
@router.get(path="/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """ Return a single article"""
    try:
        return await get_article_or_404(db, article_id)
    except (ArticleNotFound, ArticleForbidden) as e:
        _handle_article_exceptions(e)

# POST article
@router.post(path="", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(payload: ArticleCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Create a new article associated with the authentication admin"""
    article = Article(
        **payload.model_dump(),       # Expands the schema fields
        owner_id=current_user.id,     # Associate the article with the admin
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article

# PUT article
@router.put(path="/{article_id}", response_model=ArticleResponse)
async def update_article(article_id: int, payload: ArticleUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Update the article fields in the body if the admin is authenticated """
    try:
        article = await get_article_or_404(db, article_id, owner_id=current_user.id)
    except (ArticleNotFound, ArticleForbidden) as e:
        _handle_article_exceptions(e)
    else:
        # Update only fields that are not None in the payload
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(article, field, value)

        await db.commit()
        await db.refresh(article)
        return article

# DELETE article
@router.delete(path="/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Deleted an article if the user is authenticated """
    try:
        article = await get_article_or_404(db, article_id, owner_id=current_user.id)
    except (ArticleNotFound, ArticleForbidden) as e:
        _handle_article_exceptions(e)
    else:
        await db.delete(article)
        await db.commit()

# Handle
def _handle_article_exceptions(exc: Exception) -> None:
    """ Translate domain exceptions in HTTP responses """
    if isinstance(exc, ArticleNotFound):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    if isinstance(exc, ArticleForbidden):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")