import logging
import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkDelaunay2D, vtkDelaunay3D, vtkVoronoi2D
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper, vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor, vtkLight
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonTransforms import vtkTransform

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Renderer:
    def __init__(self, render_widget):
        self.render_widget = render_widget
        self.renderer = vtkRenderer()
        self.render_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.render_widget.GetRenderWindow().GetInteractor()

        # Set up actors
        self.original_actor = vtkActor()
        self.wireframe_actor = vtkActor()
        self.glyph_actor = vtkActor()

        # Add actors to renderer
        self.renderer.AddActor(self.original_actor)
        self.renderer.AddActor(self.wireframe_actor)
        self.renderer.AddActor(self.glyph_actor)

        self.setup_vtk_components()
        self.set_dark_theme()

        # Logging initialization complete
        logging.debug("Renderer initialized")

    def setup_vtk_components(self):
        # Initializing and setting up the mapper and actors
        self.original_mapper = vtkPolyDataMapper()
        self.wireframe_mapper = vtkPolyDataMapper()
        self.glyph_mapper = vtkPolyDataMapper()

        self.original_actor.SetMapper(self.original_mapper)
        self.wireframe_actor.SetMapper(self.wireframe_mapper)
        self.glyph_actor.SetMapper(self.glyph_mapper)

        # Set up light sources
        light1 = vtkLight()
        light1.SetPosition(1, 1, 1)
        light2 = vtkLight()
        light2.SetPosition(-1, -1, -1)
        self.renderer.AddLight(light1)
        self.renderer.AddLight(light2)
        
        # Logging setup completion
        logging.debug("Original actor and mapper set up.")
        logging.debug("Wireframe actor and mapper set up.")
        logging.debug("Glyph actor and mapper set up.")
        logging.debug("Dark theme set for renderer.")
        logging.debug("Light 1 added to the renderer.")
        logging.debug("Light 2 added to the renderer.")
        
    def set_dark_theme(self):
        self.renderer.SetBackground(0.145, 0.145, 0.145)
        self.renderer.GradientBackgroundOn()
        self.renderer.SetBackground2(0.290, 0.290, 0.290)
        
    def apply_material_properties(self, actor):
        prop = actor.GetProperty()
        prop.SetColor(0.75, 0.75, 0.75)  # Silver color
        prop.SetSpecular(0.5)
        prop.SetSpecularPower(30)
        logging.debug("Applied material properties to actor")

    def reset_camera(self):
        self.renderer.ResetCamera()
        self.render_widget.GetRenderWindow().Render()

    def load_stl(self, file_path):
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_path)
        reader.Update()

        self.stl_polydata = reader.GetOutput()
        self.original_mapper.SetInputData(self.stl_polydata)
        self.apply_material_properties(self.original_actor)

        logging.debug(f"STL file loaded successfully: {file_path}")
        logging.debug(f"Number of cells in STL: {self.stl_polydata.GetNumberOfCells()}")

        return True

    def set_mesh_settings(self, algorithm, resolution):
        self.mesh_algorithm = algorithm
        self.mesh_resolution = resolution
        logging.debug(f"Mesh settings updated: algorithm={algorithm}, resolution={resolution}")

    def generate_mesh(self):
        if not hasattr(self, 'stl_polydata'):
            logging.error("STL polydata not loaded")
            return

        points = self.stl_polydata.GetPoints()
        if points is None:
            logging.error("STL polydata has no points")
            return

        num_points = points.GetNumberOfPoints()
        if num_points == 0:
            logging.error("STL polydata has no points")
            return

        logging.debug(f"Generating mesh using algorithm: {self.mesh_algorithm}")

        if self.mesh_algorithm == "Delaunay":
            self.generate_delaunay_mesh()
        elif self.mesh_algorithm == "Voronoi":
            self.generate_voronoi_mesh()
        elif self.mesh_algorithm == "Tetrahedral":
            self.generate_tetrahedral_mesh()

    def generate_delaunay_mesh(self):
        delaunay = vtkDelaunay2D()
        delaunay.SetInputData(self.stl_polydata)
        delaunay.Update()
        
        mesh_polydata = delaunay.GetOutput()
        self.update_mesh(mesh_polydata)
        
        logging.debug("Delaunay mesh generated successfully")

    def generate_voronoi_mesh(self):
        try:
            logging.debug("Setting up Delaunay2D for Voronoi.")
            delaunay = vtk.vtkDelaunay2D()
            delaunay.SetInputData(self.stl_polydata)
            delaunay.Update()

            delaunay_output = delaunay.GetOutput()
            logging.debug(f"Delaunay2D for Voronoi generated with {delaunay_output.GetNumberOfCells()} cells.")
            self.log_polydata_info(delaunay_output, "Delaunay2D output")

            logging.debug("Setting up Voronoi2D.")
            voronoi = vtk.vtkVoronoi2D()
            voronoi.SetInputData(delaunay_output)
            voronoi.Update()

            voronoi_output = voronoi.GetOutput()
            logging.debug(f"Voronoi2D generated with {voronoi_output.GetNumberOfCells()} cells.")
            self.log_polydata_info(voronoi_output, "Voronoi2D output")

            self.update_mesh(voronoi_output)
            logging.debug("Voronoi mesh generated successfully.")
        except Exception as e:
            logging.error(f"Error generating Voronoi mesh: {e}")
            self.log_vtk_error()

    def log_polydata_info(self, polydata, label="PolyData"):
        logging.debug(f"{label} has {polydata.GetNumberOfPoints()} points and {polydata.GetNumberOfCells()} cells.")
        if polydata.GetNumberOfPoints() > 0:
            bounds = polydata.GetBounds()
            logging.debug(f"{label} bounds: {bounds}")

    def log_vtk_error(self):
        # Implement logging for detailed VTK errors if needed
        pass

    def update_mesh(self, polydata):
        self.wireframe_mapper.SetInputData(polydata)
        self.wireframe_actor.VisibilityOn()
        self.vtk_widget.GetRenderWindow().Render()
        logging.debug(f"Updating mesh with {polydata.GetNumberOfPoints()} points and {polydata.GetNumberOfCells()} cells")
    def log_polydata_info(self, polydata, label="PolyData"):
        logging.debug(f"{label} has {polydata.GetNumberOfPoints()} points and {polydata.GetNumberOfCells()} cells.")
        if polydata.GetNumberOfPoints() > 0:
            bounds = polydata.GetBounds()
            logging.debug(f"{label} bounds: {bounds}")

    def generate_tetrahedral_mesh(self):
        delaunay = vtkDelaunay3D()
        delaunay.SetInputData(self.stl_polydata)
        delaunay.Update()

        mesh_polydata = delaunay.GetOutput()
        self.update_mesh(mesh_polydata)
        
        logging.debug("Tetrahedral mesh generated successfully")

    def update_mesh(self, mesh_polydata):
        self.wireframe_mapper.SetInputData(mesh_polydata)
        self.wireframe_actor.GetProperty().SetRepresentationToWireframe()
        self.wireframe_actor.GetProperty().SetColor(0, 0, 0)  # Black lines
        self.wireframe_actor.SetVisibility(True)

        self.update_glyphs(mesh_polydata)
        
        self.render_widget.GetRenderWindow().Render()

        logging.debug(f"Updating mesh with {mesh_polydata.GetNumberOfPoints()} points and {mesh_polydata.GetNumberOfCells()} cells")

    def update_glyphs(self, mesh_polydata):
        points = mesh_polydata.GetPoints()
        glyphs = vtk.vtkGlyph3D()
        glyph_source = vtkSphereSource()
        glyph_source.SetRadius(0.1)  # Node size

        glyphs.SetSourceConnection(glyph_source.GetOutputPort())
        glyphs.SetInputData(mesh_polydata)
        glyphs.ScalingOff()
        glyphs.Update()

        self.glyph_mapper.SetInputConnection(glyphs.GetOutputPort())
        self.glyph_actor.GetProperty().SetColor(0.212, 0.643, 0.541)  # #36a48a color
        self.glyph_actor.SetVisibility(True)

        logging.debug("Glyphs updated")

    def toggle_stl_visibility(self):
        is_visible = self.original_actor.GetVisibility()
        self.original_actor.SetVisibility(not is_visible)
        self.render_widget.GetRenderWindow().Render()
        logging.debug(f"STL visibility toggled to {not is_visible}")

    def toggle_mesh_visibility(self):
        is_visible = self.wireframe_actor.GetVisibility()
        self.wireframe_actor.SetVisibility(not is_visible)
        self.render_widget.GetRenderWindow().Render()
        logging.debug(f"Mesh visibility toggled to {not is_visible}")

    def toggle_nodes_visibility(self):
        is_visible = self.glyph_actor.GetVisibility()
        self.glyph_actor.SetVisibility(not is_visible)
        self.render_widget.GetRenderWindow().Render()
        logging.debug(f"Nodes visibility toggled to {not is_visible}")

    def clear_scene(self):
        self.original_actor.VisibilityOff()
        self.wireframe_actor.VisibilityOff()
        self.glyph_actor.VisibilityOff()
        self.render_widget.GetRenderWindow().Render()
        logging.debug("Scene cleared")
