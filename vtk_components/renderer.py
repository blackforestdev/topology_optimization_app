import vtk
import numpy as np
import logging
from vtk.util.numpy_support import numpy_to_vtk

# Configure logging
logging.basicConfig(filename='renderer.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Renderer:
    def __init__(self, vtk_widget):
        self.vtk_frame = vtk_widget
        self.renderer = vtk.vtkRenderer()
        self.setup_vtk_components()
        self.vtk_frame.GetRenderWindow().AddRenderer(self.renderer)
        self.set_dark_theme()
        self.add_lighting()
        self.start_interactor()
        logging.debug("Renderer initialized and render window created.")

    def set_dark_theme(self):
        self.renderer.SetBackground(0.1, 0.1, 0.1)  # Dark grey background
        logging.debug("Dark theme set for renderer.")

    def setup_vtk_components(self):
        self.renderer.RemoveAllViewProps()
        
        self.original_mapper = vtk.vtkPolyDataMapper()
        self.original_actor = vtk.vtkActor()
        self.original_actor.SetMapper(self.original_mapper)
        self.original_actor.SetVisibility(True)
        self.renderer.AddActor(self.original_actor)
        logging.debug("Original actor and mapper set up.")

        self.wireframe_mapper = vtk.vtkPolyDataMapper()
        self.wireframe_actor = vtk.vtkActor()
        self.wireframe_actor.SetMapper(self.wireframe_mapper)
        self.wireframe_actor.GetProperty().SetRepresentationToWireframe()
        self.wireframe_actor.GetProperty().SetColor(0, 0, 0)  # Black color for wireframe
        self.wireframe_actor.GetProperty().SetLineWidth(2)  # Line weight
        self.wireframe_actor.SetVisibility(True)
        self.renderer.AddActor(self.wireframe_actor)
        logging.debug("Wireframe actor and mapper set up.")

        self.sphere_source = vtk.vtkSphereSource()
        self.sphere_source.SetRadius(0.05)  # Set the radius of the spheres
        self.glyph3D = vtk.vtkGlyph3D()
        self.glyph3D.SetSourceConnection(self.sphere_source.GetOutputPort())
        self.glyph_mapper = vtk.vtkPolyDataMapper()
        self.glyph_actor = vtk.vtkActor()
        self.glyph_actor.SetMapper(self.glyph_mapper)
        self.glyph_actor.GetProperty().SetColor(1, 0, 0)  # Red color for nodes
        self.glyph_actor.SetVisibility(True)
        self.renderer.AddActor(self.glyph_actor)
        logging.debug("Glyph actor and mapper set up.")

        self.mesh_settings = {"algorithm": "Delaunay", "resolution": 5}
        logging.debug("Mesh settings initialized.")

    def add_lighting(self):
        light1 = vtk.vtkLight()
        light1.SetPosition(1, 1, 1)
        light1.SetFocalPoint(0, 0, 0)
        self.renderer.AddLight(light1)
        logging.debug("Light 1 added to the renderer.")

        light2 = vtk.vtkLight()
        light2.SetPosition(-1, -1, -1)
        light2.SetFocalPoint(0, 0, 0)
        self.renderer.AddLight(light2)
        logging.debug("Light 2 added to the renderer.")

    def start_interactor(self):
        self.vtk_interactor = self.vtk_frame.GetRenderWindow().GetInteractor()
        self.vtk_interactor.Initialize()
        self.vtk_interactor.Start()
        logging.debug("Render window interactor started.")

    def load_stl(self, file_path):
        self.clear_scene()
        try:
            logging.debug(f"Attempting to load STL file from: {file_path}")
            reader = vtk.vtkSTLReader()
            reader.SetFileName(file_path)
            reader.Update()

            if not reader.GetOutput().GetNumberOfCells():
                raise ValueError("STL file contains no data or is corrupted")

            self.original_mapper.SetInputConnection(reader.GetOutputPort())
            self.original_actor.SetVisibility(True)
            self.apply_material_properties(self.original_actor)

            # Ensure actor is visible and log its position
            self.original_actor.SetVisibility(True)
            position = self.original_actor.GetPosition()
            logging.debug(f"Actor position: {position}")

            # Set a uniform scale if necessary
            scale = self.original_actor.GetScale()
            logging.debug(f"Actor scale: {scale}")
            if scale == (1.0, 1.0, 1.0):
                self.original_actor.SetScale(1.0, 1.0, 1.0)

            self.set_isometric_view()
            self.reset_camera()
            self.vtk_frame.Render()
            logging.debug("STL file loaded successfully")
            logging.debug(f"Number of cells in STL: {reader.GetOutput().GetNumberOfCells()}")

            bounds = self.original_actor.GetBounds()
            logging.debug(f"Actor bounds: {bounds}")

            camera = self.renderer.GetActiveCamera()
            logging.debug(f"Camera position: {camera.GetPosition()}")
            logging.debug(f"Camera focal point: {camera.GetFocalPoint()}")
            logging.debug(f"Camera view up: {camera.GetViewUp()}")

            self.vtk_frame.GetRenderWindow().Render()
            logging.debug("Render window updated.")

            return True
        except Exception as e:
            logging.error(f"Failed to load STL file: {str(e)}")
            return False

    def update_mesh(self, mesh):
        if hasattr(mesh, 'vertices') and hasattr(mesh, 'faces'):
            vertices = np.array(mesh.vertices, dtype='float32')
            faces = np.array(mesh.faces, dtype='int32')

            points = vtk.vtkPoints()
            for vertex in vertices:
                points.InsertNextPoint(vertex)

            cells = vtk.vtkCellArray()
            for face in faces:
                if len(face) == 3:  # Assuming triangular faces
                    triangle = vtk.vtkTriangle()
                    triangle.GetPointIds().SetId(0, face[0])
                    triangle.GetPointIds().SetId(1, face[1])
                    triangle.GetPointIds().SetId(2, face[2])
                    cells.InsertNextCell(triangle)

            polydata = vtk.vtkPolyData()
            polydata.SetPoints(points)
            polydata.SetPolys(cells)

            self.wireframe_mapper.SetInputData(polydata)

            self.glyph3D.SetInputData(polydata)
            self.glyph3D.Update()
            self.glyph_mapper.SetInputConnection(self.glyph3D.GetOutputPort())

            self.renderer.ResetCamera()
            self.vtk_frame.Render()

    def clear_scene(self):
        self.renderer.RemoveAllViewProps()
        logging.debug("Scene cleared.")

    def reset_camera(self):
        camera = self.renderer.GetActiveCamera()
        camera.SetClippingRange(0.1, 1000)
        camera.SetViewAngle(30)
        self.renderer.ResetCamera()
        self.vtk_frame.Render()
        logging.debug("Camera reset and scene rendered.")

    def generate_mesh(self):
        try:
            algorithm = self.mesh_settings.get("algorithm", "Delaunay")
            resolution = self.mesh_settings.get("resolution", 5)

            if algorithm == "Delaunay":
                delaunay = vtk.vtkDelaunay2D()
                delaunay.SetInputConnection(self.original_mapper.GetOutputPort())
                delaunay.SetAlpha(resolution)
                delaunay.Update()

                self.update_mesh(delaunay.GetOutput())

                logging.debug(f"Mesh Algorithm: {algorithm}, Resolution: {resolution}")
                logging.debug("Mesh generated successfully.")
        except Exception as e:
            logging.error(f"Error during mesh generation: {str(e)}")

    def toggle_stl_visibility(self):
        is_visible = self.original_actor.GetVisibility()
        self.original_actor.SetVisibility(not is_visible)
        self.vtk_frame.Render()
        logging.debug("STL visibility toggled.")

    def toggle_mesh_visibility(self):
        is_visible = self.wireframe_actor.GetVisibility()
        self.wireframe_actor.SetVisibility(not is_visible)
        self.vtk_frame.Render()
        logging.debug("Mesh visibility toggled.")

    def toggle_nodes_visibility(self):
        is_visible = self.glyph_actor.GetVisibility()
        self.glyph_actor.SetVisibility(not is_visible)
        self.vtk_frame.Render()
        logging.debug("Nodes visibility toggled.")

    def apply_material_properties(self, actor):
        actor.GetProperty().SetColor(0.8, 0.8, 0.8)  # Light grey color for the STL model
        logging.debug("Material properties applied to the actor.")

    def set_isometric_view(self):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(100, 100, 100)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)
        self.renderer.ResetCamera()
        logging.debug("Camera set to isometric view.")

        logging.debug(f"Camera clipping range: {camera.GetClippingRange()}")
        logging.debug(f"Camera view angle: {camera.GetViewAngle()}")

        self.vtk_frame.GetRenderWindow().Render()
        logging.debug("Render window updated after setting isometric view.")
