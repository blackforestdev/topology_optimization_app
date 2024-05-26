import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox,
                             QFileDialog, QLineEdit, QFormLayout, QDialog, QAction, QToolBar)
from PyQt5.QtCore import Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from fea.mesh_generation import load_stl, generate_mesh
from fea.material_properties import MaterialProperties
from gui.settings_dialogs import MeshSettingsDialog
from gui.settings_dialogs import LoadInputDialog
from vtk_components.renderer import Renderer

class MaterialPropertiesDialog(QDialog):
    def __init__(self, material_properties, parent=None):
        super().__init__(parent)
        self.material_properties = material_properties
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Young's modulus input with label
        self.youngs_modulus_layout = QHBoxLayout()
        self.youngs_modulus = QLineEdit(self)
        self.youngs_modulus_units = QComboBox(self)
        self.youngs_modulus_units.addItems(["Pa", "MPa", "GPa"])

        # Create a label for Young's Modulus
        youngs_modulus_label = QLabel("Young's Modulus:")
        self.youngs_modulus_layout.addWidget(youngs_modulus_label)
        self.youngs_modulus_layout.addWidget(self.youngs_modulus)
        self.youngs_modulus_layout.addWidget(self.youngs_modulus_units)
        layout.addLayout(self.youngs_modulus_layout)

        # Poisson's ratio input
        poissons_ratio_label = QLabel("Poisson's Ratio:")
        layout.addWidget(poissons_ratio_label)
        self.poissons_ratio = QLineEdit(self)
        layout.addWidget(self.poissons_ratio)

        # Density input with label
        self.density_layout = QHBoxLayout()
        self.density = QLineEdit(self)
        self.density_units = QComboBox(self)
        self.density_units.addItems(["kg/m³", "g/cm³"])
        density_label = QLabel("Density:")
        self.density_layout.addWidget(density_label)
        self.density_layout.addWidget(self.density)
        self.density_layout.addWidget(self.density_units)
        layout.addLayout(self.density_layout)

        # Submit button
        submit_button = QPushButton('Submit', self)
        submit_button.clicked.connect(self.submit)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def submit(self):
        # Convert and set properties
        youngs_modulus = float(self.youngs_modulus.text())
        if self.youngs_modulus_units.currentText() == "MPa":
            youngs_modulus *= 1e6
        elif self.youngs_modulus_units.currentText() == "GPa":
            youngs_modulus *= 1e9

        density = float(self.density.text())
        if self.density_units.currentText() == "g/cm³":
            density *= 1000  # Convert g/cm³ to kg/m³

        self.material_properties.set_properties(
            youngs_modulus, float(self.poissons_ratio.text()), density
        )
        self.accept()

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

class TopologyOptimizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Topology Optimization Application')
        self.setup_ui()
        self.create_menus()
        self.create_toolbar()
        self.center_and_resize()

    def setup_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        self.material_properties = MaterialProperties()

        self.vtk_widget = QVTKRenderWindowInteractor(self.central_widget)
        layout.addWidget(self.vtk_widget)
        self.renderer = Renderer(self.vtk_widget)
        self.vtk_widget.Initialize()
        self.vtk_widget.Start()

    def create_menus(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        load_action = QAction("&Load STL", self)
        load_action.triggered.connect(self.load_stl)
        file_menu.addAction(load_action)

        mesh_menu = menu_bar.addMenu("&Mesh")
        mesh_settings_action = QAction("&Settings", self)
        mesh_settings_action.triggered.connect(self.open_mesh_settings_dialog)
        mesh_menu.addAction(mesh_settings_action)

        material_menu = menu_bar.addMenu("&Material")
        material_properties_action = QAction("&Properties", self)
        material_properties_action.triggered.connect(self.openMaterialPropertiesDialog)
        material_menu.addAction(material_properties_action)

        load_menu = menu_bar.addMenu("&Load")
        load_settings_action = QAction("&Properties", self)
        load_settings_action.triggered.connect(self.openLoadPropertiesDialog)
        load_menu.addAction(load_settings_action)

        view_menu = menu_bar.addMenu("&View")
        toggle_mesh_action = QAction("Toggle &Mesh Visibility", self)
        toggle_mesh_action.triggered.connect(self.renderer.toggle_mesh_visibility)
        view_menu.addAction(toggle_mesh_action)

        toggle_nodes_action = QAction("Toggle &Nodes Visibility", self)
        toggle_nodes_action.triggered.connect(self.renderer.toggle_nodes_visibility)
        view_menu.addAction(toggle_nodes_action)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        mesh_settings_button = QPushButton("Mesh Settings")
        mesh_settings_button.clicked.connect(self.open_mesh_settings_dialog)
        toolbar.addWidget(mesh_settings_button)

        material_properties_button = QPushButton("Material Properties")
        material_properties_button.clicked.connect(self.openMaterialPropertiesDialog)
        toolbar.addWidget(material_properties_button)

        load_properties_button = QPushButton("Load Properties")
        load_properties_button.clicked.connect(self.openLoadPropertiesDialog)
        toolbar.addWidget(load_properties_button)

        toggle_mesh_button = QPushButton("Toggle Mesh")
        toggle_mesh_button.clicked.connect(self.renderer.toggle_mesh_visibility)
        toolbar.addWidget(toggle_mesh_button)

        toggle_nodes_button = QPushButton("Toggle Nodes")
        toggle_nodes_button.clicked.connect(self.renderer.toggle_nodes_visibility)
        toolbar.addWidget(toggle_nodes_button)

    def center_and_resize(self):
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        width = int(rect.width() * 0.8)  # Convert to integer
        height = int(rect.height() * 0.8)  # Convert to integer
        self.resize(width, height)
        self.move(rect.center() - self.rect().center())

    def load_stl(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select STL File", "", "STL Files (*.stl);;All Files (*)", options=options)
        if file_path:
            self.stlFilePath = file_path
            if self.renderer.load_stl(file_path):
                QMessageBox.information(self, "File Load Success", "The STL file was loaded successfully!")
            else:
                QMessageBox.critical(self, "File Load Error", "There was an error loading the STL file.")
        else:
            QMessageBox.warning(self, "File Load Canceled", "STL file loading was canceled.")

    def openMaterialPropertiesDialog(self):
        dialog = MaterialPropertiesDialog(self.material_properties, self)
        dialog.exec_()

    def openLoadPropertiesDialog(self):
        dialog = LoadInputDialog(self)
        dialog.exec_()

    # def openMeshSettings(self):
    #     dialog = MeshSettingsDialog(self)
    #     dialog.exec_()

    def open_mesh_settings_dialog(self):
        # Create and open the mesh settings dialog
            dialog = MeshSettingsDialog(self)
            if dialog.exec_():  # Wait for dialog to finish and check if OK was pressed
            # Retrieve settings from the dialog
                settings = dialog.getSettings()
                # Pass settings to the renderer
                self.renderer.set_mesh_settings(settings)
                # Generate the mesh
                self.renderer.generate_mesh()  # Add this line to trigger mesh generation

    # def open_mesh_settings_dialog(self):
    #         # Create and open the mesh settings dialog
    #         dialog = MeshSettingsDialog(self)
    #         if dialog.exec_():  # Wait for dialog to finish and check if OK was pressed
    #             # Retrieve settings from the dialog
    #             settings = dialog.getSettings()
    #             # Pass settings to the renderer
    #             self.renderer.set_mesh_settings(settings)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TopologyOptimizationApp()
    window.show()
    sys.exit(app.exec_())
