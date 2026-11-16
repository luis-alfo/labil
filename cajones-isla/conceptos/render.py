import numpy as np

def render(parts, az=-38, el=30, size=(620, 520), margin=0.06, bounds=None):
    """Rasterizador ortográfico con z-buffer. parts = [(trimesh, (r,g,b)), ...]."""
    V = np.vstack([p[0].vertices for p in parts])
    offs = np.cumsum([0] + [len(p[0].vertices) for p in parts])
    F = np.vstack([p[0].faces + o for p, o in zip(parts, offs)])
    N = np.vstack([p[0].face_normals for p in parts])
    C = np.vstack([np.tile(p[1], (len(p[0].faces), 1)) for p in parts])
    a, e = np.radians(az), np.radians(el)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    R = Rx @ Rz
    P = V @ R.T
    B = (bounds @ R.T) if bounds is not None else P
    W, H = size
    bx, bz = B[:, 0], B[:, 2]
    s = (1 - 2 * margin) * min(W / np.ptp(bx), H / np.ptp(bz))
    px = (P[:, 0] - bx.min()) * s + (W - np.ptp(bx) * s) / 2
    py = H - ((P[:, 2] - bz.min()) * s + (H - np.ptp(bz) * s) / 2)
    depth = P[:, 1]
    n = N @ R.T
    luz = np.array([-0.45, -0.75, 0.6]); luz /= np.linalg.norm(luz)
    shade = 0.42 + 0.58 * np.abs(n @ luz)
    zbuf = np.full((H, W), np.inf); img = np.ones((H, W, 3)); fid = np.full((H, W), -1)
    for f, (i, j, k) in enumerate(F):
        x0, y0, x1, y1, x2, y2 = px[i], py[i], px[j], py[j], px[k], py[k]
        xmin, xmax = int(max(min(x0, x1, x2), 0)), int(min(max(x0, x1, x2) + 1, W))
        ymin, ymax = int(max(min(y0, y1, y2), 0)), int(min(max(y0, y1, y2) + 1, H))
        if xmin >= xmax or ymin >= ymax: continue
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9: continue
        X, Y = np.meshgrid(np.arange(xmin, xmax) + .5, np.arange(ymin, ymax) + .5)
        w0 = ((y1 - y2) * (X - x2) + (x2 - x1) * (Y - y2)) / den
        w1 = ((y2 - y0) * (X - x2) + (x0 - x2) * (Y - y2)) / den
        w2 = 1 - w0 - w1
        m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not m.any(): continue
        d = w0 * depth[i] + w1 * depth[j] + w2 * depth[k]
        sub = zbuf[ymin:ymax, xmin:xmax]
        upd = m & (d < sub)
        sub[upd] = d[upd]
        img[ymin:ymax, xmin:xmax][upd] = C[f] * shade[f]
        fid[ymin:ymax, xmin:xmax][upd] = f
    nrm = np.where(fid[..., None] >= 0, n[np.clip(fid, 0, None)], 0)
    edge = np.zeros((H, W), bool)
    for dy, dx in ((0, 1), (1, 0)):
        a1 = nrm[:H - dy, :W - dx]; a2 = nrm[dy:, dx:]
        f1, f2 = fid[:H - dy, :W - dx] >= 0, fid[dy:, dx:] >= 0
        e1 = ((np.sum(a1 * a2, -1) < 0.9) & f1 & f2) | (f1 != f2)
        z1, z2 = zbuf[:H - dy, :W - dx], zbuf[dy:, dx:]
        with np.errstate(invalid='ignore'):
            e1 |= np.isfinite(z1) & np.isfinite(z2) & (np.abs(z1 - z2) > 2.5)
        edge[:H - dy, :W - dx] |= e1
    img[edge] = (0.30, 0.27, 0.22)
    return img
