'''
这个程序用于读取pdf文件内的文字和表格
'''


import pdfplumber


with pdfplumber.open("C:\\Users\\hank\\Downloads\\123.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        txt_file = open("C:\\Users\\hank\\Downloads\\123.txt",mode='a',encoding='utf-8')
        txt_file.write(text)