import sys
import os
import calendar
from datetime import datetime

import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QPushButton,
    QLabel, QWidget, QMessageBox, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QComboBox, QStatusBar
)
from PySide6.QtCore import Qt

# 自动安装 openpyxl
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

        self.file_path = None
        self.results = None
        self.month_days = None
        self.actual_records = None
        self.year = None
        self.month = None

        # 季节时段规则定义（来自代码1）
        self.time_rules = {
            "春秋季": {
                "peak": [10, 11, 17, 18, 19, 20, 21, 22],
                "flat": [8, 9, 12, 13, 14, 15, 16],
                "off_peak": [0, 1, 2, 3, 4, 5, 6, 7, 23]
            },
            "夏季": {
                "peak": [11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22],
                "flat": [7, 8, 9, 10, 19, 23],
                "off_peak": [0, 1, 2, 3, 4, 5, 6]
            },
            "冬季": {
                "peak": [10, 11, 16, 17, 18, 19, 20, 21, 22],
                "flat": [8, 9, 12, 13, 14, 15, 23],
                "off_peak": [0, 1, 2, 3, 4, 5, 6, 7]
            }
        }

        self.peak_hours = []
        self.flat_hours = []
        self.off_peak_hours = []

        main_widget = QWidget()
        layout = QVBoxLayout()

        # UI 布局（来自代码1）
        self.file_label = QLabel("未选择文件")
        self.file_label.setAlignment(Qt.AlignCenter)

        self.select_file_btn = QPushButton("选择Excel文件")
        self.select_file_btn.clicked.connect(self.select_file)

        self.season_combo = QComboBox()
        self.season_combo.addItems(["自动判断", "春秋季", "夏季", "冬季"])
        self.season_combo.currentIndexChanged.connect(self.update_time_slots)

        self.analyze_btn = QPushButton("分析用电数据")
        self.analyze_btn.clicked.connect(self.analyze_power_data)
        self.analyze_btn.setEnabled(False)

        self.export_btn = QPushButton("导出到Excel")
        self.export_btn.clicked.connect(self.export_to_excel)
        self.export_btn.setEnabled(False)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("季节选择："))
        top_layout.addWidget(self.season_combo)
        top_layout.addWidget(self.analyze_btn)
        top_layout.addWidget(self.export_btn)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(
            ["设备名称", "总用电量(kWh)", "峰时段用电量(kWh)", "平时段用电量(kWh)", "谷时段用电量(kWh)"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.file_label)
        layout.addWidget(self.select_file_btn)
        layout.addLayout(top_layout)
        layout.addWidget(self.result_table)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # 初始化时段规则
        self.update_time_slots()

    def update_time_slots(self):
        """根据下拉菜单选择更新时段规则"""
        selected = self.season_combo.currentText()
        if selected == "自动判断":
            # 自动判断时，不设置时段，在分析时再判断
            self.peak_hours = []
            self.flat_hours = []
            self.off_peak_hours = []
            self.status_bar.showMessage("已选择自动判断季节", 3000)
            return

        rule = self.time_rules.get(selected)
        if rule:
            self.peak_hours = rule['peak']
            self.flat_hours = rule['flat']
            self.off_peak_hours = rule['off_peak']
            self.status_bar.showMessage(f"已应用季节规则：{selected}", 3000)

    def select_file(self):
        """选择Excel文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.analyze_btn.setEnabled(True)
            self.export_btn.setEnabled(False)
            self.result_table.setRowCount(0)
            self.status_bar.showMessage("已加载文件，准备分析", 3000)

    def analyze_power_data(self):
        """分析用电数据"""
        if not self.file_path:
            QMessageBox.warning(self, "警告", "请先选择Excel文件")
            return

        try:
            # 自动查找包含“时间”列的Sheet（来自代码2）
            xlsx = pd.ExcelFile(self.file_path, engine='openpyxl')
            df = None
            for sheet in xlsx.sheet_names:
                df_candidate = pd.read_excel(xlsx, sheet_name=sheet)
                df_candidate.columns = df_candidate.columns.str.strip()  # 清理列名
                if "时间" in df_candidate.columns:
                    df = df_candidate
                    break
            else:
                raise ValueError("未找到包含“时间”列的工作表")

            # 数据预处理
            df['时间'] = pd.to_datetime(df['时间'])

            # 检查数据完整性
            first_date = df['时间'].iloc[0]
            self.year = first_date.year
            self.month = first_date.month
            self.month_days = calendar.monthrange(self.year, self.month)[1]
            expected_records = self.month_days * 24 + 1
            if len(df) != expected_records:
                QMessageBox.warning(
                    self,
                    "数据不完整",
                    f"应有 {expected_records} 条记录（含月末），实际 {len(df)} 条")

            # 去除最后一条记录，以便进行diff计算
            df = df.iloc[:-1].copy()
            self.actual_records = len(df)

            # 自动判断季节（来自代码1）
            if self.season_combo.currentText() == "自动判断":
                if self.month in [3, 4, 5, 6, 10, 11]:
                    season = "春秋季"
                elif self.month in [7, 8, 9]:
                    season = "夏季"
                else:
                    season = "冬季"
                self.season_combo.setCurrentText(season)
                self.update_time_slots()
                self.status_bar.showMessage(f"自动判断为 {season}", 3000)

            df['小时'] = df['时间'].dt.hour

            # 识别设备列
            device_columns = [
                col for col in df.columns if col not in [
                    "序号", "时间", "stn", "小时"]]

            self.results = {}

            # 正确的计算逻辑（来自代码2）
            for device in device_columns:
                df[f'{device}_diff'] = df[device].diff().fillna(0)

                total_power = round(df[device].iloc[-1] - df[device].iloc[0], 2)
                peak = round(df[df['小时'].isin(self.peak_hours)][f'{device}_diff'].sum(), 2)
                flat = round(df[df['小时'].isin(self.flat_hours)][f'{device}_diff'].sum(), 2)
                valley = round(df[df['小时'].isin(self.off_peak_hours)][f'{device}_diff'].sum(), 2)

                self.results[device] = {
                    'total': total_power,
                    'peak': peak,
                    'flat': flat,
                    'off_peak': valley
                }

            self.display_results()
            self.export_btn.setEnabled(True)
            self.status_bar.showMessage("分析完成", 3000)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析失败:\n{str(e)}")
            self.status_bar.showMessage("分析失败", 3000)
            print(e)

    def display_results(self):
        """在表格中显示结果"""
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
        """导出结果到Excel文件"""
        if not self.results:
            QMessageBox.warning(self, "警告", "没有可导出的数据")
            return

        try:
            # 建议文件名（来自代码2）
            suggested_name = f"用电统计_{self.year}{self.month:02d}_{datetime.now().strftime('%H%M%S')}.xlsx"
            save_path, _ = QFileDialog.getSaveFileName(
                self, "保存结果", suggested_name, "Excel文件 (*.xlsx)")

            if not save_path:
                return
            if not save_path.endswith(".xlsx"):
                save_path += ".xlsx"

            export_data = []
            for device, data in self.results.items():
                export_data.append({
                    '设备名称': device,
                    '总用电量(kWh)': data['total'],
                    '峰时段用电量(kWh)': data['peak'],
                    '平时段用电量(kWh)': data['flat'],
                    '谷时段用电量(kWh)': data['off_peak'],
                })

            df_export = pd.DataFrame(export_data)

            # 汇总信息
            summary = {
                '设备名称': '汇总信息',
                '总用电量(kWh)': df_export['总用电量(kWh)'].sum(),
                '峰时段用电量(kWh)': df_export['峰时段用电量(kWh)'].sum(),
                '平时段用电量(kWh)': df_export['平时段用电量(kWh)'].sum(),
                '谷时段用电量(kWh)': df_export['谷时段用电量(kWh)'].sum(),
            }

            df_export = pd.concat(
                [df_export, pd.DataFrame([summary])], ignore_index=True)

            with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
                df_export.to_excel(writer, index=False, sheet_name="分时用电统计")
                info_df = pd.DataFrame({
                    '信息': ['数据月份', '应记录天数', '应记录小时数', '实际记录小时数'],
                    '值': [f"{self.year}-{self.month:02d}", self.month_days, self.month_days * 24, self.actual_records]
                })
                info_df.to_excel(writer, index=False, sheet_name="数据信息")

            QMessageBox.information(self, "成功", f"结果已导出：\n{save_path}")
            self.status_bar.showMessage("导出完成", 3000)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")
            self.status_bar.showMessage("导出失败", 3000)
            print(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PowerAnalysisTool()
    window.show()
    sys.exit(app.exec())