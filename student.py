import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from fpdf import FPDF
import os

# إعدادات الصفحة
st.set_page_config(page_title="مشروع تحفيظ القرآن الكريم للأخوات", page_icon="🕌", layout="wide")

# ضعي رابط الـ Web App الخاص بك هنا
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbynIig3HruBqX7j-DpbTqBcq9cIPJUONIf8eVg__xDQV1dHUTxN_QNl08hUw5OSlb4/exec"

# دالات الاتصال
def fetch_data(sheet_name):
    try:
        response = requests.get(f"{WEB_APP_URL}?sheet={sheet_name}")
        return pd.DataFrame(response.json()) if response.status_code == 200 else pd.DataFrame()
    except: return pd.DataFrame()

def insert_data(sheet_name, row_data):
    try:
        requests.post(WEB_APP_URL, json={"sheet": sheet_name, "row": row_data})
        return True
    except: return False

# دالة إنشاء الـ PDF
def generate_pdf(title, content_list):
    pdf = FPDF()
    pdf.add_page()
    # تحميل الخط العربي
    if os.path.exists("Arial.ttf"):
        pdf.add_font("Arial", "", "Arial.ttf", uni=True)
        pdf.set_font("Arial", size=16)
    else:
        pdf.set_font("Arial", size=12)
        
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    for line in content_list:
        pdf.cell(200, 10, txt=str(line), ln=True, align='R')
    return pdf.output(dest='S')

# --- الهيدر ---
st.markdown("""
    <style>
    .islamic-header { background: linear-gradient(135deg, #0f5132, #1aa260); color: white; padding: 20px; text-align: center; border-radius: 10px; }
    </style>
    <div class="islamic-header"><h1>🕌 مشروع تحفيظ القرآن الكريم للأخوات 🕌</h1></div>
""", unsafe_allow_html=True)

# --- إدارة الجلسة ---
if 'user_role' not in st.session_state: st.session_state.user_role = None

# --- صفحة تسجيل الدخول ---
if st.session_state.user_role is None:
    st.subheader("🔑 تسجيل الدخول")
    role = st.selectbox("نوع الحساب:", ["طالبة", "معلمة", "المالك"])
    username = st.text_input("الاسم:")
    password = st.text_input("كلمة المرور:", type="password")
    
    if st.button("دخول"):
        if role == "المالك":
            if username == "admin" and password == "123":
                st.session_state.user_role = "owner"
                st.session_state.user_name = "الإدارة العامة"
                st.rerun()
            else: st.error("بيانات المالك غير صحيحة")
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
                else: st.error("كلمة المرور خاطئة")
            else: st.error("اسم المستخدم غير موجود")
            
    if st.button("نسيت كلمة المرور؟"):
        st.info("💡 يرجى التواصل مع الإدارة لاستعادة كلمة المرور.")

# --- لوحات التحكم (تظهر فقط بعد الدخول) ---
else:
    st.sidebar.write(f"مرحباً: {st.session_state.get('user_name', 'زائر')}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.user_role = None
        st.rerun()

    if st.session_state.user_role == "owner":
        st.title("🎛️ لوحة تحكم المالك")
        tab1, tab2 = st.tabs(["➕ إضافة معلمة", "📊 تقرير"])
        with tab1:
            name = st.text_input("اسم المعلمة")
            passwd = st.text_input("كلمة المرور", type="password")
            if st.button("حفظ"):
                if insert_data("Teachers", ["T"+str(datetime.now().microsecond), name, passwd]):
                    st.success("تم!")
        with tab2:
            st.write("تقرير المعلمات العام")
            df = fetch_data("Teachers")
            st.dataframe(df)

    elif st.session_state.user_role == "معلمة":
        st.title(f"👩‍🏫 أهلاً بكِ {st.session_state.user_name}")
        st.write("هنا تظهر أدوات المعلمة (رصد، تقارير..)")

    elif st.session_state.user_role == "طالبة":
        st.title(f"🌸 ملفكِ القرآني {st.session_state.user_name}")
        st.write("هنا تظهر درجاتكِ.")
