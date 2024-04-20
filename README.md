# 자전거, 오토바이, 킥보드, 외발휠 보호용 가방 만들기

라즈베리파이와 다양한 센서를 이용해 여러분의 이동 수단을 위한 보호 장비를 만들어보세요.  
이 프로젝트는 AI 블랙박스 기능과 사용자 설정 가능한 LED 표시 기능을 포함합니다.  
블랙박스 코드는 ftp서버로 전송시키는 기능이 있기 때문에 해당 부분은 주소 수정이 필요합니다.

# 필요한 부품및 재료

### 사용 가능 하드웨어

- **라즈베리파이 제로 W**: 블랙박스 기능 실행이 가능하나, 처리 능력이 제한적일 수 있습니다.
- **추천 하드웨어**: 라즈베리파이 B3~B5

### 블랙박스용 추천 카메라

- **Logitech BRIO**:
  - **해상도**: 최대 4K Ultra HD (4096 x 2160) @ 30fps, 1080p @ 60fps
  - **특징**: 4K 화질, HDR 기능 및 자동 조명 보정으로 다양한 조명 환경에서 우수한 화질 제공.
  - **야간 성능**: 고급 조명 보정 기술로 저조도 환경에서도 비교적 좋은 성능 제공.

### LED 144발

- **구매 링크**: [용굴이.shop LED 스트립 조명](https://용굴이.shop/product/led-스트립-조명/99/category/76/display/1/)

### 방향 지시등 LED

- **구매 링크**: [용굴이.shop 혁신적인 안전 주행 액세서리 LED 화살표 스티어링 미러 라이트](https://용굴이.shop/product/혁신적인-안전-주행-액세서리-led-화살표-스티어링-미러-라이트-33smd-노란색-차량-방향-지시등/120/category/76/display/1/)

### MPU-6050 자이로센서 및 가속도 기능 탑재된 6축 센서

- **구매 링크**: [용굴이.shop 고정밀 자이로 가속도 센서 모듈](https://용굴이.shop/product/고정밀-자이로-가속도-센서-모듈/124/category/1/display/3/)


# 필요한 라이브러리 소프트웨어 설치 및 설정

프로젝트를 실행하기 위해 다음 라이브러리들을 설치하세요:

- **Adafruit Blinka**:
  - CircuitPython 라이브러리를 라즈베리 파이와 같은 하드웨어에서 사용할 수 있도록 해주는 라이브러리입니다.
   ```bash
   sudo pip3 install adafruit-blinka --break-system-packages
   ```
- **Adafruit CircuitPython NeoPixel**:
  - NeoPixel LED를 제어하기 위한 라이브러리입니다. 이 라이브러리를 사용하면 LED 스트립의 각 LED를 개별적으로 제어할 수 있습니다.
   ```bash
   sudo pip3 install adafruit-circuitpython-neopixel --break-system-packages
   ```
- **Sounddevice**:
  - 오디오를 녹음하고 재생할 수 있는 라이브러리입니다. 이 라이브러리는 PortAudio를 기반으로 합니다.
   ```bash
   sudo pip3 install sounddevice --break-system-packages
   ```
- **libportaudio2**:
  - Sounddevice 라이브러리의 의존성인 PortAudio 라이브러리의 리눅스 패키지입니다.
   ```bash
   sudo apt-get install libportaudio2
   ```
- **rpi_ws281x**:
  - 라즈베리 파이에서 WS281x (NeoPixel) LED를 직접 제어할 수 있도록 해주는 라이브러리입니다.
   ```bash
   sudo pip3 install rpi_ws281x --break-system-packages
   ```
- **Python-SMBus**:
  - Python에서 I2C 통신을 위해 필요한 라이브러리입니다.
   ```bash
   sudo apt-get install python3-smbus i2c-tools
   ```
- **MPU6050 Python 라이브러리**
  - MPU-6050 센서 데이터를 쉽게 읽을 수 있게 해주는 라이브러리입니다.
   ```bash
   pip install mpu6050-raspberrypi --break-system-packages
   ```
## 블루투스 연결 설정

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

### 오디오 루프백 수동 설정 (테스트용 입니다. 재부팅되면 초기화됩니다 아래 자동화 기능을 사용하세요)

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

## 루프백 자동화
### 1. default.pa 설정 변경
기본적으로 default.pa 파일을 통해 항상 3.5mm 잭을 기본 출력으로 설정할 수 있습니다:
- ```bash
  sudo nano /etc/pulse/default.pa
  ```
  ```bash
  set-default-sink alsa_output.platform-bcm2835_audio.stereo-fallback
  ```

### 1. 사용자 systemd 디렉터리로 이동:
```bash
mkdir -p ~/.config/systemd/user
```
### 2. 서비스 파일 생성:
```bash
nano ~/.config/systemd/user/pulseaudio-modules.service
```
### 3. 다음 내용을 파일에 입력합니다:
```bash
[Unit]
Description=Load PulseAudio modules for user
After=pulseaudio.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c "pactl load-module module-null-sink sink_name=virtual_mic sink_properties=device.description=Virtual_Microphone; pactl load-module module-loopback source=virtual_mic.monitor"
# 10초 대기 후 기본 싱크 설정
ExecStartPost=/bin/sleep 10
ExecStartPost=/bin/pactl set-default-sink alsa_output.platform-bcm2835_audio.stereo-fallback

[Install]
WantedBy=default.target
```

### 4. 사용자 서비스 활성화 및 시작:
```bash
systemctl --user enable pulseaudio-modules.service
systemctl --user start pulseaudio-modules.service
```

### 5. 연결된 블루투스 스피커는 usb스피커로 자동 조정

#### 5-1 블루투스 연결 감지
- 아래 파일을 만들다
  ```bash
  sudo nano /etc/systemd/system/bluetooth-audio-switch.service
  ```
- 아래 내용을 입력합니다.
  ```bash
  [Unit]
Description=Switch audio to USB speaker on Bluetooth connect
After=bluetooth.service
BindsTo=bluetooth.target

[Service]
Type=simple
ExecStart=/usr/local/bin/bluetooth-audio-switch

[Install]
WantedBy=multi-user.target

  ```
#### 5-2 오디오 라우팅 변경 스크립트
- 아래 파일을 만들다
  ```bash
  sudo nano /usr/local/bin/bluetooth-audio-switch
  ```

- 아래 내용을 입력합니다.

```bash
#!/bin/bash

# 블루투스 장치 연결 상태 체크
connected=$(bluetoothctl info | grep 'Connected: yes')

if [ -n "$connected" ]; then
    # USB 스피커로 오디오 출력 설정
    pactl set-default-sink alsa_output.usb-your_usb_speaker_device_name
else
    # 기본 오디오 장치로 설정 (3.5mm 잭)
    pactl set-default-sink alsa_output.platform-bcm2835_audio.stereo-fallback
fi
```
# 루프백 자동화 이후 오디오 문제 해결

### 1. udev 룰 생성
udev 룰 파일을 생성하고 특정 USB 장치가 연결될 때 실행될 스크립트를 지정합니다.

```bash
sudo nano /etc/udev/rules.d/99-usb-autoreconnect.rules
```

파일 내에 다음과 같은 내용을 추가합니다:

```bash
ACTION=="add", ATTRS{idVendor}=="144d", ATTRS{idProduct}=="2b2b", RUN+="/home/user/usb_reconnect.sh"
```

### 2. udev 룰 리로드
udev 룰 변경사항을 적용하기 위해 리로드합니다.

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 3. Bash 스크립트 작성
USB 장치를 자동으로 연결 해제하고 재연결하는 스크립트를 생성합니다.

```bash
sudo nano /home/user/usb_reconnect.sh
```

스크립트 내용:

```bash
#!/bin/bash
# USB 장치 경로 찾기 (예: /dev/bus/usb/001/012)
USB_PATH=$(lsusb -d 144d:2b2b | awk '{print "/dev/bus/usb/" $2 "/" $4}' | sed 's/://')

# USB 장치 연결 해제
echo '0' | sudo tee $USB_PATH/authorized

# 5초 대기
sleep 5

# USB 장치 다시 연결
echo '1' | sudo tee $USB_PATH/authorized
```

실행 권한 부여:

```bash
sudo chmod +x /home/user/usb_reconnect.sh
```
# AI 블랙박스 기능
**카메라 관련 라이브러리 설치**
 ```bash
sudo apt-get update
sudo apt-get install python3-opencv
sudo pip3 install opencv-python-headless torch torchvision pillow
sudo pip3 install pandas
```
## 각종 문제 해결 방안

- 라이브러리 설치 실패 시

  ```bash
  --break-system-packages
  ```

- SSH 첫 연결 이후 호스트 변경으로 인한 연결 에러 시

  ```bash
  ssh-keygen -R 0.0.0.0
  ```
# 주의사항
사용자 이름을 경로에 포함할 때는 주의해야 합니다.  
잘못된 사용자 이름 부여는 경로 오류를 유발할 수 있으며,이로 인해 코드가 제대로 실행되지 않을 수 있습니다.


이 설정을 통해 라즈베리파이는 스마트폰에서 재생되는 음악을 받아 스피커로 출력하면서 동시에 이 오디오 데이터를 분석할 수 있는 입력 신호로 사용합니다.  
이 데이터는 FFT를 통해 분석되며, 결과에 따라 연결된 LED 스트립의 색상과 밝기가 실시간으로 변경됩니다,  
이로써 음악에 반응하는 시각적 디스플레이를 제공합니다.
