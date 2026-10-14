"""Which way is north in each Predator infrared frame?  The Predator circles its target, so every frame is turned
differently; only Blaber's schematic carries a north arrow.  This script reproduces the numbers in README.md
("Which way is north in each infrared frame"). The slides are the user's files and are not in this repository.

  python3 frame_orientation.py
        Fit Blaber's schematic onto the wide infrared frame and print the frame's north and look azimuth, and what the
        HUD azimuth implies for the HUD frame.  Needs numpy only.
  python3 frame_orientation.py --same-frame WIDE1.png WIDE2.png ...
        Check that slide screenshots share one background frame (SIFT + RANSAC on the infrared picture, annotations
        masked).  Needs opencv-python-headless.  A zoomed slide gives a handful of inliers, i.e. no match.
  python3 frame_orientation.py --figure OUT.png --schematic S.png --wide W.png --hud H.png
        Draw the north arrows (needs matplotlib, opencv, pillow).

Pixel positions below were read by eye from the screenshots (about +/-3 px on the schematic, +/-6 px on the wide frame,
where the label sits inside each outline).  The schematic is a sketch, not to scale, so treat the angles as +/-20 deg.
"""
import argparse
import math
import sys
from math import atan2, cos, degrees, radians, sin

import numpy as np

# Blaber schematic (slide "QRF INFIL/SHOOTDOWN IN RZR 01 - 6:14am", screenshot px; x right, y down) and the same
# features on the wide infrared frame (slide "Enemy Movement 5:56-6:03am", screenshot px).
SCHEMATIC = {"R2": (521.3, 64.7), "R1": (553.3, 116.7), "B2": (589.2, 85.8), "B1": (590.8, 154.2),
             "DSHK": (494.2, 23.7), "trench end": (574.7, 69.7)}
WIDE = {"R2": (250, 352), "R1": (340, 340), "B2": (290, 318), "B1": (383, 322),
        "DSHK": (195, 412), "trench end": (260, 321)}
NORTH_ARROW = 66.9                  # deg clockwise from page-up, measured on all four schematic panels (schematic_register.py)
PAGE_UP_BEARING = 360 - NORTH_ARROW  # 293.1
HUD_AZIMUTH = 232.79                # HUD field; read here as the camera's look direction (see README for the checks)
F_RANGE = (1.4, 2.9)                # f = 1/sin(depression angle): 46 to 20 deg of tilt, unknown for the frame


def fit(P, Q, f):
    """wide = t + diag(1,1/f) [[a,-b],[b,a]] schematic.  Linear in a, b, t for a given f."""
    P, Q = np.asarray(P, float), np.asarray(Q, float)
    A = np.zeros((2 * len(P), 4)); y = np.zeros(2 * len(P))
    A[0::2] = np.c_[P[:, 0], -P[:, 1], np.ones(len(P)), np.zeros(len(P))]
    A[1::2] = np.c_[P[:, 1] / f, P[:, 0] / f, np.zeros(len(P)), np.ones(len(P))]
    y[0::2], y[1::2] = Q[:, 0], Q[:, 1]
    sol = np.linalg.lstsq(A, y, rcond=None)[0]
    a, b = sol[0], sol[1]
    rms = math.sqrt((((A @ sol).reshape(-1, 2) - Q) ** 2).sum(1).mean())
    north = np.array([[a, -b], [b / f, a / f]]) @ [sin(radians(NORTH_ARROW)), -cos(radians(NORTH_ARROW))]
    psi = atan2(b, a)
    up_in_page = np.array([[cos(psi), sin(psi)], [-sin(psi), cos(psi)]]) @ [0.0, -1.0]     # camera-up in page axes
    look = (PAGE_UP_BEARING + degrees(atan2(up_in_page[0], -up_in_page[1]))) % 360
    return {"f": f, "rms_px": rms, "north_on_screen": degrees(atan2(north[0], -north[1])), "look_azimuth": look}


def north_on_screen(look_azimuth, f):
    """Screen angle (clockwise from up) of true north for a camera looking along `look_azimuth`, tilt factor f."""
    a = radians((0 - look_azimuth) % 360)
    return degrees(atan2(sin(a), cos(a) / f))


def circular(a):
    m = degrees(atan2(np.sin(np.radians(a)).mean(), np.cos(np.radians(a)).mean()))
    return m, np.percentile(((np.asarray(a) - m + 180) % 360) - 180, [5, 95])


