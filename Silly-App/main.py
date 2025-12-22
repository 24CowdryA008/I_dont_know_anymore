"""
Small startup helper: attempt to install dependencies listed in
`requirements.txt` before running the app. To skip automatic installation,
set the environment variable `SILLYAPP_SKIP_INSTALL=1`.
"""
import os
import sys
import subprocess

def _install_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if not os.path.exists(req_path):
        return
    if os.environ.get("SILLYAPP_SKIP_INSTALL"):
        return
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
    except Exception as e:
        print(f"Warning: failed to install requirements: {e}", file=sys.stderr)


_install_requirements()

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import threading
import time

WAIFU_FOLDER = os.path.join(os.path.dirname(__file__), "waifus")
WAIFU_GIFS = [
    os.path.join(WAIFU_FOLDER, f)
    for f in os.listdir(WAIFU_FOLDER)
    if f.lower()
]

GIF_DISPLAY_TIME = 3  # seconds
MIN_INTERVAL = 10     # seconds
MAX_INTERVAL = 30     # seconds

def get_screen_size():
    root = tk.Tk()
    root.withdraw()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height

def show_waifu_gif(gif_path):
    win = tk.Toplevel()
    win.overrideredirect(True)
    screen_w, screen_h = get_screen_size()
    img = Image.open(gif_path)
    frames = []
    try:
        while True:
            frames.append(ImageTk.PhotoImage(img.copy()))
            img.seek(len(frames))  # next frame
    except EOFError:
        pass

    frame_count = len(frames)
    gif_w, gif_h = frames[0].width(), frames[0].height()

    # Choose a random starting edge and direction
    edge = random.choice(['left', 'right', 'top', 'bottom'])
    if edge == 'left':
        x, y = 0, random.randint(0, screen_h - gif_h)
        dx, dy = random.randint(5, 15), random.randint(-5, 5)
    elif edge == 'right':
        x, y = screen_w - gif_w, random.randint(0, screen_h - gif_h)
        dx, dy = -random.randint(5, 15), random.randint(-5, 5)
    elif edge == 'top':
        x, y = random.randint(0, screen_w - gif_w), 0
        dx, dy = random.randint(-5, 5), random.randint(5, 15)
    else:  # bottom
        x, y = random.randint(0, screen_w - gif_w), screen_h - gif_h
        dx, dy = random.randint(-5, 5), -random.randint(5, 15)

    win.geometry(f"{gif_w}x{gif_h}+{x}+{y}")

    label = tk.Label(win)
    label.pack()

    def animate(idx=0):
        label.config(image=frames[idx])
        win.after(100, animate, (idx + 1) % frame_count)

    animate()

    # Move the window across the screen and bounce off edges
    def float_window():
        nonlocal x, y, dx, dy
        x += dx
        y += dy
        # Bounce off left/right edges
        if x < 0:
            x = 0
            dx *= -1
        elif x > screen_w - gif_w:
            x = screen_w - gif_w
            dx *= -1
        # Bounce off top/bottom edges
        if y < 0:
            y = 0
            dy *= -1
        elif y > screen_h - gif_h:
            y = screen_h - gif_h
            dy *= -1
        win.geometry(f"{gif_w}x{gif_h}+{int(x)}+{int(y)}")
        win.after(30, float_window)

    float_window()

    def close_win():
        win.destroy()

    win.after(GIF_DISPLAY_TIME * 1000, close_win)

def waifu_spawner():
    while True:
        if not WAIFU_GIFS:
            break
        gif_path = random.choice(WAIFU_GIFS)
        if os.path.exists(gif_path):
            root.after(0, show_waifu_gif, gif_path)
        interval = random.randint(MIN_INTERVAL, MAX_INTERVAL)
        time.sleep(interval)

root = tk.Tk()
root.withdraw()  # Hide main window

if not WAIFU_GIFS:
    messagebox.showerror("No GIFs Found", f"No GIFs found in {WAIFU_FOLDER}.\nPlease add .gif files to that folder.")
    root.destroy()
else:
    threading.Thread(target=waifu_spawner, daemon=True).start()
    root.mainloop()
