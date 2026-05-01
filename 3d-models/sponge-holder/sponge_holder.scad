// Sponge holder for kitchen faucet — 3D version with sponge pinch clip.
// Faucet clip (Ø 45 mm, axis Z) + arm "por detrás" + 90° drop + sponge
// C-clip (axis Y, mouth -Z) that pinches the sponge by its top edge.
// Z is up. All dimensions in millimetres.

// ====== Parameters ======
wall_t                = 4;
clip_inner_d          = 45.4;   // 45 mm shaft + 0.4 mm tolerance for PLA
clip_height           = 22;
clip_wrap_deg         = 240;    // PLA-friendly snap (less wrap = more flex)
clip_overlap          = 0.6;

arm_len               = 30;
arm_width_y           = 22;

drop_len              = 22;
drop_width_y          = 30;

sponge_gap            = 14;     // < 20 mm: pinches the sponge thickness
sponge_clip_len_y     = 50;
sponge_clip_wrap_deg  = 220;

$fn = 96;

union() {
    faucet_clip();
    arm();
    drop();
    sponge_clip();
}

module faucet_clip() {
    r_in  = clip_inner_d / 2;
    r_out = r_in + wall_t;
    half_open = (360 - clip_wrap_deg) / 2;
    translate([0, 0, -clip_height / 2])
    linear_extrude(clip_height)
        difference() {
            difference() {
                circle(r = r_out);
                circle(r = r_in);
            }
            polygon([
                [0, 0],
                [(r_out + 2) * cos(-half_open), (r_out + 2) * sin(-half_open)],
                [(r_out + 2) * cos( half_open), (r_out + 2) * sin( half_open)],
            ]);
        }
}

module arm() {
    r_out = clip_inner_d / 2 + wall_t;
    x_start = -r_out + clip_overlap;
    x_end   = -r_out - arm_len;
    z_top   = clip_height / 2;
    z_bot   = z_top - wall_t;
    translate([(x_start + x_end) / 2, 0, (z_top + z_bot) / 2])
        cube([abs(x_end - x_start), arm_width_y, wall_t], center = true);
}

module drop() {
    r_out = clip_inner_d / 2 + wall_t;
    x_arm_end = -r_out - arm_len;
    z_arm_bot = clip_height / 2 - wall_t;
    translate([
        x_arm_end - wall_t / 2,
        0,
        z_arm_bot - drop_len / 2 + clip_overlap / 2,
    ])
        cube([wall_t, drop_width_y, drop_len + clip_overlap], center = true);
}

module sponge_clip() {
    r_in  = sponge_gap / 2;
    r_out = r_in + wall_t;
    half_open = (360 - sponge_clip_wrap_deg) / 2;

    r_out_faucet  = clip_inner_d / 2 + wall_t;
    x_drop_center = -r_out_faucet - arm_len - wall_t / 2;
    z_drop_bot    = clip_height / 2 - wall_t - drop_len;

    // build the C-clip with axis along Z, mouth at +Y, then rotate so axis
    // becomes Y and mouth becomes -Z.
    translate([x_drop_center, 0, z_drop_bot - r_out + clip_overlap])
    rotate([-90, 0, 0])
    translate([0, 0, -sponge_clip_len_y / 2])
    linear_extrude(sponge_clip_len_y)
        difference() {
            difference() {
                circle(r = r_out);
                circle(r = r_in);
            }
            // mouth wedge on +Y direction (angle 90°)
            polygon([
                [0, 0],
                [(r_out + 2) * cos(90 - half_open),
                 (r_out + 2) * sin(90 - half_open)],
                [(r_out + 2) * cos(90 + half_open),
                 (r_out + 2) * sin(90 + half_open)],
            ]);
        }
}
