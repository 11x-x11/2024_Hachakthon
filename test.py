import cv2
import pyaudio
import wave
import threading

# Flag to signal when to stop the threads
stop_threads = threading.Event()

# Audio capture settings
FORMAT = pyaudio.paInt16
CHANNELS = 1  # Mono channel
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 10
AUDIO_OUTPUT_FILENAME = "output_audio.wav"

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open an audio stream
audio_stream = audio.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)

# Function to capture audio
def capture_audio():
    print("Recording audio...")
    frames = []

    while not stop_threads.is_set():
        data = audio_stream.read(CHUNK)
        frames.append(data)

    print("Finished recording audio.")

    # Save the audio file
    wf = wave.open(AUDIO_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Create thread for audio capture
audio_thread = threading.Thread(target=capture_audio)

# Start audio thread
audio_thread.start()

# Video capture settings (run in the main thread)
video_capture = cv2.VideoCapture(0)

# Capture video
while True:
    ret, frame = video_capture.read()
    if ret:
        cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        stop_threads.set()
        break

# Wait for the audio thread to finish
audio_thread.join()

# Release video capture when done
video_capture.release()
cv2.destroyAllWindows()

# Stop and close the audio stream
audio_stream.stop_stream()
audio_stream.close()
audio.terminate()
