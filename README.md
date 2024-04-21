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
- **PulseAudio**
  -PulseAudio와 상호작용할 수 있는 파이썬 라이브러리
  ```bash
  sudo pip install pulsectl --break-system-packages
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
- **ffmpeg**
  - ffmpeg는 비디오 녹화, 변환 및 스트리밍을 위한 강력한 도구입니다. 라즈베리파이에서 ffmpeg를 사용하여 웹캠을 통한 비디오 녹화를 설정할 수 있습니다.
   ```bash
   sudo apt-get install ffmpeg
   ```

# 루프백 자동화

### 1. 사용자 systemd 디렉터리로 이동:
```bash
mkdir -p ~/.config/systemd/user
```
### 1-2. 서비스 파일 생성:
```bash
nano ~/.config/systemd/user/pulseaudio-modules.service
```
### 1-3. 다음 내용을 파일에 입력합니다:
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

### 1-4. 사용자 서비스 활성화 및 시작:
```bash
systemctl --user enable pulseaudio-modules.service
systemctl --user start pulseaudio-modules.service
```

### 2. 모듈로드

### 2-1
 - 터미널을 열고 rc.local 파일을 편집기로 엽니다. 대부분의 라즈베리파이 시스템에서는 nano 편집기를 사용할 수 있습니다:
   ```bash
   sudo nano /etc/rc.local
   ```
### 2-2
 - 파일을 열면, "exit 0" 이라는 줄 전에 다음과 같은 내용을 추가합니다:
   ```bash
   modprobe snd-aloop
   ```
# AI 블랙박스 기능
**카메라 관련 라이브러리 설치**
 ```bash
sudo apt-get install python3-opencv
```
- 녹화 명령 예제 (파이썬 코드로 활용가능)
```bash
ffmpeg -f v4l2 -framerate 30 -video_size 1920x1080 -i /dev/video0 output.mp4
```

**객체 인식 훈련 데이터 설치**

### YOLOv3 가중치 파일 다운로드
```bash
wget https://pjreddie.com/media/files/yolov3.weights
```
### YOLOv3 구성 파일 다운로드
```bash
wget https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg?raw=true -O yolov3.cfg
```
### YOLOv4 가중치 파일 다운로드
```bash
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4.weights
```
### YOLOv4 구성 파일 다운로드
```bash
wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg
```
### coco.names 파일 다운로드
```bash
wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names -O coco.names
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
