#!/usr/bin/env python
# coding: utf-8

import os
import datetime
import sys
import logging
import logging.config
import pandas as pd
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
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('applog')
    logger.warning("未找到 logging.conf 文件。正在使用基本日志配置。")


def load_template(file_name):
    """加载 Excel 模板工作簿。"""
    template_path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"未找到模板文件 '{file_name}'。")
    return load_workbook(template_path)


def find_top_left_cell(ws, cell_address):
    """
    检查一个单元格是否在合并区域内，并返回该区域的左上角单元格。
    这是为了解决 'MergedCell' object attribute 'value' is read-only 的问题。
    """
    for merged_range in ws.merged_cells.ranges:
        if cell_address in merged_range:
            return ws.cell(row=merged_range.min_row, column=merged_range.min_col)
    return ws[cell_address]


def set_report_dates(ws, now):
    """在指定工作表中设置报告日期和月份。"""
    if now.month == 1:
        last_month = datetime.datetime(now.year - 1, 12, 1)
    else:
        last_month = datetime.datetime(now.year, now.month - 1, 1)

    find_top_left_cell(ws, 'F6').value = last_month.strftime('%b %Y')
    find_top_left_cell(ws, 'B8').value = last_month.strftime('%d.%m.%y')
    find_top_left_cell(ws, 'B9').value = datetime.datetime(now.year, now.month, 1).strftime('%d.%m.%y')


def write_to_excel(ws, col, row_start, data_series):
    """
    将 pandas Series 或 list 数据写入工作表的特定列。
    自动重置索引，避免因为 dropna() 等操作导致错位。
    """
    if hasattr(data_series, "reset_index"):  # 如果是 pandas Series 或 DataFrame 列
        data_series = data_series.reset_index(drop=True)
    else:  # 如果是 list 或 numpy array
        data_series = pd.Series(data_series)

    for i, value in enumerate(data_series):
        # 统一转为数值（NaN 原样写入 Excel）
        if pd.notna(value):
            try:
                value = float(value)
            except Exception:
                value = None
        else:
            value = None

        ws.cell(row=row_start + i, column=col, value=value)




def get_file_path(prefix_pattern):
    """
    在基础目录中查找与给定前缀模式匹配的文件。
    这个函数现在使用 startswith() 进行严格匹配，
    以防止不同报告类型的文件混淆。
    """
    files = os.listdir(BASE_DIR)
    for f in files:
        if f.startswith(prefix_pattern):
            return os.path.join(BASE_DIR, f)
    return None


def calculate_daily_consumption(df, column):
    """
    计算每日用量。
    使用每天的“第一个时间点的读数”，并确保列为数值。
    """
    # 确保是数值列（把非法字符串变成 NaN）
    df[column] = pd.to_numeric(df[column], errors="coerce")

    # 取每天最早的一个值
    daily_start = df.groupby(df["datetime"].dt.date)[column].first()

    # 相邻两天做差，得到每日消耗
    daily_use = daily_start.diff().dropna()

    # 重置索引，避免写入 Excel 时错位
    return daily_use.reset_index(drop=True)


def apply_borders(ws, cell_range):
    """为给定的单元格范围应用细边框。"""
    thin_border = Border(left=Side(style=BORDER_THIN),
                         right=Side(style=BORDER_THIN),
                         top=Side(style=BORDER_THIN),
                         bottom=Side(style=BORDER_THIN))
    for row in ws[cell_range]:
        for cell in row:
            cell.border = thin_border


def generate_report(report_type, config):
    """
    根据给定的配置生成报告。
    """
    logger.info(f"--- 正在生成 {report_type} 报告 ---")

    try:
        now = datetime.datetime.now()
        current_date = now.strftime('%Y%m')
        last_month_str = (now.replace(day=1) - datetime.timedelta(days=1)).strftime('%Y%m')

        # 构建完整的文件名前缀以进行严格匹配
        file_prefix = f"{config['data_file_pattern']}{current_date}"
        report_file_path = get_file_path(file_prefix)

        if not report_file_path:
            raise FileNotFoundError(f"未找到 {current_date} 的 {report_type} 报告文件。")

        # 从 Excel 文件中读取数据
        df = pd.read_excel(report_file_path, sheet_name='Report', header=1, parse_dates=['datetime'])
        df = df.dropna(subset=['datetime'])
        df.columns = df.columns.str.strip()
        df = df.dropna(how='all')
        logger.info(f"{report_type} 月度报告已成功导入！")
        logger.info(f"报告文件中找到的列: {list(df.columns)}")

        # 加载 Excel 模板
        wb2 = load_template(config['template_file_name'])

        # 在 Summary 工作表上设置日期
        if 'Summary' in wb2.sheetnames:
            set_report_dates(wb2['Summary'], now)

        # 遍历每个仪表并写入数据
        for ws_name, meters in config['ws_meters'].items():
            if ws_name in wb2.sheetnames:
                ws = wb2[ws_name]
                qq_col = meters['qq']
                qi_col = meters['qi']

                logger.info(f"正在处理工作表: {ws_name}")

                # 写入每日用量 (QQ)
                if qq_col in df.columns:
                    daily_use = calculate_daily_consumption(df, qq_col)
                    write_to_excel(ws, 5, 21, daily_use)
                    # write_to_excel(ws, 'E21' ,daily_use)

                    # 写入仪表初始和结束读数
                    start_value = df[qq_col].iloc[0]
                    end_value = df[qq_col].iloc[-1]
                    find_top_left_cell(ws, 'E8').value = start_value
                    find_top_left_cell(ws, 'E9').value = end_value
                else:
                    logger.warning(f"报告文件中未找到列 '{qq_col}'。跳过 '{ws_name}' 的用量计算和写入。")

                # 写入每日最大负荷 (QI)
                if qi_col in df.columns:
                    df_max_daily_qi = df.groupby(pd.Grouper(key='datetime', freq='D'))[qi_col].max()
                    if len(df_max_daily_qi) > 1:
                        df_max_daily_qi = df_max_daily_qi.iloc[:-1]
                    write_to_excel(ws, 3, 21, df_max_daily_qi)
                else:
                    logger.warning(f"报告文件中未找到列 '{qi_col}'。跳过 '{ws_name}' 的最大负荷写入。")

                # 应用边框
                apply_borders(ws, 'C21:C51')
                apply_borders(ws, 'E21:E51')

        # 保存填充后的 Excel 文件
        report_path = os.path.join(BASE_DIR, f"{last_month_str}_{report_type}.xlsx")
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
