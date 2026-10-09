import os
import json
from openai import OpenAI

class DocumentTranslator:
    def __init__(self, glossary_path="glossary.json"):
        """
        تهيئة المترجم وتحميل مفتاح الـ API ومسرد المصطلحات الشامل
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("مفتاح OPENAI_API_KEY غير موجود في متغيرات البيئة.")
            
        self.client = OpenAI(api_key=api_key)
        self.glossary = self._load_glossary(glossary_path)

    def _load_glossary(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"تحذير: لم يتم قراءة ملف المسرد بشكل صحيح: {e}")
        return {}

    def translate_text(self, text, target_language="العربية"):
        """
        ترجمة النص مع الالتزام التام بالمصطلحات الطبية، الزراعية، التكنولوجية، وما ينتهي بـ 'لوجيا'
        """
        if not text or not text.strip():
            return text

        # بناء نظام توجيه ذكي ومتخصص يغطي كافة العلوم
        system_prompt = (
            f"أنت خبير لغوي ومترجم أكاديمي متخصص في الترجمة العلمية والتقنية والطبية والزراعية بين اللغتين العربية والانجليزية.\n"
            f"قواعد الترجمة الصارمة:\n"
            f"1. حافظ على دقة المصطلحات العلمية (الطبية، الزراعية، والتكنولوجية) بدقة مطلقة وفقاً للمعايير الأكاديمية العالمية.\n"
            f"2. بالنسبة للمصطلحات التي تنتهي بـ (-ology / لوجيا) وما يشابهها (مثل Cardiology, Biotechnology, Geology)، قم بترجمتها إلى المقابل العلمي المعتمد في اللغة العربية (سواء باللفظ المعرب أو الترجمة المباشرة الدقيقة مثل: علم الأعصاب، الجيولوجيا، التقنية الحيوية).\n"
            f"3. حافظ على التنسيق والهوية الأصلية للمستند تماماً.\n"
        )

        # دمج مسرد المصطلحات الخاص بالمستخدم
        if self.glossary:
            glossary_str = json.dumps(self.glossary, ensure_ascii=False)
            system_prompt += (
                f"\nالرجاء الالتزام التام بترجمة هذه المصطلحات الخاصة بالمستند بناءً على هذا المسرد:\n"
                f"{glossary_str}"
            )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"ترجم النص التالي إلى {target_language} بدقة متناهية:\n\n{text}"}
                ],
                temperature=0.1  # درجة حرارة منخفضة جداً لضمان الدقة العلمية والالتزام بالمصطلحات
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"حدث خطأ أثناء الاتصال بخدمة الترجمة: {e}")
            return text
