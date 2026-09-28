# PROPRA — project page

Project page for **“Self-Supervised Anchoring of Fingertip Sensing to Proprioception and
Proactive Actions for Robot Imitation Learning”** (PROPRA), submitted to IEEE ICRA 2026.

Static site — no build step. Open `index.html`, or serve the folder:

```bash
python3 -m http.server 8000     # then open http://localhost:8000
```

The page is deliberately plain: one serif, warm greys and nothing else for colour, hairlines
instead of shadows, a single column. No CSS framework and no external requests — one
stylesheet, one webfont, and the figures carry the only colour on the page. The only JavaScript
is two inline snippets in `index.html` that make the success-rate bars grow when scrolled into
view; without JS (or with reduced motion, or when printing) the bars simply render at full length. Content is kept short on purpose —
the figures carry the story, prose is one paragraph per section at most: teaser video and
abstract, **two sensors, two moments** (Fig. 1 and the recorded sensor streams in `sample.mp4`),
**method** (Fig. 2), **results** (success-rate bar chart for Tables I+II with the exact numbers in
a collapsible table, Figs. 6–7) and the **rollout videos**. Figs. 3, 4, 5 stay in `static/images/`
but are not on the page. Each bar carries its mean in `--v` and SD in `--sd`; series colours are
the paper figures' own (`.chart` in `propra.css`).

Several blocks are commented out rather than deleted, so they are easy to switch back on after
acceptance: the hero **Paper (PDF)** button, the **Fig. 1** teaser image (replaced by a teaser
video slot), and the whole **BibTeX** section together with its nav link and the anonymity
notice that sat inside it.

## Languages

`index.html` (English) and `index_epo.html` (Esperanto) are the same page in two languages —
same sections, same assets, same CSS and JS. The top bar carries an `EN` / `EO` switch, and each
file declares the pair with `<link rel="alternate" hreflang>` plus its own `lang` attribute and
`og:locale`.

Keep them in step: any edit to one belongs in the other. Structural drift is easy to spot —
both files should yield the same list of block classes in the same order:

```bash
python3 - <<'EOF'
import re
skel = lambda f: re.findall(
    r'<(?:section|div|article|figure|details|header|footer|nav)[^>]*class="([^"]*)"',
    open(f, encoding='utf-8').read())
a, b = skel('index.html'), skel('index_epo.html')
print('in step' if a == b else 'DRIFTED', len(a), len(b))
EOF
```

Task names (PickCup, PickSponge, MovePen, OpenLid), the BibTeX entry and the maintenance
comments in the HTML stay in English on both pages; everything a visitor reads is translated.

## ⚠️ This page is anonymous on purpose

The manuscript is under **double-blind review** and links to this page from its abstract.
Author names, affiliations, lab/homepage links and analytics are all deliberately absent.
Keep it that way until the paper is accepted.

**After acceptance**, de-anonymise by editing these spots in `index.html`:

| What | Where |
| --- | --- |
| Authors and affiliations | the `.authors` / `.affil` block in the hero |
| “Under review — IEEE ICRA 2026” | the `.venue-chip` in the hero |
| arXiv / Code buttons | the `.links` block — drop `is-pending`, set real `href`s |
| Paper (PDF) button | commented out in the `.links` block |
| BibTeX entry + anonymity notice | the whole `#bibtex` section is commented out, as is its nav link |
| Canonical URL | `og:url` in `<head>` (currently the anonymous 4open.science link) |

## Adding the videos

Every clip is authored as `<video poster="…">`, so **the page is already complete without
them** — the poster still is shown until the mp4 exists, and the clip starts playing the
moment you drop the file in. No HTML changes needed for the rollout gallery:

```
static/videos/teaser.mp4          # hero slot, above the one-paragraph idea
static/videos/sample.mp4          # recorded sensor streams, #sensing (poster: images/sample.jpg)
static/videos/supplementary.mp4   # the #video section
static/videos/task_pickcup.mp4    # rollout cards
static/videos/task_picksponge.mp4
static/videos/task_movepen.mp4
static/videos/task_openlid.mp4
```

The two large slots (`teaser`, `supplementary`) are 16:9 and each sits behind a placeholder:
delete the `.video-placeholder` div and uncomment the `<video>` (or YouTube `<iframe>`) written
in the comment just above it. The four rollout cards need no HTML change at all.

Keep them short (5–10 s), muted, looping and roughly square (the cards are 1:1);
H.264 mp4, ≲ 4 MB each. A reasonable encode:

```bash
ffmpeg -i raw.mp4 -vf "scale=720:-2,fps=25" -an \
       -c:v libx264 -crf 26 -preset slow -movflags +faststart \
       static/videos/task_pickcup.mp4
```

## Figures

Figures under `static/images/` are cropped straight out of the manuscript PDF.
When the paper is revised, regenerate them rather than re-cropping by hand:

```bash
python3 tools/extract_figures.py .tmp/2026_ICRA_Propra_v6.pdf --check /tmp/sheet.png
```

Needs `ghostscript` plus Pillow and numpy. Check `/tmp/sheet.png` before committing — the
crop boxes are page fractions and will drift if the manuscript layout changes.

The page currently shows only **Fig. 2** (method); Fig. 1 is commented out in the teaser, where
a video slot took its place. The script also
produces the figures that were cut to keep the page short, and they are kept in
`static/images/` so a section can be added back with a single `<figure class="fig">` block:

| File | Manuscript | Would suit |
| --- | --- | --- |
| `fig3_policy.png` | Fig. 3 | how the encoders enter the diffusion policy |
| `fig5_retrieval.png` | Fig. 5 | tactile↔proximity retrieval without direct pairing |
| `fig6_ttc.png` | Fig. 6 | time-to-contact decoded from the frozen embedding |
| `fig7_r2.png` | Fig. 7 | the same predictor transferred to policy-execution data |
| `fig4_setup.jpg` | Fig. 4 | hardware / experimental setup |

`static/paper/propra_icra2026_anonymous.pdf` is the anonymised manuscript served by the
“Paper (PDF)” button. Swap it for the camera-ready version later, or delete both the file
and the button if you would rather not host it.

## Layout

```
index.html                 the page, English
index_epo.html             the same page, Esperanto
static/css/propra.css      the only stylesheet
static/images/             figures, task stills, social card, favicon
static/videos/             drop the mp4s here
static/paper/              anonymised manuscript
tools/extract_figures.py   regenerate static/images/ from the paper PDF
tools/snippets/            markup parked for later (success-rate charts)
```

`tools/snippets/results-chart.html` holds the success-rate charts that were removed from
`#results`. They are plain HTML/CSS, not images: each bar's number lives in its `--v` (mean) and
`--sd` (standard deviation) custom properties. The file carries its own `<style>` block and
restore instructions. Its four series expect an accent palette the page no longer defines, so
give them colours before using it.

Nothing under `static/js/` or `static/css/` other than `propra.css` is loaded any more; the
leftover Nerfies template assets (Bulma, `bulma-carousel`, `bulma-slider`, FontAwesome,
`index.js`) are kept on disk only so the template stays recoverable. The one third-party request
is Google Fonts.

## Website license

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />
This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.

Built on the [Nerfies project page](https://nerfies.github.io) template.
