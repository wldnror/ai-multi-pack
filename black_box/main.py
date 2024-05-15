# 녹화 상태를 웹소켓으로 전송하는 함수
async def notify_status_change(status):
    global connected_clients
    for client in connected_clients:
        await client.send(status)
        print(f"녹화 상태 전송: {status}")

# 녹화 시작 시 호출
def start_recording(self, output_filename, duration=60):
    self.should_stop = False
    if not self.process:
        command = [
            'ffmpeg',
            '-f', 'v4l2',
            '-framerate', '30',
            '-video_size', '1920x1080',
            '-i', '/dev/video0',
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-crf', '18',
            '-t', str(duration),
            output_filename
        ]
        self.process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
        self.recording_thread = Thread(target=self._monitor_recording)
        self.recording_thread.start()
        asyncio.run(notify_status_change("RECORDING"))

# 녹화 종료 시 호출
def stop_recording(self):
    if self.process:
        self.should_stop = True
        self.recording_thread.join()
        self.process = None
        print("녹화가 종료되었습니다.")
        asyncio.run(notify_status_change("NOT_RECORDING"))
