// =====================================================================
//  Soporte de estropajo para grifo — V5
//
//  Cuatro piezas en PLA, sin soportes y sin doblar nada al montar:
//    A = brazo: abrazadera en U (faldón fino alrededor del embellecedor,
//        agarre en la columna) + brazo plano de 3 mm a ras de encimera
//    K = cuña: cierra la U por detrás de la columna y la aprieta al bajarla
//    B = marco: bastidor plano con forma de percha (se imprime tumbado, todo trabaja en el
//        plano de las capas). Cabalga sobre la punta del brazo y apoya sus dos
//        esquinas de abajo en la pared del fregadero.
//    C = cuna: el estropajo va de canto sobre nervios. Gira entre las dos
//        aletas del marco; levantada pasa entre las patas, se apoya en la pared
//        del fregadero a ~100° y se queda sola.
//
//  Ejes (posición de uso):  z = 0 superficie de la encimera
//                           x = 0 canto de la encimera (x<0 encimera, x>0 fregadero)
//                           eje de la columna del grifo en x = -edge_dist
// =====================================================================

/* [Qué generar] */
part = "assembly"; // ["A", "K", "B", "C", "assembly", "folded", "A_use", "K_use", "B_use", "C_use", "sponge"]
fold = 0;          // ángulo de la cuna en el montaje (0 = abajo)

/* [Grifo y fregadero] */
col_d        = 45;   // Ø columna (la V1 se imprimió para 45 y encajó)
flange_d_max = 59;   // el embellecedor cabe si mide hasta este Ø (estimado en fotos: ~57)
flange_h_max = 6.5;  // ...y hasta esta altura (estimado en fotos: ~5,5)
edge_dist    = 59;   // eje de la columna -> canto (sale del brazo de la V1, que llegaba justo)
sink_d       = 400;  // Ø del hueco del fregadero (supuesto)
sink_wall_x  = 0;    // pared del fregadero respecto al canto, a 8 cm de profundidad (supuesto)

/* [Estropajo] */
sponge = [45, 95, 70];  // grosor, largo, alto (de canto, apoyado en el lado largo)

/* [Abrazadera y cuña] */
col_clr    = 0.3;
skirt_wall = 1.6;
shell_t    = 2.6;
collar_h   = 22;
key_ang    = 12;    // cuña autoblocante
key_h      = 8;
key_t0     = 4;     // grosor de la cuña abajo
key_tongue = 2.6;   // cuánto entra en cada lado de la U
ear_t      = 5.8;

/* [Brazo y punta] */
arm_w  = 22;
arm_t  = 3;
nose_t = 5;         // la punta engrosa para alojar el marco enrasado
web_w  = 18;        // ancho del alma bajo el puente del marco
web_t  = 2;
stub_l = 4.2;       // testa por delante del marco

/* [Marco] */
frame_t = 6;        // grosor (x): se imprime tumbado sobre esta cara
leg_w   = 6.5;     // brazos inclinados de la percha
sh_out  = 15.5;     // semiancho de los hombros
fin_t   = 5.5;      // aletas con la bisagra
fin_clr = 0.5;
pocket_r = 4.0;
slot_w   = 4.2;
slot_ang = 60;      // la cuna entra y sale solo a este ángulo
tie_h    = 4;
tie_t    = 3.5;     // el tirante es más fino que el marco

/* [Cuna] */
drop     = 78;      // de la encimera a los nervios donde apoya el estropajo
wall     = 1.6;
wall_h   = 15;      // 12 mm por encima de los nervios
floor_h  = 3;
back_u   = 12;      // la cuna sobresale esto por detrás del eje
back_h   = 6;       // por detrás la pared es baja: el respaldo es el propio marco
pin_u    = 10;      // tetón de tope, por delante del eje
tr_len   = 7.5;     // muñón: 7,5 × 3,6 con dos caras planas
tr_h     = 3.6;

$fn = 72;
eps = 0.01;

