import tkinter as tk
import pyautogui

# --- overlay window ---
root = tk.Tk()
root.title("Cursor PX")
root.overrideredirect(True)     # no border
root.attributes("-topmost", True)
root.attributes("-alpha", 0.85)  # transparency

# Make it click-through (Windows only)
try:
    import win32con
    import win32gui
    import win32api

    hwnd = win32gui.GetParent(root.winfo_id())
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(
        hwnd,
        win32con.GWL_EXSTYLE,
        styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
    )
except Exception:
    pass  # if click-through fails, it still works

label = tk.Label(
    root,
    text="X: 0  Y: 0",
    font=("Segoe UI", 12, "bold"),
    bg="black",
    fg="white",
    padx=12,
    pady=8
)
label.pack()

# Place overlay (top-left). Change these if you want.
root.geometry("+20+20")

def update_coords():
    x, y = pyautogui.position()
    label.config(text=f"X: {x}px   Y: {y}px")
    root.after(30, update_coords)  # ~33 FPS

# ESC to close
root.bind("<Escape>", lambda e: root.destroy())

update_coords()
root.mainloop()