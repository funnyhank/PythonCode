#!/usr/bin/env python
# coding: utf-8

import os
import datetime
import sys
import logging
import logging.config
import pandas as pd
import calendar
from openpyxl import load_workbook
from openpyxl.styles import Border, Side
from openpyxl.styles.borders import BORDER_THIN

# 设置路径和日志记录
BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
config_path = os.path.join(BASE_DIR, "logging.conf")
if os.path.exists(config_path):
    logging.config.fileConfig(config_path)
    logger = logging.getLogger('applog')
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('applog')
    logger.warning("未找到 logging.conf 文件。正在使用基本日志配置。")


def load_template(file_name):
    """加载 Excel 模板工作簿。"""
    template_path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"未找到模板文件 '{file_name}'。")
    return load_workbook(template_path)


def find_top_left_cell(ws, cell_address):
    """检查单元格是否在合并区域内，并返回左上角单元格。"""
    for merged_range in ws.merged_cells.ranges:
        if cell_address in merged_range:
            return ws.cell(
                row=merged_range.min_row,
                column=merged_range.min_col)
    return ws[cell_address]


def set_report_dates(ws, now):
    """在 Summary 工作表中设置报告日期和月份。"""
    if now.month == 1:
        last_month = datetime.datetime(now.year - 1, 12, 1)
    else:
        last_month = datetime.datetime(now.year, now.month - 1, 1)

    find_top_left_cell(ws, 'F6').value = last_month.strftime('%b %Y')
    find_top_left_cell(
        ws, 'B8').value = last_month.strftime('%d.%m.%y')
    find_top_left_cell(
        ws,
        'B9').value = datetime.datetime(
        now.year,
        now.month,
        1).strftime('%d.%m.%y')


def write_to_excel(ws, col, row_start, data_series, days_last_month):
    """写入数据，限制为上月天数。"""
    if hasattr(data_series, "reset_index"):
        data_series = data_series.reset_index(drop=True)
    else:
        data_series = pd.Series(data_series)

    # 只取上月天数
    data_series = data_series[:days_last_month]

    for i, value in enumerate(data_series):
        if pd.notna(value):
            try:
                value = float(value)
            except Exception:
                value = None
        else:
            value = None
        ws.cell(row=row_start + i, column=col, value=value)


def get_file_path(prefix_pattern):
    """在基础目录中查找匹配文件。"""
    files = os.listdir(BASE_DIR)
    for f in files:
        if f.startswith(prefix_pattern):
            return os.path.join(BASE_DIR, f)
    return None


def calculate_daily_consumption(df, column):
    """计算每日用量，返回 Series。"""
    df[column] = pd.to_numeric(df[column], errors="coerce")
    daily_start = df.groupby(df["datetime"].dt.date)[column].first()
    daily_use = daily_start.diff().dropna()
    return daily_use.reset_index(drop=True)


def apply_borders(ws, cell_range):
    """应用细边框。"""
    thin_border = Border(left=Side(style=BORDER_THIN),
                         right=Side(style=BORDER_THIN),
                         top=Side(style=BORDER_THIN),
                         bottom=Side(style=BORDER_THIN))
    for row in ws[cell_range]:
        for cell in row:
            cell.border = thin_border


