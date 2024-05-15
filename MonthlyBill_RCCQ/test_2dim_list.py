from openpyxl import load_workbook
from openpyxl.styles.borders import Border, Side
wb = load_workbook("202308_CHW.xlsx")
summary_sheet = wb['Summary']
l_side = Side(style='thin', color="000000")
r_side = Side(style='hair', color="000000")
t_side = Side(style='hair', color="000000")
b_side = Side(style='hair', color="000000")
border = Border(
    right=r_side,
    left=l_side,
    top=t_side,
    bottom=b_side
)
#
for row in summary_sheet['E8:E11', 'E13:E14', 'E16:E46']:
    for cell in row:
        cell.border = border
# li = ['E8:E11', 'E13:E14', 'E16:E46']
