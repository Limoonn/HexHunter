# HexHunter - Instant Color Picker & Manager

HexHunter is a powerful, modern desktop utility designed for designers and developers. It allows you to instantly capture the hex color code of any pixel on your screen with a simple global hotkey and organize them into specific projects.

## 🚀 Features

*   **Global Hotkey Capture:** Press `Ctrl + Alt + h` anywhere on your screen to capture a color instantly.
*   **Project Management:** Organize your captured colors into custom projects (e.g., "Web App", "Logo Design").
*   **Data Persistence:** All your projects and colors are automatically saved locally.
*   **One-Click Copy:** Easily copy color Hex codes to your clipboard.
*   **Modern Dark UI:** Built with a sleek, dark-themed user interface for comfortable usage.

## 🎮 How to Use

1.  **Launch HexHunter** (run the `.exe` or the python script).
2.  **Create a Project:** Click "+ Add Project" on the sidebar and give it a name.
3.  **Select the Project:** Click on your new project in the list.
4.  **Capture:** Hover your mouse over any color on your screen and press `Ctrl + Alt + h`.
5.  **View & Copy:** The color will appear in your list. Click "Copy" to use the Hex code.

## 📥 Installation & Running

### Option 1: Standalone Application (Recommended)
Download the latest `app.exe` from the **Releases** section of this repository. No Python installation required!

### Option 2: Run from Source
If you are a developer, you can run the Python source code directly:

1.  Clone this repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python app.py
    ```

## 🛠 Technologies Used
*   Python 3.10+
*   CustomTkinter (GUI)
*   Pynput (Global Hotkeys)
*   Pillow (Screen Capture)

---
*Built with ❤️ for pixel-perfect design.*
