#code to test the cinematic 
import time 
from comSerial import * 
from utils import * 
open_eye = [1,1]
angulos = [0,0,90,0]

def move_tilt(pos):
    tilt_motor_cinematic = []
    pos = saturate(pos,180,0)
    left_motor = 180 - pos 
    right_motor = 0 + pos 
    tilt_motor_cinematic = [left_motor,right_motor]
    return tilt_motor_cinematic

def move_roll(pos):
    # 90 meio -> maior gira para direita, menor gira pra esquerda 
    tilt_motor_cinematic = []
    pos = saturate(pos,180,0)

    left_motor =  pos 
    right_motor =  pos 
        
    tilt_motor_cinematic = [left_motor,right_motor]
    return tilt_motor_cinematic

def full_Kinematic(pos_tilt,pos_roll):
    tilt = move_tilt(pos_tilt)
    rool = move_roll(pos_roll)
    left_motor = tilt[0] - rool[0]
    right_motor = tilt[1] + rool[1]
    return [left_motor,right_motor]


for i in range(180):
    tilt_cinematic = move_tilt(i)
    angulos[1] = tilt_cinematic[1]
    angulos[0] =  tilt_cinematic[0]
    time.sleep(0.05)
    print(angulos)
    cordenadas(angulos,open_eye,[0,0,0])

for i in range(180):
    tilt_cinematic = move_roll(i)
    angulos[1] = tilt_cinematic[1]
    angulos[0] =  tilt_cinematic[0]
    time.sleep(0.05)
    print(angulos)
    cordenadas(angulos,open_eye,[0,0,0])

for i in range(180):
    tilt_cinematic = full_Kinematic(i,i)
    angulos[1] = tilt_cinematic[1]
    angulos[0] =  tilt_cinematic[0]
    time.sleep(0.05)
    print(angulos)
    cordenadas(angulos,open_eye,[0,0,0])




