// =====================================================================
//  EL SECADERO — soporte de estropajo para grifo — V5
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
skirt_wall = 2;
shell_t    = 3.2;     // 2,6 mm de pared por debajo del grabado
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
fin_t   = 6.2;      // aletas con la bisagra (y ancho de las patas)
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
pin_u    = 10;      // tetón de tope, por delante del eje
tr_len   = 7.5;     // muñón: 7,5 × 3,6 con dos caras planas
tr_h     = 3.6;
corner   = 7;       // radio de las esquinas de la cuna

/* [Estética] */
label       = "EL SECADERO | V5 | 161126";   // grabado en el anillo
label_size  = 3.0;    // altura de las mayúsculas (JetBrains Mono Bold)
label_depth = 0.6;
zs0    = 6.5;         // el anillo se estrecha en curva entre estas dos alturas
zs1    = 15.5;
top_r  = 1.5;         // canto superior redondeado
tail_r = 3;
neck_r = 7;           // cuello en media caña entre el brazo y el anillo

$fn = 72;
eps = 0.01;

use <fonts/JetBrainsMono-Bold.ttf>

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
z_k = z_a + u1 + 5;
sweep_r = wall_h - tr_h / 2 - 0.2;             // radio que barre la cuna por detrás del eje                            // codo de la percha, por encima de la cuna levantada

// --- perfil del anillo: base ancha, curva en S y banda recta para el grabado ---
R_b = r_skirt + skirt_wall;
R_g = r_grip + shell_t;
W_g = r_grip + ear_t;
function sstep(t) = t <= 0 ? 0 : t >= 1 ? 1 : 3 * t * t - 2 * t * t * t;
function topcut(z) = z <= collar_h - top_r ? 0 : top_r - sqrt(max(0, top_r * top_r - pow(z - collar_h + top_r, 2)));
function botcut(z) = z >= 0.6 ? 0 : 0.6 - z;
function Rz(z) = R_b + (R_g - R_b) * sstep((z - zs0) / (zs1 - zs0)) - topcut(z) - botcut(z);
function Wz(z) = R_b + (W_g - R_b) * sstep((z - zs0) / (zs1 - zs0)) - topcut(z) - botcut(z);
ring_zs = concat([0, 0.6], [for (z = [1.5 : 1 : collar_h - top_r - 0.01]) z],
                 [for (i = [0 : 5]) collar_h - top_r + top_r * sin(i * 18)]);
module ring_plan(z) {   // planta en herradura, con las colas redondeadas
    hull() {
        circle(r = Rz(z), $fn = 120);
        for (s = [-1, 1]) translate([-back + tail_r, s * (Wz(z) - tail_r)]) circle(r = tail_r, $fn = 24);
    }
}
// cuello: el brazo sube hasta el anillo como el mango de una cuchara. Sustituye
// a la cartela: reparte la flexión de la unión en 7 mm de altura.
function neck_f(z) = neck_r - sqrt(max(0, neck_r * neck_r - pow(neck_r - (z - arm_t), 2)));
function neck_w(z) = 10 - 7 * (z - arm_t) / neck_r;
neck_zs = [for (i = [0 : 20]) arm_t - 0.3 + i * (neck_r + 0.3) / 20];
module neck_plan(z) {
    hull() {
        circle(r = Rz(z) - 0.5, $fn = 120);
        translate([Rz(z) + neck_f(max(z, arm_t)) - neck_w(max(z, arm_t)), 0]) circle(r = neck_w(max(z, arm_t)), $fn = 48);
    }
}
// redondea en 2D: primero los rincones (radio ri), después las esquinas (radio ro)
module soften(ri, ro) { offset(r = ro) offset(delta = -ro) offset(r = -ri) offset(delta = ri) children(); }
// extruye con el canto superior matado en dos escalones de 0,4 mm
module soft_extrude(h) {
    linear_extrude(h - 0.8) children();
    translate([0, 0, h - 0.8]) linear_extrude(0.4) offset(delta = -0.4) children();
    translate([0, 0, h - 0.4]) linear_extrude(0.4) offset(delta = -0.8) children();
}

