import os
import argparse
from document_handler import DocumentHandler

def main():
    print("=" * 60)
    print("   نظام ترجمة المستندات الذكي (محلي بالكامل - بدون إنترنت)   ")
    print("=" * 60)

    parser = argparse.ArgumentParser(description="ترجمة المستندات مع الحفاظ على التنسيق والمصطلحات محلياً.")
    parser.add_argument("--file", type=str, help="مسار المستند المراد ترجمته (.docx, .pptx, .pdf)", default="")
    parser.add_argument("--output", type=str, help="مسار حفظ الملف المترجم", default="translated_output.docx")
    parser.add_argument("--lang", type=str, help="اللغة المستهدفة للترجمة", default="العربية")
    parser.add_argument("--dir", type=str, help="اتجاه الترجمة (en-ar أو ar-en)", default="en-ar")
    
    args = parser.parse_args()

    try:
        if args.file:
            if not os.path.exists(args.file):
                print(f"[!] خطأ: الملف غير موجود في المسار: {args.file}")
                return
                
            print(f"\n[i] جاري بدء معالجة الملف باستخدام الاتجاه: {args.dir}...")
            handler = DocumentHandler(glossary_path="glossary.json", direction=args.dir)
            
            handler.translate_document(
                input_path=args.file, 
                output_path=args.output, 
                target_language=args.lang
            )
            return

        print("\n[!] لم يتم تحديد ملف للترجمة.")
        print("طريقة الاستخدام عبر سطر الأوامر:")
        print("  python main.py --file \"document.docx\" --output \"output.docx\" --dir \"en-ar\"")

    except Exception as e:
        print(f"\n[!] حدث خطأ غير متوقع: {e}")

if __name__ == "__main__":
    main()