def generate_report(report_type, config):
    """根据配置生成报告。"""
    logger.info(f"--- 正在生成 {report_type} 报告 ---")

    try:
        now = datetime.datetime.now()
        current_date = now.strftime('%Y%m')
        last_month_str = (
                now.replace(
                    day=1) -
                datetime.timedelta(
                    days=1)).strftime('%Y%m')

        # 计算上月天数
        today = datetime.datetime.today()
        last_month = today.month - 1 if today.month > 1 else 12
        year = today.year if today.month > 1 else today.year - 1
        days_last_month = calendar.monthrange(year, last_month)[1]

        file_prefix = f"{config['data_file_pattern']}{current_date}"
        report_file_path = get_file_path(file_prefix)
        if not report_file_path:
            raise FileNotFoundError(
                f"未找到 {current_date} 的 {report_type} 报告文件。")

        df = pd.read_excel(
            report_file_path,
            sheet_name='Report',
            header=1,
            parse_dates=['datetime'])
        df = df.dropna(subset=['datetime'])
        df.columns = df.columns.str.strip()
        df = df.dropna(how='all')
        logger.info(f"{report_type} 月度报告已成功导入！")

        wb2 = load_template(config['template_file_name'])

        if 'Summary' in wb2.sheetnames:
            set_report_dates(wb2['Summary'], now)

        # 使用一个新的列表来明确哪些表格需要写入E8和E9的值
        sheets_with_start_end_values = [
            'HotelLZ PreHeat',
            'SvcAptLZ PreHeat',
            'HotelHZ HT',
            'HotelLZ HT',
            'HotelLZ MT',
            'SvcAptHZ HT',
            'SvcAptLZ HT',
            'SvcAptLZ MT',
            'OfficeHZ MT',
            'OfficeLZ MT',
            'PodiumE MT',
            'PodiumW MT',
            'PodiumE',
            'PodiumW',
            'HotelHZ',
            'HotelLZ',
            'OfficeHZ',
            'OfficeLZ',
            'SvcAptHZ',
            'SvcAptLZ'
        ]

        for ws_name, meters in config['ws_meters'].items():
            if ws_name in wb2.sheetnames:
                ws = wb2[ws_name]
                qq_col = meters['qq']
                qi_col = meters['qi']

                # 添加调试信息
                logger.info(f"处理工作表: {ws_name}")
                logger.info(f"QQ列: {qq_col}, 在数据中: {qq_col in df.columns}")
                logger.info(f"QI列: {qi_col}, 在数据中: {qi_col in df.columns}")

                # QQ 日用量
                if qq_col in df.columns:
                    daily_use = calculate_daily_consumption(df, qq_col)
                    write_to_excel(ws, 5, 21, daily_use, days_last_month)

                # QI 每日最大
                if qi_col in df.columns:
                    df_max_daily_qi = df.groupby(pd.Grouper(
                        key='datetime', freq='D'))[qi_col].max()
                    df_max_daily_qi = df_max_daily_qi.reset_index(drop=True)
                    write_to_excel(ws, 3, 21, df_max_daily_qi, days_last_month)

                # 修复：确保在所有需要的工作表中都写入E8和E9的值
                if ws_name in sheets_with_start_end_values and qq_col in df.columns:
                    # 计算上个月的日期范围
                    if now.month == 1:
                        last_month_start = datetime.datetime(now.year - 1, 12, 1)
                    else:
                        last_month_start = datetime.datetime(now.year, now.month - 1, 1)

                    last_month_end = last_month_start.replace(day=calendar.monthrange(
                        last_month_start.year, last_month_start.month)[1])

                    # 筛选上个月第一天的数据
                    first_day_data = df[df['datetime'].dt.date == last_month_start.date()]
                    # 筛选上个月最后一天的数据
                    last_day_data = df[df['datetime'].dt.date == last_month_end.date()]

                    # 获取上个月第一天的第一个值
                    if not first_day_data.empty:
                        start_value = first_day_data[qq_col].iloc[0]
                    else:
                        start_value = None
                        logger.warning(f"在 {ws_name} 中未找到上个月第一天的数据")

                    # 获取上个月最后一天的最后一个值
                    if not last_day_data.empty:
                        end_value = last_day_data[qq_col].iloc[-1]
                    else:
                        end_value = None
                        logger.warning(f"在 {ws_name} 中未找到上个月最后一天的数据")

                    ws["E8"].value = start_value
                    ws["E9"].value = end_value
                    logger.info(f"在 {ws_name} 中设置 E8={start_value}, E9={end_value}")
                else:
                    logger.warning(
                        f"未在 {ws_name} 中设置E8/E9值，条件: {ws_name in sheets_with_start_end_values} and {qq_col in df.columns}")

                # 边框
                apply_borders(ws, 'C21:C51')
                apply_borders(ws, 'E21:E51')

        report_path = os.path.join(
            BASE_DIR, f"{last_month_str}_{report_type}.xlsx")
        wb2.save(report_path)
        logger.info(f"{report_type} 报告已成功保存到 {report_path}")

    except Exception as e:
        logger.exception(f"处理 {report_type} 报告时发生错误: {e}")


