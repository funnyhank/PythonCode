from pydub import AudioSegment
import speech_recognition as sr


def m4a_to_wav(m4a_path,wav_path):
    audio = AudioSegment.from_file(m4a_path,format="m4a")
    audio.export(wav_path,format="wav")

def recognize_speech(wav_path):
    r =sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
    text = r.recognize_google(audio)
    return text

m4a_path = "C:/Users/funny/Downloads/Music/吴途成 2024-03-26 12-52-54.m4a"
wav_path = "C:/Users/funny/Downloads/Music/out2.wav"

m4a_to_wav(m4a_path,wav_path)
text = recognize_speech(wav_path)
print(text)