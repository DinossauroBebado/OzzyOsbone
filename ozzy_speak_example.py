import pyaudio
import numpy as np

from comSerial import * 
from utils import * 

array = [0,0,0]
booleanos = [0,0]
angulos = [90,90,0,0]

# Configurações do PyAudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024


min_origem = 0
max_origem = 4000
min_destino = 0
max_destino = 180



# Inicializar o PyAudio
audio = pyaudio.PyAudio()



# Abrir o stream de áudio
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

while True:
     data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
     normalized_data = data[0]
     resultado = int(mapear(normalized_data, min_origem, max_origem, min_destino, max_destino))
     angulos = [90,90,0,resultado]
     cordenadas(angulos, booleanos, array)



# Criar a animação
ani = animation.FuncAnimation(fig, animate, init_func=init, blit=True)

# Exibir o gráfico
plt.show()

# Fechar o stream e encerrar o PyAudio
stream.stop_stream()
stream.close()
audio.terminate()
