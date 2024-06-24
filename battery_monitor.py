# battery_monitor.py
from ina219 import INA219

SHUNT_OHMS = 0.1
MIN_VOLTAGE = 3.0  # 완전 방전 전압
MAX_VOLTAGE = 4.2  # 완전 충전 전압

def read_battery_level():
    ina = INA219(SHUNT_OHMS)
    ina.configure()
    voltage = ina.voltage()
    current = ina.current()
    power = ina.power()
    battery_percentage = ((voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE)) * 100
    battery_percentage = max(0, min(100, battery_percentage))  # 0%와 100% 사이로 제한
    return voltage, current, power, battery_percentage
