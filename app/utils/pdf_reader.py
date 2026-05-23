from pypdf import PdfReader
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    if not pdf_path or not os.path.exists(pdf_path):
        return ""
        
    if os.path.isdir(pdf_path):
        pdf_files = [os.path.join(pdf_path, f) for f in os.listdir(pdf_path) if f.lower().endswith('.pdf')]
        return extract_text_from_pdfs(pdf_files)
        
    try:
        reader = PdfReader(pdf_path)
        return "".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        return f"[Error reading PDF {os.path.basename(pdf_path)}: {str(e)}]"

def extract_text_from_pdfs(pdf_paths: list[str]) -> str:
    combined_text = ""
    for path in pdf_paths:
        if os.path.exists(path) and os.path.isfile(path):
            try:
                reader = PdfReader(path)
                combined_text += f"\n--- Source: {os.path.basename(path)} ---\n"
                combined_text += "".join([page.extract_text() for page in reader.pages])
            except Exception as e:
                combined_text += f"\n--- Source: {os.path.basename(path)} (Error: {str(e)}) ---\n"
    return combined_text

