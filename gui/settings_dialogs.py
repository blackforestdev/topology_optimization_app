# gui/settings_dialogs.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QHBoxLayout, QComboBox, QSlider, QLabel, QPushButton, QApplication

class MeshSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Mesh algorithm selection
        self.algorithmCombo = QComboBox()
        self.algorithmCombo.addItems(["Delaunay", "Voronoi", "Tetrahedral"])
        layout.addWidget(QLabel("Select Mesh Algorithm:"))
        layout.addWidget(self.algorithmCombo)

        # Mesh resolution slider
        self.resolutionSlider = QSlider()
        self.resolutionSlider.setRange(1, 10)  # 1 = Coarse, 10 = Fine
        layout.addWidget(QLabel("Select Mesh Resolution:"))
        layout.addWidget(self.resolutionSlider)

        # OK and Cancel buttons
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        layout.addWidget(self.okButton)
        layout.addWidget(self.cancelButton)

        self.setLayout(layout)

    def getSettings(self):
        return {
            "algorithm": self.algorithmCombo.currentText(),
            "resolution": self.resolutionSlider.value()
        }    

class LoadInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Load type selection
        self.load_type = QComboBox(self)
        self.load_type.addItems(["Force", "Pressure", "Thermal"])
        layout.addWidget(QLabel("Load Type:"))
        layout.addWidget(self.load_type)

        # Label and field for magnitude
        self.magnitude_label = QLabel("Magnitude:", self)
        self.magnitude = QLineEdit(self)
        layout.addWidget(self.magnitude_label)
        layout.addWidget(self.magnitude)

        # Direction inputs (used for Force only)
        self.direction_layout = QHBoxLayout()
        self.direction_x = QLineEdit(self)
        self.direction_y = QLineEdit(self)
        self.direction_z = QLineEdit(self)
        self.direction_layout.addWidget(QLabel("Direction X:"))
        self.direction_layout.addWidget(self.direction_x)
        self.direction_layout.addWidget(QLabel("Direction Y:"))
        self.direction_layout.addWidget(self.direction_y)
        self.direction_layout.addWidget(QLabel("Direction Z:"))
        self.direction_layout.addWidget(self.direction_z)
        layout.addLayout(self.direction_layout)

        # Temperature input (used for Thermal)
        self.temperature_label = QLabel("Temperature Change (°C):", self)
        self.temperature = QLineEdit(self)
        layout.addWidget(self.temperature_label)
        layout.addWidget(self.temperature)

        # Submit button
        submit_button = QPushButton('Submit', self)
        submit_button.clicked.connect(self.submit)
        layout.addWidget(submit_button)

        self.load_type.currentIndexChanged.connect(self.update_load_type)  # Ensure this connection
        self.update_load_type()  # Initial call to set up the dialog correctly

    def update_load_type(self):
        load_type = self.load_type.currentText()
        is_force = load_type == "Force"
        is_pressure = load_type == "Pressure"
        is_thermal = load_type == "Thermal"

        # Update label text and control visibility for magnitude and temperature fields
        self.magnitude_label.setText("Magnitude (N):" if is_force else "Magnitude (Pa):")
        self.magnitude.setVisible(is_force or is_pressure)
        self.magnitude_label.setVisible(is_force or is_pressure)
        self.temperature.setVisible(is_thermal)
        self.temperature_label.setVisible(is_thermal)

        # Control visibility of direction inputs (used for Force only)
        for i in range(self.direction_layout.count()):
            widget = self.direction_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(is_force)

    def submit(self):
        load_type = self.load_type.currentText()
        magnitude = float(self.magnitude.text()) if self.magnitude.isVisible() else None
        direction = (float(self.direction_x.text()), float(self.direction_y.text()), float(self.direction_z.text())) if self.direction_layout.isVisible() else None
        temperature_change = float(self.temperature.text()) if self.temperature.isVisible() else None

        print(f"Load Applied: {load_type}, Magnitude: {magnitude}, Direction: {direction}, Temperature Change: {temperature_change}")
        self.accept()
