import customtkinter as ctk
import threading
import pyperclip
from pynput import keyboard
from PIL import ImageGrab
import json
import os
import platform
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")
DATA_FILE = "projects.json"

class ProjectManager:
    """
    Handles data persistence for projects and colors.
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(self.filepath):
            return {"Default": []}
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"Default": []}

    def save_data(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=4)
        except IOError as e:
            print(f"Error saving data: {e}")

    def add_project(self, name):
        if name and name not in self.data:
            self.data[name] = []
            self.save_data()
            return True
        return False

    def delete_project(self, name):
        if name in self.data:
            del self.data[name]
            self.save_data()
            return True
        return False

    def add_color(self, project_name, hex_code):
        if project_name in self.data:
            # Avoid duplicates if desired, or allow them. 
            # Requirement says "append", so we allow matches.
            self.data[project_name].append(hex_code)
            self.save_data()
            return True
        return False

    def delete_color(self, project_name, index):
        if project_name in self.data and 0 <= index < len(self.data[project_name]):
            self.data[project_name].pop(index)
            self.save_data()
            return True
        return False
    
    def get_projects(self):
        return list(self.data.keys())

    def get_colors(self, project_name):
        return self.data.get(project_name, [])


class ColorRow(ctk.CTkFrame):
    """
    A custom frame representing a single captured color row.
    """
    def __init__(self, master, hex_code, index, delete_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.hex_code = hex_code
        self.index = index
        self.delete_callback = delete_callback
        
        # Configure grid
        self.grid_columnconfigure(0, weight=0) # Color Box
        self.grid_columnconfigure(1, weight=1) # Hex Text
        self.grid_columnconfigure(2, weight=0) # Copy Btn
        self.grid_columnconfigure(3, weight=0) # Delete Btn
        
        # Color Box
        self.color_box = ctk.CTkLabel(
            self, 
            text="", 
            width=30, 
            height=30, 
            fg_color=hex_code, 
            corner_radius=5
        )
        self.color_box.grid(row=0, column=0, padx=10, pady=5)
        
        # Hex Label
        self.label = ctk.CTkLabel(
            self, 
            text=hex_code, 
            font=("Roboto", 14),
            anchor="w"
        )
        self.label.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # Copy Button
        self.copy_btn = ctk.CTkButton(
            self, 
            text="Copy", 
            width=50, 
            height=28,
            command=self.copy_action,
            font=("Roboto", 12)
        )
        self.copy_btn.grid(row=0, column=2, padx=5, pady=5)

        # Delete Button (Red Trash Icon style, simplified to "X" or "Del")
        self.del_btn = ctk.CTkButton(
            self,
            text="X",
            width=30,
            height=28,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            command=self.delete_action,
            font=("Roboto", 12, "bold")
        )
        self.del_btn.grid(row=0, column=3, padx=5, pady=5)

    def copy_action(self):
        pyperclip.copy(self.hex_code)
        original_text = self.copy_btn.cget("text")
        self.copy_btn.configure(text="OK!", fg_color="green")
        self.after(1000, lambda: self.copy_btn.configure(text=original_text, fg_color=["#3B8ED0", "#1F6AA5"]))

    def delete_action(self):
        self.delete_callback(self.index)


class HexHunterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HexHunter - Project Manager")
        self.geometry("700x500")
        
        # Data Manager
        self.db = ProjectManager(DATA_FILE)
        self.current_project = None
        
        # Layout Config: Sidebar (0) and Main (1)
        self.grid_columnconfigure(0, weight=1) # Sidebar
        self.grid_columnconfigure(1, weight=3) # Main Content
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.sidebar_label = ctk.CTkLabel(self.sidebar_frame, text="Projects", font=("Roboto Medium", 20))
        self.sidebar_label.pack(padx=20, pady=20)
        
        self.add_proj_btn = ctk.CTkButton(self.sidebar_frame, text="+ Add Project", command=self.add_project_dialog)
        self.add_proj_btn.pack(padx=20, pady=10)

        self.project_list_frame = ctk.CTkScrollableFrame(self.sidebar_frame, label_text="Your Projects")
        self.project_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.del_proj_btn = ctk.CTkButton(
            self.sidebar_frame, 
            text="Delete Selected", 
            fg_color="#D32F2F", 
            hover_color="#B71C1C",
            command=self.delete_current_project
        )
        self.del_proj_btn.pack(padx=20, pady=20, side="bottom")

        # --- Main Area ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        
        self.header_label = ctk.CTkLabel(self.main_frame, text="Select a Project", font=("Roboto Medium", 18))
        self.header_label.pack(padx=20, pady=20, anchor="w")
        
        self.colors_scroll = ctk.CTkScrollableFrame(self.main_frame, label_text="Colors")
        self.colors_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Initialize UI state
        self.refresh_project_list()
        
        # Select first project if available
        projects = self.db.get_projects()
        if projects:
            self.select_project(projects[0])

        # Start Hotkey Listener
        self.start_listener()

    def start_listener(self):
        self.listener_thread = threading.Thread(target=self._run_listener, daemon=True)
        self.listener_thread.start()

    def _run_listener(self):
        with keyboard.GlobalHotKeys({'<ctrl>+<alt>+h': self.on_hotkey_press}) as h:
            h.join()

    def on_hotkey_press(self):
        try:
            x, y = self.get_mouse_position()
            # Grab pixel
            image = ImageGrab.grab(bbox=(x, y, x+1, y+1))
            rgb = image.getpixel((0, 0))
            # Handle RGBA if generic (sometimes returns 4 values)
            if len(rgb) > 3:
                rgb = rgb[:3]
            
            hex_code = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2]).upper()
            
            self.after(0, lambda: self.handle_capture(hex_code))
        except Exception as e:
            print(f"Capture error: {e}")

    def get_mouse_position(self):
        from pynput.mouse import Controller
        mouse = Controller()
        return (int(mouse.position[0]), int(mouse.position[1]))

    def handle_capture(self, hex_code):
        if not self.current_project:
            # Fallback to Default if exists, or create it
            if "Default" not in self.db.get_projects():
                self.db.add_project("Default")
                self.refresh_project_list()
            self.select_project("Default")
            
        success = self.db.add_color(self.current_project, hex_code)
        if success:
            self.refresh_color_list()
        else:
            print("Failed to save color")

    # --- UI Logic ---

    def refresh_project_list(self):
        # Clear existing buttons
        for widget in self.project_list_frame.winfo_children():
            widget.destroy()
        
        projects = self.db.get_projects()
        for p in projects:
            btn = ctk.CTkButton(
                self.project_list_frame, 
                text=p, 
                command=lambda name=p: self.select_project(name),
                fg_color="transparent", 
                border_width=1, 
                text_color=("gray10", "gray90")
            )
            # Highlight if selected
            if p == self.current_project:
                btn.configure(fg_color=("gray75", "gray25"))
            
            btn.pack(fill="x", padx=5, pady=2)

    def select_project(self, name):
        self.current_project = name
        self.header_label.configure(text=f"Project: {name}")
        self.refresh_project_list() # To update highlight
        self.refresh_color_list()

    def refresh_color_list(self):
        # Clear colors
        for widget in self.colors_scroll.winfo_children():
            widget.destroy()
            
        if not self.current_project:
            return

        colors = self.db.get_colors(self.current_project)
        # Display in reverse order (newest top) if desired, but user might expect append.
        # Let's do normal order (append bottom) for now to match list index easily.
        
        for i, hex_code in enumerate(colors):
            row = ColorRow(
                self.colors_scroll, 
                hex_code=hex_code, 
                index=i, 
                delete_callback=self.delete_color_from_project
            )
            row.pack(fill="x", padx=5, pady=5)

    def add_project_dialog(self):
        dialog = ctk.CTkInputDialog(text="Enter Project Name:", title="New Project")
        name = dialog.get_input()
        if name:
            if self.db.add_project(name):
                self.refresh_project_list()
                self.select_project(name)

    def delete_current_project(self):
        if self.current_project:
            self.db.delete_project(self.current_project)
            self.current_project = None
            self.refresh_project_list()
            self.refresh_color_list()
            
            # Select another if available
            projects = self.db.get_projects()
            if projects:
                self.select_project(projects[0])
            else:
                self.header_label.configure(text="Select or Create a Project")

    def delete_color_from_project(self, index):
        if self.current_project:
            self.db.delete_color(self.current_project, index)
            self.refresh_color_list()

if __name__ == "__main__":
    app = HexHunterApp()
    app.mainloop()
