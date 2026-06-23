import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from fpdf import FPDF
import os

# إعدادات الصفحة
st.set_page_config(page_title="مشروع تحفيظ القرآن الكريم", page_icon="🕌", layout="wide")

# الرابط (ضعي رابطك هنا)
WEB_APP_URL = "https://script.google.com/macros/s/XXXXX/exec"

# الدالة لقراءة البيانات
def fetch_data(sheet_name):
    try:
        response = requests.get(f"{WEB_APP_URL}?sheet={sheet_name}")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except:
        pass
    return pd.DataFrame()

# دالة إنشاء الـ PDF مع دعم العربية
def generate_pdf(title, content_list):
    pdf = FPDF()
    pdf.add_page()
    
    # تحميل الخط العربي (تأكدي من وجود Arial.ttf في المجلد)
    if os.path.exists("Arial.ttf"):
        pdf.add_font("Arial", "", "Arial.ttf", uni=True)
        pdf.set_font("Arial", size=16)
    else:
        pdf.set_font("Arial", size=12) # خط بديل إذا لم يجد الملف
        
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    
    for line in content_list:
        # تحويل النص ليدعم الـ PDF
        pdf.cell(200, 10, txt=line, ln=True, align='R')
    return pdf.output(dest='S')

# --- الهيدر ---
st.markdown("""
    <style>
    .islamic-header { background: linear-gradient(135deg, #0f5132, #1aa260); color: white; padding: 20px; text-align: center; border-radius: 10px; }
    </style>
    <div class="islamic-header"><h1>🕌 مشروع تحفيظ القرآن الكريم للأخوات 🕌</h1></div>
""", unsafe_allow_html=True)

# --- نظام الدخول ---
if 'user_role' not in st.session_state: st.session_state.user_role = None

if st.session_state.user_role is None:
    st.subheader("🔑 تسجيل الدخول")
    role = st.selectbox("نوع الحساب:", ["طالبة", "معلمة", "المالك"])
    username = st.text_input("الاسم:")
    password = st.text_input("كلمة المرور:", type="password")
    
    if st.button("دخول"):
        # منطق الدخول (تم التعديل للبحث بالاسم)
        if role == "المالك":
            if username == "admin" and password == "123":
                st.session_state.user_role = "owner"
                st.session_state.user_name = "الإدارة العامة"  # <--- هذا السطر كان ناقصاً
                st.rerun()
        else:
            sheet = "Teachers" if role == "معلمة" else "Students"
            df = fetch_data(sheet)
            if not df.empty and username in df['Name'].values:
                user = df[df['Name'] == username].iloc[0]
                if str(user['Password']) == password:
                    st.session_state.user_role = role
                    st.session_state.user_name = username
                    st.session_state.user_id = user[f"{'Teacher' if role=='معلمة' else 'Student'}_ID"]
                    st.rerun()
            st.error("بيانات الدخول غير صحيحة")

    # إضافة خاصية نسيت كلمة المرور
    if st.button("نسيت كلمة المرور؟"):
        st.info("💡 يرجى التواصل مع الإدارة أو المعلمة لاستعادة كلمة المرور.")

else:
    # ... (باقي الكود الخاص بلوحات التحكم كما هو سابقاً) ...
    # تذكري أن تضعي هنا المنطق الخاص بلوحة تحكم المالك والمعلمة والطالبة
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.user_role = None
        st.rerun()
    # بدلاً من st.write(f"مرحباً {st.session_state.user_name}")
    # استخدمي هذا السطر الآمن:
    user_display_name = st.session_state.get('user_name', 'زائر')
    st.write(f"مرحباً {user_display_name}")
