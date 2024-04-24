import cv2
import time

print("Starting the program...")

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("Set resolution: {}x{}".format(width, height))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (width, height))
print("VideoWriter initialized.")

frame_count = 0
start_time = time.time()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("No frame read from camera.")
            break

        frame_count += 1
        out.write(frame)  
        cv2.imshow('Frame', frame)  

        if cv2.waitKey(10) & 0xFF == ord('q'):  # Wait time increased
            print("Exiting loop by user command.")
            break
except Exception as e:
    print(f"An error occurred: {e}")

elapsed_time = time.time() - start_time
actual_fps = frame_count / elapsed_time
print(f"Actual FPS: {actual_fps}")

cap.release()
out.release()
cv2.destroyAllWindows()
print("Resources released, program ended.")