def main():
    """主函数，用于协调两种报告的生成。"""
    # 报告配置
    report_configs = {
        'HW': {
            'data_file_pattern': 'HW RTU_Monthly Report_',
            'template_file_name': '202309_HW_temp.xlsx',
            'ws_meters': {
                'HotelLZ PreHeat': {'qq': 'H1_QQ_9350_BTU', 'qi': 'H1_QI_9350_BTU'},
                'SvcAptLZ PreHeat': {'qq': 'H2_QQ_9350_BTU', 'qi': 'H2_QI_9350_BTU'},
                'HotelHZ HT': {'qq': 'H3_QQ_9350_BTU', 'qi': 'H3_QI_9350_BTU'},
                'HotelLZ HT': {'qq': 'H4_QQ_9350_BTU', 'qi': 'H4_QI_9350_BTU'},
                'HotelLZ MT': {'qq': 'H5_QQ_9350_BTU', 'qi': 'H5_QI_9350_BTU'},
                'SvcAptHZ HT': {'qq': 'H6_QQ_9350_BTU', 'qi': 'H6_QI_9350_BTU'},
                'SvcAptLZ HT': {'qq': 'H7_QQ_9350_BTU', 'qi': 'H7_QI_9350_BTU'},
                'SvcAptLZ MT': {'qq': 'H8_QQ_9350_BTU', 'qi': 'H8_QI_9350_BTU'},
                'OfficeHZ MT': {'qq': 'H9_QQ_9350_BTU', 'qi': 'H9_QI_9350_BTU'},
                'OfficeLZ MT': {'qq': 'H10_QQ_9350_BTU', 'qi': 'H10_QI_9350_BTU'},
                'PodiumE MT': {'qq': 'H11_QQ_9350_BTU', 'qi': 'H11_QI_9350_BTU'},
                'PodiumW MT': {'qq': 'H20_QQ_9350_BTU', 'qi': 'H20_QI_9350_BTU'}
            }
        },
        'CHW': {
            'data_file_pattern': 'CHW RTU_Monthly Report_',
            'template_file_name': '202309_CHW_temp.xlsx',
            'ws_meters': {
                'PodiumE': {'qq': 'D1_QQ_1150_BTU', 'qi': 'D1_QI_1150_BTU'},
                'PodiumW': {'qq': 'D2_QQ_1150_BTU', 'qi': 'D2_QI_1150_BTU'},
                'HotelHZ': {'qq': 'D3_QQ_1150_BTU', 'qi': 'D3_QI_1150_BTU'},
                'HotelLZ': {'qq': 'D4_QQ_1150_BTU', 'qi': 'D4_QI_1150_BTU'},
                'OfficeHZ': {'qq': 'D5_QQ_1150_BTU', 'qi': 'D5_QI_1150_BTU'},
                'OfficeLZ': {'qq': 'D6_QQ_1150_BTU', 'qi': 'D6_QI_1150_BTU'},
                'SvcAptHZ': {'qq': 'D7_QQ_1150_BTU', 'qi': 'D7_QI_1150_1_BTU'},
                'SvcAptLZ': {'qq': 'D8_QQ_1150_BTU', 'qi': 'D8_QI_1150_2_BTU'},

            }
        }
    }

    for report_type, config in report_configs.items():
        generate_report(report_type, config)


if __name__ == '__main__':
    main()