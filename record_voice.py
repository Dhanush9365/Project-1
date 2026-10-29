import speech_recognition as sr
import serial
import time

# =========================
# ESP32 CONNECTION
# =========================
esp32 = serial.Serial("COM5", 115200, timeout=1)
time.sleep(2)

# =========================
# SPEECH RECOGNITION
# =========================
recognizer = sr.Recognizer()

print("================================")
print("🏠 SMART HOME VOICE ASSISTANT")
print("================================")
print("Commands:")
print("👉 Turn on the light")
print("👉 Turn off the light")
print("👉 Turn on the fan")
print("👉 Turn off the fan")
print("👉 Exit")
print("================================")

while True:

    try:
        with sr.Microphone() as source:

            print("\n🎤 Listening...")

            # Reduce background-noise effect
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=5
            )

        # Convert voice → English text
        command = recognizer.recognize_google(
            audio,
            language="en-IN"
        ).lower()

        print("🗣️ You said:", command)

        # =========================
        # LIGHT ON
        # =========================
        if "turn on the light" in command:
            esp32.write(b"light on\n")
            print("💡 Light is ON")

        # =========================
        # LIGHT OFF
        # =========================
        elif "turn off the light" in command:
            esp32.write(b"light off\n")
            print("💡 Light is OFF")

        # =========================
        # FAN ON
        # =========================
        elif "turn on the fan" in command:
            esp32.write(b"fan on\n")
            print("🌀 Fan is ON")

        # =========================
        # FAN OFF
        # =========================
        elif "turn off the fan" in command:
            esp32.write(b"fan off\n")
            print("🌀 Fan is OFF")

        # =========================
        # EXIT
        # =========================
        elif "exit" in command:
            print("👋 Smart Home Assistant stopped.")
            break

        # =========================
        # UNKNOWN COMMAND
        # =========================
        else:
            print("❓ Command not recognized.")

    except sr.UnknownValueError:
        print("❌ Sorry, I couldn't understand.")

    except sr.RequestError:
        print("❌ Internet connection problem.")

    except sr.WaitTimeoutError:
        print("⏱️ No speech detected.")

    except KeyboardInterrupt:
        print("\n👋 Program stopped.")
        break

# Close serial connection python main.py
esp32.close()