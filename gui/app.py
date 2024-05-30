import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QVBoxLayout, QDialog, QLabel, QLineEdit, QComboBox, QHBoxLayout, QPushButton
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk_components.renderer import Renderer

class TopologyOptimizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Topology Optimization App")
        self.setGeometry(100, 100, 1200, 800)
        self.showMaximized()

        self.material_properties = {"color": (1.0, 0.0, 0.0), "opacity": 1.0}

        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.setCentralWidget(self.vtk_widget)

        self.renderer = Renderer(self.vtk_widget)
        self.create_menus()
        logging.debug("UI setup complete")

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
        material_properties_action.triggered.connect(self.open_material_properties_dialog)
        material_menu.addAction(material_properties_action)

        load_menu = menu_bar.addMenu("&Load")
        load_settings_action = QAction("&Properties", self)
        load_settings_action.triggered.connect(self.open_load_properties_dialog)
        load_menu.addAction(load_settings_action)

        view_menu = menu_bar.addMenu("&View")
        toggle_stl_action = QAction("Toggle &STL Visibility", self)
        toggle_stl_action.triggered.connect(self.renderer.toggle_stl_visibility)
        view_menu.addAction(toggle_stl_action)

        toggle_mesh_action = QAction("Toggle &Mesh Visibility", self)
        toggle_mesh_action.triggered.connect(self.renderer.toggle_mesh_visibility)
        view_menu.addAction(toggle_mesh_action)

        toggle_nodes_action = QAction("Toggle &Nodes Visibility", self)
        toggle_nodes_action.triggered.connect(self.renderer.toggle_nodes_visibility)
        view_menu.addAction(toggle_nodes_action)

    def load_stl(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open STL File", "", "STL Files (*.stl)")
        if file_path:
            self.renderer.load_stl(file_path)
            self.renderer.reset_camera()

    def open_mesh_settings_dialog(self):
        settings = {"algorithm": self.renderer.mesh_algorithm, "resolution": self.renderer.mesh_resolution}
        dialog = MeshSettingsDialog(settings)
        if dialog.exec():
            settings = dialog.get_settings()
            self.renderer.set_mesh_settings(settings["algorithm"], settings["resolution"])
            self.renderer.generate_mesh()

    def open_material_properties_dialog(self):
        dialog = MaterialPropertiesDialog(self.material_properties)
        if dialog.exec():
            self.material_properties = dialog.get_properties()

    def open_load_properties_dialog(self):
        dialog = LoadInputDialog()
        if dialog.exec():
            load_properties = dialog.get_load_properties()
            # Handle load properties

class MaterialPropertiesDialog(QDialog):
    def __init__(self, properties, parent=None):
        super().__init__(parent)
        self.properties = properties
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Color:"))
        self.color_input = QLineEdit(str(self.properties["color"]))
        layout.addWidget(self.color_input)

        layout.addWidget(QLabel("Opacity:"))
        self.opacity_input = QLineEdit(str(self.properties["opacity"]))
        layout.addWidget(self.opacity_input)

        submit_button = QPushButton('Submit', self)
        submit_button.clicked.connect(self.submit)
        layout.addWidget(submit_button)

    def submit(self):
        self.properties["color"] = eval(self.color_input.text())
        self.properties["opacity"] = float(self.opacity_input.text())
        self.accept()

    def get_properties(self):
        return self.properties

class LoadInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.load_type = QComboBox(self)
        self.load_type.addItems(["Force", "Pressure", "Thermal"])
        layout.addWidget(QLabel("Load Type:"))
        layout.addWidget(self.load_type)

        self.magnitude_label = QLabel("Magnitude:", self)
        self.magnitude = QLineEdit(self)
        layout.addWidget(self.magnitude_label)
        layout.addWidget(self.magnitude)

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

        self.temperature_label = QLabel("Temperature Change (°C):", self)
        self.temperature = QLineEdit(self)
        layout.addWidget(self.temperature_label)
        layout.addWidget(self.temperature)

        submit_button = QPushButton('Submit', self)
        submit_button.clicked.connect(self.submit)
        layout.addWidget(submit_button)

        self.load_type.currentIndexChanged.connect(self.update_load_type)
        self.update_load_type()

    def submit(self):
        self.accept()

    def update_load_type(self):
        load_type = self.load_type.currentText()
        if load_type == "Thermal":
            self.magnitude_label.hide()
            self.magnitude.hide()
            self.direction_layout.hide()
            self.temperature_label.show()
            self.temperature.show()
        else:
            self.magnitude_label.show()
            self.magnitude.show()
            self.direction_layout.show()
            self.temperature_label.hide()
            self.temperature.hide()

    def get_load_properties(self):
        load_type = self.load_type.currentText()
        properties = {"type": load_type}
        if load_type == "Thermal":
            properties["temperature_change"] = float(self.temperature.text())
        else:
            properties["magnitude"] = float(self.magnitude.text())
            properties["direction"] = (float(self.direction_x.text()), float(self.direction_y.text()), float(self.direction_z.text()))
        return properties

class MeshSettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Mesh Algorithm:"))
        self.algorithm_input = QComboBox(self)
        self.algorithm_input.addItems(["Delaunay", "Voronoi", "Tetrahedral"])
        self.algorithm_input.setCurrentText(self.settings["algorithm"])
        layout.addWidget(self.algorithm_input)

        layout.addWidget(QLabel("Mesh Resolution:"))
        self.resolution_input = QLineEdit(str(self.settings["resolution"]))
        layout.addWidget(self.resolution_input)

        submit_button = QPushButton('Submit', self)
        submit_button.clicked.connect(self.submit)
        layout.addWidget(submit_button)

    def submit(self):
        self.settings["algorithm"] = self.algorithm_input.currentText()
        self.settings["resolution"] = int(self.resolution_input.text())
        self.accept()

    def get_settings(self):
        return self.settings

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    window = TopologyOptimizationApp()
    window.show()
    window.showMaximized()
    sys.exit(app.exec_())
