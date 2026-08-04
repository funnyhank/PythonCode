#use getallfolderpdf better

from pypdf import PdfReader
content = []
reader = PdfReader(
    r"C:\Users\funny\Desktop\pdf\S8. SP OT Infra Physical Security and Facilities Management Standard.pdf")
print(len(reader.pages))
# page = reader.pages[0]
# print(page.extract_text())
for i in range(len(reader.pages)):
    content.append(reader.pages[i].extract_text())
    i += 1
with open(r"C:\Users\funny\Desktop\pdf\S8. SP OT Infra Physical Security and Facilities Management Standard.txt", 'w', encoding='utf-8') as f:
    n = f.write(str(content))
# text_file = open('output.txt', 'w', encoding='utf-8')
# content = page.extract_text()
# n = text_file.write(str(content))
f.close()
