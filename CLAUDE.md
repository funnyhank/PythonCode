# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 工作区性质

`projects/` 不是单个代码库,而是 **~30 个相互独立的 Python 项目**的集合,2026-08-03 从 Windows(`C:\Users\funny\PycharmProjects`)迁移到 WSL2。顶层 `迁移说明.md` 记录了迁移细节。

**重要约束:不要删除或修改 Windows 源目录 `C:\Users\funny\PycharmProjects`,原样保留。** (Windows 侧无 Git 版本跟踪,是唯一可信源,删除不可恢复。)

## 环境

- 每个代码项目有自己的 `.venv`(Python 3.14.4),彼此隔离。**不存在共享的全局解释器** —— 工作前先激活对应项目的 venv。
- 依赖声明在每个项目的 `requirements.txt`。其中 19 个项目的清单是从 Windows 旧 venv 的 `dist-info` 元数据重建的(2026-08-03),以重建版本为准。
- 平台差异:
  - Windows 专用包已移除(`pywin32`、`pypiwin32`、`win10toast`、`pywinpty`)。
  - `mysql-connector` 已改为 `mysql-connector-python`(PyPI 上无前者)。
  - `pygame` 用 `pygame-ce` 替代(模块名仍为 `pygame`,drop-in)。
  - 旧版本锁定已放宽到支持 Python 3.14 的版本。

## 常用命令

```bash
# 激活项目环境
source <项目>/.venv/bin/activate

# 安装/重建依赖
<项目>/.venv/bin/pip install -r <项目>/requirements.txt

# 验证环境与语法
<项目>/.venv/bin/pip check
python -m compileall -q <项目>/src <项目>/*.py   # 按实际文件位置调整

# 直接运行(多数项目无打包/入口约定,入口通常是 app.py / main.py / gui.py / <名称>.py)
<项目>/.venv/bin/python <项目>/app.py
```

没有统一的测试框架、lint 或构建工具。改动后用 `compileall` + `pip check` 做基本验证即可;GUI 项目(PySide6 / pygame)需要 X/Wayland 显示环境,在 WSL2 无图形会话时无法直接运行。

## 目录结构速览

- **Web 应用**: `Flask_web`、`myweb`、`FlaskProject01`(Flask);`DjangoTutorial`(Django)。入口均为 `app.py` 或 `manage.py`。
- **桌面 GUI**: `pyside6_gui`(PySide6)、`PygameOOP`(pygame-ce)。
- **用电/账单数据处理**(业务核心,通常含 `config.yaml` + `logging.yaml` + SQL 查询 + Excel 导出): `rccq_monthly_bill`、`shudu_bill`、`MonthlyBill_RCCQ`、`Monthlybill`、`IUDC_Monthly_elect`、`RCCQ_Query`、`export_energy.py`。
- **监控与邮件**: `data_monitor`、`dailyOAemail`。
- **数据库工具**: `MySQL_Connect`、`py_sql_DA`。
- **抓取/文本处理**: `Cricbuzz_scrapper`、`audio2txt`、`readPDFtable`、`WordSpire`。
- **教学/第三方**: `Python-master`(外部教学示例集合)、`JupyterNotebook`。
- **非代码目录**: `conf/`(配置)、`logs/`(日志)、`O&M trainning/`(PDF 文档)、`武侯月度用电/`(已编译的 Windows .exe,**Linux 上无法运行**)。

## Git

- 顶层 `projects/` 是一个 Git 仓库(历史继承自原 PycharmProjects),当前分支 `wsl`。远程:`funnyhank` → `github.com/funnyhank/PythonCode.git`、`origin` → `github.com/funnyhank/somecode.git`。
- `myweb/` 内部另有一个**独立的** Git 仓库,与顶层仓库无关,改 myweb 时注意区分。

## 已知坑

- `Python-master/` 内含 33 个 **Python 2 语法**文件(`print "x"` 等),源仓库自带问题,勿当作 Python 3 代码修复。
- 各项目遗留 `.idea/`(PyCharm 配置,含 Windows 路径),仅供参考。
- `myweb/`、`shudu_bill/` 的 requirements.txt 原本是 UTF-16,已转 UTF-8;修改时保持 UTF-8。
