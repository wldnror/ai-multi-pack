import os
import datetime
import psutil
import time

def get_cpu_temperature():
    """CPU 온도를 읽어 반환합니다."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = f.read()
        return float(temp) / 1000
    except FileNotFoundError:
        return None

def log_system_status(path, threshold):
    """시스템 상태를 로그 파일에 기록하고 실시간으로 출력합니다."""
    cpu_temp = get_cpu_temperature()
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()

    # 온도나 사용량이 임계값을 초과하는 경우에만 기록
    if cpu_temp > threshold['temp'] or cpu_usage > threshold['cpu'] or memory.percent > threshold['memory']:
        with open(path, "a") as file:
            file.write(f"{datetime.datetime.now()}, CPU Temp: {cpu_temp}C, CPU Usage: {cpu_usage}%, Memory Usage: {memory.percent}%\n")

    # 실시간으로 모니터링 값을 출력
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - CPU Temp: {cpu_temp}C, CPU Usage: {cpu_usage}%, Memory Usage: {memory.percent}%")

def main():
    log_path = "system_status.log"
    # 임계값 설정: 온도 60도, CPU 사용률 75%, 메모리 사용률 75%
    thresholds = {'temp': 60, 'cpu': 75, 'memory': 75}

    while True:
        log_system_status(log_path, thresholds)
        time.sleep(10)  # 60초 간격으로 체크

if __name__ == "__main__":
    main()
