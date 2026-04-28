from app.models.article import Article
from app.services.exceptions import ArticleForbidden, ArticleNotFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_article_or_404(db: AsyncSession, article_id: int, owner_id: int | None = None) -> Article:
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if article is None:
        raise ArticleNotFound(f"Article {article_id} not found")
    if owner_id is not None and article.owner_id != owner_id:
        raise ArticleForbidden(f"User {owner_id} is not the owner of article {article.id}")
    return article
