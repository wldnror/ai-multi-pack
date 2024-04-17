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

def record_video(output_filename, duration=60):
    # 카메라 초기화 및 녹화 설정
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("카메라를 시작할 수 없습니다.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, 30.0, (640, 480))

    start_time = time.time()
    while (time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # q 키를 누르면 종료
                break
        else:
            break

    # 자원 해제
    cap.release()
    out.release()
    cv2.destroyAllWindows()

def start_recording():
    global recording_flag
    output_filename = 'output.mp4'
    duration = 60
    record_video(output_filename, duration)
    if recording_flag:
        # FTP로 파일 전송
        upload_file_to_ftp(output_filename)

def keyboard_listener():
    global recording_flag
    while True:
        key = input("Press 'r' to start recording or 'q' to quit: ")
        if key == 'r':
            recording_flag = True
            print("Recording started.")
            thread = threading.Thread(target=start_recording)
            thread.start()
        elif key == 'q':
            recording_flag = False
            print("Quitting...")
            break
        else:
            print("Invalid input. Please press 'r' to start recording or 'q' to quit.")

if __name__ == "__main__":
    recording_flag = False
    keyboard_thread = threading.Thread(target=keyboard_listener)
    keyboard_thread.start()
