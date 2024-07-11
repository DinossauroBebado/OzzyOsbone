import serial
import time

# # Configurar a porta serial
esp = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=.1)
esp.flush()

def enviar_comando(x):
    esp.write(bytes(x, "utf-8"))
    # time.sleep(0.1)  # Aguarda para dar tempo ao ESP32 para processar
    # if esp.in_waiting > 0:
    #     line = esp.readline().decode('utf-8').rstrip()
    #     print(f'Received from ESP32: {line}')

def range_checker(range_calculo, *args):
    for i, value in enumerate(args):
        if value < range_calculo[i][0] or value > range_calculo[i][1]:
            print(f"Valor {value} fora do intervalo válido {range_calculo[i]}")
            return "invalido"
    return "valido"

def conversao_proporcao(range_calculo, value):
    if value < range_calculo[0] or value > range_calculo[1]:
        raise ValueError("O valor de entrada deve estar no intervalo especificado")
    
    # Calcular a proporção usando interpolação linear
    proportion = 20 + (value - range_calculo[0]) * (130 - 20) / (range_calculo[1] - range_calculo[0])
    inverted = 130 - proportion + 20
    return inverted

def cordenadas(angulos, booleanos, array):

    #recebe tilt_left, tilt_right,pan,mouth  

    range_calibrado = [(0, 180)] * 4  # Intervalo para os ângulos é de 0 a 180 graus
    range_calculo = range_changer(range_calibrado)
     
    angulos = [max(0, min(angulo, 180)) for angulo in angulos]

    if(angulos[3]>100):
        angulos[3] = 100
    if(angulos[3]<58):
        angulos[3] = 58

    if(angulos[2]>120):
        angulos[2] = 120
    if(angulos[2]<60):
        angulos[2] = 60

    if(angulos[1]>170):
        angulos[1] = 170
    if(angulos[1]<10):
        angulos[1] = 10
    
    if(angulos[0]>170):
        angulos[0] = 170
    if(angulos[0]<10):
        angulos[0] = 10
    
    

    # Formatar a mensagem para envio via serial
    msg = ','.join(f'{val:03d}' for val in angulos)
    msg += ',' + ','.join(map(str, booleanos))
    msg += ',' + ','.join(f'{val:03d}' for val in array)
    print(msg)

    enviar_comando(msg)

def range_changer(range_calibrado):
    return range_calibrado

# Exemplo de uso:
array = [255, 255, 255]  # Array com três valores de 0 a 255


# while True:
#     booleanos = [0, 1]  # Dois valores booleanos (0 ou 1)
#     angulos = [0, 00,90, 0]  # Quatro ângulos de 0 a 180 graus
#     cordenadas(angulos, booleanos, array)
#     time.sleep(3)
#     angulos = [00, 00, 90, 85] 
#     cordenadas(angulos, [1, 0], array)
#     time.sleep(3)


