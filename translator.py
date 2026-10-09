import os
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class DocumentTranslator:
    def __init__(self, glossary_path="glossary.json", direction="en-ar"):
        """
        تهيئة المترجم المحلي (Offline Translator)
        direction: إما 'en-ar' (من الإنجليزية للعربية) أو 'ar-en' (من العربية للإنجليزية)
        """
        self.glossary = self._load_glossary(glossary_path)
        
        # اختيار النموذج المحلي المناسب حسب اتجاه الترجمة
        if direction == "en-ar":
            self.model_name = "Helsinki-NLP/opus-mt-en-ar"
        else:
            self.model_name = "Helsinki-NLP/opus-mt-ar-en"
            
        print(f"[i] جاري تحميل نموذج الترجمة المحلي ({self.model_name})... قد يستغرق ذلك وقتاً في المرة الأولى.")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            print("[✓] تم تحميل النموذج المحلي بنجاح وجاهز للعمل بدون إنترنت.")
        except Exception as e:
            print(f"[!] خطأ في تحميل النموذج المحلي: {e}")

    def _load_glossary(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"تحذير: لم يتم قراءة ملف المسرد: {e}")
        return {}

    def translate_text(self, text, target_language="العربية"):
        """
        ترجمة النص محلياً مع تطبيق مسرد المصطلحات يدوياً
        """
        if not text or not text.strip():
            return text

        # 1. تطبيق مسرد المصطلحات المخصص أولاً على النص
        processed_text = text
        for src_term, tgt_term in self.glossary.items():
            if target_language == "العربية":
                processed_text = processed_text.replace(src_term, tgt_term)
            else:
                processed_text = processed_text.replace(tgt_term, src_term)

        try:
            # 2. الترجمة عبر النموذج المحلي
            inputs = self.tokenizer(processed_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            translated_tokens = self.model.generate(**inputs, max_length=512, num_beams=4, early_stopping=True)
            translated_text = self.tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
            
            return translated_text.strip()
            
        except Exception as e:
            print(f"حدث خطأ أثناء الترجمة المحلية: {e}")
            return text
