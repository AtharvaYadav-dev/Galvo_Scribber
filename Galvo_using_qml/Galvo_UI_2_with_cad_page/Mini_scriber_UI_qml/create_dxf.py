import ezdxf
import os

dxf_dir = r"d:\TeamDev\Scribing_V3\Scribing_V3_UI1_with_dxf_changes_for_new_files\dxf_files"
os.makedirs(dxf_dir, exist_ok=True)
out_path = os.path.join(dxf_dir, "SPPL_Date.dxf")

doc = ezdxf.new('R2010')
msp = doc.modelspace()

text1 = msp.add_text("SPPL 12082026", dxfattribs={'height': 4})
text1.set_placement((0, 0))

doc.saveas(out_path)
print(f"Successfully saved {out_path}")
