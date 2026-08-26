from pathlib import Path
import re


def replace_required(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"Expected {label} text not found: {old[:180]}")
    return text.replace(old, new)


game_path = Path("GAME_SPEC.md")
game = game_path.read_text(encoding="utf-8")

game_replacements = [
    (
        "**Visual style:** Stylised adult human workers in grounded, chunky industrial environments, with readable silhouettes and believable proportions  ",
        "**Visual style:** Highly stylised, low-detail human workers and chunky industrial environments, using simple/faceted geometry, compact expressive proportions, bold colour blocking, texture-light materials, and strong gameplay silhouettes  ",
    ),
    (
        "## 4.1 Character Form\n\nWorkers are stylised adult human figures with:\n\n- Believable adult proportions.\n- Varied body types, ages, and ethnic backgrounds.\n- Recognisably human faces, visible directly or through practical visors.\n- Industrial helmets, hoods, respirators, and protective layers appropriate to each task.\n- Slight exaggeration of hands, footwear, or equipment only where gameplay readability requires it.\n- Utility belts, radios, tools, and telemetry packs.\n- Oxygen, cooling, or life-support modules where required.\n- Visible dosimeters and department markings.\n- Strong colour identification.\n- Clear silhouettes at gameplay distance.\n\nDo not use childlike head-to-body ratios, tiny torsos, stubby limbs, mascot faces, or toy-like proportions. The workers may be stylised and expressive, but they must read as adult humans performing dangerous industrial work.\n",
        "## 4.1 Character Form\n\nWorkers are deliberately stylised adult human figures. `docs/ART_DIRECTION.md` is authoritative for their visual proportions and surface treatment. The target is compact, expressive, low-detail readability rather than anatomical realism.\n\nUse:\n\n- Compact adult-coded proportions, broadly around 5.5 to 6.5 heads tall.\n- Slightly enlarged helmet/head volume for expression and recognition.\n- Simplified torso and limb masses.\n- Readable, somewhat oversized hands/gloves and boots for physical interaction.\n- Varied body types, ages, skin tones, faces, and identities expressed within the shared stylised proportion system.\n- Recognisably human faces, visible directly or through practical visors, with simple features rather than facial microdetail.\n- Industrial helmets, hoods, respirators, sealed suits, packs, and protective layers appropriate to each task.\n- Utility belts, radios, tools, telemetry packs, dosimeters, and department markings simplified into large readable shapes.\n- Strong player/department colour identification.\n- Clear silhouettes at gameplay distance and while ragdolled.\n\nWorkers must read as adults through posture, voice, role, equipment, and context, but they should not target realistic human anatomy. Avoid baby/toddler coding, chibi/anime proportions, plush-toy materials, or mascot costumes.\n",
    ),
    (
        "1. Stylised adult human character controller.",
        "1. PEAK-led stylised human character controller with compact, readable proportions.",
    ),
    (
        "- Adult-proportioned placeholder humanoid.",
        "- Compact stylised placeholder humanoid matching `docs/ART_DIRECTION.md`.",
    ),
    (
        "The architecture should feel like a grounded industrial sci-fi facility with Sea of Thieves-inspired stylized exaggeration: bold readable silhouettes, chunky bevels, asymmetry, and controlled wear.",
        "The architecture should establish Critical Shift's PEAK-led visual language immediately: simple/faceted low-detail geometry, bold readable silhouettes, chunky functional forms, broad colour blocking, sparse surface detail, and lighting-led atmosphere. It must remain an original Critical Shift industrial design rather than copying another game's assets.",
    ),
    (
        "- **Wearable Clothes/PPE:** Stylized adult worker suit pieces, helmets, gloves, and boots presented on hangers or inside lockers.",
        "- **Wearable Clothes/PPE:** The signature Critical Shift hero hazmat suit and modular PPE pieces, using compact stylised proportions, a strong helmet/visor silhouette, chunky gloves/boots, broad colour blocks, and minimal surface noise, presented clearly on hangers or inside lockers.",
    ),
    (
        "- Hand-authored painterly materials using shared material sets, trim sheets, and decals.",
        "- Texture-light materials using broad colour blocks, simple shared material families, vertex colour/masks where useful, and sparse functional decals. Do not use painterly Sea of Thieves treatment or realistic PBR microdetail.",
    ),
]

for old, new in game_replacements:
    game = replace_required(game, old, new, "GAME_SPEC")

authority_anchor = "**Primary development model:** One human director supervising external AI agents that perform most implementation, testing, documentation, scene assembly, and maintenance\n"
authority_note = "**Visual authority:** `docs/ART_DIRECTION.md` is authoritative for character, environment, material, lighting, concept-art, and generated-asset style. It supersedes conflicting legacy visual wording in this specification while gameplay, systems, dimensions, routes, and interaction requirements remain authoritative.\n"
if authority_note not in game:
    game = replace_required(game, authority_anchor, authority_anchor + authority_note, "GAME_SPEC metadata")

