#!/usr/bin/env python3
"""Re-extract the web figures from the paper PDF.

The project page ships the manuscript figures as cropped bitmaps.  When the
paper is revised, re-run this instead of cropping by hand:

    python3 tools/extract_figures.py .tmp/2026_ICRA_Propra_v6.pdf

Requires ghostscript (`gs`) on PATH and Pillow.  The crop boxes below are
fractions of the page (x0, y0, x1, y1) and must be re-tuned if the layout of
the manuscript changes -- run with --check to write a contact sheet you can
eyeball before the assets are overwritten.
"""
import argparse, os, shutil, subprocess, sys, tempfile

try:
    from PIL import Image
    import numpy as np
except ImportError:
    sys.exit('Pillow and numpy are required: pip install pillow numpy')

DPI = 400

# name, 1-based page, (x0, y0, x1, y1) as fractions of the page
FIGURES = [
    ('fig1_overview',  1, (0.490, 0.1780, 0.960, 0.3652)),
    ('fig2_pretrain',  4, (0.060, 0.0450, 0.970, 0.2870)),
    ('fig3_policy',    5, (0.060, 0.0450, 0.487, 0.3112)),
    ('fig4_setup',     5, (0.060, 0.6720, 0.487, 0.8450)),
    ('fig5_retrieval', 6, (0.510, 0.0500, 0.970, 0.2398)),
    ('fig6_ttc',       7, (0.060, 0.3950, 0.487, 0.7080)),
    ('fig7_r2',        7, (0.510, 0.2250, 0.970, 0.4068)),
]

# Photographic figures compress far better as JPEG; diagrams and plots stay PNG.
AS_JPEG = {'fig1_overview': 92, 'fig4_setup': 92}
TASK_JPEG_QUALITY = 88

# The 2x2 grid of task stills inside Fig. 4, as a sub-region of page 5 plus
# pixel boxes within it (see --check output if the layout moves).
TASK_REGION = (0.255, 0.670, 0.500, 0.855)
TASK_COLS = [(106, 441), (452, 786)]
TASK_ROWS = [(62, 405), (427, 768)]
TASK_NAMES = [['PickCup', 'PickSponge'], ['MovePen', 'OpenLid']]


def render_pages(pdf, outdir):
    if not shutil.which('gs'):
        sys.exit('ghostscript (gs) not found on PATH')
    subprocess.run(
        ['gs', '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=png16m', f'-r{DPI}',
         '-dTextAlphaBits=4', '-dGraphicsAlphaBits=4',
         f'-sOutputFile={outdir}/p%02d.png', pdf],
        check=True)


def autotrim(im, pad=12, thresh=248):
    """Shrink-wrap the crop onto its ink so small box drifts do not matter."""
    mask = np.asarray(im.convert('L')) < thresh
    if not mask.any():
        return im
    ys, xs = np.where(mask)
    return im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad),
                    min(im.width, xs.max() + 1 + pad),
                    min(im.height, ys.max() + 1 + pad)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('-o', '--out', default='static/images')
    ap.add_argument('--check', metavar='PATH',
                    help='also write a contact sheet of every crop')
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        render_pages(args.pdf, tmp)
        produced = []

        for name, page, box in FIGURES:
            src = Image.open(f'{tmp}/p{page:02d}.png').convert('RGB')
            W, H = src.size
            x0, y0, x1, y1 = box
            im = autotrim(src.crop((int(x0 * W), int(y0 * H),
                                    int(x1 * W), int(y1 * H))))
            if im.width > 1800:
                im = im.resize((1800, round(im.height * 1800 / im.width)),
                               Image.LANCZOS)
            if name in AS_JPEG:
                path = os.path.join(args.out, name + '.jpg')
                im.save(path, quality=AS_JPEG[name], optimize=True, progressive=True)
            else:
                path = os.path.join(args.out, name + '.png')
                im.convert('P', palette=Image.ADAPTIVE, colors=160).save(path, optimize=True)
            produced.append((path, im))
            print(f'{name:16s} {im.size}  ->  {path}')

        # task stills, cut out of Fig. 4
        p5 = Image.open(f'{tmp}/p05.png').convert('RGB')
        W, H = p5.size
        fx0, fy0, fx1, fy1 = TASK_REGION
        sub = p5.crop((int(fx0 * W), int(fy0 * H), int(fx1 * W), int(fy1 * H)))
        for ri, (ry0, ry1) in enumerate(TASK_ROWS):
            for ci, (cx0, cx1) in enumerate(TASK_COLS):
                im = sub.crop((cx0, ry0, cx1, ry1))
                im = im.resize((720, round(im.height * 720 / im.width)), Image.LANCZOS)
                path = os.path.join(args.out, f'task_{TASK_NAMES[ri][ci].lower()}.jpg')
                im.save(path, quality=TASK_JPEG_QUALITY, optimize=True, progressive=True)
                produced.append((path, im))
                print(f'{TASK_NAMES[ri][ci]:16s} {im.size}  ->  {path}')

        # social preview card
        card = Image.new('RGB', (1200, 630), 'white')
        hero = Image.open(os.path.join(args.out, 'fig1_overview.jpg')).convert('RGB')
        w = 1160
        h = round(hero.height * w / hero.width)
        card.paste(hero.resize((w, h), Image.LANCZOS), (20, (630 - h) // 2))
        card.save(os.path.join(args.out, 'og_card.jpg'),
                  quality=90, optimize=True, progressive=True)
        print(f'{"og_card":16s} (1200, 630)  ->  {args.out}/og_card.jpg')

        if args.check:
            width = 900
            thumbs = [im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
                      for _, im in produced]
            sheet = Image.new('RGB', (width, sum(t.height + 16 for t in thumbs)), '#dddddd')
            y = 0
            for t in thumbs:
                sheet.paste(t, (0, y))
                y += t.height + 16
            sheet.save(args.check)
            print('contact sheet ->', args.check)


if __name__ == '__main__':
    main()
