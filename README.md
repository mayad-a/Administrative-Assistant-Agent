#  Smart Administrative Assistant - Faculty of Computers & AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green)
![Ollama](https://img.shields.io/badge/Local_LLM-Ollama-black)
![License](https://img.shields.io/badge/License-MIT-orange)

A local, open-source, RAG-based AI Agent designed specifically to support administrative staff and student affairs at the Faculty of Computers and Artificial Intelligence, Al-Riyada University. 

This system acts as a virtual assistant, operating entirely on scraped public faculty data and curated manual FAQs, to provide instant, accurate, and hallucination-free answers to student inquiries.

## ✨ Core Features

* **100% Local & Free:** Powered by local LLMs (Mistral/Gemma via Ollama) and ChromaDB, ensuring zero API costs and full data privacy (Groq API available as a high-speed fallback).
* **Zero-Hallucination Architecture:** Implements a custom **Confidence Gate** (Threshold: 0.38) that bypasses the LLM entirely if retrieved context is insufficient.
* **Gap Logger (Business Intelligence):** Automatically logs unanswered queries into a `query_gaps.jsonl` file. This acts as concrete evidence to request further internal documents from the administration.
* **Tiered Response System:** Dynamically formats responses based on retrieval confidence (Full Answer, Partial Answer with caution, or Direct Contact Routing).
* **Multilingual Support:** Uses `intfloat/multilingual-e5-base` embeddings and `langdetect` to seamlessly handle both Arabic and English queries.

## 🛠️ Tech Stack

* **Orchestration:** LangChain
* **Vector Database:** ChromaDB
* **LLM Inference:** Ollama (Local) / Groq API (Cloud Fallback)
* **Embeddings:** HuggingFace (`multilingual-e5-base`)
* **Web Scraping:** `crawl4ai`, `markdownify`
* **UI:** Gradio (with RTL support for Arabic)

## 🏗️ System Architecture

The system utilizes a 5-layer RAG pipeline:
1.  **Data Ingestion:** Scrapes the faculty website, extracts tables, and integrates manual FAQs.
2.  **Vector Store:** Embeds chunks into three separate ChromaDB collections (`web_pages`, `manual_faqs`, `structured_data`).
3.  **Confidence Gate & Retrieval:** Evaluates the highest similarity score. If `< 0.38`, it routes to the Gap Logger and Fallback Formatter.
4.  **LLM Generation:** Generates grounded answers based strictly on retrieved context.
5.  **User Interface:** Gradio chat interface with real-time source citations and feedback mechanisms.

## 🚀 Quick Start & Installation

**1. Clone the repository:**
```bash
git clone [https://github.com/yourusername/smart-admin-assistant.git](https://github.com/yourusername/smart-admin-assistant.git)
cd smart-admin-assistant