google_old = "## 32.5 Google AI Role\n\n- Visual critique.\n- Alternate technical analysis.\n- Reference analysis.\n- Documentation.\n- Independent review.\n"
google_new = "## 32.5 Google AI Role\n\n- Visual concept generation and critique using `docs/ART_DIRECTION.md` and dedicated prompts under `art/concepts/`.\n- Alternate technical analysis.\n- Reference analysis focused on high-level visual qualities rather than copying protected assets.\n- Documentation.\n- Independent review.\n"
if google_old in game:
    game = game.replace(google_old, google_new, 1)

game_path.write_text(game, encoding="utf-8")

reactor_path = Path("docs/REACTOR_ROOM_VISUAL_SPEC.md")
reactor = reactor_path.read_text(encoding="utf-8")

authority = "**Art-direction authority:** `docs/ART_DIRECTION.md`\n"
note = "**Surface-style rule:** this document remains authoritative for reactor layout, dimensions, object separation, interaction positions, and animation requirements; `docs/ART_DIRECTION.md` is authoritative for proportions, geometry language, materials, texture density, lighting treatment, and overall visual stylisation. Legacy realistic/PBR wording below is subordinate to that art bible.\n"
if note not in reactor:
    reactor = replace_required(reactor, authority, authority + note, "reactor authority")

reactor_replacements = [
    (
        "- Brushed stainless, galvanised steel and powder-coated machine housings.",
        "- Broad cool-grey/off-white/blue-green machine colour blocks that suggest industrial metal without realistic brushed-metal microdetail.",
    ),
    (
        "- Modest wear at contact edges and service areas, but no blanket rust, soot or grime.",
        "- Sparse graphic wear only where it communicates use or damage; no blanket rust, soot, grime, scratch noise, or realistic surface ageing.",
    ),
    (
        "- Deep cylindrical/segmented shaft with pale tiled, enamelled or stainless inner walls.",
        "- Deep cylindrical/segmented shaft with broad pale wall segments that suggest tile, enamel or metal without realistic surface microdetail.",
    ),
    (
        "- free/permissive PBR materials are used and their sources recorded",
        "- shared texture-light materials follow `ART_DIRECTION.md`; any external material sources used are permissively licensed and recorded",
    ),
]
for old, new in reactor_replacements:
    reactor = replace_required(reactor, old, new, "reactor")

material_section = """## 12. Material families and texture-light sourcing

The reactor room uses a restrained reusable material palette consistent with `ART_DIRECTION.md`. Materials should read by **large value/colour blocks and simple response**, not by photographic texture detail.

Required material families:

1. off-white / pale structural shell
2. cool grey machine body
3. blue-grey / muted green equipment accent
4. dark sealed floor / floor-panel family
5. white or very light coolant pipe family
6. dark rubber / grip / boot-like utility material
7. simple clear / smoked glass for windows and protective covers
8. dark screen glass
9. emissive cyan reactor light
10. coloured indicator / emergency emissives
11. small yellow-black hazard marking / decal set
12. sparse contamination / scorch / damage decal family

Preferred implementation:

- Solid colours, gradients, vertex colour, simple masks and restrained roughness variation first.
- Little or no normal-map detail on ordinary architecture and machines.
- Reuse the same material families across many objects.
- Use sparse decals only for labels, hazards, contamination and meaningful damage.
- Do not use realistic brushed-metal normals, dense scratches, photographed grime, cloth weave, or high-frequency wear as a finishing layer.
- Most ordinary assets should need no unique texture set. When textures are necessary, prefer small reusable textures; 512–1024 px is generally sufficient, with 2K reserved for a demonstrated hero/close-interaction need.
- Any externally sourced texture or material retained in production must have a compatible licence and recorded source, but the art pipeline should not depend on realistic PBR libraries.

"""
reactor, count = re.subn(
    r"## 12\. Material families and PBR sourcing\n.*?(?=## 13\. Lighting and state progression)",
    material_section,
    reactor,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f"Expected exactly one reactor material section, replaced {count}")

reactor_path.write_text(reactor, encoding="utf-8")

combined = game + reactor
forbidden_positive = [
    "Sea of Thieves-inspired stylized exaggeration",
    "Hand-authored painterly materials",
    "Believable adult proportions.",
    "Adult-proportioned placeholder humanoid",
    "Material families and PBR sourcing",
    "free/permissive PBR materials are used",
]
leftovers = [term for term in forbidden_positive if term in combined]
if leftovers:
    raise SystemExit(f"Legacy positive style language remains: {leftovers}")

required = [
    "**Visual authority:** `docs/ART_DIRECTION.md`",
    "PEAK-led stylised human character controller",
    "Critical Shift's PEAK-led visual language",
    "## 12. Material families and texture-light sourcing",
    "**Surface-style rule:**",
]
missing = [term for term in required if term not in combined]
if missing:
    raise SystemExit(f"Required migrated language missing: {missing}")

print("Visual migration applied and validated.")
