import sys
import zipfile
import xml.etree.ElementTree as ET

if len(sys.argv) < 3:
    print('Usage: python docx_to_md.py input.docx output.md')
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with zipfile.ZipFile(input_file) as z:
    xml_content = z.read('word/document.xml')

tree = ET.fromstring(xml_content)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

paragraphs = []
for para in tree.findall('.//w:p', ns):
    texts = []
    for node in para.findall('.//w:t', ns):
        if node.text:
            texts.append(node.text)
    paragraph_text = ''.join(texts).strip()
    if paragraph_text:
        paragraphs.append(paragraph_text)

text = '\n\n'.join(paragraphs)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(text)
