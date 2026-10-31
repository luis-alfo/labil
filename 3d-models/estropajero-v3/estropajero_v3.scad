// =====================================================================
//  Soporte de estropajo para grifo — V3
//  Tres piezas, todas se imprimen SIN soportes:
//    A = pinza (abraza embellecedor + columna) + brazo plano a ras de encimera
//    B = bastidor en "A" calado: espiga arriba, dos pivotes abajo
//    C = bandeja de rejilla con bisagra de bayoneta: entra desde arriba sin
//        forzar nada (apto PLA), se levanta y se queda pasada de la vertical
//
//  Ejes (posición de uso):  z = 0 superficie de la encimera
//                           x = 0 canto de la encimera (x<0 encimera, x>0 fregadero)
//                           eje de la columna del grifo en x = -edge_dist
//  Fregadero redondo: centro en x = sink_d/2
// =====================================================================

/* [Qué generar] */
part = "assembly"; // ["A", "B", "C", "assembly", "folded", "B_use", "C_use"]
print_aids = true; // orejetas de adherencia en el bastidor
fold = 0;          // ángulo de la bandeja en las vistas de montaje (0 = abajo)

/* [Grifo y fregadero — MEDIR] */
col_d     = 46;   // Ø columna del grifo, justo encima del embellecedor
flange_d  = 54;   // Ø embellecedor cromado de la base
flange_h  = 8;    // altura del embellecedor
edge_dist = 68;   // eje de la columna -> canto de la encimera (= col_d/2 + hueco)
sink_d    = 400;  // Ø del hueco del fregadero en la encimera

/* [Pinza] */
collar_h      = 18;   // altura total (no debe tocar el cuerpo horizontal del grifo)
collar_wall   = 3;
flange_clr    = 0.4;
col_clr       = 0.1;
opening_angle = 110;  // apertura de la C, mirando hacia la pared

/* [Brazo] */
arm_w = 24;
arm_t = 5;

/* [Bastidor] */
drop      = 72;   // de la encimera a la cara superior de la rejilla
gap_top   = 6;    // separación bastidor–canto arriba
pad_h     = 10;   // tope que apoya en el canto (≤ grosor visible de encimera)
pad_clr   = 0.5;
hub_w     = 24;
hub_d     = 8;    // fondo (x) del cuerpo superior y de los brazos
strut_w   = 4;    // grosor de cada brazo de la "A" (flexa para encajar la bandeja)
x_axis    = 24;   // distancia del canto al eje de la bisagra
eye_r     = 8.5;
eye_t     = 4.5;  // grosor del ojo del pivote (y)

/* [Bandeja] */
tray_W    = 100;  // ancho exterior, a lo largo del canto
tray_D    = 62;   // fondo desde el eje hacia el centro del fregadero
floor_t   = 3;
rim_t     = 2.4;
rim_h     = 10;   // altura del marco desde la base (7 mm por encima de la rejilla)
bar_w     = 2.2;
bar_pitch = 10;
axis_h    = 6;    // altura del eje sobre la base de la bandeja
pin_r     = 2.5;
side_clr  = 0.5;  // holgura bandeja–ojos
pin_clr   = 0.3;
pin_len   = 3;    // cuánto entra el pivote en el ojo
lug_len   = 2;    // pestaña de la bayoneta: cuánto entra en el ojo
lug_h     = 4;
lug_r0    = 2;
lug_r1    = 6.2;
lug_clr   = 0.3;
fold_max  = 95;   // tope al levantar (pasada la vertical se queda sola)

/* [Unión A–B] */
tenon_w   = 14;
leg_t     = 5;    // fondo de la espiga
joint_clr = 0.25;
cs        = 1.5;

$fn = 64;
eps = 0.01;

// ---------------------------------------------------------------------
x_col    = -edge_dist;
r_flange = flange_d / 2 + flange_clr;
r_col    = col_d / 2 + col_clr;
r_out    = r_flange + collar_wall;
x_nose   = gap_top + leg_t + joint_clr + cs + 3.5;
zb       = -drop - floor_t;              // base de la bandeja
z_ax     = zb + axis_h;                  // eje de la bisagra
y_eye0   = tray_W / 2 + side_clr;        // cara interior de los ojos
base_z   = z_ax - eye_r;                // base del bastidor (cama)
z_eye_top = zb + rim_h + 3;             // los brazos llegan por encima del marco
// dentro del ancho de la bandeja los brazos van por detrás de ella cuando está levantada
x_strut  = x_axis - (rim_h - axis_h) - 1.5 - hub_d;