def report():
    keys = list(SCHEMATIC)
    P, Q = [SCHEMATIC[k] for k in keys], [WIDE[k] for k in keys]
    print("Wide infrared frame: Blaber's schematic fitted onto it (6 features)")
    print("  tilt f  depression  rms px  north on screen  camera looks toward")
    for f in (1.0, 1.4, 1.7, 2.0, 2.4, 2.9):
        r = fit(P, Q, f)
        print(f"  {f:.1f}    {degrees(math.asin(1 / f)):4.0f} deg   {r['rms_px']:5.1f}   {r['north_on_screen']:+6.1f} deg      {r['look_azimuth']:5.1f} deg")
    print("  leave one feature out (f 1.4-2.9, best rms):")
    for k in keys:
        sub = [x for x in keys if x != k]
        r = min((fit([SCHEMATIC[x] for x in sub], [WIDE[x] for x in sub], f) for f in np.linspace(*F_RANGE, 31)), key=lambda d: d["rms_px"])
        print(f"    without {k:10s} north {r['north_on_screen']:+6.1f} deg, looks toward {r['look_azimuth']:5.1f} deg")
    rng, runs = np.random.default_rng(3), []
    for _ in range(1000):
        r = fit(np.array(P) + rng.normal(0, 3, (6, 2)), np.array(Q) + rng.normal(0, 6, (6, 2)), rng.uniform(*F_RANGE))
        runs.append((r["north_on_screen"], r["look_azimuth"]))
    runs = np.array(runs)
    for name, col in (("north on screen", 0), ("look azimuth", 1)):
        m, (lo, hi) = circular(runs[:, col])
        print(f"  label noise (3 px, 6 px) and f uniform in {F_RANGE}: {name} {m:.0f} deg, 5-95% {lo:+.0f}..{hi:+.0f} deg")
    # null: mirror the schematic; a plan view seen from above cannot be mirrored, so this should fit much worse
    mir = [(-x, y) for x, y in P]
    print(f"  mirrored schematic (should be worse): best rms {min(fit(mir, Q, f)['rms_px'] for f in np.linspace(*F_RANGE, 31)):.1f} px")

    hud = sorted((north_on_screen(HUD_AZIMUTH, F_RANGE[0]), north_on_screen(HUD_AZIMUTH, F_RANGE[1])))
    print(f"\nHUD frame: if {HUD_AZIMUTH} deg is the look direction, north is at {hud[0]:.0f} to {hud[1]:.0f} deg "
          f"clockwise from up (right, a little down); if it is the aircraft's bearing from the target, the camera looks "
          f"{(HUD_AZIMUTH + 180) % 360:.1f} deg and north is at {north_on_screen((HUD_AZIMUTH + 180) % 360, 1.75):.0f} deg.")
    wide_look = fit(P, Q, 1.75)["look_azimuth"]
    print(f"Schematic page-up is bearing {PAGE_UP_BEARING:.1f}; the wide frame looks toward {wide_look:.0f}, the HUD frame toward "
          f"{HUD_AZIMUTH:.0f}: {abs((HUD_AZIMUTH - wide_look + 180) % 360 - 180):.0f} deg apart the short way round.")


# ---- same-frame check -----------------------------------------------------------------------------------------------
def ir_rect(img):
    """Bounding box of the infrared picture inside a slide screenshot (not white margin, not dark UI)."""
    import cv2
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mid = (g > 35) & (g < 238)
    def longest(v):
        best, start = (0, 0, 0), None
        for i, ok in enumerate(list(v) + [False]):
            if ok and start is None: start = i
            if not ok and start is not None:
                best = max(best, (i - start, start, i)); start = None
        return best[1], best[2]
    (x0, x1), (y0, y1) = longest(mid.mean(0) > 0.55), longest(mid.mean(1) > 0.55)
    return x0, y0, x1, y1


def features(path):
    import cv2
    img = cv2.imread(path)
    x0, y0, x1, y1 = ir_rect(img)
    crop = img[y0:y1, x0:x1]
    g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    flat = cv2.blur(g.astype(np.float32), (9, 9)); var = cv2.blur((g.astype(np.float32) - flat) ** 2, (9, 9))
    box = cv2.morphologyEx(((g > 150) & (g < 225) & (var < 25)).astype(np.uint8), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    bad = (hsv[..., 1] > 60).astype(np.uint8) | box | cv2.dilate((g > 240).astype(np.uint8), np.ones((7, 7), np.uint8)) | (g < 12).astype(np.uint8)
    valid = (cv2.dilate(bad, np.ones((11, 11), np.uint8)) == 0).astype(np.uint8) * 255
    s = 900 / g.shape[1]
    g = cv2.createCLAHE(3.0, (8, 8)).apply(cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_AREA))
    valid = cv2.resize(valid, (g.shape[1], g.shape[0]), interpolation=cv2.INTER_NEAREST)
    return cv2.SIFT_create(nfeatures=4000, contrastThreshold=0.02).detectAndCompute(g, valid)


