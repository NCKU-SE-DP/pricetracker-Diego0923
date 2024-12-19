import json
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, insert
from .config import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, INITIAL_FETCH_PAGE_RANGE, DEFAULT_TOKEN_EXPIRE_MINUTES
from .models import User, NewsArticle, user_news_association_table
from urllib.parse import quote
from fastapi import Depends
from .database import get_db
from src.crawler.udn_crawler import UDNCrawler
crawler = UDNCrawler()
# 設定密碼加密上下文
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    將用戶密碼加密以進行安全存儲
    """
    return password_context.hash(password)

def get_news_article_upvote_details(article_id, uid, db):
    cnt = (
        db.query(user_news_association_table)
        .filter_by(news_articles_id=article_id)
        .count()
    )
    voted = False
    if uid:
        voted = (
                db.query(user_news_association_table)
                .filter_by(news_articles_id=article_id, user_id=uid)
                .first()
                is not None
        )
    return cnt, voted

def toggle_news_article_upvote(username_id, u_id, db):
    existing_upvote = db.execute(
        select(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == username_id,
            user_news_association_table.c.user_id == u_id,
        )
    ).scalar()

    if existing_upvote:
        delete_stmt = delete(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == username_id,
            user_news_association_table.c.user_id == u_id,
        )
        db.execute(delete_stmt)
        db.commit()
        return "Upvote removed"
    else:
        insert_stmt = insert(user_news_association_table).values(
            news_articles_id=username_id, user_id=u_id
        )
        db.execute(insert_stmt)
        db.commit()
        return "Article upvoted"
def get_all_news_articles(db=Depends(get_db)):
    """
    read new

    :param db:
    :return:
    """
    news_articles = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    formatted_articles = []
    for article in news_articles:
        upvotes, upvoted = get_news_article_upvote_details(article.id, None, db)
        formatted_articles.append(
            {**article.__dict__, "upvotes": upvotes, "is_upvoted": upvoted}
        )
    return formatted_articles
