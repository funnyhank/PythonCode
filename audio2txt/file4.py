import deepspeech
# 创建DeepSpeech对象并加载模型
ds = deepspeech.DeepSpeech()
ds.load_model('path/to/model/file')
# 读取音频文件并转换为文本
with open("C:/Users/funny/Downloads/Music/吴途成 2024-03-26 12-40-04.wav", 'rb') as audio_file:
    audio = deepspeech.Audio.from_file(audio_file)
    text = ds.stt(audio)
    print(text)