import sys, os
sys.stdout.reconfigure(encoding='utf-8')
import fitz
doc = fitz.open(r'C:\Users\Rishab Nayak\Downloads\fcb406e8-4663-4537-ac54-f0116371c20f.pdf')
text = ''
for page in doc:
    text += page.get_text()
print(text)
