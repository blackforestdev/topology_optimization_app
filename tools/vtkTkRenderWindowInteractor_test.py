import tkinter as tk
from vtkmodules.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

def main():
    root = tk.Tk()
    vtk_frame = vtkTkRenderWindowInteractor(root, width=400, height=300)
    vtk_frame.pack(fill="both", expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
