"""Gera a ilha v2 (~1 km) a partir de Unreal/Data/Mapa/mapa_v2.json.

Uso:  python -I Unreal/mapa_gerar.py
Precisa de numpy e Pillow (o Python do sistema tem os dois). É determinístico: mude o JSON e rode de novo.

Saídas em Unreal/Data/Mapa/gerado/:
  heightmap_1009.r16 / .png   relevo para o Landscape (16 bits, Z scale 100: 1 unidade = 1/128 m, 32768 = nível do mar)
  camada_<nome>.png           pesos das camadas de pintura do Landscape (8 bits, somam 255)
  T_Mapa_Base.png             imagem limpa da ilha (2048 px, norte para cima), estilo cartoon
  T_Mapa_Aquarela.png         a mesma ilha com filtro de aquarela (proposta de direção de arte)
  Previa_Mapa*.png            as imagens acima com grade, nomes dos POIs, acampamentos e pontes (revisão de design)
  mapa_ue.json                tudo em coordenadas da Unreal (cm; X = norte, Y = leste) para os scripts do editor
Os arquivos do Landscape já saem na orientação da Unreal (linha = Y/leste, coluna = X/norte).
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "Data", "Mapa")
OUT = os.path.join(DATA, "gerado")
IMG = 2048


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def value_noise(n, cells, rng):
    g = rng.random((cells + 1, cells + 1))
    t = np.linspace(0, cells, n)
    i0 = np.clip(np.floor(t).astype(int), 0, cells - 1)
    f = t - i0
    f = f * f * (3 - 2 * f)
    a, b = g[i0][:, i0], g[i0][:, i0 + 1]
    c, d = g[i0 + 1][:, i0], g[i0 + 1][:, i0 + 1]
    fx, fy = f[None, :], f[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(n, base_cells, octaves, rng, gain=0.5):
    total, amp, norm, cells = 0.0, 1.0, 0.0, base_cells
    for _ in range(octaves):
        total = total + amp * value_noise(n, cells, rng)
        norm += amp
        amp *= gain
        cells *= 2
    return total / norm


def dist_polyline(E, N, pts, pad=None):
    """Distância de cada pixel até a polilinha e a posição ao longo dela (m).
    Com `pad`, só calcula numa faixa de `pad` metros em volta de cada segmento (o resto fica inf)."""
    pts = np.asarray(pts, float)
    best = np.full(E.shape, np.inf)
    along = np.zeros(E.shape)
    cum = 0.0
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        abx, aby = bx - ax, by - ay
        L2 = abx * abx + aby * aby
        L = math.sqrt(L2)
        if L2 == 0:
            continue
        if pad is None:
            sl = (slice(None), slice(None))
        else:
            x0, step, nn = E[0, 0], E[0, 1] - E[0, 0], E.shape[1]
            i0 = max(0, int((min(ax, bx) - pad - x0) / step))
            i1 = min(nn, int((max(ax, bx) + pad - x0) / step) + 2)
            j0 = max(0, int((min(ay, by) - pad - x0) / step))
            j1 = min(nn, int((max(ay, by) + pad - x0) / step) + 2)
            if i0 >= i1 or j0 >= j1:
                cum += L
                continue
            sl = (slice(j0, j1), slice(i0, i1))
        e, nv = E[sl], N[sl]
        t = np.clip(((e - ax) * abx + (nv - ay) * aby) / L2, 0, 1)
        d = np.hypot(e - (ax + t * abx), nv - (ay + t * aby))
        b, a = best[sl], along[sl]  # views: escrever neles atualiza best/along
        m = d < b
        b[m] = d[m]
        a[m] = cum + t[m] * L
        cum += L
    return best, along


def resample(pts, step):
    """Pontos a cada `step` metros ao longo da polilinha."""
    pts = np.asarray(pts, float)
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        k = max(1, int(float(np.hypot(*(b - a))) // step))
        out.extend(a + (b - a) * i / k for i in range(1, k + 1))
    return np.array(out)


def cumlen(pts):
    return np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])


def sample(arr, xs, x, y):
    """Valor bilinear de arr[norte, leste] em coordenadas de design."""
    step = xs[1] - xs[0]
    fx = np.clip((np.asarray(x) - xs[0]) / step, 0, len(xs) - 1.001)
    fy = np.clip((np.asarray(y) - xs[0]) / step, 0, len(xs) - 1.001)
    i, j = fx.astype(int), fy.astype(int)
    tx, ty = fx - i, fy - j
    return (arr[j, i] * (1 - tx) + arr[j, i + 1] * tx) * (1 - ty) + (arr[j + 1, i] * (1 - tx) + arr[j + 1, i + 1] * tx) * ty


def box_blur(a, r):
    """Média móvel separável (raio r pixels)."""
    k = 2 * r + 1
    p = np.pad(a, r, mode="edge")
    c = np.cumsum(np.cumsum(p, 0), 1)
    c = np.pad(c, ((1, 0), (1, 0)))
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def font(names, size):
    for f in names:
        p = os.path.join("C:/Windows/Fonts", f)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def tileable_noise(size, cells, rng):
    """Ruído de valor que repete nas bordas (para textura que ladrilha)."""
    g = rng.random((cells, cells))
    t = np.arange(size) * cells / size
    i0 = np.floor(t).astype(int) % cells
    i1 = (i0 + 1) % cells
    f = t - np.floor(t)
    f = f * f * (3 - 2 * f)
    a, b, c, d = g[i0][:, i0], g[i0][:, i1], g[i1][:, i0], g[i1][:, i1]
    fx, fy = f[None, :], f[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def pigment_texture(size, rng):
    """Variação de pigmento de aquarela para o material do terreno (512 px, ladrilhável, 0..1)."""
    total, amp, norm = 0.0, 1.0, 0.0
    for cells in (4, 8, 16, 32, 64):
        total = total + amp * tileable_noise(size, cells, rng)
        norm += amp
        amp *= 0.55
    t = total / norm
    t = (t - t.min()) / (t.max() - t.min())
    return Image.fromarray((t * 255).astype(np.uint8))


def watercolor(img, rng):
    """Filtro de aquarela: manchas chapadas, borda escurecida (pigmento acumulado), sangria e papel."""
    simple = img.filter(ImageFilter.MedianFilter(7)).filter(ImageFilter.ModeFilter(9))
    c = np.asarray(simple).astype(float) / 255
    n = c.shape[0]
    # sangria: desloca a amostragem com um ruído suave (a tinta "escorre" uns pixels)
    dx = (value_noise(n, 48, rng) - 0.5) * 7
    dy = (value_noise(n, 48, rng) - 0.5) * 7
    jj, ii = np.mgrid[0:n, 0:n]
    c = c[np.clip((jj + dy).astype(int), 0, n - 1), np.clip((ii + dx).astype(int), 0, n - 1)]
    # borda escura onde a cor muda (diferença entre a imagem e uma versão borrada)
    blur = np.asarray(Image.fromarray((c * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4))).astype(float) / 255
    edge = np.clip(np.abs(c - blur).sum(-1) * 3.2, 0, 1)[..., None]
    c = c * (1 - 0.45 * edge)
    # pigmento irregular e granulação do papel
    pigment = 0.9 + 0.2 * fbm(n, 10, 4, rng)
    grain = 0.93 + 0.07 * fbm(n, 220, 2, rng) + rng.normal(0, 0.015, (n, n))
    c = c * pigment[..., None] * grain[..., None]
    # tinta transparente: clareia em direção ao branco do papel e tira um pouco de saturação
    gray = c.mean(-1, keepdims=True)
    c = gray + (c - gray) * 0.85
    c = 1 - (1 - c) * 0.82
    paper = np.array([0.99, 0.96, 0.90])
    c = c * paper
    return Image.fromarray(np.clip(c * 255, 0, 255).astype(np.uint8))


def main():
    cfg = json.load(open(os.path.join(DATA, "mapa_v2.json"), encoding="utf-8"))
    T = cfg["terreno"]
    n, side = T["resolucao"], T["lado_m"]
    spacing = side / (n - 1)
    rng = np.random.default_rng(T["semente"])
    xs = np.linspace(-side / 2, side / 2, n)
    E, N = np.meshgrid(xs, xs)  # arrays [norte, leste]
    r = np.hypot(E, N)

    # --- costa e terreno base ---------------------------------------------------------------
    coast = T["raio_costa_m"] + T["ruido_costa_m"] * (fbm(n, 3, 4, rng) - 0.5) * 2
    land = smoothstep(coast + 25, coast - 35, r)
    inland = smoothstep(coast, coast - 90, r)
    base = (T["altura_base_min_m"] + T["altura_base_var_m"] * fbm(n, 3, 5, rng)) * inland + 0.6
    detail = (fbm(n, 24, 4, rng) - 0.5) * 1.2

    # --- morros: gaussiana + ruído cumeado, unidos por norma-4 (máximo suave, sem vinco) ----------
    ridged = 1 - np.abs(2 * fbm(n, 6, 5, rng) - 1)
    acc = np.zeros_like(E)
    for m in cfg["morros"]:
        d = np.hypot(E - m["x"], N - m["y"])
        bump = m["altura"] * np.exp(-3.0 * (d / m["raio"]) ** 2) * (1 - m["aspereza"] + m["aspereza"] * 1.6 * ridged)
        acc += bump ** 4
    hills = acc ** 0.25
    hills *= smoothstep(coast + 60, coast - 20, r)  # a serra pode cair no mar como falésia

    h = base + hills + detail * inland
    h = h * land + T["fundo_mar_m"] * (1 - land)

    # --- POIs: nivelar o chão (borda irregular, para não virar um círculo perfeito) ----------------
    poi_noise = (fbm(n, 16, 3, rng) - 0.5) * 2
    for p in cfg["pois"]:
        if not p["raio"]:
            continue
        d = np.hypot(E - p["x"], N - p["y"]) + 0.15 * p["raio"] * poi_noise
        inside = d < p["raio"]
        target = float(np.mean(h[inside])) if p["altura"] == "auto" else float(p["altura"])
        w = 1 - smoothstep(p["raio"] * 0.75, p["raio"] * 1.6, d)
        h = h * (1 - w) + target * w
        p["_z"] = target

    h_pre_water = h.copy()
    smooth = box_blur(h, 6)

    # --- lagos ---------------------------------------------------------------------------------
    water_surface = np.where(h < 0.3, 0.0, -np.inf)  # mar no nível 0
    lake_noise = fbm(n, 12, 3, rng) - 0.5
    lake_q = []
    for lk in cfg["lagos"]:
        q = np.hypot((E - lk["x"]) / lk["rx"], (N - lk["y"]) / lk["ry"]) + 0.18 * lake_noise
        rim = (q > 1.25) & (q < 1.6)
        level = min(lk["nivel"], float(np.min(h_pre_water[rim])) - 0.8)
        lk["_nivel"] = round(level, 2)
        core = q < 1.0
        bed = level - lk["profundidade"] * np.sqrt(np.clip(1 - q * q, 0, 1)) - 0.3
        shore = smoothstep(1.0, 1.3, q)
        h = np.where(core, np.minimum(h, bed), np.minimum(h, (level + 0.35) * (1 - shore) + h * shore))
        water_surface = np.where(core, np.maximum(water_surface, level), water_surface)
        lake_q.append(q)

    # --- rio: traçado com meandros; a água desce sempre, 1,2 m abaixo do terreno suavizado -----------
    rv = cfg["rio"]
    rp = resample(rv["pontos"], 3.0)
    rs = cumlen(rp)
    tang = np.gradient(rp, axis=0)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True)
    normal = np.stack([-tang[:, 1], tang[:, 0]], 1)
    ph = rng.random(2) * 2 * math.pi
    wiggle = 0.6 * np.sin(2 * math.pi * rs / 150 + ph[0]) + 0.4 * np.sin(2 * math.pi * rs / 61 + ph[1])
    taper = smoothstep(0, 40, rs) * smoothstep(rs[-1], rs[-1] - 60, rs)
    for lk in cfg["lagos"]:
        q = np.hypot((rp[:, 0] - lk["x"]) / lk["rx"], (rp[:, 1] - lk["y"]) / lk["ry"])
        taper *= smoothstep(1.0, 1.6, q)
    rp = rp + normal * (rv["meandro_m"] * wiggle * taper)[:, None]
    rs = cumlen(rp)
    terr = sample(smooth, xs, rp[:, 0], rp[:, 1])
    wl = terr - rv["abaixo_do_terreno_m"]
    for lk in cfg["lagos"]:
        inl = np.hypot((rp[:, 0] - lk["x"]) / lk["rx"], (rp[:, 1] - lk["y"]) / lk["ry"]) < 0.95
        wl[inl] = np.minimum(wl[inl], lk["_nivel"])
    wl = np.maximum(np.minimum.accumulate(wl), 0.0)
    wl[-1] = 0.0
    bank_w = rv["margem_m"]
    dr, sr = dist_polyline(E, N, rp, pad=bank_w + 15)
    w_lo, w_hi = rv["largura_m"]
    half = (w_lo + (w_hi - w_lo) * sr / rs[-1]) / 2
    water_r = np.interp(sr, rs, wl)
    core = dr < half
    bed = water_r - 0.25 - rv["profundidade_m"] * np.clip(1 - (dr / half) ** 2, 0, 1)
    bank = smoothstep(0, bank_w, dr - half)
    h = np.where(core, np.minimum(h, bed),
                 np.where(dr < half + bank_w, np.minimum(h, (water_r + 0.4) * (1 - bank) + h * bank), h))
    water_surface = np.where(core, np.maximum(water_surface, water_r), water_surface)
    is_water = h < water_surface

    # --- inclinação e camadas de pintura ----------------------------------------------------------
    gy, gx = np.gradient(h, spacing)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))

    def region(lst, noise_amp=0.25):
        m = np.zeros_like(E)
        nz = fbm(n, 10, 3, rng) - 0.5
        for g in lst:
            q = np.hypot((E - g["x"]) / g["rx"], (N - g["y"]) / g["ry"]) + noise_amp * nz
            m = np.maximum(m, 1 - smoothstep(0.85, 1.05, q))
        return m

    d_road = np.full(E.shape, np.inf)
    for rd in cfg["estradas"]:
        d_road = np.minimum(d_road, dist_polyline(E, N, rd["pontos"], pad=10)[0])
    near_water = np.minimum(dr - half, np.min([np.where(q < 1, 0, (q - 1) * 60) for q in lake_q], axis=0))

    poi_paved = np.zeros_like(E)
    poi_any = np.zeros_like(E)
    for p in cfg["pois"]:
        if not p["raio"]:
            continue
        d = np.hypot(E - p["x"], N - p["y"]) + 0.15 * p["raio"] * poi_noise
        if p["tipo"] in ("cidade", "forte", "ruinas"):
            poi_paved = np.maximum(poi_paved, 1 - smoothstep(p["raio"] * 0.55, p["raio"] * 0.8, d))
        poi_any = np.maximum(poi_any, 1 - smoothstep(p["raio"] * 0.9, p["raio"] * 1.2, d))

    mask = {
        "Rocha": np.maximum(smoothstep(30, 42, slope), smoothstep(52, 64, h)),
        "Areia": np.maximum(smoothstep(2.4, 1.0, h) * smoothstep(coast - 140, coast - 40, r),  # praias
                            smoothstep(6, 1, near_water) * smoothstep(1.5, 0.3, h - np.maximum(water_surface, 0))),  # margens
        "Pedra": poi_paved,
        "Terra": 1 - smoothstep(2.5, 4.5, d_road),
        "Selva": region(cfg["regioes"]["selva"]) * (1 - poi_any),
        "Floresta": np.maximum(region(cfg["regioes"]["floresta"]), smoothstep(0.63, 0.69, fbm(n, 8, 4, rng)) * smoothstep(8, 20, h)) * (1 - poi_any),
        "Campo": np.maximum(region(cfg["regioes"]["campos"], 0.15), smoothstep(0.66, 0.72, fbm(n, 8, 4, rng))) * (1 - poi_any * 0.7),
    }
    mask["Areia"] = np.where(h < 0.2, 1.0, mask["Areia"])  # fundo do mar e dos lagos
    order = ["Rocha", "Areia", "Pedra", "Terra", "Selva", "Floresta", "Campo"]
    weights, remaining = {}, np.ones_like(E)
    for k in order:
        weights[k] = np.clip(mask[k], 0, 1) * remaining
        remaining = remaining - weights[k]
    weights["Grama"] = remaining
    layer_names = order + ["Grama"]

    # --- arquivos do Landscape (orientação da Unreal: linha = leste/Y, coluna = norte/X) -------------
    os.makedirs(OUT, exist_ok=True)
    hv = np.clip(np.round(32768 + h * 128), 0, 65535).astype("<u2").T
    hv.tofile(os.path.join(OUT, "heightmap_1009.r16"))
    Image.fromarray(hv.astype(np.uint16)).save(os.path.join(OUT, "heightmap_1009.png"))
    w8 = np.floor(np.stack([weights[k] for k in layer_names]) * 255).astype(np.int32)
    w8[-1] += 255 - w8.sum(0)  # o resto vai para a grama: soma exata 255
    for k, arr in zip(layer_names, w8):
        Image.fromarray(arr.astype(np.uint8).T).save(os.path.join(OUT, f"camada_{k}.png"))

    # --- imagem do mapa, estilo cartoon (norte para cima) ------------------------------------------
    pal = {"Grama": (132, 196, 76), "Campo": (190, 210, 92), "Floresta": (70, 140, 58), "Selva": (40, 112, 70),
           "Areia": (236, 214, 150), "Rocha": (150, 142, 132), "Pedra": (186, 180, 170), "Terra": (196, 160, 104)}
    col = sum(weights[k][..., None] * np.array(pal[k], float) for k in layer_names)
    high = smoothstep(55, 80, h)[..., None]
    col = col * (1 - high) + np.array([214, 208, 198.0]) * high
    nrm = np.sqrt(gx * gx + gy * gy + 1)
    light = np.array([-0.55, 0.55, 0.62])
    light /= np.linalg.norm(light)
    shade = (-gx * light[0] - gy * light[1] + light[2]) / nrm
    col = col * np.clip(0.55 + 0.6 * shade, 0.35, 1.25)[..., None]
    depth = np.clip(water_surface - h, 0, 8)
    ocean = (water_surface == 0.0) & is_water
    wcol = np.where(ocean[..., None], np.array([60, 160, 215.0]) * (1 - depth[..., None] / 14),
                    np.array([80, 182, 226.0]) * (1 - depth[..., None] / 20))
    col = np.where(is_water[..., None], wcol, col)
    foam = is_water & (depth < 0.6)
    col = np.where(foam[..., None], col * 0.6 + 255 * 0.4, col)
    img = Image.fromarray(np.flipud(np.clip(col, 0, 255)).astype(np.uint8)).resize((IMG, IMG), Image.LANCZOS)

    px_per_m = IMG / side

    def to_px(x, y):
        return ((x + side / 2) * px_per_m, (side / 2 - y) * px_per_m)

    # árvores como pontinhos escuros, como no mapa do Fortnite
    tree_rng = np.random.default_rng(11)
    draw = ImageDraw.Draw(img, "RGBA")
    for k, dens, fill in (("Floresta", 0.008, (28, 80, 36, 200)), ("Selva", 0.016, (18, 66, 40, 220))):
        cand = np.argwhere((weights[k] > 0.5) & ~is_water)
        for j, i in cand[tree_rng.random(len(cand)) < dens]:
            cx, cy = to_px(xs[i] + tree_rng.uniform(-0.6, 0.6), xs[j] + tree_rng.uniform(-0.6, 0.6))
            rad = 3.4 if k == "Floresta" else 2.8
            draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=fill)
    img.save(os.path.join(OUT, "T_Mapa_Base.png"))
    aq = watercolor(img, np.random.default_rng(5))
    aq.save(os.path.join(OUT, "T_Mapa_Aquarela.png"))
    pigment_texture(512, np.random.default_rng(3)).save(os.path.join(OUT, "T_Pigmento.png"))

    # --- pontes: onde as estradas cruzam o rio --------------------------------------------------------
    bridges = []
    for rd in cfg["estradas"]:
        pts = np.asarray(rd["pontos"], float)
        for a, b in zip(pts[:-1], pts[1:]):
            for c_, d_ in zip(rp[:-1], rp[1:]):
                den = (b[0] - a[0]) * (d_[1] - c_[1]) - (b[1] - a[1]) * (d_[0] - c_[0])
                if abs(den) < 1e-9:
                    continue
                t = ((c_[0] - a[0]) * (d_[1] - c_[1]) - (c_[1] - a[1]) * (d_[0] - c_[0])) / den
                u = ((c_[0] - a[0]) * (b[1] - a[1]) - (c_[1] - a[1]) * (b[0] - a[0])) / den
                if 0 <= t <= 1 and 0 <= u <= 1:
                    pos = a + t * (b - a)
                    yaw = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
                    s_here = float(dist_polyline(np.array([[pos[0]]]), np.array([[pos[1]]]), rp)[1][0, 0])
                    bridges.append({"estrada": rd["nome"], "x": round(float(pos[0]), 1), "y": round(float(pos[1]), 1),
                                    "rumo_graus": round(yaw, 1), "_agua": float(np.interp(s_here, rs, wl))})

    # --- prévias de design: grade, POIs, acampamentos, pontes ---------------------------------------
    def overlay(base_img, style):
        prev = base_img.copy()
        d2 = ImageDraw.Draw(prev, "RGBA")
        if style == "cartoon":
            grid, txt, stroke, fnames = (255, 255, 255, 70), "white", (20, 20, 30), ["impact.ttf", "arialbd.ttf"]
        else:
            grid, txt, stroke, fnames = (90, 60, 40, 60), (58, 40, 30), (250, 244, 230), ["segoeprb.ttf", "segoepr.ttf", "georgiab.ttf"]
        for g in range(1, 10):
            p = g * IMG / 10
            d2.line([(p, 0), (p, IMG)], fill=grid, width=2)
            d2.line([(0, p), (IMG, p)], fill=grid, width=2)
        fs = font(fnames, 30)
        for g in range(10):
            c = (g + 0.5) * IMG / 10
            d2.text((c, 20), "ABCDEFGHIJ"[g], font=fs, fill=txt, anchor="mm", stroke_width=3, stroke_fill=stroke)
            d2.text((20, c), str(g + 1), font=fs, fill=txt, anchor="mm", stroke_width=3, stroke_fill=stroke)
        for br in bridges:
            cx, cy = to_px(br["x"], br["y"])
            ang = math.radians(br["rumo_graus"])
            dx, dy = math.cos(ang) * 22, -math.sin(ang) * 22
            d2.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=(120, 80, 40, 255), width=11)
        for kind, rad, colr in (("pequeno", 7, (255, 214, 64)), ("medio", 10, (255, 140, 40)), ("elite", 14, (230, 40, 40))):
            for x, y in cfg["acampamentos"][kind]:
                cx, cy = to_px(x, y)
                d2.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=colr + (255,), outline=(0, 0, 0, 255), width=3)
        fl = font(fnames, 38 if style == "cartoon" else 34)
        for p in cfg["pois"]:
            cx, cy = to_px(p["x"], p["y"])
            if p["tipo"] == "montanha":
                cy -= 42
            d2.text((cx, cy), p["nome"].upper() if style == "cartoon" else p["nome"], font=fl, fill=txt, anchor="mm",
                    stroke_width=5 if style == "cartoon" else 4, stroke_fill=stroke)
        return prev

    overlay(img, "cartoon").save(os.path.join(OUT, "Previa_Mapa.png"))
    overlay(aq, "aquarela").save(os.path.join(OUT, "Previa_Mapa_Aquarela.png"))

    # --- textura da interface (minimapa, mapa M, mapa da queda) --------------------------------------
    # Aquarela + nomes dos POIs + grade 10x10 sobre a área exibida pelo mapa completo (±VISTA m), com as letras
    # e números dentro dessa área. Acampamentos e pontes ficam de fora (são informação de design, não de jogo).
    vista = cfg.get("interface", {}).get("meia_vista_m", 560)
    ui = aq.copy()
    du = ImageDraw.Draw(ui, "RGBA")
    x0, y0 = to_px(-vista, vista)
    x1, y1 = to_px(vista, -vista)
    cell = (x1 - x0) / 10
    ink, paper = (58, 40, 30), (250, 244, 230)
    for g in range(1, 10):
        du.line([(x0 + g * cell, y0), (x0 + g * cell, y1)], fill=(70, 50, 35, 55), width=2)
        du.line([(x0, y0 + g * cell), (x1, y0 + g * cell)], fill=(70, 50, 35, 55), width=2)
    fg = font(["segoeprb.ttf", "segoepr.ttf", "georgiab.ttf"], 34)
    for g in range(10):
        c = g + 0.5
        du.text((x0 + c * cell, y0 + 26), "ABCDEFGHIJ"[g], font=fg, fill=ink, anchor="mm", stroke_width=3, stroke_fill=paper)
        du.text((x0 + 24, y0 + c * cell), str(g + 1), font=fg, fill=ink, anchor="mm", stroke_width=3, stroke_fill=paper)
    fpoi = font(["segoeprb.ttf", "segoepr.ttf", "georgiab.ttf"], 46)
    for p in cfg["pois"]:
        cx, cy = to_px(p["x"], p["y"])
        if p["tipo"] == "montanha":
            cy -= 44
        du.text((cx, cy), p["nome"], font=fpoi, fill=ink, anchor="mm", stroke_width=5, stroke_fill=paper)
    ui.save(os.path.join(OUT, "T_Mapa_UI.png"))

    def grid_cell(x, y):
        col = int((x + vista) / (2 * vista) * 10)
        row = int((vista - y) / (2 * vista) * 10)
        return "ABCDEFGHIJ"[min(max(col, 0), 9)] + str(min(max(row, 0), 9) + 1)

    # --- validação e saída para a Unreal ---------------------------------------------------------------
    def info(x, y):
        return float(sample(h, xs, x, y)), float(sample(slope, xs, x, y)), bool(sample(is_water.astype(float), xs, x, y) > 0.5)

    def ue(x, y, z):
        return {"x": round(y * 100), "y": round(x * 100), "z": round(z * 100)}

    problems = []
    camps_out = {}
    for kind, lst in cfg["acampamentos"].items():
        if kind.startswith("_"):
            continue
        camps_out[kind] = []
        for x, y in lst:
            hz, sl, wet = info(x, y)
            if wet or hz < 1.0 or sl > 25:
                problems.append(f"acampamento {kind} ({x},{y}): altura {hz:.1f} m, inclinação {sl:.0f}°, água={wet}")
            camps_out[kind].append(ue(x, y, hz))
    pois_out = []
    for p in cfg["pois"]:
        hz, sl, wet = info(p["x"], p["y"])
        if wet and p["tipo"] != "lago":
            problems.append(f"POI {p['nome']} está na água")
        pois_out.append({"id": p["id"], "nome": p["nome"], "tipo": p["tipo"], "kit": p["kit"], "raio_cm": p["raio"] * 100,
                         "grade": grid_cell(p["x"], p["y"]), **ue(p["x"], p["y"], hz)})

    land_mask = h > 0.3
    land_area = float(np.sum(land_mask)) * spacing ** 2 / 1e6
    cols = np.where(land_mask.any(0))[0]
    rows = np.where(land_mask.any(1))[0]
    span_ew = (cols[-1] - cols[0]) * spacing
    span_ns = (rows[-1] - rows[0]) * spacing
    out = {
        "_doc": "Gerado por Unreal/mapa_gerar.py a partir de mapa_v2.json. Coordenadas em cm da Unreal: X = norte, Y = leste.",
        "landscape": {"arquivo_altura": "gerado/heightmap_1009.r16", "resolucao": n,
                      "location": {"x": -side * 50, "y": -side * 50, "z": 0},
                      "scale": {"x": spacing * 100, "y": spacing * 100, "z": 100}, "camadas": layer_names,
                      "componentes": "8 x 8, 2 x 2 seções de 63 quads (1008 quads por lado)"},
        "mapa_imagem": {"arquivos": ["gerado/T_Mapa_Base.png", "gerado/T_Mapa_Aquarela.png", "gerado/T_Mapa_UI.png"],
                        "cobre_cm": {"x_min": -side * 50, "x_max": side * 50, "y_min": -side * 50, "y_max": side * 50},
                        "orientacao": "topo = norte (+X), direita = leste (+Y)",
                        "interface": {"textura": "T_Mapa_UI", "meia_vista_cm": vista * 100,
                                      "grade": "10 x 10 sobre ±meia_vista: colunas A-J de oeste para leste, linhas 1-10 de norte para sul"}},
        "area_terra_km2": round(land_area, 3),
        "extensao_m": {"leste_oeste": round(span_ew), "norte_sul": round(span_ns)},
        "altura_max_m": round(float(h.max()), 1),
        "pois": pois_out,
        "acampamentos": camps_out,
        "rio": {"nome": rv["nome"], "pontos": [ue(float(x), float(y), float(z)) for (x, y), z in list(zip(rp, wl))[::4]]
                + [ue(float(rp[-1][0]), float(rp[-1][1]), 0.0)]},
        "lagos": [{"nome": lk["nome"], **ue(lk["x"], lk["y"], lk["_nivel"]), "raio_norte_cm": lk["ry"] * 100, "raio_leste_cm": lk["rx"] * 100}
                  for lk in cfg["lagos"]],
        "pontes": [{"estrada": b["estrada"], "rumo_graus": b["rumo_graus"], **ue(b["x"], b["y"], b["_agua"] + 1.5)} for b in bridges],
        "estradas": [{"nome": rd["nome"], "pontos": [ue(x, y, float(sample(h, xs, x, y))) for x, y in rd["pontos"]]} for rd in cfg["estradas"]],
    }
    json.dump(out, open(os.path.join(OUT, "mapa_ue.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"terra: {land_area:.2f} km² | extensão {span_ew:.0f} m (L-O) × {span_ns:.0f} m (N-S) | altura máx {h.max():.1f} m")
    print("lagos:", ", ".join(f"{lk['nome']} nível {lk['_nivel']} m" for lk in cfg["lagos"]))
    print(f"rio: {rs[-1]:.0f} m, água de {wl[0]:.1f} m até 0 m | pontes: {len(bridges)}")
    print("POIs:", ", ".join(f"{p['nome']} {p['_z']:.1f} m" for p in cfg["pois"] if "_z" in p))
    print("cobertura do solo (%):", {k: round(float(weights[k][land_mask].mean()) * 100, 1) for k in layer_names})
    print("problemas:" if problems else "sem problemas de posição", *problems, sep="\n  ")


if __name__ == "__main__":
    main()