// ---------------------------------------------------------------------
x_col   = -edge_dist;
r_grip  = col_d / 2 + col_clr;
r_skirt = flange_d_max / 2 + 0.25;
z1      = flange_h_max + 0.5;                 // fin del faldón
z2      = z1 + (r_skirt - r_grip);            // fin del chaflán a 45°
key_tt  = key_t0 + key_h * tan(key_ang);      // grosor de la cuña arriba
back    = col_d / 2 + key_tt + 4.5;           // la U llega esto por detrás del eje
zp0     = collar_h - key_h - 1.5;             // suelo del alojamiento de la cuña
xk0     = -col_d / 2 - key_t0 + 1.5 * tan(key_ang);  // cara trasera del alojamiento, abajo

in_x = sponge[0] + 4;                         // interior de la cuna
in_y = sponge[1] + 6;
cr_y = in_y / 2 + wall;                       // semiancho exterior de la cuna
fin_y0 = cr_y + fin_clr;
fin_y1 = fin_y0 + fin_t;
function sag(y) = sink_d / 2 - sqrt(pow(sink_d / 2, 2) - y * y);
frame_x0 = max(7, sink_wall_x + sag(fin_y1) + 0.1);  // cara trasera del marco
gx0 = frame_x0 - 0.2;
gx1 = frame_x0 + frame_t + 0.2;
nose_x0 = 3;
nose_x1 = gx1 + stub_l;
x_a  = frame_x0 + frame_t + (wall_h - tr_h / 2) + 0.1;  // eje de la bisagra
z_c0 = -drop - floor_h;                       // base de la cuna
z_a  = z_c0 + tr_h / 2;
u0 = -back_u;                                  // cuna en coordenadas locales (u, v)
u1 = u0 + in_x + 2 * wall;
z_k = z_a + u1 + 5;                            // codo de la percha, por encima de la cuna levantada

module u2d(r, b) { circle(r = r, $fn = 120); translate([-b, -r]) square([b, 2 * r]); }
module rrect(x0, x1, y0, y1, r) {
    hull() for (x = [x0 + r, x1 - r], y = [y0 + r, y1 - r]) translate([x, y]) circle(r = r, $fn = 24);
}
module bar2d(p, q, w) { hull() { translate(p) circle(d = w); translate(q) circle(d = w); } }
// extruye un perfil dibujado en (x, z) entre y0 e y1
module xz(y0, y1) { translate([0, y1, 0]) rotate([90, 0, 0]) linear_extrude(y1 - y0) children(); }

