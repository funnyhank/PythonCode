import pdfplumber as pb
import os
# os.listdir()方法获取文件夹名字，返回数组


def getAllFiles(targetDir):
    listFiles = os.listdir(targetDir)
    return listFiles


files = getAllFiles(r"C:\Users\funny\Desktop\pdf")
# 写入list到txt文件中
with open(r"test.txt", 'w+', encoding='utf-8')as f:
    # 列表生成式
    f.writelines(["'" + str(i) + "',\n" for i in files])
print(files[0])
for j in range(0, len(files)):
    file_handle = open("C:/Users/funny/Desktop/pdf/" +
                       str(files[j]) + '.txt', mode='w', encoding='utf-8')
    # 读取PDF文档
    pdf = pb.open("C:/Users/funny/Desktop/pdf/" + str(files[j]))
    # 绝对路径也可以这么写，下同
    # 获取页数
    a = len(pdf.pages)
    print("当前页：", a)
    i = 0
    for i in range(0, a):
        first_page = pdf.pages[i]
        print("本页：", first_page.page_number)
        print("-----------------------------------------")
        # # 导出当前页文本
        text = first_page.extract_text()
        # print(text)
        file_handle.write(text)
    print('已完成篇数：', j + 1, files[j])
