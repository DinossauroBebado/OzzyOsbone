import pyaudio
import numpy as np
import cv2
import mediapipe as mp
import threading
from comSerial import *
from utils import *
import matplotlib.pyplot as plt
from flask import Flask, render_template, Response
import time

# Flask setup for video feed
app = Flask(__name__)

# Ajustar a confiança mínima para aumentar a sensibilidade
mp_face_detection = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.1)

# Global variables
array = [0, 0, 0]
booleanos = [1, 1]
angulos = [90, 90, 0, 0]  # Angles for the servos (shared by both threads)
lock = threading.Lock()  # Lock for synchronizing access to angulos

# PyAudio settings
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 8192

min_origem = -5000
max_origem = 5000
min_destino = 30
max_destino = 159

# Face detection class
class OzzyManager:
    def __init__(self):
        self.rest_pan = 95
        self.rest_tilt_left = 90
        self.rest_tilt_right = 110
        self.close_mouth = 90
        self.close_eye = [0, 0]
        self.open_eye = [1, 1]

        self.cont = 0
        self.more_faces = 0
        self.target_face_index = 0
        self.frame_count = 0
        self.last_seen_face_time = 0

        self.eye = self.close_eye
        self.face_x = self.rest_pan
        self.face_y = self.rest_pan
        self.smooth_face_x = None
        self.smooth_face_y = None

        self.cap = cv2.VideoCapture(0)

    def smooth(self, value, prev_value, alpha=0.3):
        return alpha * value + (1 - alpha) * prev_value

    def should_change_focus(self, new_face, current_face, tolerance=30):
        x_diff = abs(new_face[0] - current_face[0])
        y_diff = abs(new_face[1] - current_face[1])
        return x_diff > tolerance or y_diff > tolerance

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture frame")
            return None

        # Rotate the frame 180 degrees
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        height, width, _ = frame.shape
        results = mp_face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        faces = []

        if results.detections:
            self.last_seen_face_time = time.time()
            for detection in results.detections:
                # Reduzir a confiança mínima para permitir mais detecções
                if detection.score[0] < 0.75:
                    continue

                bboxC = detection.location_data.relative_bounding_box
                x = int(bboxC.xmin * width)
                y = int(bboxC.ymin * height)
                w = int(bboxC.width * width)
                h = int(bboxC.height * height)

                # Reduzir o tamanho mínimo para detectar rostos menores
                if w < 30 or h < 30:  # Detectar rostos menores ajustando os limites mínimos
                    continue

                faces.append((x, y, w, h))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            if len(faces) > 0:
                self.handle_faces(frame, faces)
        else:
            self.handle_no_faces(frame)

        return frame

    def handle_faces(self, frame, faces):
        if len(faces) == 1:
            self.more_faces = 0
            self.target_face_index = 0
        else:
            self.more_faces = 1

        # Alternar entre os rostos detectados a cada 125 frames
        if self.frame_count % 125 == 0:
            new_target_face_index = (self.target_face_index + 1) % len(faces)
            if self.should_change_focus(faces[new_target_face_index], faces[self.target_face_index]):
                self.target_face_index = new_target_face_index

        if self.target_face_index < len(faces):
            target_face = faces[self.target_face_index]
            cv2.rectangle(frame, (target_face[0], target_face[1]), (target_face[0] + target_face[2], target_face[1] + target_face[3]), (0, 0, 255), 2)
            self.update_face_position(target_face)
            self.frame_count += 1

    def update_face_position(self, target_face):
        # Update face position for servos
        self.face_x_target = self.map_to_range(target_face[0], 0, self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), 40, 110)
        self.face_y_target = self.map_to_range(target_face[1], 0, self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT), 40, 110)

        if self.smooth_face_x is None:
            self.smooth_face_x = self.face_x_target
            self.smooth_face_y = self.face_y_target
        else:
            self.smooth_face_x = self.smooth(self.face_x_target, self.smooth_face_x)
            self.smooth_face_y = self.smooth(self.face_y_target, self.smooth_face_y)

        self.face_x = self.move_to(self.face_x, self.smooth_face_x, 50)
        self.face_y = self.move_to(self.face_y, self.smooth_face_y, 50)

        # Limitar a posição y
        pos = saturate(self.face_y, 180, 0)

        # Ajustar as variáveis de inclinação dos servos com base na posição y
        self.rest_tilt_right = 180 - pos
        self.rest_tilt_left = 0 + pos

        with lock:
            angulos[0] = int(self.rest_tilt_left)
            angulos[1] = int(self.rest_tilt_right)
            angulos[2] = int(self.face_x)
            angulos[3] = int(self.face_y)  # Atualizar o ângulo y

    def handle_no_faces(self, frame):
        timer_for_rest = time.time() - self.last_seen_face_time
        cv2.putText(frame, f"time: {timer_for_rest:.2f}", (300, 480), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 3)

    @staticmethod
    def map_to_range(value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    @staticmethod
    def move_to(current, target, step):
        if current < target:
            return min(current + step, target)
        return max(current - step, target)

    def generate_frames(self):
        while True:
            frame = self.process_frame()
            if frame is None:
                continue

            _, buffer = cv2.imencode('.jpg', frame)
            current_frame = buffer.tobytes()

            # Enviar ângulos para as coordenadas
            with lock:
                cordenadas(angulos, booleanos, array)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    ozzy = OzzyManager()
    return Response(ozzy.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Audio processing function
def process_audio():
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, frames_per_buffer=CHUNK)

    silence_threshold = 700
    silence_duration = 50
    silent_samples = 0

    try:
        while True:
            data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)

            if data.size > 0:
                normalized_data = data[0]

                # Detecção de silêncio
                if abs(normalized_data) < silence_threshold:
                    silent_samples += 1
                else:
                    silent_samples = 0

                if silent_samples >= silence_duration:
                    resultado = 0
                else:
                    resultado = int(mapear(normalized_data, min_origem, max_origem, min_destino, max_destino))

                with lock:
                    angulos[3] = resultado  # Atualizar o quarto ângulo

    except KeyboardInterrupt:
        print("Stopping audio stream...")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

# Main execution with threading
if __name__ == '__main__':
    audio_thread = threading.Thread(target=process_audio)
    video_thread = threading.Thread(target=app.run, kwargs={'debug': True, 'use_reloader': False})

    audio_thread.start()
    video_thread.start()

    audio_thread.join()
    video_thread.join()
