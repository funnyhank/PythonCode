import pandas as pd
import os

pd.options.display.max_seq_items = None


class ReadExcel2Df:
    def __init__(self, filepath, sheetname):
        self.path = filepath
        self.sheet = sheetname

    def read_excel(self):

        # folder_path = r"C:\Users\funny\Desktop\RCCQ_OA"
        folder_path = self.path
        file_list = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

        for file in file_list:
            file_path = os.path.join(folder_path, file)
            df_excel = pd.read_excel(file_path, sheet_name=self.sheet)
            excel_column_list = df_excel.columns.tolist()
        # print(df.head())
        df_unpivot = pd.melt(df_excel,
                             id_vars='time',
                             value_vars=excel_column_list,
                             var_name='tag',
                             value_name='value')
        print(df_unpivot.tail())
        return df_unpivot


excelpath = r"C:\Users\funny\Desktop\Production report"
sheetsname = r'PlantData'
x = ReadExcel2Df(excelpath, sheetsname)
x.read_excel()
print(x.read_excel().info)