# Film harness · Agent Science

```bash
chmod +x film/*.sh
./film/preflight.sh    # must exit 0
./film/build.sh        # demo/demo-final.mp4
./film/capture.sh      # rehearsal beat printer
```

**Outputs:** `demo/demo-final.mp4` · `demo/voiceover.mp3` · `submission/demo-final.mp4`

**Spine:** `docs/VIDEO-SCRIPT-2026-08-29.md` · truth-layer WOW first.

**Flipbook JSON:** bundled via `film/build.sh` (syncs screens + renders reel).  
**Cloud fallback:** if the flipbook sibling repo is absent, `film/render_reel.py` builds from `demo/flipbook.html` + `docs/assets/screens/`.
