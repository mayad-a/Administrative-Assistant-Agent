"""
Sprint 2: Data Ingestion Pipeline
Loads raw Markdown files, chunks them, generates embeddings using multilingual-e5-base,
and stores them in ChromaDB. Uses stable IDs to avoid duplicate insertions.
"""

import os
import hashlib
from pathlib import Path
from typing import List

import chromadb
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import DATA_DIR, RAW_WEB_DIR, MANUAL_FAQS_DIR, VECTOR_STORE_DIR, EMBEDDING_MODEL
from app.logger import get_logger

logger = get_logger(__name__, str(DATA_DIR.parent / "logs" / "ingestion.log"))

# ─── Configuration ──────────────────────────────────────────

# Web Pages Chunking Strategy
WEB_CHUNK_SIZE = 800  # Characters, ~400 tokens roughly
WEB_CHUNK_OVERLAP = 150

def generate_doc_id(doc: Document, idx: int) -> str:
    """Generate a deterministic ID based on content, source, and chunk index."""
    content = doc.page_content + str(doc.metadata.get("source", "")) + str(idx)
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def process_web_pages() -> List[Document]:
    """Load and chunk crawled web pages."""
    if not RAW_WEB_DIR.exists():
        logger.warning("No raw web directory found. Skipping web pages.")
        return []
    
    loader = DirectoryLoader(str(RAW_WEB_DIR), glob="*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=WEB_CHUNK_SIZE,
        chunk_overlap=WEB_CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    
    # Tag them
    for chunk in chunks:
        chunk.metadata["collection"] = "web_pages"
    
    logger.info(f"Loaded {len(docs)} web pages, split into {len(chunks)} chunks.")
    return chunks

def process_manual_faqs() -> List[Document]:
    """Load and chunk manual FAQs based on Markdown headers."""
    if not MANUAL_FAQS_DIR.exists():
        logger.warning("No manual FAQs directory found. Skipping.")
        return []
        
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    
    all_chunks = []
    
    for file_path in MANUAL_FAQS_DIR.glob("*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Split using headers
            splits = markdown_splitter.split_text(text)
            
            # Add file source metadata
            for split in splits:
                split.metadata["source"] = str(file_path.name)
                split.metadata["collection"] = "manual_faqs"
            
            all_chunks.extend(splits)
        except Exception as e:
            logger.error(f"Failed to process FAQ file {file_path.name}: {e}")
            
    logger.info(f"Loaded FAQ files, split into {len(all_chunks)} chunks.")
    return all_chunks

def ingest_data():
    logger.info("Starting ingestion pipeline...")
    
    # 1. Load Embedding Model
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL} (This may take a moment to download on first run)...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # 2. Process Documents
    web_chunks = process_web_pages()
    faq_chunks = process_manual_faqs()
    
    # 3. Setup Chroma
    logger.info("Connecting to ChromaDB...")
    
    # We will use Langchain's Chroma integration for each collection
    collections = {
        "web_pages": web_chunks,
        "manual_faqs": faq_chunks,
        # structured_data will be added in future sprints
    }
    
    total_added = 0
    for collection_name, chunks in collections.items():
        if not chunks:
            continue
            
        logger.info(f"Ingesting into collection: {collection_name} ({len(chunks)} chunks)...")
        
        # Prepare IDs
        ids = [generate_doc_id(chunk, i) for i, chunk in enumerate(chunks)]
        
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(VECTOR_STORE_DIR)
        )
        
        # Add documents in batches to avoid OOM freezes and to show progress
        batch_size = 100
        from tqdm import tqdm
        for i in tqdm(range(0, len(chunks), batch_size), desc=f"Ingesting {collection_name}"):
            batch_chunks = chunks[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            vectorstore.add_documents(documents=batch_chunks, ids=batch_ids)
            
        total_added += len(chunks)
        
    logger.info(f"Ingestion complete. Processed and stored {total_added} total chunks.")
    
    # Simple verification test
    if total_added > 0:
        logger.info("Running a quick sanity check search on 'web_pages'...")
        test_store = Chroma(collection_name="web_pages", embedding_function=embeddings, persist_directory=str(VECTOR_STORE_DIR))
        results = test_store.similarity_search_with_score("الريادة", k=1)
        if results:
            doc, score = results[0]
            logger.info(f"Sanity check success! Found document with distance: {score:.4f}")
            logger.debug(f"Preview: {doc.page_content[:100]}")

if __name__ == "__main__":
    ingest_data()
