from design_data import *
z=totals(); tot=sum(sum(v.values()) for v in z.values())
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1330 960" font-family="Helvetica, Arial, sans-serif"><rect width="1330" height="960" fill="#f4f1ea"/>']
svg.append('<text x="40" y="36" font-size="22" font-weight="700" fill="#222">Triangle budget: 800k for the whole area</text>')
svg.append('<text x="40" y="58" font-size="12" fill="#555">Design estimates, not measured. Evaluated triangles, every instance counted, text curves included, as the room validators count.</text>')
x0=40; w=1250; zones=[('Yard',z['Yard'],'#8a9a6a'),('Cafeteria',z['Cafeteria'],'#d9822b'),('Hall',z['Hall'],'#5a7a9a'),('Shared',z['Shared'],'#7a7a7a')]
res=TARGET-tot; bar_y=80; cx=x0
for name,g,col in zones:
    s=sum(g.values()); ww=w*s/TARGET
    svg.append(f'<rect x="{cx:.1f}" y="{bar_y}" width="{ww:.1f}" height="34" fill="{col}" stroke="#fff"/><text x="{cx+8:.1f}" y="{bar_y+22}" font-size="13" font-weight="700" fill="#fff">{name} {s//1000}k</text>')
    cx+=ww
ww=w*res/TARGET
svg.append(f'<rect x="{cx:.1f}" y="{bar_y}" width="{ww:.1f}" height="34" fill="#fff" stroke="#999" stroke-dasharray="5 3"/><text x="{cx+4:.1f}" y="{bar_y+22}" font-size="10.5" fill="#444">reserve {round(res/1000)}k</text>')
svg.append(f'<text x="{x0}" y="{bar_y+54}" font-size="12" fill="#222">Planned {tot:,d} of {TARGET:,d}; reserve {res:,d} ({100*res/TARGET:.0f}%) is held back for hero pieces, LOD slack and review changes.</text>')
svg.append(f'<text x="{x0}" y="{bar_y+70}" font-size="12" fill="#222">The repo flags rooms over 400k, so this area needs that noted when it goes to review.</text>')
y=bar_y+100
svg.append(f'<rect x="30" y="{y-16}" width="880" height="22" fill="#e7e2d6"/>')
for cxx,t in [(40,'Zone / group / item'),(640,'Count'),(720,'Each'),(810,'Total')]: svg.append(f'<text x="{cxx}" y="{y}" font-size="11" font-weight="700" fill="#222">{t}</text>')
y+=18; cur=None
for zone,grp,name,n,t in ITEMS:
    if zone!=cur:
        cur=zone; svg.append(f'<text x="40" y="{y}" font-size="12" font-weight="700" fill="#8a2d1a">{zone}  {sum(z[zone].values()):,d}</text>'); y+=15
    svg.append(f'<text x="52" y="{y}" font-size="10.5" fill="#444">{grp}: {name}</text><text x="680" y="{y}" font-size="10.5" text-anchor="end" fill="#222">{n}</text><text x="765" y="{y}" font-size="10.5" text-anchor="end" fill="#222">{t:,d}</text><text x="860" y="{y}" font-size="10.5" text-anchor="end" fill="#222">{n*t:,d}</text>')
    y+=13.2
svg.append('<rect x="940" y="160" width="360" height="330" fill="#fff" stroke="#bbb"/><text x="954" y="184" font-size="14" font-weight="700" fill="#1d6b3a">18 material families, whole area</text>')
yy=206
for m,where in MATERIALS:
    svg.append(f'<text x="954" y="{yy}" font-size="10.5" fill="#222">{m}</text><text x="1292" y="{yy}" font-size="9.5" text-anchor="end" fill="#777">{where}</text>'); yy+=15.5
svg.append('<rect x="940" y="505" width="360" height="250" fill="#fff" stroke="#bbb"/><text x="954" y="529" font-size="12" font-weight="700" fill="#555">Materials: one atlas per zone</text>')
for i,t in enumerate(["Shared families, no unique textures per prop. A view","from the yard also sees the mountain and refinery,","so check the per-view material cap with those loaded."]):
    svg.append(f'<text x="954" y="{549+i*15}" font-size="10.5" fill="#444">{t}</text>')
svg.append('<text x="954" y="610" font-size="14" font-weight="700" fill="#8a2d1a">How the budget is kept</text>')
tips=["Props are instanced; each instance still counts.","Bevels come from normal maps on props; geometry","  only on silhouettes the player sees up close.","Cliff is one hero kitbash (85k); nothing else is hero.","Junk is built from six cheap prop families.","Trees use crossed low-poly crowns, not leaves.","The 86k reserve is not allocated to any item.","Measure with the room validator once built; these","  numbers are what to design to, not a result."]
yy=630
for t in tips:
    svg.append(f'<text x="954" y="{yy}" font-size="10.5" fill="#222">{t}</text>'); yy+=15
svg.append('</svg>')
open('budget.svg','w').write('\n'.join(svg))
