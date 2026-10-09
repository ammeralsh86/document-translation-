import os
import argparse
from translator import DocumentTranslator

def main():
    """
    الدالة الرئيسية لتشغيل تطبيق الترجمة عبر سطر الأوامر أو كملف تشغيل رئيسي
    """
    print("=" * 50)
    print("   مرحباً بك في نظام ترجمة المستندات الذكي   ")
    print("=" * 50)

    # إعداد مُستقبل المتغيرات من سطر الأوامر (Command Line Arguments)
    parser = argparse.ArgumentParser(description="ترجمة المستندات مع الحفاظ على التنسيق والمصطلحات.")
    parser.add_argument("--file", type=str, help="مسار ملف النص أو المستند المراد ترجمته", default="")
    parser.add_argument("--text", type=str, help="نص مباشر للترجمة السريعة", default="")
    parser.add_argument("--lang", type=str, help="اللغة المستهدفة للترجمة", default="العربية")
    
    args = parser.parse_args()

    try:
        # تهيئة المترجم
        translator = DocumentTranslator(glossary_path="glossary.json")
        
        # إذا تم إدخال نص مباشر
        if args.text:
            print(f"\n[i] جاري ترجمة النص المدخل إلى ({args.lang})...\n")
            result = translator.translate_text(args.text, target_language=args.lang)
            print("--- النتيجة المترجمة ---")
            print(result)
            print("-" * 30)
            return

        # إذا تم إدخال مسار ملف
        if args.file:
            if not os.path.exists(args.file):
                print(f"[!] خطأ: الملف غير موجود في المسار: {args.file}")
                return
                
            print(f"\n[i] جاري قراءة الملف: {args.file}")
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
                
            print(f"[i] جاري ترجمة محتوى الملف إلى ({args.lang})...\n")
            translated_content = translator.translate_text(content, target_language=args.lang)
            
            # حفظ النتيجة في ملف جديد
            output_file = f"translated_{os.path.basename(args.file)}"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(translated_content)
                
            print(f"[✓] تم حفظ المستودع/الملف المترجم بنجاح في: {output_file}")
            return

        # في حال لم يتم إدخال أي خيار
        print("\n[!] لم يتم تحديد نص أو ملف للترجمة.")
        print("استخدم الوسائط التالية عند التشغيل:")
        print("  python main.py --text \"النص المراد ترجمته\"")
        print("  python main.py --file \"مسار_الملف.txt\"")

    except Exception as e:
        print(f"\n[!] حدث خطأ غير متوقع: {e}")

if __name__ == "__main__":
    main()

