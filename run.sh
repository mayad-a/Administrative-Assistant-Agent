#!/bin/bash
# =============================================
# Smart Admin Assistant — Run (Linux/Mac)
# =============================================

echo ""
echo "  Starting Smart Admin Assistant..."
echo "  ================================="
echo ""

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "  [OK] Virtual environment activated"
else
    echo "  [!!] No virtual environment found. Create one first."
    exit 1
fi

# Run the Gradio app
echo "  [..] Launching Gradio on http://localhost:7860"
echo ""
python app/main.py
