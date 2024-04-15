# 자전거, 오토바이, 킥보드, 외발휠 보호용 가방 만들기

라즈베리파이와 다양한 센서를 이용해 여러분의 이동 수단을 위한 보호 장비를 만들어보세요. 이 프로젝트는 블랙박스 기능과 사용자 설정 가능한 LED 표시 기능을 포함합니다.

## 사용 가능 하드웨어

- **라즈베리파이 제로 W**: 블랙박스 기능 실행이 가능하나, 처리 능력이 제한적일 수 있습니다.
- **지원 배터리**: B3~B5 타입.

## 블랙박스용 추천 카메라

- **Logitech BRIO**:
  - **해상도**: 최대 4K Ultra HD (4096 x 2160) @ 30fps, 1080p @ 60fps
  - **특징**: 4K 화질, HDR 기능 및 자동 조명 보정으로 다양한 조명 환경에서 우수한 화질 제공.
  - **야간 성능**: 고급 조명 보정 기술로 저조도 환경에서도 비교적 좋은 성능 제공.

## 부가 재료

### LED 144발

- **구매 링크**: [용굴이.shop LED 스트립 조명](https://용굴이.shop/product/led-스트립-조명/99/category/76/display/1/)

### 필요한 라이브러리

- **Adafruit Blinka 설치**: CircuitPython 라이브러리를 라즈베리 파이와 같은 하드웨어에서 사용할 수 있도록 해주는 라이브러리입니다.
- **Adafruit CircuitPython NeoPixel 라이브러리 설치**: NeoPixel LED를 제어하기 위한 라이브러리입니다.

```bash
pip3 install Adafruit-Blinka
pip3 install adafruit-circuitpython-neopixel
```

### 방향 지시등 LED

- **구매 링크**: [용굴이.shop 혁신적인 안전 주행 액세서리 LED 화살표 스티어링 미러 라이트](https://용굴이.shop/product/혁신적인-안전-주행-액세서리-led-화살표-스티어링-미러-라이트-33smd-노란색-차량-방향-지시등/120/category/76/display/1/)

### MPU-6050 자이로센서 및 가속도 기능 탑재된 6축 센서

- **구매 링크**: [용굴이.shop 고정밀 자이로 가속도 센서 모듈](https://용굴이.shop/product/고정밀-자이로-가속도-센서-모듈/124/category/1/display/3/)

### 필요 라이브러리

- **Python-SMBus**: Python에서 I2C 통신을 위해 필요한 라이브러리입니다.
- **MPU6050 Python 라이브러리**: MPU-6050 센서 데이터를 쉽게 읽을 수 있게 해주는 라이브러리입니다.

```bash
sudo apt-get install python3-smbus i2c-tools
pip install mpu6050-raspberrypi
```

### 블루투스 연결을 위한 설정

(이 부분은 원본 메시지에서 내용이

 불완전하여 추가 설명이 필요합니다. 필요한 내용을 알려주시면 완성해 드리겠습니다.)
