import os
# 資料庫連接 URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///news_database.db")

# JWT 配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "1892dhianiandowqd0n")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
DEFAULT_TOKEN_EXPIRE_MINUTES = int(os.getenv("DEFAULT_TOKEN_EXPIRE_MINUTES", 15))

# Sentry 配置
SENTRY_DSN = os.getenv("SENTRY_DSN", "https://4001ffe917ccb261aa0e0c34026dc343@o4505702629834752.ingest.us.sentry.io/4507694792704000")
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", 1.0))
SENTRY_PROFILES_SAMPLE_RATE = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", 1.0))

# OpenAI API 金鑰
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN", "")  # 確保替換為您的 OpenAI API 金鑰
OPENAI_AI_MODEL = os.getenv("OPENAI_AI_MODEL", "openai:gpt-4o")  # 確保替換為您的 OpenAI AI 模型

# Anthropic API 金鑰
ANTHROPIC_TOKEN = os.getenv("ANTHROPIC_TOKEN", "")  # 確保替換為您的 ANTHROPIC_API_KEY 金鑰
ANTHROPIC_API_MODEL = os.getenv("ANTHROPIC_API_MODEL", "anthropic:claude-3-5-sonnet-20240620")  # 確保替換為您的 ANTHROPIC_API_MODEL 模型
# 背景任務排程間隔
DEFAULT_SCHEDULER_INTERVAL_MINUTES = int(os.getenv("DEFAULT_SCHEDULER_INTERVAL_MINUTES", 100))

# CORS 配置
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:8080").split(",")
INITIAL_FETCH_PAGE_RANGE = range(1, 10)

PriceChangeRelevance = "你是一個關聯度評估機器人，請評估新聞標題是否與「民生用品的價格變化」相關，並給予'high'、'medium'、'low'評價。(僅需回答'high'、'medium'、'low'三個詞之一)"
newsImpactAndCause = "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})"
DesiredKeywords = "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)"

testai = "愚公能移星期三嗎？大禹能治薪水嗎?神農能嘗加班的苦嗎?精卫能填錢包嗎?后羿能射上班日嗎?嫦娥能飛出加班的窗戶嗎?伏羲能創造加班費嗎?女媧能補星期天嗎?" 