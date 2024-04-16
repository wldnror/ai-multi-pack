import cv2
import time
from ftplib import FTP
import threading

# FTP 서버 정보 설정
ftp_address = 'ftp.yourserver.com'
ftp_username = 'your_username'
ftp_password = 'your_password'
ftp_target_path = '/path/to/upload/'  # FTP 서버 상의 파일 업로드 경로

def upload_file_to_ftp(file_path):
    # FTP 서버에 파일을 업로드하는 함수
    ftp = FTP(ftp_address)
    ftp.login(ftp_username, ftp_password)
    with open(file_path, 'rb') as file:
        ftp.storbinary(f'STOR {ftp_target_path}{file_path}', file)
    ftp.quit()
    print(f"파일 {file_path}가 성공적으로 업로드되었습니다.")

def start_recording(duration=60):
    # 카메라 초기화 및 녹화 설정
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("카메라를 시작할 수 없습니다.")
        return

    output_filename = 'output.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_filename, fourcc, 20.0, (640, 480))

    start_time = time.time()
    while (time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break

    # 자원 해제
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    upload_file_to_ftp(output_filename)  # 녹화가 끝나면 FTP로 파일 업로드

# 사용자로부터 임시 가속도 값을 입력 받음
while True:
    try:
        threshold = int(input("임시 가속도 값을 입력하세요: "))
        break
    except ValueError:
        print("올바른 숫자를 입력하세요.")

print("임시 가속도 값:", threshold)

# 충격 감지 및 녹화, FTP 업로드 코드
while True:
    acceleration = threshold  # 가상 가속도 값 사용
    if abs(acceleration) > abs(threshold):
        print("충격 감지! 녹화 시작")
        
        # 녹화를 백그라운드 스레드로 시작
        recording_thread = threading.Thread(target=start_recording, args=(30,))
        recording_thread.start()

    # 녹화가 백그라운드에서 실행 중이더라도 메인 스레드는 계속해서 동작해야 함
    time.sleep(0.1)
