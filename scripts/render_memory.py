"""Render the real contribution calendar as purple memory-card blocks."""
from html import escape


def render(calendar):
    colors=dict(zip(['NONE','FIRST_QUARTILE','SECOND_QUARTILE','THIRD_QUARTILE','FOURTH_QUARTILE'],
                    ['#292735','#504069','#7855a4','#a777dc','#d1adff']))
    days=[d for w in calendar['weeks'] for d in w['contributionDays']]
    total=calendar['totalContributions']
    active=sum(d['contributionCount']>0 for d in days)
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="190" viewBox="0 0 900 190" role="img" aria-labelledby="title desc">',
         '<title id="title">Contribution memory card</title>',
         f'<desc id="desc">{active} active days and {total} contributions, {days[0]["date"]} to {days[-1]["date"]}. Brighter purple means more contributions.</desc>']
    for x,week in enumerate(calendar['weeks']):
        for day in week['contributionDays']:
            y=day['weekday']
            label=escape(f'{day["date"]}: {day["contributionCount"]} contributions')
            out.append(f'<rect x="{20+x*16}" y="{10+y*17}" width="11" height="11" rx="1" fill="{colors[day["contributionLevel"]]}"><title>{label}</title></rect>')
    out.append(f'<text x="20" y="162" font-family="monospace" font-size="13" fill="#92869f">{active} days saved / {total} contributions</text>')
    out.append('<rect x="857" y="151" width="8" height="12" fill="#b88cef"/>')
    out.append('</svg>')
    return '\n'.join(out)
