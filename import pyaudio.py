import pyaudio

# Initialize PyAudio
audio = pyaudio.PyAudio()

# List all audio devices
for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']} (Input Channels: {info['maxInputChannels']})")

# Terminate PyAudio
audio.terminate()