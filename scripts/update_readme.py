"""Fetch contribution counts and render the SVG memory card."""
import json
import os
from pathlib import Path
import sys
import urllib.request
import xml.etree.ElementTree as ET

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
    user = (payload.get('data') or {}).get('user')
    if not user:
        raise RuntimeError('GitHub user not found; README was not changed')
    calendar = user['contributionsCollection']['contributionCalendar']
    from render_memory import render as render_svg
    svg = render_svg(calendar)
    ET.fromstring(svg)  # refuse to save a card that isn't valid XML
    assets = ROOT / 'assets'
    assets.mkdir(exist_ok=True)
    tmp = assets / 'memory-card.svg.tmp'
    tmp.write_text(svg)
    os.replace(tmp, assets / 'memory-card.svg')



if __name__ == '__main__':
    main()
