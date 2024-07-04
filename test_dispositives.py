import pyaudio

p = pyaudio.PyAudio()

# Listar dispositivos de áudio
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print(f"Device {i}: {dev['name']} - {dev['maxInputChannels']} input channels, {dev['maxOutputChannels']} output channels")

p.terminate()
