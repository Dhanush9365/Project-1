import speech_recognition as sr

r = sr.Recognizer()

print("🎤 Tamil Voice Test")
print("தமிழில் பேசுங்கள்...")
print("உதாரணம்: லைட்டை ஆன் பண்ணு")

with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source, duration=1)
    audio = r.listen(source)

try:
    text = r.recognize_google(audio, language="ta-IN")
    print("\n✅ Google heard:")
    print(text)

except sr.UnknownValueError:
    print("\n❌ Tamil speech could not be understood")

except sr.RequestError as e:
    print("\n❌ Internet/API error:", e)