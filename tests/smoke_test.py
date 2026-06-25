"""
Sprint 0 — Smoke Test
Verifies the development environment is correctly set up.

Run: python tests/smoke_test.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

results = []


def check(name: str, passed: bool, message: str = ""):
    """Record a test result."""
    status = PASS if passed else FAIL
    results.append((name, passed, message))
    print(f"  {status} {name}" + (f" — {message}" if message else ""))


def main():
    print("\n" + "=" * 60)
    print("  Smart Admin Assistant — Smoke Test (Sprint 0)")
    print("=" * 60 + "\n")

    # ─── 1. Python Version ──────────────────────────────────
    print("📌 Python Environment")
    v = sys.version_info
    check(
        "Python >= 3.10",
        v.major == 3 and v.minor >= 10,
        f"Found {v.major}.{v.minor}.{v.micro}",
    )

    # ─── 2. Required Packages ───────────────────────────────
    print("\n📦 Required Packages")
    packages = {
        "langchain": "langchain",
        "langchain_community": "langchain-community",
        "chromadb": "chromadb",
        "sentence_transformers": "sentence-transformers",
        "gradio": "gradio",
        "langdetect": "langdetect",
        "groq": "groq",
        "dotenv": "python-dotenv",
    }

    for import_name, pip_name in packages.items():
        try:
            __import__(import_name)
            check(f"{pip_name}", True)
        except ImportError:
            check(f"{pip_name}", False, f"pip install {pip_name}")

    # Optional packages
    print("\n📦 Optional Packages")
    optional = {
        "crawl4ai": "crawl4ai",
        "markdownify": "markdownify",
        "supabase": "supabase",
    }
    for import_name, pip_name in optional.items():
        try:
            __import__(import_name)
            check(f"{pip_name}", True)
        except ImportError:
            print(f"  {WARN} {pip_name} — not installed (optional)")

    # ─── 3. Environment Variables ───────────────────────────
    print("\n🔑 Environment Variables")
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")

    groq_key = os.getenv("GROQ_API_KEY", "")
    check(
        "GROQ_API_KEY set",
        bool(groq_key) and groq_key != "your_groq_api_key_here",
        "Key found" if (bool(groq_key) and groq_key != "your_groq_api_key_here") else "Missing or placeholder — update .env",
    )

    supabase_url = os.getenv("SUPABASE_URL", "")
    if supabase_url and supabase_url != "your_supabase_url_here":
        check("SUPABASE_URL set", True)
    else:
        print(f"  {WARN} SUPABASE_URL — not configured (optional)")

    # ─── 4. Project Structure ───────────────────────────────
    print("\n📂 Project Structure")
    required_dirs = [
        "app", "app/prompts", "ingestion", "data", "data/raw_web",
        "data/manual_faqs", "data/structured", "vector_store",
        "vector_store/chroma_db", "logs", "tests",
    ]
    for d in required_dirs:
        path = PROJECT_ROOT / d
        check(f"{d}/", path.is_dir())

    required_files = [
        "app/config.py", "app/logger.py", "app/main.py",
        "app/rag_chain.py", "app/confidence_gate.py",
        "app/gap_logger.py", "app/response_formatter.py", "app/ui.py",
        "app/prompts/system_ar.txt", "app/prompts/system_en.txt",
        "app/prompts/fallback_ar.txt", "app/prompts/fallback_en.txt",
        "requirements.txt", ".env", ".gitignore",
    ]
    print("\n📄 Key Files")
    for f in required_files:
        path = PROJECT_ROOT / f
        check(f, path.is_file())

    # ─── 5. Config Module ───────────────────────────────────
    print("\n⚙️  Config Module")
    try:
        from app.config import GROQ_API_KEY, CONFIDENCE_THRESHOLD, PROJECT_ROOT as PR
        check("app.config imports", True)
        check("CONFIDENCE_THRESHOLD valid", isinstance(CONFIDENCE_THRESHOLD, float), f"Value: {CONFIDENCE_THRESHOLD}")
    except Exception as e:
        check("app.config imports", False, str(e))

    # ─── 6. Groq API Connectivity ───────────────────────────
    print("\n🌐 Groq API Connectivity")
    try:
        from groq import Groq

        if groq_key and groq_key != "your_groq_api_key_here":
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
                messages=[{"role": "user", "content": "Say 'Hello' in one word."}],
                max_tokens=10,
            )
            answer = response.choices[0].message.content.strip()
            check("Groq API call", True, f"Response: {answer}")
        else:
            print(f"  {WARN} Skipped — GROQ_API_KEY not configured")
    except Exception as e:
        check("Groq API call", False, str(e))

    # ─── Summary ────────────────────────────────────────────
    passed = sum(1 for _, p, _ in results if p)
    failed = sum(1 for _, p, _ in results if not p)
    total = len(results)

    print("\n" + "=" * 60)
    print(f"  Results: {passed}/{total} passed" + (f", {failed} failed" if failed else ""))

    if failed == 0:
        print("  🎉 All checks passed! Environment is ready.")
    else:
        print("  ⚠️  Some checks failed. Fix them before proceeding.")
    print("=" * 60 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
