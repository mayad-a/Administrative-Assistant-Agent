"""
Response Formatter & Fallback Logic
Generates smart fallback responses when confidence is low.
It can parse the contact directory to point the user to the right department.
"""

import re
from pathlib import Path

def detect_department_from_query(query: str) -> str:
    """
    Very simple keyword-based intent detection to guess which department
    might help the user if the exact answer is missing.
    """
    q = query.lower()
    
    if any(word in q for word in ["مصاريف", "دفع", "خزينة", "رسوم", "فلوس", "سداد", "fees", "pay", "money"]):
        return "إدارة الخزينة (الداخلي: 120، إيميل: finance@rst.edu.eg)"
        
    if any(word in q for word in ["تسجيل", "غياب", "جدول", "شؤون", "شئون", "قيد"]):
        return "شؤون الطلاب (الداخلي: 112، إيميل: affairs.f1@rst.edu.eg)"
        
    if any(word in q for word in ["خريج", "شهادة", "إخلاء", "تخرج"]):
        return "شؤون الخريجين (الداخلي: 115، إيميل: alumni@rst.edu.eg)"
        
    if any(word in q for word in ["نشاط", "رحلة", "رياضة", "عذر", "رعاية"]):
        return "رعاية الشباب (الداخلي: 130، إيميل: youth@rst.edu.eg)"
        
    # Default fallback
    return "مكتب الاستعلامات الرئيسي في الكلية"

def generate_fallback_response(query: str, lang: str = "ar") -> str:
    """
    Generates a polite fallback response containing the likely contact info.
    """
    contact_info = detect_department_from_query(query)
    
    if lang == "en":
        return (
            "I'm sorry, I don't have specific information about that in my current database. "
            f"However, you might find the answer by contacting: {contact_info}."
        )
    else:
        return (
            "عذراً، التفاصيل الدقيقة حول هذا الموضوع غير متوفرة لدي حالياً. "
            f"ولكن، يمكنك الاستفسار مباشرة عبر التواصل مع: {contact_info}."
        )
