import vtk
import numpy as np
from vtk.util.numpy_support import numpy_to_vtk

class Renderer:
    def __init__(self, vtk_widget):
        self.vtk_frame = vtk_widget
        self.renderer = vtk.vtkRenderer()
        self.setup_vtk_components()
        self.vtk_frame.GetRenderWindow().AddRenderer(self.renderer)
        self.set_dark_theme()

    def set_dark_theme(self):
        self.renderer.SetBackground(0.1, 0.1, 0.1)  # Dark grey background

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
        self.wireframe_actor.GetProperty().SetColor(0, 0, 0)  # Black color for wireframe
        self.wireframe_actor.GetProperty().SetLineWidth(2)  # Line weight
        self.renderer.AddActor(self.wireframe_actor)

        self.sphere_source = vtk.vtkSphereSource()
        self.sphere_source.SetRadius(0.05)  # Set the radius of the spheres
        self.glyph3D = vtk.vtkGlyph3D()
        self.glyph3D.SetSourceConnection(self.sphere_source.GetOutputPort())
        self.glyph_mapper = vtk.vtkPolyDataMapper()
        self.glyph_actor = vtk.vtkActor()
        self.glyph_actor.SetMapper(self.glyph_mapper)
        self.glyph_actor.GetProperty().SetColor(1, 0, 0)  # Red color for nodes
        self.renderer.AddActor(self.glyph_actor)

        self.mesh_settings = {"algorithm": "Delaunay", "resolution": 5}

    def load_stl(self, file_path):
        self.clear_scene()
        try:
            reader = vtk.vtkSTLReader()
            reader.SetFileName(file_path)
            reader.Update()
            self.original_mapper.SetInputConnection(reader.GetOutputPort())
            self.apply_material_properties(self.original_actor)
            self.set_isometric_view()
            self.reset_camera()  # Ensure the camera is reset
            self.vtk_frame.Render()
            return True
        except Exception as e:
            print(f"Failed to load STL file: {str(e)}")
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

    def reset_camera(self):
        self.renderer.ResetCamera()
        self.vtk_frame.Render()

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

                print(f"Mesh Algorithm: {algorithm}, Resolution: {resolution}")
                print("Mesh generated successfully.")
        except Exception as e:
            print(f"Error during mesh generation: {str(e)}")

    def toggle_mesh_visibility(self):
        is_visible = self.wireframe_actor.GetVisibility()
        self.wireframe_actor.SetVisibility(not is_visible)
        self.vtk_frame.Render()

    def toggle_nodes_visibility(self):
        is_visible = self.glyph_actor.GetVisibility()
        self.glyph_actor.SetVisibility(not is_visible)
        self.vtk_frame.Render()

    def apply_material_properties(self, actor):
        pass

    def set_isometric_view(self):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(1, 1, 1)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)
