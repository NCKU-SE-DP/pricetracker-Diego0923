import requests
import itertools
import os
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends
import json
from ..config import OPENAI_API_KEY, ANTHROPIC_API_KEY,OPENAI_MODEL,ANTHROPIC_MODEL
from ..database import get_db, SessionLocal
from ..models import NewsArticle
from ..schemas import PromptRequest, NewsSummaryRequestSchema, NewsSummaryCustomModelSchema
from sqlalchemy.orm import Session
from ..service import get_news_article_upvote_details
from ..dependence import authenticate_user_token
from ..service import toggle_news_article_upvote
from src.crawler.udn_crawler import UDNCrawler
from src.crawler.crawler_base import NewsWithSummary
import itertools
from src.llm_client.openai_client import OpenAIClient
from src.llm_client.anthropic_client import AnthropicClient
from src.llm_client.base import RelevanceEvaluation

_id_counter = itertools.count(start=1000000)
router = APIRouter()  
crawler = UDNCrawler()
openai_client = OpenAIClient(api_key=OPENAI_API_KEY,model=OPENAI_MODEL)
anthropic_client = AnthropicClient(api_key=ANTHROPIC_API_KEY,model=ANTHROPIC_MODEL)

#checked
@router.post("/api/v1/news/{id}/upvote")
def handle_news_article_upvote(
        id,
        db=Depends(get_db),
        user=Depends(authenticate_user_token),
):
    message = toggle_news_article_upvote(id, user.id, db)
    return {"message": message}

#checked
@router.get("/api/v1/news/user_news")
def get_user_specific_news(
        db=Depends(get_db),
        username=Depends(authenticate_user_token)
):
    news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    result = []
    for article in news:
        upvotes, upvoted = get_news_article_upvote_details(article.id, username.id, db)
        result.append(
            {
                **article.__dict__,
                "upvotes": upvotes,
                "is_upvoted": upvoted,
            }
        )
    return result
#checked
@router.get("/api/v1/news/news")
def get_user_specific_news(
    db: Session = Depends(get_db)
):
    """
    獲取用戶特定的新聞，包括投票狀態
    """
    news_articles = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    user_specific_articles = []
    for article in news_articles:
        upvotes, upvoted = get_news_article_upvote_details(article.id, None, db)
        user_specific_articles.append(
            {
                **article.__dict__,
                "upvotes": upvotes,
                "is_upvoted": upvoted,
            }
        )
    return user_specific_articles

#checked
@router.post("/api/v1/news/news_summary")
async def news_summary(payload: NewsSummaryRequestSchema, user = Depends(authenticate_user_token)):
    response = {}
    result = openai_client.generate_summary(payload.content)
    if result:
        result = json.loads(result)
        response["summary"] = result["影響"]
        response["reason"] = result["原因"]
    return response

@router.post("/api/v1/news/news_summary_custom_model")
async def news_summary_custom_model(
        payload: NewsSummaryCustomModelSchema, 
        u=Depends(authenticate_user_token)
):
    """
    Get summary of the news article using a custom AI model (OpenAI or Anthropic).
    """
    if payload.ai_model == "openai":
        ai_client = openai_client
    elif payload.ai_model == "anthropic":
        ai_client = anthropic_client
    result = ai_client.generate_summary(payload.content)
    print("->", result, "<-")
    return parse_summary_result(result)

#checked
@router.post("/api/v1/news/search_news")
async def search_news(request: PromptRequest):
    prompt = request.prompt
    news_list = []
    keywords = openai_client.extract_search_keywords(prompt)
    # Should change into simple factory pattern
    news_items = fetch_news_info(keywords, is_initial_fetch=False)
    for news_item in news_items:
        try:
            detailed_news = news_elements(crawler.parse(news_item.url))
            detailed_news["id"] = next(_id_counter)
            news_list.append(detailed_news)
        except Exception as e:
            print(e)
    return sorted(news_list, key=lambda x: x["time"], reverse=True)

def add_news_to_db(news_data):
    """
    將新聞資料添加到資料庫中
    """
    crawler.save(news_data, Session())

def fetch_and_store_news(is_initial=False):
    """
    get new info

    :param is_initial:
    :return:
    """
    news_data = fetch_news_info("價格", is_initial)
    for news in news_data:
        title = news.title
        relevance = openai_client.evaluate_relevance(title)
        if relevance == RelevanceEvaluation.HIGH:
            detailed_news = crawler.validate_and_parse(news.url)

            if detailed_news is None:
                continue

            result = openai_client.generate_summary(" ".join(detailed_news.content))
            detailed_news = NewsWithSummary(
                url=detailed_news.url,
                title=detailed_news.title,
                time=detailed_news.time,
                content=detailed_news.content,
                summary=result["影響"],
                reason=result["原因"],
            )
            add_news_to_db(detailed_news)

def fetch_news_info(search_term, is_initial_fetch=False):
    return crawler.get_headline(search_term, (1, 10) if is_initial_fetch else 1)
    
def process_news_item(news):
    """
    Fetches detailed content from a news article.
    """
    response = requests.get(news["titleLink"])
    soup = BeautifulSoup(response.text, "html.parser")
    # 標題
    title = soup.find("h1", class_="article-content__title").text
    time = soup.find("time", class_="article-content__time").text
    # 定位到包含文章内容的 <section>
    content_section = soup.find("section", class_="article-content__editor")

    paragraphs = [
        p.text
        for p in content_section.find_all("p")
        if p.text.strip() != "" and "▪" not in p.text
    ]
    detailed_news = {
        "url": news["titleLink"],
        "title": title,
        "time": time,
        "content": paragraphs,
    }

    return detailed_news

def news_elements(news):
    return {
        "url": news.url,
        "title": news.title,
        "time": news.time,
        "content": news.content,
    }

def parse_summary_result(result):
    """
    Parses the summary result JSON and extracts 'summary' and 'reason'.

    :param result: The JSON-formatted summary result string.
    :return: A dictionary with keys 'summary' and 'reason', or an empty dictionary if parsing fails.
    """
    response_data = {}
    if result:
        try:
            result = json.loads(result)
            response_data["summary"] = result["影響"]
            response_data["reason"] = result["原因"]
        except json.JSONDecodeError:
            return response_data
    return response_data

def news_exists(news_id, db: Session):
    return db.query(NewsArticle).filter_by(id=news_id).first() is not None