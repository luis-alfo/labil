// larc hq · cajonera colgada del elevador de pantalla
// Fuente de verdad del diseño. generate_stl.py la pasa por OpenSCAD.
//
// Marco de montaje (mm): x a la derecha, y hacia el fondo de la mesa, z arriba.
//   y = 0  canto delantero del tablero del elevador
//   z = 0  cara de abajo del tablero
//
// Piezas:  A carcasa (perfil con pinza y bandeja de bolis)
//          B cajón A5        C cajón pequeño
//          T prueba de la pinza (rebanada de A)
// part = "A" | "B" | "C" | "T"  -> orientación de impresión
// part = "A_use" | "B_use" | "C_use" -> en su sitio

part = "A_use";

// --- elevador (medido con tarjetas de 85,6 × 54 mm; ver APRENDIZAJES.md) ---
board_t     = 12.0;    // grosor del tablero  [ESTIMADO en foto: confirmar con la prueba T]
board_depth = 225;     // fondo del tablero: 54 + 85,6 + 85,6 (tres tarjetas)
free_h      = 85;      // alto libre bajo el tablero: una tarjeta de pie

// --- carcasa ---
W        = 250;        // ancho total (la A1 hace 256)
back_y   = 219;        // hasta dónde llega hacia el fondo (< board_depth)
web_t    = 3.0;        // pared que sube por delante del canto
top_t    = 2.0;        // placa pegada a la cara de abajo del tablero
wall_t   = 2.0;        // paredes laterales y central
H        = 44;         // alto total bajo el tablero (quedan free_h - H para el portátil)
ledge_w  = 8;          // ancho de los carriles donde apoyan los cajones
ledge_t  = 2.0;
bay_a5   = 156;        // hueco del cajón A5
bay_small = W - 3 * wall_t - bay_a5;   // hueco del cajón pequeño (88)

// --- pinza al canto delantero y bandeja de bolis ---
slot_c   = 0.4;        // holgura de la pinza sobre el grosor del tablero
lip_len  = 33;         // lo que entra la pinza encima del tablero (el pie del monitor está a ~42)
lip_t    = 2.4;        // suelo de la bandeja (el grabado se come 0,6)
tray_len = 160;        // largo de la bandeja: un boli mide ~145
tray_w   = 26;         // ancho del suelo: dos bolis de ~11 mm
tray_h   = 5;          // alto del borde
tray_rim = 3;

// --- grabado, como El Secadero ---
label       = "LARC HQ | V1 | 191126";   // fecha de diseño: 19 nov 2026
label_size  = 8;
label_depth = 0.6;

// --- cajones ---
gap_side  = 0.5;       // holgura a cada lado
gap_z     = 0.4;       // holgura arriba y abajo
dr_wall   = 1.2;
dr_floor  = 1.2;
panel_t   = 2.4;       // frente, por delante de la carcasa
panel_gap = 1.0;       // rendija entre los dos frentes
notch_r   = 13;        // muesca para el dedo
dr_back   = 216;       // hasta dónde llega el cajón cerrado

// --- tope de los cajones: lengüeta flexible en la placa de arriba ---
tongue_w    = 10;
tongue_y0   = 8;
tongue_y1   = 34;
tongue_t    = 1.0;     // el resto de top_t queda libre para que suba
hook_h      = 1.2;     // lo que baja el diente (el cajón tiene gap_z = 0,4 -> engancha 0,8)

// --- cinta de doble cara al fondo ---
pad_w = 40; pad_d = 16; pad_depth = 0.5;
pad_x = [-95, 0, 95];

// --- aligerado de la placa de arriba: ranuras a lo largo ---
slot_y0 = 48; slot_y1 = 198;

use <../el-secadero-v2/fonts/JetBrainsMono-Bold.ttf>

$fn = 64;
e = 0.01;

x_l   = -W / 2;                       // cara exterior izquierda
a5_x0 = x_l + wall_t;                 // hueco A5
div_x = a5_x0 + bay_a5;               // pared central
sm_x0 = div_x + wall_t;               // hueco pequeño
lip_z = board_t + slot_c;             // cara de abajo de la pinza
tray_z = lip_z + lip_t;               // suelo de la bandeja

module box(x0, x1, y0, y1, z0, z1) {
    translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]);
}

// perfil 2D en (y, z) extruido a lo ancho entre x0 y x1
module yz(x0, x1, pts) {
    translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(x1 - x0) polygon(pts);
}

module slot(x0, x1) {   // ranura con punta a 45° hacia el fondo: se imprime sin puentes
    w = x1 - x0;
    translate([0, 0, -top_t - e]) linear_extrude(top_t + 2 * e)
        polygon([[x0, slot_y0], [x1, slot_y0], [x1, slot_y1 - w / 2],
                 [(x0 + x1) / 2, slot_y1], [x0, slot_y1 - w / 2]]);
}

module tongue_cut(xc) {
    s = 1.2;
    difference() {      // ranura en U: la lengüeta nace delante y queda libre hacia el fondo
        box(xc - tongue_w / 2 - s, xc + tongue_w / 2 + s, tongue_y0, tongue_y1 + s, -top_t - e, e);
        box(xc - tongue_w / 2, xc + tongue_w / 2, tongue_y0 - e, tongue_y1, -top_t - 1, 1);
    }
    // hueco encima de la lengüeta para que pueda subir
    box(xc - tongue_w / 2 - e, xc + tongue_w / 2 + e, tongue_y0 - 3, tongue_y1 + e, -(top_t - tongue_t), e);
}

