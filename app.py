import os
import streamlit as st
from document_handler import DocumentHandler

# إعداد الصفحة وتصميمها
st.set_page_config(
    page_title="نظام ترجمة المستندات الذكي",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 نظام ترجمة المستندات الذكي (بدون إنترنت)")
st.write("قم برفع مستندك (Word, PowerPoint, PDF) لترجمته بدقة عالية مع الحفاظ على التنسيق والمصطلحات العلمية والتقنية.")

# شريط جانبي للإعدادات
st.sidebar.header("⚙️ إعدادات الترجمة")
direction = st.sidebar.selectbox(
    "اتجاه الترجمة",
    options=["en-ar", "ar-en"],
    format_func=lambda x: "من الإنجليزية إلى العربية" if x == "en-ar" else "من العربية إلى الإنجليزية"
)

target_lang = "العربية" if direction == "en-ar" else "الإنجليزية"

st.sidebar.info("💡 التطبيق يستخدم نماذج ذكاء اصطناعي محلية وقواميس طبية وزراعية وتقنية مدمجة.")

# منطقة رفع الملفات
uploaded_file = st.file_uploader(
    "اختر ملف المستند المراد ترجمته", 
    type=["docx", "pptx", "pdf"]
)

if uploaded_file is not None:
    # حفظ الملف المرفوع مؤقتاً في المجلد المحلي
    input_filename = uploaded_file.name
    with open(input_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.success(f"تم رفع الملف بنجاح: {input_filename}")
    
    # تحديد اسم ملف الخروج
    base_name, ext = os.path.splitext(input_filename)
    output_filename = f"{base_name}_translated{ext}"
    if ext == ".pdf":
        output_filename = f"{base_name}_translated.txt" # ملفات PDF تستخرج كنصوص منظمة

    # زر بدء الترجمة
    if st.button("🚀 بدء الترجمة الآن"):
        with st.spinner("جاري تحميل النماذج ومعالجة المستند... قد يستغرق ذلك بضع دقائق في المرة الأولى."):
            try:
                # تهيئة معالج المستندات وتنفيذ الترجمة
                handler = DocumentHandler(glossary_path="glossary.json", direction=direction)
                handler.translate_document(
                    input_path=input_filename,
                    output_path=output_filename,
                    target_language=target_lang
                )
                
                st.success("✨ تمت عملية الترجمة بنجاح!")
                
                # توفير زر لتحميل الملف المترجم
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
