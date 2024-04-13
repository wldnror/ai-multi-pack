# audio_processing.py
import sounddevice as sd
import numpy as np
import time

SAMPLE_RATE = 44100
FFT_SIZE = 1024

def audio_callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    fft_result = np.abs(np.fft.rfft(indata[:, 0], n=FFT_SIZE))
    fft_result_split = np.array_split(fft_result, 5)
    fft_result_means = [np.mean(part) for part in fft_result_split]
    
    with open('fft_data.txt', 'w') as f:
        for mean in fft_result_means:
            f.write(f"{mean}\n")

def main():
    loopback_device = 'default'
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=FFT_SIZE, device=loopback_device):
        print("Streaming started...")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
