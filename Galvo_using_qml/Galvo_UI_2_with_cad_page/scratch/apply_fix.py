with open('qml/components/cad/CadInspectorPanel.qml', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace property var selectedShape declaration
old_decl = """    property var shapesModel: []
    property int modelRevision: 0
    onShapesModelChanged: modelRevision++
    property int selectedIndex: -1
    property var selectedShape: (modelRevision >= 0 && selectedIndex >= 0 && selectedIndex < shapesModel.length) ? shapesModel[selectedIndex] : null"""

new_decl = """    property var shapesModel: []
    property int selectedIndex: -1
    property var selectedShape: null

    function syncSelectedShape() {
        if (selectedIndex >= 0 && shapesModel && selectedIndex < shapesModel.length) {
            selectedShape = shapesModel[selectedIndex]
        } else {
            selectedShape = null
        }
    }

    onSelectedIndexChanged: syncSelectedShape()
    onShapesModelChanged: syncSelectedShape()"""

old_decl_crlf = old_decl.replace('\n', '\r\n')
new_decl_crlf = new_decl.replace('\n', '\r\n')

if old_decl_crlf in text:
    text = text.replace(old_decl_crlf, new_decl_crlf, 1)
    print("Replaced selectedShape declaration successfully (CRLF)")
elif old_decl in text:
    text = text.replace(old_decl, new_decl, 1)
    print("Replaced selectedShape declaration successfully (LF)")
else:
    print("WARNING: old_decl not found!")

# 2. Remove line 1512 rogue closing brace
# Search for the block around line 1510
old_rogue = """                        }
                    }

                                    }

                    // 5. DEDICATED 2D BARCODE & QR CODE INSPECTOR"""

new_clean = """                        }
                    }

                    // 5. DEDICATED 2D BARCODE & QR CODE INSPECTOR"""

old_rogue_crlf = old_rogue.replace('\n', '\r\n')
new_clean_crlf = new_clean.replace('\n', '\r\n')

if old_rogue_crlf in text:
    text = text.replace(old_rogue_crlf, new_clean_crlf, 1)
    print("Removed rogue brace successfully (CRLF)")
elif old_rogue in text:
    text = text.replace(old_rogue, new_clean, 1)
    print("Removed rogue brace successfully (LF)")
else:
    print("WARNING: old_rogue not found!")

# 3. Add closing brace for StackLayout before the last two closing braces
# The end of the file has:
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     }
# We need one more closing brace for StackLayout
old_end = """                                CadInput { label: "Start TC"; unit: "µs"; text: "300" }
                                CadInput { label: "Laser Off"; unit: "µs"; text: "100" }
                                CadInput { label: "End TC"; unit: "µs"; text: "300" }
                                CadInput { label: "Poly TC"; unit: "µs"; text: "100" }
                            }
                        }
                    }
                }
            }
        }
    }"""

new_end = """                                CadInput { label: "Start TC"; unit: "µs"; text: "300" }
                                CadInput { label: "Laser Off"; unit: "µs"; text: "100" }
                                CadInput { label: "End TC"; unit: "µs"; text: "300" }
                                CadInput { label: "Poly TC"; unit: "µs"; text: "100" }
                            }
                        }
                    }
                }
            }
        }
    }
}"""

old_end_crlf = old_end.replace('\n', '\r\n')
new_end_crlf = new_end.replace('\n', '\r\n')

if old_end_crlf in text:
    text = text.replace(old_end_crlf, new_end_crlf, 1)
    print("Added closing brace at end successfully (CRLF)")
elif old_end in text:
    text = text.replace(old_end, new_end, 1)
    print("Added closing brace at end successfully (LF)")
else:
    print("WARNING: old_end not found!")

with open('qml/components/cad/CadInspectorPanel.qml', 'w', encoding='utf-8') as f:
    f.write(text)
print("Saved CadInspectorPanel.qml")

