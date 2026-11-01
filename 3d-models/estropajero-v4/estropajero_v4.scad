// =====================================================================
//  Soporte de estropajo para grifo — V4
//
//  Cuatro piezas en PLA, todas sin soportes y sin forzar nada al montar:
//    A = brazo: abrazadera en U alrededor del grifo + brazo plano a ras de encimera
//    K = llave: cierra la U por detrás de la columna (se mete desde arriba)
//    B = colgador: perfil plano de 10 mm (se imprime tumbado: todo trabaja en el
//        plano de las capas). Cuelga de la punta del brazo y apoya abajo en la
//        pared del fregadero, que es la que aguanta el par de la bandeja.
//    C = bandeja de rejilla con bisagra central: se mete vertical desde arriba,
//        se baja y queda atrapada; levantada se apoya sola pasada la vertical.
//
//  Ejes (posición de uso):  z = 0 superficie de la encimera
//                           x = 0 canto de la encimera (x<0 encimera, x>0 fregadero)
//                           eje de la columna del grifo en x = -edge_dist
// =====================================================================

/* [Qué generar] */
part = "assembly"; // ["A", "K", "B", "C", "assembly", "folded", "A_use", "K_use", "B_use", "C_use"]
fold = 0;          // ángulo de la bandeja en el montaje (0 = abajo)

/* [Grifo y fregadero — MEDIR] */
col_d       = 46;   // Ø columna del grifo, justo encima del embellecedor
flange_d    = 54;   // Ø embellecedor cromado de la base
flange_h    = 8;    // altura del embellecedor
edge_dist   = 68;   // eje de la columna -> canto de la encimera
sink_d      = 400;  // Ø del hueco del fregadero
sink_wall_x = 1;    // pared del fregadero a ~8 cm de profundidad, medida desde
                    // el canto de la encimera (+ hacia dentro del fregadero)

/* [Abrazadera y llave] */
collar_h    = 18;
collar_wall = 3;
flange_clr  = 0.4;
col_clr     = 0.3;  // holgura: aquí no hay clip, la llave cierra
key_d       = 7;    // fondo de la llave (x)
key_tongue  = 2.5;  // cuánto entra la llave en cada brazo de la U
key_clr     = 0.25;

/* [Brazo] */
arm_w    = 22;
arm_t    = 5;
nose_len = 13.5;    // la punta sobresale del canto
cap_t    = 2;       // remate de B embutido en la punta (queda enrasado)
tip_x0   = 3;       // diente de B que entra en la ranura de la punta
tip_w    = 4;
slot_clr = 0.5;     // deja meter el diente con B inclinado
side_clr = 0.3;

/* [Colgador] */
hanger_t  = 10;     // grosor (y): altura de impresión
drop      = 75;     // de la encimera a la cara superior de la rejilla
x_axis    = 24;     // eje de la bisagra, desde el canto
rod_r     = 3.5;
rod_clr   = 0.25;
lip_w     = 4.5;    // pared del gancho alrededor de la varilla
chin_drop = 14;     // el mentón baja esto por debajo del eje
bump_r    = 3;
brace_w   = 6;

/* [Bandeja] */
tray_W     = 100;
tray_D     = 60;    // desde el eje hacia el centro del fregadero
floor_t    = 3;
rim_t      = 2.4;
rim_h      = 8; 
bar_w      = 2.2;
bar_pitch  = 12;
axis_h     = 12;    // eje sobre la base de la bandeja (por encima del marco)
knuckle_t  = 6;
knuckle_clr = 0.4;

$fn = 72;
eps = 0.01;

// ---------------------------------------------------------------------
x_col    = -edge_dist;
r_flange = flange_d / 2 + flange_clr;
r_col    = col_d / 2 + col_clr;
r_out    = r_flange + collar_wall;
z_step   = flange_h + (r_flange - r_col);        // fin del chaflán embellecedor→columna
x_key1   = x_col - r_col - key_clr;              // cara interior de la llave
x_key0   = x_key1 - key_d;
x_back   = x_key0 - 3;                           // final de los brazos de la U
zb       = -drop - floor_t;                      // base de la bandeja
z_ax     = zb + axis_h;                          // eje de la bisagra
cup_r    = rod_r + rod_clr;
j_r      = cup_r + lip_w;
tip_x1   = tip_x0 + tip_w;
leg_x0   = nose_len + side_clr;
leg_x1   = x_axis - cup_r - 0.15;                // detrás de la ranura de la varilla
band     = hanger_t / 2 + knuckle_clr;           // hueco de la bandeja para el colgador
bump_x   = sink_wall_x + 0.5;                    // cara trasera del tope
chin_x1  = x_axis - 2.3;                         // cara del mentón contra el talón
z_chin0  = z_ax - chin_drop;

