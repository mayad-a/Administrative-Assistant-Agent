import json
import os
from pathlib import Path
import time
import sys

# Ensure app is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag_chain import process_query
from app.logger import get_logger

logger = get_logger(__name__)

EVAL_FILE = Path(__file__).parent / "eval_queries.json"

def run_evaluation():
    if not EVAL_FILE.exists():
        logger.error(f"Eval file not found: {EVAL_FILE}")
        return

    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        queries = json.load(f)

    total_queries = len(queries)
    successful_fallbacks = 0
    expected_fallbacks = 0
    successful_keywords = 0
    expected_keywords_queries = 0

    print("\n" + "="*50)
    print("🚀 Starting Automated Evaluation (Sprint 5)")
    print("="*50 + "\n")

    for idx, q_data in enumerate(queries):
        question = q_data["question"]
        expected_fallback = q_data["expected_fallback"]
        expected_keywords = q_data.get("expected_keywords", [])

        if expected_fallback:
            expected_fallbacks += 1
        else:
            expected_keywords_queries += 1

        print(f"[{idx+1}/{total_queries}] Q: {question}")
        
        # Start timing
        start_time = time.time()
        
        # We need to simulate a fresh context to avoid memory carrying over
        # Actually memory in rag_chain is a global list, let's clear it just for evaluation
        import app.rag_chain
        app.rag_chain._memory_history.clear()
        
        try:
            response = process_query(question)
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            continue

        latency = time.time() - start_time
        print(f"   ⏱️ Latency: {latency:.2f}s")
        print(f"   🤖 A: {response.replace(chr(10), ' ')}")

        # Evaluate Fallback Precision
        is_fallback = "عذراً" in response or "لا تتوفر لدي" in response or "جهة الاختصاص" in response or "شؤون الطلاب" in response or "إدارة الكلية" in response

        if expected_fallback:
            if is_fallback:
                print("   ✅ Fallback Check: SUCCESS (Correctly fell back)")
                successful_fallbacks += 1
            else:
                print("   ❌ Fallback Check: FAILED (Hallucinated an answer instead of falling back)")
        else:
            if is_fallback:
                print("   ❌ Keyword Check: FAILED (System fell back unexpectedly. Data might be missing)")
            else:
                # Evaluate Faithfulness / Keyword hit
                hits = sum(1 for kw in expected_keywords if kw in response)
                if expected_keywords and hits > 0:
                    print(f"   ✅ Keyword Check: SUCCESS (Found {hits}/{len(expected_keywords)} expected keywords)")
                    successful_keywords += 1
                elif expected_keywords:
                    print("   ⚠️ Keyword Check: PARTIAL/FAILED (Did not find expected keywords, but gave an answer)")
                else:
                    print("   ✅ Keyword Check: SUCCESS")
                    successful_keywords += 1

        print("-" * 50)
        # Small delay to avoid API rate limits on Groq
        time.sleep(2)

    print("\n" + "="*50)
    print("📊 EVALUATION RESULTS")
    print("="*50)
    
    fallback_precision = (successful_fallbacks / expected_fallbacks * 100) if expected_fallbacks > 0 else 100
    hit_rate = (successful_keywords / expected_keywords_queries * 100) if expected_keywords_queries > 0 else 100
    
    print(f"1. Fallback Precision: {fallback_precision:.1f}% ({successful_fallbacks}/{expected_fallbacks} correctly rejected)")
    print(f"2. Hit Rate (Keyword Match): {hit_rate:.1f}% ({successful_keywords}/{expected_keywords_queries} correctly answered)")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_evaluation()
