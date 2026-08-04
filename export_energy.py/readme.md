# 能源站数据导出工具（CLI）

## 一、工具说明

本工具用于从能源站数据库中导出冷量 / 热量相关数据，
支持按 **项目**、**时间范围** 查询，并导出为 Excel 文件。
代码写作于2026-01-04，最后一次pyinstaller打包也是2026-01-04 

适用于：
- 月度报表
- 能源统计
- 运维数据核查

---

## 二、目录结构
```
正确的exe文件在dist下，所有的配置文件也应该在
export_energy.py/dist/
├─ export_energy.exe 主程序
├─ config.yaml 数据库与项目配置
├─ logging.yaml 日志配置
├─ query/ SQL 查询规则
│ ├─ cooling.sql
│ └─ heating.sql
├─ logs/ 日志目录（自动生成）
└─ *.xlsx 导出的 Excel 文件
```
---

## 三、使用方法

### 1️⃣ 导出指定月份数据

```bash
export_energy.exe --project sdzx --type cooling --month 2025-07

export_energy.exe --project sdzx --type heating \
  --start 2025-07-01 --end 2025-08-01
 ```

## 四、参数说明
参数	说明
```--project	项目代号（见 config.yaml）
--type	cooling / heating
--month	月份（YYYY-MM）
--start	开始日期
--end	结束日期
```

## 五、注意事项

请勿删除 config.yaml、logging.yaml、query 目录

数据库账号为只读账号

日志文件位于 logs 目录

SQL 规则修改请谨慎确认