module rrect(x0, x1, y0, y1, r) {
    hull() for (x = [x0 + r, x1 - r], y = [y0 + r, y1 - r]) translate([x, y]) circle(r = r);
}
module rrect4(x0, x1, y0, y1, rb, rf) {
    hull() {
        for (y = [y0 + rb, y1 - rb]) translate([x0 + rb, y]) circle(r = rb);
        for (y = [y0 + rf, y1 - rf]) translate([x1 - rf, y]) circle(r = rf);
    }
}
module bar2d(p, q, w) { hull() { translate(p) circle(d = w); translate(q) circle(d = w); } }
// canal en U (planta): media circunferencia delante + recto hacia atrás
module u_channel(r, back) { circle(r = r, $fn = 96); translate([-back, -r]) square([back, 2 * r]); }

// =========================== A: BRAZO =================================
module part_A() {
    difference() {
        union() {
            translate([x_col, 0, 0]) linear_extrude(collar_h) u_channel(r_out, x_col - x_back);
            linear_extrude(arm_t) hull() {
                translate([x_col, -arm_w / 2]) square([eps, arm_w]);
                for (s = [-1, 1]) translate([nose_len - 3, s * (arm_w / 2 - 3)]) circle(r = 3);
            }
        }
        // hueco escalonado abierto por detrás: embellecedor abajo, columna arriba
        translate([x_col, 0, 0]) {
            back = x_col - x_back + 5;
            translate([0, 0, -1]) linear_extrude(flange_h + 1) u_channel(r_flange, back);
            hull() {
                translate([0, 0, flange_h - eps]) linear_extrude(eps) u_channel(r_flange, back);
                translate([0, 0, z_step]) linear_extrude(eps) u_channel(r_col, back);
            }
            linear_extrude(collar_h + 1) u_channel(r_col, back);
        }
        // ranuras de la llave en los brazos de la U (ciegas por abajo)
        for (s = [-1, 1])
            translate([x_key0 - key_clr, s > 0 ? r_col - 1 : -r_col - key_tongue - key_clr, z_step + 0.5])
                cube([key_d + 2 * key_clr, key_tongue + key_clr + 1, collar_h]);
        // punta: rebaje para el remate de B y ranura para su diente
        yb = hanger_t / 2 + side_clr;
        translate([tip_x0 - slot_clr, -yb, arm_t - cap_t]) cube([nose_len + 1, 2 * yb, cap_t + 1]);
        translate([tip_x0 - slot_clr, -yb, -1]) cube([tip_w + 2 * slot_clr, 2 * yb, arm_t + 2]);
    }
}

// =========================== K: LLAVE =================================
module part_K() {
    translate([x_key0, -(r_col + key_tongue), z_step + 0.5 + key_clr])
        cube([key_d, 2 * (r_col + key_tongue), collar_h - z_step - 0.5 - key_clr]);
}

// =========================== B: COLGADOR ==============================
// perfil en el plano xz (u = x, v = z)
module hanger_profile() {
    difference() {
        union() {
            translate([tip_x0, 1]) square([tip_w, arm_t - 1.1]);                    // diente
            translate([tip_x0, arm_t - cap_t]) square([leg_x1 - tip_x0, cap_t - 0.1]); // remate
            translate([leg_x0, z_ax]) square([leg_x1 - leg_x0, arm_t - 0.1 - z_ax]);  // pata
            translate([x_axis, z_ax]) circle(r = j_r);                               // gancho
            hull() {                                                                 // mentón + tope
                translate([bump_x + bump_r, z_chin0 + bump_r]) circle(r = bump_r);
                translate([bump_x + bump_r, z_chin0]) square([chin_x1 - bump_x - bump_r, eps]);
                translate([chin_x1 - eps, z_ax - 7]) square([eps, eps]);
                translate([bump_x + bump_r, z_ax - 7]) square([eps, eps]);
            }
            bar2d([leg_x0 + brace_w / 2, -22], [bump_x + bump_r, z_chin0 + bump_r], brace_w); // tirante
        }
        translate([x_axis, z_ax]) circle(r = cup_r);
        translate([x_axis - cup_r, z_ax]) square([2 * cup_r, 200]);
    }
}
module part_B() { rotate([90, 0, 0]) linear_extrude(hanger_t, center = true) hanger_profile(); }

