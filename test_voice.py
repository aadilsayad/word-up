from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient.from_service_account_json('tts_api/____________________________________.json')
synthesis_input = texttospeech.SynthesisInput(text='안녕하세요 저는 말하고 있습니다')
voice = texttospeech.VoiceSelectionParams(
    language_code='ko-KR', ssml_gender=texttospeech.SsmlVoiceGender.MALE, name='ko-KR-Neural2-C'
)
audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

request = texttospeech.SynthesizeSpeechRequest(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

response = client.synthesize_speech(request)

with open('ko_neural2_c_male.mp3', 'wb') as out:
    out.write(response.audio_content)


voices = client.list_voices()
for voice in voices.voices:
    print(f"Name: {voice.name}")
    print(f"Language codes: {voice.language_codes}")
    print(f"SSML gender: {voice.ssml_gender}")
    print()
