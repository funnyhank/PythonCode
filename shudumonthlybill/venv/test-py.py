import sys
import os

BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
tmplate_path = os.path.join(BASE_DIR,"Shudu Metering Report temp.xlsx")
report_path = os.path.join(BASE_DIR,'sudu08.xlsx')
print(report_path)
