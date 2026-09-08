"""Draw the console from geometric surfaces, using colored ASCII glyphs only."""
from pathlib import Path
from html import escape
import math

ROOT = Path(__file__).resolve().parents[1]


def uv(x, y, origin, a, b):
    x, y = x-origin[0], y-origin[1]
    det = a[0]*b[1]-a[1]*b[0]
    return ((x*b[1]-y*b[0])/det, (a[0]*y-a[1]*x)/det)


def surface(x, y):
    # Carry handle, behind the disc lid.
    u,v = uv(x,y,(183,43),(223,47),(0,41))
    if 0<u<1 and 0<v<1 and (u<.055 or u>.945 or v<.18):
        return '=', '#9d90b8'
    u,v = uv(x,y,(45,165),(240,50),(135,-100))
    if 0<=u<=1 and 0<=v<=1:
        if min(u,v,1-u,1-v)<.025:
            return '+', '#d5b8ff'
        r = math.hypot((u-.50)*1.08,(v-.50))
        if .34<r<.365:
            return '=', '#c2a6ef'
        if r<.34:
            # Small nested cube mark, with no wordmark.
            lx,ly=(u-.5)*100,(v-.5)*100
            if max(abs(lx),abs(ly))<6 and max(abs(lx),abs(ly))>3.4:
                return '#', '#e2d5f4'
            if abs(lx)<1.7 and abs(ly)<1.7:
                return '+', '#bba0e8'
            return '.', '#342b47'
        if math.hypot(u-.12,v-.21)<.047 or math.hypot(u-.87,v-.22)<.047:
            return 'o', '#d4bbea'
        return ':', '#b384e9'
    u,v = uv(x,y,(45,165),(240,50),(0,170))
    if 0<=u<=1 and 0<=v<=1:
        if min(u,v,1-u,1-v)<.022:
            return '+', '#c5a4f0'
        if .13<v<.56:
            for center in (.15,.38,.62,.85):
                r=math.hypot((u-center)*1.4,(v-.34))
                if .095<r<.12:
                    return 'o', '#d5d2df'
                if r<=.095:
                    if abs(u-center)<.014 and abs(v-.34)<.02:
                        return '+', '#a6a0bb'
                    return '.', '#242030'
            return ':', '#9693a8'
        if .68<v<.84 and (.15<u<.41 or .59<u<.85):
            if .69<v<.73 or .80<v<.83:
                return '=', '#aa94cf'
            return '_', '#332642'
        if v>.92:
            return '=', '#4a3669'
        return ':', '#a276da'
    u,v = uv(x,y,(285,215),(135,-100),(0,170))
    if 0<=u<=1 and 0<=v<=1:
        if min(u,v,1-u,1-v)<.02:
            return '|', '#a580ce'
        if .18<u<.88 and .20<v<.89:
            return ('|' if int(u*31)%2 else ':'), ('#49315e' if int(u*31)%2 else '#9b72c4')
        return '.', '#8b61b5'
    return None


def render():
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="480" height="410" viewBox="0 0 480 410" role="img" aria-labelledby="title desc">',
           '<title id="title">Indigo GameCube in colored ASCII</title>',
           '<desc id="desc">A code-drawn GameCube with disc lid, cube mark, carry handle, four controller ports and two memory-card slots.</desc>',
           '<g font-family="monospace" font-size="7" font-weight="600" text-anchor="middle">']
    for row in range(57):
        y=12+row*6.8
        for col in range(96):
            x=8+col*4.7
            cell=surface(x,y)
            if cell:
                ch,color=cell
                if ch==':' and (row*7+col*11)%5==0:
                    ch='.'
                parts.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}">{escape(ch)}</text>')
    parts.append('</g></svg>')
    out=ROOT/'assets'/'gamecube.svg'
    out.parent.mkdir(exist_ok=True)
    out.write_text('\n'.join(parts))


if __name__=='__main__':
    render()
