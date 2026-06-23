import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from fpdf import FPDF

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="مشروع تحفيظ القرآن الكريم للأخوات", page_icon="🕌", layout="wide")

# 1. رابط الـ Web App الخاص بك (تأكدي من وضع رابطك الحقيقي هنا)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbynIig3HruBqX7j-DpbTqBcq9cIPJUONIf8eVg__xDQV1dHUTxN_QNl08hUw5OSlb4/exec" 

# بيانات المالك الافتراضية (يمكنك تغييرها)
OWNER_USERNAME = "admin"
OWNER_PASSWORD = "owner_password_123"

# --- 3. تصميم الهيدر (مستوحى من الطابع الإسلامي لموقع طريق إلى الله) ---
st.markdown("""
    <style>
    .islamic-header {
        background: linear-gradient(135deg, #0f5132, #1aa260);
        color: white;
        padding: 30px;
        text-align: center;
        border-radius: 10px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .islamic-header h1 { color: #f1c40f; font-family: 'Cairo', sans-serif; font-size: 2.5rem; margin-bottom: 5px; }
    .islamic-header p { font-size: 1.2rem; font-style: italic; opacity: 0.9; }
    </style>
    <div class="islamic-header">
        <h1>🕌 مشروع تحفيظ القرآن الكريم للأخوات 🕌</h1>
        <p>"خَيرُكُم مَن تَعَلَّمَ القُرآنَ وَعَلَّمَهُ" - كتابة ورصد إلكتروني مبارك</p>
    </div>
""", unsafe_allow_html=True)

# --- دالات الاتصال بقاعدة البيانات ---
def fetch_data(sheet_name):
    """جلب البيانات من جوجل شيت"""
    try:
        response = requests.get(f"{WEB_APP_URL}?sheet={sheet_name}")
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)
    except:
        pass
    return pd.DataFrame()

def insert_data(sheet_name, row_data):
    """إرسال بيانات جديدة إلى جوجل شيت"""
    try:
        requests.post(WEB_APP_URL, json={"sheet": sheet_name, "row": row_data})
        return True
    except:
        return False

