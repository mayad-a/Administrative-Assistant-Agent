"""
UI Module (Sprint 4)
Provides a rich Gradio Chatbot interface for the Smart Admin Assistant.
Includes feedback mechanisms and pre-defined queries.
"""

import json
from datetime import datetime
from pathlib import Path
import gradio as gr
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag_chain import process_query
from app.config import FEEDBACK_LOG_PATH

# Premium Gradio Theme settings
theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="indigo",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Cairo"), "sans-serif"]
).set(
    body_background_fill="*neutral_50",
    block_background_fill="*neutral_100",
    block_border_width="1px",
    block_border_color="*neutral_200",
    button_primary_background_fill="*primary_500",
    button_primary_background_fill_hover="*primary_600",
)

def chat_interface(message, history):
    """
    Adapter for Gradio ChatInterface.
    Takes the user message and history, returns the assistant's response.
    """
    # Note: We rely on the internal ConversationBufferWindowMemory inside rag_chain 
    # for the LLM context, but Gradio also keeps its own history for display.
    response = process_query(message)
    return response

def handle_feedback(data: gr.LikeData):
    """
    Logs user feedback (like/dislike) to feedback.jsonl.
    """
    try:
        FEEDBACK_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "bot_response": data.value,
            "liked": data.liked,
            "index": data.index
        }
        
        with open(FEEDBACK_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_entry, ensure_ascii=False) + "\n")
            
        print(f"Feedback logged: {'Liked' if data.liked else 'Disliked'}")
    except Exception as e:
        print(f"Error logging feedback: {e}")

# Build the Gradio App
with gr.Blocks(title="المساعد الذكي للريادة") as demo:
    gr.HTML(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #1e3a8a; font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
                المساعد الذكي الإداري 🤖
            </h1>
            <h3 style="color: #475569; font-weight: normal;">
                كلية الحاسبات والذكاء الاصطناعي - جامعة الريادة
            </h3>
        </div>
        """
    )
    
    chatbot = gr.Chatbot()
    
    # Removed chatbot.like() due to version compatibility
    
    chat_input = gr.ChatInterface(
        fn=chat_interface,
        chatbot=chatbot,
        textbox=gr.Textbox(placeholder="اكتب سؤالك هنا... (مثال: ما هي رسالة الكلية؟)", container=False, scale=7),
        examples=[
            "ما هي رسالة كلية الحاسبات؟",
            "كيف يمكنني دفع المصاريف؟",
            "أريد استخراج شهادة التخرج، مع من أتواصل؟",
            "من هو عميد الكلية؟"
        ]
    )

if __name__ == "__main__":
    print("Starting Gradio Web Server with public link...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True, inbrowser=True)