module u2d(r, b) { circle(r = r, $fn = 120); translate([-b, -r]) square([b, 2 * r]); }
module rrect(x0, x1, y0, y1, r) {
    hull() for (x = [x0 + r, x1 - r], y = [y0 + r, y1 - r]) translate([x, y]) circle(r = r, $fn = 24);
}
module bar2d(p, q, w) { hull() { translate(p) circle(d = w); translate(q) circle(d = w); } }
// extruye un perfil dibujado en (x, z) entre y0 e y1
module xz(y0, y1) { translate([0, y1, 0]) rotate([90, 0, 0]) linear_extrude(y1 - y0) children(); }

// =========================== A: BRAZO =================================
module arm2d() {   // planta: el brazo nace del anillo con un cuello curvo y se estrecha
    xs = x_col + R_b;
    soften(8, 0.01) {
        translate([x_col, 0]) ring_plan(1);
        polygon([[x_col, -13.5], [xs - 2, -13.5], [nose_x0 - 8, -arm_w / 2], [gx0, -arm_w / 2],
                 [gx0, arm_w / 2], [nose_x0 - 8, arm_w / 2], [xs - 2, 13.5], [x_col, 13.5]]);
    }
}
module label_cut() {   // texto grabado alrededor de la banda recta del anillo
    n = len(label);
    adv = 0.814 * label_size;
    for (i = [0 : n - 1]) {
        a = (i - (n - 1) / 2) * adv / R_g * 180 / PI;
        translate([x_col, 0, 0]) rotate([0, 0, a])
            translate([R_g - label_depth, 0, (zs1 + collar_h - top_r - label_size) / 2])
                rotate([90, 0, 90]) linear_extrude(label_depth + 2)
                    if (label[i] == "|") translate([-0.3, 0]) square([0.6, label_size]);
                    else text(label[i], size = label_size, font = "JetBrains Mono:style=Bold", halign = "center");
    }
}
module part_A() {
    xs = x_col + R_b;
    difference() {
        union() {
            // anillo
            translate([x_col, 0, 0]) for (i = [0 : len(ring_zs) - 2]) hull() {
                translate([0, 0, ring_zs[i]]) linear_extrude(eps) ring_plan(ring_zs[i]);
                translate([0, 0, ring_zs[i + 1]]) linear_extrude(eps) ring_plan(ring_zs[i + 1]);
            }
            // brazo de 3 mm con el canto matado; la punta engrosa a 5 mm
            soft_extrude(arm_t) arm2d();
            hull() {   // rampa larga y suave hasta el grosor de la punta
                translate([nose_x0 - 16, -arm_w / 2 + 0.8, 0]) cube([eps, arm_w - 1.6, arm_t]);
                translate([nose_x0 + 2, -arm_w / 2, 0]) cube([gx1 - nose_x0 - 2, arm_w, nose_t]);
            }
            linear_extrude(nose_t) rrect(gx1 - 3, nose_x1, -web_w / 2 + 0.4, web_w / 2 - 0.4, 2.5);   // testa
            translate([x_col, 0, 0]) for (i = [0 : len(neck_zs) - 2]) hull() {                        // cuello
                translate([0, 0, neck_zs[i]]) linear_extrude(eps) neck_plan(neck_zs[i]);
                translate([0, 0, neck_zs[i + 1]]) linear_extrude(eps) neck_plan(neck_zs[i + 1]);
            }
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
        label_cut();
        // punta: el marco entra de frente por encima de la testa y cae en la ranura
        translate([gx0, -web_w / 2, web_t]) cube([gx1 - gx0, web_w, nose_t]);            // ranura del puente
        for (s = [-1, 1])
            translate([gx0, s > 0 ? web_w / 2 : -arm_w, -1]) cube([gx1 - gx0 + eps, arm_w - web_w / 2, nose_t + 2]);
    }
}

// =========================== K: CUÑA ==================================
// Cuña + visera curva: desde arriba cierra el contorno del anillo por detrás
// y sirve de uñero para sacarla.
vis_t   = 2;
vis_sag = 3;
module part_K() {
    R = col_d / 2;
    zb = zp0 + 1.5;
    zt = zb + key_h;
    hw = r_grip - 0.4;                                   // semiancho de la visera, entre las colas
    rho = (hw * hw + vis_sag * vis_sag) / (2 * vis_sag);
    translate([x_col, 0, 0]) {
        intersection() {
            xz(-40, 40) polygon([[-R, zb], [-R - key_t0, zb], [-R - key_tt, zt], [-R, zt]]);
            translate([-40, 0, 0]) rotate([90, 0, 90]) linear_extrude(80)
                rrect(-r_grip - key_tongue, r_grip + key_tongue, zb, zt, 1.5);
        }
        translate([0, 0, zt - vis_t]) linear_extrude(vis_t) intersection() {
            translate([-back - vis_sag - 1, -hw]) square([back + vis_sag + 1 - R - 2.5, 2 * hw]);
            translate([-back - vis_sag + rho, 0]) circle(r = rho, $fn = 240);
        }
    }
}

// =========================== B: MARCO =================================
module frame2d() {   // en (y, z): percha con todos los rincones y esquinas en curva
    difference() {
        soften(4, 2) {
            translate([-sh_out, -4]) square([2 * sh_out, nose_t + 4]);
            // patas verticales por fuera de la cuna (al levantarla pasa entre ellas)
            // y brazos inclinados hasta la punta del brazo
            for (s = [-1, 1]) {
                bar2d([s * (sh_out - leg_w / 2), -2.5], [s * (fin_y0 + fin_t / 2), z_k], leg_w);
                translate([s > 0 ? fin_y0 : -fin_y1, z_a - 8.5]) square([fin_t, z_k - z_a + 8.5]);
            }
        }
        translate([-web_w / 2 - 0.3, -8]) square([web_w + 0.6, web_t + 0.1 + 8]);   // hueco del alma
    }
}
module fin2d() {     // en (x, z)
    difference() {
        union() {
            soften(1.2, 2) {
                translate([frame_x0, z_a - 8.5]) square([x_a - frame_x0, 15]);
                translate([x_a, z_a]) circle(r = 6.5);
                translate([x_a, z_a - 8.5]) square([pin_u + 4, 8.5 - tr_h / 2]);   // repisa del tope
            }
            translate([frame_x0, z_a - 8.5]) square([3, 15]);   // la cara que toca la pared queda plana
        }
        translate([x_a, z_a]) circle(r = pocket_r);
        translate([x_a, z_a]) rotate(slot_ang) translate([0, -slot_w / 2]) square([30, slot_w]);
    }
}
module part_B() {
    translate([frame_x0, 0, 0]) rotate([90, 0, 90]) soft_extrude(frame_t) frame2d();
    translate([frame_x0, -fin_y1, z_a - 4 - tie_h / 2]) cube([tie_t, 2 * fin_y1, tie_h]);   // tirante
    for (s = [-1, 1]) xz(s > 0 ? fin_y0 : -fin_y1, s > 0 ? fin_y1 : -fin_y0) fin2d();
}

// =========================== C: CUNA ==================================
// se modela en locales: u = hacia el fregadero desde el eje, v = altura desde su base
module cradle_local() {
    difference() {
        linear_extrude(wall_h) difference() {
            rrect(u0, u1, -cr_y, cr_y, corner);
            rrect(u0 + wall, u1 - wall, -in_y / 2, in_y / 2, corner - wall);
        }
        // por detrás del eje el borde baja siguiendo un arco centrado en la bisagra:
        // al girar, nada barre más allá de ese radio y la cuna no toca el marco
        xz(-cr_y - 1, cr_y + 1) polygon(concat(
            [for (a = [90 : 5 : 180]) [sweep_r * cos(a), tr_h / 2 + sweep_r * sin(a)]],
            [[u0 - 2, tr_h / 2], [u0 - 2, wall_h + 5], [0, wall_h + 5]]));
        // ventanas en forma de cápsula
        for (y = [-40 : 10 : 40]) hull() for (v = [6.5, 10.5])
            translate([u1, y, v]) rotate([0, 90, 0]) cylinder(r = 2, h = 8, center = true, $fn = 24);
        for (s = [-1, 1], u = [pin_u + 9, pin_u + 18]) hull() for (v = [6.5, 10.5])
            translate([u, s * cr_y, v]) rotate([90, 0, 0]) cylinder(r = 2, h = 8, center = true, $fn = 24);
    }
    linear_extrude(floor_h) {
        difference() {                                              // marco del suelo
            rrect(u0, u1, -cr_y, cr_y, corner);
            rrect(u0 + 3, u1 - 3, -cr_y + 3, cr_y - 3, corner - 3);
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