// =========================== C: BANDEJA ===============================
module part_C() {
    x0 = x_axis - 3;
    x1 = x_axis + tray_D;
    difference() {
        union() {
            translate([0, 0, zb]) linear_extrude(rim_h) difference() {
                rrect4(x0, x1, -tray_W / 2, tray_W / 2, 2, 10);
                rrect4(x0 + rim_t, x1 - rim_t, -tray_W / 2 + rim_t, tray_W / 2 - rim_t, 1, 10 - rim_t);
            }
            translate([x0, -24, zb]) cube([6, 48, rim_h]);                         // refuerzo junto a la bisagra
            translate([0, 0, zb]) linear_extrude(floor_t) {
                intersection() {                                                   // rejilla
                    rrect4(x0 + 1, x1 - 1, -tray_W / 2 + 1, tray_W / 2 - 1, 1, 9);
                    union() for (a = [45, -45]) rotate(a)
                        for (i = [-15 : 15]) translate([i * bar_pitch - bar_w / 2, -150]) square([bar_w, 300]);
                }
                translate([x_axis - 2, -band]) square([tray_D + 1, 2 * band]);      // nervio central
            }
            for (s = [-1, 1])                                                      // orejas de la bisagra
                translate([0, s * (band + knuckle_t / 2), 0]) rotate([90, 0, 0])
                    linear_extrude(knuckle_t, center = true) hull() {
                        translate([x_axis, z_ax]) circle(r = 7);
                        translate([x0, zb]) square([x_axis + 12 - x0, 1]);
                    }
        }
        // hueco para el colgador: detrás del talón y alrededor del gancho
        translate([x0 - 1, -band, zb - 1]) cube([x_axis - 2 - x0 + 1, 2 * band, 40]);
        translate([x_axis, 0, z_ax]) rotate([90, 0, 0]) cylinder(r = j_r + 0.5, h = 2 * band, center = true);
    }
    // talón (tope abajo): bajo el eje, entre las orejas, sin entrar en el radio del gancho
    translate([x_axis - 2, -band - 1, zb]) cube([5, 2 * band + 2, axis_h - j_r - 0.5]);
    // varilla de la bisagra
    translate([x_axis, 0, z_ax]) rotate([90, 0, 0])
        cylinder(r = rod_r, h = 2 * (band + knuckle_t - 1), center = true);
}

// =========================== SALIDA ===================================
module rot_fold(a) {
    translate([x_axis, 0, z_ax]) rotate([0, -a, 0]) translate([-x_axis, 0, -z_ax]) children();
}
module env_ghost() {
    color("WhiteSmoke", 0.35) difference() {
        translate([-160, -130, -25]) cube([160 + sink_d, 260, 25]);
        translate([sink_d / 2, 0, -30]) cylinder(d = sink_d, h = 40, $fn = 180);
    }
    color("Silver", 0.4) translate([x_col, 0, 0]) {
        cylinder(d = flange_d, h = flange_h);
        cylinder(d = col_d, h = 140);
    }
}

if (part == "A") part_A();
else if (part == "K") rotate([0, 0, 0]) translate([-x_key0, 0, -(z_step + 0.5 + key_clr)]) part_K();
else if (part == "B") linear_extrude(hanger_t) hanger_profile();                   // tumbado
else if (part == "C") translate([0, 0, -zb]) part_C();
else if (part == "A_use") part_A();
else if (part == "K_use") part_K();
else if (part == "B_use") part_B();
else if (part == "C_use") part_C();
else {
    env_ghost();
    color("LightGray") part_A();
    color("DimGray") part_K();
    color("Gainsboro") part_B();
    color("White") rot_fold(part == "folded" ? 100 : fold) part_C();
}
