import speech_recognition as sr
# 创建Recognizer对象
recognizer = sr.Recognizer()
# 读取音频文件
with sr.AudioFile("C:/Users/funny/Downloads/Music/吴途成 2024-03-26 12-40-04.wav") as source:
    audio = recognizer.record(source)
    text = recognizer.recognize_google(audio, language='zh-CN')
    print(text)