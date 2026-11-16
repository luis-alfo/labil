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

arm_len               = 30;     // arm centerline length (clip → arc start)
arm_width_y           = 24;     // uniform width along Y for arm-elbow-drop
elbow_r               = 8;      // 90° fillet radius
drop_len              = 18;     // drop centerline length (arc end → bottom)

sponge_gap            = 14;     // < 20 mm: pinches the sponge thickness
sponge_clip_len_y     = 50;
sponge_clip_wrap_deg  = 220;

$fn = 96;

union() {
    faucet_clip();
    arm_drop();
    sponge_clip();
}

// Reuse these in sponge_clip() so the drop end is the single source of truth
function _r_out_faucet() = clip_inner_d / 2 + wall_t;
function _z_arm()        = clip_height / 2 - wall_t / 2;
function _x_arm_start()  = -_r_out_faucet() + clip_overlap;
function _x_corner()     = _x_arm_start() - arm_len;
function _x_drop_end()   = _x_corner() - elbow_r;
function _z_drop_end()   = _z_arm() - elbow_r - drop_len;

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

// Arm + 90° fillet + drop, extruded along Y as a single continuous piece.
// Side profile is built from three 2D primitives: arm rectangle, elbow ring,
// drop rectangle.
module arm_drop() {
    z_arm    = _z_arm();
    x_start  = _x_arm_start();
    x_corner = _x_corner();
    z_corner = z_arm - elbow_r;
    x_drop   = _x_drop_end();
    z_bottom = _z_drop_end();

    translate([0, -arm_width_y / 2, 0])
    rotate([90, 0, 0])
    linear_extrude(height = arm_width_y)
        union() {
            // arm rectangle (centerline z_arm, ±wall_t/2 in Z)
            polygon([
                [x_start,  z_arm - wall_t / 2],
                [x_corner, z_arm - wall_t / 2],
                [x_corner, z_arm + wall_t / 2],
                [x_start,  z_arm + wall_t / 2],
            ]);
            // elbow: quarter-annular sector, center (x_corner, z_corner)
            translate([x_corner, z_corner])
                difference() {
                    intersection() {
                        difference() {
                            circle(r = elbow_r + wall_t / 2);
                            circle(r = elbow_r - wall_t / 2);
                        }
                        // wedge for 90°→180° (CCW)
                        polygon([
                            [0, 0],
                            [0, elbow_r + wall_t],
                            [-(elbow_r + wall_t), elbow_r + wall_t],
                            [-(elbow_r + wall_t), 0],
                        ]);
                    }
                }
            // drop rectangle (centerline x_drop, ±wall_t/2 in X)
            polygon([
                [x_drop - wall_t / 2, z_bottom],
                [x_drop + wall_t / 2, z_bottom],
                [x_drop + wall_t / 2, z_corner],
                [x_drop - wall_t / 2, z_corner],
            ]);
        }
}

module sponge_clip() {
    r_in  = sponge_gap / 2;
    r_out = r_in + wall_t;
    half_open = (360 - sponge_clip_wrap_deg) / 2;

    // attach to the bottom of the smooth drop (single source of truth)
    x_drop_center = _x_drop_end();
    z_drop_bot    = _z_drop_end();

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
