"""Explicit research providers. Provider output is a lead, never source proof."""
import json
import http.client
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from clearance import search

PROVIDERS = ('parallel', 'perplexity')


def find(provider, query, *, live=False, limit=5, trace=None):
    if provider not in PROVIDERS:
        raise ValueError('provider must be parallel or perplexity')
    if not isinstance(query,str) or not 1 <= len(query.strip()) <= 1500:
        raise ValueError('query must contain 1–1500 characters')
    if type(limit) is not int or not 1 <= limit <= 10:
        raise ValueError('results per provider must be 1–10')
    trace = trace if trace is not None else []
    if provider == 'parallel':
        return search.find_sources(query,[query],live=live,refresh=live,max_results=limit,trace=trace,**search.private_paths()) or []
    event={'route':'perplexity','queries':[query],'outcome':'skipped'}
    trace.append(event)
    if not live:
        event['reason']='live search disabled; no Perplexity cache'
        return []
    key=os.environ.get('PERPLEXITY_API_KEY','').strip()
    path=Path.home()/'.config/keys/perplexity.key'
    if not key and path.is_file():key=path.read_text().strip()
    if not key:
        event.update(outcome='unavailable',reason='PERPLEXITY_API_KEY is not configured')
        return []
    request=urllib.request.Request('https://api.perplexity.ai/search',method='POST',
        data=json.dumps({'query':query,'max_results':limit,'search_context_size':'medium'}).encode(),
        headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    start=time.monotonic()
    event['outcome']='started'
    try:
        with urllib.request.urlopen(request,timeout=45) as response:
            raw=response.read(2_000_001)
        if len(raw)>2_000_000:raise ValueError('oversized response')
        payload=json.loads(raw)
        if not isinstance(payload,dict) or not isinstance(payload.get('results'),list):
            raise ValueError('invalid response')
        results=[]
        for row in payload['results'][:limit]:
            if not isinstance(row,dict) or not all(isinstance(row.get(k),str) for k in ('url','title','snippet')):
                raise ValueError('invalid search result')
            results.append(search.Candidate(row['url'],row['title'],row['snippet'][:400]))
        event.update(outcome='completed',search_id=payload.get('id'),candidates=len(results),
            urls=[c.url for c in results],usage='Provider billing not returned; no cost inferred')
        return results
    except urllib.error.HTTPError as exc:
        event.update(outcome='error',reason=f'Perplexity HTTP {exc.code}')
    except (OSError, ValueError, urllib.error.URLError, http.client.HTTPException):
        # Never include provider bodies, request headers or exception text.
        event.update(outcome='error',reason='Perplexity transport or response failure')
    finally:
        event['elapsed_ms']=round((time.monotonic()-start)*1000)
    return []
