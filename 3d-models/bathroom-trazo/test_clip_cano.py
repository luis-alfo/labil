#!/usr/bin/env python3
"""MVP test: the caño snap loop (Ø29) with a short stub of the line.

Prints in ~20 min. Validates the fit on the spout and gives you a piece of
line to try the jinetes on. Usage: python3 test_clip_cano.py
"""
from shapely.geometry import box

import generate_stl as g


def main():
    xc = -g.CTC / 2
    piece = g.stroke_profile().intersection(box(xc - 30, -99, xc + 30, 99))
    g.write_test_piece("test_clip_cano", [piece], [
        "Entra desde arriba con un clic, sin forzar",
        "Queda pegada al embellecedor cromado, sin tocar la pared",
        "No sale al tirar hacia arriba con un dedo",
        "Las puntas de la boca no blanquean ni se agrietan",
        "Un jinete entra en el tramo recto y no baila",
    ])
    print("Tight → FIT += 0.2 · loose → FIT -= 0.2 · cracks → CANO_WRAP -= 10")


if __name__ == "__main__":
    main()
