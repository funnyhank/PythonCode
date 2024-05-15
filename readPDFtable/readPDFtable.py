#use getallfolderpdf better

from pypdf import PdfReader
content = []
reader = PdfReader(
    r"C:\Users\funny\Downloads\Documents\ebook\Object-Oriented-Python-Master-OOP-by-Building-Games-and-GUIs-Irv-Kalb-z-lib.org_.pdf")
print(len(reader.pages))
# page = reader.pages[0]
# print(page.extract_text())
for i in range(len(reader.pages)):
    content.append(reader.pages[i].extract_text())
    i += 1
with open('output.txt', 'w', encoding='utf-8') as f:
    n = f.write(str(content))
# text_file = open('output.txt', 'w', encoding='utf-8')
# content = page.extract_text()
# n = text_file.write(str(content))
f.close()
