import vtk

def main():
    # Create a cone
    cone = vtk.vtkConeSource()
    cone.SetHeight(3.0)
    cone.SetRadius(1.0)
    cone.SetResolution(10)
    
    # Create a mapper and actor
    cone_mapper = vtk.vtkPolyDataMapper()
    cone_mapper.SetInputConnection(cone.GetOutputPort())
    
    cone_actor = vtk.vtkActor()
    cone_actor.SetMapper(cone_mapper)

    # Create a renderer and render window
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.SetWindowName("Test Cone")
    render_window.AddRenderer(renderer)
    
    # Create a render window interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)
    
    # Add the actor to the scene
    renderer.AddActor(cone_actor)
    renderer.SetBackground(0.1, 0.2, 0.4)  # Background color blue
    
    # Render and start interaction
    render_window.Render()
    render_window_interactor.Start()

if __name__ == "__main__":
    main()
