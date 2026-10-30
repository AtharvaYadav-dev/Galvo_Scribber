with open('qml/components/cad/CadCanvas.qml', 'r', encoding='utf-8') as f:
    text = f.read()

old_group_text = """                            } else if (ch.type === "text") {
                                ctx.fillStyle = isSel ? penColor : cPen
                                ctx.font = (ch.bold ? "bold " : "") + (ch.italic ? "italic " : "") + Math.round(cH * 0.75) + "px sans-serif"
                                ctx.textAlign = "center"
                                ctx.textBaseline = "middle"
                                ctx.fillText(ch.text || "TEXT", 0, 0)
                            }"""

new_group_text = """                            } else if (ch.type === "text") {
                                ctx.fillStyle = isSel ? penColor : cPen
                                ctx.font = (ch.bold ? "bold " : "") + (ch.italic ? "italic " : "") + Math.round(cH * 0.75) + "px '" + (ch.fontFamily || "Segoe UI") + "', sans-serif"
                                ctx.textAlign = "center"
                                ctx.textBaseline = "alphabetic"
                                ctx.fillText(ch.text || "TEXT", 0, cH * 0.25)
                            }"""

old_linear_text = """                        } else {
                            // Linear Text Mode: Multi-line and alignment support
                            var lines = txt.split("\\n")
                            var lineH = sh / Math.max(1, lines.length)
                            ctx.font = fontStyle + Math.max(8, Math.round(lineH * 0.85)) + "px '" + fFamily + "', sans-serif"

                            for (var lIdx = 0; lIdx < lines.length; lIdx++) {
                                var lY = (-sh / 2) + (lIdx + 0.5) * lineH
                                var lX = 0
                                if (tAlign === "left") lX = -sw / 2
                                else if (tAlign === "right") lX = sw / 2
                                ctx.fillText(lines[lIdx], lX, lY)
                            }
                        }"""

new_linear_text = """                        } else {
                            // Linear Text Mode: Multi-line and alignment support (alphabetic baseline prevents Marathi/Devanagari font descent shift)
                            var lines = txt.split("\\n")
                            var lineH = sh / Math.max(1, lines.length)
                            ctx.font = fontStyle + Math.max(8, Math.round(lineH * 0.85)) + "px '" + fFamily + "', sans-serif"
                            ctx.textBaseline = "alphabetic"

                            for (var lIdx = 0; lIdx < lines.length; lIdx++) {
                                var lY = (-sh / 2) + (lIdx + 0.75) * lineH
                                var lX = 0
                                if (tAlign === "left") lX = -sw / 2
                                else if (tAlign === "right") lX = sw / 2
                                ctx.fillText(lines[lIdx], lX, lY)
                            }
                        }"""

assert old_group_text in text, "old_group_text not found"
assert old_linear_text in text, "old_linear_text not found"

text = text.replace(old_group_text, new_group_text, 1)
text = text.replace(old_linear_text, new_linear_text, 1)

with open('qml/components/cad/CadCanvas.qml', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated CadCanvas.qml with alphabetic baseline text centering fix")

