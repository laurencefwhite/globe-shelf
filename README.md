---
title: The Globe Shelf
subtitle: The front page for a growing collection of interactive globes
---

The front page at https://laurencefwhite.github.io/globe-shelf/ for the globes:

- World Time Zones – https://laurencefwhite.github.io/world-time-zones/
- Celestial Globe – https://laurencefwhite.github.io/celestial-globe/
- River Valleys – https://laurencefwhite.github.io/river-valleys/
- History Atlas – https://laurencefwhite.github.io/history-atlas/

The page is a shelf: each globe stands on a brass meridian stand, and empty stands wait, unlabelled, for the globes
still being made. Below the shelf, each globe gets a short description and a link.

# Adding a globe

1. Add its address to `SITES` in `build/capture.py` (with any set-up that turns labels off or chooses a good
   view), and run it to cut the globe out of the live site into `img/`.
2. In `index.html`, turn one empty stand into a filled one (copy a filled `<li class="stand">`) and add an
   entry to the catalogue. Add a new empty stand if more are on the way. Empty stands carry no name, so what
   is being made stays private until it is ready.

`build/capture.py` needs Python with Playwright and Pillow. It hides each site's sky, panels and page
background, screenshots the globe on a transparent background, crops it and gives every globe the same soft
edge.

# Copyright

© 2026 Laurence F. White. All rights reserved. Each globe names its own data sources and licences.
