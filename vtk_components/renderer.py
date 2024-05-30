import logging
import numpy as np
from vtkmodules.vtkFiltersCore import vtkDelaunay3D, vtkVoronoi2D
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper, vtkRenderer, vtkRenderWindow
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.util import numpy_support
from PyQt5.QtWidgets import QFrame

class Renderer:
    def __init__(self, render_widget):
        self.render_widget = render_widget
        self.renderer = vtkRenderer()
        self.render_window = self.render_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.iren = self.render_window.GetInteractor()

        self.stl_actor = vtkActor()
        self.wireframe_actor = vtkActor()
        self.glyph_actor = vtkActor()

        self.setup_vtk_components()
        self.setup_render_window()
        logging.debug("Renderer initialized")

    def setup_vtk_components(self):
        self.setup_stl_actor()
        self.setup_wireframe_actor()
        self.setup_glyph_actor()
        self.set_background_color("#252524")

    def setup_render_window(self):
        self.iren.SetRenderWindow(self.render_window)
        self.render_window.Render()
        self.iren.Initialize()
        self.iren.Start()

    def setup_stl_actor(self):
        self.stl_mapper = vtkPolyDataMapper()
        self.stl_actor.SetMapper(self.stl_mapper)
        self.apply_material_properties(self.stl_actor)
        self.renderer.AddActor(self.stl_actor)
        logging.debug("STL actor and mapper set up")

    def setup_wireframe_actor(self):
        self.wireframe_mapper = vtkPolyDataMapper()
        self.wireframe_actor.SetMapper(self.wireframe_mapper)
        self.wireframe_actor.GetProperty().SetRepresentationToWireframe()
        self.renderer.AddActor(self.wireframe_actor)
        logging.debug("Wireframe actor and mapper set up")

    def setup_glyph_actor(self):
        self.sphere_source = vtkSphereSource()
        self.sphere_source.SetRadius(0.1)
        self.glyph_mapper = vtkPolyDataMapper()
        self.glyph_actor.SetMapper(self.glyph_mapper)
        self.renderer.AddActor(self.glyph_actor)
        logging.debug("Glyph actor and mapper set up")

    def apply_material_properties(self, actor):
        prop = actor.GetProperty()
        prop.SetColor(0.75, 0.75, 0.75)  # Silver color
        prop.SetSpecular(0.5)
        prop.SetSpecularPower(30)
        logging.debug("Applied material properties to actor")

    def set_background_color(self, color):
        r, g, b = self.hex_to_rgb(color)
        self.renderer.SetBackground(r / 255, g / 255, b / 255)
        logging.debug("Background color set")

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def load_stl(self, file_path):
        from vtkmodules.vtkIOGeometry import vtkSTLReader

        reader = vtkSTLReader()
        reader.SetFileName(file_path)
        reader.Update()
        self.stl_polydata = reader.GetOutput()

        self.stl_mapper.SetInputData(self.stl_polydata)
        self.render_window.Render()
        self.reset_camera()
        logging.debug(f"STL file loaded successfully: {file_path}")
        logging.debug(f"Number of cells in STL: {self.stl_polydata.GetNumberOfCells()}")

    def reset_camera(self):
        self.renderer.ResetCamera()
        self.render_window.Render()

    def toggle_stl_visibility(self):
        is_visible = self.stl_actor.GetVisibility()
        self.stl_actor.SetVisibility(not is_visible)
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
        delaunay = vtkDelaunay3D()
        delaunay.SetInputData(self.stl_polydata)
        delaunay.Update()
        self.update_mesh(delaunay.GetOutput())
        logging.debug("Delaunay mesh generated successfully")

    def generate_voronoi_mesh(self):
        delaunay = vtkDelaunay3D()
        delaunay.SetInputData(self.stl_polydata)
        delaunay.Update()
        logging.debug(f"Delaunay2D output has {delaunay.GetOutput().GetNumberOfPoints()} points and {delaunay.GetOutput().GetNumberOfCells()} cells")
        voronoi = vtkVoronoi2D()
        voronoi.SetInputData(delaunay.GetOutput())
        voronoi.Update()
        self.update_mesh(voronoi.GetOutput())
        logging.debug("Voronoi mesh generated successfully")

    def generate_tetrahedral_mesh(self):
        delaunay = vtkDelaunay3D()
        delaunay.SetInputData(self.stl_polydata)
        delaunay.Update()
        self.update_mesh(delaunay.GetOutput())
        logging.debug(f"Tetrahedral mesh generated successfully with {delaunay.GetOutput().GetNumberOfPoints()} points and {delaunay.GetOutput().GetNumberOfCells()} cells")

    def update_mesh(self, polydata):
        self.wireframe_mapper.SetInputData(polydata)
        self.wireframe_actor.SetVisibility(True)
        self.render_window.Render()
        logging.debug(f"Updating mesh with {polydata.GetNumberOfPoints()} points and {polydata.GetNumberOfCells()} cells")

        points = polydata.GetPoints()
        if points:
            self.update_glyphs(points)

    def update_glyphs(self, points):
        if points is None:
            logging.error("No points provided to update_glyphs method.")
            return

        num_points = points.GetNumberOfPoints()
        numpy_points = self.convert_points_to_numpy(points, num_points)
        vtk_points = self.convert_numpy_to_vtk_points(numpy_points)

        polydata = vtkPolyData()
        polydata.SetPoints(vtk_points)

        self.sphere_source.SetRadius(0.1)
        self.sphere_source.Update()

        self.glyph_mapper.SetInputData(polydata)
        self.glyph_actor.SetVisibility(True)
        self.render_window.Render()
        logging.debug("Glyphs updated")

    def convert_points_to_numpy(self, points, num_points):
        numpy_points = np.zeros((num_points, 3))
        for i in range(num_points):
            numpy_points[i, :] = points.GetPoint(i)
        return numpy_points

    def convert_numpy_to_vtk_points(self, numpy_points):
        vtk_points = vtkPoints()
        vtk_points.SetData(numpy_support.numpy_to_vtk(numpy_points))
        return vtk_points
