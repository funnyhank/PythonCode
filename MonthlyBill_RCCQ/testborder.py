import os
from win32com.client import DispatchEx
excel_path = r"C:\Users\hank\PycharmProjects\pythonProject\MonthlyBill_RCCQ\202310_CHW.xlsx"                      #这里是Excel文件的路径
pdf_path = r"C:\Users\hank\PycharmProjects\pythonProject\MonthlyBill_RCCQ\202310_CHW.pdf"                          #这里是输出PDF的保存路径

xlApp = DispatchEx("Excel.Application")
xlApp.Visible = False
xlApp.DisplayAlerts = 0
books = xlApp.Workbooks.Open(excel_path,False)
books.ExportAsFixedFormat(0, pdf_path)
books.Close(False)
xlApp.Quit()
