
# splash_screen.py - SentinelIT Startup Visual Intro

import tkinter as tk
from PIL import Image, ImageTk
import time

def show_splash():
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("600x400+400+200")  # Centered window (adjust if needed)
    root.configure(bg='black')

    # Load image
    image = Image.open("SentinelIT_Startup.png")
    image = image.resize((600, 400))
    logo = ImageTk.PhotoImage(image)

    # Add image to window
    label = tk.Label(root, image=logo, bg='black')
    label.image = logo
    label.pack()

    # Display for 3 seconds then fade out
    root.after(3000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    show_splash()
