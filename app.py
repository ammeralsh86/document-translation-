import os
import json
import streamlit as st
from document_handler import DocumentHandler
from supabase import create_client, Client

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

# ----------------------------------------------------
# إعداد اتصال Supabase (تأكد من وضع رابط ومفتاح مشروعك الصحيح هنا أو في Streamlit Secrets)
# ----------------------------------------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://nqyimxfwrwyajycslxdw.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_quqjRBtb6bF5Yl2gYqQ1Rg_R1bUu0-A")

@st.cache_resource
def init_supabase() -> Client:
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_supabase()

# دوال التعامل مع قاعدة بيانات Supabase
def get_user_from_db(email):
    if not supabase:
        return None
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
    except Exception as e:
        print(f"خطأ في البحث عن المستخدم: {e}")
    return None

def save_user_to_db(user_data):
    if not supabase:
        return False
    try:
        supabase.table("users").insert(user_data).execute()
        return True
    except Exception as e:
        print(f"خطأ في حفظ المستخدم: {e}")
        return False

def get_all_users():
    if not supabase:
        return []
    try:
        response = supabase.table("users").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        return []

# حالة الجلسة
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
            else:
                user = get_user_from_db(login_email)
                if user and user.get("password") == login_pass:
                    st.session_state.logged_in = True
                    user["is_admin"] = False
                    st.session_state.current_user = user
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("خطأ في البريد الإلكتروني/رقم الهاتف أو كلمة المرور، أو لم يتم ربط Supabase بشكل صحيح.")

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
                        existing_user = get_user_from_db(email)
                        if existing_user:
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
                        user_data = st.session_state.temp_user_data
                        success = save_user_to_db(user_data)
                        
                        if success:
                            st.session_state.logged_in = True
                            user_data["is_admin"] = False
                            st.session_state.current_user = user_data
                            st.session_state.register_step = "form"
                            st.success("✨ تم التحقق وحفظ الحساب في قاعدة البيانات بنجاح!")
                            st.rerun()
                        else:
                            st.error("حدث خطأ أثناء حفظ البيانات في Supabase. تأكد من صحة المفاتيح وجدول 'users'.")
                    else:
                        st.error("رمز التحقق غير صحيح. (رمز التجربة: 1234).")
            with col2:
                if st.button("إلغاء والعودة"):
                    st.session_state.register_step = "form"
                    st.rerun()

    # توقيع المطور أسفل الشاشة
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
        st.write("إدارة المستخدمين المسجلين عبر قاعدة بيانات Supabase السحابية:")
        
        users_list = get_all_users()
        st.subheader(f"📊 عدد المستخدمين المسجلين: {len(users_list)}")
        if users_list:
            for udata in users_list:
                st.write(f"- **الاسم:** {udata.get('full_name')} | **البريد/الهاتف:** {udata.get('email')} | **التخصص:** {udata.get('specialization')}")
        else:
            st.info("لا يوجد مستخدمون مسجلون في قاعدة البيانات حتى الآن أو أن المفاتيح بحاجة للمراجعة.")
            
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
