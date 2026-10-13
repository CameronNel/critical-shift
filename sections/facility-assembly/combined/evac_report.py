"""Meltdown escape report for the compact map (plain Python; reads the walk reports and the door table, so run it after walk_test.py and walk_test.py --meltdown):

    python3 evac_report.py [validation/evac_report.json]

1. Escape times per station from walked lanes (validation/walk_report_meltdown.json): the primary route (through the reactor hall, the south tunnel, the concourse
   and the spine to the hall, behind the spine blast door) and the backup route (emergency exits and the exterior roads, to the hall or the yard). Backups made of
   several walked legs are composed: a leg that joins the east road part-way is joined to the road leg at that point (the road is straight there).
2. Redundancy on the door graph (validation/doors.json, evacuation state: open doors and emergency exits): for each station, the number of edge-disjoint routes to the
   front block (hall or yard), every single door whose failure cuts the station off, whether a route exists that avoids the reactor hall, and two meltdown scenarios:
   the reactor chamber sealed (REACTOR_BLAST closed) and, at the same time, the spine blast door closed (HALL_SPINE).
Speeds: walking 4.5 m/s (README); a running speed is not set anywhere in the repository, so none is assumed. Geometry only: no smoke, damage or AI."""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
WALK = 4.5
V = os.path.join(HERE, 'validation')

# door graph: (space a, space b, door ids on the link; a link fails if any of its doors fails)
LINKS = [('reactor', 'turbine', ['REACTOR_N', 'TURBINE_D01']), ('turbine', 'electrical', ['TURBINE_E_ELECTRICAL', 'ELECTRICAL_D01']), ('turbine', 'condenser', ['TURBINE_W_STAIR', 'CONDENSER_D01']),
         ('reactor', 'cooling', ['REACTOR_W', 'COOLING_P01']), ('reactor', 'waste', ['REACTOR_E_WASTE', 'WASTE_RECEIVING']), ('reactor', 'concourse', ['REACTOR_S', 'REACTOR_BLAST']),
         ('concourse', 'spine', ['SPINE_W_CONCOURSE']), ('concourse', 'fuel corridor', ['FUEL_F02E']), ('fuel corridor', 'refinery', ['REFINERY_FUEL']), ('refinery', 'hall', ['HALL_WEST']),
         ('spine', 'hall', ['HALL_SPINE']), ('spine', 'dock', ['SPINE_E_DOCK', 'DOCK_P1']), ('hall', 'cafeteria', []), ('cafeteria', 'yard', ['CAF_YARD']),
         ('reactor', 'east road', ['REACTOR_SE']), ('spine', 'east road', ['SPINE_NORTH_END']), ('turbine', 'east road', ['TURBINE_D02']), ('electrical', 'east road', ['ELECTRICAL_D02']),
         ('waste', 'east road', ['WASTE_PERSONNEL']), ('waste', 'east road', ['WASTE_DISPATCH']), ('east road', 'hall', ['HALL_EAST']), ('cooling', 'west path', ['COOLING_W_EXIT']),
         ('west path', 'yard', ['YARD_SERVICE']), ('condenser', 'east road', ['CONDENSER_W_ESCAPE', 'ESCAPE_HOUSE_DOOR'])]
STATIONS = ['reactor', 'turbine', 'electrical', 'condenser', 'cooling', 'waste', 'dock', 'fuel corridor', 'concourse', 'spine']
FRONT = {'hall', 'yard', 'cafeteria'}

def lanes(path):
    if not os.path.exists(path): return {}
    return {r['route']: r for r in json.load(open(path))['routes']}

def flow(links, s):
    """Edge-disjoint paths from s to the front block (unit capacity per link, undirected), by augmenting paths."""
    cap = collections.defaultdict(int); adj = collections.defaultdict(set)
    for i, (a, b, _) in enumerate(links):
        for u, v in ((a, b), (b, a)): cap[(u, v, i)] += 1; adj[u].add((v, i))
    T = '__front__'
    for f in FRONT: adj[f].add((T, -1)); cap[(f, T, -1)] = 99
    n = 0
    while True:
        prev = {s: None}; q = [s]
        while q and T not in prev:
            u = q.pop(0)
            for v, i in adj[u]:
                if v not in prev and cap[(u, v, i)] > 0: prev[v] = (u, i); q.append(v)
        if T not in prev: return n
        v = T
        while prev[v]:
            u, i = prev[v]; cap[(u, v, i)] -= 1; cap[(v, u, i)] += 1; v = u
        n += 1

def reach(links, s, avoid=()):
    adj = collections.defaultdict(set)
    for a, b, _ in links: adj[a].add(b); adj[b].add(a)
    seen = {s}; q = [s]
    while q:
        u = q.pop()
        for v in adj[u]:
            if v not in seen and v not in avoid: seen.add(v); q.append(v)
    return bool(seen & FRONT)

