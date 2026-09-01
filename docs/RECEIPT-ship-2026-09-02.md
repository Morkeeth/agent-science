# Receipt — AS-SHIP-3 Judge UX · visibility panel HTML

**Date:** 2026-09-02  
**Branch:** `cursor/as-ship-judge-ux-2026-09-01`  
**Slice:** Replace monospace `<pre>` dump on `/visibility/ui` with judge-facing HTML panel.

## SHIPPED

- `_visibility_panel_html()` + rewritten `_visibility_page()` in `cloud/service.py`
- Verdict badge (SOURCED / UNSOURCED / CONTRARY_TO_RESEARCH / UNKNOWN)
- Transparency card: SHALLOW_ROUTE strip, angles table, IMBALANCE line — above fold
- Track-brief hook: *Paste a script. Get every checkable claim sourced verbatim — or refused with cause.*
- Footer: hosted URL + `/truths/ui` + JSON API link
- Tests: `test_visibility_html_panel`, extended `test_visibility_ui_renders_transparency`, `test_visibility_ui_sourced_badge`

## VERIFIED

| Claim | Command | Result |
|-------|---------|--------|
| Tests pass | `python3 tests/test_visibility_transparency.py` | **5/5** |
| Registry surface tests | `python3 tests/test_registry_surface.py` | **17/17** |
| Local smoke HTML | `curl -s 'http://localhost:8080/visibility/ui?q=ralph+loop+agentic' \| grep 'badge contrary'` | **1** (CONTRARY_TO_RESEARCH) |
| JSON API unchanged | `curl -s 'http://localhost:8080/visibility?q=ralph+loop+agentic'` | `primary: CONTRARY_TO_RESEARCH`, transparency keys present |
| No `<pre>` dump | `curl -s 'http://localhost:8080/visibility/ui?q=ralph+loop+agentic' \| grep -c '<pre>'` | **0** |

## Screenshots

| When | Path |
|------|------|
| Before (hosted monospace dump) | `docs/assets/screens/08-visibility-ui.png` |
| After (local judge panel) | `docs/assets/screens/08-visibility-ui-after.png` |

## WRONG / NOT VERIFIED

- **Hosted URL not updated** — deploy not run (Oscar click). `./deploy.sh` required for https://agent-science-568004190078.us-central1.run.app/visibility/ui to show new panel.
- **Before screenshot is from prior hosted capture** — not re-fetched tonight; local after shot is authoritative for new UI.
- **Field adoption / stack-fit sections** only render when data present; not separately tested for empty cases.

## Deploy note (Oscar)

```bash
./deploy.sh
# then verify:
curl -s 'https://agent-science-568004190078.us-central1.run.app/visibility/ui?q=ralph+loop+agentic' | grep 'badge contrary'
python3 scripts/capture_screens.py  # refresh 08-visibility-ui.png on hosted
```