module tongue_hook(xc) {   // rampa suave al meter el cajón, cara a 60° al sacarlo
    yz(xc - tongue_w / 2, xc + tongue_w / 2,
       [[tongue_y1 - 12, -top_t + e], [tongue_y1 - 4, -top_t - hook_h],
        [tongue_y1 - 2.7, -top_t - hook_h], [tongue_y1 - 2, -top_t + e]]);
}

module carcasa() {
    a5_c = a5_x0 + bay_a5 / 2;
    sm_c = sm_x0 + bay_small / 2;
    difference() {
        union() {
            // placa de arriba
            box(x_l, -x_l, -web_t, back_y, -top_t, 0);
            // paredes
            for (x = [x_l, div_x, -x_l - wall_t]) box(x, x + wall_t, -web_t, back_y, -H, -top_t + e);
            // carriles
            for (x = [a5_x0 - e, div_x - ledge_w, sm_x0 - e, -x_l - wall_t - ledge_w])
                box(x, x + ledge_w + e, -web_t, back_y, -H, -H + ledge_t);
            // pinza: pared delantera + labio sobre el tablero (canto trasero achaflanado para entrar)
            box(x_l, -x_l, -web_t, 0, -top_t, tray_z);
            yz(x_l, -x_l, [[-e, lip_z], [lip_len - 1.2, lip_z], [lip_len, lip_z + 1.2],
                           [lip_len, tray_z], [-e, tray_z]]);
            yz(x_l, -x_l, [[0, lip_z + e], [1, lip_z + e], [-e, lip_z - 1]]);   // acuerdo interior
            // borde de la bandeja de bolis
            box(-tray_len / 2 - tray_rim, tray_len / 2 + tray_rim, -web_t, lip_len, tray_z - e, tray_z + tray_h);
        }
        // bandeja: fondo plano y pared trasera a 45° (se imprime sin soportes)
        yz(-tray_len / 2, tray_len / 2,
           [[0, tray_z], [tray_w, tray_z], [tray_w + tray_h + e, tray_z + tray_h + e], [0, tray_z + tray_h + e]]);
        // grabado en el fondo de la bandeja, se lee desde delante
        translate([0, tray_w / 2, tray_z - label_depth]) linear_extrude(label_depth + e)
            text(label, size = label_size, font = "JetBrains Mono:style=Bold", halign = "center", valign = "center");
        // aligerado
        slot(a5_c - 55, a5_c - 10);
        slot(a5_c + 10, a5_c + 55);
        slot(sm_c - 22, sm_c + 22);
        // lengüetas de tope
        tongue_cut(a5_c);
        tongue_cut(sm_c);
        // asientos de la cinta de doble cara
        for (x = pad_x) box(x - pad_w / 2, x + pad_w / 2, back_y - 3 - pad_d, back_y - 3, -pad_depth, e);
    }
    tongue_hook(a5_c);
    tongue_hook(sm_c);
}

// cajón: bay_x0/bay_w = su hueco; px0/px1 = extremos del frente; div_y = separador (0 = sin)
module cajon(bay_x0, bay_w, px0, px1, div_y = 0) {
    x0 = bay_x0 + gap_side;
    x1 = bay_x0 + bay_w - gap_side;
    z0 = -H + ledge_t + gap_z;
    z1 = -top_t - gap_z;
    xc = (px0 + px1) / 2;
    difference() {
        union() {
            box(x0, x1, -web_t - e, dr_back, z0, z1);
            // frente con las esquinas de arriba redondeadas
            hull() {
                box(px0, px1, -web_t - panel_t, -web_t, z0, z0 + 1);
                for (x = [px0 + 2, px1 - 2]) translate([x, -web_t, -0.6 - 2])
                    rotate([90, 0, 0]) cylinder(r = 2, h = panel_t, $fn = 24);
            }
        }
        box(x0 + dr_wall, x1 - dr_wall, -web_t, dr_back - dr_wall, z0 + dr_floor, 1);
        // muesca para el dedo
        translate([xc, 0, -0.6]) rotate([90, 0, 0]) cylinder(r = notch_r, h = 20, center = true);
    }
    if (div_y > 0) box(x0 + e, x1 - e, div_y, div_y + 1.2, z0 + e, -8);
}

module cajon_a5()    { cajon(a5_x0, bay_a5, x_l, div_x + wall_t / 2 - panel_gap / 2); }
module cajon_small() { cajon(sm_x0, bay_small, div_x + wall_t / 2 + panel_gap / 2, -x_l, div_y = 85); }

module prueba() {   // rebanada de la pinza: comprueba el grosor del tablero antes de imprimir A
    intersection() {
        carcasa();
        box(90, 115, -web_t - 1, 40, -top_t - 1, 40);
    }
}

// carcasa y prueba se imprimen de pie sobre su cara delantera: todo son paredes verticales
module de_pie() { translate([0, 0, web_t]) rotate([90, 0, 0]) children(); }
module en_suelo() { translate([0, 0, H - ledge_t - gap_z]) children(); }

if (part == "A") de_pie() carcasa();
else if (part == "T") de_pie() prueba();
else if (part == "B") en_suelo() cajon_a5();
else if (part == "C") en_suelo() cajon_small();
else if (part == "A_use") carcasa();
else if (part == "B_use") cajon_a5();
else if (part == "C_use") cajon_small();
