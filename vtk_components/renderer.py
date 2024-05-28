import vtk
import numpy as np
from vtk.util.numpy_support import numpy_to_vtk
import logging

logging.basicConfig(filename="renderer.log", level=logging.DEBUG)

class Renderer:
    def __init__(self, vtk_widget):
        self.vtk_frame = vtk_widget
        self.renderer = vtk.vtkRenderer()
        self.setup_vtk_components()
        self.vtk_frame.GetRenderWindow().AddRenderer(self.renderer)
        self.set_dark_theme()
        self.stl_polydata = None

    def set_dark_theme(self):
        self.renderer.SetBackground(0.14, 0.14, 0.14)  # Dark grey background

    def setup_vtk_components(self):
        self.renderer.RemoveAllViewProps()
        self.original_mapper = vtk.vtkPolyDataMapper()
        self.original_actor = vtk.vtkActor()
        self.original_actor.SetMapper(self.original_mapper)
        self.renderer.AddActor(self.original_actor)
        self.wireframe_mapper = vtk.vtkPolyDataMapper()
        self.wireframe_actor = vtk.vtkActor()
        self.wireframe_actor.SetMapper(self.wireframe_mapper)
        self.wireframe_actor.GetProperty().SetRepresentationToWireframe()
        self.wireframe_actor.GetProperty().SetColor(0, 0, 0)
        self.wireframe_actor.GetProperty().SetLineWidth(2)
        self.renderer.AddActor(self.wireframe_actor)
        self.sphere_source = vtk.vtkSphereSource()
        self.sphere_source.SetRadius(0.1)
        self.glyph3D = vtk.vtkGlyph3D()
        self.glyph3D.SetSourceConnection(self.sphere_source.GetOutputPort())
        self.glyph_mapper = vtk.vtkPolyDataMapper()
        self.glyph_actor = vtk.vtkActor()
        self.glyph_actor.SetMapper(self.glyph_mapper)
        self.glyph_actor.GetProperty().SetColor(0.211, 0.643, 0.541)
        self.renderer.AddActor(self.glyph_actor)
        self.mesh_settings = {"algorithm": "Delaunay", "resolution": 5}

    def load_stl(self, file_path):
        self.clear_scene()
        try:
            reader = vtk.vtkSTLReader()
            reader.SetFileName(file_path)
            reader.Update()
            self.stl_polydata = reader.GetOutput()
            self.original_mapper.SetInputData(self.stl_polydata)
            self.apply_material_properties(self.original_actor)
            self.set_isometric_view()
            self.renderer.ResetCamera()
            self.vtk_frame.Render()
            logging.debug(f"STL file loaded successfully: {file_path}")
            logging.debug(f"Number of cells in STL: {self.stl_polydata.GetNumberOfCells()}")
            return True
        except Exception as e:
            logging.error(f"Failed to load STL file: {str(e)}")
            return False

    def generate_mesh(self):
        if not self.stl_polydata:
            logging.error("STL Polydata is not loaded.")
            return
        try:
            algorithm = self.mesh_settings.get("algorithm", "Delaunay")
            logging.debug(f"Generating mesh using algorithm: {algorithm}")

            if algorithm == "Delaunay":
                delaunay = vtk.vtkDelaunay2D()
                delaunay.SetInputData(self.stl_polydata)
                delaunay.Update()
                mesh_output = delaunay.GetOutput()
                logging.debug(f"Delaunay mesh generated with {mesh_output.GetNumberOfCells()} cells.")
                self.update_mesh(mesh_output)

            elif algorithm == "Voronoi":
                logging.debug("Setting up Delaunay2D for Voronoi.")
                delaunay = vtk.vtkDelaunay2D()
                delaunay.SetInputData(self.stl_polydata)
                delaunay.Update()
                delaunay_output = delaunay.GetOutput()
                logging.debug(f"Delaunay2D for Voronoi generated with {delaunay_output.GetNumberOfCells()} cells.")

                if delaunay_output.GetNumberOfCells() > 0:
                    logging.debug("Setting up Voronoi2D.")
                    try:
                        voronoi = vtk.vtkVoronoi2D()
                        logging.debug("Voronoi2D object created.")
                        voronoi.SetInputData(delaunay_output)
                        logging.debug("Input data set for Voronoi2D.")
                        voronoi.Update()
                        logging.debug("Voronoi2D update called.")
                        voronoi_output = voronoi.GetOutput()
                        logging.debug(f"Voronoi mesh generated with {voronoi_output.GetNumberOfCells()} cells.")
                        self.update_mesh(voronoi_output)
                    except Exception as e:
                        logging.error(f"Error during Voronoi mesh generation: {str(e)}")
                else:
                    logging.error("Delaunay2D output for Voronoi has no cells, skipping Voronoi generation.")

            elif algorithm == "Tetrahedral":
                delaunay = vtk.vtkDelaunay3D()
                delaunay.SetInputData(self.stl_polydata)
                delaunay.Update()
                mesh_output = delaunay.GetOutput()
                geometry_filter = vtk.vtkGeometryFilter()
                geometry_filter.SetInputData(mesh_output)
                geometry_filter.Update()
                mesh_output = geometry_filter.GetOutput()
                logging.debug(f"Tetrahedral mesh generated with {mesh_output.GetNumberOfCells()} cells.")
                self.update_mesh(mesh_output)

            logging.debug(f"Mesh Algorithm: {algorithm}")
            logging.debug("Mesh generated successfully.")
        except Exception as e:
            logging.error(f"Error during mesh generation: {str(e)}")

    def update_mesh(self, mesh):
        try:
            logging.debug(f"Updating mesh with {mesh.GetNumberOfPoints()} points and {mesh.GetNumberOfCells()} cells.")

            self.wireframe_mapper.SetInputData(mesh)
            self.wireframe_actor.VisibilityOn()

            self.sphere_source.SetRadius(0.1)
            glyph3D = vtk.vtkGlyph3D()
            glyph3D.SetSourceConnection(self.sphere_source.GetOutputPort())
            glyph3D.SetInputData(mesh)
            glyph3D.Update()
            self.glyph_mapper.SetInputConnection(glyph3D.GetOutputPort())
            self.glyph_actor.VisibilityOn()

            self.renderer.ResetCamera()
            self.vtk_frame.Render()
        except Exception as e:
            logging.error(f"Error during mesh update: {str(e)}")

    def clear_scene(self):
        self.stl_polydata = None
        self.renderer.RemoveAllViewProps()
        self.setup_vtk_components()
        self.renderer.ResetCamera()
        self.vtk_frame.Render()

    def apply_material_properties(self, actor):
        prop = actor.GetProperty()
        prop.SetColor(0.75, 0.75, 0.75)  # Silver color
        prop.SetSpecular(0.5)
        prop.SetSpecularPower(30)

    def set_isometric_view(self):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(100, 100, 100)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)

    def reset_camera(self):
        self.renderer.ResetCamera()
        self.vtk_frame.Render()

    def toggle_stl_visibility(self):
        is_visible = self.original_actor.GetVisibility()
        self.original_actor.SetVisibility(not is_visible)
        self.vtk_frame.Render()

    def toggle_mesh_visibility(self):
        is_visible = self.wireframe_actor.GetVisibility()
        self.wireframe_actor.SetVisibility(not is_visible)
        self.vtk_frame.Render()

    def toggle_nodes_visibility(self):
        is_visible = self.glyph_actor.GetVisibility()
        self.glyph_actor.SetVisibility(not is_visible)
        self.vtk_frame.Render()

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