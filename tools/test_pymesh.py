import pymesh

def test_pymesh():
    try:
        # Load a simple mesh
        mesh = pymesh.load_mesh("path_to_a_sample_stl_file.stl")
        print(f"Mesh vertices: {mesh.vertices}")
        print(f"Mesh faces: {mesh.faces}")

        # Check if meshutils is accessible (replace with an actual function if meshutils is a valid module)
        if hasattr(pymesh, 'meshutils'):
            print("meshutils module is accessible.")
        else:
            print("meshutils module is NOT accessible.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    test_pymesh()
