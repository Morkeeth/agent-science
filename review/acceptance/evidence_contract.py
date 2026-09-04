"""External acceptance script for the evidence-integrity change.

Run unchanged against both commits. Inputs come from the audit's failure cases;
only document fetching is replaced. No network or model calls are required.
"""
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

for name in ('REFUSAL_LOG_GCS_URI','CORPUS_GCS_URI'):
    os.environ.pop(name,None)
from clearance import instruments,refusal_log,dictionary
from clearance.facts import Claim,judge_claim

positive='The Acme project permits commercial redistribution of its software.'
negative='The Acme project does not permit commercial redistribution of its software.'
results=[]
for claim,source,expected in [(positive,positive,True),(negative,positive,False),(positive,negative,False),(negative,negative,True)]:
    with patch.object(instruments,'document',return_value=source):
        result=judge_claim(Claim('acceptance',claim,'https://example.org/terms','commercial'),fetch=True)
    results.append({'check':'polarity','claim':claim,'source':source,'passed':(result.verdict=='GREEN')==expected})
with tempfile.TemporaryDirectory() as temp:
    path=Path(temp)/'claims.db';con=refusal_log.connect(path)
    uncertain='It is uncertain whether the Acme project permits commercial redistribution.'
    refusal_log.record(con,term='Acme',assertion=uncertain,verdict='GREEN',production='acceptance',citation_url='https://example.org/terms',quoted_terms=uncertain)
    answer=dictionary.lookup('the Acme project permits commercial redistribution',db=path,live=False)
    results.append({'check':'uncertainty is not support','passed':answer['label']!='SOURCED'})
print(json.dumps(results,indent=2))
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
