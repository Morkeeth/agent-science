# Planted stale artifact claim — DO NOT "fix" to match reality

This file exists so the artifact-claims eval can watch a control go RED.
The number below is intentionally wrong. Shipping must label it STALE.
Null and trust-doc baseline must miss it (they never open the object).

claims on disk: **999999**

(Measured truth is the live `cache/refusal_log.db` claim count after
`python3 scripts/boot_registry.py`, which is nowhere near 999999.)
