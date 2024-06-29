# import serial
import time
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os
import pydub

# not beeing used 


# Configuração da porta serial
# ser = serial.Serial('COM3', baudrate=115200, timeout=0.1)

def reproduzir_texto_e_mover(texto):
    # Gerar áudio a partir do texto usando a API TTS
    tts = gTTS(text=texto, lang='pt')
    tts.save('temp_audio.mp3')  # Salvar o áudio temporariamente

    # Converter o áudio para WAV (necessário para algumas plataformas)
    audio = AudioSegment.from_mp3('temp_audio.mp3')
    audio.export('temp_audio.wav', format='wav')

    # Reproduzir o áudio
    play(AudioSegment.from_file('temp_audio.wav'))

    # Calcular o ângulo da mandíbula com base no texto
    angulo = calcular_angulo(texto)
    
    # Enviar comando para mover o servo
    enviar_comando(angulo)

    # Aguardar um momento para sincronização
    time.sleep(0.5)

def enviar_comando(angulo):
    comando = f"0,0,0,{angulo},0,0,0,0,0"
    print(comando)
    # ser.write(comando.encode())
    time.sleep(0.1)

def calcular_angulo(texto):
    # Aqui você pode implementar a lógica para calcular o ângulo da mandíbula com base no texto
    # Exemplo simples: retorna um ângulo fixo para demonstração
    return 45

# Exemplo de frases (você deve ajustar conforme necessário)
frases = [
    'Olá, tudo bem?',
    'Como posso te ajudar hoje?'
]

# Chama a função para reproduzir texto e mover a mandíbula
for frase in frases:
    reproduzir_texto_e_mover(frase)

# Fechar a porta serial no final do uso
# ser.close()

# Remover arquivos temporários gerados
os.remove('temp_audio.mp3')
os.remove('temp_audio.wav')
