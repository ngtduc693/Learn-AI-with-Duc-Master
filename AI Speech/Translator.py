import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

speech_config = speechsdk.translation.SpeechTranslationConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
speech_config.speech_recognition_language=subscription=os.environ.get('TRANSLATOR_FROM')

to_language = os.environ.get('TRANSLATOR_TO')
speech_config.add_target_language(to_language)

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
recognizer = speechsdk.translation.TranslationRecognizer(translation_config=speech_config, audio_config=audio_config)

print("Nói gì đó vào microphone bằng Tiếng Việt.")
result = recognizer.recognize_once_async().get()

if result.reason == speechsdk.ResultReason.TranslatedSpeech:
    print("Đã nhận dạng: {}".format(result.text))
    print("""Tiếng Anh tương ứng là '{}': {}""".format(
        to_language, 
        result.translations[to_language]))
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("Không nhận dạng được: {}".format(result.no_match_details))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation = result.cancellation_details
    print("Đã hủy: {}".format(cancellation.reason))
    if cancellation.reason == speechsdk.CancellationReason.Error:
        print("Lỗi: {}".format(cancellation.error_details))