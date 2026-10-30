import ezdxf
import sys
import os

def get_dxf_starting_position(filepath):
    try:
        # Read the DXF file
        doc = ezdxf.readfile(filepath)
        msp = doc.modelspace()

        # Get the bounding box of all entities in the modelspace
        # ezdxf provides a fast way to get the bounding box
        from ezdxf import bbox
        
        entities = list(msp)
        if not entities:
            print("The DXF file is empty.")
            return None

        # Calculate bounding box
        cache = bbox.Cache()
        box = bbox.extents(entities, cache=cache)

        if box.has_data:
            xmin, ymin, _ = box.extmin
            xmax, ymax, _ = box.extmax
            
            width = xmax - xmin
            height = ymax - ymin
            
            print(f"DXF File: {os.path.basename(filepath)}")
            print("-" * 30)
            print(f"Starting Position (Min X, Min Y): ({xmin:.3f}, {ymin:.3f})")
            print(f"Ending Position (Max X, Max Y):   ({xmax:.3f}, {ymax:.3f})")
            print(f"Total Width:  {width:.3f}")
            print(f"Total Height: {height:.3f}")
            print("-" * 30)
            
            return (xmin, ymin)
        else:
            print("Could not determine bounding box for this DXF.")
            return None

    except IOError:
        print(f"Error: Could not read file {filepath}")
    except ezdxf.DXFError as e:
        print(f"Error: Invalid DXF file - {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dxf_info.py <path_to_dxf_file>")
    else:
        dxf_path = sys.argv[1]
        get_dxf_starting_position(dxf_path)
