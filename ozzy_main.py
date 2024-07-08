from comSerial import * 
import time 
import cv2
from utils import * 

import threading

import pyaudio
import numpy as np

from rob_ozzy import * 


def ozzy_mind():
    print("run thread")
    main()

class Ozzy_manager():
    def __init__(self) -> None:

        self.rest_pan = 90 
        self.rest_tilt_left = 90
        self.rest_tilt_right = 90 
        self.close_mouth = 80 
        self.close_eye = [0,0]
        self.open_eye = [1,1]

        self.angulos = [0,0,0,0]

        self.eye =  self.close_eye 

        self.face_x = self.rest_pan

        self.last_seen_face_time = 0  # Initialize last seen face time

        self.person_detected = False 
        # audio variable 

        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.min_origem = 0
        self.max_origem = 4000

        self.min_destino = 0    
        self.max_destino = 180
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                    rate=self.RATE, input=True,
                    frames_per_buffer=self.CHUNK)
        

        # vision variable 
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)

    


    def ozzy_see(self):
          
        # see the face and make ozzy look at it 
        self.faces = self.face_cascade.detectMultiScale(self.gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

        # detect if there are any faces 
        if len(self.faces) > 0:
            # Update last seen face time
            self.last_seen_face_time = time.time()

            # Persue mode 
            for (x, y, w, h) in self.faces:

                self.person_detected = h*w>5000
                cv2.putText(
                img = self.frame,
                text = f"{w*h}",
                org = (0, 100),
                fontFace = cv2.FONT_HERSHEY_DUPLEX,
                fontScale = 2,
                color = (0,255,  0),
                thickness = 3)

                if(self.person_detected):
                    cv2.rectangle(self.frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    self.face_x_target = mapear(x, 0, self.largura, self.min_destino, self.max_destino)
                    cv2.putText(
                    img = self.frame,
                    text = "PERSUE",
                    org = (0, 480),
                    fontFace = cv2.FONT_HERSHEY_DUPLEX,
                    fontScale = 3.0,
                    color = (125, 246, 55),
                    thickness = 3)
                    print("PERSUE")
                    self.face_x = move_to(self.face_x,self.face_x_target,50)
                    # self.face_x = self.face_x_current
                    self.eye = self.open_eye
                else:
                    cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    self.face_x_target = mapear(x, 0, self.largura, self.min_destino, self.max_destino)
         
        else:
            # Check if it's been 5 seconds since last seen face
            timer_for_rest = time.time() - self.last_seen_face_time

            cv2.putText(
                img = self.frame,
                text =  f" timee:{str(timer_for_rest)}",
                org = (300, 480),
                fontFace = cv2.FONT_HERSHEY_DUPLEX,
                fontScale = 1,
                color = (0, 0, 255),
                thickness = 3
                )



            if timer_for_rest > 2:
                cv2.putText(
                img = self.frame,
                text = "REST",
                org = (0, 480),
                fontFace = cv2.FONT_HERSHEY_DUPLEX,
                fontScale = 3.0,
                color = (125, 246, 55),
                thickness = 3
                )
                print("REST")
                # Rest mode 
                self.face_x = self.rest_pan
                self.eye = self.close_eye

           


    def ozzy_speak(self):
        #get the volume from the chatbot and make the mouth move 

        data = np.frombuffer(self.stream.read(self.CHUNK), dtype=np.int16)
        system_volume = data[0]
        self.mouth_porcentagem_opem = int(mapear(system_volume, self.min_origem, self.max_origem, self.min_destino, self.max_destino))



    
    def ozzy_loop(self):
        while True:
            # Ler um frame da captura de vídeo

            self.ret, self.frame = self.cap.read()

            self.altura, self.largura, self.canais = self.frame.shape

            #640x480 
            

            # Converter o frame para escala de cinza
            self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

            # Detectar faces no frame
            self.ozzy_see()

            self.ozzy_speak()

            self.angulos = [self.rest_tilt_left,self.rest_tilt_right,self.face_x,self.mouth_porcentagem_opem]

            cv2.putText(
                img = self.frame,
                text = f"Tilt_left:{self.angulos[0]}:Tilt_right:{self.angulos[1]}Pan:{self.angulos[2]}Mout:{self.angulos[3]}",
                org = (0, 30),
                fontFace = cv2.FONT_HERSHEY_DUPLEX,
                fontScale = 1,
                color = (255, 0, 0),
                thickness = 3)

          

            # Mostrar o frame com as faces detectadas
            cv2.imshow('Reconhecimento de Faces', self.frame)


            # print(self.angulos)


            # Condição de saída do loop(pressione 'q' para sair)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    
            
            cordenadas(self.angulos, self.eye, array)


if __name__ == '__main__':
    ozzy = Ozzy_manager()
    x = threading.Thread(target=ozzy_mind)
    x.start()

    ozzy.ozzy_loop()
