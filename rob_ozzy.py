import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import os

from pydub import AudioSegment, effects, playback
import azure.cognitiveservices.speech as speechsdk

# Configuração genai(ia)
genai.configure(api_key="AIzaSyDetqlvGmCYU-hIgX6FEBCMMYW9BlM1Mcc")
# Configurações do microsoft(fala)
subscription_key = '2c065a8b424b4a74bc18bbbbed8d1a71'
region = 'brazilsouth'
# Configuração da fala
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
    audio = AudioSegment.from_file(input_file)

    # Lower the pitch
    lowered_audio = lower_pitch(audio)

    # Check if output file exists and remove it
    output_path = "C:/Users/henri/PycharmProjects/pythonProject2/.venv/output.wav"
    if os.path.exists(output_path):
        os.remove(output_path)

    lowered_audio.export(output_path, format="wav")

def ouvir_microfone():
    # Habilita o microfone para ouvir o usuario
    microfone = sr.Recognizer()
    with sr.Microphone() as source:
        # Chama a funcao de reducao de ruido disponivel na speech_recognition
        microfone.adjust_for_ambient_noise(source)
        # Avisa ao usuario que esta pronto para ouvir
        print("Diga alguma coisa: ")
        # Armazena a informacao de audio na variavel
        audio = microfone.listen(source)
        try:
            # Passa o audio para o reconhecedor de padroes do speech_recognition
            frase = microfone.recognize_google(audio, language='pt-BR')
            # Após alguns segundos, retorna a frase falada
            print("Você disse: " + frase)
            return frase
        except sr.UnknownValueError:
            # Caso nao tenha reconhecido o padrao de fala, exibe esta mensagem
            print("Não entendi o que você disse, por favor tente novamente.")
            return ""
        except sr.RequestError as e:
            # Caso nao consiga se conectar ao serviço do Google
            print("Erro ao se conectar ao serviço do Google; {0}".format(e))
            return ""

def main():
    assistente_falante = True

    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])

    # Configura o contexto inicial para o assistente
    chat.send_message("Sempre que falar comigo, lembre-se você é o Ozzyosbone uma caveira perdida do parque barigui, um vale perdido das capivaras, tem uma personalidade ríspida, informal e meio debochada, mas tem várias histórias pra contar. Agora vc está na RCX uma competição de robótica na campus party em são Paulo, faça piadas sobre a poluição de sao Paulo e a chance de ser roubado, além disso vc odeia rampas e nao usa nenhum emjoi, somente palavras. Por favor, fale comigo usando esse contexto.")

    ### Configura voz
    if assistente_falante:
        engine = pyttsx3.init()

        voices = engine.getProperty('voices')
        engine.setProperty('rate', 200)  # Velocidade 200

        voz = 0
        engine.setProperty('voice', voices[voz].id)

    bem_vindo = "# Bem Vindo ao Assistente Mil Grau com Gemini AI #"
    print("")
    print(len(bem_vindo) * "#")
    print(bem_vindo)
    print(len(bem_vindo) * "#")
    print("###   Digite 'desligar' para encerrar    ###")
    print("")

    while True:
        try:
            texto = ouvir_microfone()
        except Exception as e:
            print(f"Erro ao capturar ou reconhecer áudio: {e}")
            continue

        if texto.lower() == "desligar":
            break

        if texto:
            try:
                response = chat.send_message(texto)
                print("Gemini:", response.text, "\n")

                audio_file = "C:/Users/henri/PycharmProjects/pythonProject2/.venv/input.wav"
                # Certifica-se de que o diretório existe
                os.makedirs(os.path.dirname(audio_file), exist_ok=True)

                # Configuração do áudio para salvar em um arquivo
                audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file)
                # Criar um objeto de síntese de fala
                speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
                # Síntese de fala e salvamento em arquivo
                result = speech_synthesizer.speak_text_async(response.text).get()

                process_audio(audio_file)

                # Tocar o arquivo output.wav
                output_audio = AudioSegment.from_file("C:/Users/henri/PycharmProjects/pythonProject2/.venv/output.wav", format="wav")
                playback.play(output_audio)

            except Exception as e:
                print(f"Erro ao processar resposta do assistente: {e}")
                continue

    print("Encerrando Chat")


print("main")
main()