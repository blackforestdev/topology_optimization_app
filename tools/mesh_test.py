import vtk
import logging

# Configure logging
logging.basicConfig(filename='mesh_test.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_delaunay2D(input_polydata):
    try:
        delaunay = vtk.vtkDelaunay2D()
        delaunay.SetInputData(input_polydata)
        delaunay.Update()
        polydata = delaunay.GetOutput()
        logging.debug(f"Delaunay2D output: {polydata}")
        return polydata
    except Exception as e:
        logging.error(f"Error generating Delaunay2D mesh: {str(e)}")
        return None

def generate_voronoi2D(input_polydata):
    try:
        delaunay = vtk.vtkDelaunay2D()
        delaunay.SetInputData(input_polydata)
        delaunay.Update()
        polydata = delaunay.GetOutput()
        logging.debug(f"Delaunay2D output for Voronoi: {polydata}")
        
        voronoi = vtk.vtkVoronoi2D()
        voronoi.SetInputData(polydata)
        voronoi.Update()
        polydata = voronoi.GetOutput()
        logging.debug(f"Voronoi2D output: {polydata}")
        return polydata
    except Exception as e:
        logging.error(f"Error generating Voronoi2D mesh: {str(e)}")
        return None

def generate_tetrahedral(input_polydata):
    try:
        tetrahedral = vtk.vtkDelaunay3D()
        tetrahedral.SetInputData(input_polydata)
        tetrahedral.Update()
        unstructured_grid = tetrahedral.GetOutput()
        logging.debug(f"Tetrahedral output: {unstructured_grid}")

        converter = vtk.vtkGeometryFilter()
        converter.SetInputData(unstructured_grid)
        converter.Update()
        polydata = converter.GetOutput()
        logging.debug(f"Converted Tetrahedral output to PolyData: {polydata}")
        return polydata
    except Exception as e:
        logging.error(f"Error generating Tetrahedral mesh: {str(e)}")
        return None

def main():
    # Create a simple input polydata (e.g., a plane or cube)
    source = vtk.vtkCubeSource()
    source.Update()
    input_polydata = source.GetOutput()
    logging.debug(f"Input polydata: {input_polydata}")
    logging.debug(f"Number of points in input: {input_polydata.GetNumberOfPoints()}")
    logging.debug(f"Number of cells in input: {input_polydata.GetNumberOfCells()}")

    # Test Delaunay 2D
    delaunay_polydata = generate_delaunay2D(input_polydata)
    logging.debug(f"Delaunay2D PolyData: {delaunay_polydata}")

    # Test Voronoi 2D
    voronoi_polydata = generate_voronoi2D(input_polydata)
    logging.debug(f"Voronoi2D PolyData: {voronoi_polydata}")

    # Test Tetrahedral
    tetrahedral_polydata = generate_tetrahedral(input_polydata)
    logging.debug(f"Tetrahedral PolyData: {tetrahedral_polydata}")

if __name__ == "__main__":
    main()
