import tkinter as tk
from tkinter import messagebox
import threading
import time
import serial
import sounddevice as sd
import numpy as np
import speech_recognition as sr


# ============================================================
# ESP32 SETTINGS
# ============================================================

PORT = "COM5"
BAUD_RATE = 115200

esp32 = None

try:
    esp32 = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("ESP32 connected on", PORT)
except Exception as e:
    print("ESP32 not connected:", e)


# ============================================================
# WINDOW
# ============================================================

root = tk.Tk()
root.title("Smart Home Voice Control")
root.geometry("1250x760")
root.minsize(1100, 700)
root.configure(bg="#10141c")


# ============================================================
# STATES
# ============================================================

light_on = False
fan_on = False
fan_angle = 0
listening = False


# ============================================================
# COLORS
# ============================================================

ROOM_DARK = "#202633"
ROOM_LIGHT = "#4a4d43"

FLOOR_DARK = "#302821"
FLOOR_LIGHT = "#63513d"

PANEL = "#151a23"
PANEL2 = "#1c2330"

TEXT = "#f5f5f5"
MUTED = "#9da7b5"

GREEN = "#39d98a"
RED = "#ff5c5c"
YELLOW = "#ffd45a"
BLUE = "#4da6ff"


# ============================================================
# MAIN LAYOUT
# ============================================================

main = tk.Frame(root, bg="#10141c")
main.pack(fill="both", expand=True)

scene_frame = tk.Frame(main, bg="#10141c")
scene_frame.pack(side="left", fill="both", expand=True)

control_frame = tk.Frame(
    main,
    width=300,
    bg=PANEL
)
control_frame.pack(side="right", fill="y")
control_frame.pack_propagate(False)


# ============================================================
# CANVAS
# ============================================================

canvas = tk.Canvas(
    scene_frame,
    bg=ROOM_DARK,
    highlightthickness=0
)

canvas.pack(fill="both", expand=True)


# ============================================================
# DRAW ROOM
# ============================================================

