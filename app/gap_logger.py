"""
Gap Logger Module
Logs user queries that were rejected by the confidence gate.
Helps the university identify missing information on their website or FAQs.
"""

import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import GAP_LOG_PATH
from app.logger import get_logger

logger = get_logger(__name__)

def log_gap(query: str, best_score: float = None):
    """
    Logs a failed query to query_gaps.jsonl.
    """
    try:
        # Ensure directory exists
        GAP_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "best_distance_score": best_score,
            "status": "unanswered_low_confidence"
        }
        
        with open(GAP_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
        logger.info(f"Gap logged: '{query}' (score: {best_score})")
    except Exception as e:
        logger.error(f"Failed to log query gap: {e}")
