import pandas as pd
import os
import datetime

# 确保文件路径正确。我们直接使用原始的 .xlsx 文件。
file_path = 'HW RTU_Monthly Report_20250901000907608.xlsx'

# 检查文件是否存在
if not os.path.exists(file_path):
    print(f"错误：找不到文件 '{file_path}'。请确保文件路径正确。")
else:
    try:
        # 使用 pandas 的 read_excel 直接读取 .xlsx 文件。
        # 明确指定 sheet_name 和 header。
        # 假设数据在名为 'Report' 的工作表，且标题在第二行（索引为 1）。
        df = pd.read_excel(file_path, sheet_name='Report', header=1)

        # 将 'datetime' 列转换为 datetime 类型，确保时间处理的准确性
        date_column = 'datetime'
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
        else:
            print(f"错误：数据中未找到列 '{date_column}'。")
            exit()

        # --- 修正数据时间范围 ---
        # 确定报告的结束日期，即文件中的最大日期
        end_date = df[date_column].max()

        # 确定报告的开始日期，即结束日期的前一个月的1日
        start_date = (end_date - pd.DateOffset(months=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # 过滤数据，只保留从开始日期（包含）到结束日期（不包含）的数据
        # 这将确保我们只得到完整的月份数据
        df_filtered = df[(df[date_column] >= start_date) & (df[date_column] < end_date)].copy()

        if df_filtered.empty:
            print("错误：筛选后的数据为空。请检查文件中的时间范围和列名。")
            exit()

        # 使用过滤后的数据进行后续所有计算
        df = df_filtered

        # 定义需要计算总和的列，这些是热能消耗数据
        btu_columns = [
            'H1_QQ_9350_BTU', 'H2_QQ_9350_BTU', 'H3_QQ_9350_BTU', 'H4_QQ_9350_BTU',
            'H5_QQ_9350_BTU', 'H6_QQ_9350_BTU', 'H7_QQ_9350_BTU', 'H8_QQ_9350_BTU',
            'H9_QQ_9350_BTU', 'H10_QQ_9350_BTU', 'H11_QQ_9350_BTU', 'H20_QQ_9350_BTU'
        ]

        # 过滤掉不存在的列，以防数据不完整
        existing_btu_columns = [col for col in btu_columns if col in df.columns]
        if not existing_btu_columns:
            print("错误：未找到任何有效的 BTU 消耗列。请检查列名。")
            exit()

        # 将所有 BTU 列转换为数值类型，并强制转换错误值为 NaN
        for col in existing_btu_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 按天进行聚合，计算每天的总消耗
        df['date'] = df[date_column].dt.date
        daily_btu_sum = df.groupby('date')[existing_btu_columns].sum()

        # 计算报告摘要
        total_btu_sum = daily_btu_sum.sum()
        num_days = len(daily_btu_sum)

        # --- 生成报告 ---

        # 打印月度报告标题
        report_month = df['date'].min().strftime('%Y年%m月')
        print(f"\n==================== {report_month} 热能消耗报告 ====================")

        # 打印每日总消耗和平均消耗
        print("\n--- 每日总热能消耗 (BTU) ---")
        print(daily_btu_sum.to_string())

        print(f"\n--- 月度总热能消耗 (BTU) ---")
        for col in existing_btu_columns:
            print(f"- {col}: {total_btu_sum[col]:,.2f} BTU")

        # 打印月度平均值
        print("\n--- 月度平均每日热能消耗 (BTU) ---")
        for col in existing_btu_columns:
            average_daily = total_btu_sum[col] / num_days
            print(f"- {col}: {average_daily:,.2f} BTU/天")

        # 打印报告时间范围
        start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
        print("\n--- 数据范围 ---")
        print(f"数据覆盖时间: {start_date_str} 到 {end_date_str}")
        print(f"数据总天数: {num_days} 天")

    except Exception as e:
        print(f"处理文件时发生错误: {e}")