def draw_room():

    canvas.delete("room")

    w = canvas.winfo_width()
    h = canvas.winfo_height()

    if w < 500:
        w = 900

    if h < 500:
        h = 650

    # --------------------------------------------------------
    # WALL
    # --------------------------------------------------------

    wall_color = ROOM_LIGHT if light_on else ROOM_DARK

    canvas.create_rectangle(
        0, 0, w, h * 0.68,
        fill=wall_color,
        outline="",
        tags="room"
    )

    # wall panels
    for y in range(0, int(h * 0.68), 40):
        canvas.create_line(
            0, y, w, y,
            fill="#ffffff" if light_on else "#272d39",
            width=1,
            tags="room"
        )

    # --------------------------------------------------------
    # FLOOR
    # --------------------------------------------------------

    floor_color = FLOOR_LIGHT if light_on else FLOOR_DARK

    canvas.create_polygon(
        0, h * 0.68,
        w, h * 0.68,
        w, h,
        0, h,
        fill=floor_color,
        outline="",
        tags="room"
    )

    # floor lines
    for x in range(-w, w * 2, 80):
        canvas.create_line(
            w / 2,
            h * 0.68,
            x,
            h,
            fill="#6a5845" if light_on else "#40352d",
            tags="room"
        )

    # --------------------------------------------------------
    # WINDOW
    # --------------------------------------------------------

    wx = w * 0.10
    wy = h * 0.18
    ww = w * 0.22
    wh = h * 0.30

    canvas.create_rectangle(
        wx, wy,
        wx + ww, wy + wh,
        fill="#101b2c",
        outline="#d7dbe2",
        width=7,
        tags="room"
    )

    # sky
    canvas.create_rectangle(
        wx + 8, wy + 8,
        wx + ww - 8, wy + wh - 8,
        fill="#162d49" if not light_on else "#6fa9d8",
        outline="",
        tags="room"
    )

    # window cross
    canvas.create_line(
        wx + ww / 2, wy,
        wx + ww / 2, wy + wh,
        fill="#d7dbe2",
        width=5,
        tags="room"
    )

    canvas.create_line(
        wx, wy + wh / 2,
        wx + ww, wy + wh / 2,
        fill="#d7dbe2",
        width=5,
        tags="room"
    )

    # moon
    if not light_on:
        canvas.create_oval(
            wx + ww * 0.65,
            wy + wh * 0.18,
            wx + ww * 0.65 + 30,
            wy + wh * 0.18 + 30,
            fill="#eeeeaa",
            outline="",
            tags="room"
        )

    # --------------------------------------------------------
    # TV
    # --------------------------------------------------------

    tvx = w * 0.63
    tvy = h * 0.20
    tvw = w * 0.25
    tvh = h * 0.22

    canvas.create_rectangle(
        tvx, tvy,
        tvx + tvw, tvy + tvh,
        fill="#090b0f",
        outline="#555b65",
        width=5,
        tags="room"
    )

    canvas.create_rectangle(
        tvx + 12, tvy + 12,
        tvx + tvw - 12, tvy + tvh - 12,
        fill="#18283d",
        outline="",
        tags="room"
    )

    # TV stand
    canvas.create_rectangle(
        tvx + tvw * 0.35,
        tvy + tvh,
        tvx + tvw * 0.65,
        tvy + tvh + 20,
        fill="#15171b",
        outline="",
        tags="room"
    )

    # --------------------------------------------------------
    # SOFA
    # --------------------------------------------------------

    sx = w * 0.12
    sy = h * 0.62
    sw = w * 0.42
    sh = h * 0.20

    # sofa body
    canvas.create_rectangle(
        sx, sy,
        sx + sw, sy + sh,
        fill="#45515e",
        outline="#697786",
        width=3,
        tags="room"
    )

    # sofa back
    canvas.create_rectangle(
        sx + 15, sy - 65,
        sx + sw - 15, sy + 20,
        fill="#53616e",
        outline="#697786",
        width=3,
        tags="room"
    )

    # cushions
    canvas.create_rectangle(
        sx + 30, sy - 45,
        sx + sw * 0.48,
        sy + 5,
        fill="#687683",
        outline="",
        tags="room"
    )

    canvas.create_rectangle(
        sx + sw * 0.52,
        sy - 45,
        sx + sw - 30,
        sy + 5,
        fill="#687683",
        outline="",
        tags="room"
    )

    # sofa legs
    canvas.create_rectangle(
        sx + 20, sy + sh,
        sx + 40, sy + sh + 25,
        fill="#16191d",
        outline="",
        tags="room"
    )

    canvas.create_rectangle(
        sx + sw - 40, sy + sh,
        sx + sw - 20, sy + sh + 25,
        fill="#16191d",
        outline="",
        tags="room"
    )

    # --------------------------------------------------------
    # COFFEE TABLE
    # --------------------------------------------------------

    tx = w * 0.43
    ty = h * 0.79
    tw = w * 0.20

    canvas.create_oval(
        tx, ty,
        tx + tw, ty + 45,
        fill="#704f35",
        outline="#98704d",
        width=3,
        tags="room"
    )

    canvas.create_line(
        tx + tw * 0.2,
        ty + 35,
        tx + tw * 0.1,
        ty + 90,
        fill="#3a271b",
        width=7,
        tags="room"
    )

    canvas.create_line(
        tx + tw * 0.8,
        ty + 35,
        tx + tw * 0.9,
        ty + 90,
        fill="#3a271b",
        width=7,
        tags="room"
    )

    # coffee cup
    canvas.create_oval(
        tx + tw * 0.42,
        ty + 10,
        tx + tw * 0.57,
        ty + 25,
        fill="#eeeeee",
        outline="",
        tags="room"
    )

    # --------------------------------------------------------
    # PLANT
    # --------------------------------------------------------

    px = w * 0.84
    py = h * 0.67

    canvas.create_rectangle(
        px,
        py,
        px + 55,
        py + 75,
        fill="#9b5d38",
        outline="",
        tags="room"
    )

    for dx, dy in [
        (0, -70),
        (-25, -50),
        (25, -55),
        (-35, -25),
        (35, -30)
    ]:
        canvas.create_oval(
            px + 27 + dx,
            py + dy,
            px + 50 + dx,
            py + 15 + dy,
            fill="#3c8c57",
            outline="",
            tags="room"
        )

    # --------------------------------------------------------
    # RUG
    # --------------------------------------------------------

    canvas.create_oval(
        w * 0.30,
        h * 0.78,
        w * 0.68,
        h * 0.96,
        fill="#37404b",
        outline="#606b78",
        width=3,
        tags="room"
    )

    # --------------------------------------------------------
    # CEILING LIGHT
    # --------------------------------------------------------

    light_x = w * 0.50
    light_y = h * 0.09

    if light_on:

        # simulated glow
        for r, color in [
            (150, "#4e4931"),
            (120, "#686039"),
            (95, "#8b7c42"),
            (70, "#b29b4d")
        ]:
            canvas.create_oval(
                light_x - r,
                light_y - r * 0.45,
                light_x + r,
                light_y + r * 0.45,
                fill=color,
                outline="",
                tags="room"
            )

    # fixture
    canvas.create_rectangle(
        light_x - 75,
        light_y - 12,
        light_x + 75,
        light_y + 15,
        fill="#24272b",
        outline="#555b62",
        width=3,
        tags="room"
    )

    canvas.create_oval(
        light_x - 60,
        light_y - 5,
        light_x + 60,
        light_y + 35,
        fill="#fff5b0" if light_on else "#4a4d50",
        outline="#85898d",
        width=2,
        tags="room"
    )

    # --------------------------------------------------------
    # FAN
    # --------------------------------------------------------

    fx = w * 0.50
    fy = h * 0.30

    # fan rod
    canvas.create_line(
        fx,
        0,
        fx,
        fy,
        fill="#25282c",
        width=10,
        tags="room"
    )

    # hub
    canvas.create_oval(
        fx - 22,
        fy - 22,
        fx + 22,
        fy + 22,
        fill="#25292e",
        outline="#777e86",
        width=3,
        tags="room"
    )

    # rotating blades
    import math

    blade_length = 135
    blade_width = 32

    for i in range(4):

        angle = math.radians(fan_angle + i * 90)

        x1 = fx + math.cos(angle) * 35
        y1 = fy + math.sin(angle) * 35

        x2 = fx + math.cos(angle) * blade_length
        y2 = fy + math.sin(angle) * blade_length

        perp_x = -math.sin(angle) * blade_width
        perp_y = math.cos(angle) * blade_width

        points = [
            x1 + perp_x,
            y1 + perp_y,

            x1 - perp_x,
            y1 - perp_y,

            x2 - perp_x * 0.5,
            y2 - perp_y * 0.5,

            x2 + perp_x * 0.5,
            y2 + perp_y * 0.5
        ]

        canvas.create_polygon(
            points,
            fill="#30363d" if fan_on else "#24282d",
            outline="#707983",
            width=2,
            tags="room"
        )