module rrect(x0, x1, y0, y1, r) {
    hull() for (x = [x0 + r, x1 - r], y = [y0 + r, y1 - r])
        translate([x, y]) circle(r = r);
}
module rrect4(x0, x1, y0, y1, rb, rf) {   // radio distinto atrás / delante
    hull() {
        for (y = [y0 + rb, y1 - rb]) translate([x0 + rb, y]) circle(r = rb);
        for (y = [y0 + rf, y1 - rf]) translate([x1 - rf, y]) circle(r = rf);
    }
}
// =========================== PIEZA A =================================
module part_A() {
    difference() {
        union() {
            translate([x_col, 0, 0]) cylinder(r = r_out, h = collar_h, $fn = 96);
            linear_extrude(arm_t) hull() {
                translate([x_col, -arm_w / 2]) square([eps, arm_w]);
                translate([x_nose - arm_w / 2, 0]) circle(d = arm_w);
            }
        }
        translate([x_col, 0, 0]) {
            translate([0, 0, -1]) cylinder(r = r_flange, h = flange_h + 1, $fn = 96);
            translate([0, 0, flange_h - eps])
                cylinder(r1 = r_flange, r2 = r_col, h = r_flange - r_col, $fn = 96);
            cylinder(r = r_col, h = 3 * collar_h, center = true, $fn = 96);
            translate([0, 0, -1]) linear_extrude(collar_h + 2)
                polygon([[0, 0],
                         [-2 * r_out,  2 * r_out * tan(opening_angle / 2)],
                         [-2 * r_out, -2 * r_out * tan(opening_angle / 2)]]);
        }
        sx0 = gap_top - joint_clr; sx1 = gap_top + leg_t + joint_clr;
        sy  = tenon_w / 2 + joint_clr;
        translate([sx0, -sy, -1]) cube([sx1 - sx0, 2 * sy, arm_t + 2]);
        hull() {
            translate([sx0, -sy, arm_t - cs]) cube([sx1 - sx0, 2 * sy, eps]);
            translate([sx0 - cs, -sy - cs, arm_t]) cube([sx1 - sx0 + 2 * cs, 2 * sy + 2 * cs, 1]);
        }
    }
    z_up = flange_h + r_flange - r_col;
    for (s = [-1, 1], seg = [[r_flange, 0, z_up], [r_col, z_up, collar_h - z_up]]) {
        a = 180 + s * opening_angle / 2;
        rm = (seg[0] + r_out) / 2;
        translate([x_col + rm * cos(a), rm * sin(a), seg[1]])
            cylinder(d = r_out - seg[0], h = seg[2], $fn = 32);
    }
}

// =========================== PIEZA B =================================
// pestaña de la bayoneta, detrás del eje (o = holgura añadida)
module lug(s, o = 0) {
    yin = tray_W / 2 - 2; yout = y_eye0 + lug_len;
    y0 = s > 0 ? yin - o : -yout - o;
    hull() {
        translate([x_axis - lug_r1 - o, y0, z_ax - lug_h / 2 - o])
            cube([lug_r1 - lug_r0 + 2 * o, yout - yin + 2 * o, lug_h + 2 * o]);
        // chaflán inferior a 45°: la pestaña se imprime sin voladizo
        translate([x_axis - 3.2 - o, y0, z_ax - 5.4 - o])
            cube([3.2 - lug_r0 + 2 * o, yout - yin + 2 * o, eps]);
    }
}
module rot_fold(a) {
    translate([x_axis, 0, z_ax]) rotate([0, -a, 0]) translate([-x_axis, 0, -z_ax]) children();
}

module eye_block(s) {
    y0 = s > 0 ? y_eye0 : -y_eye0 - eye_t;
    difference() {
        hull() {
            translate([x_axis, y0 + eye_t / 2, z_ax]) rotate([90, 0, 0])
                cylinder(r = eye_r, h = eye_t, center = true);
            translate([x_axis - eye_r, y0, base_z]) cube([2 * eye_r, eye_t, eps]);
            translate([x_strut, y0, z_eye_top - eps]) cube([hub_d, eye_t, eps]);
        }
        // ranura abierta por arriba: el pivote entra desde arriba
        translate([x_axis, y0 + eye_t / 2, z_ax]) rotate([90, 0, 0])
            linear_extrude(eye_t + 2, center = true)
                hull() { circle(r = pin_r + pin_clr); translate([0, 30]) circle(r = pin_r + pin_clr); }
        // recorrido de la pestaña: sus extremos son el tope de abajo (bandeja
        // horizontal) y el de arriba (fold_max). Solo sale con la bandeja vertical.
        for (a = [3 : 2.5 : fold_max - 2.5])
            hull() { rot_fold(a) lug(s, lug_clr); rot_fold(a + 2.5) lug(s, lug_clr); }
        // canal de entrada de la pestaña (con la bandeja vertical)
        hull() { rot_fold(90) lug(s, lug_clr); translate([0, 0, 30]) rot_fold(90) lug(s, lug_clr); }
    }
}

