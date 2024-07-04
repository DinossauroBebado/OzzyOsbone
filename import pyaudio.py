import pyaudio

p = pyaudio.PyAudio()

# Lista todos os dispositivos de áudio disponíveis
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}, {info['maxInputChannels']} input channels, {info['maxOutputChannels']} output channels")
