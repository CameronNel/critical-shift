"""Measured condenser-bay layout. Metres, Z up, right-handed.

Local origin is D01 service-door threshold centre at finished bay floor.
Turbine local = condenser local + ORIGIN_IN_TURBINE.
These are implementation decisions justified by U04, headroom and circulation,
not user-approved engineering ratings.
"""

ORIGIN_IN_TURBINE = (1.6, 7.4, -6.0)

# Clear interior. West extra 0.40 m holds the D01 west leaf pocket and operator depth.
X0, X1 = -1.80, 9.60
Y0, Y1 = 0.00, 9.40
Z0, Z1 = 0.00, 6.00
WALL = 0.28
FLOOR_THICK = 0.32
CEIL_THICK = 0.30

# D01 personnel + tool-cart door in south wall
D01_C = (0.00, 0.00, 0.00)
D01_W, D01_H = 2.00, 2.40
D01_OUT = (0.0, -1.0, 0.0)

# U04 / IF_LP_EXHAUST_CONDENSER receive (turbine (4.6, 11.45, 0), 2.5 X × 1.5 Y)
EXH_C = (3.00, 4.05, 6.00)
EXH_X, EXH_Y = 2.50, 1.50

# Condenser CD-01 body (tubes along +X, steam chest on +Z)
CD_C = (3.00, 4.05, 3.15)
CD_LEN_X = 3.70
CD_WID_Y = 2.45
CD_BODY_Z0, CD_BODY_Z1 = 1.72, 4.62
HW_Z0, HW_Z1 = 1.08, 1.72
WB_DEPTH = 0.55

# Gallery
GAL_Z = 4.18
GAL_W = 0.90
GAL_RAIL = 1.10

# Stairs occupy a 0.95 m strip along the south wall, east of the D01 east leaf pocket
STAIR_Y0, STAIR_Y1 = 0.18, 1.12
STAIR_X0, STAIR_MID, STAIR_X1 = 2.15, 5.05, 6.20

# Condensate pumps north of shell
P1 = (2.35, 7.05, 0.00)
P2 = (4.05, 8.20, 0.00)

# Operator on west wall, facing condenser
OP_C = (-1.18, 4.05, 1.35)

# Vacuum ejector north-west
EJ_C = (-0.55, 7.55, 1.55)

# Sump
SUMP_C = (8.55, 8.55, 0.00)

# Unbound utility handoffs (local)
IF_CONDENSATE_HANDOFF = (7.90, 0.00, 5.42)  # toward turbine U02; does not alter turbine
IF_CW_SUPPLY = (9.60, 3.20, 3.15)
IF_CW_RETURN = (9.60, 4.90, 3.15)
IF_DRAIN_OUT = (9.60, 8.55, -0.08)
IF_VENT_OUT = (3.00, 9.40, 5.55)

# Circulation keep-clears
WEST_AISLE = dict(min=(-1.80, 0.00, 0.00), max=(0.90, 9.40, 2.40))
SOUTH_WALK = dict(min=(0.85, 1.15, 0.00), max=(5.20, 2.55, 2.40))
EAST_PULL = dict(min=(6.20, 1.20, 0.00), max=(9.45, 7.20, 2.70))
NORTH_PUMP_APRON = dict(min=(1.20, 5.55, 0.00), max=(5.20, 6.55, 2.40))
CART = (0.80, 2.20, 1.60)


def to_turbine(p):
    return (p[0] + ORIGIN_IN_TURBINE[0], p[1] + ORIGIN_IN_TURBINE[1], p[2] + ORIGIN_IN_TURBINE[2])
