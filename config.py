import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    # LLM settings - supports "openai" or "anthropic"
    "llm_provider": os.getenv("LLM_PROVIDER", "openai"),
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", ""),

    # Two-tier models (like original TradingAgents framework)
    # Quick: fast/cheap for news analysis and report formatting
    # Deep: smarter for technical analysis and final strategy decisions
    "model_quick": os.getenv("LLM_MODEL_QUICK", "gpt-5-mini"),
    "model_deep": os.getenv("LLM_MODEL_DEEP", "gpt-5.2"),

    # Data settings
    "short_term_days": 30,
    "long_term_days": 180,
    "intraday_period": "5d",
    "intraday_interval": "15m",
}