# ============================================================
# FAN ANIMATION
# ============================================================

def animate_fan():

    global fan_angle

    if fan_on:
        fan_angle = (fan_angle + 12) % 360
        draw_room()

    root.after(60, animate_fan)


# ============================================================
# ESP32 COMMAND
# ============================================================

def send_command(command):

    global esp32

    try:

        if esp32 is not None and esp32.is_open:

            esp32.write((command + "\n").encode())

            print("Sent:", command)

            return True

        else:
            print("ESP32 not connected")
            return False

    except Exception as e:

        print("Serial error:", e)
        return False


# ============================================================
# UPDATE STATES
# ============================================================

def set_light(state):

    global light_on

    light_on = state

    if state:
        send_command("light on")
        light_status.config(
            text="LIGHT  ON",
            fg=YELLOW
        )
    else:
        send_command("light off")
        light_status.config(
            text="LIGHT  OFF",
            fg=MUTED
        )

    draw_room()


def set_fan(state):

    global fan_on

    fan_on = state

    if state:
        send_command("fan on")
        fan_status.config(
            text="FAN  ON",
            fg=GREEN
        )
    else:
        send_command("fan off")
        fan_status.config(
            text="FAN  OFF",
            fg=MUTED
        )

    draw_room()


# ============================================================
# VOICE CONTROL
# ============================================================

def voice_control():

    global listening

    if listening:
        return

    listening = True

    voice_status.config(
        text="Listening...",
        fg=YELLOW
    )

    threading.Thread(
        target=listen_voice,
        daemon=True
    ).start()


