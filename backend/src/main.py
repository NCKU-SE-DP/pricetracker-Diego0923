from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import sentry_sdk
from .config import (
    SENTRY_DSN, 
    SENTRY_TRACES_SAMPLE_RATE, 
    SENTRY_PROFILES_SAMPLE_RATE, 
    DEFAULT_SCHEDULER_INTERVAL_MINUTES, 
    CORS_ALLOW_ORIGINS
)
from .database import Base, engine, get_db, SessionLocal
from .routers import user, news, price
from src.routers.news import fetch_and_store_news
from sqlalchemy.orm import Session
from .models import NewsArticle
import logging
from fastapi.responses import JSONResponse
from fastapi.requests import Request

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 初始化 Sentry，用於錯誤追蹤和性能監控
sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
    profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
)

# 創建 FastAPI 應用實例
app = FastAPI()

# 配置 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化資料庫
Base.metadata.create_all(bind=engine)

# 初始化背景排程器
background_scheduler = BackgroundScheduler()

def scheduled_fetch_and_store_news():
    try:
        # 手動創建資料庫會話
        with next(get_db()) as db:  # 使用 `next(get_db())` 來獲取會話
            fetch_and_store_news(db)
    except Exception as e:
        logger.error(f"Error occurred during scheduled news fetch: {e}")

# 設置排程器任務
background_scheduler.add_job(scheduled_fetch_and_store_news, "interval", minutes=DEFAULT_SCHEDULER_INTERVAL_MINUTES)

@app.on_event("startup")
def start_scheduler():
    db = SessionLocal()
    if db.query(NewsArticle).count() == 0:
        # should change into simple factory pattern
        fetch_and_store_news()
        db.close()
        try:
            background_scheduler.add_job(fetch_and_store_news, "interval", minutes=DEFAULT_SCHEDULER_INTERVAL_MINUTES)
            background_scheduler.start()
        except Exception as e:
            logger.error(f"Error setting up scheduler: {e}")
            raise


@app.on_event("shutdown")
def shutdown_scheduler():
    """
    應用關閉時關閉背景排程器
    """
    try:
        background_scheduler.shutdown()
    except Exception as e:
        logger.error(f"Error occurred during scheduler shutdown: {e}")

# 包含路由模組
app.include_router(user.router)
app.include_router(news.router)
app.include_router(price.router)

# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions and return a JSON response with error details.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(exc)
        },
    )