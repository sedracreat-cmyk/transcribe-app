!pip install gradio openai-whisper python-docx -q

import gradio as gr
import whisper
import warnings
import re
import os
from docx import Document
warnings.filterwarnings("ignore")

print("جاري تحميل النموذج والخدمات...")
model = whisper.load_model("base")

def smart_summarize(text):
    """استخراج أهم النقاط والأفكار الأساسية من النص"""
    sentences = re.split(r'[.!؟\n]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    if not sentences:
        return text
    if len(sentences) <= 3:
        return "- " + "\n- ".join(sentences)
        
    key_points = [sentences[0]]
    if len(sentences) > 5:
        key_points.append(sentences[len(sentences) // 2])
    if len(sentences) > 2:
        key_points.append(sentences[-1])
        
    summary_formatted = "• النقطة الرئيسية الأولى:\n  " + key_points[0] + "\n\n"
    if len(key_points) > 2:
        summary_formatted += "• النقاط الجوهرية الوسطى:\n  " + key_points[1] + "\n\n"
        summary_formatted += "• الخلاصة النهائية:\n  " + key_points[2]
    else:
        summary_formatted += "• الخلاصة النهائية:\n  " + key_points[1]
        
    return summary_formatted

def process_and_export(file_path, choice):
    if file_path is None:
        return "الرجاء رفع ملف صوتي أو فيديو أولاً!", None, None
    
    # تفريغ الصوت والكشف عن اللغة
    result = model.transcribe(file_path, beam_size=5, without_timestamps=True)
    lang = result['language'].upper()
    full_text = " ".join(result["text"].split())
    
    if choice == "تفريغ حرفي كامل":
        output_text = f"🌐 اللغة المكتشفة: {lang}\n\n📜 النص المفرغ كاملاً ودقيقاً:\n{full_text}"
        export_title = "تفريغ_صوتي"
    else:
        summary = smart_summarize(full_text)
        output_text = f"🌐 اللغة المكتشفة: {lang}\n\n📝 الملخص الذكي للنقاط الأساسية:\n{summary}"
        export_title = "ملخص_صوتي"

    # إنشاء ملف TXT
    txt_filename = f"{export_title}.txt"
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(output_text)

    # إنشاء ملف Word (DOCX)
    docx_filename = f"{export_title}.docx"
    doc = Document()
    doc.add_heading("برنامج التفريغ والتلخيص الذكي", level=1)
    doc.add_paragraph(output_text)
    doc.save(docx_filename)

    return output_text, txt_filename, docx_filename

# بناء الواجهة التفاعلية المحسنة
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎙️ منصة التفريغ والتلخيص الذكي للوسائط")
    gr.Markdown("قم برفع ملف الصوت/الفيديو للحصول على تفريغ دقيق أو ملخص مركز، مع إمكانية تحميل النتائج مباشرة.")
    
    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="اختر أو سجل الصوت/الفيديو")
    
    with gr.Row():
        choice_radio = gr.Radio(
            ["تفريغ حرفي كامل", "ملخص سريع ومباشر"], 
            label="نوع الخدمة المطلوبة", 
            value="تفريغ حرفي كامل"
        )
    
    submit_btn = gr.Button("🚀 بدء المعالجة", variant="primary")
    
    # تم إزالة الخاصية الغير مدعومة ليعمل الكود بسلاسة تامة
    output_box = gr.Textbox(label="النتيجة الشاملة", lines=12)
    
    gr.Markdown("### 📥 حفظ وتصدير النتيجة:")
    with gr.Row():
        file_txt = gr.File(label="تحميل كمستند نصي (TXT)")
        file_docx = gr.File(label="تحميل كمستند وورد (Word)")
    
    submit_btn.click(
        fn=process_and_export, 
        inputs=[audio_input, choice_radio], 
        outputs=[output_box, file_txt, file_docx]
    )

demo.launch(share=True)
