import numpy as np
import matplotlib.pyplot as plt


class L1AdaptiveController:
    def __init__(self, params):
        self.params = params
        self.u_prev = 0  # 初始化滤波器前一次的控制输入
        self.kr = params['am'] / params['b']  # 计算理想控制器的增益
        self.Phi_Ts = (
            1 - np.exp(-self.params['am'] * self.params['Ts'])) / self.params['am']

    def step(self, t):
        # 阶跃函数，t>=0时返回1，否则返回0
        return 1 if t >= 0 else 0

    def plant(self, x_prev, u, t):
        # 被控对象（系统）的动态方程，包含干扰信号
        d = 100 * (self.step(t - 0.01) - self.step(t - 0.02)) \
            + (300 + 500 * np.sin(500 * t)) * (self.step(t - 0.04) - self.step(t - 0.05)) \
            + (500 * np.sin(1000 * t) - 500) * (self.step(t - 0.07) - self.step(t - 0.08))

        dx = -self.params['a'] * x_prev + \
            self.params['b'] * (u + d)  # 系统状态的变化率
        x = x_prev + dx * self.params['dt']  # 系统状态更新
        return x, dx, d

    def predictor(self, x_hat_prev, u, sigma_hat):
        # 预测器的动态方程，用于估计下一步的系统状态
        dx_hat = -self.params['am'] * x_hat_prev + \
            self.params['b'] * (u + sigma_hat)
        x_hat = x_hat_prev + dx_hat * self.params['Ts']
        return x_hat, dx_hat

    def controller(self, sigma_hat):
        # 控制器设计，基于L1自适应控制原理
        u = self.kr * self.params['r'] - sigma_hat
        u_f = (self.params['Ts'] / self.params['tau']) * u + \
            (1 - self.params['Ts'] / self.params['tau']) * self.u_prev
        self.u_prev = u_f
        return u_f

    def estimator(self, x_tilde):
        # 不确定性估计器，用于估计系统的不确定性
        muy = np.exp(-self.params['am'] * self.params['Ts']) * x_tilde
        sigma_hat = -muy / (self.Phi_Ts * self.params['b'])
        return sigma_hat


# 参数设置
params = {
    'dt': 0.0001,  # 植物（被控对象）采样时间间隔
    'Ts': 0.001,  # 自适应采样时间
    'a': 0.01,  # 系统参数a，通常较小
    'am': 6,  # 理想模型的动态参数
    'b': 6,  # 系统参数b，影响控制输入对系统输出的作用
    'r': 0,  # 期望轨迹，初始化为0，可以在主循环中动态更新
    'tau': 0.001  # 滤波器时间常数
}

# 初始化控制器
controller = L1AdaptiveController(params)

Tf = 10  # 仿真时间
t = np.arange(0, Tf + params['dt'], params['dt'])  # 仿真时间轴
ts = np.arange(0, Tf + params['Ts'], params['Ts'])  # 自适应控制器采样时间轴

# 初始化（先建立列表方便后续可视化）
u = np.zeros(len(ts))  # 控制输入
x = np.zeros(len(t))  # 系统状态
dx = np.zeros(len(t))  # 系统状态导数
x_hat = np.zeros(len(ts))  # 预测状态
dx_hat = np.zeros(len(ts))  # 预测状态导数
x_tilde = np.zeros(len(ts))  # 状态误差
d = np.zeros(len(t))  # 干扰信号
sigma_hat = np.zeros(len(ts))  # 系统不确定性估计
r_track = np.zeros(len(t))  # 用于存储期望轨迹

# 主循环
j = 0
for i in range(len(t)):
    # 期望轨迹，这里设置为一个正弦波
    params['r'] = np.sin(2 * np.pi * 1 * t[i])
    r_track[i] = params['r']  # 记录期望轨迹

    if i % round(params['Ts'] / params['dt']) == 0:  # 自适应控制器采样
        x_tilde[j] = x_hat[j] - x[i]  # 计算状态误差

        sigma_hat[j] = controller.estimator(x_tilde[j])  # 估计系统不确定性

        u[j] = controller.controller(sigma_hat[j])  # 控制器+滤波器输出
        u[j] = u[j] * 3  # 增益调整

        if j == len(ts) - 1:  # 最后一次采样
            _, dx_hat[j] = controller.predictor(
                x_hat[j], u[j], sigma_hat[j])  # 预测系统
        else:
            # 预测系统
            x_hat[j +
                  1], dx_hat[j] = controller.predictor(x_hat[j], u[j], sigma_hat[j])

        j += 1

    if i == len(t) - 1:  # 最后一次仿真
        _, dx[i], d[i] = controller.plant(x[i], u[j - 1], t[i])  # 被控对象状态更新
    else:
        # 被控对象状态更新
        x[i + 1], dx[i], d[i] = controller.plant(x[i], u[j - 1], t[i])

# 绘图
plt.figure()
plt.plot(t, x, label='Actual Trajectory')  # 实际轨迹
plt.plot(t, r_track, '--r', label='Desired Trajectory')  # 期望轨迹
plt.title('Tracking Performance')  # 期望轨迹
plt.legend()
plt.grid()

plt.show()
