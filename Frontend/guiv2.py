import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk

class ModernSettingsGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Settings")
        self.root.geometry("1000x600")
        
        # Set the color theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create main containers
        self.left_sidebar = ctk.CTkFrame(self.root, width=200)
        self.left_sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        self.right_content = ctk.CTkFrame(self.root)
        self.right_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Add sidebar buttons
        self.create_sidebar_buttons()
        
        # Add top right controls
        self.create_top_controls()
        
        # Add main content
        self.create_main_content()
        
        # Add bottom buttons
        self.create_bottom_buttons()

    def create_sidebar_buttons(self):
        buttons = ["General", "Keyboard & Mouse", "Aim Settings", "Hotkey Settings"]
        for text in buttons:
            btn = ctk.CTkButton(
                self.left_sidebar,
                text=text,
                height=40,
                anchor="w",
                fg_color="transparent",
                text_color="black",
                hover_color=("gray70", "gray30")
            )
            btn.pack(fill="x", padx=5, pady=2)

    def create_top_controls(self):
        top_frame = ctk.CTkFrame(self.right_content)
        top_frame.pack(fill="x", pady=5)
        
        # Language buttons
        lang_frame = ctk.CTkFrame(top_frame)
        lang_frame.pack(side="right")
        
        ctk.CTkButton(lang_frame, text="ENG", width=60).pack(side="left", padx=2)
        ctk.CTkButton(lang_frame, text="中文", width=60).pack(side="left", padx=2)
        
        # Theme toggle
        self.theme_switch = ctk.CTkSwitch(top_frame, text="")
        self.theme_switch.pack(side="right", padx=10)

    def create_main_content(self):
        # Real-time detection toggle
        detection_frame = ctk.CTkFrame(self.right_content)
        detection_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(detection_frame, text="Real-time detection").pack(side="left", padx=10)
        ctk.CTkSwitch(detection_frame, text="").pack(side="right", padx=10)
        
        # Shot type selector
        shot_frame = ctk.CTkFrame(self.right_content)
        shot_frame.pack(fill="x", pady=10)
        shots = ["Fullscreen Shot", "Window Shot", "Quick Shot"]
        for shot in shots:
            ctk.CTkButton(shot_frame, text=shot, width=120).pack(side="left", padx=2)
        
        # Game Model selector
        game_frame = ctk.CTkFrame(self.right_content)
        game_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(game_frame, text="Game Model").pack(side="left", padx=10)
        ctk.CTkOptionMenu(game_frame, values=["Games(通用)", "yolox tiny"]).pack(side="right", padx=10)
        
        # Profile selector
        profile_frame = ctk.CTkFrame(self.right_content)
        profile_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(profile_frame, text="Profile").pack(side="left", padx=10)
        ctk.CTkOptionMenu(profile_frame, values=["Games"]).pack(side="right", padx=10)
        
        # GPU selector
        gpu_frame = ctk.CTkFrame(self.right_content)
        gpu_frame.pack(fill="x", pady=10)
        gpu_types = ["Nvidia", "AMD/Nvidia", "CPU"]
        for gpu in gpu_types:
            ctk.CTkButton(gpu_frame, text=gpu, width=100).pack(side="left", padx=2)
            
        # Fast toggle
        fast_frame = ctk.CTkFrame(self.right_content)
        fast_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(fast_frame, text="Fast").pack(side="left", padx=10)
        ctk.CTkSwitch(fast_frame, text="").pack(side="right", padx=10)

    def create_bottom_buttons(self):
        bottom_frame = ctk.CTkFrame(self.left_sidebar)
        bottom_frame.pack(side="bottom", fill="x", pady=10)
        
        ctk.CTkButton(bottom_frame, text="Save").pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(bottom_frame, text="Start").pack(fill="x", padx=5, pady=2)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernSettingsGUI()
    app.run()