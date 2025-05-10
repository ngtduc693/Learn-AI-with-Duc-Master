import azure.cognitiveservices.speech as speechsdk
import keyboard
import time
import string
import difflib
import json
import os
from dotenv import load_dotenv

load_dotenv()

speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
speech_config.speech_recognition_language = os.environ.get('PRONUNCIATION_ASSESSMENT_LANGUAGE')

reference_text = "Today was a beautiful day. We had a great time taking a long walk outside in the morning. The countryside was in full bloom, yet the air was crisp and cold. Towards the end of the day, clouds came in, forecasting much needed rain."

pron_config = speechsdk.PronunciationAssessmentConfig(
    reference_text=reference_text,
    grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
    granularity=speechsdk.PronunciationAssessmentGranularity.Word,
    enable_miscue=True
)

pron_config.enable_prosody_assessment()

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

pron_config.apply_to(recognizer)

print("Nhấn phím 'S' để bắt đầu ghi âm và 'E' để kết thúc...")

while not keyboard.is_pressed('s'):
    time.sleep(0.1)

print("🔴 Ghi âm đang diễn ra...")

done = False
recognized_words = []
fluency_scores = []
prosody_scores = []

def stop_cb(evt):
    global done
    print("⏹ Ghi âm kết thúc.")
    done = True

def recognized_cb(evt):
    result = evt.result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Bạn đã đọc: {result.text}")
        pron_result = speechsdk.PronunciationAssessmentResult(result)
        print(f"🎯 Độ chính xác: {pron_result.accuracy_score:.2f} \n Độ trôi chảy: {pron_result.fluency_score:.2f} \n Độ hoàn thiện: {pron_result.completeness_score:.2f}, Ngữ điệu: {pron_result.prosody_score:.2f}")
        global recognized_words, fluency_scores, prosody_scores
        recognized_words.extend(pron_result.words)
        fluency_scores.append(pron_result.fluency_score)
        prosody_scores.append(pron_result.prosody_score)

recognizer.recognized.connect(recognized_cb)
recognizer.session_stopped.connect(stop_cb)
recognizer.canceled.connect(stop_cb)

recognizer.start_continuous_recognition()

while not done:
    if keyboard.is_pressed('e'):
        recognizer.stop_continuous_recognition()
    time.sleep(0.1)

reference_words = [w.strip(string.punctuation) for w in reference_text.lower().split()]
spoken_words = [w.word.lower() for w in recognized_words]

diff = difflib.SequenceMatcher(None, reference_words, spoken_words)
final_words = []

for tag, i1, i2, j1, j2 in diff.get_opcodes():
    if tag in ['insert', 'replace']:
        for word in recognized_words[j1:j2]:
            if word.error_type == 'None':
                word._error_type = 'Insertion'
            final_words.append(word)
    if tag in ['delete', 'replace']:
        for word_text in reference_words[i1:i2]:
            word = speechsdk.PronunciationAssessmentWordResult({
                'Word': word_text,
                'PronunciationAssessment': {'ErrorType': 'Omission'}
            })
            final_words.append(word)
    if tag == 'equal':
        final_words += recognized_words[j1:j2]

acc_scores = [w.accuracy_score for w in final_words if w.error_type != 'Insertion']
accuracy_score = sum(acc_scores) / len(acc_scores) if acc_scores else 0
fluency_score = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0
prosody_score = sum(prosody_scores) / len(prosody_scores) if prosody_scores else 0
completeness_score = len([w for w in recognized_words if w.error_type == "None"]) / len(reference_words) * 100
completeness_score = min(completeness_score, 100)

pron_score = accuracy_score * 0.4 + prosody_score * 0.2 + fluency_score * 0.2 + completeness_score * 0.2

print(f"\n🔎 Đánh giá toàn đoạn:")
print(f"    Tổng điểm phát âm: {pron_score:.2f}")
print(f"    Độ chính xác: {accuracy_score:.2f}, Độ hoàn thiện: {completeness_score:.2f}, Độ trôi chảy: {fluency_score:.2f}, Ngữ điệu: {prosody_score:.2f}")
