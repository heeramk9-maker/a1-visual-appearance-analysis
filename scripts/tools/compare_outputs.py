from pathlib import Path
import json

s = Path('outputs/sync/product_231031.json')
a = Path('outputs/async/product_231031.json')

print('Sync exists', s.exists(), 'Async exists', a.exists())
if s.exists() and a.exists():
    js = json.loads(s.read_text())
    ja = json.loads(a.read_text())

    def keyset(x):
        return set(x.keys())

    print('Top-level keys equal:', keyset(js) == keyset(ja))
    print('Sync keys:', sorted(keyset(js)))
    print('Async keys:', sorted(keyset(ja)))

    # Look into the aggregated result object structure
    print('result keys equal:', set(js['result'].keys()) == set(ja['result'].keys()))
    print('result keys sync:', sorted(js['result'].keys()))
    print('result keys async:', sorted(ja['result'].keys()))

    # Compare the shape of 'raw' items and image ids
    sync_ids = [r.get('image_id') or (r.get('image') or {}).get('id') or r.get('image') for r in js['result'].get('raw', [])]
    async_ids = [r.get('image_id') or (r.get('image') or {}).get('id') or r.get('image') for r in ja['result'].get('raw', [])]
    print('number of raw items equal:', len(sync_ids) == len(async_ids), len(sync_ids), len(async_ids))
    print('sync ids:', sync_ids)
    print('async ids:', async_ids)

    async_errors = [r for r in ja['result'].get('raw', []) if r.get('errors')]
    print('async per-image errors count:', len(async_errors))
else:
    print('Missing files to compare')
