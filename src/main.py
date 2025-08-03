import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.splash_screen import SplashScreen
from ui.main_window import MainWindow
from core.theme_manager import ThemeManager

def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Banking Security Platform")
    app.setOrganizationName("Sammtan")
    
    # Apply modern dark theme
    theme_manager = ThemeManager()
    theme_manager.apply_dark_theme(app)
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    
    # Initialize main window
    main_window = MainWindow()
    
    # Show main window after splash
    splash.finish(main_window)
    main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()