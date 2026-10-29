import speech_recognition as sr
import serial
import time
import sounddevice as sd

# =========================================================
# SMART HOME VOICE ASSISTANT
# ESP32 + COM5
# =========================================================

PORT = "COM5"
BAUD_RATE = 115200

SAMPLE_RATE = 16000
RECORD_SECONDS = 5

# ---------------------------------------------------------
# CONNECT TO ESP32
# ---------------------------------------------------------

try:
    esp32 = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("ESP32 connected successfully!")

except Exception as e:
    print("ESP32 connection failed.")
    print("Check that the ESP32 is connected to COM5.")
    print("Error:", e)
    raise SystemExit

# ---------------------------------------------------------
# SPEECH RECOGNITION
# ---------------------------------------------------------

recognizer = sr.Recognizer()

print()
print("==========================================")
print("       SMART HOME VOICE ASSISTANT")
print("==========================================")
print("Commands:")
print("  Turn on the light")
print("  Turn off the light")
print("  Turn on the fan")
print("  Turn off the fan")
print("  Exit")
print("==========================================")

# ---------------------------------------------------------
# RECORD FROM MICROPHONE
# This uses sounddevice, so PyAudio is NOT required.
# ---------------------------------------------------------

def listen_from_microphone():
    print("\nListening...")

    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    audio_bytes = audio.tobytes()

    return sr.AudioData(
        audio_bytes,
        SAMPLE_RATE,
        2
    )

# ---------------------------------------------------------
# SEND COMMAND TO ESP32
# ---------------------------------------------------------

def send_command(command):
    esp32.write((command + "\n").encode())
    print("Sent to ESP32:", command)

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------

while True:

    try:
        audio = listen_from_microphone()

        try:
            command = recognizer.recognize_google(audio)
            command = command.lower().strip()

            print("You said:", command)

        except sr.UnknownValueError:
            print("Sorry, I could not understand.")
            continue

        except sr.RequestError as e:
            print("Speech recognition/internet error:", e)
            continue

        # ---------------- LIGHT ----------------

        if "turn on the light" in command or "light on" in command:
            print("LIGHT -> ON")
            send_command("light on")

        elif "turn off the light" in command or "light off" in command:
            print("LIGHT -> OFF")
            send_command("light off")

        # ---------------- FAN ----------------

        elif "turn on the fan" in command or "fan on" in command:
            print("FAN -> ON")
            send_command("fan on")

        elif "turn off the fan" in command or "fan off" in command:
            print("FAN -> OFF")
            send_command("fan off")

        # ---------------- EXIT ----------------

        elif "exit" in command or "stop" in command:
            print("Stopping Smart Home Voice Assistant...")
            send_command("all off")
            break

        else:
            print("Command not recognized.")

    except KeyboardInterrupt:
        print("\nProgram stopped.")
        break

    except Exception as e:
        print("Error:", e)

# ---------------------------------------------------------
# CLOSE ESP32
# ---------------------------------------------------------

if esp32.is_open:
    esp32.close()

print("ESP32 connection closed.")
print("Smart Home Voice Assistant stopped.")
