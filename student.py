import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from fpdf import FPDF
import os

# إعدادات الصفحة
st.set_page_config(page_title="مشروع تحفيظ القرآن الكريم", page_icon="🕌", layout="wide")

# ضعي رابط الـ Web App الخاص بك هنا (مهم جداً)
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
        
    # عنوان إنجليزي لتجنب مشاكل الترميز
    pdf.cell(200, 10, txt="Academic Report", ln=True, align='C')
    pdf.ln(10)
    for line in content_list:
        pdf.cell(200, 10, txt=str(line), ln=True, align='R')
    return pdf.output(dest='S')

# --- الهيدر ---
st.markdown("""<div style="background: #0f5132; color: white; padding: 20px; text-align: center; border-radius: 10px;">
<h1>🕌 مشروع تحفيظ القرآن الكريم للأخوات 🕌</h1></div>""", unsafe_allow_html=True)

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

# --- اللوحات التحكم بعد الدخول ---
else:
    st.sidebar.write(f"مرحباً: {st.session_state.get('user_name', 'زائر')}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.user_role = None
        st.rerun()

    # 1. لوحة المالك
    if st.session_state.user_role == "owner":
        st.title("🎛️ لوحة تحكم المالك")
        tab1, tab2 = st.tabs(["➕ إضافة معلمة", "📊 تقرير"])
        with tab1:
            name = st.text_input("اسم المعلمة")
            passwd = st.text_input("كلمة المرور", type="password")
            if st.button("حفظ"):
                if insert_data("Teachers", ["T"+str(datetime.now().microsecond), name, passwd]):
                    st.success("تم الإضافة!")
        with tab2:
            df = fetch_data("Teachers")
            st.dataframe(df)

    # 2. لوحة المعلمة
    elif st.session_state.user_role == "معلمة":
        st.title(f"👩‍🏫 لوحة المعلمة: {st.session_state.user_name}")
        df_all = fetch_data("Students")
        my_students = df_all[df_all['Teacher_ID'].astype(str) == str(st.session_state.user_id)] if not df_all.empty else pd.DataFrame()

        tab1, tab2 = st.tabs(["📝 رصد يوميات الطالبات", "📊 تقارير"])
        with tab1:
            if not my_students.empty:
                s_name = st.selectbox("اختر الطالبة:", my_students['Name'].values)
                s_id = my_students[my_students['Name'] == s_name]['Student_ID'].values[0]
                
                # الحقول الجديدة
                grade_hifz = st.text_input("درجة الحفظ:")
                grade_murajaah = st.text_input("درجة المراجعة:")
                report_hifz = st.text_area("تقرير الحفظ:")
                new_hifz = st.text_area("الحفظ الجديد:")
                
                if st.button("حفظ الرصد"):
                    data = [s_id, datetime.now().strftime("%Y-%m-%d"), grade_hifz, grade_murajaah, report_hifz, new_hifz]
                    if insert_data("Attendance_Grades", data): st.success("تم الحفظ!")
            else: st.info("لا توجد طالبات مسجلات.")

        with tab2:
            if st.button("تحميل تقرير طالباتي (PDF)"):
                lines = [f"Name: {row['Name']}" for _, row in my_students.iterrows()]
                pdf_data = generate_pdf("Report", lines)
                st.download_button("تنزيل الملف", pdf_data, "report.pdf", "application/pdf")

    # 3. لوحة الطالبة
    elif st.session_state.user_role == "طالبة":
        st.title(f"🌸 أهلاً بكِ يا {st.session_state.user_name}")
        df_grades = fetch_data("Attendance_Grades")
        if not df_grades.empty:
            my_grades = df_grades[df_grades['Student_ID'].astype(str) == str(st.session_state.user_id)]
            if not my_grades.empty:
                st.dataframe(my_grades[['Date', 'Hifz_Grade', 'Murajaah_Grade', 'Report', 'New_Hifz']])
                
                # تحضير الـ PDF للطالبة
                pdf_lines = [f"Student: {st.session_state.user_name}"]
                for _, row in my_grades.iterrows():
                    pdf_lines.append(f"Date: {row['Date']} | Hifz: {row['Hifz_Grade']} | Murajaah: {row['Murajaah_Grade']}")
                
                pdf_data = generate_pdf("My Report", pdf_lines)
                st.download_button("📥 تحميل تقريري (PDF)", pdf_data, "my_report.pdf", "application/pdf")
            else: st.info("لا توجد درجات مسجلة بعد.")
