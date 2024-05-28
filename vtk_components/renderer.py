import logging
import vtk
import numpy as np
from vtk.util.numpy_support import numpy_to_vtk

class Renderer:
    def __init__(self, vtk_widget):
        self.vtk_widget = vtk_widget
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.vtk_frame = self.vtk_widget.GetRenderWindow()

        # Background color set to #252524
        self.renderer.SetBackground(0.145, 0.145, 0.141)
        logging.debug("Background color set to #252524.")

        self.original_actor = vtk.vtkActor()
        self.wireframe_actor = vtk.vtkActor()
        self.glyph_actor = vtk.vtkActor()

        self.renderer.AddActor(self.original_actor)
        self.renderer.AddActor(self.wireframe_actor)
        self.renderer.AddActor(self.glyph_actor)

        self.vtk_widget.Initialize()
        self.vtk_widget.Start()
        logging.debug("Renderer initialized and render window created.")

        # Initialize mesh settings
        self.mesh_settings = {"algorithm": "Delaunay", "resolution": 5}
        self.original_mapper = vtk.vtkPolyDataMapper()
        self.wireframe_mapper = vtk.vtkPolyDataMapper()
        self.glyph_mapper = vtk.vtkPolyDataMapper()

        self.sphere_source = vtk.vtkSphereSource()
        self.sphere_source.SetRadius(0.1)  # Set the radius of the spheres
        self.glyph3D = vtk.vtkGlyph3D()
        self.glyph3D.SetSourceConnection(self.sphere_source.GetOutputPort())
        self.glyph_mapper = vtk.vtkPolyDataMapper()
        self.glyph_actor = vtk.vtkActor()
        self.glyph_actor.SetMapper(self.glyph_mapper)
        self.glyph_actor.GetProperty().SetColor(0.21, 0.64, 0.54)  # #36a48a color for nodes
        self.renderer.AddActor(self.glyph_actor)

    def load_stl(self, file_path):
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_path)
        reader.Update()

        poly_data = reader.GetOutput()
        logging.debug(f"Number of cells in STL: {poly_data.GetNumberOfCells()}")

        if poly_data.GetNumberOfCells() == 0:
            logging.error("Failed to load STL file or STL file is empty.")
            return False

        self.original_mapper.SetInputData(poly_data)
        self.original_actor.SetMapper(self.original_mapper)

        logging.debug("STL file loaded successfully")

        # Set initial properties for the actor to a silver metallic color
        self.original_actor.GetProperty().SetColor(0.75, 0.75, 0.75)  # Light grey color
        self.original_actor.GetProperty().SetSpecular(0.5)
        self.original_actor.GetProperty().SetSpecularPower(30)
        self.original_actor.GetProperty().SetOpacity(1.0)  # Fully opaque

        logging.debug(f"Actor visibility: {self.original_actor.GetVisibility()}")
        logging.debug(f"Actor position: {self.original_actor.GetPosition()}")
        logging.debug(f"Actor bounds: {self.original_actor.GetBounds()}")

        # Reset camera and render
        self.renderer.ResetCamera()
        self.vtk_frame.Render()
        logging.debug("Camera reset and scene rendered.")

        return True

    def toggle_stl_visibility(self):
        is_visible = self.original_actor.GetVisibility()
        self.original_actor.SetVisibility(not is_visible)
        self.vtk_frame.Render()
        logging.debug("STL visibility toggled.")

    def reset_camera(self):
        self.renderer.ResetCamera()
        self.vtk_frame.Render()
        logging.debug("Camera reset and scene rendered.")

    def convert_unstructured_grid_to_polydata(self, unstructured_grid):
        geometry_filter = vtk.vtkGeometryFilter()
        geometry_filter.SetInputData(unstructured_grid)
        geometry_filter.Update()
        return geometry_filter.GetOutput()

    def update_mesh(self, mesh):
        if isinstance(mesh, vtk.vtkPolyData):
            self.wireframe_mapper.SetInputData(mesh)
            self.wireframe_actor.GetProperty().SetColor(0, 0, 0)
            self.wireframe_actor.GetProperty().SetRepresentationToWireframe()
            self.wireframe_actor.SetVisibility(True)

            # Update the glyphs for the nodes
            self.glyph3D.SetInputData(mesh)
            self.glyph3D.Update()
            self.glyph_mapper.SetInputConnection(self.glyph3D.GetOutputPort())
            self.glyph_actor.SetVisibility(True)

            self.renderer.ResetCamera()
            self.vtk_frame.Render()
        else:
            logging.error(f"update_mesh received an unexpected mesh type: {type(mesh)}")

    def clear_scene(self):
        points = vtk.vtkPoints()
        cells = vtk.vtkCellArray()

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(cells)

        self.renderer.RemoveAllViewProps()

        self.wireframe_mapper.SetInputData(polydata)

        # Update glyphs for the nodes
        self.glyph3D.SetInputData(polydata)
        self.glyph3D.Update()
        self.glyph_mapper.SetInputConnection(self.glyph3D.GetOutputPort())

        self.renderer.ResetCamera()
        self.vtk_frame.Render()

    def generate_mesh(self):
        try:
            algorithm = self.mesh_settings.get("algorithm", "Delaunay")
            resolution = self.mesh_settings.get("resolution", 5)

            logging.debug(f"Generating mesh with algorithm: {algorithm}, resolution: {resolution}")

            if algorithm == "Delaunay":
                delaunay = vtk.vtkDelaunay2D()
                delaunay.SetInputData(self.stl_polydata)
                delaunay.SetAlpha(resolution)
                delaunay.Update()
                output = delaunay.GetOutput()
                self.update_mesh(output)
                logging.debug(f"Delaunay2D output: {output}")

            elif algorithm == "Voronoi":
                voronoi = vtk.vtkVoronoi2D()
                voronoi.SetInputData(self.stl_polydata)
                voronoi.Update()
                output = voronoi.GetOutput()
                self.update_mesh(output)
                logging.debug(f"Voronoi output: {output}")

            elif algorithm == "Tetrahedral":
                delaunay3d = vtk.vtkDelaunay3D()
                delaunay3d.SetInputData(self.stl_polydata)
                delaunay3d.Update()
                geometry_filter = vtk.vtkGeometryFilter()
                geometry_filter.SetInputConnection(delaunay3d.GetOutputPort())
                geometry_filter.Update()
                output = geometry_filter.GetOutput()
                self.update_mesh(output)
                logging.debug(f"Tetrahedral output: {output}")

            else:
                raise ValueError(f"Unsupported mesh generation algorithm: {algorithm}")

        except Exception as e:
            logging.error(f"Error during mesh generation: {str(e)}")

        self.vtk_frame.Render()

    def set_mesh_settings(self, settings):
        self.mesh_settings = settings
        logging.debug(f"Mesh settings updated: {self.mesh_settings}")

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

'''
    def apply_material_properties(self, actor):
        # Implement your material properties here
        # This method could set color, opacity, etc. for the actor
        pass

    def set_isometric_view(self):
        # Implement the logic to set the camera to an isometric view
        # For example:
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(1, 1, 1)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)

    def set_mesh_settings(self, settings):
        self.mesh_settings = settings
        logging.debug(f"Mesh settings updated: {settings}")
'''