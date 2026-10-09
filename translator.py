import os
import json
from openai import OpenAI

class DocumentTranslator:
    def __init__(self, glossary_path="glossary.json"):
        """
        تهيئة المترجم وتحميل مفتاح الـ API ومسرد المصطلحات
        """
        # استدعاء مفتاح الـ API من متغيرات البيئة لضمان الأمان
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("مفتاح OPENAI_API_KEY غير موجود في متغيرات البيئة.")
            
        self.client = OpenAI(api_key=api_key)
        self.glossary = self._load_glossary(glossary_path)

    def _load_glossary(self, path):
        """
        تحميل مسرد المصطلحات من ملف الـ JSON إن وجد
        """
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"تحذير: لم يتم قراءة ملف المسرد بشكل صحيح: {e}")
        return {}

    def translate_text(self, text, target_language="العربية"):
        """
        ترجمة النص مع الحفاظ على الهوية والمصطلحات المحددة
        """
        if not text or not text.strip():
            return text

        # بناء نظام التوجيه (System Prompt) للذكاء الاصطناعي
        system_prompt = (
            f"أنت مترجم محترف خبير في توثيق وترجمة المستندات بدقة عالية.\n"
            f"مهمتك هي ترجمة النص التالي إلى {target_language} مع الحفاظ التام على الأسلوب، الهوية، "
            f"والتنسيقات البرمجية أو علامات الهيكل (مثل Markdown أو الأوساخ إن وجدت) دون تعديلها أو حذفها.\n"
        )

        # إضافة مسرد المصطلحات إلى التوجيه إن لم يكن فارغاً
        if self.glossary:
            glossary_str = json.dumps(self.glossary, ensure_ascii=False)
            system_prompt += (
                f"\nالرجاء الالتزام التام بترجمة المصطلحات التالية حسب المقابل المرفق بدقة:\n"
                f"{glossary_str}"
            )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # أو النموذج المفضل لديك
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"ترجم النص التالي بدقة:\n\n{text}"}
                ],
                temperature=0.2  # درجة حرارة منخفضة لضمان الدقة والالتزام بالمصطلحات
            )
            
            translated_text = response.choices[0].message.content
            return translated_text.strip()
            
        except Exception as e:
            print(f"حدث خطأ أثناء الاتصال بخدمة الترجمة: {e}")
            return text  # في حال الخطأ يتم إرجاع النص الأصلي لكي لا يتعطل المستند

# مثال للاختبار المباشر
if __name__ == "__main__":
    # للاختبار فقط عند الحاجة
    pass
