# vtk_components/interactor.py
import vtk

def setup_interactor(render_window, highlight_selection_callback):
    picker = vtk.vtkCellPicker()
    picker.AddObserver("EndPickEvent", highlight_selection_callback)
    render_window.GetInteractor().SetPicker(picker)