def listen_voice():

    global listening

    try:

        fs = 16000
        duration = 4

        audio = sd.rec(
            int(duration * fs),
            samplerate=fs,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        audio_data = sr.AudioData(
            audio.tobytes(),
            fs,
            2
        )

        recognizer = sr.Recognizer()

        text = recognizer.recognize_google(
            audio_data
        ).lower()

        print("Voice:", text)

        root.after(
            0,
            lambda: process_voice(text)
        )

    except Exception as e:

        print("Voice error:", e)

        root.after(
            0,
            lambda: voice_status.config(
                text="Could not understand",
                fg=RED
            )
        )

    finally:

        listening = False


def process_voice(text):

    voice_text.config(
        text='Heard: "' + text + '"'
    )

    if "light" in text:

        if "on" in text:

            set_light(True)

        elif "off" in text:

            set_light(False)

    elif "fan" in text:

        if "on" in text:

            set_fan(True)

        elif "off" in text:

            set_fan(False)

    elif "exit" in text:

        close_program()

    else:

        voice_status.config(
            text="Command not recognized",
            fg=RED
        )
        return

    voice_status.config(
        text="Voice command executed",
        fg=GREEN
    )


# ============================================================
# CONTROL PANEL
# ============================================================

title = tk.Label(
    control_frame,
    text="SMART HOME",
    font=("Segoe UI", 24, "bold"),
    fg=TEXT,
    bg=PANEL
)

title.pack(
    pady=(30, 3)
)

subtitle = tk.Label(
    control_frame,
    text="VOICE CONTROL CENTER",
    font=("Segoe UI", 9, "bold"),
    fg=BLUE,
    bg=PANEL
)

subtitle.pack()


# ESP32 status

connection_status = tk.Label(
    control_frame,
    text="● ESP32  " +
         ("CONNECTED" if esp32 else "NOT CONNECTED"),
    font=("Segoe UI", 10, "bold"),
    fg=GREEN if esp32 else RED,
    bg=PANEL
)

connection_status.pack(pady=25)


# ------------------------------------------------------------
# LIGHT
# ------------------------------------------------------------

light_box = tk.Frame(
    control_frame,
    bg=PANEL2,
    padx=15,
    pady=15
)

light_box.pack(
    fill="x",
    padx=20,
    pady=10
)

tk.Label(
    light_box,
    text="CEILING LIGHT",
    font=("Segoe UI", 12, "bold"),
    fg=TEXT,
    bg=PANEL2
).pack(anchor="w")

light_status = tk.Label(
    light_box,
    text="LIGHT  OFF",
    font=("Segoe UI", 11, "bold"),
    fg=MUTED,
    bg=PANEL2
)

light_status.pack(anchor="w", pady=5)

light_buttons = tk.Frame(
    light_box,
    bg=PANEL2
)

light_buttons.pack(fill="x")

tk.Button(
    light_buttons,
    text="ON",
    command=lambda: set_light(True),
    bg="#d8ad32",
    fg="black",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    padx=15,
    pady=7
).pack(side="left", padx=(0, 8))

tk.Button(
    light_buttons,
    text="OFF",
    command=lambda: set_light(False),
    bg="#303640",
    fg=TEXT,
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    padx=15,
    pady=7
).pack(side="left")


# ------------------------------------------------------------
# FAN
# ------------------------------------------------------------

fan_box = tk.Frame(
    control_frame,
    bg=PANEL2,
    padx=15,
    pady=15
)

fan_box.pack(
    fill="x",
    padx=20,
    pady=10
)

tk.Label(
    fan_box,
    text="CEILING FAN",
    font=("Segoe UI", 12, "bold"),
    fg=TEXT,
    bg=PANEL2
).pack(anchor="w")

fan_status = tk.Label(
    fan_box,
    text="FAN  OFF",
    font=("Segoe UI", 11, "bold"),
    fg=MUTED,
    bg=PANEL2
)

fan_status.pack(anchor="w", pady=5)

fan_buttons = tk.Frame(
    fan_box,
    bg=PANEL2
)

fan_buttons.pack(fill="x")

tk.Button(
    fan_buttons,
    text="ON",
    command=lambda: set_fan(True),
    bg="#36a66c",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    padx=15,
    pady=7
).pack(side="left", padx=(0, 8))

tk.Button(
    fan_buttons,
    text="OFF",
    command=lambda: set_fan(False),
    bg="#303640",
    fg=TEXT,
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    padx=15,
    pady=7
).pack(side="left")


# ------------------------------------------------------------
# VOICE
# ------------------------------------------------------------

voice_box = tk.Frame(
    control_frame,
    bg=PANEL2,
    padx=15,
    pady=15
)

voice_box.pack(
    fill="x",
    padx=20,
    pady=20
)

tk.Label(
    voice_box,
    text="VOICE COMMAND",
    font=("Segoe UI", 12, "bold"),
    fg=TEXT,
    bg=PANEL2
).pack(anchor="w")

voice_status = tk.Label(
    voice_box,
    text="Ready",
    font=("Segoe UI", 10),
    fg=GREEN,
    bg=PANEL2
)

voice_status.pack(anchor="w", pady=5)

tk.Button(
    voice_box,
    text="🎙  SPEAK",
    command=voice_control,
    bg=BLUE,
    fg="white",
    font=("Segoe UI", 11, "bold"),
    relief="flat",
    padx=15,
    pady=10
).pack(fill="x", pady=5)

voice_text = tk.Label(
    voice_box,
    text='Say "turn on the light"',
    font=("Segoe UI", 9),
    fg=MUTED,
    bg=PANEL2,
    wraplength=240
)

voice_text.pack(anchor="w", pady=5)


# ------------------------------------------------------------
# COMMAND EXAMPLES
# ------------------------------------------------------------

commands = tk.Label(
    control_frame,
    text=(
        "VOICE COMMANDS\n\n"
        '• "Turn on the light"\n'
        '• "Turn off the light"\n'
        '• "Turn on the fan"\n'
        '• "Turn off the fan"'
    ),
    justify="left",
    font=("Segoe UI", 9),
    fg=MUTED,
    bg=PANEL
)

commands.pack(
    padx=25,
    pady=5,
    anchor="w"
)


# ============================================================
# CLOSE
# ============================================================

def close_program():

    try:

        if esp32 and esp32.is_open:
            esp32.close()

    except:
        pass

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_program
)


# ============================================================
# START
# ============================================================

root.after(
    200,
    draw_room
)

root.after(
    100,
    animate_fan
)

root.mainloop()