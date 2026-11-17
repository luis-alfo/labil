#!/usr/bin/env python3
"""MVP test: the dovetail that joins both halves, as two small blocks.

Usage: python3 test_union.py
"""
from shapely.geometry import box

import generate_stl as g


def main():
    left, right = g.split_profile(g.stroke_profile())
    window = box(-16, -99, 16, 99)
    g.write_test_piece("test_union", [left.intersection(window),
                                      right.intersection(window)], [
        "Entra a mano o con un golpe suave, sin lijar",
        "Montada no cabecea: el canto superior queda recto",
        "No se separa al tirar de los dos trozos",
    ])
    print("Play → JOINT_CLEAR = 0.05 · does not go in → JOINT_CLEAR = 0.15")


if __name__ == "__main__":
    main()
