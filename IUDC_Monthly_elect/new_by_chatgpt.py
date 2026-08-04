import sys
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog,
                               QVBoxLayout, QPushButton, QLabel,
                               QWidget, QMessageBox, QTableWidget,
                               QTableWidgetItem, QHBoxLayout, QStatusBar)
from PySide6.QtCore import Qt
import os
from datetime import datetime

# 自动安装依赖
try:
    import openpyxl
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl


class PowerAnalysisTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("四川省分时电价用电量统计工具")
        self.setGeometry(100, 100, 1000, 800)

        # 主窗口布局
        main_widget = QWidget()
        layout = QVBoxLayout()

        # 文件选择
        self.file_label = QLabel("未选择文件")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.select_file_btn = QPushButton("选择Excel文件")
        self.select_file_btn.clicked.connect(self.select_file)

        # 操作按钮
        self.analyze_btn = QPushButton("分析用电数据")
        self.analyze_btn.clicked.connect(self.analyze_power_data)
        self.analyze_btn.setEnabled(False)

        self.export_btn = QPushButton("导出到Excel")
        self.export_btn.clicked.connect(self.export_to_excel)
        self.export_btn.setEnabled(False)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.analyze_btn)
        btn_layout.addWidget(self.export_btn)

        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(
            ["设备名称", "总用电量(kWh)", "峰时段用电量(kWh)", "平时段用电量(kWh)", "谷时段用电量(kWh)"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 设置布局
        layout.addWidget(self.file_label)
        layout.addWidget(self.select_file_btn)
        layout.addLayout(btn_layout)
        layout.addWidget(self.result_table)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # 初始化变量
        self.file_path = None
        self.results = None
        self.month_days = None
        self.year = None
        self.month = None

        # 时段定义
        self.peak_hours = list(range(10, 21))
        self.flat_hours = [7, 8, 9, 21, 22, 23]
        self.off_peak_hours = list(range(0, 7))

    def select_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )

        if file_path:
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.analyze_btn.setEnabled(True)
            self.export_btn.setEnabled(False)
            self.result_table.setRowCount(0)
            self.status_bar.showMessage("文件已加载，准备分析", 3000)

    def analyze_power_data(self):
        if not self.file_path:
            QMessageBox.warning(self, "警告", "请先选择Excel文件")
            return

        try:
            # 自动查找包含“时间”列的Sheet
            xlsx = pd.ExcelFile(self.file_path, engine='openpyxl')
            for sheet in xlsx.sheet_names:
                df_candidate = pd.read_excel(xlsx, sheet_name=sheet)
                df_candidate.columns = df_candidate.columns.str.strip()
                if "时间" in df_candidate.columns:
                    df = df_candidate
                    break
            else:
                raise ValueError("未找到包含“时间”列的工作表")

            # 获取月份信息
            df['时间'] = pd.to_datetime(df['时间'])
            first_date = df['时间'].iloc[0]
            self.year = first_date.year
            self.month = first_date.month

            import calendar
            self.month_days = calendar.monthrange(self.year, self.month)[1]
            expected_records = self.month_days * 24

            if len(df) - 1 != expected_records:
                QMessageBox.warning(
                    self, "警告", f"数据记录不完整！应为{expected_records}条，实际为{
                        len(df) - 1}条")

            # 去除最后1小时
            df = df.iloc[:-1]

            # 提取设备列
            device_columns = [
                col for col in df.columns if col not in [
                    "序号", "时间", "stn"]]

            # 小时列
            df['小时'] = df['时间'].dt.hour

            self.actual_records = len(df)

            self.results = {}

            for device in device_columns:
                df[f'{device}_diff'] = df[device].diff().fillna(0)
                peak = round(df[df['小时'].isin(self.peak_hours)][f'{
                    device}_diff'].sum(),2)
                flat = round(df[df['小时'].isin(self.flat_hours)][f'{
                    device}_diff'].sum(),2)
                valley = round(df[df['小时'].isin(self.off_peak_hours)][f'{
                    device}_diff'].sum(),2)
                total = round(
                    df[device].iloc[-1] - df[device].iloc[0], 2)
                self.results[device] = {
                    'total': total,
                    'peak': peak,
                    'flat': flat,
                    'off_peak': valley}

            self.display_results()
            self.export_btn.setEnabled(True)
            self.status_bar.showMessage("分析完成", 3000)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析数据时出错:\n{str(e)}")
            self.status_bar.showMessage("分析失败", 3000)
            print(e)

    def display_results(self):
        if not self.results:
            return

        self.result_table.setRowCount(len(self.results))

        for row, (device, data) in enumerate(self.results.items()):
            self.result_table.setItem(row, 0, QTableWidgetItem(device))
            self.result_table.setItem(
                row, 1, QTableWidgetItem(f"{data['total']:.2f}"))
            self.result_table.setItem(
                row, 2, QTableWidgetItem(f"{data['peak']:.2f}"))
            self.result_table.setItem(
                row, 3, QTableWidgetItem(f"{data['flat']:.2f}"))
            self.result_table.setItem(
                row, 4, QTableWidgetItem(f"{data['off_peak']:.2f}"))

        self.result_table.resizeColumnsToContents()

    def export_to_excel(self):
        if not self.results:
            QMessageBox.warning(self, "警告", "没有可导出的数据")
            return

        try:
            file_dialog = QFileDialog()
            suggested_name = f"用电统计_{
                self.year}{
                self.month:02d}_{
                datetime.now().strftime('%H%M%S')}.xlsx"
            save_path, _ = file_dialog.getSaveFileName(
                self, "保存结果", suggested_name, "Excel文件 (*.xlsx)"
            )

            if save_path:
                if not save_path.endswith('.xlsx'):
                    save_path += '.xlsx'

                export_data = []
                for device, data in self.results.items():
                    export_data.append({
                        '设备名称': device,
                        '总用电量(kWh)': data['total'],
                        '峰时段用电量(kWh)': data['peak'],
                        '平时段用电量(kWh)': data['flat'],
                        '谷时段用电量(kWh)': data['off_peak'],
                        # '峰时段占比(%)': data['peak'] / data['total'] * 100 if data['total'] else 0,
                        # '平时段占比(%)': data['flat'] / data['total'] * 100 if data['total'] else 0,
                        # '谷时段占比(%)': data['off_peak'] / data['total'] * 100 if data['total'] else 0,
                    })

                df_export = pd.DataFrame(export_data)

                summary = {
                    '设备名称': '汇总信息',
                    '总用电量(kWh)': df_export['总用电量(kWh)'].sum(),
                    '峰时段用电量(kWh)': df_export['峰时段用电量(kWh)'].sum(),
                    '平时段用电量(kWh)': df_export['平时段用电量(kWh)'].sum(),
                    '谷时段用电量(kWh)': df_export['谷时段用电量(kWh)'].sum(),
                    # '峰时段占比(%)': df_export['峰时段用电量(kWh)'].sum() / df_export['总用电量(kWh)'].sum() * 100 if df_export['总用电量(kWh)'].sum() > 0 else 0,
                    # '平时段占比(%)': df_export['平时段用电量(kWh)'].sum() / df_export['总用电量(kWh)'].sum() * 100 if df_export['总用电量(kWh)'].sum() > 0 else 0,
                    # '谷时段占比(%)': df_export['谷时段用电量(kWh)'].sum() / df_export['总用电量(kWh)'].sum() * 100 if df_export['总用电量(kWh)'].sum() > 0 else 0,
                }

                df_export = pd.concat(
                    [df_export, pd.DataFrame([summary])], ignore_index=True)

                with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                    df_export.to_excel(
                        writer, index=False, sheet_name='分时用电统计')
                    info_df = pd.DataFrame({
                        '信息': ['数据月份', '应记录天数', '应记录小时数', '实际记录小时数'],
                        '值': [f"{self.year}-{self.month:02d}", self.month_days, self.month_days * 24, self.actual_records]
                    })
                    info_df.to_excel(writer, index=False, sheet_name='数据信息')

                QMessageBox.information(self, "成功", f"导出成功:\n{save_path}")
                self.status_bar.showMessage("导出完成", 3000)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出数据时出错:\n{str(e)}")
            self.status_bar.showMessage("导出失败", 3000)
            print(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PowerAnalysisTool()
    window.show()
    sys.exit(app.exec())
