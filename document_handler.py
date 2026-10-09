import os
from docx import Document
from translator import DocumentTranslator

class WordDocumentHandler:
    def __init__(self, glossary_path="glossary.json"):
        """
        تهيئة معالج ملفات وورد مع محرك الترجمة
        """
        self.translator = DocumentTranslator(glossary_path=glossary_path)

    def translate_docx(self, input_path, output_path, target_language="العربية"):
        """
        قراءة مستند Word، ترجمة فقراته وجداوله مع الحفاظ على التنسيق والهوية، وحفظه في ملف جديد.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"الملف غير موجود في المسار المحدد: {input_path}")

        print(f"[i] جاري فتح المستند: {input_path}")
        doc = Document(input_path)

        # 1. ترجمة الفقرات العادية وعناوين المستند مع الحفاظ على الأنماط (Styles)
        print("[i] جاري ترجمة فقرات وعناوين المستند...")
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                # الاحتفاظ بالتنسيق الأصلي للفقرة قدر الإمكان
                original_text = paragraph.text
                translated_text = self.translator.translate_text(original_text, target_language=target_language)
                
                # تحديث النص مع محاولة الحفاظ على خصائص النمط إن أمكن
                # نقوم بتعديل النص داخل العناصر المكونة للفقرة لكي لا يضيع التنسيق الجزئي
                if len(paragraph.runs) > 0:
                    # للسيطرة البسيطة، نضع النص المترجم في العنصر الأول ونفرغ البقية لمنع التكرار
                    paragraph.runs[0].text = translated_text
                    for run in paragraph.runs[1:]:
                        run.text = ""
                else:
                    paragraph.text = translated_text

        # 2. ترجمة محتويات الجداول (Tables) مع الحفاظ على بنية الجدول والخلايا
        print("[i] جاري ترجمة جداول المستند...")
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        original_cell_text = cell.text
                        translated_cell_text = self.translator.translate_text(original_cell_text, target_language=target_language)
                        cell.text = translated_cell_text

        # 3. حفظ المستند المترجم الناتج
        doc.save(output_path)
        print(f"[✓] تم حفظ المستند المترجم بنجاح باسم: {output_path}")

# للاختبار أو الاستخدام المباشر
if __name__ == "__main__":
    import sys
    # يمكن تمرير الملف عبر الطرفية لاحقاً
    pass
