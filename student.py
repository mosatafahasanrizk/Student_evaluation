import streamlit as st
import pandas as pd
import requests
import hashlib
import re
from datetime import datetime

# ==========================================
# 1. إعدادات الاتصال والتشفير
# ==========================================

# ضع الرابط الذي نسخته من Apps Script هنا
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbynIig3HruBqX7j-DpbTqBcq9cIPJUONIf8eVg__xDQV1dHUTxN_QNl08hUw5OSlb4/exec"

def get_data(sheet_name):
    """جلب البيانات من جوجل شيت"""
    try:
        response = requests.get(f"{WEB_APP_URL}?sheet={sheet_name}")
        data = response.json()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except:
        return pd.DataFrame()

def insert_data(sheet_name, row_data):
    """إرسال صف جديد إلى جوجل شيت"""
    try:
        response = requests.post(WEB_APP_URL, json={"sheet": sheet_name, "row": row_data}, allow_redirects=True)
        if response.status_code != 200:
            st.error(f"حدث خطأ في الاتصال بجوجل: {response.status_code}")
        else:
            # التحقق مما إذا كان جوجل قد أرسل رسالة خطأ داخلية
            if "error" in response.text.lower():
                st.error(f"جوجل رفض البيانات، تفاصيل الخطأ: {response.text}")
    except Exception as e:
        st.error(f"تعذر الاتصال بالرابط: {e}")
def hash_password(password: str) -> str:
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def generate_next_student_code(students_df) -> str:
    """توليد كود طالبة تلقائي متسلسل"""
    prefix = "STU-"
    default_start = 1001
    if students_df.empty or 'student_code' not in students_df.columns:
        return f"{prefix}{default_start}"
    
    codes = students_df['student_code'].astype(str).tolist()
    numeric_parts = [int(re.search(r'\d+', code).group()) for code in codes if re.search(r'\d+', code)]
    
    if not numeric_parts:
        return f"{prefix}{default_start}"
    return f"{prefix}{max(numeric_parts) + 1}"

# ==========================================
# 2. إعدادات الصفحة وتهيئة الجلسة
# ==========================================
st.set_page_config(page_title="منظومة المتابعة", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None 
    st.session_state.user_name = None

st.markdown("""
    <style>div.block-container { direction: rtl; text-align: right; }</style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. نظام تسجيل الدخول
# ==========================================
def login_page():
    st.title("🔑 بوابة الدخول للمنظومة")
    role = st.radio("اختر نوع الحساب:", ["طالبة", "معلمة / مشرفة"], horizontal=True)
    
    if role == "معلمة / مشرفة":
        password = st.text_input("كلمة مرور الإدارة:", type="password")
        if st.button("دخول"):
            if password == "12345":  # كلمة مرور الإدارة
                st.session_state.logged_in = True
                st.session_state.user_role = "teacher"
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة")
    else:
        student_code = st.text_input("كود الطالبة:")
        student_pass = st.text_input("كلمة المرور:", type="password")
        if st.button("دخول"):
            students_df = get_data("Students")
            if not students_df.empty:
                hashed_input = hash_password(student_pass)
                # البحث عن الطالبة
                user = students_df[(students_df['student_code'] == student_code) & (students_df['password'] == hashed_input)]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "student"
                    st.session_state.user_code = student_code
                    st.session_state.user_name = user.iloc[0]['student_name']
                    st.rerun()
                else:
                    st.error("الكود أو كلمة المرور غير صحيحة!")

# ==========================================
# 4. لوحة تحكم المعلمة
# ==========================================
def teacher_dashboard():
    st.title("🗂️ لوحة تحكم المعلمة")
    tab1, tab2, tab3 = st.tabs(["📝 رصد اليوميات", "📊 متابعة الأداء", "➕ تسجيل طالبة جديدة"])
    
    students_df = get_data("Students")
    
    with tab1:
        st.header("تسجيل الحضور والتقييم")
        if not students_df.empty:
            student_list = students_df['student_name'].tolist()
            selected_name = st.selectbox("اختر اسم الطالبة:", student_list)
            selected_code = students_df[students_df['student_name'] == selected_name].iloc[0]['student_code']
            
            date_input = datetime.now().strftime('%Y-%m-%d')
            col1, col2, col3 = st.columns(3)
            with col1: status = st.selectbox("الحالة:", ["حاضر", "غائب", "استئذان"])
            with col2: mem_grade = st.number_input("درجة التسميع:", 0.0, 10.0, 10.0, 0.5)
            with col3: rev_grade = st.number_input("درجة المراجعة:", 0.0, 10.0, 10.0, 0.5)
                
            mistakes = st.text_area("الأخطاء والملحوظات:")
            notes = st.text_input("الواجب القادم:")
            
            if st.button("حفظ الرصد"):
                row = [date_input, selected_code, status, mem_grade, rev_grade, mistakes, notes]
                insert_data("Attendance_Grades", row)
                st.success("تم الحفظ بنجاح!")
        else:
            st.warning("لا يوجد طالبات مسجلات بعد.")

    with tab2:
        st.header("سجل الدرجات العام")
        records_df = get_data("Attendance_Grades")
        if not records_df.empty:
            st.dataframe(records_df, use_container_width=True)

    with tab3:
        st.header("إضافة طالبة جديدة للمنظومة")
        new_code = generate_next_student_code(students_df)
        st.info(f"كود الطالبة الجديد سيكون: **{new_code}**")
        
        new_name = st.text_input("اسم الطالبة الثلاثي:")
        new_group = st.text_input("اسم الحلقة:")
        raw_password = st.text_input("كلمة مرور للطالبة:", type="password")
        
        if st.button("تسجيل الطالبة"):
            if new_name and raw_password:
                secured_password = hash_password(raw_password)
                insert_data("Students", [new_code, secured_password, new_name, new_group])
                st.success(f"تم تسجيل {new_name} بنجاح!")

# ==========================================
# 5. لوحة تحكم الطالبة
# ==========================================
def student_dashboard():
    st.title(f"🌸 مرحباً بكِ: {st.session_state.user_name}")
    records_df = get_data("Attendance_Grades")
    
    if not records_df.empty:
        my_records = records_df[records_df['student_code'] == st.session_state.user_code]
        if not my_records.empty:
            st.subheader("📋 سجل حصصكِ المفصل:")
            view_df = my_records.drop(columns=['student_code'])
            st.dataframe(view_df, use_container_width=True)
        else:
            st.info("لم يتم رصد أي درجات لكِ حتى الآن.")

# ==========================================
# توجيه الصفحات
# ==========================================
if st.session_state.logged_in:
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()
    if st.session_state.user_role == "teacher":
        teacher_dashboard()
    else:
        student_dashboard()
else:
    login_page()