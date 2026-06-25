import hashlib
from pathlib import Path
import sys
import requests
from markdownify import markdownify

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.config import RAW_WEB_DIR, VECTOR_STORE_DIR, EMBEDDING_MODEL
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

URL_TO_SCRAPE = "https://rst.edu.eg/%d8%b9%d9%86-%d8%a7%d9%84%d8%ac%d8%a7%d9%85%d8%b9%d8%a9/?lang=ar"
WEB_CHUNK_SIZE = 800
WEB_CHUNK_OVERLAP = 150

def generate_doc_id(doc: Document, idx: int) -> str:
    content = doc.page_content + str(doc.metadata.get("source", "")) + str(idx)
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def scrape_and_ingest():
    print(f"Scraping URL with requests: {URL_TO_SCRAPE}")
    response = requests.get(URL_TO_SCRAPE, verify=False)
    if response.status_code != 200:
        print(f"Failed to scrape. Status code: {response.status_code}")
        return
        
    print("Successfully fetched. Converting to Markdown...")
    markdown_text = markdownify(response.text)
    
    doc = Document(page_content=markdown_text, metadata={"source": "about_university.md", "url": URL_TO_SCRAPE})
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=WEB_CHUNK_SIZE,
        chunk_overlap=WEB_CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents([doc])
    
    for chunk in chunks:
        chunk.metadata["collection"] = "web_pages"
        
    print(f"Split into {len(chunks)} chunks. Embedding and pushing to ChromaDB...")
    
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    vectorstore = Chroma(
        collection_name="web_pages",
        embedding_function=embeddings,
        persist_directory=str(VECTOR_STORE_DIR)
    )
    
    ids = [generate_doc_id(chunk, i) for i, chunk in enumerate(chunks)]
    vectorstore.add_documents(documents=chunks, ids=ids)
    
    print(f"✅ Successfully ingested {len(chunks)} chunks from {URL_TO_SCRAPE} into ChromaDB!")

if __name__ == "__main__":
    try:
        import urllib3
        urllib3.disable_warnings()
        scrape_and_ingest()
    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
