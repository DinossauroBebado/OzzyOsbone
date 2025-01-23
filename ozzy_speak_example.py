# import pyaudio
# import numpy as np
# from comSerial import * 
# from utils import * 
# import matplotlib.pyplot as plt

# array = [0, 0, 0]
# booleanos = [0, 0]
# angulos = [90, 90, 0, 0]

# # Configurações do PyAudio
# FORMAT = pyaudio.paInt16
# CHANNELS = 2 
# RATE = 44100
# CHUNK = 8192

# min_origem = -2000
# max_origem = 2000
# min_destino = 0
# max_destino = 180

# # Inicializar o PyAudio
# audio = pyaudio.PyAudio()

# # Abrir o stream de áudio
# # stream = audio.open(format=FORMAT, channels=CHANNELS,
# #                     rate=RATE, input=True,
# #                     input_device_index=8,  # Adjust based on your setup 4 | 6 
# #                     frames_per_buffer=CHUNK)

# stream = audio.open(format=FORMAT,
#                     channels=CHANNELS,
#                     rate=RATE,
#                     input=True,
#                     frames_per_buffer=CHUNK)

# # # List to store normalized data
# normalized_data_list = []

# try:
#     while True:
#         # Read audio data and handle overflow
#         data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
        
#         # Check if data has any elements
#         if data.size > 0:
#             normalized_data = data[0]  # Process the first sample
#             normalized_data_list.append(normalized_data)  # Store normalized data
#             if(normalized_data > max_origem):
#                normalized_data = max_origem

#             if(normalized_data < min_origem):
#                normalized_data = min_origem
            
#             resultado = int(mapear(normalized_data, min_origem, max_origem, min_destino, max_destino))
#             print(resultado)
            
#           #   print(resultado)
#             angulos = [90, 90, 0, resultado]
#             cordenadas(angulos, booleanos, array)
        
# except KeyboardInterrupt:
#     print("Stopping audio stream...")

# finally:
#     # Close the stream and terminate PyAudio
#     stream.stop_stream()
#     stream.close()
#     audio.terminate()
#     print("Audio stream closed.")

# # Plotting the recorded normalized data
# plt.figure(figsize=(10, 5))
# plt.plot(normalized_data_list, color='blue')
# plt.title('Normalized Audio Data')
# plt.xlabel('Samples')
# plt.ylabel('Normalized Value')
# plt.grid()

# # Save the plot to a file
# plt.savefig('normalized_audio_data.png')
# print("Plot saved as normalized_audio_data.png.")


# import pyaudio
# import numpy as np
# import matplotlib.pyplot as plt

# # Use a non-interactive backend
# plt.switch_backend('Agg')

# # Audio configuration
# FORMAT = pyaudio.paInt16
# CHANNELS = 2
# RATE = 44100
# CHUNK = 8192

# # Initialize PyAudio
# audio = pyaudio.PyAudio()

# # Open audio stream
# stream = audio.open(format=FORMAT,
#                     channels=CHANNELS,
#                     rate=RATE,
#                     input=True,
#                     frames_per_buffer=CHUNK)

# # List to store normalized data
# normalized_data_list = []

# try:
#     print("Recording audio... Press Ctrl+C to stop.")
#     while True:
#         # Read audio data
#         data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)

#         # Check if data has any elements
#         if data.size > 0:
#             normalized_data = data[0]  # Process the first sample
#             normalized_data_list.append(normalized_data)  # Store normalized data
# except KeyboardInterrupt:
#     print("Stopping audio stream...")

# finally:
#     # Close the stream and terminate PyAudio
#     stream.stop_stream()
#     stream.close()
#     audio.terminate()
#     print("Audio stream closed.")

# # Plotting the recorded normalized data
# plt.figure(figsize=(10, 5))
# plt.plot(normalized_data_list, color='blue')
# plt.title('Normalized Audio Data')
# plt.xlabel('Samples')
# plt.ylabel('Normalized Value')
# plt.grid()

# # Save the plot to a file
# plt.savefig('normalized_audio_data.png')
# print("Plot saved as normalized_audio_data.png.")

import pyaudio
import numpy as np
from comSerial import * 
from utils import * 
import matplotlib.pyplot as plt

array = [0, 0, 0]
booleanos = [0, 0]
angulos = [90, 90, 0, 0]

# Configurações do PyAudio
FORMAT = pyaudio.paInt16
CHANNELS = 2 
RATE = 44100
CHUNK = 8192

min_origem = -5000
max_origem = 5000
min_destino = 0
max_destino = 180

# Inicializar o PyAudio
audio = pyaudio.PyAudio()

# Abrir o stream de áudio
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

# List to store normalized data
normalized_data_list = []

# Silence detection settings
silence_threshold = 700  # Threshold to consider the sound as silence
silence_duration = 50     # Number of silent samples required to declare silence
silent_samples = 0        # Counter for consecutive silent samples

try:
    while True:
        # Read audio data and handle overflow
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
        
        # Check if data has any elements
        if data.size > 0:
            normalized_data = data[0]  # Process the first sample
            normalized_data_list.append(normalized_data)  # Store normalized data

            # Silence detection: check if current data is below the silence threshold
            if abs(normalized_data) < silence_threshold:
                silent_samples += 1
            else:
                silent_samples = 0  # Reset the counter if sound is detected

            # If enough silent samples are detected, set servo to 0
            if silent_samples >= silence_duration:
                resultado = 0  # Servo output is set to 0 when silence is detected
            else:
                # Perform normal mapping when sound is present
                if normalized_data > max_origem:
                    normalized_data = max_origem
                if normalized_data < min_origem:
                    normalized_data = min_origem

                resultado = int(mapear(normalized_data, min_origem, max_origem, min_destino, max_destino))

            print(resultado)
            angulos = [90, 90, 0, resultado]
            cordenadas(angulos, booleanos, array)

except KeyboardInterrupt:
    print("Stopping audio stream...")

finally:
    # Close the stream and terminate PyAudio
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print("Audio stream closed.")

# Plotting the recorded normalized data
plt.figure(figsize=(10, 5))
plt.plot(normalized_data_list, color='blue')
plt.title('Normalized Audio Data')
plt.xlabel('Samples')
plt.ylabel('Normalized Value')
plt.grid()

# Save the plot to a file
plt.savefig('normalized_audio_data_with_silence.png')
print("Plot saved as normalized_audio_data_with_silence.png.")
