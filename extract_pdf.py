import pdfplumber
from pathlib import Path

pdf_path = Path("data/documents/19e4137121dac9c925c1.pdf")
output_path = Path("data/documents/auchan_pdf_extract.txt")

text_content = ""

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        page_text = page.extract_text() or f"[Страница {i+1} - нет текста]"
        text_content += f"=== СТРАНИЦА {i+1} ===\n"
        text_content += page_text
        text_content += "\n\n"

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(text_content)

print(f"Extracted {len(text_content)} characters to {output_path}")
print("First 500 chars:")
print(text_content[:500])
