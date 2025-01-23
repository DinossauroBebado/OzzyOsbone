from comSerial import *
import time
import cv2
from utils import *
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

        self.cont = 0
        self.more_faces = 0

        self.angulos = [0, 0, 0, 0]

        self.eye = self.close_eye

        self.face_x = self.rest_pan
        self.face_y = self.rest_pan
        self.face_y2 = self.rest_pan

        self.last_seen_face_time = 0
        self.person_detected = False

        self.target_face_index = 0  # Para rastrear qual rosto está sendo focado
        self.frame_count = 0  # Contador de frames para alternar entre rostos

        # Variáveis de áudio (não relevantes para a comunicação serial)
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.min_origem = 0
        self.max_origem = 4000

        self.min_destino = 40
        self.max_destino = 110

        # Variáveis de visão
        self.cap = cv2.VideoCapture(0)

        # Variáveis para suavização
        self.smooth_face_x = None
        self.smooth_face_y = None

    def smooth(self, value, prev_value, alpha=0.3):
        return alpha * value + (1 - alpha) * prev_value

    def should_change_focus(self, new_face, current_face, tolerance=30):
        x_diff = abs(new_face[0] - current_face[0])
        y_diff = abs(new_face[1] - current_face[1])
        return x_diff > tolerance or y_diff > tolerance
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/video_feed')
    def video_feed():
        ozzy = OzzyManager()
        return Response(ozzy.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


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
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Bounding box azul

            if len(self.faces) == 1:
                # Quando houver apenas um rosto, foque nele imediatamente
                self.more_faces = 0
                self.target_face_index = 0
                target_face = self.faces[self.target_face_index]
                cv2.rectangle(self.frame, (target_face[0], target_face[1]),
                              (target_face[0] + target_face[2], target_face[1] + target_face[3]), (0, 0, 255), 2)  # Bounding box vermelho
                self.face_x_target = mapear(target_face[0], 0, self.largura, self.min_destino, self.max_destino)
                self.face_y_target = mapear(target_face[1], 0, self.altura, self.min_destino, self.max_destino)

            elif len(self.faces) > 1:
                self.more_faces = 1

                # Alternar entre os rostos detectados a cada 125 frames
                if self.frame_count % 125 == 0:
                    new_target_face_index = (self.target_face_index + 1) % len(self.faces)
                    if self.should_change_focus(self.faces[new_target_face_index], self.faces[self.target_face_index]):
                        self.target_face_index = new_target_face_index

                if self.target_face_index < len(self.faces):
                    target_face = self.faces[self.target_face_index]

                    cv2.rectangle(self.frame, (target_face[0], target_face[1]),
                                  (target_face[0] + target_face[2], target_face[1] + target_face[3]), (0, 0, 255), 2)  # Bounding box vermelho

                    self.face_x_target = mapear(target_face[0], 0, self.largura, self.min_destino, self.max_destino)
                    self.face_y_target = mapear(target_face[1], 0, self.altura, self.min_destino, self.max_destino)

            # Suavização dos movimentos
            if self.smooth_face_x is None:
                self.smooth_face_x = self.face_x_target
                self.smooth_face_y = self.face_y_target
            else:
                self.smooth_face_x = self.smooth(self.face_x_target, self.smooth_face_x, alpha=0.3)
                self.smooth_face_y = self.smooth(self.face_y_target, self.smooth_face_y, alpha=0.3)

            self.face_x = move_to(self.face_x, self.smooth_face_x, 50)
            self.face_y = move_to(self.face_y, self.smooth_face_y, 50)

            pos = saturate(self.face_y, 180, 0)
            self.rest_tilt_right = 180 - pos
            self.rest_tilt_left = 0 + pos

            self.eye = self.open_eye

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

            self.frame_count += 1

        else:
            # Se não houver rostos detectados, entrar no modo de descanso
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
            print("aqui")
            # Ler um frame da captura de vídeo
            self.ret, self.frame = self.cap.read()

            # Verificar se o frame foi capturado corretamente
            if not self.ret:
                print("Falha ao capturar frame")
                continue

            # Rotaciona o frame 180 graus antes do processamento
            self.frame = cv2.rotate(self.frame, cv2.ROTATE_180)

            self.altura, self.largura, self.canais = self.frame.shape

            # Detectar faces no frame
            self.ozzy_see()

            self.angulos = [self.rest_tilt_left, self.rest_tilt_right, self.face_x, 0]
            print(self.angulos)

            # Exibir o frame para visualização
            cv2.imshow("Frame", self.frame)

            # Condição de saída do loop (pressione 'q' para sair)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if self.more_faces > 1:
                if self.cont == 15:
                    cordenadas(self.angulos, self.eye, array)
                    self.cont = 0
                else:
                    self.cont = self.cont + 1
            else:
                cordenadas(self.angulos, self.eye, array)
                self.cont = 0

if __name__ == '__main__':

    # Create threads for audio and video processing
    audio_thread = threading.Thread(target=process_audio)
    video_thread = threading.Thread(target=app.run, kwargs={'debug': True, 'use_reloader': False})

    ozzy = Ozzy_manager()
    print("aqui")
    ozzy.ozzy_loop()
