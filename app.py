import os
import json
import streamlit as st
from document_handler import DocumentHandler

# إعداد الصفحة وتصميمها
st.set_page_config(
    page_title="مكتبة المعهد الصحي - نظام الترجمة الذكي",
    page_icon="🏥",
    layout="centered"
)

# دمج ملف الثيمات والتصميم الجرافيكي (style.css)
css_file = "style.css"
if os.path.exists(css_file):
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

USERS_DB_FILE = "users_db.json"

def load_users():
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "register_step" not in st.session_state:
    st.session_state.register_step = "form"
if "temp_user_data" not in st.session_state:
    st.session_state.temp_user_data = {}

# ----------------------------------------------------
# 1. واجهة تسجيل الدخول أو إنشاء حساب (الجرافيكس الثلاثي الأبعاد)
# ----------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🏥 مكتبة المعهد الصحي</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #b2dfdb;'>نظام ترجمة المستندات الذكي والمتخصص</h4>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد"])
    
    with tab1:
        st.write("أهلاً بك مجدداً. يرجى إدخال بيانات حسابك للمتابعة.")
        login_email = st.text_input("البريد الإلكتروني أو رقم الهاتف", key="login_email")
        login_pass = st.text_input("كلمة المرور", type="password", key="login_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("تسجيل الدخول"):
            users = load_users()
            # حساب الآدمن الافتراضي
            if login_email == "admin@health.org" and login_pass == "admin123":
                st.session_state.logged_in = True
                st.session_state.current_user = {
                    "full_name": "مشرف النظام (الآدمن)",
                    "email": "admin@health.org",
                    "specialization": "إدارة النظام",
                    "is_admin": True
                }
                st.success("تم تسجيل الدخول بصفتك (آدمن) بنجاح!")
                st.rerun()
            elif login_email in users and users[login_email]["password"] == login_pass:
                st.session_state.logged_in = True
                users[login_email]["is_admin"] = False
                st.session_state.current_user = users[login_email]
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("خطأ في البريد الإلكتروني/رقم الهاتف أو كلمة المرور.")

    with tab2:
        if st.session_state.register_step == "form":
            st.write("أنشئ حساباً جديداً للوصول إلى كافة الخدمات والقواميس الطبية.")
            
            with st.form("register_form"):
                full_name = st.text_input("الاسم كاملاً")
                email = st.text_input("البريد الإلكتروني أو رقم الهاتف")
                phone = st.text_input("رقم الهاتف (للتأكيد)")
                password = st.text_input("كلمة المرور", type="password")
                confirm_password = st.text_input("كلمة المرور (تأكيد)", type="password")
                
                specialization = st.selectbox(
                    "التخصص",
                    options=["طبي", "تكنولوجي", "زراعي", "عصبي / بيولوجي", "أخرى"]
                )
                
                verify_method = st.selectbox(
                    "طريقة الحصول على رمز التأكيد",
                    options=["البريد", "واتس أب", "اس ام اس"]
                )
                
                privacy_policy = st.checkbox("الموافقة على بنود الخصوصية وشروط الاستخدام")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_btn = st.form_submit_button("تسجيل")
                
                if submit_btn:
                    if not full_name or not email or not phone or not password:
                        st.warning("يرجى ملء جميع الحقول المطلوبة.")
                    elif password != confirm_password:
                        st.error("كلمات المرور غير متطابقة.")
                    elif not privacy_policy:
                        st.error("يجب الموافقة على بنود الخصوصية لإتمام التسجيل.")
                    else:
                        users = load_users()
                        if email in users:
                            st.error("هذا الحساب مسجل مسبقاً.")
                        else:
                            st.session_state.temp_user_data = {
                                "full_name": full_name,
                                "email": email,
                                "phone": phone,
                                "password": password,
                                "specialization": specialization,
                                "verify_method": verify_method
                            }
                            st.session_state.register_step = "verify"
                            st.rerun()
                            
        elif st.session_state.register_step == "verify":
            st.info(f"📤 تم إرسال رمز التحقق عبر ({st.session_state.temp_user_data.get('verify_method')}) إلى رقمك أو بريدك المسجل.")
            st.write("رمز التحقق للتجربة هو: **1234**")
            
            entered_code = st.text_input("أدخل رمز التحقق المكون من 4 أرقام", max_chars=4)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("تأكيد وإتمام التسجيل"):
                    if entered_code == "1234":
                        users = load_users()
                        user_data = st.session_state.temp_user_data
                        email = user_data["email"]
                        users[email] = user_data
                        save_users(users)
                        
                        st.session_state.logged_in = True
                        user_data["is_admin"] = False
                        st.session_state.current_user = user_data
                        st.session_state.register_step = "form"
                        st.success("✨ تم التحقق وتسجيل الحساب بنجاح!")
                        st.rerun()
                    else:
                        st.error("رمز التحقق غير صحيح. (رمز التجربة: 1234).")
            with col2:
                if st.button("إلغاء والعودة"):
                    st.session_state.register_step = "form"
                    st.rerun()

    # توقيع المطور أسفل الشاشة كما طلبت
    st.markdown("<div class='developer-footer'>تطوير م/ أبومعاوية الشبيبي</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. الواجهة الرئيسية أو لوحة تحكم الآدمن (بعد تسجيل الدخول)
# ----------------------------------------------------
else:
    user = st.session_state.current_user
    st.sidebar.success(f"مرحباً: {user.get('full_name')}")
    st.sidebar.write(f"التخصص: {user.get('specialization')}")
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    if user.get("is_admin", False):
        st.title("🛡️ لوحة تحكم الآدمن - مكتبة المعهد الصحي")
        st.write("إدارة المستخدمين والنظام محلياً:")
        
        users = load_users()
        st.subheader(f"📊 عدد المستخدمين المسجلين: {len(users)}")
        if users:
            for email, udata in users.items():
                st.write(f"- **الاسم:** {udata.get('full_name')} | **البريد/الهاتف:** {email} | **التخصص:** {udata.get('specialization')}")
        else:
            st.info("لا يوجد مستخدمون مسجلون حتى الآن.")
            
        st.markdown("---")
        st.markdown("<div class='developer-footer'>تطوير م/ أبومعاوية الشبيبي</div>", unsafe_allow_html=True)
        
    else:
        st.title("🏥 مكتبة المعهد الصحي")
        st.subheader("نظام ترجمة المستندات الذكي (بدون إنترنت)")
        st.write("قم برفع مستندك الصحي أو العلمي (Word, PowerPoint, PDF) لترجمته بدقة عالية.")

        st.sidebar.header("⚙️ إعدادات الترجمة")
        direction = st.sidebar.selectbox(
            "اتجاه الترجمة",
            options=["en-ar", "ar-en"],
            format_func=lambda x: "من الإنجليزية إلى العربية" if x == "en-ar" else "من العربية إلى الإنجليزية"
        )

        target_lang = "العربية" if direction == "en-ar" else "الإنجليزية"

        uploaded_file = st.file_uploader(
            "اختر ملف المستند المراد ترجمته", 
            type=["docx", "pptx", "pdf"]
        )

        if uploaded_file is not None:
            input_filename = uploaded_file.name
            with open(input_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            st.success(f"تم رفع الملف بنجاح: {input_filename}")
            
            base_name, ext = os.path.splitext(input_filename)
            output_filename = f"{base_name}_translated{ext}"
            if ext == ".pdf":
                output_filename = f"{base_name}_translated.txt"

            if st.button("🚀 بدء الترجمة الآن"):
                with st.spinner("جاري ترجمة المستند بواسطة قواميس مكتبة المعهد الصحي..."):
                    try:
                        handler = DocumentHandler(glossary_path="glossary.json", direction=direction)
                        handler.translate_document(
                            input_path=input_filename,
                            output_path=output_filename,
                            target_language=target_lang
                        )
                        
                        st.success("✨ تمت عملية الترجمة بنجاح!")
                        
                        with open(output_filename, "rb") as f:
                            file_bytes = f.read()
                            
                        st.download_button(
                            label="📥 تحميل المستند المترجم",
                            data=file_bytes,
                            file_name=output_filename,
                            mime="application/octet-stream"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء عملية الترجمة: {e}")

        st.markdown("<div class='developer-footer'>تطوير م/ أبومعاوية الشبيبي</div>", unsafe_allow_html=True)
