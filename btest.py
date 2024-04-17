import time
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from ftplib import FTP

# FTP 서버 정보 설정
ftp_address = '79webhard.com'  # "ftp://" 접두사 제거
ftp_username = 'webmaster'
ftp_password = 'your_password'
ftp_target_path = '/home/video/'  # 실제 파일 업로드 경로로 변경

class MockSMBus:
    def __init__(self, bus_number):
        self.value = 0  # 초기 가속도 값은 0

    def write_byte_data(self, addr, reg, value):
        pass

    def read_i2c_block_data(self, addr, reg, length):
        # 현재 설정된 가속도 값 반환
        return [self.value >> 8 & 0xFF, self.value & 0xFF]

    def set_acceleration(self, new_value):
        self.value = new_value  # 새로운 가속도 값 설정

def start_recording(duration=10):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("카메라를 시작할 수 없습니다.")
        return

    # 카메라 화면을 미리 보여줌
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Camera Preview', frame)
        else:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    output_filename = 'output.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4 코덱 사용
    out = cv2.VideoWriter(output_filename, fourcc, 30.0, (4096, 2160))  # 최대 해상도 및 프레임 속도 사용

    # 한글 폰트 설정
    fontpath = "/Library/Fonts/Arial Unicode.ttf"  # 폰트 파일 경로
    font = ImageFont.truetype(fontpath, 20)

    start_time = time.time()
    try:
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if ret:
                # Pillow로 이미지 변환
                img_pil = Image.fromarray(frame)
                draw = ImageDraw.Draw(img_pil)
                draw.text((50, 50), "녹화 중", font=font, fill=(255, 255, 255))
                frame = np.array(img_pil)
                out.write(frame)
            else:
                break
    except Exception as e:
        print(f"예외 발생: {e}")
    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        return output_filename

def upload_file_to_ftp(file_path):
    try:
        ftp = FTP(ftp_address)
        ftp.login(ftp_username, ftp_password)
        with open(file_path, 'rb') as file:
            ftp.storbinary(f'STOR {ftp_target_path}{file_path}', file)
        print(f"파일 {file_path}가 성공적으로 업로드되었습니다.")
    except Exception as e:
        print(f"파일 업로드 중 오류 발생: {e}")
    finally:
        ftp.quit()

# 테스트 실행
if __name__ == "__main__":
    output_file = start_recording(10)
    if output_file:
        upload_file_to_ftp(output_file)
