from comSerial import * 
import time 
import cv2
from utils import * 
import numpy as np
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

class Ozzy_manager():
    def __init__(self) -> None:
        self.rest_pan = 95
        self.rest_tilt_left = 90
        self.rest_tilt_right = 110
        self.close_mouth = 90
        self.close_eye = [0, 0]
        self.open_eye = [1, 1]

        self.angulos = [0, 0, 0, 0]

        self.eye = self.close_eye 

        self.face_x = self.rest_pan
        self.face_y = self.rest_pan
        self.face_y2 = self.rest_pan

        self.last_seen_face_time = 0

        self.person_detected = False 

        # audio variable 
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.min_origem = 0
        self.max_origem = 4000

        self.min_destino = 40   
        self.max_destino = 110
        
        # vision variable 
        self.cap = cv2.VideoCapture(0)
    
    def ozzy_see(self):
        # Processar a imagem para detectar rostos usando MediaPipe
        self.results = mp_face_detection.process(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))
        self.faces = []

        if self.results.detections:
            # Atualizar o tempo da última vez que um rosto foi visto
            self.last_seen_face_time = time.time()

            # Extrair as coordenadas dos rostos detectados
            for detection in self.results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = self.frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                self.faces.append((x, y, w, h))
                
                self.person_detected = h * w > 2700
                cv2.putText(
                    img=self.frame,
                    text=f"{w * h}",
                    org=(0, 100),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                    fontScale=2,
                    color=(0, 255, 0),
                    thickness=3
                )

                if self.person_detected:
                    cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    self.face_x_target = mapear(x, 0, self.largura, self.min_destino, self.max_destino)
                    self.face_y_target = mapear(y, 0, self.altura, self.min_destino, self.max_destino)
                                        
                    cv2.putText(
                        img=self.frame,
                        text="PERSUE",
                        org=(0, 480),
                        fontFace=cv2.FONT_HERSHEY_DUPLEX,
                        fontScale=3.0,
                        color=(125, 246, 55),
                        thickness=3
                    )
                    print("PERSUE")
                    self.face_x = move_to(self.face_x, self.face_x_target, 50)
                    self.face_y = move_to(self.face_y, self.face_y_target, 50)
                    pos = saturate(self.face_y, 180, 0)
                    self.rest_tilt_left = 180 - pos 
                    self.rest_tilt_right = 0 + pos
                    print(self.rest_tilt_right)
                    print(self.rest_tilt_left)
                    self.eye = self.open_eye
                else:
                    cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    self.face_x_target = mapear(x, 0, self.largura, self.min_destino, self.max_destino)
                    self.face_y_target = mapear(y, 0, self.altura, self.min_destino, self.max_destino)
         
        else:
            timer_for_rest = time.time() - self.last_seen_face_time

            cv2.putText(
                img=self.frame,
                text=f" timee:{str(timer_for_rest)}",
                org=(300, 480),
                fontFace=cv2.FONT_HERSHEY_DUPLEX,
                fontScale=1,
                color=(0, 0, 255),
                thickness=3
            )

            if timer_for_rest > 2:
                cv2.putText(
                    img=self.frame,
                    text="REST",
                    org=(0, 480),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                    fontScale=3.0,
                    color=(125, 246, 55),
                    thickness=3
                )
                print("REST")
                # Rest mode 
                self.face_x = self.rest_pan
                self.eye = self.close_eye

    def ozzy_loop(self):
        while True:
            # Ler um frame da captura de vídeo
            self.ret, self.frame = self.cap.read()

            self.altura, self.largura, self.canais = self.frame.shape
            
            # Detectar faces no frame
            self.ozzy_see()

            self.angulos = [self.rest_tilt_left, self.rest_tilt_right, self.face_x, 0]

            cv2.putText(
                img=self.frame,
                text=f"Tilt_left:{self.angulos[0]}:Tilt_right:{self.angulos[1]}Pan:{self.angulos[2]}Mout:{self.angulos[3]}",
                org=(0, 30),
                fontFace=cv2.FONT_HERSHEY_DUPLEX,
                fontScale=1,
                color=(255, 0, 0),
                thickness=3
            )

            # Condição de saída do loop (pressione 'q' para sair)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break

            cordenadas(self.angulos, self.eye, array)

if __name__ == '__main__':
    ozzy = Ozzy_manager()
    ozzy.ozzy_loop()