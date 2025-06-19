import re
from logger_config import logger

def compile_task_pattern(keyword_string):
    if not keyword_string or not isinstance(keyword_string, str):
        logger.warning("⚠️ Invalid keyword input for pattern compilation.")
        return None

    keywords = [kw.strip() for kw in keyword_string.split(",") if kw.strip()]
    if not keywords:
        logger.warning("⚠️ No valid keywords found to compile.")
        return None

    pattern_string = r'\b(?:' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'
    try:
        return re.compile(pattern_string, re.IGNORECASE)
    except re.error as e:
        logger.error(f"❌ Failed to compile regex pattern: {e}")
        return None