// =========================== A: BRAZO =================================
module part_A() {
    difference() {
        union() {
            translate([x_col, 0, 0]) {
                linear_extrude(z1) u2d(r_skirt + skirt_wall, back);
                hull() {
                    translate([0, 0, z1 - eps]) linear_extrude(eps) u2d(r_skirt + skirt_wall, back);
                    translate([0, 0, z2]) linear_extrude(eps) u2d(r_grip + shell_t, back);
                }
                translate([0, 0, z2]) linear_extrude(collar_h - z2) u2d(r_grip + shell_t, back);
                // orejas que alojan la cuña
                for (s = [-1, 1]) translate([-back, s > 0 ? r_grip - 1 : -r_grip - ear_t, zp0 - 2])
                    cube([back - 19, ear_t + 1, collar_h - zp0 + 2]);
            }
            // brazo de 3 mm y punta de 5 mm
            xs = x_col + r_skirt + 0.5;
            translate([xs, -arm_w / 2, 0]) cube([nose_x0 - xs, arm_w, arm_t]);
            hull() {
                translate([nose_x0 - 6, -arm_w / 2, 0]) cube([eps, arm_w, arm_t]);
                translate([nose_x0, -arm_w / 2, 0]) cube([nose_x1 - nose_x0, arm_w, nose_t]);
            }
            // cartela brazo–abrazadera
            xz(-1.5, 1.5) polygon([[xs - 9, arm_t - eps], [xs + 11, arm_t - eps],
                                   [x_col + r_grip + shell_t - 0.5, z2 - 0.5]]);
        }
        translate([x_col, 0, 0]) {
            // canal escalonado abierto por detrás: embellecedor abajo, columna arriba
            translate([0, 0, -1]) linear_extrude(z1 + 1) u2d(r_skirt, back + 5);
            hull() {
                translate([0, 0, z1 - eps]) linear_extrude(eps) u2d(r_skirt, back + 5);
                translate([0, 0, z2]) linear_extrude(eps) u2d(r_grip, back + 5);
            }
            translate([0, 0, z2 - eps]) linear_extrude(collar_h) u2d(r_grip, back + 5);
            // alojamientos de la cuña: cara trasera inclinada
            for (s = [-1, 1])
                xz(s > 0 ? r_grip - 1 : -r_grip - key_tongue - 0.3, s > 0 ? r_grip + key_tongue + 0.3 : -r_grip + 1)
                    polygon([[-20, zp0], [xk0, zp0],
                             [xk0 - (collar_h + 1 - zp0) * tan(key_ang), collar_h + 1], [-20, collar_h + 1]]);
        }
        // punta: el marco entra de frente por encima de la testa y cae en la ranura
        translate([gx0, -web_w / 2, web_t]) cube([gx1 - gx0, web_w, nose_t]);            // ranura del puente
        for (s = [-1, 1]) {
            translate([gx0, s > 0 ? web_w / 2 : -arm_w, -1]) cube([gx1 - gx0, arm_w - web_w / 2, nose_t + 2]);
            translate([gx1 - eps, s > 0 ? web_w / 2 - 0.4 : -arm_w, -1])
                cube([stub_l + 1, arm_w - web_w / 2 + 0.4, nose_t + 2]);                  // testa más estrecha
        }
    }
}

// =========================== K: CUÑA ==================================
module part_K() {
    translate([x_col, 0, 0]) {
        zb = zp0 + 1.5;
        xz(-r_grip - key_tongue, r_grip + key_tongue)
            polygon([[-col_d / 2, zb], [-col_d / 2 - key_t0, zb],
                     [-col_d / 2 - key_tt, zb + key_h], [-col_d / 2, zb + key_h]]);
        translate([-col_d / 2 - 3, -6, zb + key_h - eps]) cube([3, 12, 2.5]);   // tirador
    }
}

