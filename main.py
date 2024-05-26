import sys
from PyQt5.QtWidgets import QApplication
from gui.app import TopologyOptimizationApp

def main():
    app = QApplication(sys.argv) # Create a Qt application
    app.setStyle("Fusion")
    mainWindow = TopologyOptimizationApp() # Initialize the main window
    mainWindow.show() # Show the main window
    sys.exit(app.exec_())  # Start the application event loop

if __name__ == "__main__":
    main()
