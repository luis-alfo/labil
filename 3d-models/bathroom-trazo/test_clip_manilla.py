#!/usr/bin/env python3
"""MVP test: the manilla snap loop (Ø42) with a short stub of the line.

The one that matters most: it tells you whether Ø42 is the FIXED sleeve next
to the wall and whether the 8 mm depth clears the moving cap.
Usage: python3 test_clip_manilla.py
"""
from shapely.geometry import box

import generate_stl as g


def main():
    xm = g.CTC / 2
    piece = g.stroke_profile().intersection(box(xm - 31, -99, xm + 33, 99))
    g.write_test_piece("test_clip_manilla", [piece], [
        "Empujada a fondo, su cara de delante queda a ras con la del caño",
        "Abraza el casquillo fijo, no el mando que se mueve",
        "Abres y cierras el agua a tope sin que el mando la roce",
        "Giras frío/caliente a tope sin que la palanca la toque",
        "Entra con un clic y no sale al tirar hacia arriba",
        "Las puntas de la boca no blanquean ni se agrietan",
    ], pads=[g.mani_pad_polygon()])
    print("Touches the cap → lower DEPTH · tight/loose → FIT ± 0.2 · "
          "cracks → MANI_WRAP -= 10")


if __name__ == "__main__":
    main()
