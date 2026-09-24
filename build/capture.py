"""Cut each globe out of its live site, for the shelf on the front page.

Hides the sky canvas, the panels and the page background, screenshots with a transparent background, crops to
what is left (the globe and its glow) and saves a WebP into img/. Run again whenever a globe changes its look.
"""
import io, os
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'img'))
os.makedirs(OUT, exist_ok=True)

HIDE = """
  #sky, .panel, #tip, #hint, #scrub, #scrubber, .floatbtn, #credit, button { display: none !important; }
  html, body, #stage { background: transparent !important; }
"""
SITES = [
    ('world-time-zones', 'https://laurencefwhite.github.io/world-time-zones/',
     "['cities','names','labels','codes','times','wx','spin'].forEach(function(k){ if (k in WTZ.opt) WTZ.opt[k] = false; });"),
    ('celestial-globe', 'https://laurencefwhite.github.io/celestial-globe/',
     "['daylight','starnames','bayer','connames','lplanets','lmoons','lasteroids','lcomets','ldso','lsats','lshowers','lstars','spin','preview'].forEach(function(k){ if (k in CG.opt) CG.opt[k] = false; });"
     " try { CG.setTime(new Date('2026-09-24T12:30:00Z')); } catch (e) {} CG.draw();"),
    ('river-valleys', 'https://laurencefwhite.github.io/river-valleys/',
     "if (window.RV) { ['bnames','tnames','names','cities','spin'].forEach(function(k){ if (k in RV.opt) RV.opt[k] = false; }); RV.setView(22, 8, 1); }"),
    ('history-atlas', 'https://laurencefwhite.github.io/history-atlas/',
     "if (window.HA) { HA.opt.names = false; HA.opt.cities = false; HA.opt.oceans = false; HA.setYear(1300); HA.setView(62, 30, 1); }"),
]

def feather(im):
    """the same soft circular edge on every globe, whatever its own glow does at the frame"""
    from PIL import ImageDraw, ImageFilter, ImageChops
    n = im.size[0]
    m = Image.new('L', (n, n), 0)
    ImageDraw.Draw(m).ellipse((n * 0.035, n * 0.035, n * 0.965, n * 0.965), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(n * 0.012))
    r, g, b, a = im.split()
    return Image.merge('RGBA', (r, g, b, ImageChops.multiply(a, m)))

if __name__ == '__main__' and os.environ.get('FEATHER_ONLY'):
    for k in ('world-time-zones', 'celestial-globe', 'river-valleys', 'history-atlas'):
        pth = os.path.join(OUT, k + '.webp')
        feather(Image.open(pth).convert('RGBA')).save(pth, 'WEBP', quality=86, method=6)
    raise SystemExit('feathered existing images')

with sync_playwright() as pw:
    b = pw.chromium.launch()
    for key, url, setup in SITES:
        pg = b.new_page(viewport={'width': 1300, 'height': 1300}, device_scale_factor=2)
        pg.goto(url, wait_until='load')
        pg.wait_for_timeout(4500)                     # the opening fly-in, and the first data
        if setup:
            pg.evaluate(setup)
            if key == 'world-time-zones':
                pg.mouse.move(5, 5)
                for _ in range(2): pg.keyboard.press('-'); pg.wait_for_timeout(300)
            pg.wait_for_timeout(1500)
            if key == 'history-atlas':
                pg.wait_for_function('HA.chunksLoaded().pending === 0', timeout=30000)
                pg.wait_for_timeout(800)
                pg.evaluate('HA.setView(62, 30, 1)')
                pg.wait_for_timeout(600)
        pg.add_style_tag(content=HIDE)
        pg.wait_for_timeout(400)
        png = pg.screenshot(omit_background=True)
        im = Image.open(io.BytesIO(png)).convert('RGBA')
        a = im.split()[3].point(lambda v: 255 if v > 24 else 0)
        box = a.getbbox()
        im = im.crop(box)
        side = max(im.size)
        sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        sq.paste(im, ((side - im.size[0]) // 2, (side - im.size[1]) // 2))
        sq = sq.resize((560, 560), Image.LANCZOS)
        sq = feather(sq)
        path = os.path.join(OUT, key + '.webp')
        sq.save(path, 'WEBP', quality=86, method=6)
        print('%-18s crop %s -> %s  %d kB' % (key, box, os.path.basename(path), os.path.getsize(path) // 1024))
        pg.close()
    b.close()
