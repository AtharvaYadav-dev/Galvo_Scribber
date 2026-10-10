import ezdxf

# create test dxf
with open("test.dxf", "w") as f:
    f.write("  0\nSECTION\n  2\nENTITIES\n")
    f.write("  0\nLWPOLYLINE\n100\nAcDbEntity\n  8\n0\n100\nAcDbPolyline\n 90\n5\n 70\n1\n")
    f.write(" 10\n0.0\n 20\n0.0\n")
    f.write(" 10\n10.0\n 20\n0.0\n")
    f.write(" 10\n10.0\n 20\n10.0\n")
    f.write(" 10\n0.0\n 20\n10.0\n")
    f.write(" 10\n0.0\n 20\n0.0\n")
    f.write("  0\nENDSEC\n  0\nEOF\n")

doc = ezdxf.readfile("test.dxf")
msp = doc.modelspace()
for entity in msp:
    print(entity.dxftype())
