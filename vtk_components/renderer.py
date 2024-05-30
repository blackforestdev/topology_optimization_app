import logging
import numpy as np
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkDelaunay3D, vtkVoronoi2D
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper, vtkRenderer, vtkLight
from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class Renderer:
    def __init__(self, render_widget: QVTKRenderWindowInteractor):
        self.render_widget = render_widget
        self.renderer = vtkRenderer()
        self.render_window = render_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetSize(1920, 1080)
        self.iren = self.render_window.GetInteractor()
        self.stl_polydata = None
        self.mesh_polydata = None
        self.mesh_algorithm = "Delaunay"
        self.mesh_resolution = 1
        self.setup_vtk_components()
        self.setup_lighting()
        logging.debug("Renderer initialized")

    def setup_vtk_components(self):
        self.original_mapper = vtkPolyDataMapper()
        self.original_actor = vtkActor()
        self.original_actor.SetMapper(self.original_mapper)

        self.wireframe_mapper = vtkPolyDataMapper()
        self.wireframe_actor = vtkActor()
        self.wireframe_actor.SetMapper(self.wireframe_mapper)
        self.wireframe_actor.GetProperty().SetRepresentationToWireframe()

        self.sphere_source = vtkSphereSource()
        self.sphere_source.SetRadius(0.1)
        self.glyph_mapper = vtkPolyDataMapper()
        self.glyph_actor = vtkActor()
        self.glyph_actor.SetMapper(self.glyph_mapper)

        self.renderer.AddActor(self.original_actor)
        self.renderer.AddActor(self.wireframe_actor)
        self.renderer.AddActor(self.glyph_actor)

        self.apply_material_properties(self.original_actor)
        logging.debug("Original actor and mapper set up.")
        logging.debug("Wireframe actor and mapper set up.")
        logging.debug("Glyph actor and mapper set up.")

    def setup_lighting(self):
        """
        Sets up lighting for the renderer
        """
        self.add_light()
        self.add_light()  # Add a second light source
        
    def add_light(self):
        """
        Adds a light source to the renderer.
        """
        light2 = vtkLight()
        light2.SetPosition(-1, -1, -1)
        self.renderer.AddLight(light2)
        logging.debug("Added second light to the renderer.")

    def apply_material_properties(self, actor):
        """
        Applies material properties to the given actor.
        """
        prop = actor.GetProperty()
        prop.SetColor(0.75, 0.75, 0.75)
        prop.SetSpecular(0.5)
        prop.SetSpecularPower(30)
        logging.debug("Applied material properties to actor.")

    def load_stl(self, file_path):
        """
        Loads an STL file from the given path.
        """
        self.stl_polydata = self.read_stl(file_path)
        if self.stl_polydata is not None:
            self.original_mapper.SetInputData(self.stl_polydata)
            self.original_actor.SetVisibility(True)
            self.reset_camera()
            logging.debug("Loaded STL file from %s.", file_path)
            logging.debug("STL contains %d cells.", self.stl_polydata.GetNumberOfCells())

    def read_stl(self, file_path):
        """
        Reads an STL file from the given path.
        """
        from vtkmodules.vtkIOGeometry import vtkSTLReader
        reader = vtkSTLReader()
        reader.SetFileName(file_path)
        reader.Update()
        return reader.GetOutput()

    def reset_camera(self):
        """
        Resets the camera and renders the window.
        """
        self.renderer.ResetCamera()
        self.render_window.Render()

    def set_mesh_settings(self, algorithm, resolution):
        """
        Sets the mesh algorithm and resolution.
        """
        self.mesh_algorithm = algorithm
        self.mesh_resolution = resolution
        logging.debug("Updated mesh settings: algorithm=%s, resolution=%d", algorithm, resolution)

    def generate_mesh(self):
        """
        Generates a mesh from the loaded STL data.
        """
        if self.stl_polydata is None:
            logging.error("No STL data loaded.")
            return

        points = self.stl_polydata.GetPoints()
        if points is None:
            logging.error("Loaded STL data contains no points.")
            return
    
    def generate_delaunay_mesh(self):
        try:
            delaunay = vtkDelaunay3D()
            delaunay.SetInputData(self.stl_polydata)
            delaunay.Update()

            self.mesh_polydata = delaunay.GetOutput()
            self.update_mesh()
            logging.debug("Delaunay mesh generated successfully")
        except Exception as e:
            logging.error(f"Error generating Delaunay mesh: {e}")

    def generate_voronoi_mesh(self):
        try:
            delaunay = vtkDelaunay3D()  # Update the appropriate class if needed
            delaunay.SetInputData(self.stl_polydata)
            delaunay.Update()

            voronoi = vtkVoronoi2D()
            voronoi.SetInputData(delaunay.GetOutput())
            voronoi.Update()

            self.mesh_polydata = voronoi.GetOutput()
            self.update_mesh()
            logging.debug("Voronoi mesh generated successfully")
        except Exception as e:
            logging.error(f"Error generating Voronoi mesh: {e}")

    def update_mesh(self):
        self.wireframe_mapper.SetInputData(self.mesh_polydata)
        self.glyph_mapper.SetInputData(self.mesh_polydata)
        self.render_window.Render()
        logging.debug("Mesh updated successfully")

    def toggle_stl_visibility(self):
        is_visible = self.original_actor.GetVisibility()
        self.original_actor.SetVisibility(not is_visible)
        self.render_window.Render()
        logging.debug(f"STL visibility toggled to {not is_visible}")

    def toggle_mesh_visibility(self):
        is_visible = self.wireframe_actor.GetVisibility()
        self.wireframe_actor.SetVisibility(not is_visible)
        self.render_window.Render()
        logging.debug(f"Mesh visibility toggled to {not is_visible}")

    def toggle_nodes_visibility(self):
        is_visible = self.glyph_actor.GetVisibility()
        self.glyph_actor.SetVisibility(not is_visible)
        self.render_window.Render()
        logging.debug(f"Nodes visibility toggled to {not is_visible}")

    def log_pipeline_info(self):
        if self.mesh_polydata:
            bounds = self.mesh_polydata.GetBounds()
            logging.debug(f"Mesh bounds: {bounds}")
            num_points = self.mesh_polydata.GetNumberOfPoints()
            num_cells = self.mesh_polydata.GetNumberOfCells()
            logging.debug(f"Mesh points: {num_points}, cells: {num_cells}")
        else:
            logging.debug("No mesh data to log")
