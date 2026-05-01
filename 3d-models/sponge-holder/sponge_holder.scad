// Kitchen sponge holder that hooks over a faucet base.
// Prints flat on the side wall (Y plane) so the loop closes correctly
// and the layer lines run perpendicular to the load.
//
// All dimensions in millimetres.

// ====== Parameters ======
faucet_d        = 32;   // diameter of the faucet shaft the hook clips on
strap_t         = 4;    // wall / strap thickness
strap_w         = 28;   // strap width (depth, into the page)
hook_wrap_deg   = 220;  // how far around the faucet the hook wraps (>180 = snap-on)

descent_h       = 30;   // vertical drop from end of hook to the cradle arm
arm_l           = 50;   // horizontal arm from descent to cradle back
cradle_back_h   = 80;   // cradle back wall (vertical, where sponge sits)
cradle_bottom_l = 55;   // cradle bottom (horizontal)
cradle_front_h  = 37;   // cradle front lip (vertical, holds sponge in)

corner_r        = 4;    // small fillet radius at sharp bends
$fn             = 96;

// ====== Build ======
linear_extrude(height = strap_w, center = true, convexity = 6)
    holder_profile();

module holder_profile() {
    R_inner = faucet_d / 2;
    R_outer = R_inner + strap_t;

    // Centerline radius for the hook
    R_c     = R_inner + strap_t / 2;

    // Hook arc endpoints (so wrap > 180 produces a snap-on clip)
    extra   = (hook_wrap_deg - 180) / 2;          // beyond the equator, both sides
    a_back  = 180 + extra;                        // back-bottom start
    a_front = -extra;                             // front-bottom end
    p_hook_end = [R_c * cos(a_front), R_c * sin(a_front)];

    // Key centerline points after hook
    p1 = p_hook_end;
    p2 = [p1[0],            p1[1] - descent_h];
    p3 = [p2[0] + arm_l,    p2[1]];
    p4 = [p3[0],            p3[1] - cradle_back_h];
    p5 = [p4[0] + cradle_bottom_l, p4[1]];
    p6 = [p5[0],            p5[1] + cradle_front_h];

    // Slightly rounded outer outline by offset() trick:
    // build the medial polyline as a thin ribbon, then inflate by strap_t/2
    offset(r = strap_t / 2 + corner_r) offset(r = -corner_r)
    union() {
        // --- Hook ring (open ring since wrap < 360) ---
        hook_ring(R_inner = R_inner, R_outer = R_outer,
                  a_start = a_back, a_end = a_front);

        // --- Straps as thick segments ---
        thick_segment(p1, p2);
        thick_segment(p2, p3);
        thick_segment(p3, p4);
        thick_segment(p4, p5);
        thick_segment(p5, p6);
    }
}

// Open ring sweeping CCW from a_start down to a_end (a_start > a_end)
module hook_ring(R_inner, R_outer, a_start, a_end) {
    // build by intersection of an annulus with a "wedge" polygon
    intersection() {
        difference() {
            circle(r = R_outer);
            circle(r = R_inner);
        }
        // wedge polygon covering angular sweep
        polygon(points = concat(
            [[0, 0]],
            [for (a = [a_start : -2 : a_end]) [(R_outer + 2) * cos(a),
                                               (R_outer + 2) * sin(a)]],
            [[(R_outer + 2) * cos(a_end), (R_outer + 2) * sin(a_end)]]
        ));
    }
}

// Thick polygon between two 2D points, width = strap_t
module thick_segment(a, b) {
    hull() {
        translate(a) circle(d = strap_t);
        translate(b) circle(d = strap_t);
    }
}
