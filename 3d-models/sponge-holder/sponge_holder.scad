// Sponge holder for kitchen faucet — 3D version
// =================================================
// Clip in the horizontal plane (axis = Z, parallel to the floor) pinches
// a vertical element of the faucet. A horizontal arm leaves the clip and
// then turns 90° down into a vertical drop, which feeds a U-shaped cradle
// that holds the sponge vertically.
//
// Coordinates: Z is up. All dimensions are in millimetres.

// ====== Parameters ======
wall_t          = 4;     // plastic wall thickness everywhere

// Clip
clip_inner_d    = 18;    // < 20 mm so it pinches
clip_height     = 18;    // along Z (axis of the ring)
clip_wrap_deg   = 280;   // > 180 → snap-on
clip_overlap    = 0.6;

// Horizontal arm
arm_len         = 30;
arm_width_y     = 18;

// Vertical drop (the 90° turn)
drop_len        = 22;

// Cradle (U opening upward)
cradle_width_y  = 30;
cradle_back_h   = 80;
cradle_bot_len  = 32;
cradle_front_h  = 37;

$fn = 96;

// ====== Build ======
union() {
    clip();
    arm();
    drop();
    cradle();
}

// ---- Clip: partial cylinder, axis Z, mouth opens on +X ----
module clip() {
    r_in  = clip_inner_d / 2;
    r_out = r_in + wall_t;
    half_open = (360 - clip_wrap_deg) / 2;

    translate([0, 0, -clip_height / 2])
    linear_extrude(height = clip_height)
        difference() {
            // ring
            difference() {
                circle(r = r_out);
                circle(r = r_in);
            }
            // mouth: wedge that subtracts the +X opening
            polygon(points = [
                [0, 0],
                [(r_out + 2) * cos(-half_open),
                 (r_out + 2) * sin(-half_open)],
                [(r_out + 2) * cos( half_open),
                 (r_out + 2) * sin( half_open)],
            ]);
        }
}

// ---- Horizontal arm: -X side of clip ----
module arm() {
    r_out = clip_inner_d / 2 + wall_t;
    x_start = -r_out + clip_overlap;
    x_end   = -r_out - arm_len;
    z_top   = clip_height / 2;
    z_bot   = z_top - wall_t;
    translate([(x_start + x_end) / 2, 0, (z_top + z_bot) / 2])
        cube([abs(x_end - x_start), arm_width_y, wall_t], center = true);
}

// ---- Vertical drop ----
module drop() {
    r_out = clip_inner_d / 2 + wall_t;
    x_arm_end = -r_out - arm_len;
    z_arm_bot = clip_height / 2 - wall_t;
    translate([
        x_arm_end - wall_t / 2,
        0,
        z_arm_bot - drop_len / 2 + clip_overlap / 2,
    ])
        cube([wall_t, cradle_width_y, drop_len + clip_overlap], center = true);
}

// ---- Cradle ----
module cradle() {
    r_out = clip_inner_d / 2 + wall_t;
    x_back = -r_out - arm_len - wall_t;
    z_drop_bot = clip_height / 2 - wall_t - drop_len;

    // back wall
    translate([
        x_back + wall_t / 2,
        0,
        z_drop_bot - cradle_back_h / 2 + clip_overlap / 2,
    ])
        cube([wall_t, cradle_width_y, cradle_back_h + clip_overlap], center = true);

    // bottom
    z_bottom_top = z_drop_bot - cradle_back_h;
    translate([
        x_back - cradle_bot_len / 2 + clip_overlap / 2,
        0,
        z_bottom_top - wall_t / 2,
    ])
        cube([cradle_bot_len + clip_overlap, cradle_width_y, wall_t], center = true);

    // front lip
    x_front = x_back - cradle_bot_len;
    translate([
        x_front + wall_t / 2,
        0,
        z_bottom_top - wall_t + cradle_front_h / 2 + clip_overlap / 2,
    ])
        cube([wall_t, cradle_width_y, cradle_front_h + clip_overlap], center = true);
}
