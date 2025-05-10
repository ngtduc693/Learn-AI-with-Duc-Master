import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

speech_config.speech_synthesis_voice_name=os.environ.get('VOICE_NAME')

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

print("Nhập văn bản bạn muốn chuyển đổi thành giọng nói (Tiếng Việt):>")
text = input()

result = speech_synthesizer.speak_text_async(text).get()

if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Đã phát [{}]".format(text))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation = result.cancellation_details
    print("Đã hủy: {}".format(cancellation.reason))
    if cancellation.reason == speechsdk.CancellationReason.Error:
        if cancellation.error_details:
            print("Lỗi: {}".format(cancellation.error_details))