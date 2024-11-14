import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Helper function to create rounded corner buttons with Pillow
def create_rounded_button(parent, text, color, radius=10):
    button_image = Image.new("RGBA", (120, 40), color)
    mask = Image.new("L", (120, 40), 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, 120, 40), radius=radius, fill=255)
    button_image.putalpha(mask)
    img_tk = ImageTk.PhotoImage(button_image)
    
    button = tk.Label(parent, text=text, image=img_tk, compound="center", bg="#ffffff", fg="#ffffff", font=("Arial", 10, "bold"))
    button.image = img_tk  # keep reference
    return button

# Initialize the main window
root = tk.Tk()
root.title("Custom GUI")
root.geometry("600x700")
root.config(bg="#e5e5e5")

# Create the side menu
side_menu = tk.Frame(root, bg="#f0f0f0", width=150)
side_menu.pack(side="left", fill="y")

# Add buttons to the side menu with rounded corners
side_buttons = ["General", "Keyboard & Mouse", "Aim Settings", "Hotkey Settings"]
for text in side_buttons:
    btn = create_rounded_button(side_menu, text=text, color="#0078d7")
    btn.pack(fill="x", pady=5, padx=5)

# Create main content area
content_area = tk.Frame(root, bg="#ffffff")
content_area.pack(expand=True, fill="both", side="right")

# Language and Theme buttons
lang_theme_frame = tk.Frame(content_area, bg="#ffffff")
lang_theme_frame.pack(pady=10, anchor="ne")

lang_eng = create_rounded_button(lang_theme_frame, text="ENG", color="#0078d7")
lang_eng.grid(row=0, column=0, padx=5)

lang_ch = create_rounded_button(lang_theme_frame, text="中文", color="#dcdcdc")
lang_ch.grid(row=0, column=1, padx=5)

day_mode = create_rounded_button(lang_theme_frame, text="☀", color="#0078d7")
day_mode.grid(row=0, column=2, padx=5)

# Switches
switch_frame = tk.Frame(content_area, bg="#ffffff")
switch_frame.pack(pady=10, fill="x", padx=20)

anti_scsx = tk.Checkbutton(switch_frame, text="Anti-SCSX", bg="#ffffff", anchor="w")
anti_scsx.grid(row=0, column=0, sticky="w")

hotkeys = create_rounded_button(switch_frame, text="HotKeys", color="#dcdcdc")
hotkeys.grid(row=0, column=1, sticky="e")

# Real-time detection switch
realtime_detection = tk.Checkbutton(content_area, text="Real-time detection", bg="#ffffff")
realtime_detection.pack(anchor="w", padx=20)

# Screenshot options
screenshot_frame = tk.Frame(content_area, bg="#ffffff")
screenshot_frame.pack(pady=10, fill="x", padx=20)

fullscreen = create_rounded_button(screenshot_frame, text="Fullscreen Shot", color="#dcdcdc")
fullscreen.grid(row=0, column=0, padx=5)

window_shot = create_rounded_button(screenshot_frame, text="Window Shot", color="#0078d7")
window_shot.grid(row=0, column=1, padx=5)

quick_shot = create_rounded_button(screenshot_frame, text="Quick Shot", color="#dcdcdc")
quick_shot.grid(row=0, column=2, padx=5)

# Game model and profile settings
model_frame = tk.Frame(content_area, bg="#ffffff")
model_frame.pack(pady=10, fill="x", padx=20)

ttk.Label(model_frame, text="Game Model", background="#ffffff").grid(row=0, column=0, sticky="w")
ttk.Combobox(model_frame, values=["Games(通用)", "Other"]).grid(row=0, column=1, sticky="w")

ttk.Label(model_frame, text="Model Type", background="#ffffff").grid(row=1, column=0, sticky="w")
ttk.Combobox(model_frame, values=["yolox tiny", "other type"]).grid(row=1, column=1, sticky="w")

# Profile settings
profile_frame = tk.Frame(content_area, bg="#ffffff")
profile_frame.pack(pady=10, fill="x", padx=20)

ttk.Label(profile_frame, text="Profile", background="#ffffff").grid(row=0, column=0, sticky="w")
ttk.Combobox(profile_frame, values=["Games", "Other"]).grid(row=0, column=1, sticky="w")

gpu_frame = tk.Frame(profile_frame, bg="#ffffff")
gpu_frame.grid(row=1, column=0, columnspan=2, sticky="w")

gpu_buttons = ["Nvidia", "AMD/Nvidia", "CPU"]
for i, text in enumerate(gpu_buttons):
    btn = create_rounded_button(gpu_frame, text=text, color="#dcdcdc")
    btn.grid(row=0, column=i, padx=5)

# Fast switch
fast_switch = tk.Checkbutton(content_area, text="Fast", bg="#ffffff")
fast_switch.pack(anchor="w", padx=20)

# Save and exit buttons at the bottom
bottom_frame = tk.Frame(root, bg="#f0f0f0", height=50)
bottom_frame.pack(side="bottom", fill="x")

save_button = create_rounded_button(bottom_frame, text="Save", color="#0078d7")
save_button.pack(side="left", padx=10, pady=10)

exit_button = create_rounded_button(bottom_frame, text="Exit", color="#dcdcdc")
exit_button.pack(side="right", padx=10, pady=10)

# Run the main loop
root.mainloop()
