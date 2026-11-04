from pathlib import Path
from datetime import datetime, timezone
import json
import os
import urllib.parse
import urllib.request

import yaml


ROOT = Path(__file__).resolve().parents[1]
METRICS_FILE = ROOT / 'data' / 'scholar_metrics.yml'

AUTHOR_ID = 'o1WEf7wAAAAJ'


def fetch_scholar_metrics():
    api_key = os.environ.get('SERPAPI_KEY')

    if not api_key:
        raise SystemExit(
            'SERPAPI_KEY is not set. '
            'Add it as a GitHub Actions repository secret.'
        )

    params = {
        'engine': 'google_scholar_author',
        'author_id': AUTHOR_ID,
        'hl': 'en',
        'api_key': api_key,
        'output': 'json',
    }

    url = 'https://serpapi.com/search?' + urllib.parse.urlencode(params)

    request = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'SOL-Yonsei-Scholar-Updater/1.0'
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))

    if data.get('error'):
        raise RuntimeError(f"SerpApi error: {data['error']}")

    table = data.get('cited_by', {}).get('table', [])

    metrics = {}

    for item in table:
        if 'citations' in item:
            metrics['citations'] = item['citations'].get('all')

        if 'h_index' in item:
            metrics['h_index'] = item['h_index'].get('all')

        if 'i10_index' in item:
            metrics['i10_index'] = item['i10_index'].get('all')

    required = ('citations', 'h_index', 'i10_index')

    missing = [
        key
        for key in required
        if metrics.get(key) is None
    ]

    if missing:
        raise RuntimeError(
            'Could not retrieve Scholar metrics: '
            + ', '.join(missing)
        )

    return metrics


def save_metrics(metrics):
    output = {
        'author_id': AUTHOR_ID,
        'citations': metrics['citations'],
        'h_index': metrics['h_index'],
        'i10_index': metrics['i10_index'],
        'updated_at': datetime.now(timezone.utc).strftime(
            '%Y-%m-%d %H:%M UTC'
        ),
    }

    METRICS_FILE.write_text(
        yaml.safe_dump(
            output,
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding='utf-8',
    )


def main():
    metrics = fetch_scholar_metrics()
    save_metrics(metrics)

    print(
        'Google Scholar metrics updated: '
        f'Citations={metrics["citations"]}, '
        f'h-index={metrics["h_index"]}, '
        f'i10-index={metrics["i10_index"]}'
    )


if __name__ == '__main__':
    main()