def match(a, b):
    import cv2
    (ka, da), (kb, db) = a, b
    good = [m for m, n in cv2.BFMatcher().knnMatch(da, db, k=2) if m.distance < 0.8 * n.distance]
    if len(good) < 8: return len(good), 0, None, None
    pa = np.float32([ka[m.queryIdx].pt for m in good]); pb = np.float32([kb[m.trainIdx].pt for m in good])
    M, inl = cv2.estimateAffinePartial2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=6, maxIters=5000, confidence=0.999)
    if M is None: return len(good), 0, None, None
    return len(good), int(inl.sum()), math.hypot(M[0, 0], M[1, 0]), degrees(atan2(M[1, 0], M[0, 0]))


def same_frame(paths):
    feats = [features(p) for p in paths]
    print("pair                 good  inliers  scale  rotation (deg, clockwise on screen)")
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            g, n, s, r = match(feats[i], feats[j])
            tail = f"{s:5.3f}  {r:+7.1f}" if s is not None else "  -       -"
            name = lambda q: q.split("/")[-1].rsplit(".", 1)[0][-6:]
            print(f"{name(paths[i]):>8} {name(paths[j]):<8}   {g:5d} {n:7d}  {tail}")
    print("Same still: more than a thousand inliers, scale 1.000, rotation 0.0. A handful of inliers means no match.")


# ---- figure ---------------------------------------------------------------------------------------------------------
def figure(out, schematic, wide, hud):
    import cv2
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch
    from PIL import Image

    def vec(theta, length):
        return length * sin(radians(theta)), -length * cos(radians(theta))

    def arrow(ax, x, y, theta, length, spread=None):
        for th in (np.linspace(*spread, 18) if spread else []):
            dx, dy = vec(th, length + 6); ax.plot([x, x + dx], [y, y + dy], color="#00e5ff", alpha=0.16, lw=6, zorder=3)
        dx, dy = vec(theta, length)
        ax.add_patch(FancyArrowPatch((x, y), (x + dx, y + dy), arrowstyle="-|>", mutation_scale=22, color="#00e5ff", lw=3.5, zorder=5))
        lx, ly = vec(theta, length + 26)
        ax.text(x + lx, y + ly, "N", color="#00e5ff", fontsize=17, fontweight="bold", ha="center", va="center", zorder=6)

    P, Q = list(SCHEMATIC.values()), list(WIDE.values())
    r = fit(P, Q, 1.75)
    lo, hi = fit(P, Q, F_RANGE[1])["north_on_screen"], fit(P, Q, F_RANGE[0])["north_on_screen"]
    hlo, hhi = north_on_screen(HUD_AZIMUTH, F_RANGE[1]), north_on_screen(HUD_AZIMUTH, F_RANGE[0])
    hmid = north_on_screen(HUD_AZIMUTH, 1.75)
    fig, axs = plt.subplots(1, 3, figsize=(27, 7.6), dpi=100)
    axs[0].imshow(cv2.cvtColor(cv2.imread(schematic), cv2.COLOR_BGR2RGB))
    axs[0].set_title(f"Blaber's schematic: his own arrow, north is {NORTH_ARROW:.0f} deg clockwise from page-up (page-up = bearing {PAGE_UP_BEARING:.0f})", fontsize=12)
    img = cv2.imread(wide); x0, y0, x1, y1 = ir_rect(img)
    axs[1].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)[y0:y1, x0:x1]); arrow(axs[1], 120, 175, r["north_on_screen"], 112, (lo, hi))
    axs[1].set_title(f"Wide infrared frame (five slides, one still): north {r['north_on_screen']:+.0f} deg ({lo:+.0f} to {hi:+.0f} by camera tilt); camera looks toward {r['look_azimuth']:.0f}", fontsize=12)
    axs[2].imshow(np.asarray(Image.open(hud).convert("RGB"))); arrow(axs[2], 190, 130, hmid, 160, (hlo, hhi))
    axs[2].set_title(f"Predator HUD frame: if {HUD_AZIMUTH} deg is the look direction, north is {hmid:.0f} deg clockwise from up", fontsize=12)
    for ax in axs: ax.axis("off")
    plt.tight_layout(); plt.savefig(out, dpi=100)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--same-frame", nargs="+", metavar="PNG")
    ap.add_argument("--figure", metavar="OUT.png")
    ap.add_argument("--schematic"); ap.add_argument("--wide"); ap.add_argument("--hud")
    a = ap.parse_args()
    if a.same_frame:
        same_frame(a.same_frame)
    elif a.figure:
        if not (a.schematic and a.wide and a.hud): sys.exit("--figure needs --schematic, --wide and --hud")
        figure(a.figure, a.schematic, a.wide, a.hud)
    else:
        report()
