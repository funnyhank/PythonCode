
# -*- coding: utf-8 -*-
"""
@Purpose: 通过温度、气压、相对湿度 计算 比湿
@Method:《天气诊断分析》-尚可政 气象出版社
1、计算饱和水汽压（p44）：
Tenlens公式（1930）：
saturation_vapor_pressure = 6.11 * 10**((7.5 * temperature) / (temperature + 237.3))
2、通过相对湿度、饱和水汽压，计算实际水汽压：
actual_vapor_pressure = (relative_humidity / 100) * saturation_vapor_pressure
3、计算比湿（p47）：
specific_humidity = (0.622 * actual_vapor_pressure) / (pressure - actual_vapor_pressure*0.378)
"""


def calculate_saturation_vapor_pressure(temperature):
    """计算饱和水汽压（hPa）"""
    return 6.11 * 10**((7.5 * temperature) / (temperature + 237.3))


def calculate_actual_vapor_pressure(
        relative_humidity,
        saturation_vapor_pressure):
    """计算实际水汽压（hPa）"""
    return (relative_humidity / 100) * saturation_vapor_pressure


def calculate_specific_humidity(actual_vapor_pressure, pressure):
    """计算比湿（g/kg）"""
    return (0.622 * actual_vapor_pressure) / \
        (pressure - actual_vapor_pressure * 0.378) * 1000


# 示例数据
temperature = 30  # 近地面温度（单位：摄氏度）
relative_humidity = 40  # 相对湿度（单位：%）
pressure = 1000  # 气压（单位：hPa）

# 计算
saturation_vapor_pressure = calculate_saturation_vapor_pressure(temperature)
actual_vapor_pressure = calculate_actual_vapor_pressure(
    relative_humidity, saturation_vapor_pressure)
specific_humidity = calculate_specific_humidity(
    actual_vapor_pressure, pressure)

print(f"饱和水汽压: {saturation_vapor_pressure:.2f} hPa")
print(f"实际水汽压: {actual_vapor_pressure:.2f} hPa")
print(f"比湿: {specific_humidity:.5f} g/kg")
