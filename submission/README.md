# Submission folder · Agent Science · Agentic Cinema

**Deadline:** Sep 9 2026 14:00 PDT · **Track:** Parallel

## Ship checklist

| # | Item | Path / action |
|---|------|----------------|
| 1 | **Video** ≤180s public | `demo/demo-final.mp4` → YouTube/Vimeo URL in `VIDEO-URL.txt` |
| 2 | **Devpost** | `docs/DEVPOST-READY.md` + `docs/SUBMISSION-PACK-2026-08-29.md` §0 |
| 3 | **Hosted** | https://agent-science-568004190078.us-central1.run.app |
| 4 | **Repo** | https://github.com/Morkeeth/agent-science (public, MIT) |
| 5 | **Screenshot** | `docs/assets/screens/08-visibility-ui.png` |
| 6 | **Sealed** | `docs/SEALED-PREDICTION-2026-08-31.md` |

## Build video

```bash
./film/preflight.sh
./film/build.sh
cp demo/demo-final.mp4 submission/demo-final.mp4
```

## Pitch (30s)

> Agent Science is the truth layer for what agentic builders believe and use. Transparent websearch — angles searched, field signals, sourced or refused — and CONTRARY TO RESEARCH when the field outruns papers. Ask once; shelf compounds.

Full: `docs/PITCH-TOMORROW.md`

## Film pack

| File | Purpose |
|------|---------|
| `demo/FILM-AND-SUBMIT.md` | Teleprompter |
| `demo/RECORD-IT-FRESH.md` | Record options |
| `demo/voiceover.txt` | Kokoro script |
| `demo/voiceover.mp3` | Rendered audio |
| `demo/flipbook.html` | Hand storyboard |
| `film/build.sh` | Full pipeline |
| `film/preflight.sh` | Gate before upload |

## After submit

- [ ] Logged-out: video plays on Devpost entry
- [ ] Logged-out: hosted URL loads
- [ ] Note submission URL in `docs/STATUS.md`
