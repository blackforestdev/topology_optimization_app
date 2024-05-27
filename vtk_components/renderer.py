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

        # Dark theme background color
        self.renderer.SetBackground(0.1, 0.1, 0.1)
        logging.debug("Dark theme set for renderer.")
        
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
        self.glyph_actor.GetProperty().SetColor(0.3, 0.7, 0.6)  # Blue color for nodes
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

        # Set initial properties for the actor
        self.original_actor.GetProperty().SetColor(0.8, 0.8, 0.8)  # Red color
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

    def set_dark_theme(self):
        self.renderer.SetBackground(0.1, 0.1, 0.1)  # Dark grey background

    def setup_vtk_components(self):
        # Clear existing scene first
        self.renderer.RemoveAllViewProps()
        
        # Setup for the original mesh
        self.original_mapper = vtk.vtkPolyDataMapper()
        self.original_actor = vtk.vtkActor()
        self.original_actor.SetMapper(self.original_mapper)
        self.renderer.AddActor(self.original_actor)

        # Setup for the wireframe mesh overlay
        self.wireframe_mapper = vtk.vtkPolyDataMapper()
        self.wireframe_actor = vtk.vtkActor()
        self.wireframe_actor.SetMapper(self.wireframe_mapper)
        self.wireframe_actor.GetProperty().SetRepresentationToWireframe()
        self.wireframe_actor.GetProperty().SetColor(0, 0, 0)  # Black color for wireframe
        self.wireframe_actor.GetProperty().SetLineWidth(2)  # Line weight
        self.renderer.AddActor(self.wireframe_actor)

        # Sphere glyphs setup for nodes
        self.sphere_source = vtk.vtkSphereSource()
        self.sphere_source.SetRadius(0.5)  # Set the radius of the spheres
        self.glyph3D = vtk.vtkGlyph3D()
        self.glyph3D.SetSourceConnection(self.sphere_source.GetOutputPort())
        self.glyph_mapper = vtk.vtkPolyDataMapper()
        self.glyph_actor = vtk.vtkActor()
        self.glyph_actor.SetMapper(self.glyph_mapper)
        self.glyph_actor.GetProperty().SetColor(0, 0, 1)  # Blue color for nodes
        self.renderer.AddActor(self.glyph_actor)

        # Initialize mesh settings
        self.mesh_settings = {"algorithm": "Delaunay", "resolution": 5}

    def convert_unstructured_grid_to_polydata(self, unstructured_grid):
        geometry_filter = vtk.vtkGeometryFilter()
        geometry_filter.SetInputData(unstructured_grid)
        geometry_filter.Update()
        return geometry_filter.GetOutput()

    def update_mesh(self, polydata):
        self.wireframe_mapper.SetInputData(polydata)
        self.wireframe_actor.SetMapper(self.wireframe_mapper)
        self.wireframe_actor.GetProperty().SetRepresentationToWireframe()
        self.wireframe_actor.GetProperty().SetColor(0, 0, 0)  # Black color for wireframe
        self.wireframe_actor.GetProperty().SetLineWidth(5)  # Line weight

        # Extract points for glyphs
        points = polydata.GetPoints()
        polydata_glyphs = vtk.vtkPolyData()
        polydata_glyphs.SetPoints(points)

        self.glyph3D.SetInputData(polydata_glyphs)
        self.glyph3D.Update()
        self.glyph_mapper.SetInputConnection(self.glyph3D.GetOutputPort())

        self.glyph_actor.SetMapper(self.glyph_mapper)
        self.glyph_actor.GetProperty().SetColor(0.3, 0.7, 0.6)  # Blue color for nodes

        logging.debug("Mesh and glyphs updated")
        
        self.renderer.ResetCamera()
        self.vtk_frame.Render()

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
            algorithm = self.mesh_settings.get("algorithm", "Delaunay")  # Default to Delaunay if algorithm is not specified
            resolution = self.mesh_settings.get("resolution", 5)  # Default resolution to 5 if not specified

            # Placeholder mesh generation using VTK's Delaunay algorithm
            if algorithm == "Delaunay":
                delaunay = vtk.vtkDelaunay2D()
                delaunay.SetInputData(self.original_mapper.GetInput())  # Corrected input connection
                delaunay.SetAlpha(resolution)  # Set alpha parameter for Delaunay
                delaunay.Update()

                polydata = delaunay.GetOutput()
                self.update_mesh(polydata)  # Update the mesh with the generated Delaunay mesh

                # For debugging purposes, let's print a message indicating successful mesh generation
                logging.debug(f"Mesh Algorithm: {algorithm}, Resolution: {resolution}")
                logging.debug("Mesh generated successfully.")
                logging.debug(f"Number of points in generated mesh: {polydata.GetNumberOfPoints()}")
                logging.debug(f"Number of cells in generated mesh: {polydata.GetNumberOfCells()}")

        except Exception as e:
            # Print any exceptions that occur during mesh generation
            logging.error(f"Error during mesh generation: {str(e)}")

    def toggle_mesh_visibility(self):
        # Toggle visibility of the wireframe mesh
        is_visible = self.wireframe_actor.GetVisibility()
        self.wireframe_actor.SetVisibility(not is_visible)
        self.vtk_frame.Render()
        logging.debug("Wireframe visibility toggled.")

    def toggle_nodes_visibility(self):
        # Toggle visibility of the nodes
        is_visible = self.glyph_actor.GetVisibility()
        self.glyph_actor.SetVisibility(not is_visible)
        self.vtk_frame.Render()
        logging.debug("Node visibility toggled.")

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
