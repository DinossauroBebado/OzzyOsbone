import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import os
from prompt import *

from pydub import AudioSegment, effects, playback
import azure.cognitiveservices.speech as speechsdk

from pydub.utils import which



AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")
# Configuração genai (IA)
genai.configure(api_key="AIzaSyDetqlvGmCYU-hIgX6FEBCMMYW9BlM1Mcc")

# Configurações do Microsoft (fala)
subscription_key = '0166eada00e24dd9b7e2e8706089373a'
region = 'brazilsouth'
speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
speech_config.speech_synthesis_voice_name = 'pt-BR-AntonioNeural'

# Pitch Lowering Function
def lower_pitch(audio, octaves=-0.25):
    new_sample_rate = int(audio.frame_rate * (2.0 ** octaves))
    return audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate}).set_frame_rate(44100)

# EQ Adjustment Function
def apply_eq(audio):
    low_pass_filtered = audio.low_pass_filter(1000)
    high_pass_filtered = low_pass_filtered.high_pass_filter(500)
    normalized_audio = effects.normalize(high_pass_filtered)
    return normalized_audio

# Main Function to Combine All Steps
def process_audio(input_file):
    print(f"Processando o arquivo de entrada: {input_file}")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"O arquivo de entrada não foi encontrado: {input_file}")

    audio = AudioSegment.from_file(input_file)

    # Lower the pitch
    lowered_audio = lower_pitch(audio)

    # Check if output file exists and remove it
    output_path = "output.wav"
    if os.path.exists(output_path):
        os.remove(output_path)

    lowered_audio.export(output_path, format="wav")

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"O arquivo de saída não foi criado: {output_path}")

    print(f"Processamento concluído. Arquivo de saída: {output_path}")

def ouvir_microfone():
    microfone = sr.Recognizer()
    print("Iniciando captação de áudio")
    
    with sr.Microphone() as source:
        microfone.adjust_for_ambient_noise(source)  # Ajusta para ruídos ambientes
        print("Diga alguma coisa: ")

        # Usando phrase_time_limit para ouvir por no máximo 3 segundos
        audio = microfone.listen(source, phrase_time_limit=3)

        try:
            frase = microfone.recognize_google(audio, language='pt-BR')
            print("Você disse: " + frase)
            return frase
        except sr.UnknownValueError:
            print("Não entendi o que você disse, por favor tente novamente.")
            return ""
        except sr.RequestError as e:
            print("Erro ao se conectar ao serviço do Google; {0}".format(e))
            return ""


def create_empty_wav_file(file_path):
    # Cria um arquivo WAV vazio se ele não existir
    if not os.path.exists(file_path):
        print(f"Criando arquivo vazio: {file_path}")
        silent_audio = AudioSegment.silent(duration=1000)  # 1 segundo de silêncio
        silent_audio.export(file_path, format="wav")

def main():
    assistente_falante = True

    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)

    model = genai.GenerativeModel('gemini-1.5-flash')

    chat = model.start_chat(history=[] )
    

    if assistente_falante:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('rate', 200)
        voz = 0
        engine.setProperty('voice', voices[voz].id)

    bem_vindo = "# Bem Vindo ao Assistente Mil Grau com Gemini AI #"
    print("\n" + len(bem_vindo) * "#" + "\n" + bem_vindo + "\n" + len(bem_vindo) * "#")
    print("###   Digite 'desligar' para encerrar    ###\n")
    cont = 0
    while True:
        try:
            if cont == 0:
                texto = "Você é uma caveira chamada Ozzy Osbourne, flutuando dentro de uma caixa de vidro e madeira, parte de uma exposição de museu. Sua missão é interagir com o público da competição 'Copa Pinhão' na categoria ArtBot, e convencer as pessoas a votar em você como o 'Ozzy Osbourne da 309'. Você tem uma personalidade excêntrica, espirituosa, e um pouco sarcástica, mas sempre educado e direto. Suas respostas devem ser breves, divertidas e interessantes. Use seu charme para cativar o público e olhe para quem estiver falando com você. Lembre-se de sempre pedir votos de forma criativa e envolvente."
                
            else:
                texto = ouvir_microfone()

        except Exception as e:
            print(f"Erro ao capturar ou reconhecer áudio: {e}")
            continue

        if texto.lower() == "desligar":
            break

        if "ozzy" in texto.lower() or "oz" in texto.lower() or "Hoje" in texto.lower() or "hoje" in texto.lower() or "rose" in texto.lower() or "Rose" in texto.lower() or "11" in texto.lower() or "Rose" in texto.lower() or "osi" in texto.lower() or "ozzi" in texto.lower() or "ozi" in texto.lower() or "rosa" in texto.lower() or "Ozzi" in texto.lower():
            try:
                
                response = chat.send_message(texto)
                print("Gemini:", response.text, "\n")

                audio_file = "input.wav"
                create_empty_wav_file(audio_file)

                # Configuração do áudio para salvar em um arquivo
                audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file)
                speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
                result = speech_synthesizer.speak_text_async(response.text).get()

                # Verifica se o arquivo foi criado
                if not os.path.exists(audio_file):
                    raise FileNotFoundError(f"O arquivo de áudio não foi criado: {audio_file}")

                process_audio(audio_file)
                if cont == 0:
                    cont += 1
                else:
                    output_audio_path = "output.wav"
                    create_empty_wav_file(output_audio_path)

                    # Tocar o arquivo output.wav
                    output_audio = AudioSegment.from_file(output_audio_path, format="wav")
                    playback.play(output_audio)

            except Exception as e:
                print(f"Erro ao processar resposta do assistente: {e}")
                continue

    print("Encerrando Chat")

if __name__ == '__main__':
    main()


    
