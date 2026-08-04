import argparse
import os
import sys
import yaml
import logging
import logging.config
import pandas as pd
import pymysql
from datetime import date
from dateutil.relativedelta import relativedelta
import re
import openpyxl  # 显式导入，保证 PyInstaller 打包 Excel 依赖

# =========================
# 运行目录（关键修正点）
# =========================
def get_runtime_dir():
    """
    返回程序运行时应使用的根目录：
    - exe：exe 所在目录
    - python：脚本所在目录
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_runtime_dir()

# =========================
# CLI 参数
# =========================
def parse_args():
    parser = argparse.ArgumentParser(
        description="能源站冷/热量数据导出工具"
    )

    parser.add_argument("--project", required=True, help="项目代号，如 sdzx")
    parser.add_argument(
        "--type",
        required=True,
        choices=["cooling", "heating"],
        help="数据类型：cooling / heating"
    )
    parser.add_argument("--month", help="月份 YYYY-MM")
    parser.add_argument("--start", help="开始日期 YYYY-MM-DD")
    parser.add_argument("--end", help="结束日期 YYYY-MM-DD")

    return parser.parse_args()


# =========================
# 时间解析
# =========================
def resolve_date_range(args):
    # 指定 start / end 优先
    if args.start and args.end:
        return args.start, args.end

    # 使用 month 参数
    if args.month:
        # 严格校验 YYYY-MM
        if not re.match(r"^\d{4}-\d{2}$", args.month):
            raise ValueError(
                f"--month 参数格式错误: {args.month}，正确格式应为 YYYY-MM，例如 2025-12"
            )
        y, m = map(int, args.month.split("-"))
        if not (1 <= m <= 12):
            raise ValueError(f"--month 中的月份非法: {m}")

        start = date(y, m, 1)
        end = start + relativedelta(months=1)
        return start.isoformat(), end.isoformat()

    # 默认上一个自然月
    today = date.today()
    start = (today.replace(day=1) - relativedelta(months=1))
    end = today.replace(day=1)
    return start.isoformat(), end.isoformat()


# =========================
# 主程序
# =========================
def main():
    args = parse_args()

    # ---- 确保日志目录存在 ----
    os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

    # ---- 加载日志配置 ----
    logging_path = os.path.join(BASE_DIR, "logging.yaml")
    with open(logging_path, encoding="utf-8") as f:
        logging.config.dictConfig(yaml.safe_load(f))
    logger = logging.getLogger("export")

    logger.info("程序启动")
    logger.info(f"运行目录: {BASE_DIR}")

    # ---- 加载配置 ----
    config_path = os.path.join(BASE_DIR, "config.yaml")
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if args.project not in config["projects"]:
        raise ValueError(f"未知项目: {args.project}")

    project_cfg = config["projects"][args.project]
    table_name = project_cfg["table"]

    start_date, end_date = resolve_date_range(args)

    logger.info(f"项目: {args.project}")
    logger.info(f"类型: {args.type}")
    logger.info(f"时间范围: {start_date} ~ {end_date}")

    # ---- 读取 SQL ----
    sql_path = os.path.join(BASE_DIR, "query", f"{args.type}.sql")
    with open(sql_path, encoding="utf-8") as f:
        sql = f.read().format(table=table_name)

    # ---- 查询数据库 ----
    conn = pymysql.connect(**config["mysql"])
    df = pd.read_sql(
        sql,
        conn,
        params={
            "start_date": start_date,
            "end_date": end_date
        }
    )
    conn.close()
    logger.info(f"查询完成，记录数: {len(df)}")

    if df.empty:
        logger.warning("查询结果为空，导出文件将为空")
        return

    # ---------- 数据处理 ----------
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # ---------- 数据透视（宽格式） ----------
    pivot_df = df.pivot_table(
        index='Timestamp',
        columns='Tag',
        values='Value'
    ).reset_index()
    pivot_df.columns.name = None # 移除列名中的 'Tag'

    # ---------- 重命名列（可读性） ----------
    rename_map = {
        '1期累计冷量': '一期-累计冷量',
        '2期累计冷量': '二期-累计冷量',
        '1期累计热量': '一期-累计热量',
        '2期累计热量': '二期-累计热量',
        '1期供水温度': '一期-供水温度',
        '1期回水温度': '一期-回水温度',
        '2期供水温度': '二期-供水温度',
        '2期回水温度': '二期-回水温度',
        '1期流量': '一期-流量',
        '2期流量': '二期-流量'
    }
    pivot_df.rename(columns=rename_map, inplace=True)

    # ---------- 对累计冷量/热量取整 ----------
    for col in pivot_df.columns:
        if '累计冷量' in col or '累计热量' in col:
            pivot_df[col] = pd.to_numeric(pivot_df[col], errors='coerce').round(0).astype('Int64')

    # ---------- 温度保留一位小数 ----------
    for col in pivot_df.columns:
        if '温度' in col:
            pivot_df[col] = pd.to_numeric(pivot_df[col], errors='coerce').round(1)

    # ---------- 转为三维表（MultiIndex） ----------
    # pivot_df.columns = pd.MultiIndex.from_tuples([tuple(c.split('-')) for c in pivot_df.columns])

    # ---------- 写入 Excel ----------
    timestamp_str = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{args.project}_{args.type}_{timestamp_str}.xlsx"
    output_file_path = os.path.join(BASE_DIR, output_filename)

    pivot_df.to_excel(output_file_path, index=True)  # 保留 Timestamp
    logger.info(f"数据已成功写入 Excel 文件: {output_file_path}")


if __name__ == "__main__":
    main()