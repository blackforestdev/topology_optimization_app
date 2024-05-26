# gui/controls.py
import tkinter as tk

def create_gui_controls(master, load_stl_func, set_constraint_value_func, set_max_iterations_func, start_optimization_func):
    tk.Button(master, text="Load STL", command=load_stl_func).pack()
    tk.Button(master, text="Set Constraint Value", command=set_constraint_value_func).pack()
    tk.Button(master, text="Set Max Iterations", command=set_max_iterations_func).pack()
    tk.Button(master, text="Start Optimization", command=start_optimization_func).pack()
