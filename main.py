import sys
import webbrowser
import threading
from PyQt5.QtWidgets import QMainWindow, QWidget, QLineEdit, QVBoxLayout, QSystemTrayIcon, QMenu, QAction, QGraphicsDropShadowEffect, QApplication
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QTimer
import pyautogui
import json
import keyboard


ThemeFilePath = 'data/Theme.css'
ShortCutFilePath = 'data/config.json'
Theme = ''

class SpotlightSearch(QMainWindow):
    def __init__(self):
        super().__init__()

        self.open_files = []

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.shortcuts = self.LoadShortcuts()


        # Set transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.LoadTheme()

        # Create a central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create and style the text box
        self.text_box = QLineEdit()
        self.text_box.setPlaceholderText("Search the web...")
        self.setStyleSheet(Theme)
        
        # Add the text box to the layout
        layout.addWidget(self.text_box)

        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(8)  # The spread/sof6tness of the shadow
        shadow_effect.setOffset(0, 7)   # The horizontal and vertical offset
        shadow_effect.setColor(QColor(0, 0, 0, 160))  # RGBA (black shadow, 160 alpha)

        # Apply the shadow effect to the central widget
        central_widget.setGraphicsEffect(shadow_effect)

        # Focus on the text box automatically
        self.text_box.setFocus()

        self.create_tray_icon()
        # Close dialog when Enter is pressed (optional)
        self.text_box.returnPressed.connect(self.close_dialog)

    def LoadTheme(self):
        global Theme
        try: 
            with open(ThemeFilePath, 'r') as file:
                Theme = file.read()
                self.open_files.append(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading JSON: {e}")
            return {}
    
    def LoadShortcuts(self):
        try:
            with open(ShortCutFilePath, 'r') as file:
                self.open_files.append(file)
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error leading Json: {e}")
            return{}

    def create_tray_icon(self):
        """Create a system tray icon for the app."""
        # Set up the tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("data/icon.png"))  # Replace with your icon path

        # Create a menu for the tray icon
        tray_menu = QMenu()

        # Add "Quit" action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)

        # Set the menu to the tray icon
        self.tray_icon.setContextMenu(tray_menu)

        # Show the tray icon
        self.tray_icon.show()

    def showEvent(self, event):
        """Ensure the text box gets focus when the window is shown."""
        super().showEvent(event)
        self.text_box.setFocus()
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def reload_theme_and_style(self):
        self.LoadTheme()
        self.setStyleSheet(Theme)
        self.hide()
        self.text_box.clear()
        
    
    def close_dialog(self):
        """Load the URL entered in the text box."""
        url = self.text_box.text()

        if url == "!e" or url == "!E":
            self.hide()
            self.text_box.clear()
            print(f"end:{url}")
            return

        if url == "!reload" or url == "!Reload":
            QTimer.singleShot(0, self.reload_theme_and_style)
            return

        if any(url.endswith(suffix) for suffix in [".com", ".ca", ".org", ".net", ".edu", ".gov", ".io", ".tv"]):
            # If it ends with a domain suffix, treat it as a URL
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"  # Assume https if no scheme is provided

        if url and url[0] == '-': #for search pers
            try:
                for keyword, link in self.shortcuts["Search Config"].items(): 
                    if url.startswith(keyword):
                        url = url.partition(keyword)[2]
                        url = f'{link.partition(' ')[0]}{url}{link.partition(' ')[2]}'
                        break
                else:
                    url = "https://www.google.com"
                    
            except KeyError:
                print("error")
                url = "https://www.google.com"
        elif url and url[0] == '!': # for shortcuts
            try:
                for keyword, link in self.shortcuts["Shortcuts"].items(): 
                    if url.startswith(keyword):
                        url = f'{link}'
                        break
                else:
                    url = "https://www.google.com"      
            except KeyError:
                print("error")
                url = "https://www.google.com"
        elif not url.startswith("https://"):
            url = f"https://www.google.com/search?safe=active&q={url}"
        # Find the current tab and set the URL in its web view
        webbrowser.open_new_tab(url)
        self.text_box.clear()
        self.hide()

def show_spotlight():
    global window

    if not window.isVisible():
        window.show()
        window.raise_()
        window.activateWindow()
        sw,sh = pyautogui.size() 
        pyautogui.moveTo(sw // 2, sh // 2 - 30)
        pyautogui.leftClick()
        window.text_box.setFocus()
def start_hotkey_listener():
    keyboard.add_hotkey('ctrl+space', show_spotlight)
    keyboard.wait()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create and show the main window
    window = SpotlightSearch()
    window.show()

    hotkey_thread = threading.Thread(target=start_hotkey_listener,  daemon=True)
    hotkey_thread.start()

    sys.exit(app.exec_())
