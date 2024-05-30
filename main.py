from PyQt5.QtWidgets import QApplication
from gui.app import TopologyOptimizationApp
import sys

def main():
    app = QApplication(sys.argv)  # Create a Qt application
    app.setStyle("Fusion")
    window = TopologyOptimizationApp()  # Initialize the main window
    window.show()  # Show the main window
    sys.exit(app.exec_())  # Start the application event loop

if __name__ == "__main__":
    main()
