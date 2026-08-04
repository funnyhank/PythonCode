import pandas as pd
import pymysql
import yaml
import logging
import logging.config
from datetime import datetime
import os
import matplotlib.pyplot as plt

# 设置 matplotlib 支持中文，防止图表中出现乱码
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

# ---------- 设置目录 ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- 加载日志配置 ----------
try:
    with open(os.path.join(BASE_DIR, "logging.yaml"), "r", encoding="utf-8") as f:
        logging_config = yaml.safe_load(f)
        logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
except Exception as e:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.error(f"加载日志配置失败: {e}")

# ---------- 加载数据库配置 ----------
try:
    with open(os.path.join(BASE_DIR, "config.yaml"), "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    db_config = {
        "host": config["mysql"]["host"],
        "port": config["mysql"]["port"],
        "user": config["mysql"]["user"],
        "password": config["mysql"]["password"],
        "db": config["mysql"]["database"],
        "charset": "utf8mb4"
    }
except Exception as e:
    logger.exception(f"加载数据库配置失败: {e}")
    exit()


# ---------- 主程序 ----------
def main():
    """
    主函数，负责数据查询、处理、导出和绘图。
    """
    try:
        # ---------- 读取 SQL 文件 ----------
        sql_file_path = os.path.join(BASE_DIR, "query", "cooling_data.sql")
        logger.info(f"正在读取 SQL 文件: {sql_file_path}")
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_query = f.read()

        # ---------- 查询数据 ----------
        logger.info("开始连接数据库...")
        with pymysql.connect(**db_config) as conn:
            df = pd.read_sql(sql_query, conn)
        logger.info(f"成功从数据库读取 {len(df)} 条记录。")

        # ---------- 数据处理 ----------
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        pivot_df = df.pivot(
            index='Timestamp',
            columns='Tag',
            values='Value'
        ).reset_index()
        pivot_df.columns.name = None

        pivot_df.rename(columns={
            '1期累计冷量': '一期累计冷量',
            '2期累计冷量': '二期累计冷量',
            '1期供水温度': '1期供水温度',
            '1期回水温度': '1期回水温度',
            '1期流量': '1期流量',
            '2期供水温度': '2期供水温度',
            '2期回水温度': '2期回水温度',
            '2期流量': '2期流量'
        }, inplace=True)

        for col in ['一期累计冷量', '二期累计冷量']:
            if col in pivot_df.columns:
                pivot_df[col] = pd.to_numeric(
                    pivot_df[col], errors='coerce'
                ).round(0).astype('Int64')
        logger.info("数据处理完成，已对指定列取整。")

        # ---------- 写入 Excel ----------
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M')
        output_filename = f"冷量累计数据_取整_{timestamp_str}.xlsx"
        output_file_path = os.path.join(BASE_DIR, output_filename)
        pivot_df.to_excel(output_file_path, index=False)
        logger.info(f"数据已成功写入 Excel 文件: {output_file_path}")

        # ---------- 绘制并保存折线图 ----------
        logger.info("开始绘制夜间流量趋势图...")

        # 筛选出夜间数据（22:00 到次日 08:00）
        # 'Timestamp' 列需要是 datetime 类型才能使用 .dt 属性
        night_data = pivot_df[
            ((pivot_df['Timestamp'].dt.hour >= 22) & (pivot_df['Timestamp'].dt.hour <= 23)) |
            ((pivot_df['Timestamp'].dt.hour >= 0) & (pivot_df['Timestamp'].dt.hour < 8))
            ].copy()  # 使用 .copy() 防止 SettingWithCopyWarning

        # 确保数据不为空
        if not night_data.empty:
            plt.figure(figsize=(15, 8))

            # 定义需要绘图的列
            plot_cols = [
                '1期供水温度', '1期回水温度', '1期流量',
                '2期供水温度', '2期回水温度', '2期流量'
            ]

            for col in plot_cols:
                # 检查列是否存在，防止因数据缺失导致报错
                if col in night_data.columns:
                    plt.plot(night_data['Timestamp'], night_data[col], label=col)

            plt.title('夜间 22:00 - 次日 08:00 冷却趋势图', fontsize=16)
            plt.xlabel('时间', fontsize=12)
            plt.ylabel('值', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.legend(fontsize=10)
            plt.tight_layout()  # 自动调整子图参数，使之填充整个图像区域

            # 保存图片
            chart_filename = f"夜间冷却趋势图_{timestamp_str}.png"
            chart_file_path = os.path.join(BASE_DIR, chart_filename)
            plt.savefig(chart_file_path)

            logger.info(f"折线图已成功保存为图片: {chart_file_path}")
        else:
            logger.warning("未找到符合夜间条件的数据，跳过绘图。")

    except Exception as e:
        logger.exception("程序运行失败，请检查错误日志。")


if __name__ == "__main__":
    main()