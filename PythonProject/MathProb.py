import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体（确保中文正常显示）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 时间轴 (0 到 22.5 分钟)
t = np.linspace(0, 22.5, 1000)

# 计算甲和乙的位置 (以A地为原点 0，B地为 7200)
pos_jia = np.zeros_like(t)
pos_yi = np.zeros_like(t)

for i, ti in enumerate(t):
    # 甲的路线
    if ti <= 18:
        pos_jia[i] = 300 * ti
    else:
        pos_jia[i] = 5400 + 400 * (ti - 18)

    # 乙的路线
    if ti <= 18:
        pos_yi[i] = 400 * ti
    else:
        pos_yi[i] = 7200 - 500 * (ti - 18)

# 两人的距离
distance = np.abs(pos_jia - pos_yi)

# 创建画布
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# 图1：位置 - 时间 图
ax1.plot(t, pos_jia, label='甲的位置', color='blue', linewidth=2)
ax1.plot(t, pos_yi, label='乙的位置', color='orange', linewidth=2)
ax1.axhline(7200, color='gray', linestyle='--', label='B地 (7200m)')
ax1.axhline(0, color='black', linestyle='-', alpha=0.3, label='A地 (0m)')
ax1.set_ylabel('距离 A 地位置 (m)')
ax1.set_title('甲、乙运动轨迹与信息闭塞状态分析')
ax1.legend(loc='upper left')
ax1.grid(True, linestyle=':', alpha=0.6)

# 图2：两人间距 - 时间 图
ax2.plot(t, distance, label='两人距离', color='green', linewidth=2)
ax2.axhline(1000, color='red', linestyle='--', label='信息闭塞临界值 (1000m)')

# 高亮闭塞区间
blocked = distance > 1000
ax2.fill_between(t, 0, distance, where=blocked, color='red', alpha=0.2, label='处于闭塞状态')
ax1.fill_between(t, 0, 7200, where=blocked, color='red', alpha=0.1)

ax2.set_xlabel('时间 (分钟)')
ax2.set_ylabel('两人距离 (m)')
ax2.legend(loc='upper right')
ax2.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.show()