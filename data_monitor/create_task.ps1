# 设置任务名称
$TaskName = "DataMonitorHourly"

# 要执行的脚本路径
$ScriptPath = "C:\Users\funny\PycharmProjects\data_monitor\run_check.bat"

# 设置每小时触发一次，重复 1 天（每天自动续）
$Trigger = New-ScheduledTaskTrigger -Once -At "00:00" `
    -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration (New-TimeSpan -Days 1)

# 创建动作
$Action = New-ScheduledTaskAction -Execute $ScriptPath

# 设置系统账户运行
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest

# 注册任务
Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -Principal $Principal -Description "每小时运行一次的数据监测任务"
