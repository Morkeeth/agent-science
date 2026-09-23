# FINDING — shipping health gate requires parallel_sdk · 2026-09-23

**Objects:** `scripts/verify_partners_hosted.sh` · `scripts/eval_hosted_partner_baseline.py`
`shipping_health` · this VM's `clearance.search.sdk_available()`

## Measured

```bash
python3 -c 'from clearance import search; print(search.sdk_available(), search.integration_info()["transport"])'
# → False urllib-rest

pip show parallel-web
# → WARNING: Package(s) not found: parallel-web
```

`requirements.txt` pins `parallel-web==1.3.2`, but this agent image does not have it
installed. Local `/health` (after call-proof) reports `parallel_sdk: false` /
`parallel_transport: urllib-rest` while still proving Parallel **calls** via mocked REST.

Both `verify_partners_hosted.sh` and the shipping arm of
`eval_hosted_partner_baseline.py` assert `parallel_sdk: True`. That is the Parallel
**track preference**, not proof a search ran. After Oscar deploy, if the Cloud Run
image installs requirements, the assert is correct. If the image ships without the
SDK wheel, verify stays RED even with a working urllib Parallel path and a key.

## What we did not change tonight

Left the SDK assert in place (track prize surface). Call-proof and baseline still
prove the **embarrassing** stripped-health case (keys missing entirely). A follow-on
could split "SDK present" from "Parallel callable" the same way we split
`gemini_configured` from `gemini`.

## Related

- `docs/FINDING-gemini-health-env-alone-2026-09-20.md` — same class: presence ≠ call
- Track note in `clearance/search.py`: "SDK when installed … or REST"
