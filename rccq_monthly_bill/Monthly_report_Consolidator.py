import os
import datetime

# 假设报告文件存放在一个名为 'reports' 的文件夹中
REPORT_FOLDER = 'reports'


def generate_report(report_type):
    """
    根据报告类型生成月度报告。
    该函数现在根据生成报告的月份来构建文件名，
    但处理的数据仍然是前一个月的。
    """
    # 获取当前日期
    current_date = datetime.date.today()

    # 格式化当前月份作为文件名的一部分
    # 例如，在 2025年9月1日生成，文件名为 202509
    this_month_str = current_date.strftime('%Y%m')

    # 计算上一个月的日期
    first_day_of_this_month = current_date.replace(day=1)
    last_day_of_last_month = first_day_of_this_month - datetime.timedelta(days=1)
    last_month_str = last_day_of_last_month.strftime('%Y%m')

    print(f"--- 正在生成 {report_type} 报告 ---")

    # 构建正确的文件名
    file_name = f'HW RTU_Monthly Report_{this_month_str}01000907608.xlsx'
    file_path = os.path.join(REPORT_FOLDER, file_name)

    try:
        # 尝试打开并处理文件
        # 这里只是一个占位符，您可以添加实际的文件处理逻辑
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"未找到 {this_month_str} 的 {report_type} 报告文件。")

        # 成功找到文件后，可以继续处理数据
        print(f"成功找到文件：{file_path}，正在处理 {last_month_str} 的数据...")

    except FileNotFoundError as e:
        print(f"处理 {report_type} 报告时发生错误: {e}")
        # 您可以在这里添加更多错误处理逻辑，例如记录日志或发送通知。
    except Exception as e:
        print(f"处理 {report_type} 报告时发生意外错误: {e}")


# 示例调用
# 请确保您的 'reports' 文件夹中有一个名为 "HW RTU_Monthly Report_20250901000907608.xlsx" 的文件
generate_report('HW')
generate_report('CHW')
