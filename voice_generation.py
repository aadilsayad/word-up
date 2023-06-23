from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient.from_service_account_json('tts_api/careful-hangar-387107-77cf98976c20.json')
with open("data/korean_words.txt", encoding='utf-8') as file:
    word_list = file.readlines()

for word in word_list:
    word = word.strip()
    synthesis_input = texttospeech.SynthesisInput(text=f"{word}")
    voice = texttospeech.VoiceSelectionParams(
        language_code='ko-KR', ssml_gender=texttospeech.SsmlVoiceGender.MALE, name='ko-KR-Neural2-C'
    )

    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=0.75)

    request = texttospeech.SynthesizeSpeechRequest(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    response = client.synthesize_speech(request)

    with open(f"voices/{word}.mp3", 'wb') as out:
        out.write(response.audio_content)