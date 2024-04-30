## 파일 목록

### `led_spectrum.py`
- **설명**: 이 파일은 LED 스펙트럼을 테스트하기 위한 코드가 작성되어 있습니다.
- **하드웨어 연결**
  - **LED 스트립 설정**
    - `LED_COUNT`: LED 개수 (8x32 매트릭스)
    - `LED_PIN`: GPIO 핀 번호 (예: board.D21)
    - `LED_BRIGHTNESS`: LED 밝기 (0.0에서 1.0 사이)
    - `SAMPLE_RATE`: 오디오 샘플레이트 (48000Hz)
    - `FFT_SIZE`: FFT 크기 (1024)
    - `bands_per_column`: 사용할 열의 수 (32)

### `gyro_led_steering.py`
- **설명**: 자이로스코프 MPU-6050 센서에 따라 방향 지시등을 동작시키는 코드를 포함하고 있습니다.
- **하드웨어 연결**
  - **LED 1 (좌회전 신호)**: 양극 -> Raspberry Pi GPIO pin (예: GPIO 17), 음극 -> 220Ω 저항을 거쳐 Raspberry Pi GND
  - **LED 2 (우회전 신호)**: 양극 -> Raspberry Pi GPIO pin (예: GPIO 27), 음극 -> 220Ω 저항을 거쳐 Raspberry Pi GND

### `main.py`
- **설명**: 이 파일은 위의 내용을 혼합하여 실행시키는 기능을 지니고 있습니다.