def main(out):
    doors = {d['id']: d for d in json.load(open(os.path.join(V, 'doors.json')))['doors']}
    def usable(link, state):
        return all(d not in doors or (doors[d]['evac_state'] if state == 'evac' else doors[d]['state']) == 'open' for d in link[2])
    G = {st: [l for l in LINKS if usable(l, st)] for st in ('normal', 'evac')}
    red = {}
    for s in STATIONS:
        E = G['evac']; cut = []
        for i, l in enumerate(E):
            if not reach(E[:i] + E[i + 1:], s): cut.append('/'.join(l[2]) or '%s-%s' % l[:2])
        sealed = [l for l in E if 'REACTOR_BLAST' not in l[2]]; both = [l for l in sealed if 'HALL_SPINE' not in l[2]]
        red[s] = dict(routes_normal=flow(G['normal'], s), routes_evacuation=flow(E, s), single_door_failures_that_cut_off=cut,
                      route_avoiding_reactor=reach(E, s, avoid=('reactor',)) if s != 'reactor' else None,
                      out_with_chamber_sealed=reach(sealed, s), out_with_chamber_and_spine_blast_door_sealed=reach(both, s))
    L = lanes(os.path.join(V, 'walk_report_meltdown.json'))
    ln = lambda k: L[k]['lane_length_m'] if k in L and L[k]['passed'] else None
    road = ln('evac_road_to_hall')
    def on_road(k, y_join):           # a leg joining the east road at y_join, then the road leg from there (straight from y 22.6 to -50)
        a = ln(k); return None if a is None or road is None else round(a + road - (22.6 - y_join), 1)
    RY = -18.7
    times = {
        'reactor (core)': (ln('evac_reactor_via_tunnel_to_hall'), ln('evac_reactor_SE_to_spine'), 'SE stub emergency exit, alley, spine end door, spine'),
        'turbine (D01)': (ln('primary_turbine_via_reactor'), round(ln('evac_turbine_D02_to_road') + road, 1) if ln('evac_turbine_D02_to_road') and road else None, 'D02, north strip, east road, hall east door'),
        'electrical (D01)': (ln('primary_electrical_via_reactor'), on_road('evac_electrical_D02_to_road', RY + 27.0), 'D02, east road, hall east door'),
        'waste (receiving)': (ln('primary_waste_via_reactor'), on_road('evac_waste_dispatch_to_road', RY + 3.86), 'dispatch shutter, east road, hall east door'),
        'condenser (bay, by D01)': (round(ln('evac_condenser_to_turbine_D02') + 34.4 + road, 1) if ln('evac_condenser_to_turbine_D02') and road else None,
                                    round(ln('evac_condenser_to_escape_ladder') + ln('evac_escape_house_to_road') + road, 1) if ln('evac_condenser_to_escape_ladder') and ln('evac_escape_house_to_road') and road else None,
                                    'first: stair, turbine D02, north strip, road; second: west escape door, tunnel, 6.0 m ladder (not in the distance), north strip, road'),
        'cooling (P01)': (ln('primary_cooling_via_reactor'), ln('evac_cooling_west_to_yard'), 'rear emergency door, west path, yard service door'),
        'dock (P1)': (ln('primary_dock_via_spine'), None, 'none: P1 is the dock\'s only door; P2 is its sealed arrival (contract)'),
        'fuel corridor (F02E)': (None, ln('evac_fuel_corridor_via_refinery_to_hall'), 'F01, refinery, colonnade, hall west door (the concourse route is the primary)'),
    }
    rows = []
    for k, (a, b, how) in times.items():
        rows.append(dict(station=k, primary_m=a, primary_s=round(a / WALK, 1) if a else None, backup_m=b, backup_s=round(b / WALK, 1) if b else None, backup_route=how))
    gate = ln('evac_hall_to_yard_gate')
    rep = dict(note=__doc__.split('\n\n')[1], walking_speed_m_s=WALK, hall_to_yard_gate_m=gate, hall_to_yard_gate_s=round(gate / WALK, 1) if gate else None,
               legs={k: dict(passed=v['passed'], lane_m=v.get('lane_length_m')) for k, v in L.items()}, escape_times=rows, redundancy=red)
    json.dump(rep, open(out, 'w'), indent=1)
    for r in rows: print('ESCAPE %-22s primary %6s m %5s s | backup %6s m %5s s  %s' % (r['station'], r['primary_m'], r['primary_s'], r['backup_m'], r['backup_s'], r['backup_route']))
    for s, r in red.items(): print('GRAPH %-14s routes normal %d evac %d | cut-off doors %s | avoids reactor %s | sealed chamber %s | + spine blast door %s' % (
        s, r['routes_normal'], r['routes_evacuation'], r['single_door_failures_that_cut_off'] or '-', r['route_avoiding_reactor'], r['out_with_chamber_sealed'], r['out_with_chamber_and_spine_blast_door_sealed']))
    print('GATE hall -> yard evacuation gate %s m' % gate)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(V, 'evac_report.json'))
