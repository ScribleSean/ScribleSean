"""Fetch contribution counts and render the SVG memory card."""
import json
import os
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
QUERY = '''query($login: String!) {
  user(login: $login) { contributionsCollection {
    contributionCalendar { totalContributions weeks {
      contributionDays { date contributionCount contributionLevel weekday }
    } }
  } }
}'''


def main():
    if len(sys.argv) > 1:
        payload = json.loads(Path(sys.argv[1]).read_text())
    else:
        request = urllib.request.Request(
            'https://api.github.com/graphql',
            data=json.dumps({'query': QUERY, 'variables': {'login': os.environ['PROFILE_LOGIN']}}).encode(),
            headers={'Authorization': f'Bearer {os.environ["GH_TOKEN"]}',
                     'Content-Type': 'application/json', 'User-Agent': 'profile-memory-card'},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    if payload.get('errors'):
        raise RuntimeError('GitHub contribution query failed; README was not changed')
    calendar = payload['data']['user']['contributionsCollection']['contributionCalendar']
    from render_memory import render as render_svg
    assets = ROOT / 'assets'
    assets.mkdir(exist_ok=True)
    (assets / 'memory-card.svg').write_text(render_svg(calendar))



if __name__ == '__main__':
    main()
