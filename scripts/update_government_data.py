"""Validate existing data; no government registry synchronization is implemented."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    bundle = json.loads((ROOT / 'taiwan_parks_database.json').read_text(encoding='utf-8'))
    total = 0
    ids = set()
    for pid, park in bundle['parks'].items():
        assert park['county_id'] in bundle['counties'], f'Unknown county: {pid}'
        assert pid in bundle['counties'][park['county_id']]['parks'], f'County mismatch: {pid}'
        for client in park['clients']:
            assert isinstance(client['id'], int) and client['id'] > 0, f'Invalid ID: {pid}'
            assert client['id'] not in ids, f'Duplicate ID: {client["id"]}'
            assert client['name'].strip(), f'Empty name: {pid}'
            ids.add(client['id'])
            total += 1
    message = f'Dataset format checked: {len(bundle["parks"])} parks, {total} records. Official verification NOT performed. Existing data includes generated examples.'
    print(message)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as output:
            output.write(message + '\n')
    subprocess.run([sys.executable, 'build_index_html.py'], cwd=ROOT, check=True)

if __name__ == '__main__':
    main()
