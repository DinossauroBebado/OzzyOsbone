from comSerial import * 
import time 
import cv2
from utils import * 


import pyaudio
import numpy as np

def mover(posicao_atual, posicao_desejada, aceleracao):
    # Calcula a diferença entre a posição desejada e a posição atual
    delta_posicao = posicao_desejada - posicao_atual

    # Calcula a nova posição usando a fórmula da cinemática
    nova_posicao = posicao_atual +  delta_posicao*aceleracao
    
    return nova_posicao


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



array = [0,0,0]





# Exemplo: mapear 320 de 0 a 640 para 0 a 180
numero = 320
min_origem = 0
max_origem = 640
min_destino = 0
max_destino = 180

resultado = mapear(numero, min_origem, max_origem, min_destino, max_destino)


# booleanos = [0,0]
# angulos = [0,180,90,0]
# cordenadas(angulos, booleanos, array)
# time.sleep(10)


# booleanos = [1,1]
# angulos = [90,90,90,0]
# cordenadas(angulos, booleanos, array)

# time.sleep(1)


# Carregar o classificador pré-treinado para detecção de faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Inicializar a captura de vídeo da webcam
cap = cv2.VideoCapture(0)
 
while True:
    # Ler um frame da captura de vídeo
    ret, frame = cap.read()

    altura, largura, canais = frame.shape

    #640x480 
    

    # Converter o frame para escala de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar faces no frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
    if len(faces) > 0:
    # Desenhar retângulos ao redor das faces detectadas
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            #add filter or timeout only go to sleep after some time 
            resultado = mapear(x, min_origem, max_origem, min_destino, max_destino)
            booleanos = [1,1]
            angulos = [90,90,int(resultado),0]
    else:
        #add desaceleration 
        resultado = 90
        booleanos = [0,0]
        angulos = [0,180,resultado,0]

    # Mostrar o frame com as faces detectadas
    cv2.imshow('Reconhecimento de Faces', frame)


    print(angulos)


    # Condição de saída do loop(pressione 'q' para sair)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    normalized_data = data[0]
    resultado = int(mapear(normalized_data, min_origem, max_origem, min_destino, max_destino))
    angulos[3] = resultado
    
    cordenadas(angulos, booleanos, array)