module part_B() {
    // espiga + cabeza avellanada (queda enrasada con el brazo)
    z_h0 = arm_t - cs - joint_clr;
    z_h1 = arm_t - 0.1;
    grow = z_h1 - z_h0;
    translate([gap_top, -tenon_w / 2, -1]) cube([leg_t, tenon_w, z_h0 + 1]);
    hull() {
        translate([gap_top, -tenon_w / 2, z_h0]) cube([leg_t, tenon_w, eps]);
        translate([gap_top - grow, -tenon_w / 2 - grow, z_h1 - eps])
            cube([leg_t + 2 * grow, tenon_w + 2 * grow, eps]);
    }
    // cuerpo superior, con la base en V a 45°
    hull() {
        translate([gap_top, -hub_w / 2, -8]) cube([hub_d, hub_w, 7.4]);
        translate([gap_top, -1, -8 - (hub_w / 2 - 1)]) cube([hub_d, 2, eps]);
    }
    // tope contra el canto, con chaflán inferior a 45°
    pad_x1 = gap_top + 3;
    translate([0, hub_w / 2, 0]) rotate([90, 0, 0]) linear_extrude(hub_w)
        polygon([[pad_clr, -0.6], [pad_x1, -0.6],
                 [pad_x1, -pad_h - (pad_x1 - pad_clr)], [pad_clr, -pad_h]]);
    // brazos de la "A"
    for (s = [-1, 1]) {
        hull() {
            translate([gap_top, s > 0 ? hub_w / 2 - strut_w : -hub_w / 2, -9])
                cube([hub_d, strut_w, 8]);
            translate([x_strut, s > 0 ? y_eye0 : -y_eye0 - eye_t, z_eye_top - eps])
                cube([hub_d, eye_t, eps]);
        }
        eye_block(s);
    }
}

// =========================== PIEZA C =================================
module part_C() {
    x0 = x_axis - 3;
    x1 = x_axis + tray_D;
    difference() {
        union() {
            // marco
            translate([0, 0, zb]) linear_extrude(rim_h) difference() {
                rrect4(x0, x1, -tray_W / 2, tray_W / 2, 2, 10);
                rrect4(x0 + rim_t, x1 - rim_t, -tray_W / 2 + rim_t, tray_W / 2 - rim_t, 1, 10 - rim_t);
            }
            // travesaño trasero macizo bajo el eje (aloja los pivotes)
            translate([x0, -tray_W / 2, zb]) cube([6, tray_W, axis_h]);
            // rejilla en diagonal
            translate([0, 0, zb]) linear_extrude(floor_t) intersection() {
                rrect4(x0 + 1, x1 - 1, -tray_W / 2 + 1, tray_W / 2 - 1, 1, 9);
                union() for (a = [45, -45]) rotate(a)
                    for (i = [-15 : 15]) translate([i * bar_pitch - bar_w / 2, -150]) square([bar_w, 300]);
            }
            // eje: varilla trasera que sale por los dos lados como pivote
            translate([x_axis, 0, z_ax]) rotate([90, 0, 0])
                cylinder(r = pin_r, h = 2 * (y_eye0 + pin_len), center = true, $fn = 40);
            // pestañas de la bayoneta
            for (s = [-1, 1]) lug(s);
        }
        // chaflán a 45° en la esquina trasera inferior: queda dentro del radio del eje,
        // así al levantar la bandeja no baja de su base
        translate([x_axis, 0, z_ax]) rotate([90, 0, 0]) linear_extrude(2 * tray_W, center = true)
            polygon([[-4, -axis_h - 1], [0, -axis_h - 1], [0, -axis_h], [-3, -axis_h + 3], [-4, -axis_h + 3]]);
    }
}

// =========================== SALIDA ==================================
module env_ghost() {
    color("WhiteSmoke", 0.35) difference() {
        translate([-160, -130, -25]) cube([160 + sink_d, 260, 25]);
        translate([sink_d / 2, 0, -30]) cylinder(d = sink_d, h = 40, $fn = 180);
    }
    color("DimGray", 0.25) difference() {
        translate([sink_d / 2, 0, -180]) cylinder(d = sink_d + 4, h = 155, $fn = 180);
        translate([sink_d / 2, 0, -181]) cylinder(d = sink_d, h = 160, $fn = 180);
    }
    color("Silver", 0.4) translate([x_col, 0, 0]) {
        cylinder(d = flange_d, h = flange_h);
        cylinder(d = col_d, h = 140);
    }
}
module C_at(angle) {   // angle > 0: levantada
    translate([x_axis, 0, z_ax]) rotate([0, -angle, 0]) translate([-x_axis, 0, -z_ax]) part_C();
}

if (part == "A") part_A();
else if (part == "B") translate([0, 0, -base_z]) {
    part_B();
    // orejetas de adherencia (0,4 mm): el bastidor es alto y apoya en dos pies
    // pequeños; en una impresora de cama móvil ayudan a que no se despegue.
    // Se arrancan con la mano después de imprimir.
    if (print_aids) for (s = [-1, 1])
        translate([x_axis, s * (y_eye0 + eye_t / 2), base_z]) cylinder(d = 22, h = 0.4);
}
else if (part == "C") translate([0, 0, -zb]) part_C();
else if (part == "B_use") part_B();
else if (part == "C_use") part_C();
else {
    env_ghost();
    color("LightGray") part_A();
    color("Gainsboro") part_B();
    color("White") C_at(part == "folded" ? fold_max : fold);
}
