# 자전거, 오토바이, 킥보드, 외발휠 보호용 가방 만들기

라즈베리파이와 다양한 센서를 이용해 여러분의 이동 수단을 위한 보호 장비를 만들어보세요. 이 프로젝트는 블랙박스 기능과 사용자 설정 가능한 LED 표시 기능을 포함합니다.

## 사용 가능 하드웨어

- **라즈베리파이 제로 W**: 블랙박스 기능 실행이 가능하나, 처리 능력이 제한적일 수 있습니다.
- **추천 하드웨어**: 라즈베리파이 B3~B5

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

### 블루투스 연결 설정

블루투스를 이용해 스마트폰과 라즈베리파이를 연결하고, 스마트폰에서 재생되는 음악을 라즈베리파이에 연결된 스피커를 통해 출력하며, 이 음악 신호를 입력 신호로 변환하여 FFT(고속 푸리에 변환)를 통해 스펙트럼 분석을 수행하는 과정을 설명합니다.

1. **블루투스 소프트웨어 설치**:
   ```bash
   sudo apt-get install bluetooth bluez libbluetooth-dev libudev-dev
   ```
2. **블루투스 서비스 활성화 및 시작**:
   ```bash
   sudo systemctl enable bluetooth.service
   sudo systemctl start bluetooth.service
   ```
3. **블루투스 장치 페어링**:
   - 라즈베리파이에서 `bluetoothctl` 명령을 사용하여 블루투스 장치를 검색하고 페어링합니다.

### 오디오 루프백 설정

스마트폰에서 재생되는 음악을 라즈베리파이를 통해 스피커로 전송한 후, 이를 루프백 장치를 통해 다시 입력 신호로 취급하여 실시간으로 스펙트럼 분석을 수행합니다.

1. **pavucontrol 설치**:
   ```bash
   sudo apt-get install pavucontrol
   ```
   - 설치 후 `pavucontrol`을 실행하여 오디오 스트림이 올바르게 루프백 디바이스로 라우팅되는지 확인합니다.

2. **Loopback 모듈 로드**:
   ```bash
   pactl load-module module-loopback
   ```
   - `snd-aloop` 모듈 상태 확인:
     ```bash
     lsmod | grep snd_aloop
     ```
   - 모듈이 로드되지 않았다면, 다음 명령어로 모듈을 로드합니다:
     ```bash
     sudo modprobe snd-aloop
     ```

이 설정을 통해 라즈베리파이는 스마트폰에서 재생되는 음악을 받아 스피커로 출력하면서 동시에 이 오디오 데이터를 분석할 수 있는 입력 신호로 사용합니다. 이 데이터는 FFT를 통해 분석되며, 결과에 따라 연결된 LED 스트립의 색상과 밝기가 실시간으로 변경됩니다, 이로써 음악에 반응하는 시각적 디스플레이를 제공합니다.
