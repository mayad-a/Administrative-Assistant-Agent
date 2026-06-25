"""
Confidence Gate Module
Evaluates retrieval results. If the highest similarity score is below CONFIDENCE_THRESHOLD,
it flags the query for fallback logic instead of Hallucination.
"""

from typing import List, Tuple
from langchain_core.documents import Document

def check_confidence(results: List[Tuple[Document, float]], threshold: float) -> bool:
    """
    Evaluates whether the retrieved documents meet the minimum confidence threshold.
    Similarity search with cosine distance in Chroma: lower distance is better, 
    but Langchain wraps it as similarity score or distance depending on the metric.
    Assuming we use default L2 distance: lower is more similar.
    Wait, Langchain's similarity_search_with_score with default Chroma returns L2 distances.
    Wait, let's look at config. CONFIDENCE_THRESHOLD = 0.38
    If it's cosine distance, smaller is better.
    Let's assume threshold is the MAXIMUM allowed distance.
    So if min(scores) <= threshold, we are confident.
    """
    if not results:
        return False
        
    # Get the best (minimum) distance score
    best_score = min(score for doc, score in results)
    
    # If the best score is less than or equal to the threshold, we have high confidence.
    return best_score <= threshold

def filter_low_confidence(results: List[Tuple[Document, float]], threshold: float) -> List[Tuple[Document, float]]:
    """
    Filters out any specific document chunks that are worse than the threshold,
    even if the best score passed. This ensures we don't feed garbage context to the LLM.
    """
    return [(doc, score) for doc, score in results if score <= threshold]