// =========================== B: MARCO =================================
module frame2d() {   // en (y, z)
    difference() {
        translate([-sh_out, -4]) square([2 * sh_out, nose_t + 4]);
        translate([-web_w / 2 - 0.3, -5]) square([web_w + 0.6, web_t + 0.1 + 5]);
    }
    // patas verticales por fuera de la cuna (al levantarla pasa entre ellas) y
    // brazos inclinados hasta la punta del brazo
    for (s = [-1, 1]) {
        bar2d([s * (sh_out - leg_w / 2), -2.5], [s * (fin_y0 + fin_t / 2), z_k], leg_w);
        translate([s > 0 ? fin_y0 : -fin_y1, z_a - 8.5]) square([fin_t, z_k - z_a + 8.5]);
    }
}
module fin2d() {     // en (x, z)
    difference() {
        union() {
            translate([frame_x0, z_a - 8.5]) square([x_a - frame_x0, 15]);
            translate([x_a, z_a]) circle(r = 6.5);
            translate([x_a, z_a - 8.5]) square([pin_u + 2.5, 8.5 - tr_h / 2]);   // repisa del tope
        }
        translate([x_a, z_a]) circle(r = pocket_r);
        translate([x_a, z_a]) rotate(slot_ang) translate([0, -slot_w / 2]) square([30, slot_w]);
    }
}
module part_B() {
    translate([frame_x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(frame_t) frame2d();
    translate([frame_x0, -fin_y1, z_a - 4 - tie_h / 2]) cube([tie_t, 2 * fin_y1, tie_h]);   // tirante
    for (s = [-1, 1]) xz(s > 0 ? fin_y0 : -fin_y1, s > 0 ? fin_y1 : -fin_y0) fin2d();
}

// =========================== C: CUNA ==================================
// se modela en locales: u = hacia el fregadero desde el eje, v = altura desde su base
module cradle_local() {
    difference() {
        linear_extrude(wall_h) difference() {
            rrect(u0, u1, -cr_y, cr_y, 3);
            rrect(u0 + wall, u1 - wall, -in_y / 2, in_y / 2, 1.4);
        }
        // por detrás del eje las paredes bajan en pendiente: al girar, nada barre
        // más allá del radio del borde delantero y la cuna no toca el marco
        xz(-cr_y - 1, cr_y + 1) polygon([[u0 - 1, back_h + (wall_h - back_h) * (-1) / (-u0)], [0, wall_h],
                                        [0, wall_h + 5], [u0 - 1, wall_h + 5]]);
        // ventanas en rombo (se imprimen sin soporte)
        for (y = [-45 : 10 : 45])
            translate([u1, y, 9]) rotate([45, 0, 0]) cube([8, 5.4, 5.4], center = true);
        for (s = [-1, 1], u = [pin_u + 10, pin_u + 20])
            translate([u, s * cr_y, 9]) rotate([0, 45, 0]) cube([5.4, 8, 5.4], center = true);
    }
    linear_extrude(floor_h) {
        difference() {                                              // marco del suelo
            rrect(u0, u1, -cr_y, cr_y, 3);
            rrect(u0 + 3, u1 - 3, -cr_y + 3, cr_y - 3, 1.4);
        }
        for (f = [0.2, 0.5, 0.8])                                   // nervios
            translate([u0 + wall + in_x * f - 1, -cr_y + 1]) square([2, 2 * cr_y - 2]);
        for (y = [-22, 22]) translate([u0 + 1, y - 0.8]) square([u1 - u0 - 2, 1.6]);
    }
    for (s = [-1, 1]) {
        y0 = s > 0 ? cr_y - 0.5 : -fin_y1 - 0.5;
        y1 = s > 0 ? fin_y1 + 0.5 : -cr_y + 0.5;
        xz(y0, y1) {
            hull() for (u = [-1, 1]) translate([u * (tr_len - tr_h) / 2, tr_h / 2]) circle(d = tr_h, $fn = 32);
            translate([pin_u, tr_h / 2]) circle(d = tr_h, $fn = 32);
        }
    }
}
module part_C() { translate([x_a, 0, z_c0]) cradle_local(); }

// =========================== SALIDA ===================================
module rot_fold(a) {
    translate([x_a, 0, z_a]) rotate([0, -a, 0]) translate([-x_a, 0, -z_a]) children();
}
module sponge_box() {
    translate([x_a + u0 + wall + 2, -sponge[1] / 2, z_c0 + floor_h]) cube(sponge);
}
module env_ghost() {
    color("WhiteSmoke", 0.35) difference() {
        translate([-150, -110, -25]) cube([150 + sink_d, 220, 25]);
        translate([sink_d / 2, 0, -30]) cylinder(d = sink_d, h = 40, $fn = 180);
    }
    color("Silver", 0.4) translate([x_col, 0, 0]) {
        cylinder(d = 57, h = 5.5);
        cylinder(d = col_d, h = 120);
    }
}

if (part == "A") part_A();
else if (part == "K")   // tumbada sobre la cara que toca la columna
    rotate([0, 90, 0]) translate([edge_dist + col_d / 2, 0, -(zp0 + 1.5)]) part_K();
else if (part == "B")   // tumbado sobre la cara trasera
    translate([0, 0, -frame_x0]) rotate([0, -90, 0]) part_B();
else if (part == "C") cradle_local();
else if (part == "A_use") part_A();
else if (part == "K_use") part_K();
else if (part == "B_use") part_B();
else if (part == "C_use") part_C();
else if (part == "sponge") sponge_box();
else {
    env_ghost();
    color("LightGray") part_A();
    color("DimGray") part_K();
    color("Gainsboro") part_B();
    color("White") rot_fold(part == "folded" ? 100 : fold) part_C();
    if (part != "folded") color("Gold", 0.5) sponge_box();
}