# --- 4. دالة إنشاء تقارير PDF بسيطة ---
def generate_simple_pdf(title, content_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # نغير العنوان ليكون بالإنجليزية فقط لتجنب الخطأ
    pdf.cell(200, 10, txt="Report Document", ln=True, align='C') 
    pdf.ln(10)
    
    # نستخدم خطاً بسيطاً للبيانات (يجب أن تكون المحتويات إنجليزية أو أرقام)
    for line in content_list:
        # هنا نتأكد أننا لا نمرر حروفاً عربية للمكتبة الافتراضية
        clean_line = str(line).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(200, 10, txt=clean_line, ln=True)
    return pdf.output(dest='S')

# --- نظام تسجيل الدخول وإدارة الجلسة ---
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
    st.session_state.user_id = None
    st.session_state.user_name = None

# --- صفحة الدخول الرئيسية ---
if st.session_state.user_role is None:
    st.subheader("🔑 تسجيل الدخول للمنظومة")
    role = st.selectbox("اختر نوع الحساب:", ["طالبة", "معلمة", "المالك (الإدارة العامة)"])
    
    username = st.text_input("اسم المستخدم / كود الحساب:")
    password = st.text_input("كلمة المرور:", type="password")
    
    if st.button("دخول", use_container_width=True):
        if role == "المالك (الإدارة العامة)":
            if username == OWNER_USERNAME and password == OWNER_PASSWORD:
                st.session_state.user_role = "owner"
                st.rerun()
            else:
                st.error("بيانات المالك غير صحيحة!")
                
                elif role == "معلم&" or role == "معلمة":
            df_teachers = fetch_data("Teachers")
            # التعديل هنا: البحث في عمود 'Name' بدلاً من 'Teacher_ID'
            if not df_teachers.empty and username in df_teachers['Name'].values:
                user_row = df_teachers[df_teachers['Name'] == username].iloc[0]
                if str(user_row['Password']) == password:
                    st.session_state.user_role = "teacher"
                    st.session_state.user_id = user_row['Teacher_ID'] # سنحتفظ بالكود داخلياً للربط
                    st.session_state.user_name = user_row['Name']
                    st.rerun()
            st.error("اسم المعلمة أو كلمة المرور خاطئة!")
            
               elif role == "طالبة":
            df_students = fetch_data("Students")
            # التعديل هنا: البحث في عمود 'Name' بدلاً من 'Student_ID'
            if not df_students.empty and username in df_students['Name'].values:
                user_row = df_students[df_students['Name'] == username].iloc[0]
                if str(user_row['Password']) == password:
                    st.session_state.user_role = "student"
                    st.session_state.user_id = user_row['Student_ID'] # سنحتفظ بالكود داخلياً للربط
                    st.session_state.user_name = user_row['Name']
                    st.rerun()
            st.error("اسم الطالبة أو كلمة المرور خاطئة!")

else:
    # زر تسجيل الخروج في شريط جانبي
    st.sidebar.write(f"مرحباً بكِ: **{st.session_state.user_name if st.session_state.user_name else 'المالك'}**")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.user_role = None
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.rerun()

    # ==================== 1. لوحة تحكم المالك ====================
    if st.session_state.user_role == "owner":
        st.title("🎛️ لوحة تحكم المالك")
        tab1, tab2, tab3 = st.tabs(["➕ إضافة معلمة جديدة", "📊 تقرير المعلمات المعينين", "📈 إحصائيات عامة"])
        
        with tab1:
            st.subheader("تسجيل معلمة جديدة في المشروع")
            t_id = st.text_input("كود المعلمة المقترح (مثال: T-101):")
            t_name = st.text_input("اسم المعلمة الكامل:")
            t_pass = st.text_input("تعيين كلمة مرور للمعلمة:", type="password")
            
            if st.button("حفظ وتثبيت المعلمة"):
                if t_id and t_name and t_pass:
                    if insert_data("Teachers", [t_id, t_name, t_pass]):
                        st.success(f"تم تسجيل المعلمة {t_name} بنجاح!")
                    else:
                        st.error("حدث خطأ أثناء الحفظ.")
                else:
                    st.warning("يرجى ملء جميع الحقول.")
                    
        with tab2:
            st.subheader("🗂️ كشف المعلمات الحاليين وتقاريرهن")
            df_t = fetch_data("Teachers")
            if not df_t.empty:
                st.dataframe(df_t, use_container_width=True)
                
                # تقرير المعلمات PDF للمالك
                lines = [f"ID: {row['Teacher_ID']} | Name: {row['Name']}" for idx, row in df_t.iterrows()]
                pdf_data = generate_simple_pdf("Project Teachers Report", lines)
                st.download_button("تحميل تقرير المعلمات الشامل (PDF)", pdf_data, file_name="teachers_report.pdf", mime="application/pdf")
            else:
                st.info("لا توجد معلمات مسجلات بعد.")

    # ==================== 2. لوحة تحكم المعلمة ====================
    elif st.session_state.user_role == "teacher":
        st.title(f"👩‍🏫 لوحة تحكم المعلمة / {st.session_state.user_name}")
        tab1, tab2, tab3 = st.tabs(["📝 رصد يوميات الطالبات", "➕ تسجيل طالبة جديدة لملفك", "📊 تقرير طالباتي"])
        
        df_all_students = fetch_data("Students")
        # فلترة الطالبات التابعات لهذه المعلمة فقط
        if not df_all_students.empty and 'Teacher_ID' in df_all_students.columns:
            my_students = df_all_students[df_all_students['Teacher_ID'].astype(str) == str(st.session_state.user_id)]
        else:
            my_students = pd.DataFrame()
            
        with tab1:
            st.subheader("رصد الحضور والدرجات اليومي")
            if not my_students.empty:
                student_choice = st.selectbox("اختر اسم الطالبة:", my_students['Name'].values)
                student_id = my_students[my_students['Name'] == student_choice]['Student_ID'].values[0]
                
                status = st.radio("حالة الحضور:", ["حاضرة", "غائبة", "غائبة بعذر"])
                grade = st.slider("درجة التسميع والحفظ (من 10):", 0, 10, 10)
                notes = st.text_area("الواجب اليومي أو ملاحظات الحفظ:")
                
                if st.button("حفظ الرصد اليومي"):
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    if insert_data("Attendance_Grades", [str(student_id), date_str, status, grade, notes]):
                        st.success("تم الحفظ في سجل الطالبة بنجاح!")
            else:
                st.info("لم تقومي بتسجيل أي طالبة تحت إشرافك بعد. اذهبي للتبويب الثاني.")
                
        with tab2:
            st.subheader("إضافة طالبة جديدة حصرًا في حلقتكِ")
            s_id = st.text_input("كود الطالبة (مثال: STU-501):")
            s_name = st.text_input("اسم الطالبة:")
            s_pass = st.text_input("كلمة مرور الطالبة:", type="password")
            s_halaqa = st.text_input("اسم الحلقة القرأنية:")
            
            if st.button("تسجيل الطالبة برقمكِ"):
                if s_id and s_name and s_pass:
                    if insert_data("Students", [s_id, s_name, s_pass, s_halaqa, str(st.session_state.user_id)]):
                        st.success(f"تم تسجيل الطالبة {s_name} وربطها بملفك بنجاح!")
                    else:
                        st.error("خطأ في الاتصال.")
                        
        with tab3:
            st.subheader("📊 استخراج تقارير طالبات الحلقة")
            if not my_students.empty:
                st.dataframe(my_students[['Student_ID', 'Name', 'Halaqa']], use_container_width=True)
                
                # تقرير مجمع للمعلمة عن طالباتها PDF
                lines = [f"Student ID: {row['Student_ID']} | Name: {row['Name']} | Halaqa: {row['Halaqa']}" for idx, row in my_students.iterrows()]
                pdf_data = generate_simple_pdf(f"Halaqa Students Report - Teacher {st.session_state.user_name}", lines)
                st.download_button("تحميل كشف طالباتك المجمع (PDF)", pdf_data, file_name="my_students_report.pdf", mime="application/pdf")
            else:
                st.info("لا توجد بيانات لاستخراج التقرير.")

    # ==================== 3. لوحة تحكم الطالبة ====================
    elif st.session_state.user_role == "student":
        st.title(f"🌸 الملف القرآني للطالبة: {st.session_state.user_name}")
        
        df_grades = fetch_data("Attendance_Grades")
        if not df_grades.empty:
            my_records = df_grades[df_grades['Student_ID'].astype(str) == str(st.session_state.user_id)]
            if not my_records.empty:
                st.subheader("📜 درجاتك وملاحظات المعلمة الأخيرة:")
                st.dataframe(my_records[['Date', 'Status', 'Grade', 'Notes']], use_container_width=True)
                
                # تقرير PDF شخصي للطالبة لتقديمه لولي أمرها
                lines = [f"Date: {row['Date']} | Status: {row['Status']} | Grade: {row['Grade']}/10 | Notes: {row['Notes']}" for idx, row in my_records.iterrows()]
                pdf_data = generate_simple_pdf(f"Student Progress Report - {st.session_state.user_name}", lines)
                st.download_button("تحميل تقرير درجاتي وحضوري (PDF)", pdf_data, file_name="my_progress_report.pdf", mime="application/pdf")
            else:
                st.info("أهلاً بكِ في المنظومة! لم تقم المعلمة برصد أي درجات لكِ حتى الآن.")
        else:
            st.info("لا توجد سجلات حالية.")
