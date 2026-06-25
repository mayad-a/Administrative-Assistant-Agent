"""
Core RAG Orchestrator
Connects ChromaDB, LangDetect, Confidence Gate, Fallback Logic, and Groq LLM.
"""

import os
from pathlib import Path
from typing import List, Tuple
from langdetect import detect

from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import (
    VECTOR_STORE_DIR, EMBEDDING_MODEL, GROQ_API_KEY, GROQ_MODEL, 
    CONFIDENCE_THRESHOLD, TOP_K_RESULTS, 
    SYSTEM_PROMPT_AR_PATH, SYSTEM_PROMPT_EN_PATH
)
from app.logger import get_logger
from app.confidence_gate import check_confidence, filter_low_confidence
from app.gap_logger import log_gap
from app.response_formatter import generate_fallback_response

logger = get_logger(__name__)

# Initialize components globally to avoid reloading
_embeddings = None
_web_store = None
_faq_store = None
_llm = None
_memory_history = []  # Stores (user_msg, assistant_msg)

def init_components():
    global _embeddings, _web_store, _faq_store, _llm
    if _embeddings is None:
        logger.info("Initializing RAG components...")
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        _web_store = Chroma(
            collection_name="web_pages", 
            embedding_function=_embeddings, 
            persist_directory=str(VECTOR_STORE_DIR)
        )
        
        _faq_store = Chroma(
            collection_name="manual_faqs", 
            embedding_function=_embeddings, 
            persist_directory=str(VECTOR_STORE_DIR)
        )
        
        _llm = ChatGroq(
            temperature=0.1, # Low temperature for factual accuracy
            model_name=GROQ_MODEL,
            groq_api_key=GROQ_API_KEY
        )

def load_prompt(lang: str) -> str:
    path = SYSTEM_PROMPT_AR_PATH if lang == "ar" else SYSTEM_PROMPT_EN_PATH
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    # Fallback minimal prompt if file is missing
    return "Context:\n{context}\n\nHistory:\n{history}\n\nQuestion: {question}\nAnswer:"

def get_standalone_query(query: str, history: List[Tuple[str, str]]) -> str:
    if not history:
        return query
    
    history_text = "\n".join([f"User: {u}\nAssistant: {a}" for u, a in history[-2:]])
    prompt = f"""Based on the conversation history, rewrite the user's follow-up question to be a complete standalone question in Arabic.
If it is already a complete question, just return it as is. Do not answer it.

History:
{history_text}

Follow-up: {query}
Standalone Question:"""
    
    try:
        response = _llm.invoke(prompt)
        standalone = response.content.strip()
        # Clean up if the LLM adds prefixes
        for prefix in ["Standalone Question:", "السؤال المستقل:", "السؤال:", "Question:"]:
            if standalone.startswith(prefix):
                standalone = standalone[len(prefix):].strip()
        return standalone
    except Exception as e:
        logger.error(f"Failed to contextualize query: {e}")
        return query

def process_query(query: str) -> str:
    """Main function to handle user query."""
    init_components()
    
    # 1. Detect Language
    try:
        lang = "ar" if detect(query) == "ar" else "en"
    except:
        lang = "ar"
        
    logger.info(f"Processing query (Lang: {lang}): {query}")

    # 1.5 Contextualize query if there is history
    search_query = get_standalone_query(query, _memory_history)
    if search_query != query:
        logger.info(f"Contextualized Search Query: {search_query}")

    # 2. Parallel Retrieval (Simulated sequentially for simplicity, but fast enough locally)
    # Get top K from both collections using the standalone query
    web_results = _web_store.similarity_search_with_score(search_query, k=TOP_K_RESULTS)
    faq_results = _faq_store.similarity_search_with_score(search_query, k=TOP_K_RESULTS)
    
    # 3. Merge and Prioritize (User requested web_pages to have higher priority)
    # L2 distance: lower is better. We subtract 0.05 from web_pages scores to artificially boost them.
    combined_results = []
    for doc, score in web_results:
        combined_results.append((doc, score - 0.05))
        
    for doc, score in faq_results:
        combined_results.append((doc, score))
        
    # Sort by the adjusted distance (lowest first)
    combined_results.sort(key=lambda x: x[1])
    
    # Take overall Top K
    top_results = combined_results[:TOP_K_RESULTS]
    
    # 4. Confidence Gate
    # Threshold check. Using the original distance metric concept: lower is better.
    # Check if the best score is acceptable.
    if not check_confidence(top_results, CONFIDENCE_THRESHOLD):
        # Even the best result is worse than the threshold
        best_score = top_results[0][1] if top_results else None
        logger.warning(f"Confidence Gate REJECTED query. Best score: {best_score}")
        log_gap(query, best_score)
        return generate_fallback_response(query, lang)
        
    # 5. Filter garbage chunks (if some chunks in top K are above threshold)
    filtered_results = filter_low_confidence(top_results, CONFIDENCE_THRESHOLD)
    
    # 6. Construct Context
    context_text = "\n\n---\n\n".join([doc.page_content for doc, score in filtered_results])
    
    # 6.5 HARDCODED RULES (Forcing the Dean's name and Faculty scope)
    hardcoded_rules = "معلومة هامة جداً وثابتة: عميد كلية الحاسبات والذكاء الاصطناعي (أو عميد الجامعة كما يقول المستخدم بالخطأ أحياناً) هو الأستاذ الدكتور يحيى الحلوجي."
    context_text = hardcoded_rules + "\n\n---\n\n" + context_text
    
    # 7. LLM Generation
    prompt_template = load_prompt(lang)
    
    # Format history manually from our list (last 5 turns as requested)
    history_text = ""
    for u, a in _memory_history[-5:]:
        history_text += f"User: {u}\nAssistant: {a}\n\n"
    
    formatted_prompt = prompt_template.format(
        context=context_text,
        chat_history=history_text,
        question=query
    )
    
    logger.info("Sending prompt to Groq LLM...")
    response = _llm.invoke(formatted_prompt)
    
    # 8. Update Memory
    _memory_history.append((query, response.content))
    
    return response.content

# For local testing
if __name__ == "__main__":
    while True:
        q = input("\nUser: ")
        if q.lower() in ['exit', 'quit']:
            break
        ans = process_query(q)
        print(f"\nAssistant: {ans}")
